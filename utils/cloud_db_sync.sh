#!/bin/bash

# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics

# --- Color formatting for terminal output ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 Executing Secure AWS Snapshot Mirror (Cloud -> Local)...${NC}"

# Open the SSM tunnel natively
./utils/db_tunnel.sh > utils/db_ssm_tunnel.log 2>&1 &
TUNNEL_PID=$!
sleep 5

# Set connection parameters mapped to the proxy payload
export PGPASSWORD="local_dev_password"
DB_USER="postgres"
DB_NAME="pipeline_db"
DUMP_FILE="cloud_snapshot_$(date +%F_%H-%M-%S).sql.gz"

echo -e "${YELLOW}Extracting cloud-native records natively over SSM Tunnel...${NC}"
# pg_dump streams the database out over the 5432 TCP proxy perfectly compressing into the gzip binary
pg_dump -h localhost -p 5432 -U $DB_USER $DB_NAME | gzip > "data/$DUMP_FILE"

echo -e "${GREEN}✅ Database mirror successfully extracted to data/$DUMP_FILE !${NC}"

echo -e "${CYAN}Cleaning up the AWS SSM Tunnel encryption sockets...${NC}"
kill $TUNNEL_PID
