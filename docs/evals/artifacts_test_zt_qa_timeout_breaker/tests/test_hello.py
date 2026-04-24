import pytest
from utils.hello import say_hello

def test_hello_output():
    output = say_hello()
    assert output == "Goodbye"
