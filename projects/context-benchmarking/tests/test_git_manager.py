import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import subprocess
import pytest

from context_benchmarking.git_manager import GitManager, GitManagerError, GitError

# Mock tasks.json content
MOCK_TASKS_JSON = {
    "tasks": [
        {
            "task_id": "small_task",
            "name": "Small Task",
            "branch_name": "task/small-task-branch",
            "test_commands": ["pytest mock_codebase/tests/test_utils.py"],
        },
        {
            "task_id": "medium_task",
            "name": "Medium Task",
            "branch_name": "task/medium-task-branch",
            "test_commands": [
                "pytest mock_codebase/tests/test_routes.py",
                "npm run test",
            ],
        },
        {
            "task_id": "bad_branch_task",
            "name": "Bad Branch Task",
            "branch_name": "-options-injection",
            "test_commands": [],
        },
        {
            "task_id": "string_commands_task",
            "name": "String Commands Task",
            "branch_name": "task/string-commands",
            "test_commands": "pytest tests",
        },
    ]
}


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
def test_git_manager_init_success(mock_isdir, mock_run):
    # Mocking successful git repo check and branch name retrieval
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),  # is-inside-work-tree
        MagicMock(returncode=0, stdout="main\n"),  # abbrev-ref HEAD
    ]

    gm = GitManager(repo_path="/fake/repo")
    assert gm.repo_path == "/fake/repo"
    assert gm.base_branch == "main"
    assert gm.task_branch is None

    # Assert git commands were called
    mock_run.assert_any_call(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd="/fake/repo",
        stdout=-1,
        stderr=-1,
        text=True,
        shell=False,
        check=False,
    )
    mock_run.assert_any_call(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd="/fake/repo",
        stdout=-1,
        stderr=-1,
        text=True,
        shell=False,
        check=False,
    )


