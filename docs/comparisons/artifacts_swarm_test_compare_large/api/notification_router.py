class SMSHandler:
    def handle(self, message: str) -> str:
        return f"SMS: {message}"

class PagerHandler:
    def handle(self, message: str) -> str:
        return f"PAGER: {message}"

class NotificationRouter:
    _handlers = {
        "HIGH": SMSHandler,
        "LOW": PagerHandler
    }

    @staticmethod
    def route_message(message: str, severity: str) -> str:
        handler_class = NotificationRouter._handlers.get(severity)
        if not handler_class:
            raise ValueError(f"Invalid severity: {severity}")
        return handler_class().handle(message)
