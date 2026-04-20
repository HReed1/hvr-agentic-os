#!/bin/bash
# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics
# Diagnostic script to audit locally cached Nextflow SUCCEEDED/FAILED nodes natively from AWS Batch.

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

source venv/bin/activate || { echo -e "${RED}Failed to source venv.${NC}"; exit 1; }

QUEUES="somatic-gpu-ondemand-queue somatic-gpu-queue somatic-cpu-ondemand-queue ngs-spot-queue somatic-cpu-queue"
STATES="FAILED SUCCEEDED"

echo -e "${CYAN}📡 Polling AWS Batch Job Queues for recently concluded Nextflow DAG orchestrations...${NC}\n"

FOUND_JOBS=false

for q in $QUEUES; do
    for state in $STATES; do
        JOBS=$(aws --profile admin batch list-jobs --job-queue "$q" --job-status "$state" --query "jobSummaryList[*].[jobName, jobId, status, startedAt, stoppedAt]" --output text 2>/dev/null | head -n 10)
        
        if [ -n "$JOBS" ] && [ "$JOBS" != "None" ]; then
            FOUND_JOBS=true
            echo -e "${YELLOW}► Queue: $q | Terminal State: $state${NC} (Showing up to 10 most recent)"
            
            echo "$JOBS" | awk -F'\t' -v state_val="$state" '{
                status_color = (state_val == "FAILED") ? "\033[0;31m" : "\033[0;32m"
                reset_color = "\033[0m"
                
                # Check if startedAt and stoppedAt are valid integers
                if ($4 != "None" && $4 != "" && $5 != "None" && $5 != "") {
                    dur_s = int(($5 - $4) / 1000)
                    dur_str = sprintf("%dm %ds", int(dur_s / 60), dur_s % 60)
                } else {
                    dur_str = "N/A (Crashed early)"
                }
                
                printf "  ↳ Job: %-45s | ID: %-38s | Status: %s%-10s%s | Execution Time: %s\n", $1, $2, status_color, $3, reset_color, dur_str
            }'
            echo ""
        fi
    done
done

if [ "$FOUND_JOBS" = false ]; then
    echo -e "${GREEN}✅ No recent successes or failures found within the 24-hour job horizon.${NC}"
fi
echo ""
