import os
import json
import time
import re
from typing import Dict, Any, Optional

try:
    from google import genai
    from google.genai import types

    _has_google_genai = True
except ImportError:
    _has_google_genai = False

from context_benchmarking.git_manager import GitManager
from context_benchmarking.dataset import DatasetLoader


class CoderAgentSimulator:
    """
    Simulates a coding agent solving software tasks in an isolated Git branch.
    Uses the google-genai SDK to run the agent loop, calling Gemini models
    with bound toolsets for Scenario A (text baseline) or Scenario B (AST-guided).
    Logs all steps to a transcript file and cleans up the workspace upon completion.
    """

    def __init__(self, repo_path: str = ".", model_name: str = "gemini-2.5-flash"):
        """
        Initializes the CoderAgentSimulator.

        Args:
            repo_path: Absolute or relative path to the target repository.
            model_name: The Gemini model name to invoke.
        """
        self.repo_path = os.path.realpath(os.path.abspath(repo_path))
        self.model_name = model_name
        self.git_manager = GitManager(repo_path=self.repo_path)

        if not _has_google_genai:
            raise ImportError(
                "google-genai package is not installed. Please install it using 'uv pip install google-genai'."
            )

        # Initialize the Gemini Client
        # The Client automatically reads GEMINI_API_KEY from environment variables.
        self.client = genai.Client()

    def run_simulation(
        self,
        task_id: str,
        scenario: str,
        transcript_path: str = "transcript.jsonl",
        max_steps: int = 15,
    ) -> Dict[str, Any]:
        """
        Runs the agent coding simulation loop for a given task and scenario.

        Args:
            task_id: Unique task identifier from tasks database.
            scenario: "A" (baseline views) or "B" (AST-guided optimization).
            transcript_path: Path where the step execution log will be written.
            max_steps: Maximum reasoning loop cycles before forced termination.

        Returns:
            Dict[str, Any]: Consolidated execution metrics and test outcomes.
        """
        # 1. Load the task definition using DatasetLoader
        tasks_file = os.path.join(self.repo_path, "data", "tasks.json")
        loader = DatasetLoader(tasks_file_path=tasks_file)
        task = loader.get_task(task_id)

        # 2. Setup run-level metrics tracking structure
        metrics = {
            "task_id": task_id,
            "scenario": scenario.upper(),
            "latency": 0.0,
            "total_tool_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "steps_executed": 0,
            "test_exit_code": -1,
            "test_output": "",
            "success": False,
            "status": "initiated",
        }

        # Clear transcript file if it exists
        abs_transcript = os.path.abspath(transcript_path)
        if os.path.exists(abs_transcript):
            try:
                os.remove(abs_transcript)
            except OSError as e:
                print(f"Warning: Could not remove old transcript file: {e}")

        # 3. Setup workspace isolation branch
        print(f"Setting up branch for task: {task_id}")
        branch_name = self.git_manager.setup_branch(task_id)
        print(f"Checked out isolated task branch: {branch_name}")

        try:
            # 4. Define local tool bindings with current repo path pre-bound
            def grep_search_tool(query: str, path: str) -> str:
                """
                Recursively searches for occurrences of a query string inside files.

                Args:
                    query: The search term.
                    path: Relative or absolute path to search.
                """
                from context_benchmarking.tools import grep_search

                abs_file = os.path.realpath(
                    os.path.abspath(os.path.join(self.repo_path, path))
                )
                try:
                    is_outside = (
                        os.path.commonpath([self.repo_path, abs_file]) != self.repo_path
                    )
                except ValueError:
                    is_outside = not (
                        abs_file.startswith(self.repo_path + os.sep)
                        or abs_file == self.repo_path
                    )
                if is_outside:
                    return f"Error: GrepSearch target path '{path}' is outside repository boundaries."
                return grep_search(query, path, repo_path=self.repo_path)

            def view_file_tool(path: str) -> str:
                """
                Reads file contents with prefixed line numbers.

                Args:
                    path: Path to the target file.
                """
                from context_benchmarking.tools import view_file

                abs_file = os.path.realpath(
                    os.path.abspath(os.path.join(self.repo_path, path))
                )
                try:
                    is_outside = (
                        os.path.commonpath([self.repo_path, abs_file]) != self.repo_path
                    )
                except ValueError:
                    is_outside = not (
                        abs_file.startswith(self.repo_path + os.sep)
                        or abs_file == self.repo_path
                    )
                if is_outside:
                    return f"Error: ViewFile target path '{path}' is outside repository boundaries."
                return view_file(abs_file)

            def get_skeleton(file_path: str) -> str:
                """
                Generates a structural skeleton of a Python or TypeScript/JavaScript file,
                removing function/method bodies but preserving signatures and docstrings/comments.

                Args:
                    file_path: Path to the target source file.
                """
                from context_benchmarking.tools import get_skeleton as get_skel

                abs_file = os.path.realpath(
                    os.path.abspath(os.path.join(self.repo_path, file_path))
                )
                try:
                    is_outside = (
                        os.path.commonpath([self.repo_path, abs_file]) != self.repo_path
                    )
                except ValueError:
                    is_outside = not (
                        abs_file.startswith(self.repo_path + os.sep)
                        or abs_file == self.repo_path
                    )
                if is_outside:
                    return f"Error: Target path '{file_path}' is outside repository boundaries."
                return get_skel(abs_file)

            def get_symbols(file_path: str) -> str:
                """
                List all classes, interfaces, methods, functions, and types in a Python or TypeScript/JavaScript file.
                Returns a JSON array of symbols.

                Args:
                    file_path: Path to the target source file.
                """
                from context_benchmarking.tools import get_symbols as get_syms

                abs_file = os.path.realpath(
                    os.path.abspath(os.path.join(self.repo_path, file_path))
                )
                try:
                    is_outside = (
                        os.path.commonpath([self.repo_path, abs_file]) != self.repo_path
                    )
                except ValueError:
                    is_outside = not (
                        abs_file.startswith(self.repo_path + os.sep)
                        or abs_file == self.repo_path
                    )
                if is_outside:
                    return f"Error: Target path '{file_path}' is outside repository boundaries."
                return get_syms(abs_file)

            def get_symbol_block(file_path: str, symbol_name: str) -> str:
                """
                Retrieve the exact raw source code block for a specific symbol (class, method, or function)
                in a Python or TypeScript/JavaScript file.

                Args:
                    file_path: Path to the target source file.
                    symbol_name: Qualified or short symbol name.
                """
                from context_benchmarking.tools import get_symbol_block as get_sym_block

                abs_file = os.path.realpath(
                    os.path.abspath(os.path.join(self.repo_path, file_path))
                )
                try:
                    is_outside = (
                        os.path.commonpath([self.repo_path, abs_file]) != self.repo_path
                    )
                except ValueError:
                    is_outside = not (
                        abs_file.startswith(self.repo_path + os.sep)
                        or abs_file == self.repo_path
                    )
                if is_outside:
                    return f"Error: Target path '{file_path}' is outside repository boundaries."
                return get_sym_block(abs_file, symbol_name)

            def query_codebase_graph_tool(symbol: str) -> str:
                """
                Maps definitions and imports/call references for a symbol across Python files.

                Args:
                    symbol: Name of the symbol to query.
                """
                from context_benchmarking.tools import query_codebase_graph

                return query_codebase_graph(symbol, repo_path=self.repo_path)

            def write_to_file_tool(path: str, content: str) -> str:
                """
                Writes or overwrites the full content of a target file.

                Args:
                    path: Path of the file to write.
                    content: Text content to write.
                """
                from context_benchmarking.tools import write_to_file

                abs_file = os.path.realpath(
                    os.path.abspath(os.path.join(self.repo_path, path))
                )
                try:
                    is_outside = (
                        os.path.commonpath([self.repo_path, abs_file]) != self.repo_path
                    )
                except ValueError:
                    is_outside = not (
                        abs_file.startswith(self.repo_path + os.sep)
                        or abs_file == self.repo_path
                    )
                if is_outside:
                    return f"Error: WriteToFile target path '{path}' is outside repository boundaries."
                return write_to_file(abs_file, content)

            def replace_file_content_tool(
                path: str, target: str, replacement: str, StartLine: int, EndLine: int
            ) -> str:
                """
                Replaces a specific target code block in a file with replacement content.

                Args:
                    path: Target file path.
                    target: Text block to replace.
                    replacement: Code to insert.
                    StartLine: 1-based start line of replacement block (for analyzer tracking).
                    EndLine: 1-based end line of replacement block (for analyzer tracking).
                """
                from context_benchmarking.tools import replace_file_content

                abs_file = os.path.realpath(
                    os.path.abspath(os.path.join(self.repo_path, path))
                )
                try:
                    is_outside = (
                        os.path.commonpath([self.repo_path, abs_file]) != self.repo_path
                    )
                except ValueError:
                    is_outside = not (
                        abs_file.startswith(self.repo_path + os.sep)
                        or abs_file == self.repo_path
                    )
                if is_outside:
                    return f"Error: ReplaceFileContent target path '{path}' is outside repository boundaries."
                return replace_file_content(
                    abs_file, target, replacement, StartLine, EndLine
                )

            # 5. Select tool list matching Scenario definition
            if scenario.upper() == "A":
                tools = [
                    grep_search_tool,
                    view_file_tool,
                    write_to_file_tool,
                    replace_file_content_tool,
                ]
            elif scenario.upper() == "B":
                tools = [
                    grep_search_tool,
                    get_skeleton,
                    get_symbols,
                    get_symbol_block,
                    query_codebase_graph_tool,
                    write_to_file_tool,
                    replace_file_content_tool,
                ]
            else:
                raise ValueError(
                    f"Invalid Scenario option: '{scenario}'. Must be 'A' or 'B'."
                )

            # 6. Setup prompt configurations
            system_instruction = (
                "You are an expert software developer agent. Your job is to complete the user's task in the repository.\n"
                "You have access to tools for searching, reading, and editing code files.\n"
                "Use them systematically to find the code that needs modification, perform edits, and resolve the requirements.\n"
                "For each step, explain your reasoning in your thoughts, select the tool to invoke, and review the result.\n"
                "When you have completed all edits and believe the task is fully resolved, stop calling tools and provide your final response."
            )

            user_content = (
                f"Task Name: {task.name}\n"
                f"Description: {task.description}\n\n"
                f"Instructions:\n{task.instructions}\n\n"
                f"Files targeted for modification: {', '.join(task.files_to_modify)}\n"
            )

            # Initialize chat history content list
            contents = [
                types.Content(
                    role="user", parts=[types.Part.from_text(text=user_content)]
                )
            ]

            # 7. Execute agent coding loop
            step_idx = 0
            while step_idx < max_steps:
                metrics["steps_executed"] = step_idx + 1

                # Time the API request
                start_time = time.perf_counter()
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            tools=tools,
                            temperature=0.0,
                            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                                disable=True
                            )
                        ),
                    )
                except Exception as e:
                    # Log the API crash as a failed step and propagate
                    self._write_transcript_step(
                        transcript_path=abs_transcript,
                        step_index=step_idx,
                        tool_name=None,
                        args=None,
                        output=f"API Error: {str(e)}",
                        thinking="API call crashed.",
                    )
                    raise

                latency_delta = time.perf_counter() - start_time
                metrics["latency"] += latency_delta

                # Accumulate token usage metrics
                if response.usage_metadata:
                    metrics["input_tokens"] += (
                        response.usage_metadata.prompt_token_count or 0
                    )
                    metrics["output_tokens"] += (
                        response.usage_metadata.candidates_token_count or 0
                    )

                candidate = response.candidates[0]
                model_content = candidate.content

                if model_content is None:
                    finish_reason = getattr(candidate, 'finish_reason', 'UNKNOWN')
                    safety_ratings = getattr(candidate, 'safety_ratings', None)
                    print(f"CRITICAL: model_content is None. Candidate details: finish_reason={finish_reason}, safety={safety_ratings}")
                    try:
                        import pprint
                        print("DEBUG: candidate =")
                        pprint.pprint(candidate)
                    except Exception as de:
                        print("DEBUG: could not print candidate:", de)
                    raise ValueError(f"Model returned empty content (finish_reason: {finish_reason})")

                # Extract reasoning/thinking block
                thinking = self._extract_thinking(model_content)

                # Append model's reply to the message history
                contents.append(model_content)

                # Extract function calls if requested
                function_calls = []
                if model_content.parts:
                    function_calls = [
                        p.function_call for p in model_content.parts if p.function_call
                    ]

                if not function_calls:
                    # No tool calls: Agent declares solution and breaks the loop
                    self._write_transcript_step(
                        transcript_path=abs_transcript,
                        step_index=step_idx,
                        tool_name=None,
                        args=None,
                        output=(
                            model_content.parts[0].text
                            if (model_content.parts and model_content.parts[0].text)
                            else "Simulation finished."
                        ),
                        thinking=thinking,
                    )
                    break

                # Execute tool calls
                tool_response_parts = []
                for fc in function_calls:
                    metrics["total_tool_calls"] += 1

                    tool_name = fc.name
                    tool_args = dict(fc.args) if fc.args else {}

                    # Run the tool and catch errors internally
                    tool_output = self._execute_tool_by_name(
                        tool_name,
                        tool_args,
                        {
                            "grep_search": grep_search_tool,
                            "view_file": view_file_tool,
                            "get_skeleton": get_skeleton,
                            "get_symbols": get_symbols,
                            "get_symbol_block": get_symbol_block,
                            "query_codebase_graph": query_codebase_graph_tool,
                            "write_to_file": write_to_file_tool,
                            "replace_file_content": replace_file_content_tool,
                        },
                    )

                    # Log step to transcript.jsonl
                    self._write_transcript_step(
                        transcript_path=abs_transcript,
                        step_index=step_idx,
                        tool_name=tool_name,
                        args=tool_args,
                        output=tool_output,
                        thinking=thinking,
                    )

                    # Create tool response part
                    tool_response_parts.append(
                        types.Part.from_function_response(
                            name=tool_name, response={"result": tool_output}
                        )
                    )

                # Append tool responses to chat history
                contents.append(types.Content(role="tool", parts=tool_response_parts))

                step_idx += 1

            # 8. Post-loop evaluation: run test suite
            print("Simulation complete. Executing task validation tests...")
            test_results = self.git_manager.run_tests(task_id)
            metrics["test_exit_code"] = test_results.get("exit_code", -1)
            metrics["test_output"] = (
                f"Stdout:\n{test_results.get('stdout', '')}\n\n"
                f"Stderr:\n{test_results.get('stderr', '')}"
            )
            metrics["success"] = test_results.get("exit_code") == 0
            metrics["status"] = "completed"

        except Exception as e:
            metrics["status"] = "failed"
            metrics["test_output"] = f"Simulation Loop Crash Error: {str(e)}"
            raise
        finally:
            # 9. Restore workspace state (clean git checkout base)
            print("Cleaning up workspace and restoring baseline state...")
            self.git_manager.cleanup()

        return metrics

    def _extract_thinking(self, content: types.Content) -> str:
        """
        Robustly extracts model reasoning/thought blocks from GenerateContent parts.
        Handles SDK native thought fields as well as manual tag parsing.
        """
        thoughts = []
        if content and content.parts:
            for part in content.parts:
                # Check for SDK-native thought representation
                if getattr(part, "thought", False) or getattr(part, "reasoning", False):
                    thoughts.append(part.text or "")
                elif part.text:
                    thoughts.append(part.text)

        thinking = "\n".join(thoughts).strip()

        # Regex fallback to extract thoughts enclosed in tags
        tag_match = re.search(r"<thought>(.*?)</thought>", thinking, re.DOTALL)
        if tag_match:
            return tag_match.group(1).strip()

        return thinking

    def _execute_tool_by_name(self, name: str, args: dict, tool_map: dict) -> str:
        """
        Resolves a tool name and runs it safely, capturing exceptions.
        """
        # Resolve mapped tool function (handling suffix variations if necessary)
        tool_fn = tool_map.get(name)
        if not tool_fn:
            # Fallback check for suffix/prefix variations (e.g. view_file_tool)
            for key, fn in tool_map.items():
                if name.startswith(key) or key.startswith(name):
                    tool_fn = fn
                    break

        if not tool_fn:
            return f"Error: Tool '{name}' is not registered."

        try:
            return tool_fn(**args)
        except TypeError as e:
            return f"Error: Invalid arguments for tool '{name}': {str(e)}"
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

    def _write_transcript_step(
        self,
        transcript_path: str,
        step_index: int,
        tool_name: Optional[str],
        args: Optional[dict],
        output: str,
        thinking: str,
    ):
        """
        Writes a standard step log entry into transcript.jsonl.
        Duplicates keys to guarantee schema compatibility with any OfflineAnalyzer variant.
        """
        log_entry = {
            "step_index": step_index,
            # Tool Name Keys
            "tool": tool_name,
            "name": tool_name,
            "action": tool_name,
            # Arguments Keys
            "arguments": args or {},
            "args": args or {},
            "parameters": args or {},
            # Output Keys
            "output": output,
            "content": output,
            "result": output,
            "response": output,
            # Thinking/Reasoning Keys
            "thinking": thinking,
            "thought": thinking,
            "rationale": thinking,
        }

        with open(transcript_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
