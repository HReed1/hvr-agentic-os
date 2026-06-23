import os
import json
import tempfile
import pytest
from pydantic import ValidationError
from context_benchmarking.dataset import (
    DatasetLoader,
    TaskDefinition,
    DatasetError,
    TaskValidationError,
)


def test_task_definition_validation():
    # Valid task definition
    valid_data = {
        "task_id": "task_01",
        "name": "Test Task",
        "size": "small",
        "difficulty": "easy",
        "description": "A test task.",
        "branch_name": "task/test-task",
        "files_to_modify": ["app.py"],
        "test_commands": ["pytest"],
        "instructions": "Do the task.",
    }
    task = TaskDefinition.model_validate(valid_data)
    assert task.task_id == "task_01"
    assert task.files_to_modify == ["app.py"]

    # Missing required field
    invalid_data = valid_data.copy()
    del invalid_data["name"]
    with pytest.raises(ValidationError):
        TaskDefinition.model_validate(invalid_data)


def test_dataset_loader_success():
    dataset_content = {
        "tasks": [
            {
                "task_id": "task_01",
                "name": "Task One",
                "size": "small",
                "difficulty": "easy",
                "description": "First task.",
                "branch_name": "task/one",
                "files_to_modify": ["app.py"],
                "test_commands": ["pytest"],
                "instructions": "Do it.",
            },
            {
                "task_id": "task_02",
                "name": "Task Two",
                "size": "medium",
                "difficulty": "medium",
                "description": "Second task.",
                "branch_name": "task/two",
                "files_to_modify": ["main.py", "utils.py"],
                "test_commands": ["pytest tests/test_two.py"],
                "instructions": "Do it again.",
            },
        ]
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        tasks_file = os.path.join(temp_dir, "tasks.json")
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(dataset_content, f)

        loader = DatasetLoader(tasks_file_path=tasks_file)
        assert len(loader.tasks) == 2

        # Test get_task
        task1 = loader.get_task("task_01")
        assert task1.name == "Task One"

        with pytest.raises(KeyError):
            loader.get_task("non_existent")

        # Test list_tasks filters
        assert len(loader.list_tasks(size="small")) == 1
        assert len(loader.list_tasks(size="medium")) == 1
        assert len(loader.list_tasks(size="large")) == 0
        assert len(loader.list_tasks(difficulty="easy")) == 1
        assert len(loader.list_tasks(difficulty="medium")) == 1
        assert len(loader.list_tasks(size="small", difficulty="easy")) == 1
        assert len(loader.list_tasks(size="small", difficulty="medium")) == 0


def test_dataset_loader_file_not_found():
    with pytest.raises(FileNotFoundError):
        DatasetLoader(tasks_file_path="non_existent_file.json")


def test_dataset_loader_invalid_json():
    with tempfile.TemporaryDirectory() as temp_dir:
        tasks_file = os.path.join(temp_dir, "tasks.json")
        with open(tasks_file, "w", encoding="utf-8") as f:
            f.write("{invalid_json:")

        with pytest.raises(DatasetError) as exc_info:
            DatasetLoader(tasks_file_path=tasks_file)
        assert "Invalid JSON syntax" in str(exc_info.value)


def test_dataset_loader_validation_errors():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Case 1: Root is not a dict
        tasks_file = os.path.join(temp_dir, "tasks_root_not_dict.json")
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(["not", "a", "dict"], f)
        with pytest.raises(TaskValidationError) as exc_info:
            DatasetLoader(tasks_file_path=tasks_file)
        assert "must be a JSON object" in str(exc_info.value)

        # Case 2: Missing 'tasks' key
        tasks_file = os.path.join(temp_dir, "tasks_missing_key.json")
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump({"not_tasks": []}, f)
        with pytest.raises(TaskValidationError) as exc_info:
            DatasetLoader(tasks_file_path=tasks_file)
        assert "must contain a 'tasks' key" in str(exc_info.value)

        # Case 3: 'tasks' is not a list
        tasks_file = os.path.join(temp_dir, "tasks_not_list.json")
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump({"tasks": "not a list"}, f)
        with pytest.raises(TaskValidationError) as exc_info:
            DatasetLoader(tasks_file_path=tasks_file)
        assert "must be a JSON array" in str(exc_info.value)

        # Case 4: Duplicate task_id
        tasks_file = os.path.join(temp_dir, "tasks_duplicate.json")
        dup_content = {
            "tasks": [
                {
                    "task_id": "dup",
                    "name": "A",
                    "size": "S",
                    "difficulty": "E",
                    "description": "D",
                    "branch_name": "B",
                    "files_to_modify": [],
                    "test_commands": [],
                    "instructions": "I",
                },
                {
                    "task_id": "dup",
                    "name": "B",
                    "size": "S",
                    "difficulty": "E",
                    "description": "D",
                    "branch_name": "B",
                    "files_to_modify": [],
                    "test_commands": [],
                    "instructions": "I",
                },
            ]
        }
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(dup_content, f)
        with pytest.raises(TaskValidationError) as exc_info:
            DatasetLoader(tasks_file_path=tasks_file)
        assert "Duplicate task_id" in str(exc_info.value)
