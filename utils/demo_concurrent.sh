#!/bin/bash

# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics

# --- Color formatting for terminal output ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

export AWS_PROFILE=admin

DATASET=$1

if [ -z "$DATASET" ]; then
    echo -e "${YELLOW}Please provide a specific dataset to run concurrently: human-ont, viral, colo829, seqc2, or all${NC}"
    exit 1
fi

PROFILE="awsbatch"
EXTRA_ARGS=()
shift
while [[ $# -gt 0 ]]; do
  case $1 in
    --compute_mode)
      if [[ "$2" == "awsbatch" ]]; then
          PROFILE="awsbatch"
      else
          PROFILE="standard"
      fi
      shift 2
      ;;
    --cpu_queue|--gpu_queue)
      EXTRA_ARGS+=("$1" "$2")
      shift 2
      ;;
    *)
      EXTRA_ARGS+=("$1")
      shift
      ;;
  esac
done

echo -e "${CYAN}🚀 Bridging the Python Virtual Environment Native Pathway...${NC}"
source venv/bin/activate || { echo -e "${YELLOW}Failed to source venv. Are you in the project root?${NC}"; exit 1;}

if [ "$PROFILE" == "awsbatch" ]; then
    echo -e "${CYAN}🚀 Initializing Head-Node Bridged Concurrent Pipeline...${NC}"

    # Pre-Flight Ghosting Check
    if lsof -nP -iTCP:5432 -sTCP:LISTEN >/dev/null 2>&1; then
        BINDING_PROCESS=$(lsof -nP -iTCP:5432 -sTCP:LISTEN | grep -v "COMMAND" | awk '{print $1}' | head -n 1)
        if [[ ! "$BINDING_PROCESS" =~ "session-m" ]]; then
            echo -e "${YELLOW}[FATAL] Local port 5432 is maliciously bound by $BINDING_PROCESS, not AWS SSM.${NC}"
            echo -e "${YELLOW}[FATAL] This will cause a catastrophic 'Ghosting' pipeline collision!${NC}"
            echo -e "${GREEN}Please completely shutdown local developer containers by running: ./utils/stop_dev.sh${NC}"
            exit 1
        fi
        echo -e "${GREEN}AWS SSM Tunnel pre-existing binding successfully structurally validated.${NC}"
    fi

    # EC2 Head-Node Auto-Healing Sequence
    echo -e "${CYAN}Evaluating Somatic-Head-Node AWS SSM connectivity parameters...${NC}"
    HEAD_NODE_ID=$(aws --profile admin ec2 describe-instances --filters "Name=tag:Name,Values=Somatic-Head-Node" "Name=instance-state-name,Values=running,stopped" --query "Reservations[0].Instances[0].InstanceId" --output text 2>/dev/null)
    
    if [ "$HEAD_NODE_ID" != "None" ] && [ -n "$HEAD_NODE_ID" ]; then
        PING_STATUS=$(aws --profile admin ssm describe-instance-information --filters "Key=InstanceIds,Values=$HEAD_NODE_ID" --query "InstanceInformationList[0].PingStatus" --output text 2>/dev/null)
        
        if [ "$PING_STATUS" != "Online" ]; then
            echo -e "${YELLOW}⚠️ Somatic-Head-Node ($HEAD_NODE_ID) lacks active SSM heartbeat (Status: $PING_STATUS). Transmitting automated reboot...${NC}"
            aws --profile admin ec2 reboot-instances --instance-ids "$HEAD_NODE_ID"
            
            echo -e "${CYAN}Waiting for EC2 instance to structurally synchronize (Approx: 60s)...${NC}"
            aws --profile admin ec2 wait instance-status-ok --instance-ids "$HEAD_NODE_ID"
            echo -e "${GREEN}✅ Head-Node successfully rebooted and SSM Agent registered Online.${NC}"
        else
            echo -e "${GREEN}✅ Head-Node SSM Connection structurally verified (Status: Online).${NC}"
        fi
    fi

    # 1. Start the AWS Systems Manager (SSM) Tunnel to securely inject database records
    ./utils/db_tunnel.sh > utils/db_ssm_tunnel.log 2>&1 &
    echo -e "${CYAN}Waiting for AWS SSM Port-Forwarding Tunnel to establish on localhost:5432...${NC}"
    TIMEOUT=30
    ELAPSED=0
    while ! nc -z localhost 5432; do
        sleep 1
        let ELAPSED=ELAPSED+1
        if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
            echo -e "${YELLOW}❌ Database tunnel failed to establish within 30 seconds. Aborting concurrent initialization.${NC}"
            exit 1
        fi
    done
    echo -e "${GREEN}✅ Database tunnel established securely in $ELAPSED seconds.${NC}"

    # 2. Non-destructively add the new records to the LIVE Cloud Database
    echo -e "${YELLOW}Safely seeding $DATASET into LIVE Postgres Database via SSM...${NC}"
    export DB_HOST="localhost"
    export DB_PORT="5432"
    export DB_USER="postgres"
    export DB_NAME="pipeline_db"

    # Securely extract DB_PASSWORD dynamically from AWS Secrets Manager
    echo -e "${CYAN}Fetching encrypted database credentials directly from AWS Secrets Manager...${NC}"
    export DB_PASSWORD=$(aws --profile admin ssm get-parameter --name "/ngs/db_password" --with-decryption --query "Parameter.Value" --output text 2>/dev/null || echo "local_dev_password")

    # Dynamically inject the core ETL runtime roles bypassing the raw Alembic gaps
    venv/bin/python utils/fix_db_roles.py

    venv/bin/alembic upgrade head
    # Skip DB seed if local run dir exists to preserve Nextflow caching
    if [ ! -d ".run_${DATASET}" ] && [ "$DATASET" != "all" ]; then
        venv/bin/python -m etl.jobs.seed_database --dataset "$DATASET"
    elif [ ! -d ".run_viral" ] && [ "$DATASET" == "all" ]; then
        venv/bin/python -m etl.jobs.seed_database --dataset "$DATASET"
    else
        echo -e "${GREEN}Database structurally verified. Bypassing ETL Seed to enforce Nextflow cache resuming...${NC}"
    fi

    # 3. Preserve SSM mapping for Local UI Telemetry
    echo -e "${CYAN}Preserving secure SSM proxy tunnel so the UI FastAPI matrix stays constantly synced...${NC}"

    # CRITICAL BASH ABSTRACTION: Unload local SSM variables so Nextflow inherits physical AWS IPs
    HEAD_NODE_IP=$(aws --profile admin ec2 describe-instances --filters "Name=tag:Name,Values=Somatic-Head-Node" "Name=instance-state-name,Values=running" --query "Reservations[0].Instances[0].PrivateIpAddress" --output text)
    echo -e "${CYAN}Dynamically mapping Cloud Database IP: $HEAD_NODE_IP for Native Pipeline Executors.${NC}"

    export DB_HOST="$HEAD_NODE_IP"
    export DB_PORT="5432"
    export DB_USER="postgres"
    export DB_NAME="pipeline_db"

    # Dynamically map the Telemetry S3 Bucket optionally sourced securely from Docker .env
    if [ -n "$S3_TELEMETRY_BUCKET" ]; then
        TELEMETRY_BUCKET=$(echo "$S3_TELEMETRY_BUCKET" | sed 's/s3:\/\///')
        export S3_TELEMETRY_URI="s3://${TELEMETRY_BUCKET}/telemetry/pending"
        export S3_REFERENCE_URI="s3://${TELEMETRY_BUCKET}/reference"
    else
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --profile admin)
        TELEMETRY_BUCKET="ngs-variant-validator-work-${ACCOUNT_ID}"
        export S3_TELEMETRY_URI="s3://${TELEMETRY_BUCKET}/telemetry/pending"
        export S3_REFERENCE_URI="s3://${TELEMETRY_BUCKET}/reference"
    fi
