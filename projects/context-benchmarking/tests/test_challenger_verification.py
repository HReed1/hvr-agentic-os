import os
import sys
import json
import tempfile
import ast
import pytest
from unittest.mock import MagicMock, patch
from google.genai import types

# Import the code to test
from context_benchmarking.analyzer import OfflineAnalyzer
from context_benchmarking.simulator import CoderAgentSimulator


def get_tools_for_scenario(scenario="B", repo_path="."):
    """Helper to extract the actual tool functions defined inside CoderAgentSimulator."""
    with (
        patch("context_benchmarking.simulator.GitManager"),
        patch("context_benchmarking.simulator.DatasetLoader") as mock_loader_class,
    ):

        mock_task = MagicMock()
        mock_task.name = "Test Task"
        mock_task.description = "Task Description"
        mock_task.instructions = "Task Instructions"
        mock_task.files_to_modify = ["inside.txt"]

        mock_loader = MagicMock()
        mock_loader.get_task.return_value = mock_task
        mock_loader_class.return_value = mock_loader

        with patch("context_benchmarking.simulator.genai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            captured_tools = {}

            def mock_generate_content(*args, **kwargs):
                config = kwargs.get("config")
                if config and config.tools:
                    for t in config.tools:
                        captured_tools[t.__name__] = t
                raise ValueError("Stop simulation")

            mock_client.models.generate_content.side_effect = mock_generate_content

            simulator = CoderAgentSimulator(
                repo_path=repo_path, model_name="gemini-2.5-flash"
            )

            try:
                simulator.run_simulation(task_id="t1", scenario=scenario, max_steps=1)
            except ValueError:
                pass

            return captured_tools


# =====================================================================
# 1. PATH TRAVERSAL CHECK STRESS-TESTS
# =====================================================================


def test_path_traversal_bypasses():
    """Verify that path traversal checks in simulator tools block standard bypasses, but check for symlink vulnerability."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create directory structure:
        # temp_dir/
        #   repo/           <-- CoderAgentSimulator repo_path
        #     inside.txt
        #   sibling/
        #     sibling.txt
        #   outside.txt

        repo_dir = os.path.join(temp_dir, "repo")
        sibling_dir = os.path.join(temp_dir, "sibling")
        os.makedirs(repo_dir, exist_ok=True)
        os.makedirs(sibling_dir, exist_ok=True)

        inside_file = os.path.join(repo_dir, "inside.txt")
        sibling_file = os.path.join(sibling_dir, "sibling.txt")
        outside_file = os.path.join(temp_dir, "outside.txt")

        with open(inside_file, "w") as f:
            f.write("inside content")
        with open(sibling_file, "w") as f:
            f.write("sibling content")
        with open(outside_file, "w") as f:
            f.write("outside content")

        # Create a symlink inside repo pointing to outside_file
        symlink_path = os.path.join(repo_dir, "symlink_to_outside.txt")
        try:
            os.symlink(outside_file, symlink_path)
            has_symlink_support = True
        except (OSError, NotImplementedError):
            has_symlink_support = False

        # Extract actual tool functions bound to repo_dir
        tools = get_tools_for_scenario("B", repo_path=repo_dir)

        # Tools: grep_search_tool, view_ast_skeleton_tool, view_symbol_tool, write_to_file_tool, replace_file_content_tool
        view_file_tool = get_tools_for_scenario("A", repo_path=repo_dir)[
            "view_file_tool"
        ]
        grep_search_tool = tools["grep_search_tool"]
        write_to_file_tool = tools["write_to_file_tool"]
        replace_file_content_tool = tools["replace_file_content_tool"]
        view_ast_skeleton_tool = tools["view_ast_skeleton_tool"]
        view_symbol_tool = tools["view_symbol_tool"]

        # Define bypass targets
        absolute_bypass = outside_file
        dot_dot_bypass = "../outside.txt"
        dot_dot_nested_bypass = "./../outside.txt"
        sibling_bypass = "../sibling/sibling.txt"
        weird_slashes_bypass = "..//outside.txt"

        # A. Verify standard bypasses are BLOCKED (return Error: ... is outside repository boundaries)
        for tool_name, tool_fn in [
            ("view_file_tool", view_file_tool),
            ("grep_search_tool", lambda path: grep_search_tool(query="foo", path=path)),
            (
                "write_to_file_tool",
                lambda path: write_to_file_tool(path=path, content="hacked"),
            ),
            (
                "replace_file_content_tool",
                lambda path: replace_file_content_tool(
                    path=path,
                    target="inside",
                    replacement="hacked",
                    StartLine=1,
                    EndLine=1,
                ),
            ),
            ("view_ast_skeleton_tool", view_ast_skeleton_tool),
            (
                "view_symbol_tool",
                lambda path: view_symbol_tool(symbol="foo", path=path),
            ),
        ]:
            for bypass_path in [
                absolute_bypass,
                dot_dot_bypass,
                dot_dot_nested_bypass,
                sibling_bypass,
                weird_slashes_bypass,
            ]:
                res = tool_fn(bypass_path)
                assert (
                    "is outside repository boundaries" in res
                ), f"{tool_name} allowed bypass with path: {bypass_path}. Result: {res}"

        # B. Verify symlink vulnerability (if symlinks are supported by OS)
        if has_symlink_support:
            # View File tool via symlink
            res_view = view_file_tool("symlink_to_outside.txt")
            # After remedy, symlink traversal is blocked
            assert "is outside repository boundaries." in res_view

            # Write to File tool via symlink
            res_write = write_to_file_tool(
                path="symlink_to_outside.txt", content="hacked outside via symlink"
            )
            assert "is outside repository boundaries." in res_write

            # Replace File Content tool via symlink
            res_replace = replace_file_content_tool(
                path="symlink_to_outside.txt",
                target="hacked outside",
                replacement="replaced outside",
                StartLine=1,
                EndLine=1,
            )
            assert "is outside repository boundaries." in res_replace


# =====================================================================
# 2. RECONSTRUCT_FILE_FROM_VIEW_OUTPUT EDGE CASES
# =====================================================================


def test_reconstruct_file_from_view_output_edge_cases():
    """Verify that reconstruct_file_from_view_output falls back to raw code blocks on non-sequential or low density."""
    analyzer = OfflineAnalyzer()

    # Case 1: Decreasing line numbers
    decreasing_output = "   3: def foo():\n   2:     pass\n   1: # end"
    res = analyzer.reconstruct_file_from_view_output(decreasing_output)
    assert (
        res == decreasing_output
    ), "Should have fallen back to raw code due to decreasing sequence"

    # Case 2: Non-sequential line numbers (large gaps)
    gaps_output = "  10: def foo():\n  20:     pass\n  30:     return"
    res = analyzer.reconstruct_file_from_view_output(gaps_output)
    assert (
        res == gaps_output
    ), "Should have fallen back to raw code due to non-sequential steps (gap of 10)"

    # Case 3: Low density (less than 70% matching lines)
    # 4 lines total, only 2 match regex -> density = 2/4 = 50%
    low_density_output = "   1: def foo():\nthis is a random unnumbered line\n   2:     pass\nanother unnumbered line"
    res = analyzer.reconstruct_file_from_view_output(low_density_output)
    assert (
        res == low_density_output
    ), "Should have fallen back to raw code due to low line-number density"

    # Case 4: Duplicate line numbers
    duplicate_output = "   1: def foo():\n   1: def foo():"
    res = analyzer.reconstruct_file_from_view_output(duplicate_output)
    assert (
        res == duplicate_output
    ), "Should have fallen back to raw code due to duplicate line numbers"


# =====================================================================
# 3. AST SKELETON ON NESTED CLASSES AND ATTRIBUTES
# =====================================================================


def test_ast_skeleton_nested_classes_and_attributes():
    """Verify how python AST skeleton generator handles nested classes and attributes."""
    analyzer = OfflineAnalyzer()

    code = """
class Outer:
    \"\"\"Outer class docstring.\"\"\"
    outer_class_attr = "hello"
    annotated_attr: int = 123
    
    class Inner:
        \"\"\"Inner class docstring.\"\"\"
        inner_class_attr = 456
        
        def inner_method(self):
            \"\"\"Inner method docstring.\"\"\"
            self.x = 10
            return self.x
            
    def outer_method(self):
        \"\"\"Outer method docstring.\"\"\"
        pass
"""
    skeleton = analyzer.generate_ast_skeleton(code, file_path="module.py")

    # Verify nesting structure is preserved
    assert "class Outer:" in skeleton
    assert "class Inner:" in skeleton
    assert "def inner_method" in skeleton
    assert "def outer_method" in skeleton

    # Verify docstrings are preserved
    assert "Outer class docstring." in skeleton
    assert "Inner class docstring." in skeleton
    assert "Inner method docstring." in skeleton
    assert "Outer method docstring." in skeleton

    # Verify class attributes and instance attributes are STRIPPED
    # Class attributes
    assert "outer_class_attr" not in skeleton
    assert "inner_class_attr" not in skeleton
    assert "annotated_attr" not in skeleton

    # Instance attributes inside methods
    assert "self.x" not in skeleton

    # Verify that class body with only stripped attributes/no children gets 'pass'
    empty_class_code = """
class EmptyClass:
    class_attr = 123
"""
    empty_skeleton = analyzer.generate_ast_skeleton(
        empty_class_code, file_path="module.py"
    )
    assert "class EmptyClass:" in empty_skeleton
    assert "pass" in empty_skeleton
