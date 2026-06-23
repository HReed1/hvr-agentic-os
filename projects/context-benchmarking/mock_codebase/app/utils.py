# mock_codebase/app/utils.py
import time

def format_log_message(level: str, message: str, timestamp: float | None = None, metadata: dict | None = None) -> str:
    """
    Formats a log message with a timestamp and optional metadata.
    
    Baseline version:
    - Uses raw timestamp float representation instead of ISO 8601.
    - Does not sanitize newlines in message, leaving it vulnerable to log injection.
    - Does not validate the log level.
    - Uses str() representation of metadata instead of compact JSON.
    """
    t = timestamp if timestamp is not None else time.time()
    
    # Insecure representation and missing sanitization
    meta_str = f" | {metadata}" if metadata else ""
    return f"[{t}] {level.upper()}: {message}{meta_str}"
