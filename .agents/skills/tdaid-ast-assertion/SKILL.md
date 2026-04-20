---
name: tdaid-ast-assertion
description: Empowers the executor to construct offline Test-Driven AI Development validation schemas. Use this to programmatically parse bash code injected inside Nextflow strings before AWS Batch orchestration execution occurs.
---

# TDAID AST Assertion Engine

Modifying string manipulations, variable escapes (`\${task.cpus}`), or regex hooks inside Nextflow groovy bindings is historically highly brittle and frequently breaks AWS execution stages. Simple Python `re` string lookups will drastically fail when Nextflow closures (`{ }`) are nested multiple levels deep. 

## When to use this skill
- When proposing a syntax overhaul to `src/pipelines/main.nf`.
- When engineering new Bash scripting hooks.
- When engineering orchestration fallbacks, queue routing, or error strategies inside `src/pipelines/nextflow.config`.

## How to use it
Use internal Pytest frameworks targeting AST topologies (Example: `tests/test_phase132_deepsomatic_lexical.py`).
1. Instead of trusting logical AI inference, write Python tests that physically load the `main.nf` codebase string.
2. **Robust Extraction Mechanic**: You MUST use a bracket-counting state machine to flawlessly isolate nested Nextflow closures. *Do not use naked Regular Expressions across multi-line Groovy AST.*

**Copy & Paste this deterministic closure extraction utility:**
```python
def extract_dsl2_block(content, target_process):
    """
    Extracts an entire nested DSL2 process block using bracket matching,
    preventing mid-closure regex failures.
    """
    start_token = f"process {target_process} {{"
    start_idx = content.find(start_token)
    if start_idx == -1:
        return None
    
    bracket_count = 0
    in_block = False
    
    for i in range(start_idx, len(content)):
        if content[i] == '{':
            bracket_count += 1
            in_block = True
        elif content[i] == '}':
            bracket_count -= 1
        
### Phase 149 Mandate: Structural Fallbacks
The Executor relies on the AST logic to extract configuration arrays.
**WARNING (Phase C Scaling Horizon)**: For complex DAG state validation, rely exclusively on `nextflow config` CLI dry-runs or the Python AST extraction block provided above. Note: As the Executor, you do NOT possess the AST validation MCP tools natively (`parse_nextflow_ast`); you MUST utilize the native python `extract_dsl2_block` engine defined in this manifest to analyze closure topologies.

3. assert that generated structural boundaries remain intact within the blocked extraction (e.g., `assert "text" in block`).
4. Execute via `pytest` to verify the "Red" (failing) test state. Implement the correction inside `.nf` or `nextflow.config`, verify the "Green" (passing) `Exit 0` state natively.
5. **CRITICAL:** Pause the tactical execution cycle. Wait for the `[EXECUTION APPROVED]` signal from the Director.

### 3. Configuration Assertion Constraints:
When modifying `nextflow.config` AWS Batch Spot profiles, you MUST ensure that `errorStrategy` leverages Groovy's null-safe array lookup (e.g., `task.exitStatus in ((130..145) + 104 + 255) ? 'retry' : 'finish'`). Nextflow (>20.0) natively intercepts AWS Batch API-level Spot Rips (`Host EC2 Terminated`) completely bypassing the strategy block evaluation. Do NOT hallucinate brittle unconditional integer loops (e.g., `task.attempt <= maxRetries`) that inadvertently promote deterministic Syntax Errors into expensive On-Demand Queues!

### 4. Zero-Trust API Testing via `fuzz_telemetry_webhook`
Before deploying pipeline changes to the cloud, you can test if Nextflow's Webhook will correctly penetrate the FastAPI Security backend:
- Utilize the `fuzz_telemetry_webhook` MCP tool natively.
- Pass fake payloads (e.g., `fuzz_telemetry_webhook(run_id="TEST-DAG-1")`).
- Use this during TDAID loops to assert whether FastAPI correctly issues a `200 OK` (when `use_valid_secret=True`) or explicitly bounces unauthorized Webhooks with `401 Unauthorized` (when `use_valid_secret=False`).
