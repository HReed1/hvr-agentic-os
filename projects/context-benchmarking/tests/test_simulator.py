import os
import json
import pytest
from unittest.mock import MagicMock, patch
from context_benchmarking.simulator import CoderAgentSimulator


@patch("context_benchmarking.simulator.GitManager")
@patch("context_benchmarking.simulator.DatasetLoader")
def test_simulator_lifecycle(mock_dataset_loader, mock_git_manager_class):
    # Setup mocks
    mock_git_manager = MagicMock()
    mock_git_manager.setup_branch.return_value = "task/test-branch"
    mock_git_manager.run_tests.return_value = {
        "exit_code": 0,
        "stdout": "All tests passed",
        "stderr": "",
    }
    mock_git_manager_class.return_value = mock_git_manager

    mock_task = MagicMock()
    mock_task.name = "Test Task"
    mock_task.description = "Task Description"
    mock_task.instructions = "Task Instructions"
    mock_task.files_to_modify = ["app.py"]

    mock_loader = MagicMock()
    mock_loader.get_task.return_value = mock_task
    mock_dataset_loader.return_value = mock_loader

    # Instantiate simulator
    with patch("context_benchmarking.simulator.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Configure mock generate_content behavior (thinking without tool call, then exit)
        mock_part = MagicMock()
        mock_part.text = "I need to view the file."
        mock_part.thought = True
        mock_part.function_call = None

        mock_response_1 = MagicMock()
        mock_response_1.candidates = [MagicMock(content=MagicMock(parts=[mock_part]))]
        mock_response_1.usage_metadata.prompt_token_count = 100
        mock_response_1.usage_metadata.candidates_token_count = 50

        mock_client.models.generate_content.side_effect = [mock_response_1]

        simulator = CoderAgentSimulator(repo_path=".", model_name="gemini-2.5-flash")

        transcript_path = "test_transcript.jsonl"
        metrics = simulator.run_simulation(
            task_id="small_task",
            scenario="A",
            transcript_path=transcript_path,
            max_steps=2,
        )

        # Verify GitManager setup and cleanup called
        mock_git_manager.setup_branch.assert_called_once_with("small_task")
        mock_git_manager.run_tests.assert_called_once_with("small_task")
        mock_git_manager.cleanup.assert_called_once()

        # Verify returned metrics
        assert metrics["success"] is True
        assert metrics["test_exit_code"] == 0
        assert metrics["steps_executed"] == 1
        assert metrics["input_tokens"] == 100
        assert metrics["output_tokens"] == 50

        # Verify transcript was written
        assert os.path.exists(transcript_path)
        with open(transcript_path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 1
        step_log = json.loads(lines[0])
        assert step_log["step_index"] == 0
        assert step_log["thinking"] == "I need to view the file."
        assert step_log["tool"] is None

        # Cleanup test transcript
        if os.path.exists(transcript_path):
            os.remove(transcript_path)


@patch("context_benchmarking.simulator.GitManager")
@patch("context_benchmarking.simulator.DatasetLoader")
def test_simulator_with_tool_call(mock_dataset_loader, mock_git_manager_class):
    # Setup mocks
    mock_git_manager = MagicMock()
    mock_git_manager.setup_branch.return_value = "task/test-branch"
    mock_git_manager.run_tests.return_value = {
        "exit_code": 0,
        "stdout": "All tests passed",
        "stderr": "",
    }
    mock_git_manager_class.return_value = mock_git_manager

    mock_task = MagicMock()
    mock_task.name = "Test Task"
    mock_task.description = "Task Description"
    mock_task.instructions = "Task Instructions"
    mock_task.files_to_modify = ["app.py"]

    mock_loader = MagicMock()
    mock_loader.get_task.return_value = mock_task
    mock_dataset_loader.return_value = mock_loader

    # Instantiate simulator
    with patch("context_benchmarking.simulator.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Step 1: Model requests grep_search
        mock_part_tool = MagicMock()
        mock_part_tool.text = "Searching for helper."
        mock_part_tool.thought = True
        mock_fc = MagicMock()
        mock_fc.name = "grep_search"
        mock_fc.args = {"query": "helper", "path": "mock_codebase"}
        mock_part_tool.function_call = mock_fc

        mock_response_1 = MagicMock()
        mock_response_1.candidates = [
            MagicMock(content=MagicMock(parts=[mock_part_tool]))
        ]
        mock_response_1.usage_metadata.prompt_token_count = 100
        mock_response_1.usage_metadata.candidates_token_count = 50

        # Step 2: Model finishes task
        mock_part_final = MagicMock()
        mock_part_final.text = "Finished task."
        mock_part_final.thought = False
        mock_part_final.function_call = None

        mock_response_2 = MagicMock()
        mock_response_2.candidates = [
            MagicMock(content=MagicMock(parts=[mock_part_final]))
        ]
        mock_response_2.usage_metadata.prompt_token_count = 150
        mock_response_2.usage_metadata.candidates_token_count = 30

        mock_client.models.generate_content.side_effect = [
            mock_response_1,
            mock_response_2,
        ]

        simulator = CoderAgentSimulator(repo_path=".", model_name="gemini-2.5-flash")

        transcript_path = "test_transcript_tool.jsonl"

        # Patch grep_search so we don't actually search the disk in this mock unit test
        with patch(
            "context_benchmarking.tools.grep_search", return_value="mock_match"
        ) as mock_grep:
            metrics = simulator.run_simulation(
                task_id="small_task",
                scenario="A",
                transcript_path=transcript_path,
                max_steps=5,
            )

        assert metrics["success"] is True
        assert metrics["total_tool_calls"] == 1
        assert metrics["steps_executed"] == 2
        assert metrics["input_tokens"] == 250
        assert metrics["output_tokens"] == 80

        # Verify transcript
        assert os.path.exists(transcript_path)
        with open(transcript_path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 2

        log_step_0 = json.loads(lines[0])
        assert log_step_0["step_index"] == 0
        assert log_step_0["tool"] == "grep_search"
        assert log_step_0["arguments"] == {"query": "helper", "path": "mock_codebase"}

        log_step_1 = json.loads(lines[1])
        assert log_step_1["step_index"] == 1
        assert log_step_1["tool"] is None
        assert log_step_1["thinking"] == "Finished task."

        if os.path.exists(transcript_path):
            os.remove(transcript_path)
