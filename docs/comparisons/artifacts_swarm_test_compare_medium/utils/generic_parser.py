import csv

class GenericParser:
    @staticmethod
    def load_dict_from_csv(path: str) -> dict:
        result = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                for row in csv.reader(f):
                    if len(row) >= 2:
                        result[row[0]] = row[1]
        except FileNotFoundError:
            pass
        return result
