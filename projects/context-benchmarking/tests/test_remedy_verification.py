import os
import json
import tempfile
import pytest
from unittest.mock import patch
from context_benchmarking.analyzer import OfflineAnalyzer


def test_spacing_variations_reconstruction():
    """Verify that reconstruct_file_from_view_output handles spacing variations (no space, tab, spaces)."""
    analyzer = OfflineAnalyzer()

    # Case 1: No space after colon
    output_no_space = "   1:import os\n   2:def test():\n   3:pass"
    reconstructed = analyzer.reconstruct_file_from_view_output(output_no_space)
    assert reconstructed == "import os\ndef test():\npass"

    # Case 2: Tab after colon
    output_tab = "   1:\timport os\n   2:\tdef test():\n   3:\t\tpass"
    reconstructed = analyzer.reconstruct_file_from_view_output(output_tab)
    # The tab is part of group 2 if it's not a space
    assert reconstructed == "\timport os\n\tdef test():\n\t\tpass"

    # Case 3: Space after colon
    output_space = "   1: import os\n   2: def test():\n   3:     pass"
    reconstructed = analyzer.reconstruct_file_from_view_output(output_space)
    assert reconstructed == "import os\ndef test():\n    pass"


def test_path_comparisons():
    """Verify path comparisons between absolute and relative path formats."""
    analyzer = OfflineAnalyzer(repo_path="/workspace/myrepo")

    # Absolute vs relative
    assert analyzer._paths_match("/workspace/myrepo/src/app.py", "src/app.py")
    assert analyzer._paths_match("src/app.py", "/workspace/myrepo/src/app.py")

    # Relative path suffix checks
    assert analyzer._paths_match("/workspace/myrepo/src/app.py", "app.py")
    assert analyzer._paths_match("app.py", "/workspace/myrepo/src/app.py")

    # Non-matching paths
    assert not analyzer._paths_match("/workspace/myrepo/src/app.py", "src/utils.py")


def test_symbol_collisions():
    """Verify symbol name collisions between class methods and global functions."""
    analyzer = OfflineAnalyzer()
    code = """
def run():
    print("global run")

class Runner:
    def run(self):
        print("class method run")
"""
    symbols = analyzer.extract_symbols(code)
    # Extracting symbols should give both, with distinct qnames
    qnames = [s["qname"] for s in symbols]
    assert "run" in qnames
    assert "Runner.run" in qnames

    # Retrieve runner block specifically
    runner_run_block = analyzer.get_symbol_block(code, "Runner.run")
    assert "class method run" in runner_run_block
    assert "global run" not in runner_run_block

    # Retrieve global block
    global_run_block = analyzer.get_symbol_block(code, "run")
    assert "global run" in global_run_block
    assert "class method run" not in global_run_block


def test_token_double_counting_prevention():
    """Verify double-counting prevention for overlapping/nested symbols."""
    analyzer = OfflineAnalyzer()
    code = 'class Container:\n    def process(self):\n        print("inner logic")'
    # Create transcript where both Container and Container.process are inspected
    # because they both lie in the edited line range.
    transcript_data = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "app.py"},
                "output": '   1: class Container:\n   2:     def process(self):\n   3:         print("inner logic")',
            },
            {
                "tool": "replace_file_content",
                "arguments": {"TargetFile": "app.py", "StartLine": 2, "EndLine": 3},
            },
        ]
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        t_path = os.path.join(temp_dir, "transcript.json")
        with open(t_path, "w") as f:
            json.dump(transcript_data, f)

        report = analyzer.parse_transcript(t_path)
        event = report.events[0]

        # Verify both symbols detected
        assert "Container" in event.inspected_symbols
        # Note: Container.process isn't in inspected_symbols directly unless we search for it.
        # But wait, does raw_inspected_symbols add both name and qname?
        # Let's check: Container (name: Container, qname: Container), process (name: process, qname: Container.process)
        # Yes, since process falls within the range, Container.process is added to raw_inspected_symbols.

        # Let's calculate manual skeleton + Container cost
        skeleton_code = analyzer.generate_ast_skeleton(code, "app.py")
        skeleton_cost = analyzer.count_tokens(skeleton_code)

        # Container class spans lines 1 to 3, process spans lines 2 to 3.
        # Merged range should just be lines 1 to 3 (the whole file).
        expected_scenario_b = skeleton_cost + analyzer.count_tokens(code)
        # Cap at scenario_a (which is count_tokens(code))
        expected_scenario_b = min(expected_scenario_b, analyzer.count_tokens(code))

        assert event.scenario_b_tokens == expected_scenario_b


