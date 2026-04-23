from abc import ABC, abstractmethod

class NotificationHandler(ABC):
    @abstractmethod
    def handle(self, message: str) -> str:
        pass

class SMSHandler(NotificationHandler):
    def handle(self, message: str) -> str:
        return f"SMS: {message}"

class PagerHandler(NotificationHandler):
    def handle(self, message: str) -> str:
        return f"PAGER: {message}"

class NotificationRouter:
    _handlers = {
        "HIGH": SMSHandler(),
        "LOW": PagerHandler()
    }

    @staticmethod
    def route_message(message: str, severity: str) -> str:
        handler = NotificationRouter._handlers.get(severity)
        if handler:
            return handler.handle(message)
        raise ValueError(f"Unknown severity: {severity}")
