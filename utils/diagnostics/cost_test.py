import os
import boto3
from datetime import datetime, timedelta, timezone
import json
from dotenv import load_dotenv

load_dotenv()

finops_access_key = os.getenv("FINOPS_AWS_ACCESS_KEY_ID")
finops_secret_key = os.getenv("FINOPS_AWS_SECRET_ACCESS_KEY")

ce_client = boto3.client(
    'ce',
    aws_access_key_id=finops_access_key,
    aws_secret_access_key=finops_secret_key,
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# Expand the window aggressively to capture everything!
end_date = (datetime.now(timezone.utc) + timedelta(days=1)).date()
start_date = end_date - timedelta(days=30)

response = ce_client.get_cost_and_usage(
    TimePeriod={
        'Start': start_date.strftime('%Y-%m-%d'),
        'End': end_date.strftime('%Y-%m-%d')
    },
    Granularity='DAILY',
    Metrics=['UnblendedCost'],
    GroupBy=[
        {'Type': 'DIMENSION', 'Key': 'SERVICE'}
    ]
)

print(json.dumps(response['ResultsByTime'], indent=2))
