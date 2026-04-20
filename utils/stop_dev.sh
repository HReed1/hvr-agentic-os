#!/bin/bash

# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics

# --- Color formatting for terminal output ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping local development environment...${NC}"

# 1. Kill ngrok if it's running
if pgrep ngrok > /dev/null; then
    echo -e "${YELLOW}Shutting down ngrok tunnel...${NC}"
    pkill ngrok
    echo -e "${GREEN}✓ ngrok stopped.${NC}"
fi

# 2. Handle Docker teardown
if [[ "$1" == "--clean" ]]; then
    echo -e "${RED}Clean flag detected. Tearing down containers AND wiping database volumes...${NC}"
    docker-compose down -v
    echo -e "${GREEN}✓ Environment stopped and database reset to zero.${NC}"
else
    echo -e "${YELLOW}Tearing down containers (database data will be saved)...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ Environment stopped safely.${NC}"
    echo -e "${NC}Tip: Run './stop_dev.sh --clean' if you want to completely wipe the database data next time.${NC}"
fi

# 3. Stop colima
echo -e "${YELLOW}Stopping colima...${NC}"
colima stop
echo -e "${GREEN}✓ Colima stopped.${NC}"