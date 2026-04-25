import pytest
from api.notification_router import NotificationRouter, SMSHandler, PagerHandler

def test_sms_handler():
    assert SMSHandler.handle("alert") == "SMS: alert"

def test_pager_handler():
    assert PagerHandler.handle("alert") == "PAGER: alert"

def test_notification_router_high():
    assert NotificationRouter.route_message("system down", "HIGH") == "SMS: system down"

def test_notification_router_low():
    assert NotificationRouter.route_message("system slow", "LOW") == "PAGER: system slow"

def test_notification_router_invalid():
    with pytest.raises(KeyError):
        NotificationRouter.route_message("hello", "UNKNOWN")
