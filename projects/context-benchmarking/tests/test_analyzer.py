import os
import json
import tempfile
import ast
import pytest
from unittest.mock import patch, MagicMock

from context_benchmarking.analyzer import (
    OfflineAnalyzer,
    TokenReadEvent,
    TokenSavingsReport,
    SkeletonTransformer,
)


def test_count_tokens_fallback():
    """Verify tokenizer count fallbacks when tiktoken is not installed or raises errors."""
    analyzer = OfflineAnalyzer()

    # Test empty string
    assert analyzer.count_tokens("") == 0
    assert analyzer.count_tokens(None) == 0

    # Test fallback directly by mocking _has_tiktoken as False
    import context_benchmarking.analyzer as cb_analyzer

    original_has_tiktoken = cb_analyzer._has_tiktoken

    cb_analyzer._has_tiktoken = False
    try:
        # 38 characters / 3.8 = 10 tokens
        assert analyzer.count_tokens("a" * 38) == 10
    finally:
        cb_analyzer._has_tiktoken = original_has_tiktoken

    # Test fallback when tiktoken raises an error
    cb_analyzer._has_tiktoken = True
    with patch("tiktoken.get_encoding", side_effect=Exception("mock tiktoken error")):
        assert analyzer.count_tokens("a" * 38) == 10


def test_ast_skeleton_generation_python():
    """Verify AST skeleton generation for Python code strips bodies and keeps docstrings."""
    analyzer = OfflineAnalyzer()

    code = """
class MyClass:
    \"\"\"This is a class docstring.\"\"\"
    def my_method(self):
        \"\"\"Method docstring.\"\"\"
        x = 1
        return x

def my_function(a, b):
    # Some comment
    return a + b
"""
    skeleton = analyzer.generate_ast_skeleton(code)

    # Check that it compiles
    tree = ast.parse(skeleton)
    assert isinstance(tree, ast.Module)

    # ClassDef should exist and its body should contain the docstring
    assert "class MyClass:" in skeleton
    assert "This is a class docstring." in skeleton
    assert "pass" in skeleton
    # Class method is now preserved in the skeleton
    assert "def my_method" in skeleton
    assert "def my_function" in skeleton


def test_skeleton_generation_fallbacks():
    """Verify key extraction and regex fallbacks for other extensions, including async and default exports in JS/TS."""
    analyzer = OfflineAnalyzer()

    # JSON fallback
    json_code = '{"name": "test", "items": [{"id": 1, "value": "A"}]}'
    json_skeleton = analyzer.generate_ast_skeleton(json_code)
    loaded = json.loads(json_skeleton)
    assert loaded["name"] == "..."
    assert isinstance(loaded["items"], list)
    assert loaded["items"][0]["id"] == "..."
    assert loaded["items"][0]["value"] == "..."

    # Markdown fallback
    md_code = """
# Main Page
Welcome
## Section 1
Content
### Subsection 1.1
Detail
"""
    md_skeleton = analyzer.generate_ast_skeleton(md_code)
    assert "# Main Page" in md_skeleton
    assert "## Section 1" in md_skeleton
    assert "### Subsection 1.1" in md_skeleton
    assert "Welcome" not in md_skeleton

    # JS/TS fallback
    js_code = """
import { something } from 'lib';
export default class Helper {
    constructor() {}
}
export async function utility(arg) {
    return arg * 2;
}
async function localAsync() {
    return 1;
}
const arrowFunc = () => {
    console.log("hello");
};
"""
    js_skeleton = analyzer.generate_ast_skeleton(js_code)
    assert "export default class Helper" in js_skeleton
    assert "export async function utility" in js_skeleton
    assert "async function localAsync" in js_skeleton
    assert "const arrowFunc = () =>" in js_skeleton
    assert "console.log" not in js_skeleton


def test_reconstruct_file_from_view_output():
    """Verify that file reconstruction strips line number prefixes."""
    analyzer = OfflineAnalyzer()

    view_output = """
   1: import os
   2: 
   3: class Foo:
   4:     def bar(self):
   5:         pass
"""
    reconstructed = analyzer.reconstruct_file_from_view_output(view_output)
    expected = "import os\n\nclass Foo:\n    def bar(self):\n        pass"
    assert reconstructed.strip() == expected.strip()


def test_symbol_extraction_and_block():
    """Verify symbol extraction, line range matching, and block recovery with fully-qualified names."""
    analyzer = OfflineAnalyzer()

    code = """
class MyClass:
    def my_method(self):
        pass

def my_function(a, b):
    result = a + b
    return result
"""
    symbols = analyzer.extract_symbols(code)

    # Check symbol details
    assert len(symbols) == 3
    assert symbols[0]["name"] == "MyClass"
    assert symbols[0]["type"] == "class"
    assert symbols[1]["name"] == "my_method"
    assert symbols[1]["qname"] == "MyClass.my_method"
    assert symbols[1]["type"] == "function"
    assert symbols[2]["name"] == "my_function"
    assert symbols[2]["qname"] == "my_function"
    assert symbols[2]["type"] == "function"

    # Check block retrieval
    func_block = analyzer.get_symbol_block(code, "my_function")
    assert "result = a + b" in func_block
    assert "class MyClass" not in func_block

    class_block = analyzer.get_symbol_block(code, "MyClass")
    assert "class MyClass" in class_block
    assert "def my_method" in class_block
    assert "my_function" not in class_block


