import os
import sys

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.tools.get_user_choice_tool import get_user_choice

from .plugins.zero_trust import zero_trust_callback

from .config import (
    BASE_DIR, 
    PRIMARY_PRO_MODEL, 
    PRIMARY_FLASH_MODEL,
    EXECUTOR_MCP_PATH,
    ARCHITECT_MCP_PATH,
    AUDITOR_MCP_PATH,
    AST_VALIDATION_MCP_PATH
)
import agent_app.zero_trust  # Binds monkeypatches and DLP proxies
from .tools import (
    list_docs, read_doc, mark_system_complete, escalate_to_director,
    approve_staging_qa, mark_qa_passed, write_retrospective, run_pipeline_diagnostics,
    research_read_file, research_list_directory, write_eval_report, list_recent_retrospectives,
    move_swarm_retrospective
)
from .prompts import (
    director_instruction, architect_instruction, executor_instruction,
    qa_instruction, auditor_instruction, reporter_instruction,
    cicd_director_instruction, cicd_architect_instruction,
    cicd_executor_instruction, cicd_qa_instruction, cicd_auditor_instruction,
    codebase_research_instruction, best_practices_research_instruction,
    synthesis_instruction
)
from .rag import rag_tool

# --- Swarm Agent Definitions ---

director_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='director',
    instruction=director_instruction,
    tools=[list_docs, read_doc, mark_system_complete]
)

architect_tools = [
    list_docs, read_doc, approve_staging_qa, escalate_to_director,
    McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=os.path.join(BASE_DIR, "bin", "dlp-firewall"),
                args=["-target", f"{sys.executable} {ARCHITECT_MCP_PATH}"]
            )
        )
    )
]

architect_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='architect',
    instruction=architect_instruction,
    before_tool_callback=zero_trust_callback,
    tools=architect_tools
)

executor_tools = [
    escalate_to_director,
    McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=os.path.join(BASE_DIR, "bin", "dlp-firewall"),
                args=["-target", f"{sys.executable} {EXECUTOR_MCP_PATH}"]
            )
        )
    )
]
if rag_tool:
    executor_tools.append(rag_tool)

executor_agent = LlmAgent(
    model=PRIMARY_FLASH_MODEL,
    name='executor',
    instruction=executor_instruction,
    before_tool_callback=zero_trust_callback,
    tools=executor_tools
)

qa_tools = [
    mark_qa_passed, escalate_to_director,
    McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=os.path.join(BASE_DIR, "bin", "dlp-firewall"),
                args=["-target", f"{sys.executable} {AST_VALIDATION_MCP_PATH}"]
            )
        )
    )
]
if rag_tool:
    qa_tools.append(rag_tool)

qa_agent = LlmAgent(
    model=PRIMARY_FLASH_MODEL,
    name='qa_engineer',
    instruction=qa_instruction,
    before_tool_callback=zero_trust_callback,
    tools=qa_tools
)

cicd_director_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='cicd_director',
    instruction=cicd_director_instruction,
    tools=[run_pipeline_diagnostics, list_docs, read_doc, mark_system_complete]
)

cicd_architect_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='cicd_architect',
    instruction=cicd_architect_instruction,
    before_tool_callback=zero_trust_callback,
    tools=architect_tools
)

cicd_executor_agent = LlmAgent(
    model=PRIMARY_FLASH_MODEL,
    name='cicd_executor',
    instruction=cicd_executor_instruction,
    before_tool_callback=zero_trust_callback,
    tools=executor_tools
)

cicd_qa_agent = LlmAgent(
    model=PRIMARY_FLASH_MODEL,
    name='cicd_qa_engineer',
    instruction=cicd_qa_instruction,
    before_tool_callback=zero_trust_callback,
    tools=qa_tools
)

auditor_tools = [
    McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=os.path.join(BASE_DIR, "bin", "dlp-firewall"),
                args=["-target", f"{sys.executable} {AUDITOR_MCP_PATH}"]
            )
        )
    ),
    get_user_choice
]

