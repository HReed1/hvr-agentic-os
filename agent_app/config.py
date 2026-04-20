import os
import sys
from google.adk.models.lite_llm import LiteLlm

# Determine if we are running in headless evaluation mode
IS_HEADLESS_EVAL = "eval" in sys.argv or os.environ.get("HEADLESS_EVAL", "false").lower() == "true"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXECUTOR_MCP_PATH = os.path.join(BASE_DIR, "utils", "executor_mcp.py")
ARCHITECT_MCP_PATH = os.path.join(BASE_DIR, "utils", "architect_mcp.py")
AUDITOR_MCP_PATH = os.path.join(BASE_DIR, "utils", "auditor_mcp.py")
AST_VALIDATION_MCP_PATH = os.path.join(BASE_DIR, "utils", "ast_validation_mcp.py")

# --- Model Configuration ---
PRIMARY_PRO_MODEL = os.environ.get("GEMINI_PRO_MODEL", "gemini-3.1-pro-preview")
PRIMARY_FLASH_MODEL = os.environ.get("GEMINI_FLASH_MODEL", "gemini-3.1-flash-lite-preview")

ANTHROPIC_PRO_MODEL = LiteLlm(
    model="anthropic/" + os.environ.get("ANTHROPIC_PRO_MODEL", "claude-opus-4-5")
)
ANTHROPIC_FLASH_MODEL = LiteLlm(
    model="anthropic/" + os.environ.get("ANTHROPIC_FLASH_MODEL", "claude-sonnet-4-5")
)

_provider = os.environ.get("ADK_MODEL_PROVIDER", "gemini").lower()
if _provider == "anthropic":
    PRIMARY_PRO_MODEL = ANTHROPIC_PRO_MODEL

CONTEXT_SAFE_MODE = os.environ.get("ADK_CONTEXT_SAFE_MODE", "false").lower() == "true"
