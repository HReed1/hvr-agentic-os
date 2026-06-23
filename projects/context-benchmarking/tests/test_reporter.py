import os
import json
import tempfile
import pytest
from context_benchmarking.reporter import Reporter, RunMetrics, TaskResultEnvelope


def test_run_metrics_validation():
    metrics = RunMetrics(
        task_id="small_task",
        scenario="A",
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        latency_seconds=1.5,
        tool_call_count=3,
        exit_code=0,
        tests_passed=True,
    )
    assert metrics.task_id == "small_task"
    assert metrics.scenario == "A"
    assert metrics.total_tokens == 150


def test_task_result_envelope_calculations():
    a = RunMetrics(
        task_id="small_task",
        scenario="A",
        input_tokens=1000,
        output_tokens=200,
        total_tokens=1200,
        latency_seconds=10.0,
        tool_call_count=5,
        exit_code=0,
        tests_passed=True,
    )
    b = RunMetrics(
        task_id="small_task",
        scenario="B",
        input_tokens=400,
        output_tokens=100,
        total_tokens=500,
        latency_seconds=4.0,
        tool_call_count=2,
        exit_code=0,
        tests_passed=True,
    )
    envelope = TaskResultEnvelope(task_id="small_task", scenario_a=a, scenario_b=b)
    assert envelope.is_complete is True
    assert envelope.token_savings == 700
    assert envelope.token_savings_pct == pytest.approx(58.33, 0.01)
    assert envelope.latency_reduction == 6.0
    assert envelope.latency_reduction_pct == pytest.approx(60.0, 0.1)
    assert envelope.tool_call_reduction == 3
    assert envelope.tool_call_reduction_pct == pytest.approx(60.0, 0.1)


def test_reporter_save_and_load():
    with tempfile.TemporaryDirectory() as temp_dir:
        reporter = Reporter(results_dir=temp_dir)
        metrics_a = {
            "input_tokens": 1000,
            "output_tokens": 200,
            "latency_seconds": 10.0,
            "tool_call_count": 5,
            "exit_code": 0,
            "tests_passed": True,
        }
        filepath = reporter.save_run_metrics(
            scenario="A", task_id="small_task", metrics=metrics_a
        )
        assert os.path.exists(filepath)
        results = reporter.load_all_results()
        assert "small_task" in results
        env = results["small_task"]
        assert env.scenario_a is not None
        assert env.scenario_a.input_tokens == 1000
        assert env.scenario_b is None


def test_generate_markdown_report():
    with tempfile.TemporaryDirectory() as temp_dir:
        reporter = Reporter(results_dir=temp_dir)
        reporter.save_run_metrics(
            scenario="A",
            task_id="small_task",
            metrics={
                "input_tokens": 1000,
                "output_tokens": 200,
                "latency_seconds": 10.0,
                "tool_call_count": 5,
                "exit_code": 0,
                "tests_passed": True,
            },
        )
        reporter.save_run_metrics(
            scenario="B",
            task_id="small_task",
            metrics={
                "input_tokens": 400,
                "output_tokens": 100,
                "latency_seconds": 4.0,
                "tool_call_count": 2,
                "exit_code": 0,
                "tests_passed": True,
            },
        )
        report = reporter.generate_markdown_report()
        assert "# Context Benchmarking Scorecard" in report
        assert "## Executive Summary" in report
        assert "Total Input Tokens" in report
        assert "small_task" in report
        assert "60.0%" in report


def test_generate_markdown_report_with_offline_analyzer():
    # Test that when a transcript file is present, generate_markdown_report integrates it
    with tempfile.TemporaryDirectory() as temp_dir:
        reporter = Reporter(results_dir=temp_dir)

        # Save metrics for a completed task
        reporter.save_run_metrics(
            scenario="A",
            task_id="test_task_savings",
            metrics={
                "input_tokens": 1000,
                "output_tokens": 200,
                "latency_seconds": 10.0,
                "tool_call_count": 5,
                "exit_code": 0,
                "tests_passed": True,
            },
        )
        reporter.save_run_metrics(
            scenario="B",
            task_id="test_task_savings",
            metrics={
                "input_tokens": 400,
                "output_tokens": 100,
                "latency_seconds": 4.0,
                "tool_call_count": 2,
                "exit_code": 0,
                "tests_passed": True,
            },
        )

        # Write a dummy transcript file in the results directory
        # Named '{task_id}_scenario_a_transcript.jsonl'
        transcript_path = os.path.join(
            temp_dir, "test_task_savings_scenario_a_transcript.jsonl"
        )
        transcript_data = [
            {
                "tool": "view_file",
                "arguments": {"AbsolutePath": "app.py"},
                "output": "   1: def hello():\n   2:     pass",
            }
        ]
        with open(transcript_path, "w") as f:
            for item in transcript_data:
                f.write(json.dumps(item) + "\n")

        # Generate markdown report
        report = reporter.generate_markdown_report()

        # Verify that Theoretical Context Read Savings is in the report
        assert "## Theoretical Context Read Savings" in report
        assert (
            "### Task: `test_task_savings` — File Read Optimization Details" in report
        )
        assert "app.py" in report  # Comes from the analyzer report table

        # Now test when transcript is missing
        os.remove(transcript_path)
        report_missing = reporter.generate_markdown_report()
        assert "## Theoretical Context Read Savings" in report_missing
        assert "Warning: Transcript file" in report_missing
