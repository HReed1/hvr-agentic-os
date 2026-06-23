import os
import shutil
import tempfile
import subprocess
import json
import pytest
from unittest.mock import patch, MagicMock

from context_benchmarking.git_manager import GitManager, GitManagerError, GitError


def test_invalid_repo_path_not_exists():
    """Verify that GitManager raises GitManagerError if repo_path does not exist."""
    with pytest.raises(GitManagerError) as exc_info:
        GitManager(repo_path="/nonexistent/directory/path/here")
    assert "is not a directory" in str(exc_info.value)


def test_invalid_repo_path_not_git_repo():
    """
    Verify that GitManager raises GitManagerError if directory is not a git repo.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(GitManagerError) as exc_info:
            GitManager(repo_path=temp_dir)
        # It now correctly raises the friendly message from __init__ because the GitError is not masked
        assert "is not a valid Git repository" in str(exc_info.value)
        assert "not a git repository" in str(exc_info.value)


def test_missing_git_on_path():
    """Verify GitManager error when git is not found on the PATH."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(GitManagerError) as exc_info:
                with patch("os.path.isdir", return_value=True):
                    GitManager(repo_path=temp_dir)
            assert "git command not found on the system PATH" in str(exc_info.value)


def test_unknown_task_id():
    """Verify GitManager handles unknown task ID gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        dummy_file = os.path.join(temp_dir, "file.txt")
        with open(dummy_file, "w") as f:
            f.write("test")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")
        with open(tasks_path, "w") as f:
            json.dump(
                {
                    "tasks": [
                        {
                            "task_id": "valid_task",
                            "branch_name": "task/valid",
                            "test_commands": [],
                        }
                    ]
                },
                f,
            )
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        gm = GitManager(repo_path=temp_dir)

        with pytest.raises(ValueError) as exc_info:
            gm.setup_branch("unknown_task")
        assert "not found in tasks database" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            gm.run_tests("unknown_task")
        assert "not found in tasks database" in str(exc_info.value)


def test_git_behavior_isolation_and_pollution():
    """Verify git checkout, reset, and cleanup isolation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        tracked_file = os.path.join(temp_dir, "tracked.txt")
        with open(tracked_file, "w") as f:
            f.write("version 1")
        subprocess.run(
            ["git", "add", "tracked.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")
        with open(tasks_path, "w") as f:
            json.dump(
                {
                    "tasks": [
                        {
                            "task_id": "t1",
                            "branch_name": "task/t1",
                            "test_commands": ["echo 'running tests'"],
                        }
                    ]
                },
                f,
            )
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "add tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        gm = GitManager(repo_path=temp_dir)
        assert gm.base_branch == "main"

        branch = gm.setup_branch("t1")
        assert branch == "task/t1"
        assert gm._get_current_branch() == "task/t1"

        # Modify a file after setting up branch
        with open(tracked_file, "w") as f:
            f.write("version 2 modified")

        untracked_file = os.path.join(temp_dir, "untracked.txt")
        with open(untracked_file, "w") as f:
            f.write("new file content")

        assert os.path.exists(untracked_file)
        with open(tracked_file, "r") as f:
            assert f.read() == "version 2 modified"

        gm.cleanup()

        # Verify clean state
        assert gm._get_current_branch() == "main"
        assert gm.task_branch is None

        with open(tracked_file, "r") as f:
            assert f.read() == "version 1"

        assert not os.path.exists(untracked_file)

        branches_res = subprocess.run(
            ["git", "branch"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            text=True,
            shell=False,
        )
        assert "task/t1" not in branches_res.stdout


def test_missing_tasks_json():
    """Verify GitManager raises error if tasks.json is missing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        dummy_file = os.path.join(temp_dir, "file.txt")
        with open(dummy_file, "w") as f:
            f.write("test")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        gm = GitManager(repo_path=temp_dir)
        with pytest.raises(GitManagerError) as exc_info:
            gm.setup_branch("t1")
        assert "Tasks file not found" in str(exc_info.value)


def test_malformed_test_commands():
    """Verify behavior when test_commands is not a list in tasks.json."""
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        dummy_file = os.path.join(temp_dir, "file.txt")
        with open(dummy_file, "w") as f:
            f.write("test")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")

        # test_commands as a string instead of a list
        tasks_data = {
            "tasks": [
                {
                    "task_id": "malformed_task",
                    "branch_name": "task/malformed",
                    "test_commands": "echo 'not a list'",
                }
            ]
        }
        with open(tasks_path, "w") as f:
            json.dump(tasks_data, f)
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        gm = GitManager(repo_path=temp_dir)
        gm.setup_branch("malformed_task")

        # Calling run_tests should now raise ValueError indicating test_commands must be a list
        with pytest.raises(ValueError, match="test_commands must be a list"):
            gm.run_tests("malformed_task")


def test_pythonpath_hijacking_protection():
    """
    Verify that PYTHONPATH in the run_tests environment prepends self.repo_path.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        dummy_file = os.path.join(temp_dir, "file.txt")
        with open(dummy_file, "w") as f:
            f.write("test")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")
        tasks_data = {
            "tasks": [
                {
                    "task_id": "pythonpath_task",
                    "branch_name": "task/pythonpath",
                    "test_commands": ["pytest --version"],
                }
            ]
        }
        with open(tasks_path, "w") as f:
            json.dump(tasks_data, f)
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        gm = GitManager(repo_path=temp_dir)
        gm.setup_branch("pythonpath_task")

        # We will mock subprocess.run safely by delegating git commands to the real subprocess.run
        original_run = subprocess.run

        def mock_subprocess_run(args, *args_list, **kwargs):
            if args and args[0] == "git":
                return original_run(args, *args_list, **kwargs)
            return MagicMock(returncode=0, stdout="pytest 8.0", stderr="")

        with patch("subprocess.run", side_effect=mock_subprocess_run):
            # Case 1: PYTHONPATH is already set in external environment
            with patch.dict(os.environ, {"PYTHONPATH": "/external/path"}):
                gm.run_tests("pythonpath_task")
                # Since we want to verify the env argument passed to subprocess.run for pytest
                # we don't have to capture call_args directly if the mock side_effect intercepts it.
                # Let's inspect the env in a wrapper or check mocked_run call_args.

        # Let's do a more direct assertion by spying on subprocess.run
        with patch("subprocess.run", side_effect=mock_subprocess_run) as spy_run:
            with patch.dict(os.environ, {"PYTHONPATH": "/external/path"}):
                gm.run_tests("pythonpath_task")
                # Look for calls that were not 'git'
                pytest_call = None
                for call in spy_run.call_args_list:
                    call_args = call[0][0]
                    if call_args and call_args[0] != "git":
                        pytest_call = call
                        break
                assert pytest_call is not None
                env = pytest_call[1].get("env", {})
                expected_pythonpath = gm.repo_path + os.pathsep + "/external/path"
                assert env.get("PYTHONPATH") == expected_pythonpath

            spy_run.reset_mock()
            with patch.dict(os.environ, {}, clear=True):
                gm.run_tests("pythonpath_task")
                pytest_call = None
                for call in spy_run.call_args_list:
                    call_args = call[0][0]
                    if call_args and call_args[0] != "git":
                        pytest_call = call
                        break
                assert pytest_call is not None
                env = pytest_call[1].get("env", {})
                assert env.get("PYTHONPATH") == gm.repo_path


def test_branch_option_injection_extended():
    """
    Verify branch name option injection checks and command injection safety.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        dummy_file = os.path.join(temp_dir, "file.txt")
        with open(dummy_file, "w") as f:
            f.write("test")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")
        tasks_data = {
            "tasks": [
                {
                    "task_id": "dash_branch",
                    "branch_name": "--orphan",
                    "test_commands": [],
                },
                {
                    "task_id": "malicious_chars_branch",
                    "branch_name": "task/branch; echo hijacked",
                    "test_commands": [],
                },
            ]
        }
        with open(tasks_path, "w") as f:
            json.dump(tasks_data, f)
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        gm = GitManager(repo_path=temp_dir)

        # 1. Branch starting with '-' must raise ValueError
        with pytest.raises(ValueError, match="Branch name cannot start with '-'"):
            gm.setup_branch("dash_branch")

        # 2. Branch with shell injection characters should not execute the shell command
        # due to shell=False, but it will fail git checkout since it's an invalid branch name.
        with pytest.raises(GitError) as exc_info:
            gm.setup_branch("malicious_chars_branch")
        assert "Git command failed" in str(exc_info.value)
        # Verify the command was executed directly with shell=False and did not run 'echo hijacked'
        assert (
            "not a valid branch name" in str(exc_info.value)
            or "invalid reference" in str(exc_info.value)
            or "invalid branch name" in str(exc_info.value)
            or "invalid refname" in str(exc_info.value)
            or "not a valid object name" in str(exc_info.value)
        )


def test_uncommitted_changes_protection_matrix():
    """
    Verify the dirty workspace detection under unstaged, staged, untracked, and ignored file scenarios.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        tracked_file = os.path.join(temp_dir, "tracked.txt")
        with open(tracked_file, "w") as f:
            f.write("original")
        subprocess.run(
            ["git", "add", "tracked.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")
        tasks_data = {
            "tasks": [
                {
                    "task_id": "test_task",
                    "branch_name": "task/test",
                    "test_commands": [],
                }
            ]
        }
        with open(tasks_path, "w") as f:
            json.dump(tasks_data, f)
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        # Create .gitignore for the ignored test case
        gitignore_path = os.path.join(temp_dir, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("ignored.log\n")
        subprocess.run(
            ["git", "add", ".gitignore"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "add gitignore"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        # Case 1: Clean workspace -> setup_branch succeeds
        gm = GitManager(repo_path=temp_dir)
        gm.setup_branch("test_task")
        gm.cleanup()

        # Case 2: Unstaged modifications to tracked file -> raises GitManagerError
        with open(tracked_file, "w") as f:
            f.write("unstaged modification")
        gm = GitManager(repo_path=temp_dir)
        with pytest.raises(GitManagerError, match="Workspace is dirty"):
            gm.setup_branch("test_task")
        # clean it up manually for next test cases
        subprocess.run(
            ["git", "reset", "--hard", "HEAD"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        # Case 3: Staged modification to tracked file -> raises GitManagerError
        with open(tracked_file, "w") as f:
            f.write("staged modification")
        subprocess.run(
            ["git", "add", "tracked.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        gm = GitManager(repo_path=temp_dir)
        with pytest.raises(GitManagerError, match="Workspace is dirty"):
            gm.setup_branch("test_task")
        # clean it up manually
        subprocess.run(
            ["git", "reset", "--hard", "HEAD"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        # Case 4: Untracked file -> raises GitManagerError
        untracked_file = os.path.join(temp_dir, "untracked.txt")
        with open(untracked_file, "w") as f:
            f.write("untracked")
        gm = GitManager(repo_path=temp_dir)
        with pytest.raises(GitManagerError, match="Workspace is dirty"):
            gm.setup_branch("test_task")
        # clean it up manually
        os.remove(untracked_file)

        # Case 5: Ignored file -> passes (no error raised)
        ignored_file = os.path.join(temp_dir, "ignored.log")
        with open(ignored_file, "w") as f:
            f.write("log message")
        gm = GitManager(repo_path=temp_dir)
        # Should not raise exception
        branch = gm.setup_branch("test_task")
        assert branch == "task/test"
        gm.cleanup()
        # cleanup manually
        if os.path.exists(ignored_file):
            os.remove(ignored_file)


def test_detached_head_cleanup():
    """
    Verify that if initialized in a detached HEAD state, the manager correctly resolves the
    commit hash as base_branch, sets up the task branch, and reverts back to the detached HEAD commit.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        dummy_file = os.path.join(temp_dir, "file.txt")
        with open(dummy_file, "w") as f:
            f.write("initial commit")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "commit 1"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        # Get the commit hash
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            text=True,
            shell=False,
        )
        commit_hash = res.stdout.strip()

        # Write tasks database
        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")
        tasks_data = {
            "tasks": [
                {
                    "task_id": "detached_task",
                    "branch_name": "task/detached",
                    "test_commands": [],
                }
            ]
        }
        with open(tasks_path, "w") as f:
            json.dump(tasks_data, f)
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        # Get the new commit hash (since tasks commit is the HEAD)
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            text=True,
            shell=False,
        )
        head_commit_hash = res.stdout.strip()

        # Checkout head_commit_hash directly to enter detached HEAD state
        subprocess.run(
            ["git", "checkout", head_commit_hash],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )

        # Check current branch is HEAD (detached)
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            text=True,
            shell=False,
        )
        assert res.stdout.strip() == "HEAD"

        # Initialize GitManager
        gm = GitManager(repo_path=temp_dir)
        # Should resolve base_branch to the commit hash
        assert gm.base_branch == head_commit_hash

        # Setup branch
        branch = gm.setup_branch("detached_task")
        assert branch == "task/detached"
        assert gm._get_current_branch() == "task/detached"

        # Cleanup should return to detached HEAD state at head_commit_hash
        gm.cleanup()
        assert gm.task_branch is None

        # Verify current branch is HEAD (detached)
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            text=True,
            shell=False,
        )
        assert res.stdout.strip() == "HEAD"

        # Verify current commit is head_commit_hash
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            text=True,
            shell=False,
        )
        assert res.stdout.strip() == head_commit_hash


def test_subprocess_execution_security():
    """
    Verify that test commands cannot escape using shell operators like redirections, pipes, or chains.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        dummy_file = os.path.join(temp_dir, "file.txt")
        with open(dummy_file, "w") as f:
            f.write("test")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")

        # Command attempts redirection and chaining
        tasks_data = {
            "tasks": [
                {
                    "task_id": "malicious_cmd_task",
                    "branch_name": "task/malicious-cmd",
                    "test_commands": [
                        "echo hello > redirection_test.txt",
                        "echo first && echo second",
                    ],
                }
            ]
        }
        with open(tasks_path, "w") as f:
            json.dump(tasks_data, f)
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        gm = GitManager(repo_path=temp_dir)
        gm.setup_branch("malicious_cmd_task")

        results = gm.run_tests("malicious_cmd_task")

        # 1. Redirection file should not be created in temp_dir
        assert not os.path.exists(os.path.join(temp_dir, "redirection_test.txt"))

        # 2. Verify command output contains redirection tokens, meaning they were passed as literal args
        assert "hello > redirection_test.txt" in results["stdout"]

        # 3. Verify chained command output prints first and the chaining operators as arguments
        assert "first && echo second" in results["stdout"]


def test_branch_name_whitespace_and_special_chars():
    """Verify that branch names containing whitespace or control characters fail git checkout safely without command execution."""
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        dummy_file = os.path.join(temp_dir, "file.txt")
        with open(dummy_file, "w") as f:
            f.write("test")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")

        invalid_branches = [
            "task name with spaces",
            "task\nnewline",
            "task\rreturn",
            "task\tbacktab",
            "task\0null",
        ]
        tasks_data = {
            "tasks": [
                {"task_id": f"special_{i}", "branch_name": name, "test_commands": []}
                for i, name in enumerate(invalid_branches)
            ]
        }
        with open(tasks_path, "w") as f:
            json.dump(tasks_data, f)
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        gm = GitManager(repo_path=temp_dir)
        for i in range(len(invalid_branches)):
            with pytest.raises((GitError, GitManagerError)) as exc_info:
                gm.setup_branch(f"special_{i}")
            assert "Git command failed" in str(
                exc_info.value
            ) or "Error executing git command" in str(exc_info.value)


def test_uncommitted_deletions():
    """Verify that uncommitted deletions of tracked files are correctly detected as workspace dirty."""
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        tracked_file = os.path.join(temp_dir, "tracked.txt")
        with open(tracked_file, "w") as f:
            f.write("tracked content")
        subprocess.run(
            ["git", "add", "tracked.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")
        tasks_data = {
            "tasks": [
                {
                    "task_id": "test_task",
                    "branch_name": "task/test",
                    "test_commands": [],
                }
            ]
        }
        with open(tasks_path, "w") as f:
            json.dump(tasks_data, f)
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        gm = GitManager(repo_path=temp_dir)

        # Delete tracked file
        os.remove(tracked_file)

        with pytest.raises(GitManagerError, match="Workspace is dirty"):
            gm.setup_branch("test_task")


def test_subprocess_execution_with_non_string_commands():
    """Verify that non-string test command values in the tasks JSON raise TypeError/AttributeError due to unhandled shlex.split outside try/except."""
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
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

        dummy_file = os.path.join(temp_dir, "file.txt")
        with open(dummy_file, "w") as f:
            f.write("test")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        tasks_path = os.path.join(temp_dir, "data", "tasks.json")
        tasks_data = {
            "tasks": [
                {
                    "task_id": "invalid_types_task",
                    "branch_name": "task/invalid-types",
                    "test_commands": [123],
                }
            ]
        }
        with open(tasks_path, "w") as f:
            json.dump(tasks_data, f)
        subprocess.run(
            ["git", "add", "data/tasks.json"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "tasks"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            shell=False,
        )

        gm = GitManager(repo_path=temp_dir)
        gm.setup_branch("invalid_types_task")

        # Calling run_tests with non-string command (int) raises AttributeError because of shlex.split(cmd_str)
        # called outside the try/except block.
        with pytest.raises((AttributeError, TypeError)):
            gm.run_tests("invalid_types_task")


def test_empty_repo_initialization():
    """Verify that GitManager raises a friendly error or handles initialization in an empty repo gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize an empty git repo with no commits
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )

        try:
            gm = GitManager(repo_path=temp_dir)
            # If initialization succeeds, setup_branch must fail since there is no commit
            os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
            with open(os.path.join(temp_dir, "data", "tasks.json"), "w") as f:
                json.dump(
                    {
                        "tasks": [
                            {
                                "task_id": "t1",
                                "branch_name": "task/t1",
                                "test_commands": [],
                            }
                        ]
                    },
                    f,
                )

            with pytest.raises(GitError):
                gm.setup_branch("t1")
        except GitManagerError as e:
            # If it fails at initialization, that is also a correct safe behavior
            assert "is not a valid Git repository" in str(
                e
            ) or "Git command failed" in str(e)
