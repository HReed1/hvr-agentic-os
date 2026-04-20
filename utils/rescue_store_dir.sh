#!/bin/bash
set -e

echo "Rescuing exactly identified cache files from Nextflow work/ into our global rescued_cache/ ..."

WORK_BUCKET="s3://ngs-variant-validator-work-816549818028/work"
RESCUE_BUCKET="s3://ngs-variant-validator-work-816549818028/rescued_cache"

echo "Copying Tumor and Normal Deduplicated BAMs..."
aws s3 cp ${WORK_BUCKET}/b5/408261e66e66524b102ce58fea2907/RUN-SEQC2-TUMOR_tumor_dedup.bam ${RESCUE_BUCKET}/RUN-SEQC2-TUMOR_tumor_dedup.bam
aws s3 cp ${WORK_BUCKET}/b5/408261e66e66524b102ce58fea2907/RUN-SEQC2-TUMOR_tumor_dedup.bam.bai ${RESCUE_BUCKET}/RUN-SEQC2-TUMOR_tumor_dedup.bam.bai

aws s3 cp ${WORK_BUCKET}/d8/35cca93cf5b9b94ef67d2bb70ded1c/RUN-SEQC2-TUMOR_normal_dedup.bam ${RESCUE_BUCKET}/RUN-SEQC2-TUMOR_normal_dedup.bam
aws s3 cp ${WORK_BUCKET}/d8/35cca93cf5b9b94ef67d2bb70ded1c/RUN-SEQC2-TUMOR_normal_dedup.bam.bai ${RESCUE_BUCKET}/RUN-SEQC2-TUMOR_normal_dedup.bam.bai

echo "Copying Mosdepth Coverage Distributions..."
aws s3 cp ${WORK_BUCKET}/13/0ecfd6d4028acea5747be94104ff36/RUN-SEQC2-TUMOR_tumor.mosdepth.global.dist.txt ${RESCUE_BUCKET}/RUN-SEQC2-TUMOR_tumor.mosdepth.global.dist.txt
aws s3 cp ${WORK_BUCKET}/13/0ecfd6d4028acea5747be94104ff36/RUN-SEQC2-TUMOR_tumor.regions.bed.gz ${RESCUE_BUCKET}/RUN-SEQC2-TUMOR_tumor.regions.bed.gz

aws s3 cp ${WORK_BUCKET}/23/8af817ac6b1f20a08f9985155222e7/RUN-SEQC2-TUMOR_normal.mosdepth.global.dist.txt ${RESCUE_BUCKET}/RUN-SEQC2-TUMOR_normal.mosdepth.global.dist.txt
aws s3 cp ${WORK_BUCKET}/23/8af817ac6b1f20a08f9985155222e7/RUN-SEQC2-TUMOR_normal.regions.bed.gz ${RESCUE_BUCKET}/RUN-SEQC2-TUMOR_normal.regions.bed.gz

echo "--------------------------------------------------------"
echo "Rescue complete. All files materialized locally in S3."
echo "You can now launch the pipeline passing parameters:"
echo "--starting_step call_variants --rescued_cache_dir ${RESCUE_BUCKET}"