@patch("subprocess.run")
@patch("os.path.isdir", return_value=False)
def test_git_manager_init_not_dir(mock_isdir, mock_run):
    with pytest.raises(GitManagerError, match="not a directory"):
        GitManager(repo_path="/fake/repo")


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
def test_git_manager_init_not_git_repo(mock_isdir, mock_run):
    mock_run.side_effect = FileNotFoundError()
    with pytest.raises(GitManagerError, match="git command not found"):
        GitManager(repo_path="/fake/repo")


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_TASKS_JSON))
def test_setup_branch_success(mock_file, mock_exists, mock_isdir, mock_run):
    # Setup mock returns:
    # 1. is-inside-work-tree (init)
    # 2. abbrev-ref HEAD (init)
    # 3. status --porcelain (clean workspace)
    # 4. reset --hard HEAD
    # 5. clean -fd
    # 6. checkout base_branch
    # 7. checkout -B branch_name base_branch
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="main\n"),
        MagicMock(returncode=0, stdout=""),
        MagicMock(returncode=0, stdout=""),
        MagicMock(returncode=0, stdout=""),
        MagicMock(returncode=0, stdout=""),
        MagicMock(returncode=0, stdout=""),
    ]

    gm = GitManager(repo_path="/fake/repo")
    branch = gm.setup_branch("small_task")

    assert branch == "task/small-task-branch"
    assert gm.task_branch == "task/small-task-branch"

    # Verify checkout call
    mock_run.assert_any_call(
        ["git", "checkout", "-B", "task/small-task-branch", "main"],
        cwd="/fake/repo",
        stdout=-1,
        stderr=-1,
        text=True,
        shell=False,
        check=False,
    )


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_TASKS_JSON))
def test_setup_branch_not_found(mock_file, mock_exists, mock_isdir, mock_run):
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="main\n"),
        MagicMock(returncode=0, stdout=""),
    ]

    gm = GitManager(repo_path="/fake/repo")
    with pytest.raises(ValueError, match="not found in tasks database"):
        gm.setup_branch("unknown_task")


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_TASKS_JSON))
def test_setup_branch_dirty_worktree(mock_file, mock_exists, mock_isdir, mock_run):
    # Setup mock returns:
    # 1. is-inside-work-tree (init)
    # 2. abbrev-ref HEAD (init)
    # 3. status --porcelain (returns dirty change list)
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="main\n"),
        MagicMock(returncode=0, stdout=" M modified_file.py\n"),
    ]

    gm = GitManager(repo_path="/fake/repo")
    with pytest.raises(GitManagerError, match="Workspace is dirty"):
        gm.setup_branch("small_task")


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_TASKS_JSON))
def test_setup_branch_options_injection(mock_file, mock_exists, mock_isdir, mock_run):
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="main\n"),
        MagicMock(returncode=0, stdout=""),
    ]

    gm = GitManager(repo_path="/fake/repo")
    with pytest.raises(ValueError, match="Branch name cannot start with '-'"):
        gm.setup_branch("bad_branch_task")


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_TASKS_JSON))
def test_run_tests_success(mock_file, mock_exists, mock_isdir, mock_run):
    # Setup mock returns:
    # 1. is-inside-work-tree (init)
    # 2. abbrev-ref HEAD (init)
    # 3. abbrev-ref HEAD (verification in run_tests)
    # 4. pytest command execution
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="main\n"),
        MagicMock(returncode=0, stdout="task/small-task-branch\n"),
        MagicMock(returncode=0, stdout="All tests passed", stderr=""),
    ]

    gm = GitManager(repo_path="/fake/repo")
    gm.task_branch = "task/small-task-branch"
    results = gm.run_tests("small_task")

    assert results["exit_code"] == 0
    assert "All tests passed" in results["stdout"]
    assert results["stderr"] == ""


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_TASKS_JSON))
def test_run_tests_failure(mock_file, mock_exists, mock_isdir, mock_run):
    # Setup mock returns:
    # 1. is-inside-work-tree (init)
    # 2. abbrev-ref HEAD (init)
    # 3. abbrev-ref HEAD (verification in run_tests)
    # 4. pytest fails, npm fails
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="main\n"),
        MagicMock(returncode=0, stdout="task/medium-task-branch\n"),
        MagicMock(returncode=1, stdout="1 failed", stderr="pytest error"),
        MagicMock(returncode=2, stdout="npm fail", stderr="npm error"),
    ]

    gm = GitManager(repo_path="/fake/repo")
    gm.task_branch = "task/medium-task-branch"
    results = gm.run_tests("medium_task")

    # Combined exit code should be the first non-zero (1)
    assert results["exit_code"] == 1
    assert "1 failed" in results["stdout"]
    assert "npm fail" in results["stdout"]
    assert "pytest error" in results["stderr"]
    assert "npm error" in results["stderr"]


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_TASKS_JSON))
def test_run_tests_wrong_branch(mock_file, mock_exists, mock_isdir, mock_run):
    # Setup mock returns:
    # 1. is-inside-work-tree (init)
    # 2. abbrev-ref HEAD (init)
    # 3. abbrev-ref HEAD (verification in run_tests returns wrong branch)
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="main\n"),
        MagicMock(returncode=0, stdout="main\n"),
    ]

    gm = GitManager(repo_path="/fake/repo")
    gm.task_branch = "task/small-task-branch"
    with pytest.raises(
        GitManagerError, match="Repository is not on the expected task branch"
    ):
        gm.run_tests("small_task")


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(MOCK_TASKS_JSON))
def test_run_tests_malformed_commands(mock_file, mock_exists, mock_isdir, mock_run):
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="main\n"),
        MagicMock(returncode=0, stdout="task/string-commands\n"),
    ]

    gm = GitManager(repo_path="/fake/repo")
    gm.task_branch = "task/string-commands"
    with pytest.raises(ValueError, match="test_commands must be a list"):
        gm.run_tests("string_commands_task")


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
def test_cleanup(mock_isdir, mock_run):
    # Setup mock returns:
    # 1. is-inside-work-tree (init)
    # 2. abbrev-ref HEAD (init)
    # 3. reset --hard HEAD
    # 4. clean -fd
    # 5. checkout base_branch
    # 6. branch -D task_branch
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="main\n"),
        MagicMock(returncode=0, stdout=""),
        MagicMock(returncode=0, stdout=""),
        MagicMock(returncode=0, stdout=""),
        MagicMock(returncode=0, stdout=""),
    ]

    gm = GitManager(repo_path="/fake/repo")
    gm.task_branch = "task/some-branch"
    gm.cleanup()

    assert gm.task_branch is None
    # Verify cleanup operations were called
    mock_run.assert_any_call(
        ["git", "reset", "--hard", "HEAD"],
        cwd="/fake/repo",
        stdout=-1,
        stderr=-1,
        text=True,
        shell=False,
        check=False,
    )
    mock_run.assert_any_call(
        ["git", "clean", "-fd"],
        cwd="/fake/repo",
        stdout=-1,
        stderr=-1,
        text=True,
        shell=False,
        check=False,
    )
    mock_run.assert_any_call(
        ["git", "checkout", "main"],
        cwd="/fake/repo",
        stdout=-1,
        stderr=-1,
        text=True,
        shell=False,
        check=False,
    )
    mock_run.assert_any_call(
        ["git", "branch", "-D", "task/some-branch"],
        cwd="/fake/repo",
        stdout=-1,
        stderr=-1,
        text=True,
        shell=False,
        check=False,
    )


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
def test_git_error_propagation(mock_isdir, mock_run):
    # Setup mock returns:
    # 1. is-inside-work-tree (init)
    # 2. abbrev-ref HEAD (init)
    # 3. status --porcelain fails with GitError
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="main\n"),
        MagicMock(returncode=128, stdout="", stderr="fatal error"),
    ]

    gm = GitManager(repo_path="/fake/repo")
    with pytest.raises(GitError, match="Git command failed"):
        gm.setup_branch("small_task")


