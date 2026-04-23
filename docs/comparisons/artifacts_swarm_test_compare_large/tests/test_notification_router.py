import pytest
from api.notification_router import NotificationRouter, SMSHandler, PagerHandler

def test_sms_handler():
    handler = SMSHandler()
    assert handler.handle("Test SMS") == "SMS: Test SMS"

def test_pager_handler():
    handler = PagerHandler()
    assert handler.handle("Test Pager") == "PAGER: Test Pager"

def test_route_message_high():
    result = NotificationRouter.route_message("Critical issue", "HIGH")
    assert result == "SMS: Critical issue"

def test_route_message_low():
    result = NotificationRouter.route_message("Minor issue", "LOW")
    assert result == "PAGER: Minor issue"

def test_route_message_invalid():
    with pytest.raises(ValueError):
        NotificationRouter.route_message("Unknown", "MEDIUM")
