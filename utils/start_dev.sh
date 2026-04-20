#!/bin/bash

# hvr-informatics bioinformatics engine. Copyright (C) 2026 hvr-informatics

# --- Color formatting for terminal output ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

CONTAINER_NAME="pipeline_postgres_local"

echo -e "${YELLOW}Checking local development environment...${NC}"

# 1. Check if the Docker daemon is actually running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}Docker is not running. Attempting to start/restart colima...${NC}"
    colima start || colima restart
    
    # Check again after trying to start colima
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker is still not running after trying to start colima. Please check your colima/docker installation.${NC}"
        exit 1
    fi
fi

# 2. Check Database Container
if [ "$(docker ps -q -f name=^/${CONTAINER_NAME}$)" ]; then
    echo -e "${GREEN}✓ Database container '${CONTAINER_NAME}' is already running.${NC}"
else
    echo -e "${YELLOW}Container is stopped or missing. Starting services via Docker Compose...${NC}"
    docker-compose up -d

    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to start Docker containers. Please check your docker-compose.yml syntax.${NC}"
        exit 1
    fi
fi

# 3. Poll the database until it is fully ready
echo -n "Waiting for PostgreSQL to initialize..."
RETRIES=30
until docker exec ${CONTAINER_NAME} pg_isready -U postgres > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
    echo -n "."
    sleep 1
    ((RETRIES--))
done
echo "" 

if [ $RETRIES -eq 0 ]; then
    echo -e "${RED}Timed out waiting for PostgreSQL to start.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Database is up and accepting connections on port 5432!${NC}"

# 4. Handle ngrok for Webhook Testing
if command -v ngrok &> /dev/null; then
    # Check if ngrok is already running
    if pgrep ngrok > /dev/null; then
        echo -e "${GREEN}✓ ngrok is already running.${NC}"
    else
        echo -e "${YELLOW}Starting ngrok tunnel on port 8000...${NC}"
        # Start ngrok in the background and discard its standard UI output
        ngrok http 8000 > /dev/null 2>&1 &
        
        # Give ngrok a second to boot up and establish the tunnel
        sleep 2 
    fi
    
    # Extract the public URL from ngrok's local API
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o '[^"]*$')
    
    if [ ! -z "$NGROK_URL" ]; then
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${CYAN}🚀 Webhook URL: ${NGROK_URL}/webhook${NC}"
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${NC}Copy the URL above into your GitHub Webhook settings.${NC}"
    else
        echo -e "${RED}Failed to extract ngrok URL. You may need to authenticate your ngrok account.${NC}"
    fi
else
    echo -e "${YELLOW}ngrok is not installed. Skipping webhook tunnel setup.${NC}"
fi

echo -e "\n${GREEN}Environment is ready. You can now run your FastAPI webhook service!${NC}"

echo -e "\n${YELLOW}Running database migrations...${NC}"
# Run the Alembic Migration
DB_HOST=localhost DB_PORT=5432 venv/bin/alembic upgrade head
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to run database migrations. Please check your database connection.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Seeding the database with synthetic and real data...${NC}"
# Seed the database with synthetic data
DB_HOST=localhost DB_PORT=5432 venv/bin/python -m etl.jobs.seed_database

echo -e "\n${YELLOW}Running cloud pipeline...${NC}"
bash "$(dirname "$0")/run_cloud_pipeline.sh"