def test_parse_mock_transcript_log():
    """Verify transcript parsing, scenario B heuristics, and reporting."""
    analyzer = OfflineAnalyzer()

    transcript_data = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "app.py"},
                "output": """
   1: class App:
   2:     def run(self):
   3:         print("Running")
   4: 
   5: def greet():
   6:     print("Hello")
   7: 
   8: def large_unrelated():
   9:     print("Some text here to increase the token count of this function significantly.")
  10:     print("Some text here to increase the token count of this function significantly.")
  11:     print("Some text here to increase the token count of this function significantly.")
  12:     print("Some text here to increase the token count of this function significantly.")
  13:     print("Some text here to increase the token count of this function significantly.")
  14:     print("Some text here to increase the token count of this function significantly.")
  15:     print("Some text here to increase the token count of this function significantly.")
  16:     print("Some text here to increase the token count of this function significantly.")
  17:     print("Some text here to increase the token count of this function significantly.")
  18:     print("Some text here to increase the token count of this function significantly.")
""",
                "thinking": "I need to inspect the App class and maybe modify run method.",
            },
            {
                "tool": "replace_file_content",
                "arguments": {"TargetFile": "app.py", "StartLine": 2, "EndLine": 3},
            },
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "config.json"},
                "output": '{"port": 8080}',
            },
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "utils.py"},
                "output": """
   1: def helper_one():
   2:     print("Some text here to increase the token count of this function significantly.")
   3:     print("Some text here to increase the token count of this function significantly.")
   4:     print("Some text here to increase the token count of this function significantly.")
   5:     return 1
   6: 
   7: def helper_two():
   8:     print("Some text here to increase the token count of this function significantly.")
   9:     print("Some text here to increase the token count of this function significantly.")
  10:     print("Some text here to increase the token count of this function significantly.")
  11:     return 2
""",
            },
        ]
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        transcript_path = os.path.join(temp_dir, "mock_transcript.json")
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f)

        report = analyzer.parse_transcript(transcript_path)

        # Verify structure
        assert isinstance(report, TokenSavingsReport)
        assert len(report.events) == 3

        # event 0: app.py (Python)
        event_app = report.events[0]
        assert event_app.file_path == "app.py"
        assert event_app.is_python is True
        # App and App.run are inspected because:
        # - run is inside App and got edited (lines 2-3 overlap with App lines 1-3)
        # - App is mentioned in thinking block
        assert "App" in event_app.inspected_symbols
        # Scenario B cost should be skeleton cost + App cost (since App range covers App.run, no double-counting)
        assert event_app.scenario_b_tokens < event_app.scenario_a_tokens

        # event 1: config.json (non-Python)
        event_config = report.events[1]
        assert event_config.file_path == "config.json"
        assert event_config.is_python is False
        # JSON skeleton is supported, but config has no subsequent edits, so cost is just skeleton cost.
        # Note: For small JSON files, skeleton cost can equal full cost due to minimal structure.
        assert event_config.scenario_b_tokens <= event_config.scenario_a_tokens
        assert event_config.savings_tokens >= 0

        # event 2: utils.py (Python, not edited, not mentioned)
        event_utils = report.events[2]
        assert event_utils.file_path == "utils.py"
        assert event_utils.is_python is True
        assert len(event_utils.inspected_symbols) == 0
        # Cost B should be average size of top-level symbols (helper_one, helper_two)
        assert event_utils.scenario_b_tokens < event_utils.scenario_a_tokens


def test_tokenizer_fallback_accuracy():
    """Verify tokenizer fallback accuracy issues under missing tiktoken."""
    analyzer = OfflineAnalyzer()

    import context_benchmarking.analyzer as cb_analyzer

    original_has_tiktoken = cb_analyzer._has_tiktoken

    cb_analyzer._has_tiktoken = False
    try:
        # Non-ASCII text (e.g. Chinese characters)
        chinese_text = "你好世界" * 100  # 400 characters
        fallback_count = analyzer.count_tokens(chinese_text)
        assert fallback_count == 105

        # Indentation text
        indent_text = "    " * 100  # 400 spaces
        fallback_indent_count = analyzer.count_tokens(indent_text)
        assert fallback_indent_count == 105
    finally:
        cb_analyzer._has_tiktoken = original_has_tiktoken


