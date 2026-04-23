import csv

class GenericParser:
    @staticmethod
    def load_dict_from_csv(path: str) -> dict:
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                return {row[0]: row[1] for row in csv.reader(f) if len(row) >= 2}
        except FileNotFoundError:
            return {}
