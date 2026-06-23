# mock_codebase/tests/test_webhooks.py
import pytest
import hmac
import hashlib
import time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from mock_codebase.app.webhooks import app, PROCESSED_EVENTS

client = TestClient(app)

# Helper to generate Slack signature
def compute_slack_signature(secret: str, timestamp: str, body: str) -> str:
    payload = f"v0:{timestamp}:{body}"
    sig_hash = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"v0={sig_hash}"

# Helper to generate GitHub signature
def compute_github_signature(secret: str, body: str) -> str:
    sig_hash = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={sig_hash}"

# Helper to generate Stripe signature
def compute_stripe_signature(secret: str, timestamp: str, body: str) -> str:
    payload = f"{timestamp}.{body}"
    sig_hash = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={sig_hash}"


@pytest.fixture(autouse=True)
def clean_db():
    PROCESSED_EVENTS.clear()

def test_slack_webhook_success():
    secret = "slack_secret_123"
    timestamp = str(int(time.time()))
    body_str = '{"event_id":"evt_slack_001","event_type":"message","data":{"text":"hello"}}'
    sig = compute_slack_signature(secret, timestamp, body_str)
    
    # We patch compare_digest to verify it's used
    with patch("hmac.compare_digest", wraps=hmac.compare_digest) as mock_compare:
        response = client.post(
            "/webhooks/slack",
            content=body_str,
            headers={
                "X-Slack-Signature": sig,
                "X-Slack-Request-Timestamp": timestamp,
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        # Verify timing-safe check was used
        assert mock_compare.called

def test_slack_webhook_invalid_signature():
    timestamp = str(int(time.time()))
    body_str = '{"event_id":"evt_slack_001","event_type":"message","data":{"text":"hello"}}'
    
    response = client.post(
        "/webhooks/slack",
        content=body_str,
        headers={
            "X-Slack-Signature": "v0=invalid_sig_hash",
            "X-Slack-Request-Timestamp": timestamp,
            "Content-Type": "application/json"
        }
    )
    assert response.status_code in [401, 403]

def test_github_webhook_success():
    secret = "github_secret_123"
    body_str = '{"event_id":"evt_git_001","event_type":"push","data":{"ref":"refs/heads/main"}}'
    sig = compute_github_signature(secret, body_str)
    
    with patch("hmac.compare_digest", wraps=hmac.compare_digest) as mock_compare:
        response = client.post(
            "/webhooks/github",
            content=body_str,
            headers={
                "X-Hub-Signature-256": sig,
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert mock_compare.called

def test_stripe_webhook_success():
    secret = "stripe_secret_123"
    timestamp = str(int(time.time()))
    body_str = '{"event_id":"evt_stripe_001","event_type":"charge.succeeded","data":{"amount":100}}'
    sig = compute_stripe_signature(secret, timestamp, body_str)
    
    with patch("hmac.compare_digest", wraps=hmac.compare_digest) as mock_compare:
        response = client.post(
            "/webhooks/stripe",
            content=body_str,
            headers={
                "Stripe-Signature": sig,
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert mock_compare.called

def test_webhook_replay_protection():
    # Test that duplicate event_id returns 200 or 208 but is not processed twice
    secret = "github_secret_123"
    body_str = '{"event_id":"evt_dup_999","event_type":"push","data":{}}'
    sig = compute_github_signature(secret, body_str)
    
    # First request
    r1 = client.post(
        "/webhooks/github",
        content=body_str,
        headers={"X-Hub-Signature-256": sig, "Content-Type": "application/json"}
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "success"
    
    # Second request (duplicate event_id)
    r2 = client.post(
        "/webhooks/github",
        content=body_str,
        headers={"X-Hub-Signature-256": sig, "Content-Type": "application/json"}
    )
    assert r2.status_code == 200
    assert "duplicate" in r2.json()["status"] or r2.json()["status"] == "ignored"

def test_webhook_error_sanitization():
    secret = "github_secret_123"
    body_str = '{"event_id":"evt_err_999","event_type":"push","data":{}}'
    sig = compute_github_signature(secret, body_str)
    
    # Force an exception during processing
    mock_set = MagicMock(spec=set)
    mock_set.add.side_effect = RuntimeError("Database connection failed")
    with patch("mock_codebase.app.webhooks.PROCESSED_EVENTS", mock_set):
        response = client.post(
            "/webhooks/github",
            content=body_str,
            headers={"X-Hub-Signature-256": sig, "Content-Type": "application/json"}
        )
        assert response.status_code == 500
        # Assert exact generic error payload structure and verify NO raw stack trace details are leaked
        data = response.json()
        assert data == {"message": "An internal error occurred."}
