#!/bin/bash

# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics
# Phase 39: The Auto-Healing Zero-Trust Database Tunnel

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

export PATH=$PATH:$HOME/bin

SSM_PID=""

# Task 2: Implement Clean Teardown
cleanup() {
    echo -e "\n${YELLOW}🛑 Caught termination signal. Tearing down the database tunnel cleanly...${NC}"
    if [ -n "$SSM_PID" ]; then
        kill -9 $SSM_PID 2>/dev/null
    fi
    # Bruteforce cleanup of zombie bindings on local port 5432
    lsof -t -i:5432 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Database port 5432 cleanly released. Daemon terminated.${NC}"
    exit 0
}

# Trap keyboard interrupts and termination signals
trap cleanup SIGINT SIGTERM

echo -e "${CYAN}🚀 Initializing Self-Healing Zero-Trust Database Tunnel Daemon...${NC}"

# Task 1: Daemon Loop
while true; do
    # Check if port 5432 is legitimately bound
    if lsof -nP -iTCP:5432 -sTCP:LISTEN >/dev/null 2>&1; then
        BINDING_PROCESS=$(lsof -nP -iTCP:5432 -sTCP:LISTEN | grep -v "COMMAND" | awk '{print $1}' | head -n 1)
        if [[ ! "$BINDING_PROCESS" =~ "session-m" ]]; then
            echo -e "${YELLOW}[FATAL] Local port 5432 is maliciously bound by $BINDING_PROCESS, not AWS SSM.${NC}"
            echo -e "${YELLOW}[FATAL] This will cause a catastrophic 'Ghosting' pipeline collision!${NC}"
            echo -e "${GREEN}Please completely shutdown local developer containers by running: ./utils/stop_dev.sh${NC}"
            exit 1
        fi
        # It's an SSM tunnel. Sleep and continue polling.
    else
        echo -e "${YELLOW}⚠️ Local port 5432 is dead. Re-establishing the AWS SSM port-forwarding session...${NC}"
        
        # Dynamically fetch the Bastion / Head Node EC2 instance ID
        INSTANCE_ID=$(aws --profile admin ec2 describe-instances --filters "Name=tag:Name,Values=Somatic-Head-Node" "Name=instance-state-name,Values=running" --query "Reservations[0].Instances[0].InstanceId" --output text)
        
        if [ "$INSTANCE_ID" == "None" ] || [ -z "$INSTANCE_ID" ]; then
            echo -e "${YELLOW}❌ Could not locate the running Somatic-Head-Node in AWS to act as a bastion. Retrying in 5s...${NC}"
            sleep 5
            continue
        fi

        # Dynamically sense if there is an explicit RDS / PostgreSQL engine running or if we fall back to EC2 PostGIS
        RDS_HOST=$(aws --profile admin rds describe-db-instances --query "DBInstances[0].Endpoint.Address" --output text 2>/dev/null)
        
        if [ "$RDS_HOST" == "None" ] || [ -z "$RDS_HOST" ]; then
             echo -e "${GREEN}✅ AWS EC2 Target Located ($INSTANCE_ID). Bridging local database SSM connection...${NC}"
             aws --profile admin ssm start-session \
                --target "$INSTANCE_ID" \
                --document-name AWS-StartPortForwardingSession \
                --parameters "portNumber=5432,localPortNumber=5432" > utils/db_ssm_tunnel.log 2>&1 &
        else
             echo -e "${GREEN}✅ AWS EC2 Target Located ($INSTANCE_ID). Bridging RDS connection ($RDS_HOST)...${NC}"
             aws --profile admin ssm start-session \
                --target "$INSTANCE_ID" \
                --document-name AWS-StartPortForwardingSessionToRemoteHost \
                --parameters "host=$RDS_HOST,portNumber=5432,localPortNumber=5432" > utils/db_ssm_tunnel.log 2>&1 &
        fi
            
        SSM_PID=$!
        
        echo -e "${CYAN}📡 Secure Tunnel Daemon mapped actively in background (PID: $SSM_PID).${NC}"
        # Provide AWS infrastructure a brief moment to stabilize the port handshake
        sleep 5
    fi
    
    # Sleep to prevent CPU thrashing
    sleep 5
done
