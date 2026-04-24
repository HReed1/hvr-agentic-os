import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.hello import print_hello

def test_print_hello(capsys):
    print_hello()
    captured = capsys.readouterr()
    assert captured.out == 'Goodbye\n'
