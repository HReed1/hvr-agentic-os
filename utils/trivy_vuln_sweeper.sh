#!/bin/bash
set -e

# trivy_vuln_sweeper.sh
# An automated security utility to execute a local Trivy scan, 
# dump the results, and parse out High/Critical vulnerabilities.
# This utility is designed to be invoked by the Antigravity Executor agent.

IMAGE_NAME=$1

if [ -z "$IMAGE_NAME" ]; then
    echo "Usage: $0 <image_name:tag>"
    exit 1
fi

echo "[Trivy Sweeper] Sweeping image: $IMAGE_NAME"
# Map string safely to file path name
SAFE_NAME=$(echo "$IMAGE_NAME" | tr '/:' '_')
REPORT_PATH="/tmp/trivy_${SAFE_NAME}.txt"

echo "[Trivy Sweeper] Pulling Trivy Database and initiating scan..."
docker run --rm -v trivy-cache:/root/.cache/ -v /var/run/docker.sock:/var/run/docker.sock ghcr.io/aquasecurity/trivy:latest image --severity HIGH,CRITICAL "$IMAGE_NAME" > "$REPORT_PATH"

echo "[Trivy Sweeper] Scan complete. Report saved to: $REPORT_PATH"
echo "[Trivy Sweeper] Vulnerability count summary:"
grep -oE "Total: [0-9]+" "$REPORT_PATH" || echo "No high/critical vulnerabilities found."
echo "Please review the report at $REPORT_PATH for further Threat Model Analysis."
