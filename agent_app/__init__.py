import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig

from . import agents
from .config import IS_HEADLESS_EVAL
from .agents import autonomous_swarm, evaluation_swarm, research_discovery_loop

swarm_mode = os.environ.get("ADK_SWARM_MODE", "").lower()

if swarm_mode == "research":
    root_agent = research_discovery_loop
elif swarm_mode == "meta_eval":
    from .agents import evaluator_agent
    root_agent = evaluator_agent
else:
    root_agent = evaluation_swarm

# Era 5.1: Context Caching — static_instruction content is cached by Vertex AI
# to avoid re-tokenizing the same ~35KB of rules/prompts on every inference.
agent = App(
    name="agent_app",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,      # Only cache if content > ~2K tokens
        ttl_seconds=1800,     # 30 min TTL (covers a full eval run)
        cache_intervals=15    # Refresh cache after 15 invocations
    )
)
