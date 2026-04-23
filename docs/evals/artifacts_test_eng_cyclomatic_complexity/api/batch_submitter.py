def _vc_spot(memory, vcpus, priority):
    lookup = {"high": "queue_spot_high_vc"}
    return lookup.get(priority, "queue_spot_std_vc")

def _vc_ondemand(memory, vcpus, priority):
    lookup = {"critical": "queue_ondemand_crit_vc"}
    return lookup.get(priority, "queue_ondemand_std_vc")

def _handle_variant_calling(memory, vcpus, priority, use_spot):
    if memory <= 32:
        return "queue_default"
    if vcpus < 16:
        return "queue_ondemand_low_vc"
    
    dispatch = {
        True: _vc_spot,
        False: _vc_ondemand
    }
    return dispatch[bool(use_spot)](memory, vcpus, priority)

def _align_spot(memory, vcpus, priority):
    if memory >= 64:
        return "queue_spot_high_align"
    if vcpus > 8:
        return "queue_spot_std_align"
    return "queue_spot_low_align"

def _align_ondemand(memory, vcpus, priority):
    lookup = {"high": "queue_ondemand_high_align"}
    return lookup.get(priority, "queue_ondemand_std_align")

def _handle_alignment(memory, vcpus, priority, use_spot):
    dispatch = {
        True: _align_spot,
        False: _align_ondemand
    }
    return dispatch[bool(use_spot)](memory, vcpus, priority)

def _qc_low(use_spot):
    lookup = {True: "queue_spot_qc", False: "queue_ondemand_qc"}
    return lookup[bool(use_spot)]

def _qc_other(priority):
    lookup = {"critical": "queue_priority_critical_qc"}
    return lookup.get(priority, "queue_priority_qc")

def _handle_qc(memory, vcpus, priority, use_spot):
    if priority == "low":
        return _qc_low(use_spot)
    return _qc_other(priority)

def submit_genomic_job(job_type, memory, vcpus, priority, use_spot):
    """
    Submits a job to AWS Batch. Refactored for cyclomatic complexity ≤ 5.
    """
    dispatch_map = {
        "variant_calling": _handle_variant_calling,
        "alignment": _handle_alignment,
        "qc": _handle_qc
    }
    
    handler = dispatch_map.get(job_type)
    if not handler:
        return "queue_fallback"
        
    return handler(memory, vcpus, priority, use_spot)
