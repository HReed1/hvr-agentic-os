import pexpect
import sys
import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')
reservations = ec2.describe_instances(
    Filters=[
        {'Name': 'tag:Name', 'Values': ['Somatic-Head-Node']},
        {'Name': 'instance-state-name', 'Values': ['running']}
    ]
)
instance_id = reservations['Reservations'][0]['Instances'][0]['InstanceId']

print(f"Connecting to {instance_id}...")
child = pexpect.spawn(f'aws ssm start-session --target {instance_id}', encoding='utf-8')
child.expect(r'\$')
print("Connected! Running sudo su -")
child.sendline('sudo su -')
child.expect(r'#')

print("Fetching netstat...")
child.sendline('netstat -tuln | grep 5432')
child.expect(r'#')
print(child.before)

print("Checking docker ps...")
child.sendline('docker ps')
child.expect(r'#')
print(child.before)

print("Exiting...")
child.sendline('exit')
child.expect(r'\$')
child.sendline('exit')
child.expect(pexpect.EOF)
