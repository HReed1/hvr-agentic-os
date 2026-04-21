from api.batch_submitter import submit_genomic_job

def test_submit_genomic_job_dispatch():
    # Test dispatch logic and fallback
    assert submit_genomic_job("unknown", 16, 4, "low", True) == "queue_fallback"
    assert submit_genomic_job("variant_calling", 16, 4, "low", True) == "queue_default"
    assert submit_genomic_job("qc", 16, 4, "critical", False) == "queue_priority_critical_qc"

def test_submit_genomic_job_variant_calling():
    # Test specific path in _handle_variant_calling
    assert submit_genomic_job("variant_calling", 64, 32, "high", True) == "queue_spot_high_vc"
    assert submit_genomic_job("variant_calling", 64, 32, "critical", False) == "queue_ondemand_crit_vc"

def test_submit_genomic_job_alignment():
    # Test specific path in _handle_alignment
    assert submit_genomic_job("alignment", 64, 4, "low", True) == "queue_spot_high_align"
    assert submit_genomic_job("alignment", 16, 4, "high", False) == "queue_ondemand_high_align"
