#!/usr/bin/env python3
import os
import glob
from datetime import datetime
import re

EVALS_DIR = "docs/evals"
SCORECARD_PATH = os.path.join(EVALS_DIR, "GLOBAL_EVAL_SCORECARD.md")

def generate_scorecard():
    # Find all current markdown files in docs/evals/ (excluding legacy)
    files = [f for f in glob.glob(os.path.join(EVALS_DIR, "*.md")) if f != SCORECARD_PATH]
    
    total_tests = 0
    passed = 0
    failed = 0
    unknown = 0
    
    results = []
    
    for filepath in files:
        filename = os.path.basename(filepath)
        total_tests += 1
        with open(filepath, 'r') as f:
            content = f.read()
            
            # Regex search for standard ADK terminal outputs or Result strings
            if re.search(r'(?i)\[PASS\]|\bRESULT\b.*PASS', content):
                passed += 1
                status = "✅ PASS"
            elif re.search(r'(?i)\[FAIL\]|\bRESULT\b.*FAIL', content):
                failed += 1
                status = "❌ FAIL"
            else:
                unknown += 1
                status = "⚠️ UNKNOWN"
            
            results.append((filename, status))
            
    # Calculate score
    pass_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    
    # Generate Markdown payload
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    md_content = f"# Autonomous Swarm Global Evaluation Scorecard\n\n"
    md_content += f"> **Generated:** {date_str}\n\n"
    
    md_content += f"## Aggregated Performance\n\n"
    md_content += f"- **Total Evaluations:** {total_tests}\n"
    md_content += f"- **Passed:** {passed}\n"
    md_content += f"- **Failed:** {failed}\n"
    md_content += f"- **Unknown/Pending:** {unknown}\n"
    md_content += f"- **Final Score:** `{pass_rate:.1f}%`\n\n"
    
    md_content += f"## Evaluation Breakdown\n\n"
    md_content += f"| Status | Evaluation File |\n"
    md_content += f"|---|---|\n"
    
    for filename, status in sorted(results, key=lambda x: x[1]):
        md_content += f"| {status} | `{filename}` |\n"
        
    with open(SCORECARD_PATH, 'w') as f:
        f.write(md_content)
        
    print(f"\n[GLOBAL SCORECARD] Final Pass Rate: {pass_rate:.1f}%")
    print(f"Read full breakdown at: {SCORECARD_PATH}\n")

if __name__ == "__main__":
    generate_scorecard()
