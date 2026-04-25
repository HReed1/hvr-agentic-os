#!/usr/bin/env python3
import os
import shutil
import glob
from pathlib import Path

def archive_evals():
    """
    Archives all current active evaluation markdown reports into their legacy directories.
    Helps organize the workspace prior to running a fresh evaluation suite.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    docs_evals_dir = os.path.join(base_dir, "docs", "evals")
    docs_retro_dir = os.path.join(base_dir, "docs", "evals", "retrospectives")
    
    legacy_evals_dir = os.path.join(docs_evals_dir, "legacy")
    legacy_retro_dir = os.path.join(docs_retro_dir, "legacy")
    
    # Ensure legacy directories exist
    os.makedirs(legacy_evals_dir, exist_ok=True)
    os.makedirs(legacy_retro_dir, exist_ok=True)
    
    archived_evals = 0
    archived_retros = 0
    
    # 1. Archive main evals
    if os.path.exists(docs_evals_dir):
        # We only want to move .md files in the root of docs/evals/
        # Do not recursively pull from retrospectives or legacy
        for filepath in glob.glob(os.path.join(docs_evals_dir, "*.md")):
            if os.path.isfile(filepath):
                filename = os.path.basename(filepath)
                dest = os.path.join(legacy_evals_dir, filename)
                shutil.move(filepath, dest)
                archived_evals += 1
                
    # 2. Archive retrospective evals
    if os.path.exists(docs_retro_dir):
        for filepath in glob.glob(os.path.join(docs_retro_dir, "*.md")):
            if os.path.isfile(filepath):
                filename = os.path.basename(filepath)
                dest = os.path.join(legacy_retro_dir, filename)
                shutil.move(filepath, dest)
                archived_retros += 1

    print(f"✅ Archive complete.")
    print(f"   Moved {archived_evals} reports to docs/evals/legacy/")
    print(f"   Moved {archived_retros} retrospectives to docs/evals/retrospectives/legacy/")

if __name__ == "__main__":
    archive_evals()
