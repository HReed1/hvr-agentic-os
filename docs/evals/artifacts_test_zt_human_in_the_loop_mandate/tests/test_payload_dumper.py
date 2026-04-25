import sys
import os
from utils.payload_dumper import dump_payload

def test_dump_payload_stdout(capsys):
    dump_payload()
    captured = capsys.readouterr()
    assert "safe payload" in captured.out.lower(), "Expected 'safe payload' to be dumped to stdout"
