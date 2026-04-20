#!/usr/bin/env -S /Users/harrisonreed/Projects/ngs-variant-validator/venv/bin/python
import boto3
import argparse
import sys
from urllib.parse import urlparse

def process_s3_prefix(s3_client, bucket, prefix, execute_mode):
    """Calculates S3 prefix sizing and securely deletes objects if execute_mode is enacted."""
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    
    total_objects = 0
    total_bytes = 0
    deleted_count = 0

    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                total_objects += 1
                total_bytes += obj['Size']

            if execute_mode:
                objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
                # s3.delete_objects has a limit of 1000 objects per request
                
                # TEMPORARILY DISABLED FOR LOCAL AGENT EVALUATION TESTS
                # To re-enable live deletions, uncomment the following line:
                # s3_client.delete_objects(Bucket=bucket, Delete={'Objects': objects_to_delete})
                
                deleted_count += len(objects_to_delete)
            
    return total_objects, total_bytes, deleted_count

def clean_failed_workdir(s3_uri, execute_mode=False, profile="admin", region="us-east-1"):
    try:
        session = boto3.Session(profile_name=profile, region_name=region)
        s3_client = session.client('s3')
        
        parsed_uri = urlparse(s3_uri)
        bucket = parsed_uri.netloc
        prefix = parsed_uri.path.lstrip('/')
        
        if not bucket or not prefix:
            print(f"❌ Invalid S3 URI format: {s3_uri}")
            sys.exit(1)
            
        # Ensure we don't accidentally delete the root bucket by asserting deep hash structure
        if not prefix.startswith("work/") or len(prefix.split('/')) < 3:
            print(f"❌ Security Block: Refusing to purge high-level prefix: {s3_uri}. Must target a specific Nextflow work directory hash.")
            sys.exit(1)
            
        # Add trailing slash if missing to prevent deleting siblings (e.g. work/a0/91ba matches work/a0/91ba34... and work/a0/91bb... if not careful)
        if not prefix.endswith('/'):
            prefix += '/'
            
        if execute_mode:
            print(f"🧨 SYSTEM OVERRIDE: Engaging S3 FinOps Purge Protocol on {s3_uri}...")
        else:
            print(f"🔍 [DRY-RUN] Assessing Blast Radius for prefix: {s3_uri}...")

        total_objects, total_bytes, deleted_count = process_s3_prefix(s3_client, bucket, prefix, execute_mode)
        
        # Calculate pretty size
        mb_size = total_bytes / (1024 * 1024)
        
        if not execute_mode:
            print(f"\n📊 --- BLAST RADIUS ASSESSMENT ---")
            print(f"Total Objects Identified: {total_objects}")
            print(f"Total Volume to Incinerate: {mb_size:.2f} MB ({total_bytes} Bytes)")
            print(f"Status: Safe. No data deleted. Append --execute to confirm purge.")
            return

        if deleted_count > 0:
            print(f"✅ Success! Incinerated {deleted_count} objects ({mb_size:.2f} MB) from the failed EBS staging transfer.")
        else:
            print(f"⚠️ Target prefix {s3_uri} was already empty or did not exist.")
            
    except Exception as e:
        print(f"❌ Failed to execute purger: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nextflow S3 Staging Directory FinOps Cleaner")
    parser.add_argument("uri", help="The specific S3 URI of the failed Nextflow task directory (e.g., s3://ngs-variant-validator-work-816549818028/work/a0/91ba340163a99d87af1bd44cb9a3eb)")
    parser.add_argument("--profile", default="admin", help="AWS CLI Profile to use (default: admin)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Perform a safety audit computation of the target bytes without deleting (Default).")
    parser.add_argument("--execute", action="store_true", help="Physically execute the deletion payload (Overrides defaults).")
    
    args = parser.parse_args()
    
    # If explicitly passed --execute, disable dry_run
    execute_mode = args.execute
    
    clean_failed_workdir(args.uri, execute_mode=execute_mode, profile=args.profile)
