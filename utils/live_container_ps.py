#!/usr/bin/env python3
import sys
import boto3
import time
from botocore.exceptions import ClientError

if len(sys.argv) < 2:
    print("Usage: ./live_container_ps.py <AWS_BATCH_JOB_ID>")
    sys.exit(1)

job_id = sys.argv[1]

batch = boto3.client('batch', region_name='us-east-1')
ecs = boto3.client('ecs', region_name='us-east-1')
ec2 = boto3.client('ec2', region_name='us-east-1')
ssm = boto3.client('ssm', region_name='us-east-1')

print(f"📡 Resolving AWS Batch Job: {job_id}...")
resp = batch.describe_jobs(jobs=[job_id])
if not resp['jobs']:
    print(f"❌ Could not find Job: {job_id}")
    sys.exit(1)

job = resp['jobs'][0]
task_arn = job['container']['taskArn']
cluster_arn = job['container'].get('containerInstanceArn')

if not cluster_arn:
    # Safely get cluster from task definition if needed
    cluster_name = task_arn.split('/')[1]
    task_desc = ecs.describe_tasks(cluster=cluster_name, tasks=[task_arn])
    cluster_arn = task_desc['tasks'][0]['containerInstanceArn']

ecs_cluster = task_arn.split('/')[1]
inst_desc = ecs.describe_container_instances(cluster=ecs_cluster, containerInstances=[cluster_arn])
ec2_instance_id = inst_desc['containerInstances'][0]['ec2InstanceId']

print(f"✅ Mapped to EC2 Instance: {ec2_instance_id}")

shell_cmd = f"""
CONT_ID=$(docker ps -q --filter label=com.amazonaws.ecs.task-arn={task_arn})
echo "--- FILE TYPE CHECK ---"
docker exec $CONT_ID ls -l /tmp/nxf.YwIaoTQ6yR/input*.fastq
echo ""
echo "--- PROCESS TREE CHECK ---"
docker exec $CONT_ID ps auxfw
"""

try:
    ssm_resp = ssm.send_command(
        InstanceIds=[ec2_instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [shell_cmd]}
    )
except ClientError as e:
    if e.response['Error']['Code'] == 'AccessDeniedException':
        print("\n⚠️ IAM Security Block: SSM send_command AccessDenied.")
        print("Falling back to passive EC2 instance discovery...")
        ec2_resp = ec2.describe_instances(InstanceIds=[ec2_instance_id])
        inst = ec2_resp['Reservations'][0]['Instances'][0]
        lifecycle = inst.get('InstanceLifecycle', 'on-demand')
        print(f"✅ Telemetry Fallback -> Instance: {inst['InstanceType']} | Lifecycle: {lifecycle}")
        sys.exit(0)
    raise
cmd_id = ssm_resp['Command']['CommandId']

while True:
    time.sleep(2)
    inv = ssm.get_command_invocation(CommandId=cmd_id, InstanceId=ec2_instance_id)
    if inv['Status'] in ['Success', 'Failed']:
        print(inv.get('StandardOutputContent', ''))
        if inv['Status'] == 'Failed':
            print(inv.get('StandardErrorContent', ''))
        break
