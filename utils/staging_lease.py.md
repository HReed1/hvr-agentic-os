# Staging Lease Manager (`staging_lease.py`)

## Overview
This script implements a native OS-Kernel level concurrency lock intended to prevent structural race conditions between decoupled agents attempting to perform disparate operations within the `.staging/` sandbox simultaneously.

## Functionality
- **`acquire_staging_lease(exclusive=False)`**: A Python context manager utilizing `fcntl.flock()`. 
    - `exclusive=False` grants a `LOCK_SH` (shared) lock typically used by Executor or QA personas running non-destructive reads and Pytests.
    - `exclusive=True` grants a `LOCK_EX` (exclusive) lock, actively utilized by the Auditor/Architect to block all other file interactions during sensitive structural teardowns or code promotions.
- **Agentic Rate-Limiter**: Specifically engineered to throttle AI processing. By blocking the python event loop (via a `BlockingIOError` paired with `time.sleep`), it serves as a physical buffer against hallucinated, rapid-retry Denial of Service loops instantiated by the Swarm.
