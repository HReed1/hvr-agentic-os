import logging
from agent_app import agent as active_agent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# Export the top-level orchestrator as the simulation workflow
simulation_workflow = active_agent

if __name__ == "__main__":
    print("ADK Graph Engine Successfully Assembled.")
