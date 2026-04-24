def get_variant_calling_queue(memory, vcpus, priority, use_spot):
    if memory <= 32:
        return "queue_default"
    if vcpus < 16:
        return "queue_ondemand_low_vc"
    if use_spot:
        return {"high": "queue_spot_high_vc"}.get(priority, "queue_spot_std_vc")
    return {"critical": "queue_ondemand_crit_vc"}.get(priority, "queue_ondemand_std_vc")

def get_alignment_queue(memory, vcpus, priority, use_spot):
    if not use_spot:
        return {"high": "queue_ondemand_high_align"}.get(priority, "queue_ondemand_std_align")
    if memory >= 64:
        return "queue_spot_high_align"
    return {True: "queue_spot_std_align"}.get(vcpus > 8, "queue_spot_low_align")

def get_qc_queue(memory, vcpus, priority, use_spot):
    if priority == "low":
        return {True: "queue_spot_qc"}.get(use_spot, "queue_ondemand_qc")
    return {"critical": "queue_priority_critical_qc"}.get(priority, "queue_priority_qc")

def get_fallback_queue(memory, vcpus, priority, use_spot):
    return "queue_fallback"

def submit_genomic_job(job_type, memory, vcpus, priority, use_spot):
    dispatch = {
        "variant_calling": get_variant_calling_queue,
        "alignment": get_alignment_queue,
        "qc": get_qc_queue
    }
    return dispatch.get(job_type, get_fallback_queue)(memory, vcpus, priority, use_spot)
