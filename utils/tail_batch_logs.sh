#!/bin/bash
# Description: Dynamically extracts real-time CloudWatch telemetry for active Somatic Scatter Arrays natively.
set -e

QUEUE="somatic-cpu-queue"
TARGET_JOB="SPLIT_FASTQ_BATCH"

echo "📡 Scanning AWS Batch queue '$QUEUE' for active $TARGET_JOB instances..."

# Fetch all RUNNING job IDs that contain our Scatter-Gather target name
JOB_IDS=$(aws --profile admin batch list-jobs --job-queue "$QUEUE" --job-status RUNNING --query "jobSummaryList[?contains(jobName, '$TARGET_JOB')].jobId" --output text)

if [ -z "$JOB_IDS" ] || [ "$JOB_IDS" == "None" ]; then
    echo "⚠️ No running $TARGET_JOB operations detected."
    exit 0
fi

counter=1
for JOB_ID in $JOB_IDS; do
    echo "--------------------------------------------------------"
    echo "🔍 Intercepting CloudWatch Array for Job ID: $JOB_ID"
    
    # Resolve the internal CloudWatch Log Stream Index mapping to the Batch Container
    LOG_STREAM=$(aws --profile admin batch describe-jobs --jobs "$JOB_ID" --query "jobs[0].container.logStreamName" --output text)
    
    if [ "$LOG_STREAM" != "None" ] && [ -n "$LOG_STREAM" ]; then
        echo "📥 Downloading telemetry stream: $LOG_STREAM"
        
        # Download the full active tail matrix and map native string boundaries via jq
        aws --profile admin logs get-log-events \
            --log-group-name /aws/batch/job \
            --log-stream-name "$LOG_STREAM" \
            --output json | jq -r '.events[].message' > "somatic_batch_${counter}.log"
            
        echo "✅ Saved output natively to: somatic_batch_${counter}.log"
        counter=$((counter + 1))
    else
        echo "⏳ Telemetry Stream Not Yet Initialized for Job $JOB_ID"
    fi
done

echo "--------------------------------------------------------"
echo "🚀 CloudWatch Synchronization Complete!"
