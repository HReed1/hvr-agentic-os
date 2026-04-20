#!/usr/bin/env python3
import sys
import boto3
import time
from decimal import Decimal, getcontext

getcontext().prec = 10

if len(sys.argv) < 2:
    print("Usage: ./live_job_cost.py <AWS_BATCH_JOB_ID>")
    sys.exit(1)

job_id = sys.argv[1]

batch = boto3.client('batch', region_name='us-east-1')
ecs = boto3.client('ecs', region_name='us-east-1')
ec2 = boto3.client('ec2', region_name='us-east-1')

print(f"📡 Resolving FinOps Data for AWS Batch Job: {job_id}...")
resp = batch.describe_jobs(jobs=[job_id])
if not resp['jobs']:
    print(f"❌ Could not find Job: {job_id}")
    sys.exit(1)

job = resp['jobs'][0]

# Temporal Calculation
created_at = job.get('createdAt', 0) / 1000.0
started_at = job.get('startedAt', created_at * 1000.0) / 1000.0

if 'stoppedAt' in job:
    stopped_at = job['stoppedAt'] / 1000.0
else:
    stopped_at = time.time()

if started_at == 0:
    print("⏳ Job has not started executing yet. Cost evaluates to $0.00.")
    sys.exit(0)

duration_sec = max(0, stopped_at - started_at)
duration_decimal = Decimal(str(duration_sec))
hours_decimal = duration_decimal / Decimal('3600')

# Format Uptime
m, s = divmod(int(duration_sec), 60)
h, m = divmod(m, 60)
uptime_str = f"{h:02d}:{m:02d}:{s:02d}"

# Architecture Traverse
try:
    task_arn = job['container']['taskArn']
    
    cluster_arn = job['container'].get('containerInstanceArn')
    if not cluster_arn:
        cluster_name = task_arn.split('/')[1]
        task_desc = ecs.describe_tasks(cluster=cluster_name, tasks=[task_arn])
        cluster_arn = task_desc['tasks'][0]['containerInstanceArn']

    ecs_cluster = task_arn.split('/')[1]
    inst_desc = ecs.describe_container_instances(cluster=ecs_cluster, containerInstances=[cluster_arn])
    ec2_instance_id = inst_desc['containerInstances'][0]['ec2InstanceId']

    ec2_desc = ec2.describe_instances(InstanceIds=[ec2_instance_id])
    instance_data = ec2_desc['Reservations'][0]['Instances'][0]
    
    instance_type = instance_data['InstanceType']
    lifecycle = instance_data.get('InstanceLifecycle', 'on-demand')
    
except Exception as e:
    print(f"⚠️ Could not traverse to underlying EC2 Instance (perhaps already terminated?): {e}")
    print("Falling back to estimating via job queue string hints...")
    queue_name = job.get('jobQueue', '')
    if 'gpu' in queue_name.lower() or 'spot' in queue_name.lower():
        instance_type = "g4dn.xlarge"
        lifecycle = "spot"
    else:
        instance_type = "r5.4xlarge"
        lifecycle = "on-demand"

print(f"✅ Extracted Hardware: {instance_type} ({lifecycle})")

# Financial Engine (Strict Decimals)
ON_DEMAND_RATES = {
    'r5.4xlarge': Decimal('1.008'),
    'g4dn.2xlarge': Decimal('0.752'),
    'g4dn.xlarge': Decimal('0.526'),
    'c5.large': Decimal('0.085'),
    'm5.large': Decimal('0.096'),
    'c5.2xlarge': Decimal('0.340'),
    'm5.2xlarge': Decimal('0.384')
}

hourly_rate = Decimal('0.00')

if lifecycle == 'spot':
    try:
        spot_resp = ec2.describe_spot_price_history(
            InstanceTypes=[instance_type],
            MaxResults=1,
            ProductDescriptions=['Linux/UNIX']
        )
        if spot_resp['SpotPriceHistory']:
            hourly_rate = Decimal(spot_resp['SpotPriceHistory'][0]['SpotPrice'])
        else:
            raise ValueError("No spot history returned.")
    except Exception as e:
        print(f"⚠️ Failed to fetch Spot price dynamically. Falling back to 60% of On-Demand. Err: {e}")
        base = ON_DEMAND_RATES.get(instance_type, Decimal('1.008'))
        hourly_rate = base * Decimal('0.4')
else:
    hourly_rate = ON_DEMAND_RATES.get(instance_type, Decimal('1.008'))

# Total Cost Calculation
total_cost = hours_decimal * hourly_rate

print("\n" + "="*50)
print(f"💵 LIVE BATCH FINOPS REPORT 💵")
print("="*50)
print(f"Job ID:      {job_id}")
print(f"Hardware:    {instance_type}")
print(f"Market:      {lifecycle.upper()}")
print(f"Uptime:      {uptime_str} (HH:MM:SS)")
print(f"Hourly Rate: ${hourly_rate:.4f} USD")
print(f"LIVE COST:   ${total_cost:.4f} USD")
print("="*50)
