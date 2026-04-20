# Trivy Vulnerability Sweeper (`trivy_vuln_sweeper.sh`)

## Overview
A standalone bash execution script intended to be natively invoked by the Antigravity Executor. It orchestrates local, transient static analysis scans against Docker images utilizing Aqua Security's Trivy vulnerability database.

## Functionality
- **Scan Configuration**: Executes a temporary docker container pulling `ghcr.io/aquasecurity/trivy:latest`, targeting the user-provided `<image_name:tag>`.
- **Target Parameters**: Constrains the security evaluation explicitly to dependencies yielding `HIGH` and `CRITICAL` severity CVEs.
- **Output Routing**: Streams the raw scan result payload mapping directly to `/tmp/trivy_<image_name>.txt` on the host, subsequently parsing via `grep` to bubble the critical vulnerability total count back up to the Executor's standard output pipeline for Threat Model Analysis.
