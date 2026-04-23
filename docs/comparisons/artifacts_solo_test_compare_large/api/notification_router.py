from abc import ABC, abstractmethod

class BaseHandler(ABC):
    @abstractmethod
    def handle(self, message: str) -> str:
        pass

class SMSHandler(BaseHandler):
    def handle(self, message: str) -> str:
        return f"SMS: {message}"

class PagerHandler(BaseHandler):
    def handle(self, message: str) -> str:
        return f"PAGER: {message}"

class NotificationRouter:
    _HANDLERS = {
        "HIGH": SMSHandler(),
        "LOW": PagerHandler()
    }

    @staticmethod
    def route_message(message: str, severity: str) -> str:
        handler = NotificationRouter._HANDLERS.get(severity)
        if not handler:
            raise ValueError(f"Unknown severity: {severity}")
        return handler.handle(message)
