from api.notification_router import NotificationRouter

def test_route_message_high():
    result = NotificationRouter.route_message("system down", "HIGH")
    assert result == "SMS: system down"

def test_route_message_low():
    result = NotificationRouter.route_message("high cpu", "LOW")
    assert result == "PAGER: high cpu"

def test_route_message_unknown():
    result = NotificationRouter.route_message("hello", "MEDIUM")
    assert result == "UNKNOWN: hello"
