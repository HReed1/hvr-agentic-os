import os
import json
import tempfile
import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from context_benchmarking.dataset import (
    DatasetLoader,
    TaskDefinition,
    TaskValidationError,
    DatasetError,
)
from context_benchmarking.tools import (
    write_to_file,
    replace_file_content,
    view_file,
    query_codebase_graph,
)
from context_benchmarking.simulator import CoderAgentSimulator
from context_benchmarking.reporter import RunMetrics, TaskResultEnvelope
from context_benchmarking.analyzer import OfflineAnalyzer

# =====================================================================
# 1. Invalid JSON or schemas in tasks.json
# =====================================================================


def test_tasks_json_edge_cases():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Case 1.1: Syntax error in JSON
        bad_json_path = os.path.join(temp_dir, "bad_syntax.json")
        with open(bad_json_path, "w") as f:
            f.write("{invalid_json: true")
        with pytest.raises(DatasetError) as exc:
            DatasetLoader(tasks_file_path=bad_json_path)
        assert "Invalid JSON syntax" in str(exc.value)

        # Case 1.2: Root not object (list instead)
        bad_root_path = os.path.join(temp_dir, "bad_root.json")
        with open(bad_root_path, "w") as f:
            json.dump([{"task_id": "t1"}], f)
        with pytest.raises(TaskValidationError) as exc:
            DatasetLoader(tasks_file_path=bad_root_path)
        assert "must be a JSON object" in str(exc.value)

        # Case 1.3: Root missing 'tasks' key
        missing_tasks_path = os.path.join(temp_dir, "missing_tasks.json")
        with open(missing_tasks_path, "w") as f:
            json.dump({"not_tasks": []}, f)
        with pytest.raises(TaskValidationError) as exc:
            DatasetLoader(tasks_file_path=missing_tasks_path)
        assert "must contain a 'tasks' key" in str(exc.value)

        # Case 1.4: 'tasks' is not a list
        tasks_not_list_path = os.path.join(temp_dir, "tasks_not_list.json")
        with open(tasks_not_list_path, "w") as f:
            json.dump({"tasks": "not a list"}, f)
        with pytest.raises(TaskValidationError) as exc:
            DatasetLoader(tasks_file_path=tasks_not_list_path)
        assert "must be a JSON array" in str(exc.value)

        # Case 1.5: Duplicate task_id
        dup_task_path = os.path.join(temp_dir, "duplicate_task.json")
        dup_data = {
            "tasks": [
                {
                    "task_id": "dup",
                    "name": "A",
                    "size": "S",
                    "difficulty": "E",
                    "description": "D",
                    "branch_name": "B1",
                    "instructions": "I",
                },
                {
                    "task_id": "dup",
                    "name": "B",
                    "size": "S",
                    "difficulty": "E",
                    "description": "D",
                    "branch_name": "B2",
                    "instructions": "I",
                },
            ]
        }
        with open(dup_task_path, "w") as f:
            json.dump(dup_data, f)
        with pytest.raises(TaskValidationError) as exc:
            DatasetLoader(tasks_file_path=dup_task_path)
        assert "Duplicate task_id" in str(exc.value)

        # Case 1.6: Task element not a JSON object
        elem_not_obj_path = os.path.join(temp_dir, "elem_not_obj.json")
        with open(elem_not_obj_path, "w") as f:
            json.dump({"tasks": ["not_an_object"]}, f)
        with pytest.raises(TaskValidationError) as exc:
            DatasetLoader(tasks_file_path=elem_not_obj_path)
        assert "is not a valid JSON object" in str(exc.value)

        # Case 1.7: Missing required field in task schema (e.g. branch_name)
        missing_field_path = os.path.join(temp_dir, "missing_field.json")
        missing_field_data = {
            "tasks": [
                {
                    "task_id": "t1",
                    "name": "A",
                    "size": "S",
                    "difficulty": "E",
                    "description": "D",
                    "instructions": "I",
                    # missing branch_name
                }
            ]
        }
        with open(missing_field_path, "w") as f:
            json.dump(missing_field_data, f)
        with pytest.raises(TaskValidationError) as exc:
            DatasetLoader(tasks_file_path=missing_field_path)
        assert "Validation failed for task" in str(exc.value)

        # Case 1.8: Wrong types in fields (e.g. files_to_modify is string instead of list)
        wrong_type_path = os.path.join(temp_dir, "wrong_type.json")
        wrong_type_data = {
            "tasks": [
                {
                    "task_id": "t1",
                    "name": "A",
                    "size": "S",
                    "difficulty": "E",
                    "description": "D",
                    "branch_name": "B",
                    "instructions": "I",
                    "files_to_modify": "should_be_list",
                }
            ]
        }
        with open(wrong_type_path, "w") as f:
            json.dump(wrong_type_data, f)
        with pytest.raises(TaskValidationError) as exc:
            DatasetLoader(tasks_file_path=wrong_type_path)
        assert "Validation failed for task" in str(exc.value)


