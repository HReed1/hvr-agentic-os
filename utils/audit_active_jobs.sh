#!/bin/bash
# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics
# Real-Time Nextflow DAG execution Poller for AWS Batch

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

source venv/bin/activate || { echo -e "Failed to source venv."; exit 1; }

QUEUES="somatic-gpu-ondemand-queue somatic-gpu-queue somatic-cpu-ondemand-queue ngs-spot-queue somatic-cpu-queue"
STATES="RUNNING STARTING RUNNABLE PENDING SUBMITTED"

echo -e "${CYAN}📡 Polling Nextflow DAG nodes across AWS Batch Job Queues...${NC}\n"

FOUND_JOBS=false

for q in $QUEUES; do
    for state in $STATES; do
        # Pull raw tab-delimited job summaries from the AWS CLI with time metrics
        JOBS=$(aws --profile admin batch list-jobs --job-queue "$q" --job-status "$state" --query "jobSummaryList[*].[jobName, jobId, status, createdAt, startedAt]" --output text 2>/dev/null)
        
        if [ -n "$JOBS" ] && [ "$JOBS" != "None" ]; then
            FOUND_JOBS=true
            echo -e "${YELLOW}► Queue: $q | State: $state${NC}"
            
            # Fetch current time locally in MS
            CURRENT_MS=$(python3 -c "import time; print(int(time.time() * 1000))")
            
            echo "$JOBS" | awk -F'\t' -v curr="$CURRENT_MS" '{
                if ($5 != "None" && $5 != "") {
                    dur_s = int((curr - $5) / 1000)
                } else if ($4 != "None" && $4 != "") {
                    dur_s = int((curr - $4) / 1000)
                } else {
                    dur_s = 0
                }
                
                dur_str = sprintf("%dm %ds", int(dur_s / 60), dur_s % 60)
                
                printf "  ↳ Job: %-55s | ID: %-38s | Status: %-10s | Time in State: %s\n", $1, $2, $3, dur_str
            }'
            echo ""
        fi
    done
done

if [ "$FOUND_JOBS" = false ]; then
    echo -e "${GREEN}✅ No active Nextflow orchestration nodes running in the AWS Batch environment.${NC}"
fi
echo ""
