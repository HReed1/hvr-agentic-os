import pytest
from api.notification_router import NotificationRouter, SMSHandler, PagerHandler
import os

def test_sms_handler():
    assert SMSHandler.handle("alert") == "SMS: alert"

def test_pager_handler():
    assert PagerHandler.handle("alert") == "PAGER: alert"

def test_router_high():
    assert NotificationRouter.route_message("server down", "HIGH") == "SMS: server down"

def test_router_low():
    assert NotificationRouter.route_message("disk usage warning", "LOW") == "PAGER: disk usage warning"

def test_router_invalid():
    assert NotificationRouter.route_message("info", "MEDIUM") == "UNKNOWN: info"
