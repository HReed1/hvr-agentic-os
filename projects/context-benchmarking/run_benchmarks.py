#!/usr/bin/env python3
"""
CLI entry point wrapper for the Context Benchmarking Harness.
Enables running the benchmarks from the root directory with mock LLM logic.
"""

import sys
import os
from unittest.mock import MagicMock

# Define original and solution file contents using triple single quotes
ORIGINAL_UTILS_PY = r'''# mock_codebase/app/utils.py
import time

def format_log_message(level: str, message: str, timestamp: float | None = None, metadata: dict | None = None) -> str:
    """
    Formats a log message with a timestamp and optional metadata.
    
    Baseline version:
    - Uses raw timestamp float representation instead of ISO 8601.
    - Does not sanitize newlines in message, leaving it vulnerable to log injection.
    - Does not validate the log level.
    - Uses str() representation of metadata instead of compact JSON.
    """
    t = timestamp if timestamp is not None else time.time()
    
    # Insecure representation and missing sanitization
    meta_str = f" | {metadata}" if metadata else ""
    return f"[{t}] {level.upper()}: {message}{meta_str}"
'''

SOLUTION_UTILS_PY = r"""# mock_codebase/app/utils.py
import time
from datetime import datetime, timezone
import json
import re

def format_log_message(level: str, message: str, timestamp: float | str | None = None, metadata: dict | None = None) -> str:
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    level_upper = level.upper()
    if level_upper not in valid_levels:
        raise ValueError(f"Invalid log level: {level}")
        
    t = timestamp if timestamp is not None else time.time()
    if isinstance(t, (int, float)):
        ts_str = datetime.fromtimestamp(t, tz=timezone.utc).isoformat()
    elif isinstance(t, str):
        ts_str = t
    else:
        raise ValueError("Invalid timestamp type")
        
    sanitized_msg = re.sub(r'[\r\n]+', ' ', message)
    
    meta_str = ""
    if metadata:
        meta_str = " | " + json.dumps(metadata, sort_keys=True, separators=(',', ':'))
        
    return f"[{ts_str}] {level_upper}: {sanitized_msg}{meta_str}"
"""

ORIGINAL_ROUTES_PY = r'''# mock_codebase/app/routes.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TaskItem(BaseModel):
    id: str
    title: str
    status: str

# In-memory mock database
MOCK_DB = [
    {"id": "1", "title": "Setup repository", "status": "completed"},
    {"id": "2", "title": "Design mock codebase", "status": "pending"},
    {"id": "3", "title": "Implement git manager", "status": "pending"},
    {"id": "4", "title": "Add test suites", "status": "completed"},
    {"id": "5", "title": "Run baseline benchmarks", "status": "pending"},
]

@app.get("/api/tasks")
def get_tasks():
    """
    Retrieves a list of tasks.
    
    Baseline version:
    - Returns a raw list of all tasks.
    - Lacks pagination (limit/offset) support.
    - Lacks filtering by status.
    """
    return MOCK_DB
'''

SOLUTION_ROUTES_PY = r"""# mock_codebase/app/routes.py
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

app = FastAPI()

class TaskItem(BaseModel):
    id: str
    title: str
    status: str

# In-memory mock database
MOCK_DB = [
    {"id": "1", "title": "Setup repository", "status": "completed"},
    {"id": "2", "title": "Design mock codebase", "status": "pending"},
    {"id": "3", "title": "Implement git manager", "status": "pending"},
    {"id": "4", "title": "Add test suites", "status": "completed"},
    {"id": "5", "title": "Run baseline benchmarks", "status": "pending"},
]

@app.get("/api/tasks")
def get_tasks(
    status: str | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    filtered = MOCK_DB
    if status is not None:
        filtered = [t for t in filtered if t["status"] == status]
    
    total = len(filtered)
    items = filtered[offset:offset+limit]
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset
    }
"""