# =====================================================================
# 2. File path traversal bounds in write_to_file and replace_file_content
# =====================================================================


@patch("context_benchmarking.simulator.genai.Client")
@patch("context_benchmarking.simulator.GitManager")
@patch("context_benchmarking.simulator.DatasetLoader")
def test_path_traversal_tool_bounds(mock_loader_cls, mock_git_cls, mock_client_cls):
    # Setup standard simulation mocks so we can instantiate the CoderAgentSimulator
    # and inspect the local tool functions defined within run_simulation
    mock_git = MagicMock()
    mock_git.setup_branch.return_value = "branch"
    mock_git_cls.return_value = mock_git

    mock_task = MagicMock()
    mock_task.name = "T"
    mock_task.description = "D"
    mock_task.instructions = "I"
    mock_task.files_to_modify = ["f.py"]

    mock_loader = MagicMock()
    mock_loader.get_task.return_value = mock_task
    mock_loader_cls.return_value = mock_loader

    # Let's run a fake simulation to extract the bound tools
    simulator = CoderAgentSimulator(repo_path="/foo/bar", model_name="gemini-2.5-flash")

    # To inspect the local tools, we mock client.models.generate_content to raise an error immediately
    # so we can intercept the local tools passed to it
    with patch.object(simulator.client.models, "generate_content") as mock_generate:

        def intercept_tools(*args, **kwargs):
            # Save the tools for testing
            intercept_tools.tools = kwargs.get("config").tools
            raise RuntimeError("Stop simulation")

        mock_generate.side_effect = intercept_tools

        try:
            simulator.run_simulation(task_id="t1", scenario="A")
        except RuntimeError:
            pass

        # Recover tools
        tools_list = intercept_tools.tools
        tools_dict = {t.__name__: t for t in tools_list}

        write_tool = tools_dict["write_to_file_tool"]
        replace_tool = tools_dict["replace_file_content_tool"]

        # Mock write_to_file and replace_file_content to prevent OS errors
        with (
            patch(
                "context_benchmarking.tools.write_to_file", return_value="mocked write"
            ) as mock_write_fn,
            patch(
                "context_benchmarking.tools.replace_file_content",
                return_value="mocked replace",
            ) as mock_replace_fn,
        ):

            # Case 2.1: Write to file outside repository (using traversal in relative path)
            # Sibling directory starting with same prefix: /foo/bar_sibling/file.py
            # Since repo_path is /foo/bar, does it allow /foo/bar_sibling/file.py?
            # Target path: ../bar_sibling/file.py.
            # os.path.abspath(os.path.join(self.repo_path, "../bar_sibling/file.py")) resolves to /foo/bar_sibling/file.py
            # Does /foo/bar_sibling/file.py start with /foo/bar?
            # Yes! "/foo/bar_sibling/file.py".startswith("/foo/bar") is True!
            # Verify that this is blocked.
            res = write_tool("../bar_sibling/file.py", "content")
            assert "is outside repository boundaries." in res
            mock_write_fn.assert_not_called()

            # Case 2.2: Write to file completely outside repo path, e.g. /etc/passwd
            # target path: /etc/passwd
            # os.path.abspath(os.path.join(self.repo_path, "/etc/passwd")) resolves to /etc/passwd
            # "/etc/passwd".startswith("/foo/bar") is False.
            # Should be blocked!
            res_blocked = write_tool("/etc/passwd", "content")
            assert "is outside repository boundaries." in res_blocked

            # Case 2.3: replace_file_content traversal in relative path
            res_replace = replace_tool(
                "../bar_sibling/file.py", "target", "replacement", 1, 2
            )
            assert "is outside repository boundaries." in res_replace
            mock_replace_fn.assert_not_called()

            # Case 2.4: replace_file_content completely outside repo path
            res_replace_blocked = replace_tool(
                "/etc/passwd", "target", "replacement", 1, 2
            )
            assert "is outside repository boundaries." in res_replace_blocked

        # Case 2.5: Let's check view_file_tool. Does it have any bounds checks at all?
        # view_file_tool is defined in run_simulation
        view_tool = tools_dict["view_file_tool"]
        # It must check for repo bounds!
        with patch("context_benchmarking.tools.view_file") as mock_view_file:
            res_view_blocked = view_tool("/etc/passwd")
            assert "is outside repository boundaries." in res_view_blocked
            mock_view_file.assert_not_called()


