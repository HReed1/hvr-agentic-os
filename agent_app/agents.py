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
    AUDITOR_MCP_PATH,
    AST_VALIDATION_MCP_PATH,
    ADK_TRACE_MCP_PATH
)
import agent_app.zero_trust  # Binds monkeypatches and DLP proxies
from .tools import (
    list_docs, read_doc, mark_system_complete, escalate_to_director,
    approve_staging_qa, mark_qa_passed, write_retrospective, run_pipeline_diagnostics,
    research_read_file, research_list_directory, write_eval_report
)
from .prompts import (
    director_instruction, architect_instruction, executor_instruction,
    qa_instruction, auditor_instruction, reporter_instruction,
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
    list_docs, read_doc, escalate_to_director
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

auditor_tools = [
    McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=os.path.join(BASE_DIR, "bin", "dlp-firewall"),
                args=["-target", f"{sys.executable} {AUDITOR_MCP_PATH}"]
            )
        )
    ),
    McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=os.path.join(BASE_DIR, "bin", "dlp-firewall"),
                args=["-target", f"{sys.executable} {AST_VALIDATION_MCP_PATH}"]
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
    tools=[
        write_retrospective,
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=os.path.join(BASE_DIR, "bin", "dlp-firewall"),
                    args=["-target", f"{sys.executable} {ADK_TRACE_MCP_PATH}"]
                )
            )
        )
    ]
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

director_loop = LoopAgent(
    name="director_loop",
    max_iterations=10,
    sub_agents=[director_agent, architect_agent, development_loop, auditor_agent]
)

autonomous_swarm = SequentialAgent(
    name="autonomous_swarm",
    sub_agents=[director_loop]
)

evaluator_instruction = """You are the Meta-Evaluator. Your only purpose is to review the entire execution trace of the preceding autonomous swarm against the [EVALUATOR_CRITERIA] block provided in the original user prompt.
CRITICAL MANDATE: You MUST first read and adhere to the [Evaluator Governance Rule](file:///.agents/rules/evaluator-governance.md) and the [Evaluator Wrapup Workflow](file:///.agents/workflows/evaluator-wrapup.md) before performing your audit.
CRITICAL RULE 1: You MUST invoke the `get_latest_adk_session` tool to retrieve the execution trace data. Since you are running in the same process as the swarm, the full history is already available in your session database. You cannot physically evaluate the system state without reading this history.
CRITICAL RULE 2: You MUST write a detailed markdown report analyzing whether the swarm met the philosophical and technical criteria using the `write_eval_report` tool. 
You will logically determine if the Swarm natively PASSED or FAILED the framework constraints, and forcefully pipe your boolean conclusion natively into the `is_passing: bool` parameter of `write_eval_report`. 
BOUNDARY ENFORCEMENT: Your duty ends at reporting. YOU ARE FORBIDDEN from attempting physical workspace resets or git commands. Once `write_eval_report` returns successfully, cleanly conclude your execution by exclusively outputting the text `[EVALUATION COMPLETE]` to hand control to the system automation."""

evaluator_tools = [
     write_eval_report,
     McpToolset(
         connection_params=StdioConnectionParams(
             server_params=StdioServerParameters(
                 command=os.path.join(BASE_DIR, "bin", "dlp-firewall"),
                 args=["-target", f"{sys.executable} {ADK_TRACE_MCP_PATH}"]
             )
         )
     )
]

evaluator_agent = LlmAgent(
    model=PRIMARY_PRO_MODEL,
    name='meta_evaluator',
    instruction=evaluator_instruction,
    tools=evaluator_tools
)

evaluator_loop = LoopAgent(
    name="evaluator_loop",
    max_iterations=1,
    sub_agents=[evaluator_agent]
)

evaluation_swarm = SequentialAgent(
    name="evaluation_wrapper",
    sub_agents=[autonomous_swarm, reporter_agent, evaluator_loop]
)
