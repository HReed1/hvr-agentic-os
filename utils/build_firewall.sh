#!/bin/bash
set -e

echo "Compiling Native Golang DLP Firewall..."

export PATH="/opt/homebrew/bin:$PATH"

# Navigate to project root safely
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

# Ensure bin directory exists
mkdir -p "$PROJECT_ROOT/bin"

# Compile with stripped debug symbols for performance edge
go build -ldflags="-s -w" -trimpath -o "$PROJECT_ROOT/bin/dlp-firewall" "$PROJECT_ROOT/cmd/dlp-firewall/main.go"

echo "[SUCCESS] Native dlp-firewall compiled securely to bin/dlp-firewall"
