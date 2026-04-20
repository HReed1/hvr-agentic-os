---
trigger: always_on
description: Enforces Terraform State Parity and Instance hardware ceilings to prevent AWS Batch scheduler death traps.
---

# Infrastructure as Code Guardrails

When inspecting or mutating Terraform files regarding the orchestration hardware:

1. **Terraform State Drift Anti-Pattern**: You are **STRICTLY FORBIDDEN** from using `version = "$Latest"` when binding an `aws_launch_template` to an `aws_batch_compute_environment`. 
2. **The Fix**: You MUST use dynamic traversal attributes (e.g., `aws_launch_template.target.latest_version`) to force physical state cycles during terraform deployment. This prevents AWS Batch from internally trapping and spinning up isolated, dead hardware configurations.