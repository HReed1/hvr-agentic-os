import os

def scan_for_keys(directory: str = ".", max_files: int | float = 100) -> list:
    max_files = min(max_files, 1000)
    keys = []
    scanned = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if scanned >= max_files:
                return keys
            scanned += 1
    return keys
