# Zero-Trust API Schema Boundaries

This document defines the strict constraints for all HTTP and network-based infrastructure generated within the `api/` directory matrices. The Architect must ensure all proposed `FastAPI` structures adhere to these specifications.

### 1. Unified Route Prefixes
All routes MUST be prefixed with `/api/v1/`. Naked root-level endpoints other than a static `/health` probe will trigger validation failures during `tdaid-audit`.

### 2. Forbidden Execution Primitives
Never expose native standard-library interfaces through request parameters. 
If an endpoint natively accepts arbitrary JSON strings, it MUST NOT pass them unverified into any of the following boundaries:
- `subprocess.run`
- `os.system`
- `eval()`
- `exec()`

Attempting to design endpoints wrapping these primitives will be flagged as an exploit by the Auditor.

### 3. Pydantic Type Enforcement
All incoming POST/PUT JSON payload structures MUST be strictly typed utilizing Pydantic `BaseModel` classes inside `api/schemas.py`. Weak structural enforcement (e.g., dynamically accepting broad `dict` objects) is strictly prohibited.

### 4. Telemetry Fuzzer Integration
For complex DAGs resolving via the dashboard API, refer back to the `fuzz_telemetry_webhook` capability native to the QA Engineer. Complex payloads should be validated by fuzzing the HTTP POST endpoint simulating an external orchestrator weblog prior to staging promotion.
