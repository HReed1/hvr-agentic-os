import os
import tempfile
import pytest
from context_benchmarking.tools import (
    grep_search,
    view_file,
    get_skeleton,
    get_symbol_block,
    get_symbols,
    query_codebase_graph,
    write_to_file,
    replace_file_content,
)


def test_grep_search():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        file1 = os.path.join(temp_dir, "file1.txt")
        with open(file1, "w", encoding="utf-8") as f:
            f.write("hello world\npython search test\n")

        file2 = os.path.join(temp_dir, "file2.py")
        with open(file2, "w", encoding="utf-8") as f:
            f.write("def func():\n    print('hello')\n")

        # 1. Search for query with matches
        res = grep_search("hello", temp_dir, repo_path=temp_dir)
        assert "file1.txt:1: hello world" in res
        assert "file2.py:2:     print('hello')" in res

        # 2. Search for query with no matches
        res_none = grep_search("absent_query", temp_dir, repo_path=temp_dir)
        assert "No matches found" in res_none

        # 3. Non-existent path
        with pytest.raises(FileNotFoundError):
            grep_search("hello", "non_existent_dir")


def test_view_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.py")
        content = "line one\nline two\nline three\nline four\n"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        # 1. View full file
        res = view_file(test_file)
        expected = "   1: line one\n   2: line two\n   3: line three\n   4: line four"
        assert res == expected

        # 2. View subset of lines
        res_sub = view_file(test_file, start_line=2, end_line=3)
        expected_sub = "   2: line two\n   3: line three"
        assert res_sub == expected_sub

        # 3. Handle out of bounds/non-existent
        with pytest.raises(FileNotFoundError):
            view_file("non_existent_file.py")
        with pytest.raises(IsADirectoryError):
            view_file(temp_dir)


def test_get_skeleton():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.py")
        content = """class MyClass:
    \"\"\"Docstring here.\"\"\"
    pass

def my_function():
    \"\"\"Function docstring.\"\"\"
    x = 1
    return x
"""
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        res = get_skeleton(test_file)
        assert "class MyClass" in res
        assert "Docstring here." in res
        assert "def my_function" in res
        assert "Function docstring." in res
        assert "x = 1" not in res


def test_get_symbol_block():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.py")
        content = """def my_func():
    return 42

class TargetClass:
    def method(self):
        pass
"""
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        res_func = get_symbol_block(test_file, "my_func")
        assert "def my_func():" in res_func
        assert "return 42" in res_func
        assert "TargetClass" not in res_func

        res_class = get_symbol_block(test_file, "TargetClass")
        assert "class TargetClass" in res_class
        assert "def method" in res_class

        with pytest.raises(ValueError):
            get_symbol_block(test_file, "NonExistent")


def test_get_symbols():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.py")
        content = """def my_func():
    return 42

class TargetClass:
    def method(self):
        pass
"""
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        import json
        res = get_symbols(test_file)
        symbols = json.loads(res)
        assert len(symbols) == 3
        
        # Verify symbol properties
        sym_names = [s["name"] for s in symbols]
        assert "my_func" in sym_names
        assert "TargetClass" in sym_names
        assert "method" in sym_names


def test_query_codebase_graph():
    with tempfile.TemporaryDirectory() as temp_dir:
        # File 1 defining a function
        file1 = os.path.join(temp_dir, "def_file.py")
        with open(file1, "w", encoding="utf-8") as f:
            f.write("def helper():\n    pass\n")

        # File 2 referencing the function
        file2 = os.path.join(temp_dir, "ref_file.py")
        with open(file2, "w", encoding="utf-8") as f:
            f.write("from def_file import helper\n\ndef main():\n    helper()\n")

        res = query_codebase_graph("helper", repo_path=temp_dir)
        assert "def_file.py:1 (function definition: helper)" in res
        assert "ref_file.py:1 (import)" in res
        assert "ref_file.py:4 (name_reference)" in res


def test_write_to_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "subdir/new_file.py")
        write_to_file(test_file, "print('hello')")
        assert os.path.exists(test_file)
        with open(test_file, "r") as f:
            assert f.read() == "print('hello')"


def test_replace_file_content():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "edit_test.py")
        content = "line one\nline two\nline three\n"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        # 1. Global replace
        replace_file_content(test_file, "line two", "line modified")
        with open(test_file, "r") as f:
            assert f.read() == "line one\nline modified\nline three\n"

        # 2. Line-restricted replace
        replace_file_content(
            test_file, "line modified", "line restricted", start_line=2, end_line=2
        )
        with open(test_file, "r") as f:
            assert f.read() == "line one\nline restricted\nline three\n"

        # 3. Line-restricted replace where target is not found in range
        with pytest.raises(ValueError):
            replace_file_content(
                test_file, "line restricted", "fail", start_line=1, end_line=1
            )

        # 4. Target not found anywhere
        with pytest.raises(ValueError):
            replace_file_content(test_file, "non_existent_text", "fail")


def test_ts_ast_support():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.ts")
        content = """export function calculateSum(a: number, b: number): number {
    return a + b;
}

export class Calculator {
    multiply(a: number, b: number) {
        return a * b;
    }
}
"""
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        # 1. View AST Skeleton
        skel = get_skeleton(test_file)
        assert "function calculateSum" in skel
        assert "/* ... */" in skel
        assert "class Calculator" in skel
        assert "multiply" in skel

        # 2. View Symbol block for calculateSum
        block_sum = get_symbol_block(test_file, "calculateSum")
        assert "export function calculateSum" in block_sum
        assert "return a + b;" in block_sum

        # 3. View Symbol block for Calculator.multiply
        block_mult = get_symbol_block(test_file, "Calculator.multiply")
        assert "multiply(a: number, b: number)" in block_mult
        assert "return a * b;" in block_mult