def test_non_python_skeleton_cost():
    """Verify JS/TS/JSON/MD skeleton Scenario B cost calculations."""
    analyzer = OfflineAnalyzer()

    # 1. JS/TS
    js_code = "class A {}\nfunction b() {}\nconst c = 123;"
    js_skeleton = analyzer.generate_ast_skeleton(js_code, "app.js")
    assert "class A" in js_skeleton
    assert "function b" in js_skeleton
    assert "const c" not in js_skeleton

    # 2. JSON
    json_code = '{"a": 1, "b": [2, 3]}'
    json_skeleton = analyzer.generate_ast_skeleton(json_code, "config.json")
    loaded = json.loads(json_skeleton)
    assert loaded["a"] == "..."
    assert loaded["b"] == ["...", "..."]

    # 3. MD
    md_code = "# Heading\ntext\n## Subheading\ntext"
    md_skeleton = analyzer.generate_ast_skeleton(md_code, "readme.md")
    assert "# Heading" in md_skeleton
    assert "## Subheading" in md_skeleton
    assert "text" not in md_skeleton


def test_upper_case_extensions():
    """Verify that upper-case Python file extensions (.PY) are handled as Python files."""
    analyzer = OfflineAnalyzer()
    code = "def foo():\n    pass"

    transcript_data = {
        "steps": [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "main.PY"},
                "output": "   1: def foo():\n   2:     pass",
            }
        ]
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        t_path = os.path.join(temp_dir, "transcript.json")
        with open(t_path, "w") as f:
            json.dump(transcript_data, f)

        report = analyzer.parse_transcript(t_path)
        event = report.events[0]
        assert event.is_python is True
        assert event.file_path == "main.PY"


@patch("context_benchmarking.simulator.genai.Client")
@patch("context_benchmarking.simulator.GitManager")
@patch("context_benchmarking.simulator.DatasetLoader")
def test_symlink_path_traversal(mock_loader_cls, mock_git_cls, mock_client_cls):
    """Verify that symlink path traversal to external files is blocked by simulator tools."""
    from unittest.mock import MagicMock, patch
    from context_benchmarking.simulator import CoderAgentSimulator

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock repository path inside the temp_dir
        repo_dir = os.path.join(temp_dir, "repo")
        os.makedirs(repo_dir)

        # Create a target file outside the mock repository path
        external_file = os.path.join(temp_dir, "secret.txt")
        with open(external_file, "w") as f:
            f.write("sensitive data")

        # Create a symlink inside the mock repository pointing to the external file
        symlink_path = os.path.join(repo_dir, "link_to_secret.txt")
        os.symlink(external_file, symlink_path)

        # Setup standard simulation mocks
        mock_git = MagicMock()
        mock_git.setup_branch.return_value = "branch"
        mock_git_cls.return_value = mock_git

        mock_task = MagicMock()
        mock_task.name = "T"
        mock_task.description = "D"
        mock_task.instructions = "I"
        mock_task.files_to_modify = ["link_to_secret.txt"]

        mock_loader = MagicMock()
        mock_loader.get_task.return_value = mock_task
        mock_loader_cls.return_value = mock_loader

        # Instantiate CoderAgentSimulator
        repo_path_real = os.path.realpath(repo_dir)
        simulator = CoderAgentSimulator(
            repo_path=repo_path_real, model_name="gemini-2.5-flash"
        )

        # Test Scenario A tools
        with patch.object(simulator.client.models, "generate_content") as mock_generate:

            def intercept_tools(*args, **kwargs):
                intercept_tools.tools = kwargs.get("config").tools
                raise RuntimeError("Stop simulation")

            mock_generate.side_effect = intercept_tools

            try:
                simulator.run_simulation(task_id="t1", scenario="A")
            except RuntimeError:
                pass

            tools_list = intercept_tools.tools
            tools_dict = {t.__name__: t for t in tools_list}

            # 1. view_file_tool
            view_tool = tools_dict["view_file_tool"]
            res = view_tool("link_to_secret.txt")
            assert "is outside repository boundaries." in res
            assert "ViewFile" in res

            # 2. write_to_file_tool
            write_tool = tools_dict["write_to_file_tool"]
            res = write_tool("link_to_secret.txt", "new content")
            assert "is outside repository boundaries." in res
            assert "WriteToFile" in res

            # 3. grep_search_tool
            grep_tool = tools_dict["grep_search_tool"]
            res = grep_tool("query", "link_to_secret.txt")
            assert "is outside repository boundaries." in res
            assert "GrepSearch" in res

            # 4. replace_file_content_tool
            replace_tool = tools_dict["replace_file_content_tool"]
            res = replace_tool("link_to_secret.txt", "target", "replacement", 1, 2)
            assert "is outside repository boundaries." in res
            assert "ReplaceFileContent" in res

        # Test Scenario B tools (view_ast_skeleton_tool, view_symbol_tool)
        with patch.object(
            simulator.client.models, "generate_content"
        ) as mock_generate_b:

            def intercept_tools_b(*args, **kwargs):
                intercept_tools_b.tools = kwargs.get("config").tools
                raise RuntimeError("Stop simulation")

            mock_generate_b.side_effect = intercept_tools_b

            try:
                simulator.run_simulation(task_id="t1", scenario="B")
            except RuntimeError:
                pass

            tools_list_b = intercept_tools_b.tools
            tools_dict_b = {t.__name__: t for t in tools_list_b}

            # 5. view_ast_skeleton_tool
            ast_tool = tools_dict_b["view_ast_skeleton_tool"]
            res = ast_tool("link_to_secret.txt")
            assert "is outside repository boundaries." in res
            assert "ViewASTSkeleton" in res

            # 6. view_symbol_tool
            symbol_tool = tools_dict_b["view_symbol_tool"]
            res = symbol_tool("symbol", "link_to_secret.txt")
            assert "is outside repository boundaries." in res
            assert "ViewSymbol" in res


