#!/bin/bash

# Extract Head Node Public IP dynamically from IaC state
cd infrastructure/aws || exit 1
HEAD_IP=$(terraform output -raw head_node_public_ip)
cd ../../

if [ -z "$HEAD_IP" ]; then
    echo "ERROR: Failed to dynamically extract Head Node IP from Terraform state in infrastructure/aws"
    exit 1
fi

echo "Resolving Head Node at $HEAD_IP..."

# Wipe stale cryptographic fingerprints to bypass prompt interruptions
ssh-keygen -R "$HEAD_IP" 2>/dev/null

# Establish connection avoiding strict host key validation
ssh -A -o StrictHostKeyChecking=no -i ~/.ssh/ngs-head-node-key.pem "ec2-user@$HEAD_IP"
