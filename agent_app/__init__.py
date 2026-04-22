import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from . import agents
from .config import IS_HEADLESS_EVAL
from .agents import autonomous_swarm, evaluation_swarm, research_discovery_loop

swarm_mode = os.environ.get("ADK_SWARM_MODE", "").lower()

if swarm_mode == "research":
    agent = research_discovery_loop
elif swarm_mode == "meta_eval":
    from .agents import evaluator_agent
    agent = evaluator_agent
elif swarm_mode == "solo":
    from .agents import solo_evaluation_swarm
    agent = solo_evaluation_swarm
else:
    agent = evaluation_swarm
