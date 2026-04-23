import pytest
import os
import tempfile
from utils.generic_parser import GenericParser

def test_load_dict_from_csv_success():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tf:
        tf.write("key1,value1\nkey2,value2\n")
        tf_path = tf.name
    
    try:
        result = GenericParser.load_dict_from_csv(tf_path)
        assert result == {"key1": "value1", "key2": "value2"}
    finally:
        os.remove(tf_path)

def test_load_dict_from_csv_file_not_found():
    result = GenericParser.load_dict_from_csv("/non/existent/path.csv")
    assert result == {}
