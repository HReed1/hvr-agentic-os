---
name: trivy-vuln-sweeper
description: Automates the Trivy Vulnerability Audit constraint processing by triggering local sweeps when CI/CD blocks occur on OS-layer vulnerabilities.
---
# Trivy Vulnerability Sweeper

## Purpose
This skill empowers the Executor to autonomously assess base-layer Docker container vulnerabilities when the GitHub Actions CI/CD pipeline fails due to `Trivy` scan blocks.

## When to use this skill
Execute this diagnostic immediately whenever you encounter a CI/CD `Exit 1` caused by `aquasec/trivy-action`. 

## Operating Instructions
1. Identify the failing Docker image from the CI/CD pipeline logs (e.g., `python:3.11-slim`, `staphb/bcftools:1.17`, `816549818028.dkr.ecr.us-east-1.amazonaws.com/ngs-bcftools:v1.2.0`).
2. Run the internal utility script natively on the host to generate the offline threat matrix:
   ```bash
   ./utils/trivy_vuln_sweeper.sh <image_name:tag>
   ```
3. Read the output report generated in `/tmp/`.
4. **The Threat Model Audit**:
   - Classify kernel-level, driver, and operating system packages (e.g. `linux-libc-dev`, `libsystemd0`, `libncurses`) as `INERT` if the container runs in an isolated AWS Batch environment without inbound ingress.
   - Inject `INERT` CVEs linearly into the root `.trivyignore`.
   - Classify networking and application-layer packages (e.g., `jaraco.context`, `wheel`, `urllib3`, `requests`) as `ACTIONABLE`.
   - Patch `ACTIONABLE` CVEs directly via `RUN pip install --upgrade <package>` or `RUN apt-get update && apt-get upgrade -y <package>` within the respective `Dockerfile`.