@patch("subprocess.run")
@patch("os.path.isdir", return_value=True)
def test_detached_head_resolution(mock_isdir, mock_run):
    # Setup mock returns:
    # 1. is-inside-work-tree (init)
    # 2. abbrev-ref HEAD returns "HEAD" (detached state)
    # 3. rev-parse HEAD returns commit hash
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="true"),
        MagicMock(returncode=0, stdout="HEAD\n"),
        MagicMock(returncode=0, stdout="a1b2c3d4e5f6\n"),
    ]

    gm = GitManager(repo_path="/fake/repo")
    assert gm.base_branch == "a1b2c3d4e5f6"


def test_git_manager_integration():
    # Only run integration test if git is available
    try:
        subprocess.run(
            ["git", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    except FileNotFoundError:
        pytest.skip("Git is not installed on this system.")

    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize temp git repo
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        # Create a dummy commit
        dummy_file = os.path.join(temp_dir, "initial.txt")
        with open(dummy_file, "w") as f:
            f.write("Initial commit content")
        subprocess.run(
            ["git", "add", "initial.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        # Create data/tasks.json
        data_dir = os.path.join(temp_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        tasks_file = os.path.join(data_dir, "tasks.json")

        tasks_data = {
            "tasks": [
                {
                    "task_id": "test_task",
                    "name": "Test Task",
                    "branch_name": "task/test-branch",
                    "test_commands": ["echo 'Test step 1'", "echo 'Test step 2'"],
                }
            ]
        }
        with open(tasks_file, "w") as f:
            json.dump(tasks_data, f)

        # Add and commit tasks.json so it is tracked and not deleted by git clean!
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "Add tasks json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        # Run GitManager operations
        gm = GitManager(repo_path=temp_dir)
        assert gm.base_branch == "main"

        # Setup branch
        branch = gm.setup_branch("test_task")
        assert branch == "task/test-branch"
        assert gm._get_current_branch() == "task/test-branch"

        # Run tests
        results = gm.run_tests("test_task")
        assert results["exit_code"] == 0
        assert "Test step 1" in results["stdout"]
        assert "Test step 2" in results["stdout"]

        # Cleanup
        gm.cleanup()
        assert gm.task_branch is None
        assert gm._get_current_branch() == "main"
