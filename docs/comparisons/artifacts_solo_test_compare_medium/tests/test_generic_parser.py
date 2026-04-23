import os
import pytest
from utils.generic_parser import GenericParser

def test_load_dict_from_csv_success(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("key1,value1\nkey2,value2\n")
    
    result = GenericParser.load_dict_from_csv(str(csv_file))
    assert result == {"key1": "value1", "key2": "value2"}

def test_load_dict_from_csv_file_not_found():
    result = GenericParser.load_dict_from_csv("non_existent_file.csv")
    assert result == {}
