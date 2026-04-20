---
description: Natively enforces the local virtual environment and AWS multi-account IAM profiles prior to Executer terminal deployments.
glob: "*.sh, *.nf, *aws*, *terraform*, *pytest*, *python*"
---

# Local Environment and Authentication Boundaries

The execution layer operates under the strict assumption that it resides in a containerized void. Because the Director physically runs a local macOS environment with partitioned IAM trust relationships, you **MUST** logically assert environmental contexts before invoking `run_command` tooling.

1. **Python Toolkit Isolation (`source venv/bin/activate`)**: 
   - All external execution (including custom `.py` hooks, AWS Batch diagnostic scripts, TDAID Pytest routines, and local Nextflow evaluations) must be wrapped natively in the virtual environment. 
   - **Mandate**: Prepend `source venv/bin/activate && ` to any command interacting with `python`, `pytest`, `run_omics_annotation.py`, or similar custom scripts inside `utils/`.

2. **AWS FinOps & IaaS Privileges (`export AWS_PROFILE=admin`)**: 
   - Operations that hit the AWS control plane (ECR pushes, S3 interactions, Terraform deployments, or Nextflow running against AWS Batch) will fail with authentication errors unless explicitly utilizing the `admin` profile.
   - **Strict Context Dependency**: Only prepend `export AWS_PROFILE=admin && ` to commands that actually require external credentials (e.g., `aws ecr get-login-password`, `docker push` into AWS, `./infrastructure/docker/build_*.sh`, or `terraform apply`). 
   - Do NOT blanket-export this variable for purely local/offline operations (like `pytest` or `cat`) as it wastes token evaluations and pollutes the execution string.

3. **Ephemeral Scratch Execution**: Target `tests/agent_workspace_tmp/` exclusively for `run_command` dry-runs. You are physically blocked from writing to the OS `/tmp` path.

## Terminal String Synthesis Example
When invoking a script that hits AWS and uses Python internal tooling:
```bash
source venv/bin/activate && export AWS_PROFILE=admin && ./infrastructure/docker/build_bcftools_amd64.sh
```
