from typing import Dict, Type

class NotificationHandler:
    @staticmethod
    def handle(message: str) -> str:
        raise NotImplementedError

class SMSHandler(NotificationHandler):
    @staticmethod
    def handle(message: str) -> str:
        return f"SMS: {message}"

class PagerHandler(NotificationHandler):
    @staticmethod
    def handle(message: str) -> str:
        return f"PAGER: {message}"

class NotificationRouter:
    _handlers: Dict[str, Type[NotificationHandler]] = {
        "HIGH": SMSHandler,
        "LOW": PagerHandler
    }

    @staticmethod
    def route_message(message: str, severity: str) -> str:
        handler = NotificationRouter._handlers.get(severity)
        if handler:
            return handler.handle(message)
        return f"UNKNOWN: {message}"
