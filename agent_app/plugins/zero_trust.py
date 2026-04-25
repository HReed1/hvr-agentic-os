import logging
import re

logger = logging.getLogger(__name__)

# Compile blacklist patterns restricting the Executor's bash capabilities natively
BLACKLIST_PATTERNS = [
    re.compile(r'\baws\s+s3\s+(rm|sync.*\-\-delete)\b', re.IGNORECASE),
    re.compile(r'\bnextflow\s+clean\b', re.IGNORECASE),
    re.compile(r'\baws\s+(batch|ec2|sts)\b', re.IGNORECASE),
    re.compile(r'\bterraform\s+(destroy|apply)\b', re.IGNORECASE),
    re.compile(r'rm\s+-r?f\s+(/|\.)\b', re.IGNORECASE),
    re.compile(r'\bgit\s+(push|commit|reset|checkout|clean)\b', re.IGNORECASE),
    re.compile(r'\bpython3?\s+-c\b', re.IGNORECASE)
]

# Test-runner patterns — blocked for executor agents via execute_transient_docker_sandbox.
# The executor must NOT run tests; that responsibility belongs exclusively to the QA Engineer.
TEST_RUNNER_PATTERNS = [
    re.compile(r'\bvitest\b', re.IGNORECASE),
    re.compile(r'\bjest\b', re.IGNORECASE),
    re.compile(r'\bpytest\b', re.IGNORECASE),
    re.compile(r'\bnpm\s+(run\s+)?test\b', re.IGNORECASE),
    re.compile(r'\bnpx\s+vitest\b', re.IGNORECASE),
    re.compile(r'\bnpx\s+jest\b', re.IGNORECASE),
    re.compile(r'\bpython3?\s+-m\s+pytest\b', re.IGNORECASE),
]

# Agent names that are forbidden from running test commands via docker sandbox
EXECUTOR_AGENT_NAMES = {'executor', 'cicd_executor'}


def _enforce_sandbox_blacklist(command: str):
    for pattern in BLACKLIST_PATTERNS:
        if pattern.search(command):
            logger.error(f"BLOCKED: Destructive command intercepted: {command}")
            raise PermissionError(f"Zero-Trust Block: Command matches destructive signature: {pattern.pattern}")

def _enforce_executor_airgap(command: str, agent_name: str):
    if agent_name in EXECUTOR_AGENT_NAMES:
        for pattern in TEST_RUNNER_PATTERNS:
            if pattern.search(command):
                logger.error(f"BLOCKED: Executor attempted test execution via sandbox: {command}")
                raise PermissionError(
                    f"Zero-Trust Block: The executor is air-gapped from test execution. "
                    f"Command '{command}' matches test-runner signature: {pattern.pattern}. "
                    f"Output [TASK COMPLETE] and let the QA Engineer handle testing."
                )

def zero_trust_callback(tool=None, args=None, tool_context=None, **kwargs):
    """
    Validates tool execution against Zero-Trust policies natively.
    Replaces the brittle Markdown instructions from AGENTS.md.
    """
    tool_name = tool.name if hasattr(tool, 'name') else str(tool)
    tool_args = args or {}
    logger.info(f"Zero-Trust Policy Check: Intercepting tool {tool_name} with args: {tool_args}")

    # Resolve calling agent name
    agent_name = None
    if tool_context is not None:
        agent_name = getattr(tool_context, 'agent_name', None) or getattr(
            getattr(tool_context, 'agent', None), 'name', None
        )

    # Filter operations natively via decoupled sub-handlers
    if tool_name == "execute_transient_docker_sandbox":
        command = tool_args.get("command", "")
        _enforce_sandbox_blacklist(command)
        _enforce_executor_airgap(command, agent_name)

    return None