def test_slicing_and_reconstruction_malformed():
    """Verify that file reconstruction successfully recovers lines under malformed input (no space or tabs after colon)."""
    analyzer = OfflineAnalyzer()

    view_output = """
   1: import os
   2:def foo():
   3:\tprint("hello")
   4:    pass
"""
    reconstructed = analyzer.reconstruct_file_from_view_output(view_output)
    expected = 'import os\ndef foo():\n\tprint("hello")\n   pass'
    assert reconstructed.strip() == expected.strip()
    assert "def foo():" in reconstructed
    assert "print" in reconstructed


def test_overlapping_symbols_and_duplicate_names():
    """Verify that symbol name collisions are resolved via qualification."""
    analyzer = OfflineAnalyzer()

    code = """
class MyClass:
    def my_method(self):
        print("class method")

def my_method(a):
    print("global function")
"""

    symbols = analyzer.extract_symbols(code)
    assert len(symbols) == 3
    assert symbols[0]["name"] == "MyClass"
    assert symbols[1]["name"] == "my_method"
    assert symbols[1]["qname"] == "MyClass.my_method"
    assert symbols[2]["name"] == "my_method"
    assert symbols[2]["qname"] == "my_method"

    # Querying by the qualified name returns the class method
    class_method_block = analyzer.get_symbol_block(code, "MyClass.my_method")
    assert "class method" in class_method_block
    assert "global function" not in class_method_block

    # Querying by the simple name returns the global method (since it's not qualified)
    global_method_block = analyzer.get_symbol_block(code, "my_method")
    assert "global function" in global_method_block
    assert "class method" not in global_method_block


def test_scenario_b_calculation_and_mismatches():
    """Verify Scenario B cost calculation for non-python files works as expected."""
    analyzer = OfflineAnalyzer()

    js_transcript = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "index.js"},
                "output": "export class Controller {\n  constructor() {}\n  action() {\n    doSomething();\n  }\n}",
            }
        ]
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        transcript_path = os.path.join(temp_dir, "js_transcript.json")
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(js_transcript, f)

        report = analyzer.parse_transcript(transcript_path)
        assert len(report.events) == 1
        event = report.events[0]
        assert event.file_path == "index.js"
        assert event.is_python is False
        assert event.scenario_b_tokens < event.scenario_a_tokens
        assert event.savings_tokens > 0


def test_path_and_quote_parsing_robustness():
    """Verify that path parsing is robust under absolute vs relative path combinations."""
    analyzer = OfflineAnalyzer(repo_path="/Users/harrisonreed/project")

    transcript_data = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "/Users/harrisonreed/project/app.py"},
                "output": """
   1: def run():
   2:     print("original")
""",
            },
            {
                "tool": "replace_file_content",
                "arguments": {"TargetFile": "app.py", "StartLine": 1, "EndLine": 2},
            },
        ]
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        transcript_path = os.path.join(temp_dir, "path_transcript.json")
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f)

        report = analyzer.parse_transcript(transcript_path)
        assert len(report.events) == 1
        event = report.events[0]
        # Paths resolve correctly to absolute, matching the subsequent edit.
        assert "run" in event.inspected_symbols


def test_nested_symbol_no_double_counting():
    """Verify that overlapping nested symbols do not double-count tokens."""
    analyzer = OfflineAnalyzer()
    transcript_data = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "app.py"},
                "output": """
   1: class MyClass:
   2:     def my_method(self):
   3:         print("method line 1")
   4:         print("method line 2")
""",
                "thinking": "I need to inspect MyClass and my_method.",
            },
            {
                "tool": "replace_file_content",
                "arguments": {"TargetFile": "app.py", "StartLine": 2, "EndLine": 4},
            },
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        transcript_path = os.path.join(temp_dir, "nested_transcript.json")
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f)
        report = analyzer.parse_transcript(transcript_path)
        assert len(report.events) == 1
        event = report.events[0]

        # Inspected symbols should include MyClass and MyClass.my_method
        assert "MyClass" in event.inspected_symbols
        assert "MyClass.my_method" in event.inspected_symbols

        # Cost B should be skeleton_cost + MyClass_cost (no double counting of my_method)
        clean_code = 'class MyClass:\n    def my_method(self):\n        print("method line 1")\n        print("method line 2")'
        skeleton_code = analyzer.generate_ast_skeleton(clean_code)
        skeleton_cost = analyzer.count_tokens(skeleton_code)
        class_cost = analyzer.count_tokens(clean_code)

        expected_cost = min(skeleton_cost + class_cost, class_cost)
        assert event.scenario_b_tokens == expected_cost


def test_case_insensitive_python_extension():
    """Verify that uppercase .PY extension is correctly recognized as Python."""
    analyzer = OfflineAnalyzer()
    transcript_data = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "APP.PY"},
                "output": "   1: def run():\n   2:     print('hello')",
            }
        ]
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        transcript_path = os.path.join(temp_dir, "uppercase_transcript.json")
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f)
        report = analyzer.parse_transcript(transcript_path)
        assert len(report.events) == 1
        event = report.events[0]
        assert event.is_python is True
