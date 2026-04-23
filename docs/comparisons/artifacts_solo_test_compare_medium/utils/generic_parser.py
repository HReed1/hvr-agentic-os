import csv

class GenericParser:
    @staticmethod
    def load_dict_from_csv(path: str) -> dict:
        result = {}
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        result[row[0]] = row[1]
        except FileNotFoundError:
            return {}
        return result
