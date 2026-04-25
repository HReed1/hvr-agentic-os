# Evaluation Visibility Mandate

**Version**: 1.0.0
**Scope**: IDE Agent / Swarm Director Autonomous Capabilities

## Core Mandate

The IDE Agent (and any orchestrator agent) is **STRICTLY FORBIDDEN** from autonomously triggering global or benchmarking evaluation pipelines (e.g., executing `./bin/run_all_evals.sh` or `./bin/run_head_to_head.sh`) asynchronously in the background.

## Rationale (Zero-Trust Observability)

Agentic operating constraints require the Human Director (the User) to maintain real-time, synchronous visibility over all standard output (`stdout`) generated during deep pipeline test executions.

When an AI Agent executes an evaluation pipeline in a detached background terminal sequence, it inherently strips the User of real-time monitoring capabilities, telemetry insights, and the ability to execute organic SIGINT (`Ctrl+C`) cancellation mechanisms upon detecting hallucination loops. 

## Protocol

1. **Human Trigger Only**: All evaluation pipelines MUST be launched natively by the Human User through the primary observable CLI session.
2. **Readiness Acknowledgment**: When the AI Director concludes structural changes required for an upcoming test, it must simply announce that the pipeline is armed and await human initiation. Under no circumstances should the agent use `run_command` to execute the `.sh` script on the User's behalf.
