# Build Firewall Script (`build_firewall.sh`)

## Overview
A lightweight execution bash script responsible for natively compiling the Data Loss Prevention (DLP) Proxy Firewall (`dlp-firewall`).

## Functionality
- **Path Management**: Safely enforces the current working directory to the project root relative to the location of the script.
- **Golang Compilation**: Targets the source at `cmd/dlp-firewall/main.go`. 
- **Optimization**: Uses the `-ldflags="-s -w"` and `-trimpath` flags to strip debug symbols, thereby compiling a highly optimized, lean binary. 
- **Output**: The compiled Go binary is securely moved into the root `bin/` directory (`bin/dlp-firewall`).
