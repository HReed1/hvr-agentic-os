from utils.math_helpers import add_numbers, subtract

def test_add_numbers():
    assert add_numbers(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2
