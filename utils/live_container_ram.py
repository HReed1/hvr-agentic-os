#!/usr/bin/env python3
# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics
import boto3
import sys
import time
import argparse
from botocore.exceptions import ClientError

def get_live_ram_metrics(job_id, profile="admin", watch=False):
    """
    Connects to AWS Batch, traces the physical EC2 instance backing the ECS Task,
    and executes a zero-trust SSM tunnel to query the live `docker stats` natively from the node OS.
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
        print(f"❌ Error: Job is in state '{status}', not 'RUNNING'. Live RAM telemetry is only available for active nodes.")
        sys.exit(1)
        
    container_instance_arn = job['container'].get('containerInstanceArn')
    if not container_instance_arn:
        print("❌ Error: Could not extract containerInstanceArn. Is it a Fargate task?")
        sys.exit(1)
        
    print(f"✅ Found ECS Node: {container_instance_arn.split('/')[-1]}")
    
    # Extract Cluster Name and Instance ID from ARN
    # arn:aws:ecs:us-east-1:123:container-instance/CLUSTER_NAME/INSTANCE_ID
    parts = container_instance_arn.split(':container-instance/')
    path_parts = parts[1].split('/')
    cluster_name = path_parts[0]
    container_id = path_parts[1]
    
    # Get physical EC2 Instance ID
    print(f"📡 Resolving underlying EC2 architecture on cluster '{cluster_name}'...")
    ecs_resp = ecs_client.describe_container_instances(cluster=cluster_name, containerInstances=[container_instance_arn])
    ec2_instance_id = ecs_resp['containerInstances'][0]['ec2InstanceId']
    
    print(f"✅ Mapped to EC2 Instance: {ec2_instance_id}")
    
    # Execute docker stats via SSM
    while True:
        if watch:
            print(chr(27) + "[2J")
        print(f"🚀 Firing secure AWS Systems Manager (SSM) Shell injection to calculate live RAM footprints...")
        command = "docker stats --no-stream --format 'table {{.Name}}\\t{{.MemUsage}}\\t{{.MemPerc}}\\t{{.CPUPerc}}'"
        
        try:
            ssm_response = ssm_client.send_command(
                InstanceIds=[ec2_instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': [command]}
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
            print(f"\n📊 --- LIVE DOCKER TELEMETRY (EC2: {ec2_instance_id}) --- 📊\n")
            print(invocation['StandardOutputContent'])
            print(f"-----------------------------------------------------------\n")
            print(f"Target Job Identifier matches ECS Task ARN: {job['container'].get('taskArn').split('/')[-1]}")
        else:
            print(f"❌ SSM Command {status}. Does the EC2 instance have the AmazonSSMManagedInstanceCore role attached?")
            if 'StandardErrorContent' in invocation:
                print(invocation['StandardErrorContent'])
                
        if not watch:
            break
        time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live AWS Batch Pipeline RAM Visualizer via SSM")
    parser.add_argument("JOB_ID", nargs="?", help="The AWS Batch Job ID to query")
    parser.add_argument("--process-name", help="Auto-discover JOB_ID by Nextflow process name (e.g., MERGE_BAMS_REGIONAL)")
    parser.add_argument("--watch", action="store_true", help="Continuously poll telemetry creating a live dashboard")
    parser.add_argument("--profile", default="admin", help="AWS CLI Profile to use (default: admin)")
    
    args = parser.parse_args()
    
    job_id = args.JOB_ID
    
    if args.process_name:
        session = boto3.Session(profile_name=args.profile, region_name='us-east-1')
        batch_client = session.client('batch')
        queues = ["somatic-cpu-ondemand-queue", "somatic-cpu-queue", "somatic-gpu-queue", "somatic-gpu-ondemand-queue", "viral-cpu-queue", "viral-cpu-ondemand-queue"]
        
        while not job_id:
            if args.watch:
                print(chr(27) + "[2J", end="")
                print(f"🔍 [WATCH] Polling active queues for process '{args.process_name}' to enter RUNNING state...")
            else:
                print(f"🔍 Auto-discovering JOB_ID for process '{args.process_name}' across all active queues...")
                
            for q in queues:
                try:
                    res = batch_client.list_jobs(jobQueue=q, jobStatus='RUNNING')
                    for job in res.get('jobSummaryList', []):
                        if args.process_name in job['jobName']:
                            job_id = job['jobId']
                            print(f"✅ Auto-Discovered JOB_ID: {job_id} in queue {q}")
                            break
                except Exception as e:
                    print(f"⚠️ Error querying queue {q}: {e}")
                
                if job_id:
                    break
                    
            if not job_id:
                if args.watch:
                    time.sleep(5)
                else:
                    print(f"❌ Error: No RUNNING job found matching '{args.process_name}'.")
                    sys.exit(1)
                
    if not job_id:
        print("❌ Error: You must provide a JOB_ID or valid --process-name")
        sys.exit(1)
        
    get_live_ram_metrics(job_id, args.profile, args.watch)
