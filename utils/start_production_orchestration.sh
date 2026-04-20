#!/bin/bash
# start_production_orchestration.sh
# Dynamically fetches secrets from AWS SSM and exports them to the environment.

echo "Fetching configuration from AWS SSM..."

# Fetch parameters and export them as environment variables
export DB_PASSWORD=$(aws ssm get-parameter --region us-east-1 --name "/ngs/db_password" --with-decryption --query "Parameter.Value" --output text)
export AUTH0_DOMAIN=$(aws ssm get-parameter --region us-east-1 --name "/ngs/auth0_domain" --query "Parameter.Value" --output text)
export AUTH0_AUDIENCE=$(aws ssm get-parameter --region us-east-1 --name "/ngs/auth0_audience" --query "Parameter.Value" --output text)

if [ -z "$DB_PASSWORD" ] || [ -z "$AUTH0_DOMAIN" ] || [ -z "$AUTH0_AUDIENCE" ]; then
    echo "Error: Failed to fetch required parameters from SSM."
    # In production, we might exit 1 here.
else
    echo "Environment variables initialized successfully."
fi

# Clean up any residual .env if it accidentally exists to maintain Zero-Trust
if [ -f .env ]; then
    rm .env
fi

# Execute docker compose
docker compose up -d
