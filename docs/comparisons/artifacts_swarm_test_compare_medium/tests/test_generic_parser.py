import os
import csv
from utils.generic_parser import GenericParser

def test_load_dict_from_csv_success(tmp_path):
    csv_file = tmp_path / "test.csv"
    with open(csv_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "value"])
        writer.writerow(["name", "John"])
        writer.writerow(["age", "30"])

    result = GenericParser.load_dict_from_csv(str(csv_file))
    assert result == {"name": "John", "age": "30"}

def test_load_dict_from_csv_file_not_found():
    result = GenericParser.load_dict_from_csv("non_existent_file.csv")
    assert result == {}
