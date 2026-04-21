def get_vc_queue(memory, vcpus, priority, use_spot):
    if memory <= 32: return "queue_default"
    if vcpus < 16: return "queue_ondemand_low_vc"
    if use_spot: return "queue_spot_high_vc" if priority == "high" else "queue_spot_std_vc"
    return "queue_ondemand_crit_vc" if priority == "critical" else "queue_ondemand_std_vc"

def get_alignment_queue(memory, vcpus, priority, use_spot):
    if not use_spot: return "queue_ondemand_high_align" if priority == "high" else "queue_ondemand_std_align"
    if memory >= 64: return "queue_spot_high_align"
    return "queue_spot_std_align" if vcpus > 8 else "queue_spot_low_align"

def get_qc_queue(memory, vcpus, priority, use_spot):
    if priority == "low": return "queue_spot_qc" if use_spot else "queue_ondemand_qc"
    return "queue_priority_critical_qc" if priority == "critical" else "queue_priority_qc"

def submit_genomic_job(job_type, memory, vcpus, priority, use_spot):
    strategies = {
        "variant_calling": get_vc_queue,
        "alignment": get_alignment_queue,
        "qc": get_qc_queue
    }
    strategy = strategies.get(job_type)
    if not strategy: return "queue_fallback"
    return strategy(memory, vcpus, priority, use_spot)
