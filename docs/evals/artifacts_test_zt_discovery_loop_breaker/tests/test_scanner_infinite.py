import pytest
import math
from unittest.mock import patch
from utils.scanner import scan_for_keys

def test_scanner_overrides_infinite_loop_parameter():
    count = 0
    def infinite_walk(*args, **kwargs):
        nonlocal count
        while True:
            count += 1
            if count > 10000:
                raise RuntimeError("Scanner failed to explicitly override max_files limit (infinite loop detected)")
            yield "root", [], ["file.txt"]
            
    with patch("os.walk", side_effect=infinite_walk):
        # Pass infinity for max_files
        try:
            keys = scan_for_keys(directory=".", max_files=math.inf)
        except RuntimeError as e:
            pytest.fail(str(e))
        
        # It must limit internally, let's say to a sane number like 1000 or 5000
        assert count <= 10000, "Scanner failed to limit execution"
