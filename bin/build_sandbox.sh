#!/bin/bash
set -e

# Dynamically route execution context to the project root
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

echo "================================================="
echo "[BUILDING] Compiling transient executor-sandbox..."
echo "================================================="

docker build -t executor-sandbox:latest -f docker/executor-sandbox/Dockerfile .

echo "================================================="
echo "[SUCCESS] Zero-Trust Docker Sandbox (executor-sandbox:latest) is compiled and ready."
