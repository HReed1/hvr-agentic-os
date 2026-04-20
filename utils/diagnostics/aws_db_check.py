import boto3
import time

session = boto3.Session(profile_name='admin', region_name='us-east-1')
ssm = session.client('ssm')
ec2 = session.client('ec2')

reservations = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['Somatic-Head-Node']}, {'Name': 'instance-state-name', 'Values': ['running']}])
iid = reservations['Reservations'][0]['Instances'][0]['InstanceId']

cmds = [
    "docker exec pipeline_postgres_local psql -U postgres -d pipeline_db -c '\du'",
    "docker exec pipeline_postgres_local psql -U postgres -d pipeline_db -c '\dt'"
]

resp = ssm.send_command(InstanceIds=[iid], DocumentName="AWS-RunShellScript", Parameters={'commands': cmds})
cmd_id = resp['Command']['CommandId']

while True:
    r = ssm.get_command_invocation(CommandId=cmd_id, InstanceId=iid)
    if r['Status'] not in ['Pending', 'InProgress']:
        print("STATUS:", r['Status'])
        print(r.get('StandardOutputContent', ''))
        if r.get('StandardErrorContent'):
            print("ERROR", r.get('StandardErrorContent'))
        break
    time.sleep(2)
