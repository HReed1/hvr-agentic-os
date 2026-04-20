#!/bin/bash

# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics
# This script is meant to execute strictly on the Persistent EC2 Head Node natively via `cron`.

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 Initializing Native EC2 Head-Node S3 Backup...${NC}"

# Parameters mapped to the Dockerized Postgres Container 
# (Since it executes physically on the Head Node, it connects natively to localhost Docker limits)
export PGPASSWORD="local_dev_password"
DB_USER="postgres"
DB_NAME="pipeline_db"

# Dynamically calculate the secure AWS Account Project Bucket
PROJECT=$(aws sts get-caller-identity --query "Account" --output text)
S3_BUCKET="s3://ngs-variant-validator-work-${PROJECT}/backups"
DUMP_FILE="cloud_snapshot_$(date +%F_%H-%M-%S).sql.gz"

echo -e "Extracting Head-Node Database into Native Zip..."
pg_dump -h localhost -p 5432 -U $DB_USER $DB_NAME | gzip > "$DUMP_FILE"

echo -e "Streaming ${DUMP_FILE} securely to ${S3_BUCKET}..."
aws s3 cp "$DUMP_FILE" "${S3_BUCKET}/${DUMP_FILE}"

echo -e "Cleaning up temporary local drive footprints..."
rm "$DUMP_FILE"

echo -e "${GREEN}✅ Database successfully secured to deep AWS S3 storage!${NC}"