@patch("context_benchmarking.simulator.genai.Client")
@patch("context_benchmarking.simulator.GitManager")
@patch("context_benchmarking.simulator.DatasetLoader")
def test_symlink_path_traversal_adversarial(
    mock_loader_cls, mock_git_cls, mock_client_cls
):
    """Verify that complex adversarial symlinks (nested, absolute, circular, directory symlinks) are blocked."""
    from unittest.mock import MagicMock, patch
    from context_benchmarking.simulator import CoderAgentSimulator

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock repository path inside the temp_dir
        repo_dir = os.path.join(temp_dir, "repo")
        os.makedirs(repo_dir)

        # Create a target file outside the mock repository path
        external_file = os.path.join(temp_dir, "secret.txt")
        with open(external_file, "w") as f:
            f.write("sensitive data")

        # 1. Nested symlink: link_a -> link_b -> external_file
        link_b = os.path.join(repo_dir, "link_b")
        os.symlink(external_file, link_b)
        link_a = os.path.join(repo_dir, "link_a")
        os.symlink(link_b, link_a)

        # 2. Absolute path symlink
        link_abs = os.path.join(repo_dir, "link_abs")
        os.symlink(external_file, link_abs)

        # 3. Directory symlink: link_dir -> external directory containing a file
        external_dir = os.path.join(temp_dir, "ext_dir")
        os.makedirs(external_dir)
        ext_file_in_dir = os.path.join(external_dir, "confidential.txt")
        with open(ext_file_in_dir, "w") as f:
            f.write("secret in dir")
        link_dir = os.path.join(repo_dir, "link_dir")
        os.symlink(external_dir, link_dir)

        # 4. Relative path symlink with '..' prefix: link_rel -> ../secret.txt
        link_rel = os.path.join(repo_dir, "link_rel")
        os.symlink("../secret.txt", link_rel)

        # 5. Circular symlinks: circle_1 -> circle_2 -> circle_1
        circle_1 = os.path.join(repo_dir, "circle_1")
        circle_2 = os.path.join(repo_dir, "circle_2")
        os.symlink(circle_2, circle_1)
        os.symlink(circle_1, circle_2)

        # Setup standard simulation mocks
        mock_git = MagicMock()
        mock_git.setup_branch.return_value = "branch"
        mock_git_cls.return_value = mock_git

        mock_task = MagicMock()
        mock_task.name = "T"
        mock_task.description = "D"
        mock_task.instructions = "I"
        mock_task.files_to_modify = []

        mock_loader = MagicMock()
        mock_loader.get_task.return_value = mock_task
        mock_loader_cls.return_value = mock_loader

        # Instantiate CoderAgentSimulator
        repo_path_real = os.path.realpath(repo_dir)
        simulator = CoderAgentSimulator(
            repo_path=repo_path_real, model_name="gemini-2.5-flash"
        )

        # Test Scenario A tools
        with patch.object(simulator.client.models, "generate_content") as mock_generate:

            def intercept_tools(*args, **kwargs):
                intercept_tools.tools = kwargs.get("config").tools
                raise RuntimeError("Stop simulation")

            mock_generate.side_effect = intercept_tools

            try:
                simulator.run_simulation(task_id="t1", scenario="A")
            except RuntimeError:
                pass

            tools_list = intercept_tools.tools
            tools_dict = {t.__name__: t for t in tools_list}
            view_tool = tools_dict["view_file_tool"]
            write_tool = tools_dict["write_to_file_tool"]
            grep_tool = tools_dict["grep_search_tool"]
            replace_tool = tools_dict["replace_file_content_tool"]

            # Test Nested Symlink
            res = view_tool("link_a")
            assert "is outside repository boundaries." in res

            # Test Absolute Symlink
            res = view_tool("link_abs")
            assert "is outside repository boundaries." in res

            # Test Directory Symlink file access
            res = view_tool("link_dir/confidential.txt")
            assert "is outside repository boundaries." in res

            # Test Relative dotdot Symlink
            res = view_tool("link_rel")
            assert "is outside repository boundaries." in res

            # Test Circular symlinks (safe failure check)
            try:
                res = view_tool("circle_1")
                # If the traversal check let it pass, opening it must raise or return error
                if "is outside repository boundaries." not in res:
                    assert (
                        "Error" in res or "FileNotFoundError" in res or "OSError" in res
                    )
            except (OSError, FileNotFoundError, ValueError):
                pass
