import pytest
from api.batch_submitter import submit_genomic_job

def test_variant_calling():
    assert submit_genomic_job('variant_calling', 64, 32, 'high', True) == 'queue_spot_high_vc'
    assert submit_genomic_job('variant_calling', 64, 32, 'normal', True) == 'queue_spot_std_vc'
    assert submit_genomic_job('variant_calling', 64, 32, 'critical', False) == 'queue_ondemand_crit_vc'
    assert submit_genomic_job('variant_calling', 64, 32, 'normal', False) == 'queue_ondemand_std_vc'
    assert submit_genomic_job('variant_calling', 64, 8, 'high', True) == 'queue_ondemand_low_vc'
    assert submit_genomic_job('variant_calling', 16, 32, 'high', True) == 'queue_default'

def test_alignment():
    assert submit_genomic_job('alignment', 128, 16, 'high', True) == 'queue_spot_high_align'
    assert submit_genomic_job('alignment', 32, 16, 'high', True) == 'queue_spot_std_align'
    assert submit_genomic_job('alignment', 32, 4, 'high', True) == 'queue_spot_low_align'
    assert submit_genomic_job('alignment', 128, 16, 'high', False) == 'queue_ondemand_high_align'
    assert submit_genomic_job('alignment', 128, 16, 'normal', False) == 'queue_ondemand_std_align'

def test_qc():
    assert submit_genomic_job('qc', 16, 4, 'low', True) == 'queue_spot_qc'
    assert submit_genomic_job('qc', 16, 4, 'low', False) == 'queue_ondemand_qc'
    assert submit_genomic_job('qc', 16, 4, 'critical', True) == 'queue_priority_critical_qc'
    assert submit_genomic_job('qc', 16, 4, 'high', True) == 'queue_priority_qc'

def test_fallback():
    assert submit_genomic_job('unknown', 16, 4, 'low', True) == 'queue_fallback'
