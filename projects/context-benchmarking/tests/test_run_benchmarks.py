import os
import json
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from context_benchmarking.run_benchmarks import main, run_task_scenario
from context_benchmarking.dataset import TaskDefinition


@pytest.fixture
def mock_task():
    return TaskDefinition(
        task_id="test_task",
        name="Test Task",
        size="small",
        difficulty="easy",
        description="A test task description",
        branch_name="task/test-branch",
        files_to_modify=["app.py"],
        test_commands=["pytest test_app.py"],
        instructions="Modify app.py to pass tests.",
    )


@patch("context_benchmarking.run_benchmarks.CoderAgentSimulator")
def test_run_task_scenario_success(mock_sim_class, mock_task):
    # Setup simulator mock
    mock_sim = MagicMock()
    mock_sim.run_simulation.return_value = {
        "success": True,
        "input_tokens": 100,
        "output_tokens": 50,
        "latency": 2.5,
        "total_tool_calls": 3,
        "test_exit_code": 0,
        "test_output": "Passed",
    }
    mock_sim_class.return_value = mock_sim

    # Mock Reporter and Analyzer
    mock_reporter = MagicMock()
    mock_analyzer = MagicMock()

    # Configure mock analyzer to return a mock report to prevent print format crash
    mock_savings_report = MagicMock()
    mock_savings_report.events = []
    mock_savings_report.total_savings_tokens = 50
    mock_savings_report.savings_percentage = 33.3
    mock_analyzer.parse_transcript.return_value = mock_savings_report

    # We stub transcript existence
    with (
        patch("os.path.exists", return_value=True),
        patch("context_benchmarking.run_benchmarks.print"),
    ):

        run_task_scenario(
            task=mock_task,
            scenario="A",
            model_name="gemini-2.5-flash",
            repo_path="/mock/repo",
            results_dir="/mock/results",
            max_steps=10,
            reporter=mock_reporter,
            analyzer=mock_analyzer,
        )

        # Verify simulator was instantiated and run
        mock_sim_class.assert_called_once_with(
            repo_path="/mock/repo", model_name="gemini-2.5-flash"
        )
        mock_sim.run_simulation.assert_called_once()

        # Verify analyzer parsed transcript
        mock_analyzer.parse_transcript.assert_called_once()

        # Verify reporter saved metrics with correctly mapped keys
        mock_reporter.save_run_metrics.assert_called_once()
        saved_args = mock_reporter.save_run_metrics.call_args[1]
        assert saved_args["scenario"] == "A"
        assert saved_args["task_id"] == "test_task"
        metrics = saved_args["metrics"]
        assert metrics["input_tokens"] == 100
        assert metrics["output_tokens"] == 50
        assert metrics["total_tokens"] == 150
        assert metrics["latency_seconds"] == 2.5
        assert metrics["tool_call_count"] == 3
        assert metrics["exit_code"] == 0
        assert metrics["tests_passed"] is True
        assert metrics["error"] is None


@patch("context_benchmarking.run_benchmarks.CoderAgentSimulator")
def test_run_task_scenario_crash_handling(mock_sim_class, mock_task):
    # Setup simulator mock to crash
    mock_sim = MagicMock()
    mock_sim.run_simulation.side_effect = RuntimeError("API key invalid")
    mock_sim_class.return_value = mock_sim

    mock_reporter = MagicMock()
    mock_analyzer = MagicMock()

    with patch("context_benchmarking.run_benchmarks.print"):
        run_task_scenario(
            task=mock_task,
            scenario="B",
            model_name="gemini-2.5-flash",
            repo_path="/mock/repo",
            results_dir="/mock/results",
            max_steps=10,
            reporter=mock_reporter,
            analyzer=mock_analyzer,
        )

        # Verify reporter saved error metrics
        mock_reporter.save_run_metrics.assert_called_once()
        saved_args = mock_reporter.save_run_metrics.call_args[1]
        assert saved_args["scenario"] == "B"
        assert saved_args["task_id"] == "test_task"
        metrics = saved_args["metrics"]
        assert metrics["tests_passed"] is False
        assert "API key invalid" in metrics["error"]


@patch("context_benchmarking.run_benchmarks.DatasetLoader")
@patch("context_benchmarking.run_benchmarks.Reporter")
@patch("context_benchmarking.run_benchmarks.OfflineAnalyzer")
@patch("context_benchmarking.run_benchmarks.run_task_scenario")
def test_cli_main_routing(
    mock_run_scenario, mock_analyzer_cls, mock_reporter_cls, mock_loader_cls
):
    # Mock dataset loader
    mock_loader = MagicMock()
    mock_task_1 = MagicMock(task_id="t1")
    mock_task_2 = MagicMock(task_id="t2")
    mock_loader.list_tasks.return_value = [mock_task_1, mock_task_2]
    mock_loader.get_task.return_value = mock_task_1
    mock_loader_cls.return_value = mock_loader

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a dummy tasks.json
        tasks_file_dir = os.path.join(temp_dir, "data")
        os.makedirs(tasks_file_dir)
        with open(os.path.join(tasks_file_dir, "tasks.json"), "w") as f:
            f.write("{}")

        # Case 1: Run all tasks, both scenarios
        argv = [
            "--repo-path",
            temp_dir,
            "--task",
            "all",
            "--scenario",
            "both",
            "--report",
            "report.md",
        ]
        with patch("context_benchmarking.run_benchmarks.print"):
            exit_code = main(argv)
            assert exit_code == 0

            # Should call run_scenario 4 times (2 tasks * 2 scenarios)
            assert mock_run_scenario.call_count == 4

        # Case 2: Run single task, scenario A only
        mock_run_scenario.reset_mock()
        argv = [
            "--repo-path",
            temp_dir,
            "--task",
            "t1",
            "--scenario",
            "A",
            "--report",
            "report.md",
        ]
        with patch("context_benchmarking.run_benchmarks.print"):
            exit_code = main(argv)
            assert exit_code == 0

            # Should call run_scenario 1 time
            assert mock_run_scenario.call_count == 1
            call_args = mock_run_scenario.call_args[1]
            assert call_args["task"] == mock_task_1
            assert call_args["scenario"] == "A"


def test_clean_safety_check_pyproject(capsys):
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "pyproject.toml"), "w") as f:
            f.write("")

        argv = ["--repo-path", temp_dir, "--results-dir", ".", "--clean"]
        exit_code = main(argv)
        assert exit_code == 1

        captured = capsys.readouterr()
        assert (
            "Error: results directory contains critical project files..."
            in captured.err
        )


def test_clean_safety_check_package_json(capsys):
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "package.json"), "w") as f:
            f.write("")

        argv = ["--repo-path", temp_dir, "--results-dir", ".", "--clean"]
        exit_code = main(argv)
        assert exit_code == 1

        captured = capsys.readouterr()
        assert (
            "Error: results directory contains critical project files..."
            in captured.err
        )
