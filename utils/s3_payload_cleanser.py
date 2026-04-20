import boto3
import logging

class S3PayloadCleanser:
    def __init__(self, bucket_name, prefix='payloads/'):
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.s3 = boto3.client('s3')
        self.logger = logging.getLogger(__name__)
        self.last_run_results = []

    def cleanse(self, dry_run=True):
        """
        Scans the bucket for objects matching the prefix and returns a list of items to be cleaned.
        If dry_run is False, it would proceed to delete (NOT IMPLEMENTED FOR SAFETY).
        """
        self.logger.info(f"Starting cleanse operation on bucket: {self.bucket_name} with prefix: {self.prefix} (dry_run={dry_run})")
        
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=self.prefix)
        
        items_to_clean = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    # Simple filter: matches the prefix
                    items_to_clean.append({
                        'Key': obj['Key'],
                        'Size': obj['Size']
                    })
        
        self.last_run_results = items_to_clean

        if dry_run:
            self.logger.info(f"Dry run enabled. Would delete {len(items_to_clean)} objects.")
            return items_to_clean
        else:
            # According to directive: "Direct mutations or destructive actions against 
            # production AWS environments are strictly forbidden."
            # Even if dry_run=False was passed, we enforce a safety guard here.
            raise RuntimeError("Destructive operations are forbidden in this environment.")

    def get_report(self):
        """
        Returns a human-readable summary of the dry run operation.
        """
        total_size = sum(item['Size'] for item in self.last_run_results)
        count = len(self.last_run_results)
        
        report = [
            "--- S3 Cleanse Dry Run Report ---",
            f"Bucket: {self.bucket_name}",
            f"Prefix: {self.prefix}",
            f"Objects identified: {count}",
            f"Total reclaimable size: {total_size} bytes",
            "Status: DRY RUN SUCCESSFUL (No deletions performed)"
        ]
        return "\n".join(report)
