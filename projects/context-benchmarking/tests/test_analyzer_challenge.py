import os
import json
import tempfile
import ast
import pytest
from unittest.mock import patch, MagicMock

import context_benchmarking.analyzer as cb_analyzer
from context_benchmarking.analyzer import (
    OfflineAnalyzer,
    TokenReadEvent,
    TokenSavingsReport,
    SkeletonTransformer,
)

# =====================================================================
# 1. TOKENIZER FALLBACK ACCURACY UNDER MISSING PACKAGES
# =====================================================================


def test_tokenizer_fallback_missing_packages():
    """Verify tokenizer count fallback behavior and accuracy when tiktoken is missing or failing."""
    analyzer = OfflineAnalyzer()

    # Save original _has_tiktoken state
    original_has_tiktoken = cb_analyzer._has_tiktoken

    try:
        # Case A: tiktoken is missing (ImportError simulated)
        cb_analyzer._has_tiktoken = False

        # Test empty input
        assert analyzer.count_tokens("") == 0
        assert analyzer.count_tokens(None) == 0

        # Test boundary cases (length < 4)
        # int(1 / 3.8) = 0
        assert analyzer.count_tokens("a") == 0
        # int(3 / 3.8) = 0
        assert analyzer.count_tokens("abc") == 0
        # int(4 / 3.8) = 1
        assert analyzer.count_tokens("abcd") == 1

        # Test precision fallback ratio exactly int(len / 3.8)
        text = (
            "Hello, this is a test string to check the token count accuracy fallback."
        )
        expected_tokens = int(len(text) / 3.8)
        assert analyzer.count_tokens(text) == expected_tokens

        # Case B: tiktoken is present but fails during encoding
        cb_analyzer._has_tiktoken = True
        with patch("tiktoken.get_encoding") as mock_get_encoding:
            # Simulate general Exception when calling get_encoding
            mock_get_encoding.side_effect = Exception("failed to load encoding")
            assert analyzer.count_tokens(text) == expected_tokens

        with patch("tiktoken.get_encoding") as mock_get_encoding:
            mock_encoder = MagicMock()
            # Simulate Exception when calling encode
            mock_encoder.encode.side_effect = Exception("encode failure")
            mock_get_encoding.return_value = mock_encoder
            assert analyzer.count_tokens(text) == expected_tokens

    finally:
        cb_analyzer._has_tiktoken = original_has_tiktoken


# =====================================================================
# 2. SLICING AND RECONSTRUCTION UNDER MALFORMED INPUTS OR TRUNCATED LOGS
# =====================================================================


def test_reconstruction_malformed_or_truncated():
    """Verify reconstruction logic under malformed view outputs or truncated logs."""
    analyzer = OfflineAnalyzer()

    # Case A: Truncated output (stops in the middle of a line, or line numbers skip)
    view_output_truncated = """
   1: import os
   2: def test():
   3:     print("trunc
"""
    reconstructed = analyzer.reconstruct_file_from_view_output(view_output_truncated)
    assert reconstructed.strip() == 'import os\ndef test():\n    print("trunc'

    # Case B: Malformed output containing compilation/error logs interspersed
    view_output_with_errors = """
   1: def first():
   2:     pass
Error: Process finished with exit code 1
   3: def second():
   4:     pass
"""
    reconstructed = analyzer.reconstruct_file_from_view_output(view_output_with_errors)
    # The error line should be skipped
    expected = "def first():\n    pass\ndef second():\n    pass"
    assert reconstructed.strip() == expected

    # Case C: Python code containing line that accidentally matches the prefix regex
    # Regex: r'^\s*(\d+):(?: (.*))?$'
    # If the user has a line of python code like `  123: "value"` (e.g. inside a dict),
    # but the tool output was NOT line-numbered (or was line-numbered and it got doubly stripped).
    # First, let's see what happens if code has no line numbers but contains a matching pattern:
    code_with_dict_element = """
my_dict = {
    42: "answer",
    100: "percent"
}
"""
    reconstructed = analyzer.reconstruct_file_from_view_output(code_with_dict_element)
    # Check that reconstruction preserves the dictionary intact
    assert reconstructed.strip() == code_with_dict_element.strip()

    # Let's verify how parse_transcript handles this if we pass such output.
    # If a non-line-numbered view output contains a line matching `^\s*(\d+):(.*)`,
    # the parser gets the original code instead of the mangled code.
    transcript_data = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "my_dict.py"},
                "output": code_with_dict_element,
            }
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        t_path = os.path.join(temp_dir, "transcript.json")
        with open(t_path, "w") as f:
            json.dump(transcript_data, f)
        report = analyzer.parse_transcript(t_path)
        event = report.events[0]
        original_tokens = analyzer.count_tokens(code_with_dict_element)
        assert event.scenario_a_tokens == original_tokens


