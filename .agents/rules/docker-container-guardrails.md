---
trigger: always_on
description: Mandatory verification rules for biocontainer deployment, AWS Batch CLI requirements, and ECR pushing constraints.
---

# Docker Container & Biocontainer Guardrails

When mutating Dockerfiles, especially when extending minimalistic images like `quay.io/biocontainers`:

1. **Distroless Package Manager Verification**
   Agents MUST manually verify the internal package manager BEFORE blindly injecting dependencies via `apt-get` or `conda`. Biocontainers are heavily pruned and often completely distroless (lacking package managers). You MUST use the `inspect_container_os_release` MCP tool (e.g., passing `quay.io/biocontainers/minimap2:2.26--he4a0461_1`) to physically interrogate the `/etc/os-release` layer and locate internal binaries (`apt`, `apk`, `yum`). You are strictly forbidden from attempting to run `docker run` inside your sandbox.

2. **AWS Batch Execution Capability (awscli requirement)**
   If a Docker container will be used as a Nextflow module executing via the `awsbatch` profile, it **MUST** have the `awscli` physically installed inside the container. If the native package managers are stripped, Agents must use raw binary installation (e.g., downloading the `.zip` via `wget`, inflating it via `unzip`, and bypassing the package manager) to allow native S3 staging of `.command.run` scripts.

3. **Zero-Trust ECR Bootstrapping**
   A container cannot be actively deployed to the AWS cluster until its exact pristine repository registry (e.g., `aws_ecr_repository` block) is statically declared inside `infrastructure/aws/ecr_oidc.tf` and physically granted specific GitHub Actions OIDC permissions. Never blindly push images to non-existent ECR repositories.