# =====================================================================
# 3. Class method symbol extraction and duplicate name queries in codebases
# =====================================================================


def test_duplicate_symbol_extraction_and_graph_queries():
    code = """
def run():
    print("global run")

class Runner:
    def run(self):
        print("Runner class method run")

class AnotherRunner:
    def run(self):
        print("AnotherRunner class method run")
"""
    analyzer = OfflineAnalyzer()
    symbols = analyzer.extract_symbols(code)

    # 3.1 Verify extraction identifies all three run symbols with distinct qualified names
    assert (
        len(symbols) == 5
    )  # run, Runner, Runner.run, AnotherRunner, AnotherRunner.run
    # Wait, the global def run is also there!
    # Let's check all symbols:
    # 1. run (function)
    # 2. Runner (class)
    # 3. Runner.run (function/method)
    # 4. AnotherRunner (class)
    # 5. AnotherRunner.run (function/method)
    # Wait, let's see. Let's list their qnames:
    qnames = {s["qname"]: s for s in symbols}
    assert "run" in qnames
    assert "Runner" in qnames
    assert "Runner.run" in qnames
    assert "AnotherRunner" in qnames
    assert "AnotherRunner.run" in qnames

    # 3.2 Query codebase graph for "run" should return all definitions
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "app.py")
        with open(file_path, "w") as f:
            f.write(code)

        res = query_codebase_graph("run", repo_path=temp_dir)
        # Should contain definitions for global run, Runner.run, and AnotherRunner.run
        assert "app.py:2 (function definition: run)" in res
        assert "app.py:6 (method definition: Runner.run)" in res
        assert "app.py:10 (method definition: AnotherRunner.run)" in res

        # 3.3 Query codebase graph for qualified name "Runner.run"
        res_q = query_codebase_graph("Runner.run", repo_path=temp_dir)
        assert "app.py:6 (method definition: Runner.run)" in res_q
        assert "Runner.run" in res_q
        assert "AnotherRunner.run" not in res_q
        assert "app.py:2" not in res_q


# =====================================================================
# 4. Duplicate key writing in step logs for full OfflineAnalyzer compatibility
# =====================================================================


@patch("context_benchmarking.simulator.GitManager")
@patch("context_benchmarking.simulator.DatasetLoader")
def test_step_log_duplicate_keys(mock_loader_cls, mock_git_cls):
    mock_git = MagicMock()
    mock_git_cls.return_value = mock_git
    mock_loader_cls.return_value = MagicMock()

    with patch("context_benchmarking.simulator.genai.Client") as mock_client_cls:
        simulator = CoderAgentSimulator(repo_path=".", model_name="gemini-2.5-flash")

        # Call private method to write step
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "transcript.jsonl")

            simulator._write_transcript_step(
                transcript_path=log_path,
                step_index=42,
                tool_name="view_file",
                args={"AbsolutePath": "app.py"},
                output="file content",
                thinking="I am thinking",
            )

            with open(log_path, "r") as f:
                line = f.readline()
                entry = json.loads(line)

            # Verify all duplicated keys exist
            assert entry["step_index"] == 42
            # Tool Name Keys
            assert entry["tool"] == "view_file"
            assert entry["name"] == "view_file"
            assert entry["action"] == "view_file"
            # Arguments Keys
            assert entry["arguments"] == {"AbsolutePath": "app.py"}
            assert entry["args"] == {"AbsolutePath": "app.py"}
            assert entry["parameters"] == {"AbsolutePath": "app.py"}
            # Output Keys
            assert entry["output"] == "file content"
            assert entry["content"] == "file content"
            assert entry["result"] == "file content"
            assert entry["response"] == "file content"
            # Thinking Keys
            assert entry["thinking"] == "I am thinking"
            assert entry["thought"] == "I am thinking"
            assert entry["rationale"] == "I am thinking"


