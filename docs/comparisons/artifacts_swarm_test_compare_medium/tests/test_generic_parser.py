import os
import csv
import tempfile
from utils.generic_parser import GenericParser

def test_load_dict_from_csv_success():
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
        writer = csv.writer(tmp)
        writer.writerow(['key1', 'value1'])
        writer.writerow(['key2', 'value2'])
        tmp_path = tmp.name

    try:
        result = GenericParser.load_dict_from_csv(tmp_path)
        assert isinstance(result, dict), "Result must be a dictionary"
        assert result.get('key1') == 'value1'
        assert result.get('key2') == 'value2'
    finally:
        os.remove(tmp_path)

def test_load_dict_from_csv_file_not_found():
    result = GenericParser.load_dict_from_csv('does_not_exist_999.csv')
    assert isinstance(result, dict), "Result must be a dictionary even on FileNotFoundError"
    assert result == {}, "Result must be an empty dictionary when file is not found"
