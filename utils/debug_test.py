import pytest
import sys
from unittest.mock import patch, MagicMock
from api.services.telemetry_sync import sync_telemetry_from_s3
import api.services.telemetry_sync as TS

def run_debug():
    with patch("api.services.telemetry_sync.boto3.client") as mock_boto, \
         patch("api.services.telemetry_sync.etl_engine") as mock_engine:
         
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "ngs-variant-validator-work-123"}]}
        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "telemetry/pending/RUN-TEST-001_qc_metrics.json"},
            ]
        }
        
        import json
        mock_body = MagicMock()
        mock_body.read.return_value = json.dumps({"status": "complete", "quality_profile": "A"}).encode('utf-8')
        mock_s3.get_object.return_value = {"Body": mock_body}
        
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_engine.begin.return_value = mock_conn
        
        mock_conn.execute.return_value.fetchone.side_effect = [
            True, False, []
        ]
        mock_conn.execute.return_value.fetchall.return_value = []
        
        import io
        captured = io.StringIO()
        sys.stdout = captured
        sync_telemetry_from_s3()
        sys.stdout = sys.__stdout__
        
        print("Captured output:")
        print(captured.getvalue())
        print(f"Call count: {mock_conn.execute.call_count}")

if __name__ == '__main__':
    run_debug()
