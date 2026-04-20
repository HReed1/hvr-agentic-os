#!/bin/bash
set -e

echo "Applying Architecture via IaC..."
cd infrastructure/aws || exit 1
terraform apply -auto-approve

echo "Extracting dynamic telemetry IPs from state..."
PUBLIC_IP=$(terraform output -raw head_node_public_ip)
PRIVATE_IP=$(terraform output -raw head_node_private_ip)
cd ../../ || exit 1

if [ -z "$PRIVATE_IP" ] || [ -z "$PUBLIC_IP" ]; then
    echo "ERROR: Failed to dynamically extract Head Node IPs from Terraform state."
    exit 1
fi

echo "Resolving Head Node Database connection string over Private Subnet routing..."

# Safely search and replace Nextflow DB_HOST via literal Python AST Regex mappings natively
python3 - <<EOF
import os, re
target = 'src/pipelines/nextflow.config'
private_ip = '${PRIVATE_IP}'
if os.path.exists(target):
    with open(target, 'r') as f: 
        content = f.read()
    # Match both DB_HOST = '...' and DB_HOST = "..." protecting FinOps arrays
    updated = re.sub(r"(DB_HOST\s*=\s*)['\"].*?['\"]", rf"\g<1>'{private_ip}'", content)
    with open(target, 'w') as f: 
        f.write(updated)
    print(f'Successfully injected Private Subnet DB Route: {private_ip}')
else:
    print('Warning: nextflow.config not found. Database dependency tracking bypassed.')
EOF

# Erase ephemeral FinOps Node footprints to securely suppress prompt interceptions
echo "Erasing legacy SSH tracking footprint for Public IP: $PUBLIC_IP"
ssh-keygen -R "$PUBLIC_IP" 2>/dev/null || true

echo "Pipeline Automation Complete 🚀"
