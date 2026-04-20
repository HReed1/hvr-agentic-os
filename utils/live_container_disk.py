#!/usr/bin/env python3
# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics
import boto3
import sys
import time
import argparse
from botocore.exceptions import ClientError

def get_live_disk_metrics(job_id, path="/dev/shm", profile="admin"):
    """
    Connects to AWS Batch, traces the physical EC2 instance backing the ECS Task,
    and executes a zero-trust SSM tunnel to query the live `du` / `df` footprints natively 
    inside the active Docker container to watch RAM-disk or EBS extraction expand byte-by-byte.
    """
    session = boto3.Session(profile_name=profile)
    batch_client = session.client('batch')
    ecs_client = session.client('ecs')
    ssm_client = session.client('ssm')
    
    print(f"📡 Resolving AWS Batch Job: {job_id}...")
    response = batch_client.describe_jobs(jobs=[job_id])
    jobs = response.get('jobs', [])
    
    if not jobs:
        print(f"❌ Error: Job {job_id} not found.")
        sys.exit(1)
        
    job = jobs[0]
    status = job.get('status')
    
    if status != 'RUNNING':
        print(f"❌ Error: Job is in state '{status}', not 'RUNNING'. Live Disk telemetry is only available for active nodes.")
        sys.exit(1)
        
    container_instance_arn = job['container'].get('containerInstanceArn')
    task_arn = job['container'].get('taskArn')
    
    if not container_instance_arn or not task_arn:
        print("❌ Error: Could not extract containerInstanceArn or taskArn. Is it a Fargate task?")
        sys.exit(1)
        
    print(f"✅ Found ECS Node: {container_instance_arn.split('/')[-1]}")
    
    # Extract Cluster Name and Instance ID from ARN
    parts = container_instance_arn.split(':container-instance/')
    path_parts = parts[1].split('/')
    cluster_name = path_parts[0]
    
    # Get physical EC2 Instance ID
    print(f"📡 Resolving underlying EC2 architecture on cluster '{cluster_name}'...")
    ecs_resp = ecs_client.describe_container_instances(cluster=cluster_name, containerInstances=[container_instance_arn])
    ec2_instance_id = ecs_resp['containerInstances'][0]['ec2InstanceId']
    
    print(f"✅ Mapped to EC2 Instance: {ec2_instance_id}")
    
    # Execute docker exec via SSM
    print(f"🚀 Firing secure AWS Systems Manager (SSM) Shell injection to calculate live {path} footprints...")
    
    # Securely locate the exact container using the ECS Task ARN label
    shell_command = f"""
    CONT_ID=$(docker ps -q --filter label=com.amazonaws.ecs.task-arn={task_arn})
    if [ -z "$CONT_ID" ]; then
        echo "❌ Could not dynamically locate Docker container for Task ARN: {task_arn}"
        exit 1
    fi
    echo "✅ Dynamically locked onto Container ID: $CONT_ID"
    echo ""
    echo "📊 --- PARTITION TOTALS --- 📊"
    docker exec $CONT_ID df -h {path}
    echo ""
    echo "📊 --- DIRECTORY PAYLOAD SIZES --- 📊"
    docker exec $CONT_ID bash -c "du -sh {path}/* 2>/dev/null" || true
    """
    
    try:
        ssm_response = ssm_client.send_command(
            InstanceIds=[ec2_instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': [shell_command]}
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print("\n⚠️ IAM Security Block: SSM send_command AccessDenied.")
            print("Falling back to passive EC2 instance discovery...")
            ec2_client = session.client('ec2')
            ec2_resp = ec2_client.describe_instances(InstanceIds=[ec2_instance_id])
            inst = ec2_resp['Reservations'][0]['Instances'][0]
            lifecycle = inst.get('InstanceLifecycle', 'on-demand')
            print(f"✅ Telemetry Fallback -> Instance: {inst['InstanceType']} | Lifecycle: {lifecycle}")
            sys.exit(0)
        raise
    
    command_id = ssm_response['Command']['CommandId']
    
    # Poll for completion
    while True:
        time.sleep(2)
        invocation = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=ec2_instance_id
        )
        status = invocation['Status']
        if status in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
            break
            
    if status == 'Success':
        print(f"\n📊 --- LIVE DISK X-RAY (EC2: {ec2_instance_id}) --- 📊\n")
        print(invocation['StandardOutputContent'])
        print(f"-----------------------------------------------------------\n")
    else:
        print(f"❌ SSM Command {status}. Error Traceback:")
        if 'StandardErrorContent' in invocation:
            print(invocation['StandardErrorContent'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live AWS Batch Pipeline Disk/RAM-Disk Visualizer via SSM")
    parser.add_argument("JOB_ID", help="The AWS Batch Job ID to query")
    parser.add_argument("--path", default="/dev/shm", help="Target container directory to explicitly monitor (default: /dev/shm)")
    parser.add_argument("--profile", default="admin", help="AWS CLI Profile to use (default: admin)")
    
    args = parser.parse_args()
    get_live_disk_metrics(args.JOB_ID, args.path, args.profile)
