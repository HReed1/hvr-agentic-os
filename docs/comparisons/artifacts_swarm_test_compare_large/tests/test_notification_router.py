import pytest
from api.notification_router import NotificationRouter, SMSHandler, PagerHandler

def test_sms_handler():
    handler = SMSHandler()
    assert handler.handle("test") == "SMS: test"

def test_pager_handler():
    handler = PagerHandler()
    assert handler.handle("test") == "PAGER: test"

def test_notification_router_high():
    assert NotificationRouter.route_message("critical issue", "HIGH") == "SMS: critical issue"

def test_notification_router_low():
    assert NotificationRouter.route_message("minor issue", "LOW") == "PAGER: minor issue"

def test_notification_router_invalid():
    with pytest.raises(ValueError):
        NotificationRouter.route_message("unknown", "UNKNOWN")
