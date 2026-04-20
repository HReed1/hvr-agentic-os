import os
import sys
import json
import boto3
import urllib.request
from decimal import Decimal

# Cost Baseline Hours
MONTHLY_HOURS = Decimal("730.0")

def get_on_demand_price(pricing_client, service_code, instance_type, os_system="Linux"):
    """
    Query the AWS Pricing API dynamically to locate the absolute base On-Demand USD price.
    """
    # Defensive dictionary for Service codes to Field keys
    field_key = "instanceClass" if service_code == "AmazonRDS" else "instanceType"
    
    filters = [
        {'Type': 'TERM_MATCH', 'Field': field_key, 'Value': instance_type},
        {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'}
    ]
    
    if service_code == "AmazonEC2":
        filters.extend([
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': os_system},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
            {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'}
        ])
    
    try:
        response = pricing_client.get_products(
            ServiceCode=service_code,
            Filters=filters,
            MaxResults=1
        )
        
        for price_str in response.get('PriceList', []):
            product = json.loads(price_str)
            terms = product.get('terms', {}).get('OnDemand', {})
            for term_data in terms.values():
                dims = term_data.get('priceDimensions', {})
                for dim_data in dims.values():
                    usd_val = dim_data.get('pricePerUnit', {}).get('USD')
                    if usd_val:
                        return Decimal(usd_val)
    except Exception as e:
        print(f"Failed to isolate Pricing API for {instance_type}: {e}")
        
    return Decimal("0.0")

def get_spot_price(ec2_client, instance_type):
    """
    Spot Pricing history fluctuates violently; the pricing API doesn't accurately reflect live bounds.
    We natively hit the primary describe_spot_price_history matrix.
    """
    try:
        response = ec2_client.describe_spot_price_history(
            InstanceTypes=[instance_type],
            ProductDescriptions=['Linux/UNIX'],
            MaxResults=1
        )
        history = response.get('SpotPriceHistory', [])
        if history:
            return Decimal(history[0]['SpotPrice'])
    except Exception as e:
        print(f"Failed to isolate EC2 Spot API for {instance_type}: {e}")
        
    return Decimal("0.0")

def post_github_comment(markdown_body):
    """
    Sovereign Zero-Trust GitHub API Comment Extractor.
    Bypasses external composite Actions entirely.
    """
    token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    pr_number = os.environ.get('PR_NUMBER')
    
    if not token or not repo or not pr_number:
        print("GitHub Environment Context Missing. Dumping breakdown exactly to STDOUT:")
        print(markdown_body)
        return

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    payload = json.dumps({"body": markdown_body}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 201:
                print(f"FinOps Payload injected natively into PR #{pr_number}.")
    except Exception as e:
        print(f"Fatal error pushing GitHub Object natively: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pr_cost_estimator.py <plan.json>")
        sys.exit(1)
        
    plan_path = sys.argv[1]
    if not os.path.exists(plan_path):
        print(f"Fatal: Terraform plan schema {plan_path} does not exist.")
        sys.exit(1)
        
    with open(plan_path, 'r') as f:
        plan_data = json.load(f)
        
    pricing = boto3.client('pricing', region_name='us-east-1')
    ec2 = boto3.client('ec2', region_name='us-east-1')
    
    resources_analyzed = []
    total_monthly_impact = Decimal("0.0")
    
    for change in plan_data.get('resource_changes', []):
        r_type = change.get('type')
        actions = change.get('change', {}).get('actions', [])
        
        # We only care about explicit creations or updates
        if 'create' not in actions and 'update' not in actions:
            continue
            
        after = change.get('change', {}).get('after', {})
        if not after:
            continue
            
        instance_type = None
        service_code = "AmazonEC2"
        vcpus_multiplier = Decimal("1.0")
        is_spot = False
        
        if r_type == 'aws_instance':
            instance_type = after.get('instance_type')
        elif r_type == 'aws_db_instance':
            instance_type = after.get('instance_class')
            service_code = "AmazonRDS"
        elif r_type == 'aws_batch_compute_environment':
            resources = after.get('compute_resources', [])
            if resources:
                block = resources[0]
                instance_targets = block.get('instance_type', [])
                if instance_targets:
                    # Natively pick the primary hardware target fallback
                    instance_type = instance_targets[0] 
                # The mathematical multiplier for parallel clusters
                max_vcpus = Decimal(block.get('max_vcpus', 1))
                # Hardware approximation: EC2 vCPUs map universally (e.g. 4xlarge = 16 cores)
                # To calculate cluster cost, we derive the max instances using the node size:
                vcpus_multiplier = max_vcpus / Decimal("16.0") # Generic normalizer
                
                env_type = block.get('type', 'SPOT')
                is_spot = env_type == 'SPOT'
        
        if instance_type:
            if "." not in instance_type:
                instance_type = f"{instance_type}.xlarge"
                
            hourly_rate = Decimal("0.0")
            if is_spot:
                hourly_rate = get_spot_price(ec2, instance_type)
            else:
                hourly_rate = get_on_demand_price(pricing, service_code, instance_type)
                
            monthly_cost = hourly_rate * MONTHLY_HOURS * max(Decimal("1.0"), vcpus_multiplier)
            total_monthly_impact += monthly_cost
            
            resources_analyzed.append({
                "resource": change.get('address'),
                "type": r_type,
                "instance": instance_type,
                "monthly_cost": f"${monthly_cost:,.2f}"
            })

    # 4. Synthesize Markdown Presentation
    markdown = "## 🛡️ Sovereign FinOps Architectural Evaluation\n\n"
    markdown += "This PR dynamically alters the foundational compute architectures. The projected execution math is mapped strictly below bypassing third-party vendors:\n\n"
    markdown += "| Infrastructure Target | Resource Node | Instance Spec | Est. Monthly Ceiling |\n"
    markdown += "| --- | --- | --- | --- |\n"
    
    if not resources_analyzed:
        markdown += "| Zero Financial Impact | N/A | N/A | $0.00 |\n"
    else:
        for r in resources_analyzed:
            markdown += f"| `{r['resource']}` | `{r['type']}` | `{r['instance']}` | **{r['monthly_cost']}** |\n"
            
    markdown += f"\n### Total Architecture Drift Impact: **${total_monthly_impact:,.2f} / mo**\n"
    markdown += "> _Pricing generated natively via `boto3` querying `us-east-1` AWS Service matrices._"
    
    post_github_comment(markdown)

if __name__ == "__main__":
    main()
