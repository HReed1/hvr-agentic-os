class NotificationHandler:
    def handle(self, message: str) -> str:
        raise NotImplementedError

class SMSHandler(NotificationHandler):
    def handle(self, message: str) -> str:
        return f"SMS: {message}"

class PagerHandler(NotificationHandler):
    def handle(self, message: str) -> str:
        return f"PAGER: {message}"

class NotificationRouter:
    _dispatch_map = {
        "HIGH": SMSHandler(),
        "LOW": PagerHandler()
    }

    @staticmethod
    def route_message(message: str, severity: str) -> str:
        handler = NotificationRouter._dispatch_map.get(severity)
        return handler.handle(message) if handler else "UNKNOWN SEVERITY"
