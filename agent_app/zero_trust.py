import os
import sys
import asyncio
from datetime import datetime
from google.adk.agents import LlmAgent, LoopAgent
import google.adk.flows.llm_flows.functions as adk_llm_functions
from google.adk.tools.function_tool import FunctionTool
from mcp.client.session import ClientSession
from datetime import timedelta
from google.adk.utils.context_utils import Aclosing
from utils.dlp_proxy import redact_genomic_phi

from .config import CONTEXT_SAFE_MODE, BASE_DIR

# --- Globals for Zero Trust ---
class ZeroTrustEscalationEvent:
    class MockActions:
        escalate = False
        state_delta = None
    class MockPart:
        def __init__(self, t): self.text = t
    class MockContent:
        def __init__(self, t): self.parts = [ZeroTrustEscalationEvent.MockPart(t)]

    _counter = 0

    def __init__(self, text):
        ZeroTrustEscalationEvent._counter += 1
        self.id = f"zt-escalation-{ZeroTrustEscalationEvent._counter}"
        self.content = ZeroTrustEscalationEvent.MockContent(text)
        self.partial = False
        self.actions = ZeroTrustEscalationEvent.MockActions()
        self.timestamp = datetime.now()
        self.author = "zero_trust_framework"
        self.long_running_tool_ids_to_be_cancelled = None


# Headless Evaluation Monkeypatch
def patched_get_user_choice(options: list[str]) -> str:
    return "Approve"

# Hallucination Intercept
_original_get_tool = adk_llm_functions._get_tool

def _patched_get_tool(function_call, tools_dict):
    try:
        return _original_get_tool(function_call, tools_dict)
    except ValueError as e:
        if "not found" in str(e) and function_call.name:
            def recover_from_hallucination(*args, **kwargs) -> str:
                available_tools = ", ".join(tools_dict.keys())
                return (
                    f"[ZERO-TRUST FRAMEWORK ERROR] Tool '{function_call.name}' is physically air-gapped... "
                    f"Available tools: {available_tools}\nCourse-correct."
                )
            recover_from_hallucination.__name__ = function_call.name
            return FunctionTool(func=recover_from_hallucination)
        raise e

adk_llm_functions._get_tool = _patched_get_tool

# MCP Session Override
_original_init = ClientSession.__init__
def patched_mcp_init(self, *args, **kwargs):
    kwargs['read_timeout_seconds'] = timedelta(seconds=600)
    _original_init(self, *args, **kwargs)
ClientSession.__init__ = patched_mcp_init

# LoopAgent Intercept
_original_loop_run = LoopAgent._run_async_impl

