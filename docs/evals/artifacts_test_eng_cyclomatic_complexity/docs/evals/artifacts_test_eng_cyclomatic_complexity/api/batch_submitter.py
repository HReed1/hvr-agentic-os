def _get_vc_queue(memory, vcpus, priority, use_spot):
    if memory <= 32:
        return "queue_default"
    if vcpus < 16:
        return "queue_ondemand_low_vc"
    
    if use_spot:
        return {True: "queue_spot_high_vc"}.get(priority == "high", "queue_spot_std_vc")
    return {True: "queue_ondemand_crit_vc"}.get(priority == "critical", "queue_ondemand_std_vc")

def _get_align_queue(memory, vcpus, priority, use_spot):
    if not use_spot:
        return {True: "queue_ondemand_high_align"}.get(priority == "high", "queue_ondemand_std_align")
    
    if memory >= 64:
        return "queue_spot_high_align"
        
    return {True: "queue_spot_std_align"}.get(vcpus > 8, "queue_spot_low_align")

def _get_qc_queue(memory, vcpus, priority, use_spot):
    if priority == "low":
        return {True: "queue_spot_qc"}.get(bool(use_spot), "queue_ondemand_qc")
    return {True: "queue_priority_critical_qc"}.get(priority == "critical", "queue_priority_qc")

def _get_fallback_queue(memory, vcpus, priority, use_spot):
    return "queue_fallback"

def submit_genomic_job(job_type, memory, vcpus, priority, use_spot):
    """
    Submits a job to AWS Batch.
    Refactored to maintain McCable Cyclomatic Complexity <= 5 via dictionary mapping.
    """
    dispatch_map = {
        "variant_calling": _get_vc_queue,
        "alignment": _get_align_queue,
        "qc": _get_qc_queue
    }
    handler = dispatch_map.get(job_type, _get_fallback_queue)
    return handler(memory, vcpus, priority, use_spot)
