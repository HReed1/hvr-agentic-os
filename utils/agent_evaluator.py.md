# Agent Evaluator Script (`agent_evaluator.py`)

## Overview
This is a concise functional test script leveraging `pytest` to validate the orchestration integrity of the agentic swarm through the ADK evaluation framework.

## Components

### `test_triad_simulation` (Async Pytest)
- **Purpose**: Automatically tests the deterministic state machine transitions of the Agent Triad (e.g., Director -> Architect -> Executor).
- **Implementation**: Uses `AgentEvaluator.evaluate()` provided by `google.adk.evaluation.agent_evaluator`. It specifically binds the `agent_app` module to the dataset defined at `tests/triad_eval.test.json`.
- **Environment Constraints**: This test contains an explicit `@pytest.mark.skipif("CI" in os.environ)` boundary, completely blocking its execution on remote Continuous Integration runners. This is enforced because ADK Swarm simulations are strictly restrained to local execution for safety and dependency isolation reasons.
