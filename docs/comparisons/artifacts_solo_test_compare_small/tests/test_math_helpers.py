import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.math_helpers import add_numbers, subtract

def test_add_numbers():
    assert add_numbers(2, 3) == 5
    assert add_numbers(-1, 1) == 0

def test_subtract():
    assert subtract(5, 2) == 3
    assert subtract(10, 10) == 0
