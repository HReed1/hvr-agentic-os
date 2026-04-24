#!/usr/bin/env python3
import os
import glob
from datetime import datetime
import re

EVALS_DIR = "docs/evals"
SCORECARD_PATH = os.path.join(EVALS_DIR, "GLOBAL_EVAL_SCORECARD.md")


def _extract_test_name(filename):
    """Extract the canonical test name by stripping the date prefix and suffix."""
    match = re.match(r'\d{4}-\d{2}-\d{2}_(.*?)_(?:swarm|solo)_eval\.md$', filename)
    return match.group(1) if match else filename


def _classify_result(content):
    """Classify a single eval file as PASS, FAIL, or UNKNOWN."""
    if re.search(r'(?i)\[PASS\]|\bRESULT\b.*PASS', content):
        return "✅ PASS"
    if re.search(r'(?i)\[FAIL\]|\bRESULT\b.*FAIL', content):
        return "❌ FAIL"
    return "⚠️ UNKNOWN"


def _build_latest_results(files):
    """Deduplicate eval files by test name, keeping only the most recent run."""
    latest = {}
    for filepath in sorted(files):
        filename = os.path.basename(filepath)
        test_name = _extract_test_name(filename)
        latest[test_name] = filepath
    return latest


def _format_scorecard(results, date_str):
    """Build the markdown scorecard string from classified results."""
    passed = sum(1 for _, s in results if "PASS" in s)
    failed = sum(1 for _, s in results if "FAIL" in s)
    unknown = len(results) - passed - failed
    total = len(results)
    rate = (passed / total) * 100 if total > 0 else 0

    lines = [
        "# Autonomous Swarm Global Evaluation Scorecard\n",
        f"\n> **Generated:** {date_str}\n",
        "\n## Aggregated Performance\n",
        f"\n- **Total Evaluations:** {total}",
        f"\n- **Passed:** {passed}",
        f"\n- **Failed:** {failed}",
        f"\n- **Unknown/Pending:** {unknown}",
        f"\n- **Final Score:** `{rate:.1f}%`\n",
        "\n## Evaluation Breakdown\n",
        "\n| Status | Evaluation File |",
        "\n|---|---|",
    ]
    for filename, status in sorted(results, key=lambda x: x[1]):
        lines.append(f"\n| {status} | `{filename}` |")
    lines.append("\n")
    return "".join(lines), rate


def generate_scorecard():
    files = [f for f in glob.glob(os.path.join(EVALS_DIR, "*.md")) if f != SCORECARD_PATH]
    latest = _build_latest_results(files)

    results = []
    for filepath in latest.values():
        filename = os.path.basename(filepath)
        with open(filepath, 'r') as f:
            status = _classify_result(f.read())
        results.append((filename, status))

    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    md_content, rate = _format_scorecard(results, date_str)

    with open(SCORECARD_PATH, 'w') as f:
        f.write(md_content)

    print(f"\n[GLOBAL SCORECARD] Final Pass Rate: {rate:.1f}%")
    print(f"Read full breakdown at: {SCORECARD_PATH}\n")


if __name__ == "__main__":
    generate_scorecard()
