import os
import shutil
from agent_app.tools import write_eval_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Setup mock retrospective
retro_dir = os.path.join(BASE_DIR, "docs", "retrospectives")
os.makedirs(retro_dir, exist_ok=True)
mock_retro_path = os.path.join(retro_dir, "2026-04-21_mock_test_swarm.md")
with open(mock_retro_path, "w") as f:
    f.write("# Mock Retrospective\nSwarm completed successfully.\n")

# 2. Trigger the write_eval_report pipeline
result = write_eval_report("test_eng_cyclomatic_complexity", "Test Meta Evaluator Content", True)
print(result)

# 3. Assert and read outputs!
import glob
print("\n--- EVAL REPORT ---")
eval_reports = glob.glob(os.path.join(BASE_DIR, "docs", "evals", "*test_eng_cyclomatic_complexity*eval.md"))
if eval_reports:
    with open(eval_reports[0], "r") as f:
        print(f.read())
else:
    print("NO EVAL REPORT FOUND")

print("\n--- MOVED RETROSPECTIVE ---")
dest_dir = os.path.join(BASE_DIR, "docs", "evals", "retrospectives")
moved_retros = glob.glob(os.path.join(dest_dir, "2026-04-21_mock_test_swarm.md"))
if moved_retros:
    with open(moved_retros[0], "r") as f:
        print(f.read())
else:
    print("NO MOVED RETROSPECTIVE FOUND")
