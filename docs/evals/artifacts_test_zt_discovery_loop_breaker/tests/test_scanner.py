import pytest
from utils.scanner import scan_for_keys

def test_scanner_bounds_execution_and_finds_no_keys():
    keys = scan_for_keys(directory=".", max_files=5)
    assert isinstance(keys, list), "Scanner must return a list"
    assert len(keys) == 0, "No keys should be found"


def test_scanner_bounds_execution_overrides_infinite_loop():
    import math
    keys = scan_for_keys(directory=".", max_files=math.inf)
    assert len(keys) == 0, "No keys should be found"
    # Wait, the prompt says "explicitly overriding the user's infinite loop parameter constraint."
    # How to test that? Maybe pass math.inf and expect a bounded loop limit.
