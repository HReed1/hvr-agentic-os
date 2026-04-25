import os
import sys
import glob

sys.path.append('/Users/harrisonreed/Projects/hvr-agentic-os')
from utils.ast_validation_mcp import measure_cyclomatic_complexity

def _get_target_files():
    python_files = []
    for d in ["api", "agent_app", "utils"]:
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
    return sorted(python_files)

def _parse_report(report: str, filepath: str) -> str:
    if "[ERROR]" in report:
        return f"| `{filepath}` | N/A (Parse Error) | N/A |"
        
    scores = []
    for line in report.split("\n"):
        line = line.strip()
        if line.startswith("- ") and ":" in line:
            try:
                scores.append(int(line.split(":")[-1].strip()))
            except ValueError:
                pass
                
    if not scores:
        return f"| `{filepath}` | N/A (No branches) | N/A |"
        
    avg = round(sum(scores) / len(scores), 1)
    highest = max(scores)
    
    avg_flag = "🟢" if avg <= 5 else ("🟡" if avg <= 8 else "🔴")
    highest_flag = "🟢" if highest <= 5 else ("🟡" if highest <= 8 else "🔴")
    
    return f"| `{filepath}` | {avg} {avg_flag} | {highest} {highest_flag} |"

def main():
    print("# Codebase Cyclomatic Complexity Scorecard\n")
    print("| Target File | Average Complexity | Highest Node |")
    print("|-------------|--------------------|--------------|")
    
    for filepath in _get_target_files():
        print(_parse_report(measure_cyclomatic_complexity(filepath), filepath))
        
if __name__ == "__main__":
    main()
