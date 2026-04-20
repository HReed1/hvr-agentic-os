#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
build_llms_txt.py – produce llms.txt and llms-full.txt for ngs-variant-validator
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys
import textwrap
from datetime import datetime
from typing import List
from typing import Tuple
import urllib.error
import urllib.request

RE_JAVA = re.compile(r"```java[ \t\r\n][\s\S]*?```", re.I | re.M)
RE_SNIPPET = re.compile(r"^(\s*)--8<--\s+\"([^\"]+?)(?::([^\"]+))?\"$", re.M)

GITHUB_BASE = "https://github.com/HReed1/ngs-variant-validator/blob/main"

def strip_java(md: str) -> str:
  return RE_JAVA.sub("", md)


def first_heading(md: str) -> str | None:
  for line in md.splitlines():
    if line.startswith("#"):
      return line.lstrip("#").strip()
  return None


def md_to_text(md: str) -> str:
  try:
    import bs4
    import markdown
  except ImportError:
    # Fallback if libraries are missing
    return md

  html = markdown.markdown(
      md, extensions=["fenced_code", "tables", "attr_list"]
  )
  return bs4.BeautifulSoup(html, "html.parser").get_text("\n")


def count_tokens(text: str, model: str = "cl100k_base") -> int:
  try:
    import tiktoken
    return len(tiktoken.get_encoding(model).encode(text))
  except Exception:
    return len(text.split())


def get_file_sort_key(p: Path) -> float:
  """
  Extracts timestamp from YYYY-MM-DD prefix if available, 
  falling back to physical file creation time (macOS st_birthtime).
  """
  match = re.match(r"^(\d{4}-\d{2}-\d{2})", p.name)
  if match:
    try:
      return datetime.strptime(match.group(1), "%Y-%m-%d").timestamp()
    except ValueError:
      pass
  stat = p.stat()
  return getattr(stat, "st_birthtime", stat.st_ctime)


def expand_code_snippets(content: str, project_root: Path) -> str:
  """
  Expands code snippets marked with --8<-- "path/to/file.py" or
  --8<-- "path/to/file.py:section_name" into the content.
  """

  def replace_snippet(match):
    indent = match.group(1)
    snippet_path_str = match.group(2)
    section_name = match.group(3)
    snippet_full_path = project_root / snippet_path_str

    if snippet_full_path.exists():
      try:
        file_content = snippet_full_path.read_text(encoding="utf-8")
        if section_name:
          # Extract content based on section markers
          start_marker_patterns = [
              f"# --8<-- [start:{section_name.strip()}]",
              f"## --8<-- [start:{section_name.strip()}]",
          ]
          end_marker_patterns = [
              f"# --8<-- [end:{section_name.strip()}]",
              f"## --8<-- [end:{section_name.strip()}]",
          ]

          start_index = -1
          end_index = -1

          for pattern in start_marker_patterns:
            start_index = file_content.find(pattern)
            if start_index != -1:
              start_marker = pattern
              break

          for pattern in end_marker_patterns:
            end_index = file_content.find(pattern)
            if end_index != -1:
              break

          if start_index != -1 and end_index != -1 and start_index < end_index:
            start_of_code = start_index + len(start_marker)
            temp_content = file_content[start_of_code:end_index]
            lines = temp_content.splitlines(keepends=True)
            extracted_lines = []
            for line in lines:
              if not line.strip().startswith(("# --8<--", "## --8<--")) and line.strip() != "":
                extracted_lines.append(line)
            extracted_content = "".join(extracted_lines).strip("\n")
            return textwrap.indent(extracted_content, indent)
        else:
          return textwrap.indent(file_content, indent)
      except Exception as e:
        return match.group(0)
    return match.group(0)

  return RE_SNIPPET.sub(replace_snippet, content)


def build_index(docs_dir: Path, project_root: Path) -> str:
  # Locate README
  readme_path = project_root / "README.md"
  if readme_path.exists():
    readme = readme_path.read_text(encoding="utf-8")
  else:
    readme = "# ngs-variant-validator"

  title = first_heading(readme) or "ngs-variant-validator Documentation"
  summary = md_to_text(readme).split("\n\n")[0]
  lines = [f"# {title}", "", f"> {summary}", ""]

  primary: List[Tuple[str, str]] = []

  # Process Markdown files
  md_files = []
  for root, dirs, files in os.walk(str(docs_dir), followlinks=True):
    for f in files:
      if f.endswith(".md"):
        md_files.append(Path(root) / f)

  # Sort by YYYY-MM-DD prefix, falling back to physical creation time
  md_files.sort(key=get_file_sort_key)

  for md in md_files:
    rel = md.relative_to(docs_dir)
    actual_path = md.resolve()
    try:
      rel_to_root = actual_path.relative_to(project_root.resolve())
    except ValueError:
      rel_to_root = rel # Fallback

    url = f"{GITHUB_BASE}/{rel_to_root}".replace(" ", "%20")
    h = first_heading(strip_java(md.read_text(encoding="utf-8"))) or rel.stem
    primary.append((h, url))

  if primary:
    lines.append("## Documentation")
    lines += [f"- [{h}]({u})" for h, u in primary]
    lines.append("")

  return "\n".join(lines)


def build_full(docs_dir: Path, project_root: Path) -> str:
  out = []

  # Add root README
  readme_path = project_root / "README.md"
  if readme_path.exists():
    out.append("# README")
    out.append("")
    out.append(expand_code_snippets(strip_java(readme_path.read_text(encoding="utf-8")), project_root))
    out.append("")
    out.append("---")
    out.append("")

  # Process Markdown files
  md_files = []
  for root, dirs, files in os.walk(str(docs_dir), followlinks=True):
    for f in files:
      if f.endswith(".md"):
        md_files.append(Path(root) / f)

  # Sort by YYYY-MM-DD prefix, falling back to physical creation time
  md_files.sort(key=get_file_sort_key)

  for md in md_files:
    # Avoid duplicating the root README if it was symlinked into docs_dir
    actual_path = md.resolve()
    if actual_path == (project_root / "README.md").resolve():
        continue

    md_content = md.read_text(encoding="utf-8")
    expanded_md_content = expand_code_snippets(strip_java(md_content), project_root)
    out.append(expanded_md_content)

  return "\n\n".join(out)


def main() -> None:
  ap = argparse.ArgumentParser(description="Generate llms.txt / llms-full.txt")
  ap.add_argument("--docs-dir", required=True, type=Path)
  ap.add_argument("--project-root", required=True, type=Path)
  ap.add_argument("--out-root", default=Path("."), type=Path)
  args = ap.parse_args()

  idx = build_index(args.docs_dir, args.project_root)
  full = build_full(args.docs_dir, args.project_root)

  (args.out_root / "llms.txt").write_text(idx, encoding="utf-8")
  (args.out_root / "llms-full.txt").write_text(full, encoding="utf-8")
  print("✅ Generated llms.txt and llms-full.txt successfully")


if __name__ == "__main__":
  main()
