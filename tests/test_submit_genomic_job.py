import pytest

def test_submit_genomic_job_mapping():
    from api.batch_submitter import submit_genomic_job
    # Test a few paths to ensure logic consistency after refactor
    assert submit_genomic_job("variant_calling", 64, 32, "high", True) == "queue_spot_high_vc"
    assert submit_genomic_job("alignment", 64, 8, "high", True) == "queue_spot_high_align"
    assert submit_genomic_job("qc", 8, 8, "low", True) == "queue_spot_qc"
    assert submit_genomic_job("unknown", 0, 0, "low", False) == "queue_fallback"
