import sys
import os
import csv
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.generic_parser import GenericParser

def test_load_dict_from_csv_success():
    # Setup temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
        writer = csv.writer(tmp)
        writer.writerow(['key', 'value'])
        writer.writerow(['k1', 'v1'])
        writer.writerow(['k2', 'v2'])
        tmp_path = tmp.name

    try:
        result = GenericParser.load_dict_from_csv(tmp_path)
        assert result == {'k1': 'v1', 'k2': 'v2'}
    finally:
        os.remove(tmp_path)

def test_load_dict_from_csv_file_not_found():
    result = GenericParser.load_dict_from_csv("non_existent_file_path_12345.csv")
    assert result == {}
