#!/bin/bash

# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics

# Parse arguments
PROFILE="awsbatch"
for arg in "$@"; do
    if [[ "$arg" == "--priority" || "$arg" == "--ondemand" ]]; then
        PROFILE="awsbatch_ondemand"
        echo "🚨 Priority flag detected. Using On-Demand infrastructure."
    fi
done

# Execution Profile Initialization Let's Go
echo "🔗 Booting AWS Batch Stateless Executors: Zero-Trust S3 Polling Architecture..."

# Closed-Loop FinOps Config Ingestion
NEXTFLOW_OPTS=""
if [ -f "finops_optimized.config" ]; then
    echo "💡 FinOps Profiler Active: Absorbing Closed-Loop hardware constraints from finops_optimized.config..."
    NEXTFLOW_OPTS="-c finops_optimized.config"
fi

# Execute the pipeline
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
nextflow run "$PROJECT_ROOT/src/pipelines/main.nf" $NEXTFLOW_OPTS -with-trace execution_trace.csv "$@"

# Autonomous EC2 Hardware Analytics Engine
if [ -f "execution_trace.csv" ]; then
    echo "🧠 Generating Autonomous EC2 FinOps Profile..."
    python "$PROJECT_ROOT/etl/jobs/finops_profiler.py" execution_trace.csv
fi