async def patched_loop_run(self, ctx):
    consecutive_discovery_tools = getattr(ctx, '_consecutive_discovery', 0)
    consecutive_qa_rejections = getattr(ctx, '_consecutive_qa_rejections', 0)
    last_rejection_signature = getattr(ctx, '_last_rejection_signature', None)
    
    import hmac, hashlib
    
    # Needs to match the cryptographic tools logic implicitly
    sig_path = os.path.join(BASE_DIR, ".staging", ".qa_signature")
    
    async with Aclosing(_original_loop_run(self, ctx)) as agen:
        async for event in agen:
            content = getattr(event, 'content', None)
            if content:
                for part in getattr(content, 'parts', []):
                    fc = getattr(part, 'function_call', None) or getattr(part, 'functionCall', None)
                    if fc and hasattr(fc, 'name'):
                        func_name = str(getattr(fc, 'name', ''))

                        if func_name == 'mark_system_complete' and getattr(self, 'name', '') in ('director_loop', 'cicd_director_loop'):
                            return
                        if func_name == 'approve_staging_qa' and getattr(self, 'name', '') in ('architectural_loop', 'cicd_architectural_loop'):
                            if os.path.exists(sig_path):
                                with open(sig_path, "r") as f:
                                    stored = f.read().strip()
                                
                                # Resolve dynamic secret mapped from tools logic
                                key_file = os.path.join(BASE_DIR, ".agents", "memory", "staging_key.txt")
                                try:
                                    with open(key_file, "r") as kf:
                                        dynamic_secret = kf.read().strip().encode('utf-8')
                                except Exception:
                                    dynamic_secret = b"NGS_ZERO_TRUST_SIMULATION_KEY_2026"
                                    
                                expected = hmac.new(dynamic_secret, b"QA_PASSED", hashlib.sha256).hexdigest()
                                if hmac.compare_digest(stored, expected):
                                    return
                            print(f"\n[Zero-Trust Intercepted] approve_staging_qa called but .qa_signature is missing or invalid. Loop continues.", flush=True)
                        if func_name == 'mark_qa_passed' and getattr(self, 'name', '') in ('developer_qa_loop', 'cicd_development_loop'):
                            consecutive_qa_rejections = 0
                            last_rejection_signature = None
                            return
                        if func_name == 'escalate_to_director':
                            yield ZeroTrustEscalationEvent("[ESCALATING TO DIRECTOR]\n\nEscalation explicitly triggered via state transition tool.")
                            return

                        if func_name in ['list_workspace_directory', 'search_workspace']:
                            consecutive_discovery_tools += 1
                            if consecutive_discovery_tools >= 15:
                                yield ZeroTrustEscalationEvent("[ESCALATING TO DIRECTOR]\n\nZERO-TRUST VIOLATION: Excessive Discovery Loop Intercepted.")
                                return
                        else:
                            consecutive_discovery_tools = 0

                    text = getattr(part, 'text', None)
                    if text and isinstance(text, str) and '[QA REJECTED]' in text:
                        sig_start = text.find('[QA REJECTED]')
                        rejection_sig = text[sig_start:sig_start + 200].strip()
                        if rejection_sig == last_rejection_signature:
                            consecutive_qa_rejections += 1
                        else:
                            consecutive_qa_rejections = 1
                            last_rejection_signature = rejection_sig

                        if consecutive_qa_rejections >= 2:
                            yield ZeroTrustEscalationEvent(
                                f"[ESCALATING TO DIRECTOR]\n\n"
                                f"ZERO-TRUST VIOLATION: QA rejection loop detected...\n"
                                f"Last rejection: {last_rejection_signature[:150]}"
                            )
                            return

            setattr(ctx, '_consecutive_discovery', consecutive_discovery_tools)
            setattr(ctx, '_consecutive_qa_rejections', consecutive_qa_rejections)
            setattr(ctx, '_last_rejection_signature', last_rejection_signature)

            yield event

    if getattr(self, 'max_iterations', 1) > 1:
        yield ZeroTrustEscalationEvent(f"[ESCALATING TO DIRECTOR]\n\nZERO-TRUST VIOLATION: The '{getattr(self, 'name', 'unknown')}' loop hit its physical limit...")

LoopAgent._run_async_impl = patched_loop_run


# Data Loss Prevention Wrapper
_original_llm_run = LlmAgent._run_async_impl

async def patched_llm_run(self, ctx, *args, **kwargs):
    if hasattr(ctx, 'messages'):
        should_reset_context = False
        if len(ctx.messages) > 2:
            for msg in ctx.messages[-2:]:
                if hasattr(msg, 'parts'):
                    for part in msg.parts:
                        if hasattr(part, 'text') and isinstance(part.text, str):
                            if '[AUDIT PASSED]' in part.text:
                                should_reset_context = True

        if CONTEXT_SAFE_MODE:
            if should_reset_context:
                ctx.messages = ctx.messages[:1] + ctx.messages[-2:]
            elif len(ctx.messages) > 7:
                ctx.messages = ctx.messages[:1] + ctx.messages[-7:]
        for msg in ctx.messages:
            if hasattr(msg, 'parts'):
                for part in msg.parts:
                    if hasattr(part, 'text') and isinstance(part.text, str):
                        part.text = redact_genomic_phi(part.text)
                        if len(part.text) > 10000:
                            part.text = part.text[:10000] + "\n\n...[HEURISTIC TRUNCATION: Payload exceeded context limits.]..."
                        
    max_retries = 20
    for attempt in range(max_retries):
        try:
            if CONTEXT_SAFE_MODE:
                await asyncio.sleep(12.5)
            async with Aclosing(_original_llm_run(self, ctx, *args, **kwargs)) as agen:
                async for event in agen:
                    content = getattr(event, 'content', None)
                    if content:
                        for part in getattr(content, 'parts', None) or []:
                            if hasattr(part, 'text') and isinstance(part.text, str):
                                part.text = redact_genomic_phi(part.text)
                    yield event
            break
        except Exception as e:
            error_str = str(e)
            if "Zero-Trust Block" in error_str:
                print(f"[Zero-Trust Intercepted] Soft-Escalating Fatal Exception: {error_str}", flush=True)
                yield ZeroTrustEscalationEvent(f"[ESCALATING TO DIRECTOR]\n\nZERO-TRUST VIOLATION: {error_str}")
                break
            elif "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "503" in error_str or "UNAVAILABLE" in error_str:
                if attempt < max_retries - 1:
                    print(f"\n[API Throttle] 429/503 Quota hit. Cooldown (Attempt {attempt+1}/{max_retries})...", flush=True)
                    await asyncio.sleep(65)
                else:
                    raise
            else:
                raise

LlmAgent._run_async_impl = patched_llm_run