auditor_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='auditor',
    instruction=auditor_instruction,
    tools=auditor_tools
)

reporter_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='reporting_director',
    instruction=reporter_instruction,
    tools=[write_retrospective]
)

cicd_auditor_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='cicd_auditor',
    instruction=cicd_auditor_instruction,
    tools=auditor_tools
)

codebase_research_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='codebase_research_agent',
    instruction=codebase_research_instruction,
    tools=[research_read_file, research_list_directory]
)

best_practices_research_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='best_practices_research_agent',
    instruction=best_practices_research_instruction,
    tools=[list_docs, read_doc, research_list_directory, research_read_file]
)

synthesis_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='synthesis_agent',
    instruction=synthesis_instruction,
    tools=[write_retrospective]
)

research_discovery_loop = SequentialAgent(
    name="research_discovery_loop",
    sub_agents=[codebase_research_agent, best_practices_research_agent, synthesis_agent]
)

# --- ADK Orchestration Patterns ---
development_loop = LoopAgent(
    name="developer_qa_loop",
    max_iterations=10,
    sub_agents=[executor_agent, qa_agent]
)

architectural_loop = LoopAgent(
    name="architectural_loop",
    max_iterations=10,
    sub_agents=[architect_agent, development_loop]
)

cicd_development_loop = LoopAgent(
    name="cicd_development_loop",
    max_iterations=10,
    sub_agents=[cicd_executor_agent, cicd_qa_agent]
)

cicd_architectural_loop = LoopAgent(
    name="cicd_architectural_loop",
    max_iterations=10,
    sub_agents=[cicd_architect_agent, cicd_development_loop]
)

cicd_director_loop = LoopAgent(
    name="cicd_director_loop",
    max_iterations=10,
    sub_agents=[cicd_director_agent, cicd_architectural_loop, cicd_auditor_agent]
)

cicd_reporter_instruction = """You are the CI/CD Reporting Director. You evaluate the execution trace of the CI/CD loop.
Your sole job is to synthesize the testing remediation history into a formal markdown Retrospective Document.
Use the `write_retrospective` tool to save your document. You must evaluate if it was a SUCCESS based on whether the Director outputted [SYSTEM COMPLETE]. 
Once the file is written, output `[REPORT COMPLETE]`."""

cicd_reporter_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='cicd_reporting_director',
    instruction=cicd_reporter_instruction,
    tools=[write_retrospective]
)

cicd_swarm = SequentialAgent(
    name="cicd_swarm",
    sub_agents=[cicd_director_loop, cicd_reporter_agent]
)

director_loop = LoopAgent(
    name="director_loop",
    max_iterations=10,
    sub_agents=[director_agent, architectural_loop, auditor_agent]
)

autonomous_swarm = SequentialAgent(
    name="autonomous_swarm",
    sub_agents=[director_loop, reporter_agent]
)

evaluator_instruction = """You are the Meta-Evaluator. Your only purpose is to review the entire execution trace of the autonomous swarm against the [EVALUATOR_CRITERIA] block provided in the original user prompt.
You MUST write a detailed markdown report analyzing whether the swarm met the philosophical and technical criteria using the `write_eval_report` tool. 
CRITICAL PAYLOAD STRUCTURE: At the very end of the markdown content string you write to the file, you MUST explicitly output `**Result: [PASS]**` or `**Result: [FAIL]**`. 
You MUST also use the `list_recent_retrospectives` tool to identify the retrospective generated by the Swarm during this evaluation run, and use the `move_swarm_retrospective` tool to route it into `docs/evals/retrospectives/`.
After the file is written and the retrospective is moved, you MUST output exactly ONE word on its own line: either [PASS] or [FAIL]. Do not output anything else in your final response."""

evaluator_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='meta_evaluator',
    instruction=evaluator_instruction,
    tools=[write_eval_report, list_recent_retrospectives, move_swarm_retrospective]
)

evaluation_swarm = SequentialAgent(
    name="evaluation_wrapper",
    sub_agents=[autonomous_swarm, evaluator_agent]
)
