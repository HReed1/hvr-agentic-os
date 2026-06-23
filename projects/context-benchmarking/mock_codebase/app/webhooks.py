# mock_codebase/app/webhooks.py
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
