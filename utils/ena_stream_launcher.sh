#!/bin/bash

# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics

BUCKET="s3://ngs-variant-validator-work-816549818028/seqc2"
PROFILE="admin"

echo "Started streaming SEQC2 Normal (HCC1395BL) Run 1 (SRR7890827_1) to S3..."
curl -s ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR789/007/SRR7890827/SRR7890827_1.fastq.gz | AWS_PROFILE=$PROFILE aws s3 cp - $BUCKET/normal_R1.fastq.gz --expected-size 48813880638

echo "Started streaming SEQC2 Normal (HCC1395BL) Run 2 (SRR7890827_2) to S3..."
curl -s ftp://ftp.sra.ebi.ac.uk/vol1/fastq/SRR789/007/SRR7890827/SRR7890827_2.fastq.gz | AWS_PROFILE=$PROFILE aws s3 cp - $BUCKET/normal_R2.fastq.gz --expected-size 53911612296

echo "Finished streaming normal reads!"
