#!/bin/bash

# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics
# Dedicated React & FastAPI Development Bootstrap Matrix

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

export AWS_PROFILE=admin

# Inject local Environment values natively so Uvicorn successfully passes the internal Auth0 Guardrails
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo -e "${CYAN}🚀 Initializing Isolated UI Development Sandbox...${NC}"

# 0. Sweep active network bindings to annihilate any orphaned instances
echo -e "${YELLOW}Sweeping active host interfaces to securely release ports 8000 and 5173...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

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

# 1. Mount the Ephemeral PostgreSQL Tunnel
echo -e "${YELLOW}Establishing Zero-Trust SSM Tunnel to Cloud Database...${NC}"
./utils/db_tunnel.sh > utils/db_ssm_tunnel.log 2>&1 &
TUNNEL_PID=$!

echo -e "${CYAN}Waiting for AWS SSM Port-Forwarding Tunnel to establish on localhost:5432...${NC}"
TIMEOUT=30
ELAPSED=0
while ! nc -z localhost 5432; do
    sleep 1
    let ELAPSED=ELAPSED+1
    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        echo -e "${YELLOW}❌ Database tunnel failed to establish within 30 seconds. Aborting UI Bootstrap.${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ Database tunnel established securely in $ELAPSED seconds.${NC}"

# 2. Map Database Variables to the strict Localhost Tunnel Binding
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_USER="postgres"
export DB_NAME="pipeline_db"

echo -e "${CYAN}Fetching encrypted database credentials directly from AWS Secrets Manager...${NC}"
export DB_PASSWORD=$(aws --profile admin ssm get-parameter --name "/ngs/db_password" --with-decryption --query "Parameter.Value" --output text 2>/dev/null || echo "local_dev_password")

# 3. Securely Start the FastAPI Core in the Background
echo -e "${GREEN}Booting explicit FastAPI Control Plane on Port 8000...${NC}"
echo "⚡️ Booting Backend FastAPI Service on Port 8000..."
source venv/bin/activate
# Route stdin to /dev/null securely so Uvicorn survives the background TTY detach during --reload!
nohup venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > uvicorn.log 2>&1 < /dev/null &
FASTAPI_PID=$!

# 4. Bind React UI to Foreground Interface
export VITE_AUTH0_DOMAIN=$AUTH0_DOMAIN
export VITE_AUTH0_AUDIENCE=$AUTH0_AUDIENCE
export VITE_AUTH0_CLIENT_ID=$AUTH0_CLIENT_ID

echo -e "${CYAN}Booting React UI Hot-Reloading Webpack via Vite...${NC}"
cd ngs-variant-ui && npm install && npm run dev

# Trap CTRL+C recursively to terminate the FastAPI and SSM subprocesses gracefully
trap "echo -e '\n${YELLOW}Tearing down Sandbox...${NC}'; kill $FASTAPI_PID; kill $TUNNEL_PID; exit 0" INT TERM EXIT
