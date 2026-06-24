import ast
import re
import os
import json
from typing import List, Dict, Any, Optional

try:
    import tiktoken

    _has_tiktoken = True
except ImportError:
    _has_tiktoken = False


class TokenReadEvent:
    def __init__(
        self,
        file_path: str,
        scenario_a_tokens: int,
        scenario_b_tokens: int,
        is_python: bool,
        inspected_symbols: List[str] = None,
    ):
        self.file_path = file_path
        self.scenario_a_tokens = scenario_a_tokens
        self.scenario_b_tokens = scenario_b_tokens
        self.savings_tokens = scenario_a_tokens - scenario_b_tokens
        self.is_python = is_python
        self.inspected_symbols = inspected_symbols or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "scenario_a_tokens": self.scenario_a_tokens,
            "scenario_b_tokens": self.scenario_b_tokens,
            "savings_tokens": self.savings_tokens,
            "is_python": self.is_python,
            "inspected_symbols": self.inspected_symbols,
        }


class TokenSavingsReport:
    def __init__(self, events: List[TokenReadEvent]):
        self.events = events
        self.total_scenario_a_tokens = sum(e.scenario_a_tokens for e in events)
        self.total_scenario_b_tokens = sum(e.scenario_b_tokens for e in events)
        self.total_savings_tokens = (
            self.total_scenario_a_tokens - self.total_scenario_b_tokens
        )
        if self.total_scenario_a_tokens > 0:
            self.savings_percentage = (
                self.total_savings_tokens / self.total_scenario_a_tokens
            ) * 100.0
        else:
            self.savings_percentage = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "events": [e.to_dict() for e in self.events],
            "total_scenario_a_tokens": self.total_scenario_a_tokens,
            "total_scenario_b_tokens": self.total_scenario_b_tokens,
            "total_savings_tokens": self.total_savings_tokens,
            "savings_percentage": self.savings_percentage,
        }

    def to_markdown(self) -> str:
        lines = []
        lines.append(
            "| File Path | Type | Scenario A (Full) | Scenario B (Opt) | Savings | % Savings | Inspected Symbols |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for e in self.events:
            pct = (
                (e.savings_tokens / e.scenario_a_tokens * 100)
                if e.scenario_a_tokens > 0
                else 0.0
            )
            ftype = "Python" if e.is_python else "Other"
            syms = ", ".join(e.inspected_symbols) if e.inspected_symbols else "-"
            lines.append(
                f"| {e.file_path} | {ftype} | {e.scenario_a_tokens} | {e.scenario_b_tokens} | {e.savings_tokens} | {pct:.1f}% | {syms} |"
            )

        lines.append(
            f"| **Total** | - | **{self.total_scenario_a_tokens}** | **{self.total_scenario_b_tokens}** | **{self.total_savings_tokens}** | **{self.savings_percentage:.1f}%** | - |"
        )
        return "\n".join(lines)


class SkeletonTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        docstring = ast.get_docstring(node)
        new_body = []
        if docstring is not None:
            new_body.append(ast.Expr(value=ast.Constant(value=docstring)))
        new_body.append(ast.Pass())
        node.body = new_body
        return node

    def visit_AsyncFunctionDef(self, node):
        docstring = ast.get_docstring(node)
        new_body = []
        if docstring is not None:
            new_body.append(ast.Expr(value=ast.Constant(value=docstring)))
        new_body.append(ast.Pass())
        node.body = new_body
        return node

    def visit_ClassDef(self, node):
        docstring = ast.get_docstring(node)
        new_body = []
        if docstring is not None:
            new_body.append(ast.Expr(value=ast.Constant(value=docstring)))

        preserved_children = []
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visited_child = self.visit(child)
                if visited_child is not None:
                    preserved_children.append(visited_child)

        new_body.extend(preserved_children)
        if not preserved_children:
            new_body.append(ast.Pass())

        node.body = new_body
        return node


class OfflineAnalyzer:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)

    def _paths_match(self, p1: str, p2: str) -> bool:
        if not p1 or not p2:
            return False
        norm1 = os.path.normpath(p1)
        norm2 = os.path.normpath(p2)
        if norm1 == norm2:
            return True
        abs1 = (
            norm1
            if os.path.isabs(norm1)
            else os.path.normpath(os.path.join(self.repo_path, norm1))
        )
        abs2 = (
            norm2
            if os.path.isabs(norm2)
            else os.path.normpath(os.path.join(self.repo_path, norm2))
        )
        if abs1 == abs2:
            return True
        if not os.path.isabs(norm2):
            suffix = norm2.replace(os.sep, "/")
            abs_path_str = abs1.replace(os.sep, "/")
            if abs_path_str.endswith("/" + suffix) or abs_path_str == suffix:
                return True
        if not os.path.isabs(norm1):
            suffix = norm1.replace(os.sep, "/")
            abs_path_str = abs2.replace(os.sep, "/")
            if abs_path_str.endswith("/" + suffix) or abs_path_str == suffix:
                return True
        return False

    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        if _has_tiktoken:
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(text))
            except Exception:
                pass
        return int(len(text) / 3.8)

    def generate_ast_skeleton(self, code: str, file_path: Optional[str] = None) -> str:
        # Determine extension if file_path is provided
        ext = ""
        if file_path:
            _, ext = os.path.splitext(file_path.lower())

        # Route based on extension if known
        if ext == ".json":
            return self._generate_json_skeleton(code)
        elif ext == ".md":
            return self._generate_markdown_skeleton(code)
        elif ext in (".js", ".ts"):
            return self._generate_js_ts_skeleton(code)
        elif ext == ".py":
            try:
                return self._generate_python_skeleton(code)
            except SyntaxError:
                pass

        # Heuristics fallback if extension is unknown/unsupported
        stripped = code.strip()
        if (stripped.startswith("{") and stripped.endswith("}")) or (
            stripped.startswith("[") and stripped.endswith("]")
        ):
            return self._generate_json_skeleton(code)

        # Check if it looks like python first
        if (
            "def " in code
            or "class " in code
            or "import " in code
            or "from " in code
            or " = " in code
        ):
            try:
                return self._generate_python_skeleton(code)
            except SyntaxError:
                pass

        # Check if it looks like markdown (e.g. starts with '# ' or has multiple hashes followed by space)
        if any(
            line.strip().startswith("# ") or line.strip().startswith("##")
            for line in code.splitlines()[:10]
        ):
            return self._generate_markdown_skeleton(code)

        # Fallback to Python AST, and if that fails, JS/TS regex
        try:
            return self._generate_python_skeleton(code)
        except SyntaxError:
            return self._generate_js_ts_skeleton(code)

    def _generate_json_skeleton(self, code: str) -> str:
        try:
            obj = json.loads(code)

            def json_skeleton(o):
                if isinstance(o, dict):
                    return {k: json_skeleton(v) for k, v in o.items()}
                elif isinstance(o, list):
                    if len(o) > 0:
                        return [json_skeleton(o[0]), "..."]
                    return []
                else:
                    return "..."

            skeleton_obj = json_skeleton(obj)
            return json.dumps(skeleton_obj, indent=2)
        except Exception:
            return "{}"

    def _generate_markdown_skeleton(self, code: str) -> str:
        headers = [line for line in code.splitlines() if line.strip().startswith("#")]
        return "\n".join(headers)

    def _generate_js_ts_skeleton(self, code: str) -> str:
        import re

        class_pat = re.compile(r"\bclass\s+[a-zA-Z0-9_$]+")
        func_pat = re.compile(r"\bfunction\s*[a-zA-Z0-9_$]*\s*\(")
        interface_pat = re.compile(r"\binterface\s+[a-zA-Z0-9_$]+")
        arrow_pat = re.compile(r"\b(const|let|var|export)\b.*=>")
        method_pat = re.compile(
            r"^\s*(?:async\s+)?(?:public\s+|private\s+|protected\s+|static\s+)?(?:get\s+|set\s+)?"
            r"(?!(?:if|for|while|switch|catch|return|super|require|import|export)\b)([a-zA-Z0-9_$]+)\s*\([^)]*\)\s*"
            r"(?::\s*[^{;]+)?\s*\{?$"
        )
        skeleton_lines = []
        for line in code.splitlines():
            trimmed = line.strip()
            if (
                class_pat.search(trimmed)
                or func_pat.search(trimmed)
                or interface_pat.search(trimmed)
                or arrow_pat.search(trimmed)
                or method_pat.match(line)
            ):
                skeleton_lines.append(line)
        return "\n".join(skeleton_lines)

    def _generate_python_skeleton(self, code: str) -> str:
        tree = ast.parse(code)
        transformer = SkeletonTransformer()
        modified_tree = transformer.visit(tree)
        ast.fix_missing_locations(modified_tree)
        return ast.unparse(modified_tree)

    def extract_symbols(self, code: str) -> List[Dict[str, Any]]:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        class SymbolVisitor(ast.NodeVisitor):
            def __init__(self):
                self.symbols = []
                self.class_stack = []

            def visit_ClassDef(self, node):
                self.class_stack.append(node.name)
                fq_name = ".".join(self.class_stack)
                self.symbols.append(
                    {
                        "name": node.name,
                        "qname": fq_name,
                        "type": "class",
                        "start_line": node.lineno,
                        "end_line": getattr(node, "end_lineno", node.lineno),
                    }
                )
                self.generic_visit(node)
                self.class_stack.pop()

            def visit_FunctionDef(self, node):
                fq_name = ".".join(self.class_stack + [node.name])
                self.symbols.append(
                    {
                        "name": node.name,
                        "qname": fq_name,
                        "type": "function",
                        "start_line": node.lineno,
                        "end_line": getattr(node, "end_lineno", node.lineno),
                    }
                )
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                fq_name = ".".join(self.class_stack + [node.name])
                self.symbols.append(
                    {
                        "name": node.name,
                        "qname": fq_name,
                        "type": "function",
                        "start_line": node.lineno,
                        "end_line": getattr(node, "end_lineno", node.lineno),
                    }
                )
                self.generic_visit(node)

        visitor = SymbolVisitor()
        visitor.visit(tree)
        visitor.symbols.sort(key=lambda s: s["start_line"])
        return visitor.symbols

    def get_symbol_block(self, code: str, symbol_name: str) -> Optional[str]:
        symbols = self.extract_symbols(code)
        for sym in symbols:
            if sym.get("qname") == symbol_name:
                lines = code.splitlines()
                start = sym["start_line"] - 1
                end = sym["end_line"]
                start = max(0, start)
                end = min(len(lines), end)
                return "\n".join(lines[start:end])
        for sym in symbols:
            if sym["name"] == symbol_name:
                lines = code.splitlines()
                start = sym["start_line"] - 1
                end = sym["end_line"]
                start = max(0, start)
                end = min(len(lines), end)
                return "\n".join(lines[start:end])
        return None

    def reconstruct_file_from_view_output(self, view_output: str) -> str:
        lines_list = view_output.splitlines()
        matched_nums = []
        matched_contents = []
        pattern = re.compile(r"^\s*(\d+): ?(.*)$")

        for line in lines_list:
            match = pattern.match(line)
            if match:
                matched_nums.append(int(match.group(1)))
                content = match.group(2)
                matched_contents.append(content if content is not None else "")

        total_non_empty = sum(1 for line in lines_list if line.strip() != "")
        density = (len(matched_nums) / total_non_empty) if total_non_empty > 0 else 0.0

        increasing = all(
            matched_nums[i] < matched_nums[i + 1] for i in range(len(matched_nums) - 1)
        )

        if len(matched_nums) <= 1:
            mostly_sequential = True
        else:
            diff_one_count = sum(
                1
                for i in range(len(matched_nums) - 1)
                if (matched_nums[i + 1] - matched_nums[i]) == 1
            )
            mostly_sequential = (diff_one_count / (len(matched_nums) - 1)) >= 0.8

        if density >= 0.7 and increasing and mostly_sequential:
            return "\n".join(matched_contents)
        else:
            return view_output

    def parse_transcript(self, transcript_path: str) -> TokenSavingsReport:
        try:
            cleaned_path = transcript_path.strip("'\"")
            if not os.path.exists(cleaned_path):
                alt_path = os.path.join(self.repo_path, cleaned_path)
                if os.path.exists(alt_path):
                    cleaned_path = alt_path
                else:
                    raise FileNotFoundError(
                        f"Transcript file not found: {cleaned_path}"
                    )

            with open(cleaned_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            try:
                data = json.loads(content)
                if isinstance(data, list):
                    steps = data
                elif isinstance(data, dict):
                    found_list = False
                    for key in ["steps", "events", "logs", "history", "actions"]:
                        if key in data and isinstance(data[key], list):
                            steps = data[key]
                            found_list = True
                            break
                    if not found_list:
                        steps = [data]
                else:
                    steps = []
            except json.JSONDecodeError:
                steps = []
                for line in content.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        steps.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        except Exception:
            return TokenSavingsReport([])

        events = []
        for i, step in enumerate(steps):
            try:
                tool_name = (
                    step.get("tool") or step.get("name") or step.get("action") or ""
                )
                if not isinstance(tool_name, str):
                    tool_name = str(tool_name)

                # Check if this step is a view, read, or get_skeleton/get_symbols/get_symbol_block tool call
                if not (
                    "view" in tool_name
                    or "read" in tool_name
                    or "show" in tool_name
                    or "get_file" in tool_name
                    or "get_skeleton" in tool_name
                    or "get_symbols" in tool_name
                    or "get_symbol_block" in tool_name
                ):
                    continue

                args = (
                    step.get("arguments")
                    or step.get("parameters")
                    or step.get("args")
                    or {}
                )
                if not isinstance(args, dict):
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {"path": args}
                    else:
                        args = {}

                file_path = None
                for path_key in [
                    "AbsolutePath",
                    "TargetFile",
                    "path",
                    "file",
                    "filename",
                    "file_path",
                ]:
                    if path_key in args and isinstance(args[path_key], str):
                        file_path = args[path_key].strip("'\"")
                        break

                if not file_path:
                    continue

                norm_file_path = os.path.normpath(file_path)

                output = (
                    step.get("output")
                    or step.get("result")
                    or step.get("response")
                    or step.get("content")
                    or ""
                )
                if not isinstance(output, str):
                    output = str(output)

                clean_code = self.reconstruct_file_from_view_output(output)
                if not clean_code.strip() and output.strip():
                    clean_code = output

                _, ext = os.path.splitext(norm_file_path.lower())
                is_python = ext == ".py"
                has_skeleton = ext in (".py", ".js", ".ts", ".json", ".md")

                scenario_a_tokens = self.count_tokens(clean_code)
                inspected_symbols = []

                if has_skeleton:
                    skeleton_code = self.generate_ast_skeleton(
                        clean_code, file_path=norm_file_path
                    )
                    skeleton_cost = self.count_tokens(skeleton_code)

                    subsequent_steps = steps[i + 1 :]
                    subsequent_edits = []
                    for s_step in subsequent_steps:
                        s_args = (
                            s_step.get("arguments")
                            or s_step.get("parameters")
                            or s_step.get("args")
                            or {}
                        )
                        if not isinstance(s_args, dict):
                            continue
                        s_file_path = None
                        for path_key in [
                            "TargetFile",
                            "AbsolutePath",
                            "path",
                            "file",
                            "filename",
                            "file_path",
                        ]:
                            if path_key in s_args and isinstance(s_args[path_key], str):
                                s_file_path = s_args[path_key].strip("'\"")
                                break
                        if s_file_path and self._paths_match(
                            s_file_path, norm_file_path
                        ):
                            s_tool = (
                                s_step.get("tool")
                                or s_step.get("name")
                                or s_step.get("action")
                                or ""
                            )
                            if not isinstance(s_tool, str):
                                s_tool = str(s_tool)
                            if (
                                "replace_file_content" in s_tool
                                or "edit" in s_tool
                                or "patch" in s_tool
                            ):
                                start = s_args.get("StartLine")
                                end = s_args.get("EndLine")
                                if start is not None and end is not None:
                                    try:
                                        subsequent_edits.append((int(start), int(end)))
                                    except (ValueError, TypeError):
                                        pass
                                chunks = s_args.get("ReplacementChunks")
                                if isinstance(chunks, list):
                                    for chunk in chunks:
                                        if isinstance(chunk, dict):
                                            c_start = chunk.get("StartLine")
                                            c_end = chunk.get("EndLine")
                                            if (
                                                c_start is not None
                                                and c_end is not None
                                            ):
                                                try:
                                                    subsequent_edits.append(
                                                        (int(c_start), int(c_end))
                                                    )
                                                except (ValueError, TypeError):
                                                    pass
                            elif "write_to_file" in s_tool:
                                subsequent_edits.append((1, 999999))

                    if is_python:
                        all_symbols = self.extract_symbols(clean_code)

                        thinking_texts = []
                        for s in steps:
                            for thinking_key in ["thinking", "thought", "rationale"]:
                                txt = s.get(thinking_key)
                                if isinstance(txt, str) and txt:
                                    thinking_texts.append(txt)
                        combined_thinking = "\n".join(thinking_texts)

                        mentioned_symbols = set()
                        for sym in all_symbols:
                            name = sym["name"]
                            qname = sym.get("qname", name)
                            if re.search(
                                r"\b" + re.escape(name) + r"\b", combined_thinking
                            ) or re.search(
                                r"\b" + re.escape(qname) + r"\b", combined_thinking
                            ):
                                mentioned_symbols.add(qname)

                        raw_inspected_symbols = []
                        for sym in all_symbols:
                            name = sym["name"]
                            qname = sym.get("qname", name)
                            is_inspected = False
                            if qname in mentioned_symbols:
                                is_inspected = True
                            else:
                                for start_e, end_e in subsequent_edits:
                                    if max(sym["start_line"], start_e) <= min(
                                        sym["end_line"], end_e
                                    ):
                                        is_inspected = True
                                        break
                            if is_inspected:
                                raw_inspected_symbols.append(name)
                                if qname != name:
                                    raw_inspected_symbols.append(qname)

                        # Store all inspected symbols
                        inspected_symbols = raw_inspected_symbols

                        if inspected_symbols:
                            # Avoid double-counting of nested/overlapping symbols by range merging
                            ranges = []
                            for sym in all_symbols:
                                qname = sym.get("qname", sym["name"])
                                if qname in inspected_symbols:
                                    ranges.append((sym["start_line"], sym["end_line"]))

                            ranges.sort(key=lambda r: r[0])
                            merged_ranges = []
                            for start, end in ranges:
                                if not merged_ranges:
                                    merged_ranges.append([start, end])
                                else:
                                    last_start_val, last_end_val = merged_ranges[-1]
                                    if start <= last_end_val + 1:
                                        merged_ranges[-1][1] = max(last_end_val, end)
                                    else:
                                        merged_ranges.append([start, end])

                            lines = clean_code.splitlines()
                            inspected_parts = []
                            for start, end in merged_ranges:
                                s_idx = max(0, start - 1)
                                e_idx = min(len(lines), end)
                                inspected_parts.append("\n".join(lines[s_idx:e_idx]))

                            symbols_cost = self.count_tokens("\n".join(inspected_parts))
                            scenario_b_tokens = skeleton_cost + symbols_cost
                        else:
                            top_level_symbols = []
                            try:
                                tree = ast.parse(clean_code)
                                for node in tree.body:
                                    if isinstance(
                                        node,
                                        (
                                            ast.FunctionDef,
                                            ast.AsyncFunctionDef,
                                            ast.ClassDef,
                                        ),
                                    ):
                                        top_level_symbols.append(node.name)
                            except Exception:
                                pass

                            symbol_sizes = []
                            for sym in top_level_symbols:
                                block = self.get_symbol_block(clean_code, sym)
                                if block:
                                    symbol_sizes.append(self.count_tokens(block))

                            if symbol_sizes:
                                scenario_b_tokens = int(
                                    sum(symbol_sizes) / len(symbol_sizes)
                                )
                            else:
                                scenario_b_tokens = int(0.2 * scenario_a_tokens)
                    else:
                        # Non-python files with skeleton support (JS, TS, JSON, MD)
                        if subsequent_edits:
                            subsequent_edits.sort(key=lambda r: r[0])
                            merged_edits = []
                            for start, end in subsequent_edits:
                                if not merged_edits:
                                    merged_edits.append([start, end])
                                else:
                                    last_start_val, last_end_val = merged_edits[-1]
                                    if start <= last_end_val + 1:
                                        merged_edits[-1][1] = max(last_end_val, end)
                                    else:
                                        merged_edits.append([start, end])

                            lines = clean_code.splitlines()
                            edited_code_parts = []
                            for start_e, end_e in merged_edits:
                                start_idx = max(0, start_e - 1)
                                end_idx = min(len(lines), end_e)
                                edited_code_parts.append(
                                    "\n".join(lines[start_idx:end_idx])
                                )

                            edited_cost = self.count_tokens(
                                "\n".join(edited_code_parts)
                            )
                            scenario_b_tokens = skeleton_cost + edited_cost
                        else:
                            scenario_b_tokens = skeleton_cost
                else:
                    scenario_b_tokens = scenario_a_tokens
                    inspected_symbols = []

                scenario_b_tokens = min(scenario_b_tokens, scenario_a_tokens)
                scenario_b_tokens = int(scenario_b_tokens)

                events.append(
                    TokenReadEvent(
                        file_path=file_path,
                        scenario_a_tokens=scenario_a_tokens,
                        scenario_b_tokens=scenario_b_tokens,
                        is_python=is_python,
                        inspected_symbols=inspected_symbols,
                    )
                )
            except Exception:
                pass

        return TokenSavingsReport(events)