# =====================================================================
# 5. Pydantic V2 compatibility in RunMetrics and TaskResultEnvelope serialization
# =====================================================================


def test_pydantic_v2_compatibility():
    metrics = RunMetrics(
        task_id="t1",
        scenario="A",
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        latency_seconds=2.5,
        tool_call_count=4,
        exit_code=0,
        tests_passed=True,
    )

    # 5.1 Test model_dump_json (Pydantic V2 method)
    json_str = metrics.model_dump_json()
    parsed = json.loads(json_str)
    assert parsed["task_id"] == "t1"
    assert parsed["scenario"] == "A"
    assert parsed["total_tokens"] == 150
    assert parsed["tests_passed"] is True

    # 5.2 Test initialization and nested validation
    envelope = TaskResultEnvelope(task_id="t1", scenario_a=metrics, scenario_b=metrics)
    assert envelope.is_complete is True
    assert envelope.token_savings == 0
    assert envelope.token_savings_pct == 0.0

    # 5.3 Test model_dump (Pydantic V2 method)
    dump_dict = envelope.model_dump()
    assert dump_dict["task_id"] == "t1"
    assert dump_dict["scenario_a"]["input_tokens"] == 100


# =====================================================================
# 6. Mocking of google-genai Client and GitManager
# =====================================================================


@patch("context_benchmarking.simulator.GitManager")
@patch("context_benchmarking.simulator.DatasetLoader")
def test_mocking_infrastructure(mock_loader_cls, mock_git_cls):
    mock_git = MagicMock()
    mock_git.setup_branch.return_value = "task/test-branch"
    mock_git.run_tests.return_value = {"exit_code": 0, "stdout": "Passed", "stderr": ""}
    mock_git_cls.return_value = mock_git

    mock_task = MagicMock()
    mock_task.name = "T"
    mock_task.description = "D"
    mock_task.instructions = "I"
    mock_task.files_to_modify = ["f.py"]

    mock_loader = MagicMock()
    mock_loader.get_task.return_value = mock_task
    mock_loader_cls.return_value = mock_loader

    with patch("context_benchmarking.simulator.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        # Configure response structure for the Gemini API call
        mock_part = MagicMock()
        mock_part.text = "Solving the task directly."
        mock_part.thought = True
        mock_part.function_call = None

        mock_response = MagicMock()
        mock_response.candidates = [MagicMock(content=MagicMock(parts=[mock_part]))]
        mock_response.usage_metadata.prompt_token_count = 50
        mock_response.usage_metadata.candidates_token_count = 25

        mock_client.models.generate_content.return_value = mock_response

        simulator = CoderAgentSimulator(repo_path=".", model_name="gemini-2.5-flash")

        with tempfile.TemporaryDirectory() as temp_dir:
            transcript_path = os.path.join(temp_dir, "transcript.jsonl")

            metrics = simulator.run_simulation(
                task_id="t1", scenario="A", transcript_path=transcript_path, max_steps=2
            )

            # Verify GitManager setup, run_tests, and cleanup were called
            mock_git.setup_branch.assert_called_once_with("t1")
            mock_git.run_tests.assert_called_once_with("t1")
            mock_git.cleanup.assert_called_once()

            # Verify API client generate_content was called
            mock_client.models.generate_content.assert_called_once()

            # Verify results
            assert metrics["success"] is True
            assert metrics["test_exit_code"] == 0
            assert metrics["steps_executed"] == 1
