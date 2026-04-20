import boto3
import time
import csv
import argparse
import sys
import re
from io import StringIO

def parse_time(time_str):
    """Converts a Nextflow time string (e.g. '10m 30s', '1.5s', '500ms') into seconds."""
    val = 0.0
    s_str = str(time_str).strip()
    
    if 'ms' in s_str:
        ms_part = re.search(r'([0-9.]+)\s*ms', s_str)
        if ms_part:
            val += float(ms_part.group(1)) / 1000.0
        s_str = s_str.replace('ms', '')
        
    if 'h' in s_str:
        m = re.search(r'([0-9.]+)\s*h', s_str)
        if m: val += float(m.group(1)) * 3600
        
    if 'm' in s_str:
        m = re.search(r'([0-9.]+)\s*m', s_str)
        if m: val += float(m.group(1)) * 60
        
    s_part = re.search(r'([0-9.]+)\s*s', s_str)
    if s_part:
        val += float(s_part.group(1))
        
    return val

def analyze_execution_trace(profile="admin", region="us-east-1", process_filter="MERGE_BAMS_REGIONAL"):
    """
    Connects to AWS EC2, queries the head node,
    and executes an SSM tunnel to securely retrieve the Nextflow trace CSV.
    """
    session = boto3.Session(profile_name=profile, region_name=region)
    ec2_client = session.client('ec2')
    ssm_client = session.client('ssm')
    
    print("🔍 Resolving AWS Head Node architecture...")
    res = ec2_client.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['Somatic-Head-Node']}, 
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    # Sort instances by launch time descending to get the newest active head node
    instances = sorted(res['Reservations'], key=lambda x: x['Instances'][0]['LaunchTime'], reverse=True)
    if not instances:
        print("❌ Error: Active ngs-head-node not found.")
        sys.exit(1)
        
    head_node_id = instances[0]['Instances'][0]['InstanceId']
    print(f"✅ Mapped to Head Node EC2 Instance: {head_node_id}")
    
    print(f"🚀 Firing secure AWS SSM Shell injection to retrieve trace telemetry...")
    # Retrieve the execution trace payload remotely, utilizing grep to bypass the 24KB SSM buffer limit
    command = f"head -n 1 /home/ec2-user/ngs-variant-validator/reports/execution_trace-1.csv && grep {process_filter} /home/ec2-user/ngs-variant-validator/reports/execution_trace-1.csv || true"
    
    ssm_response = ssm_client.send_command(
        InstanceIds=[head_node_id],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [command]}
    )
    
    command_id = ssm_response['Command']['CommandId']
    
    # Poll for completion natively
    while True:
        time.sleep(2)
        invocation = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=head_node_id
        )
        status = invocation['Status']
        if status in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
            break
            
    if status == 'Success':
        raw_csv = invocation['StandardOutputContent']
        
        if not raw_csv.strip():
            print("⚠️ The execution trace is empty. Did the pipeline hydrate properly?")
            sys.exit(1)
            
        print(f"\n📊 --- LIVE FINOPS TRACE ANALYSIS ({process_filter}) --- 📊\n")
        
        try:
            lines = raw_csv.strip().split('\n')
            if not lines:
                print("⚠️ File is empty.")
                sys.exit(1)
                
            headers = re.split(r'\t|,', lines[0])
            dur_idx = -1
            if 'duration' in headers:
                dur_idx = headers.index('duration')
            elif 'realtime' in headers:
                dur_idx = headers.index('realtime')
                
            durations = []
            
            for line in lines[1:]:
                if process_filter in line:
                    parts = re.split(r'\t|,', line)
                    if dur_idx != -1 and dur_idx < len(parts):
                        rt = parts[dur_idx]
                        if not rt or not rt.strip() or rt.strip() == '-':
                            rt = '0s'
                        durations.append(parse_time(rt))
                        
            if not durations:
                print(f"❌ No execution records found matching '{process_filter}'.")
                sys.exit(0)
                
            fastest = min(durations)
            slowest = max(durations)
            average = sum(durations) / len(durations)
            
            print(f"✅ Scanned {len(durations)} tasks successfully.")
            print(f"⚡ Fastest Duration: {fastest:.2f} seconds")
            print(f"🐢 Slowest Duration: {slowest:.2f} seconds")
            print(f"📈 Average Duration: {average:.2f} seconds")
            print("\n-----------------------------------------------------------")
            
        except Exception as e:
            print(f"❌ Failed to parse the returned artifact schema: {e}")
            
    else:
        print(f"❌ SSM Command {status}. Error retrieving reports/execution_trace-1.csv from the head node.")
        if 'StandardErrorContent' in invocation:
            print(invocation['StandardErrorContent'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live AWS Nextflow FinOps Trace Analyzer")
    parser.add_argument("--process-name", default="MERGE_BAMS_REGIONAL", help="Process to filter from the trace")
    parser.add_argument("--profile", default="admin", help="AWS CLI Profile to use (default: admin)")
    
    args = parser.parse_args()
    analyze_execution_trace(args.profile, "us-east-1", args.process_name)
