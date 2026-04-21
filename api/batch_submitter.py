def _handle_variant_calling(memory, vcpus, priority, use_spot):
    if memory <= 32:
        return "queue_default"
    if vcpus < 16:
        return "queue_ondemand_low_vc"
    if use_spot:
        return "queue_spot_high_vc" if priority == "high" else "queue_spot_std_vc"
    return "queue_ondemand_crit_vc" if priority == "critical" else "queue_ondemand_std_vc"

def _handle_alignment(memory, vcpus, priority, use_spot):
    if use_spot:
        if memory >= 64:
            return "queue_spot_high_align"
        return "queue_spot_std_align" if vcpus > 8 else "queue_spot_low_align"
    return "queue_ondemand_high_align" if priority == "high" else "queue_ondemand_std_align"

def _handle_qc(memory, vcpus, priority, use_spot):
    if priority == "low":
        return "queue_spot_qc" if use_spot else "queue_ondemand_qc"
    return "queue_priority_critical_qc" if priority == "critical" else "queue_priority_qc"

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