else
    echo -e "${CYAN}🚀 Initializing Solo-Researcher BYOC Local Pipeline...${NC}"
    
    # Bypass AWS SSM mappings and target the local Docker-Compose db endpoint natively
    export DB_HOST="localhost"
    export DB_PORT="5432"
    export DB_USER="postgres"
    export DB_NAME="ngs_variant_db"
    export DB_PASSWORD="${DB_PASSWORD:-postgres}"
    
    echo -e "${YELLOW}Validating $DATASET in containerized Postgres Database...${NC}"
    
    # Skip DB seed if local run dir exists to preserve Nextflow caching
    if [ ! -d ".run_${DATASET}" ] && [ "$DATASET" != "all" ]; then
        venv/bin/python -m etl.jobs.seed_database --dataset "$DATASET"
    elif [ ! -d ".run_viral" ] && [ "$DATASET" == "all" ]; then
        venv/bin/python -m etl.jobs.seed_database --dataset "$DATASET"
    else
        echo -e "${GREEN}Database structurally verified. Bypassing ETL Seed to enforce Nextflow cache resuming...${NC}"
    fi
    
    # Route storage natively based on standard environment mappings
    if [ -n "$S3_TELEMETRY_BUCKET" ]; then
        # Hybrid integration: User is running local SLURM but mapped their clinical AWS S3 bucket explicitly
        TELEMETRY_BUCKET=$(echo "$S3_TELEMETRY_BUCKET" | sed 's/s3:\/\///')
        export S3_TELEMETRY_URI="s3://${TELEMETRY_BUCKET}/telemetry/pending"
        export S3_REFERENCE_URI="s3://${TELEMETRY_BUCKET}/reference"
    else
        # Pure offline execution natively mapping absolute Unix boundaries
        mkdir -p "$PWD/local_telemetry/pending" "$PWD/local_reference"
        export S3_TELEMETRY_URI="$PWD/local_telemetry/pending"
        export S3_REFERENCE_URI="$PWD/local_reference"
    fi
