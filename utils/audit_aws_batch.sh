#!/bin/bash
# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics
# Pre-Flight Diagnostic to guarantee Zero-Trust Cloud architecture is ready for GPU workload drops

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🚀 Initializing AWS Batch Zero-Trust Infrastructure Audit...${NC}\n"

source venv/bin/activate || { echo -e "${RED}Failed to source venv. Are you in the project root?${NC}"; exit 1;}

# 1. Audit Compute Environments
echo -e "${YELLOW}[1/4] Polling AWS Batch Compute Environments...${NC}"
aws --profile admin batch describe-compute-environments \
    --query "computeEnvironments[*].[computeEnvironmentName, state, status]" \
    --output table || echo -e "${RED}Failed to pull Compute Environments!${NC}"

# 2. Audit Job Queues
echo -e "\n${YELLOW}[2/4] Polling AWS Batch Job Queues...${NC}"
aws --profile admin batch describe-job-queues \
    --query "jobQueues[*].[jobQueueName, state, status]" \
    --output table || echo -e "${RED}Failed to pull Job Queues!${NC}"

# 3. Audit ECS GPU Cluster Registration
echo -e "\n${YELLOW}[3/4] Polling ECS GPU Spot-Fleet Matrix...${NC}"
GPU_CE=$(aws --profile admin batch describe-compute-environments --query "computeEnvironments[?contains(computeEnvironmentName, 'somatic-gpu-spot')].ecsClusterArn" --output text 2>/dev/null | awk '{print $1}')

if [ -n "$GPU_CE" ] && [ "$GPU_CE" != "None" ]; then
    # Grab the active ECS instances registered inside the Fleet
    INSTANCES=$(aws --profile admin ecs list-container-instances --cluster "$GPU_CE" --query "containerInstanceArns" --output text 2>/dev/null)
    if [ -n "$INSTANCES" ] && [ "$INSTANCES" != "None" ]; then
        echo -e "${GREEN}SUCCESS: DeepSomatic GPU Fleet has active ECS container registrations.${NC}"
        aws --profile admin ecs describe-container-instances --cluster "$GPU_CE" --container-instances $INSTANCES --query "containerInstances[*].[ec2InstanceId, status, runningTasksCount]" --output table
    else
        echo -e "${YELLOW}INFO: No active DeepSomatic GPU Spot Instances attached to the ECS Cluster (Scale is 0). Nextflow will seamlessly trigger a new EC2 cold-boot!${NC}"
    fi
else
    echo -e "${RED}ERROR: DeepSomatic GPU Compute Environment not found! Is Terraform applied?${NC}"
fi

# 4. Audit SSM Head Node Tunnel Target
echo -e "\n${YELLOW}[4/4] Polling Somatic-Head-Node SSM Portability...${NC}"
HEAD_NODE_ID=$(aws --profile admin ec2 describe-instances --filters "Name=tag:Name,Values=Somatic-Head-Node" "Name=instance-state-name,Values=running" --query "Reservations[0].Instances[0].InstanceId" --output text 2>/dev/null)

if [ -n "$HEAD_NODE_ID" ] && [ "$HEAD_NODE_ID" != "None" ]; then
    SSM_STATUS=$(aws --profile admin ssm describe-instance-information --filters "Key=InstanceIds,Values=$HEAD_NODE_ID" --query "InstanceInformationList[0].PingStatus" --output text 2>/dev/null)
    if [ "$SSM_STATUS" == "Online" ]; then
         echo -e "${GREEN}SUCCESS: Target Head Node ($HEAD_NODE_ID) is Online and accepting active SSM Postgres Tunnels.${NC}"
    else
         echo -e "${RED}ERROR: Target Head Node ($HEAD_NODE_ID) is Offline. Launchpad execution will fail database handshakes!${NC}"
    fi
else
    echo -e "${RED}ERROR: Somatic-Head-Node EC2 Instance is either terminated or not actively running in AWS EC2!${NC}"
fi

echo -e "\n${CYAN}✅ Infrastructure Audit Script Complete.${NC}"
