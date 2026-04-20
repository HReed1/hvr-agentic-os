import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from . import agents
from .config import IS_HEADLESS_EVAL
from .agents import autonomous_swarm, evaluation_swarm, research_discovery_loop

swarm_mode = os.environ.get("ADK_SWARM_MODE", "").lower()

if swarm_mode == "research":
    agent = research_discovery_loop
elif swarm_mode == "eval" or IS_HEADLESS_EVAL:
    agent = evaluation_swarm
else:
    agent = autonomous_swarm
