import pytest
from api.notification_router import NotificationRouter

def test_route_message_high():
    assert NotificationRouter.route_message("system down", "HIGH") == "SMS: system down"

def test_route_message_low():
    assert NotificationRouter.route_message("system slow", "LOW") == "PAGER: system slow"

def test_route_message_unknown():
    assert NotificationRouter.route_message("hello", "UNKNOWN") == "UNKNOWN SEVERITY"
