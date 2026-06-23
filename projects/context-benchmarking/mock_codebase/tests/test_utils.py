# mock_codebase/tests/test_utils.py
import pytest
import time
from datetime import datetime, timezone
import json
from mock_codebase.app.utils import format_log_message

def test_format_log_message_basic():
    # Test message with specific timestamp
    ts = 1785000000.0 # float timestamp
    res = format_log_message("INFO", "Operation successful", timestamp=ts)
    
    # Expected timestamp format in UTC is ISO 8601
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    expected_ts = dt.isoformat()
    
    assert res.startswith(f"[{expected_ts}]")
    assert "INFO: Operation successful" in res

def test_format_log_message_invalid_level():
    with pytest.raises(ValueError):
        format_log_message("INVALID_LEVEL", "Should fail")

def test_format_log_message_case_insensitivity():
    # Validation should convert lowercase to uppercase and pass
    ts = 1785000000.0
    res = format_log_message("info", "Lowercase level", timestamp=ts)
    assert "INFO: Lowercase level" in res

def test_format_log_message_sanitization():
    # Message containing newlines should be sanitized to prevent log injection
    injected_message = "Line 1\nLine 2\r\nLine 3"
    res = format_log_message("WARNING", injected_message, timestamp=1785000000.0)
    
    # Newlines and carriage returns should be replaced by a single space
    assert "\n" not in res
    assert "\r" not in res
    assert "WARNING: Line 1 Line 2 Line 3" in res

def test_format_log_message_metadata():
    # Metadata should be serialized to compact sorted JSON
    metadata = {"z_key": "val1", "a_key": "val2", "nested": {"num": 42}}
    res = format_log_message("ERROR", "Failed processing", timestamp=1785000000.0, metadata=metadata)
    
    # Assert exact formatting of metadata at the end
    expected_meta_str = '{"a_key":"val2","nested":{"num":42},"z_key":"val1"}'
    assert res.endswith(f" | {expected_meta_str}")
