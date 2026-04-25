import pytest
import os
from google.adk.evaluation.agent_evaluator import AgentEvaluator

@pytest.mark.asyncio
@pytest.mark.skipif("CI" in os.environ, reason="ADK Swarm simulations are physically restricted to Local Execution")
async def test_triad_simulation():
    # Validates the deterministic handoff via ADK eval engine
    await AgentEvaluator.evaluate(
        agent_module="agent_app",
        eval_dataset_file_path_or_dir="tests/triad_eval.test.json"
    )
