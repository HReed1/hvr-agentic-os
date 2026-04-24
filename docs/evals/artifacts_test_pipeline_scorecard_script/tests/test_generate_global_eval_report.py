import os
import pytest
from unittest.mock import patch, mock_open
from utils.generate_global_eval_report import (
    _extract_test_name,
    _classify_result,
    _build_latest_results,
    _format_scorecard,
    generate_scorecard,
    SCORECARD_PATH
)

def test_extract_test_name():
    filename = "2023-10-15_my_feature_swarm_eval.md"
    assert _extract_test_name(filename) == "my_feature"
    
    filename2 = "2023-10-15_other_feature_solo_eval.md"
    assert _extract_test_name(filename2) == "other_feature"
    
    filename3 = "not_matching_format.md"
    assert _extract_test_name(filename3) == "not_matching_format.md"

def test_classify_result():
    assert _classify_result("Some text \n[PASS]\n more text") == "✅ PASS"
    assert _classify_result("RESULT: PASS") == "✅ PASS"
    assert _classify_result("Some text \n[FAIL]\n more text") == "❌ FAIL"
    assert _classify_result("RESULT: FAIL") == "❌ FAIL"
    assert _classify_result("No clear outcome here") == "⚠️ UNKNOWN"

def test_build_latest_results():
    files = [
        "docs/evals/2023-10-14_feature_a_solo_eval.md",
        "docs/evals/2023-10-15_feature_a_solo_eval.md",
        "docs/evals/2023-10-15_feature_b_swarm_eval.md"
    ]
    latest = _build_latest_results(files)
    assert len(latest) == 2
    assert "feature_a" in latest
    assert "feature_b" in latest
    assert latest["feature_a"] == "docs/evals/2023-10-15_feature_a_solo_eval.md"

def test_format_scorecard():
    results = [
        ("2023-10-15_feature_a_solo_eval.md", "✅ PASS"),
        ("2023-10-15_feature_b_swarm_eval.md", "❌ FAIL"),
        ("2023-10-15_feature_c_swarm_eval.md", "⚠️ UNKNOWN")
    ]
    date_str = "2023-10-15 12:00:00"
    content, rate = _format_scorecard(results, date_str)
    
    assert rate == (1 / 3) * 100
    assert "**Total Evaluations:** 3" in content
    assert "**Passed:** 1" in content
    assert "**Failed:** 1" in content
    assert "**Unknown/Pending:** 1" in content
    assert "33.3%" in content

@patch("utils.generate_global_eval_report.glob.glob")
@patch("builtins.open", new_callable=mock_open, read_data="[PASS]")
@patch("utils.generate_global_eval_report.datetime")
@patch("builtins.print")
def test_generate_scorecard(mock_print, mock_datetime, mock_file, mock_glob):
    mock_glob.return_value = ["docs/evals/2023-10-15_feature_a_solo_eval.md", SCORECARD_PATH]
    mock_datetime.now.return_value.strftime.return_value = "2023-10-15 12:00:00"
    
    generate_scorecard()
    
    mock_file.assert_any_call(SCORECARD_PATH, 'w')
    mock_print.assert_any_call(f"\n[GLOBAL SCORECARD] Final Pass Rate: 100.0%")
    mock_print.assert_any_call(f"Read full breakdown at: {SCORECARD_PATH}\n")