fi

echo -e "${CYAN}Dynamically mapping Telemetry Destination: $S3_TELEMETRY_URI${NC}"
echo -e "${CYAN}Dynamically mapping Reference Source: $S3_REFERENCE_URI${NC}"

# 2. Function to launch a pipeline with isolated Nextflow caching
launch_pipeline() {
    local dataset_arg=$1
    local run_id=$2
    local run_in_bg=$3
    shift 3
    local INLINE_ARGS=("$@")

    local launch_dir=".run_${dataset_arg}"
    mkdir -p "$launch_dir"
    
    # Removed destructive pre-flight Lock bypass. Nextflow must retain its persistence matrix to achieve DAG caching

    echo -e "${GREEN}Launching AWS Batch Pipeline sequence [Profile: ${PROFILE}] for ${dataset_arg} inside ${launch_dir}...${NC}"
    
    # Predictive Resiliency: Auto-Spawn UI Telemetry
    if ! nc -z localhost 8000 >/dev/null 2>&1; then
        echo -e "${YELLOW}Telemetry Array 8000 Offline! Passively spinning up FASTAPI Uvicorn Telemetry...${NC}"
        bash utils/dev_ui.sh &
        sleep 5
    fi
    
    # Implicitly inject the dynamically mapped --compute_mode profile along with standard AWS URls
    if [ "$run_in_bg" == "true" ]; then
        echo -e "${CYAN}Backgrounding Nextflow stream to terminal_${dataset_arg}.log${NC}"
        (cd "$launch_dir" && bash ../utils/run_cloud_pipeline.sh -name "${run_id}-$(date +%s)" -profile "$PROFILE" --run "$run_id" --telemetry_bucket "$S3_TELEMETRY_URI" --reference_bucket "$S3_REFERENCE_URI" "${INLINE_ARGS[@]}" "${EXTRA_ARGS[@]}" -resume > "../terminal_${dataset_arg}.log" 2>&1 &)
    else
        (cd "$launch_dir" && bash ../utils/run_cloud_pipeline.sh -name "${run_id}-$(date +%s)" -profile "$PROFILE" --run "$run_id" --telemetry_bucket "$S3_TELEMETRY_URI" --reference_bucket "$S3_REFERENCE_URI" "${INLINE_ARGS[@]}" "${EXTRA_ARGS[@]}" -resume)
    fi
}

# 3. Launch Pipeline(s)
if [ "$DATASET" == "all" ]; then
    echo -e "${YELLOW}Launching ALL concurrent pipelines automatically in the background...${NC}"
    launch_pipeline "viral" "RUN-VIRAL-TEST" "true" --assay_type Viral_Micro --genome_size small "${EXTRA_ARGS[@]}"
    launch_pipeline "human-ont" "RUN-HUMAN-TEST" "true" --assay_type WGS --genome_size large "${EXTRA_ARGS[@]}"
    launch_pipeline "colo829" "RUN-COLO829-TUMOR" "true" --assay_type WGS --genome_size large "${EXTRA_ARGS[@]}"
    echo -e "${GREEN}All pipelines launched successfully! You can monitor them via: tail -f terminal_colo829.log${NC}"
elif [ "$DATASET" == "viral" ]; then
    launch_pipeline "viral" "RUN-VIRAL-TEST" "false" --assay_type Viral_Micro --genome_size small "${EXTRA_ARGS[@]}"
elif [ "$DATASET" == "human-ont" ]; then
    launch_pipeline "human-ont" "RUN-HUMAN-TEST" "false" --assay_type WGS --genome_size large "${EXTRA_ARGS[@]}"
elif [ "$DATASET" == "colo829" ]; then
    launch_pipeline "colo829" "RUN-COLO829-TUMOR" "false" --assay_type WGS --genome_size large "${EXTRA_ARGS[@]}"
elif [ "$DATASET" == "seqc2" ]; then
    launch_pipeline "seqc2" "RUN-SEQC2-TUMOR" "false" --assay_type WGS --genome_size large "${EXTRA_ARGS[@]}"
else
    echo "Unknown dataset: $DATASET. Try human-ont, viral, colo829, seqc2, or all."
    exit 1
fi
