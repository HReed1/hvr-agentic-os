import os
import pytest
from utils.generic_parser import GenericParser

@pytest.fixture
def temp_csv_file():
    file_path = "test_data.csv"
    with open(file_path, "w") as f:
        f.write("key1,value1\nkey2,value2\n")
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path)

def test_load_dict_success(temp_csv_file):
    result = GenericParser.load_dict_from_csv(temp_csv_file)
    assert result == {"key1": "value1", "key2": "value2"}

def test_load_dict_file_not_found():
    result = GenericParser.load_dict_from_csv("non_existent_file.csv")
    assert result == {}
