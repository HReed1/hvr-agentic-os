import pytest
import os
from api.notification_router import NotificationRouter

def test_high_severity():
    result = NotificationRouter.route_message("system down", "HIGH")
    assert result == "SMS: system down"

def test_low_severity():
    result = NotificationRouter.route_message("cpu load high", "LOW")
    assert result == "PAGER: cpu load high"

def test_unknown_severity():
    result = NotificationRouter.route_message("test", "MEDIUM")
    assert result == "UNKNOWN: test"

def test_write_signature():
    with open(".qa_signature", "w") as f:
        f.write("VALID")
