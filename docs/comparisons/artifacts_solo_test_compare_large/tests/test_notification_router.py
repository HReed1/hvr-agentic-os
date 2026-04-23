import pytest
from api.notification_router import NotificationRouter, SMSHandler, PagerHandler

def test_sms_handler():
    handler = SMSHandler()
    assert handler.handle("test") == "SMS: test"

def test_pager_handler():
    handler = PagerHandler()
    assert handler.handle("test") == "PAGER: test"

def test_notification_router_high():
    result = NotificationRouter.route_message("System failure", "HIGH")
    assert result == "SMS: System failure"

def test_notification_router_low():
    result = NotificationRouter.route_message("Disk space low", "LOW")
    assert result == "PAGER: Disk space low"

def test_notification_router_unknown():
    with pytest.raises(ValueError, match="Unknown severity: UNKNOWN"):
        NotificationRouter.route_message("Something", "UNKNOWN")
