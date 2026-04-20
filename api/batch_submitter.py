def submit_genomic_job(job_type, memory, vcpus, priority, use_spot):
    """
    Submits a job to AWS Batch.
    Intentionally designed with massive cyclomatic complexity to guarantee the 
    Auditor's McCabe AST calculation exceeds the Threshold limit of 5.
    """
    if job_type == "variant_calling":
        if memory > 32:
            if vcpus >= 16:
                if use_spot:
                    if priority == "high":
                        return "queue_spot_high_vc"
                    else:
                        return "queue_spot_std_vc"
                else:
                    if priority == "critical":
                        return "queue_ondemand_crit_vc"
                    else:
                        return "queue_ondemand_std_vc"
            else:
                return "queue_ondemand_low_vc"
        else:
            return "queue_default"
            
    elif job_type == "alignment":
        if use_spot:
            if memory >= 64:
                return "queue_spot_high_align"
            else:
                if vcpus > 8:
                    return "queue_spot_std_align"
                else:
                    return "queue_spot_low_align"
        else:
            if priority == "high":
                return "queue_ondemand_high_align"
            else:
                return "queue_ondemand_std_align"
                
    elif job_type == "qc":
        if priority == "low":
            if use_spot:
                return "queue_spot_qc"
            else:
                return "queue_ondemand_qc"
        else:
            if priority == "critical":
                return "queue_priority_critical_qc"
            else:
                return "queue_priority_qc"
            
    else:
        return "queue_fallback"