# =====================================================================
# 3. OVERLAPPING CLASS/METHOD RANGES IN SYMBOL RESOLUTION
# =====================================================================


def test_overlapping_symbol_resolution():
    """Verify symbol extraction and block recovery with overlapping/nested classes and methods."""
    analyzer = OfflineAnalyzer()

    # Nested functions and classes
    code = """
class OuterClass:
    def method_one(self):
        def nested_helper():
            pass
        return nested_helper()
    
    def method_two(self):
        pass
"""
    symbols = analyzer.extract_symbols(code)
    # Expected symbols sorted by start line:
    # 1. OuterClass (class)
    # 2. method_one (function)
    # 3. nested_helper (function)
    # 4. method_two (function)
    assert len(symbols) == 4
    assert [s["name"] for s in symbols] == [
        "OuterClass",
        "method_one",
        "nested_helper",
        "method_two",
    ]

    # Verify that get_symbol_block retrieves overlapping/nested ranges
    # block of OuterClass should include everything
    outer_block = analyzer.get_symbol_block(code, "OuterClass")
    assert "class OuterClass:" in outer_block
    assert "def method_two(self):" in outer_block

    # block of method_one should contain nested_helper but not method_two
    method_one_block = analyzer.get_symbol_block(code, "method_one")
    assert "def method_one(self):" in method_one_block
    assert "def nested_helper():" in method_one_block
    assert "method_two" not in method_one_block

    # Check double-counting potential:
    # If method_one is edited, both OuterClass and method_one will match the edit line range.
    # If the edit is on the line of return nested_helper() (line 6), which falls within:
    # - OuterClass (lines 2-9)
    # - method_one (lines 3-6)
    # Both are marked as inspected symbols.
    # Let's check how parse_transcript counts Scenario B tokens for this.
    transcript_data = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "nested.py"},
                "output": f"   1: {code.splitlines()[1]}\n"
                + "\n".join(
                    f"{i+2:4d}: {line}" for i, line in enumerate(code.splitlines()[2:])
                ),
            },
            {
                "tool": "replace_file_content",
                "arguments": {"TargetFile": "nested.py", "StartLine": 5, "EndLine": 6},
            },
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        t_path = os.path.join(temp_dir, "transcript.json")
        with open(t_path, "w") as f:
            json.dump(transcript_data, f)
        report = analyzer.parse_transcript(t_path)
        event = report.events[0]
        # Both OuterClass and method_one are inspected
        assert "OuterClass" in event.inspected_symbols
        assert "method_one" in event.inspected_symbols

        # Verify double counting:
        # Scenario B cost should be: skeleton_cost + cost(OuterClass) + cost(method_one)
        # Note: cost(OuterClass) already includes cost(method_one).
        # Thus, cost(method_one) is counted twice.


# =====================================================================
# 4. SCENARIO B CALCULATION ACCURACY (CAPPED AT SCENARIO A COST)
# =====================================================================


