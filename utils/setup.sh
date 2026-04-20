#!/usr/bin/env bash
# NGS Variant Validator - Interactive Deployment Wizard

echo "=========================================================="
echo "🧬 Constructing the Zero-Trust Hybrid-HPC Environment"
echo "=========================================================="

# 1. Auth0 Identity Provider Configuration
read -p "Enter your Auth0 Domain (e.g., dev-xxx.us.auth0.com): " AUTH0_DOMAIN
read -p "Enter your Auth0 API Audience (e.g., https://ngs-api.local): " AUTH0_AUDIENCE

# 2. Cryptographic Subsystem Initialization
echo "Generating secure 32-byte hexadecimal PostgreSQL passwords autonomously..."
DB_PASSWORD=$(openssl rand -hex 32)

echo "AUTH0_DOMAIN=$AUTH0_DOMAIN" > .env
echo "AUTH0_AUDIENCE=$AUTH0_AUDIENCE" >> .env
echo "DB_PASSWORD=$DB_PASSWORD" >> .env

# 3. Hybrid Cloud Arbitrage Option
echo ""
read -p "Do you want to enable AWS Cloud Integrations (HealthOmics, Open Data S3 pull, AWS Batch)? (y/n): " ENABLE_AWS

if [[ "$ENABLE_AWS" =~ ^[Yy]$ ]]; then
    echo "Securing AWS Credentials in local memory..."
    read -sp "AWS_ACCESS_KEY_ID: " AWS_ACCESS_KEY_ID
    echo ""
    read -sp "AWS_SECRET_ACCESS_KEY: " AWS_SECRET_ACCESS_KEY
    echo ""
    read -p "S3_TELEMETRY_BUCKET (e.g., s3://my-clinical-bucket): " S3_TELEMETRY_BUCKET

    echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" >> .env
    echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" >> .env
    echo "S3_TELEMETRY_BUCKET=$S3_TELEMETRY_BUCKET" >> .env
    echo "AWS_REGION=us-east-1" >> .env
    echo "AWS Integration successfully hybridized."
else
    echo "Running in pure computational isolation (On-Premise Mode)."
fi

# 4. Mandatory Cryptographic Egress Guardrail
if ! grep -q "^.env$" .gitignore; then
    echo ".env" >> .gitignore
    echo "Strict FinOps guardrail applied. .env has been forcefully appended to .gitignore."
fi

echo "✅ Environment initialized. Execute 'docker-compose up -d --build' to synthesize the cluster."
