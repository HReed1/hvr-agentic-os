process GET_PARABRICKS_HELP {
    container '816549818028.dkr.ecr.us-east-1.amazonaws.com/ngs-alignment:v2.0.0'
    queue 'somatic-gpu-ondemand-queue'
    accelerator 1, type: 'nvidia'

    script:
    """
    pbrun fq2bam -h > parabricks_help.txt 2>&1 || true
    aws s3 cp parabricks_help.txt s3://ngs-variant-validator-work-816549818028/docs-cache/parabricks_help.txt
    """
}

process GET_DEEPSOMATIC_HELP {
    container '816549818028.dkr.ecr.us-east-1.amazonaws.com/ngs-deepsomatic:v1.5.0'
    queue 'somatic-cpu-ondemand-queue'

    script:
    """
    run_deepsomatic --help > deepsomatic_help.txt 2>&1 || true
    aws s3 cp deepsomatic_help.txt s3://ngs-variant-validator-work-816549818028/docs-cache/deepsomatic_help.txt
    """
}

workflow { 
    GET_PARABRICKS_HELP()
    GET_DEEPSOMATIC_HELP()
}I don't know