def test_scenario_b_capped_at_scenario_a():
    """Verify that Scenario B cost is capped at Scenario A cost, preventing negative savings."""
    analyzer = OfflineAnalyzer()

    # Create a code file where skeleton + double counted nested symbols exceed full code size.
    code = """
class LargeClass:
    def method_a(self):
        print("large method line 1")
        print("large method line 2")
        print("large method line 3")
        print("large method line 4")
        print("large method line 5")
"""
    # Verify Scenario B token calculation capping
    # If method_a is edited, both LargeClass and method_a are inspected.
    # cost(LargeClass) is almost equal to the whole file.
    # cost(method_a) is also significant.
    # cost(skeleton) + cost(LargeClass) + cost(method_a) > cost(whole file)
    transcript_data = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "large_class.py"},
                "output": "\n".join(
                    f"{i+1:4d}: {line}" for i, line in enumerate(code.splitlines())
                ),
            },
            {
                "tool": "replace_file_content",
                "arguments": {
                    "TargetFile": "large_class.py",
                    "StartLine": 4,
                    "EndLine": 6,
                },
            },
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        t_path = os.path.join(temp_dir, "transcript.json")
        with open(t_path, "w") as f:
            json.dump(transcript_data, f)
        report = analyzer.parse_transcript(t_path)
        event = report.events[0]

        # Verify the cap is applied: scenario_b_tokens must be exactly equal to scenario_a_tokens
        assert event.scenario_b_tokens == event.scenario_a_tokens
        assert event.savings_tokens == 0
        assert report.total_scenario_b_tokens == report.total_scenario_a_tokens
        assert report.total_savings_tokens == 0
        assert report.savings_percentage == 0.0


# =====================================================================
# 5. PATH AND QUOTE PARSING ROBUSTNESS UNDER WEIRD FORMATS
# =====================================================================


def test_path_and_quote_parsing_robustness():
    """Verify path comparison and edit matching under absolute/relative and quote-wrapped paths."""
    analyzer = OfflineAnalyzer()

    # Case A: Absolute path in view_file and relative path in edit (or vice-versa)
    # The analyzer uses direct string comparison: os.path.normpath(s_file_path) == norm_file_path.
    # This means relative and absolute paths referring to the same file do NOT match.
    transcript_data = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "/workspace/src/app.py"},
                "output": "   1: def run():\n   2:     pass",
            },
            {
                "tool": "replace_file_content",
                "arguments": {"TargetFile": "src/app.py", "StartLine": 1, "EndLine": 2},
            },
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        t_path = os.path.join(temp_dir, "transcript.json")
        with open(t_path, "w") as f:
            json.dump(transcript_data, f)

        report = analyzer.parse_transcript(t_path)
        event = report.events[0]
        # With the fix, absolute vs relative path mismatch is resolved.
        # Let's verify that run() is in inspected_symbols.
        assert "run" in event.inspected_symbols

    # Case B: Quote wrapping in path strings
    # The analyzer strips single and double quotes: file_path = args[path_key].strip("'\"")
    # Verify that single/double quotes around paths are handled correctly.
    transcript_data_quotes = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "'/workspace/src/app.py'"},
                "output": "   1: def run():\n   2:     pass",
            },
            {
                "tool": "replace_file_content",
                "arguments": {
                    "TargetFile": '"/workspace/src/app.py"',
                    "StartLine": 1,
                    "EndLine": 2,
                },
            },
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        t_path = os.path.join(temp_dir, "transcript.json")
        with open(t_path, "w") as f:
            json.dump(transcript_data_quotes, f)

        report = analyzer.parse_transcript(t_path)
        event = report.events[0]
        # Since both paths have their quotes stripped, they should match as "/workspace/src/app.py".
        # Therefore, run() should be marked as inspected.
        assert "run" in event.inspected_symbols

    # Case C: Weird path variations (whitespace, duplicate slashes, parent directory traversal)
    # The analyzer uses normpath, which resolves duplicates and parent directory traversals.
    transcript_data_weird_paths = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "/workspace/src/foo/../app.py"},
                "output": "   1: def run():\n   2:     pass",
            },
            {
                "tool": "replace_file_content",
                "arguments": {
                    "TargetFile": "/workspace//src/app.py",
                    "StartLine": 1,
                    "EndLine": 2,
                },
            },
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        t_path = os.path.join(temp_dir, "transcript.json")
        with open(t_path, "w") as f:
            json.dump(transcript_data_weird_paths, f)

        report = analyzer.parse_transcript(t_path)
        event = report.events[0]
        # Both normalize to "/workspace/src/app.py" via os.path.normpath, so the edit is matched.
        assert "run" in event.inspected_symbols
