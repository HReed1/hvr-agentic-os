"""
Zero-Trust enforcement layer for the Agentic OS.

- interceptors: Monkeypatches on LlmAgent and LoopAgent for PHI redaction,
                loop termination signals, and context truncation.
- callbacks:    before_tool_callback validators for sandbox blacklists
                and executor airgap enforcement.
"""
from .interceptors import patched_llm_run, patched_loop_run  # noqa: F401
from .callbacks import zero_trust_callback  # noqa: F401
