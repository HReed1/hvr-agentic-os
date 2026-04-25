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


def _extract_telemetry(content):
    """Extract total inferences and token counts from eval file content."""
    inferences = 0
    tokens_in = 0
    tokens_out = 0

    # Match: **Total LLM Inferences:** `19`
    inf_match = re.search(r'\*\*Total LLM Inferences:\*\*\s*`(\d+)`', content)
    if inf_match:
        inferences = int(inf_match.group(1))

    # Match trace breakdown lines: - **agent**: N inferences [In: X | Out: Y]
    for m in re.finditer(r'\[In:\s*([\d,]+)\s*\|\s*Out:\s*([\d,]+)\]', content):
        tokens_in += int(m.group(1).replace(',', ''))
        tokens_out += int(m.group(2).replace(',', ''))

    return inferences, tokens_in, tokens_out


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
    passed = sum(1 for _, s, _, _, _ in results if "PASS" in s)
    failed = sum(1 for _, s, _, _, _ in results if "FAIL" in s)
    unknown = len(results) - passed - failed
    total = len(results)
    rate = (passed / total) * 100 if total > 0 else 0

    total_inferences = sum(inf for _, _, inf, _, _ in results)
    total_tokens_in = sum(ti for _, _, _, ti, _ in results)
    total_tokens_out = sum(to for _, _, _, _, to in results)

    lines = [
        "# Autonomous Swarm Global Evaluation Scorecard\n",
        f"\n> **Generated:** {date_str}\n",
        "\n## Aggregated Performance\n",
        f"\n- **Total Evaluations:** {total}",
        f"\n- **Passed:** {passed}",
        f"\n- **Failed:** {failed}",
        f"\n- **Unknown/Pending:** {unknown}",
        f"\n- **Final Score:** `{rate:.1f}%`\n",
        "\n## Inference Metrics\n",
        f"\n- **Total LLM Inferences:** {total_inferences:,}",
        f"\n- **Total Input Tokens:** {total_tokens_in:,}",
        f"\n- **Total Output Tokens:** {total_tokens_out:,}",
        f"\n- **Total Tokens:** {total_tokens_in + total_tokens_out:,}\n",
        "\n## Evaluation Breakdown\n",
        "\n| Status | Inferences | Tokens (In/Out) | Evaluation File |",
        "\n|---|---|---|---|",
    ]
    for filename, status, inf, ti, to in sorted(results, key=lambda x: x[1]):
        token_str = f"{ti:,} / {to:,}" if inf > 0 else "—"
        inf_str = str(inf) if inf > 0 else "—"
        lines.append(f"\n| {status} | {inf_str} | {token_str} | `{filename}` |")
    lines.append("\n")
    return "".join(lines), rate


def generate_scorecard():
    files = [f for f in glob.glob(os.path.join(EVALS_DIR, "*.md")) if f != SCORECARD_PATH]
    latest = _build_latest_results(files)

    results = []
    for filepath in latest.values():
        filename = os.path.basename(filepath)
        with open(filepath, 'r') as f:
            content = f.read()
        status = _classify_result(content)
        inferences, tokens_in, tokens_out = _extract_telemetry(content)
        results.append((filename, status, inferences, tokens_in, tokens_out))

    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    md_content, rate = _format_scorecard(results, date_str)

    with open(SCORECARD_PATH, 'w') as f:
        f.write(md_content)

    total_inf = sum(inf for _, _, inf, _, _ in results)
    total_tok = sum(ti + to for _, _, _, ti, to in results)
    print(f"\n[GLOBAL SCORECARD] Final Pass Rate: {rate:.1f}%")
    print(f"[GLOBAL SCORECARD] Total Inferences: {total_inf:,} | Total Tokens: {total_tok:,}")
    print(f"Read full breakdown at: {SCORECARD_PATH}\n")


if __name__ == "__main__":
    generate_scorecard()