ORIGINAL_API_CLIENT_JS = r"""// mock_codebase/app/apiClient.js

/**
 * Fetches tasks from the API.
 * 
 * Baseline version:
 * - Does not accept query options (status, limit, offset).
 * - Expects a raw JSON array back.
 */
export async function fetchTasks(baseUrl) {
  const response = await fetch(`${baseUrl}/api/tasks`);
  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }
  const data = await response.json();
  return data; // Assumes raw array: [ {id, title, status}, ... ]
}
"""

SOLUTION_API_CLIENT_JS = r"""// mock_codebase/app/apiClient.js

/**
 * Fetches tasks from the API.
 * 
 * Baseline version:
 * - Does not accept query options (status, limit, offset).
 * - Expects a raw JSON array back.
 */
export async function fetchTasks(baseUrl, options = {}) {
  const url = new URL(`${baseUrl}/api/tasks`);
  if (options.status) url.searchParams.append('status', options.status);
  if (options.limit !== undefined) url.searchParams.append('limit', options.limit);
  if (options.offset !== undefined) url.searchParams.append('offset', options.offset);
  
  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }
  const data = await response.json();
  return {
    tasks: data.items,
    total: data.total
  };
}
"""

ORIGINAL_WEBHOOKS_PY = r'''# mock_codebase/app/webhooks.py
from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel
import logging

app = FastAPI()
logger = logging.getLogger("webhooks")

# Simple mock database of processed event IDs for replay protection
PROCESSED_EVENTS = set()

# Secret keys (normally from environment)
SLACK_SIGNING_SECRET = "slack_secret_123"
GITHUB_WEBHOOK_SECRET = "github_secret_123"
STRIPE_WEBHOOK_SECRET = "stripe_secret_123"

class WebhookPayload(BaseModel):
    event_id: str
    event_type: str
    data: dict

@app.post("/webhooks/slack")
async def slack_webhook(
    request: Request,
    x_slack_signature: str = Header(None)
):
    """
    Slack Webhook endpoint.
    
    Baseline version:
    - Uses non-constant-time string comparison (==) for signature verification.
    - Lacks replay protection (does not check PROCESSED_EVENTS).
    - Lacks error sanitization (leaks internal exception message).
    """
    try:
        body = await request.json()
        payload = WebhookPayload(**body)
        
        # Insecure signature verification (uses raw string equality)
        # In production, Slack signatures involve hmac sha256 of timestamp + body
        expected_sig = "slack_sig_hash" # dummy check
        if x_slack_signature != expected_sig:
            raise HTTPException(status_code=401, detail="Invalid Slack signature")
        
        # Missing replay protection checks
        PROCESSED_EVENTS.add(payload.event_id)
        
        return {"status": "success", "event_id": payload.event_id}
    except Exception as e:
        # Insecure: Leaks raw exception message to the caller
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None)
):
    """
    GitHub Webhook endpoint.
    
    Baseline version:
    - Missing signature verification completely.
    - Lacks replay protection.
    - Lacks error sanitization.
    """
    try:
        body = await request.json()
        payload = WebhookPayload(**body)
        
        # Missing signature verification completely (always accepted)
        # Missing replay protection check
        PROCESSED_EVENTS.add(payload.event_id)
        
        return {"status": "success", "event_id": payload.event_id}
    except Exception as e:
        # Insecure: Leaks raw exception message to the caller
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    """
    Stripe Webhook endpoint.
    
    Baseline version:
    - Uses non-constant-time signature validation.
    - Lacks replay protection.
    - Lacks error sanitization.
    """
    try:
        body = await request.json()
        payload = WebhookPayload(**body)
        
        # Insecure signature check
        if not stripe_signature or stripe_signature != "stripe_sig_hash":
            raise HTTPException(status_code=400, detail="Invalid Stripe signature")
            
        # Missing replay protection check
        PROCESSED_EVENTS.add(payload.event_id)
        
        return {"status": "success", "event_id": payload.event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

SOLUTION_WEBHOOKS_PY = r"""# mock_codebase/app/webhooks.py
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import hmac
import hashlib

app = FastAPI()
logger = logging.getLogger("webhooks")

PROCESSED_EVENTS = set()

SLACK_SIGNING_SECRET = "slack_secret_123"
GITHUB_WEBHOOK_SECRET = "github_secret_123"
STRIPE_WEBHOOK_SECRET = "stripe_secret_123"

class WebhookPayload(BaseModel):
    event_id: str
    event_type: str
    data: dict

@app.post("/webhooks/slack")
async def slack_webhook(
    request: Request,
    x_slack_signature: str = Header(None),
    x_slack_request_timestamp: str = Header(None)
):
    try:
        body_bytes = await request.body()
        body = await request.json()
        payload = WebhookPayload(**body)
        
        if not x_slack_signature or not x_slack_request_timestamp:
            return JSONResponse(status_code=401, content={"detail": "Missing headers"})
        payload_str = f"v0:{x_slack_request_timestamp}:{body_bytes.decode()}"
        expected_sig = "v0=" + hmac.new(SLACK_SIGNING_SECRET.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(x_slack_signature, expected_sig):
            return JSONResponse(status_code=401, content={"detail": "Invalid Slack signature"})
        
        if payload.event_id in PROCESSED_EVENTS:
            return {"status": "ignored", "event_id": payload.event_id}
        PROCESSED_EVENTS.add(payload.event_id)
        
        return {"status": "success", "event_id": payload.event_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in slack webhook: {e}")
        return JSONResponse(status_code=500, content={"message": "An internal error occurred."})

@app.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None)
):
    try:
        body_bytes = await request.body()
        body = await request.json()
        payload = WebhookPayload(**body)
        
        if not x_hub_signature_256:
            return JSONResponse(status_code=401, content={"detail": "Missing signature"})
        expected_sig = "sha256=" + hmac.new(GITHUB_WEBHOOK_SECRET.encode(), body_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(x_hub_signature_256, expected_sig):
            return JSONResponse(status_code=401, content={"detail": "Invalid GitHub signature"})
        
        if payload.event_id in PROCESSED_EVENTS:
            return {"status": "ignored", "event_id": payload.event_id}
        PROCESSED_EVENTS.add(payload.event_id)
        
        return {"status": "success", "event_id": payload.event_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in github webhook: {e}")
        return JSONResponse(status_code=500, content={"message": "An internal error occurred."})

@app.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    try:
        body_bytes = await request.body()
        body = await request.json()
        payload = WebhookPayload(**body)
        
        t_val, v1_val = None, None
        if stripe_signature:
            parts = stripe_signature.split(",")
            for part in parts:
                if part.startswith("t="):
                    t_val = part[2:]
                elif part.startswith("v1="):
                    v1_val = part[3:]
        if not t_val or not v1_val:
            return JSONResponse(status_code=400, content={"detail": "Invalid Stripe signature"})
        
        payload_str = f"{t_val}.{body_bytes.decode()}"
        expected_sig = hmac.new(STRIPE_WEBHOOK_SECRET.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(v1_val, expected_sig):
            return JSONResponse(status_code=400, content={"detail": "Invalid Stripe signature"})
        
        if payload.event_id in PROCESSED_EVENTS:
            return {"status": "ignored", "event_id": payload.event_id}
        PROCESSED_EVENTS.add(payload.event_id)
        
        return {"status": "success", "event_id": payload.event_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in stripe webhook: {e}")
        return JSONResponse(status_code=500, content={"message": "An internal error occurred."})
"""

ORIGINAL_WEBHOOK_SIGNER_JS = r"""// mock_codebase/app/webhookSigner.js

/**
 * JS Helper to generate webhook signatures.
 * 
 * Baseline version:
 * - Stubbed implementations returning empty or static values.
 */

export function generateSlackSignature(secret, timestamp, body) {
  return "stubbed_slack_sig";
}

export function generateGithubSignature(secret, body) {
  return "stubbed_github_sig";
}

export function generateStripeSignature(secret, timestamp, body) {
  return "stubbed_stripe_sig";
}
"""

SOLUTION_WEBHOOK_SIGNER_JS = r"""// mock_codebase/app/webhookSigner.js
import crypto from 'crypto';

/**
 * JS Helper to generate webhook signatures.
 * 
 * Baseline version:
 * - Stubbed implementations returning empty or static values.
 */

export function generateSlackSignature(secret, timestamp, body) {
  const payload = `v0:${timestamp}:${body}`;
  const hash = crypto.createHmac('sha256', secret).update(payload).digest('hex');
  return `v0=${hash}`;
}

export function generateGithubSignature(secret, body) {
  const hash = crypto.createHmac('sha256', secret).update(body).digest('hex');
  return `sha256=${hash}`;
}

export function generateStripeSignature(secret, timestamp, body) {
  const payload = `${timestamp}.${body}`;
  const hash = crypto.createHmac('sha256', secret).update(payload).digest('hex');
  return `t=${timestamp},v1=${hash}`;
}
"""


class MockFunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args


class MockPart:
    def __init__(self, text=None, thought=None, function_call=None):
        self.text = text
        self.thought = thought
        self.function_call = function_call


class MockContent:
    def __init__(self, parts):
        self.parts = parts


class MockResponse:
    def __init__(self, content, prompt_tokens, candidates_tokens):
        self.candidates = [MagicMock(content=content)]
        self.usage_metadata = MagicMock(
            prompt_token_count=prompt_tokens, candidates_token_count=candidates_tokens
        )


def mock_generate_content(*args, **kwargs):
    contents = kwargs.get("contents", [])
    user_text = contents[0].parts[0].text

    if "mock_codebase/app/utils.py" in user_text:
        task_id = "small_task"
    elif "mock_codebase/app/routes.py" in user_text:
        task_id = "medium_task"
    else:
        task_id = "large_task"

    tools = kwargs.get("config").tools
    tool_names = [t.__name__ for t in tools]
    if "view_file_tool" in tool_names:
        scenario = "A"
    else:
        scenario = "B"

    step_idx = len(contents) // 2

    print(f"[MOCK LLM] Task: {task_id} | Scenario: {scenario} | Step: {step_idx}")

    # Return different token sizes for Scenario A vs Scenario B
    prompt_tokens = 2000 if scenario == "A" else 500
    candidates_tokens = 200

    if task_id == "small_task":
        if step_idx == 0:
            tool_name = (
                "view_file_tool" if scenario == "A" else "view_ast_skeleton_tool"
            )
            part = MockPart(
                text="Viewing utils.py to locate format_log_message function.",
                thought=True,
                function_call=MockFunctionCall(
                    name=tool_name, args={"path": "mock_codebase/app/utils.py"}
                ),
            )
        elif step_idx == 1:
            part = MockPart(
                text="Applying solution to utils.py.",
                thought=True,
                function_call=MockFunctionCall(
                    name="replace_file_content_tool",
                    args={
                        "path": "mock_codebase/app/utils.py",
                        "target": ORIGINAL_UTILS_PY,
                        "replacement": SOLUTION_UTILS_PY,
                        "StartLine": 1,
                        "EndLine": 18,
                    },
                ),
            )
        else:
            part = MockPart(text="Task completed.", thought=False)

    elif task_id == "medium_task":
        if step_idx == 0:
            tool_name = (
                "view_file_tool" if scenario == "A" else "view_ast_skeleton_tool"
            )
            part = MockPart(
                text="Viewing routes.py to locate the tasks route.",
                thought=True,
                function_call=MockFunctionCall(
                    name=tool_name, args={"path": "mock_codebase/app/routes.py"}
                ),
            )
        elif step_idx == 1:
            part = MockPart(
                text="Applying pagination changes to routes.py.",
                thought=True,
                function_call=MockFunctionCall(
                    name="replace_file_content_tool",
                    args={
                        "path": "mock_codebase/app/routes.py",
                        "target": ORIGINAL_ROUTES_PY,
                        "replacement": SOLUTION_ROUTES_PY,
                        "StartLine": 1,
                        "EndLine": 32,
                    },
                ),
            )
        elif step_idx == 2:
            tool_name = (
                "view_file_tool" if scenario == "A" else "view_ast_skeleton_tool"
            )
            part = MockPart(
                text="Viewing apiClient.js to locate fetchTasks function.",
                thought=True,
                function_call=MockFunctionCall(
                    name=tool_name, args={"path": "mock_codebase/app/apiClient.js"}
                ),
            )
        elif step_idx == 3:
            part = MockPart(
                text="Applying pagination changes to apiClient.js.",
                thought=True,
                function_call=MockFunctionCall(
                    name="replace_file_content_tool",
                    args={
                        "path": "mock_codebase/app/apiClient.js",
                        "target": ORIGINAL_API_CLIENT_JS,
                        "replacement": SOLUTION_API_CLIENT_JS,
                        "StartLine": 1,
                        "EndLine": 18,
                    },
                ),
            )
        else:
            part = MockPart(text="Task completed.", thought=False)

    elif task_id == "large_task":
        if step_idx == 0:
            tool_name = (
                "view_file_tool" if scenario == "A" else "view_ast_skeleton_tool"
            )
            part = MockPart(
                text="Viewing webhooks.py to inspect webhook routes.",
                thought=True,
                function_call=MockFunctionCall(
                    name=tool_name, args={"path": "mock_codebase/app/webhooks.py"}
                ),
            )
        elif step_idx == 1:
            part = MockPart(
                text="Hardening webhooks.py signature verification and error sanitization.",
                thought=True,
                function_call=MockFunctionCall(
                    name="replace_file_content_tool",
                    args={
                        "path": "mock_codebase/app/webhooks.py",
                        "target": ORIGINAL_WEBHOOKS_PY,
                        "replacement": SOLUTION_WEBHOOKS_PY,
                        "StartLine": 1,
                        "EndLine": 106,
                    },
                ),
            )
        elif step_idx == 2:
            tool_name = (
                "view_file_tool" if scenario == "A" else "view_ast_skeleton_tool"
            )
            part = MockPart(
                text="Viewing webhookSigner.js.",
                thought=True,
                function_call=MockFunctionCall(
                    name=tool_name, args={"path": "mock_codebase/app/webhookSigner.js"}
                ),
            )
        elif step_idx == 3:
            part = MockPart(
                text="Implementing webhook signing in webhookSigner.js.",
                thought=True,
                function_call=MockFunctionCall(
                    name="replace_file_content_tool",
                    args={
                        "path": "mock_codebase/app/webhookSigner.js",
                        "target": ORIGINAL_WEBHOOK_SIGNER_JS,
                        "replacement": SOLUTION_WEBHOOK_SIGNER_JS,
                        "StartLine": 1,
                        "EndLine": 21,
                    },
                ),
            )
        else:
            part = MockPart(text="Task completed.", thought=False)

    content = MockContent(parts=[part])
    return MockResponse(content, prompt_tokens, candidates_tokens)


# Monkeypatch google.genai.Client class property and initializer
import google.genai


class PatchedModels:
    def __init__(self):
        self.generate_content = mock_generate_content


google.genai.Client.models = property(lambda self: PatchedModels())


def patched_client_init(self, *args, **kwargs):
    pass


google.genai.Client.__init__ = patched_client_init

# Add src/ directory to system path to ensure context_benchmarking package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from context_benchmarking.run_benchmarks import main

if __name__ == "__main__":
    sys.exit(main())
