#!/usr/bin/env python3
import os
import glob
from pathlib import Path

def compile_context():
    """
    Bootstrap compiler for Forced Context Injection (Phase A).
    Scrapes .agents/rules/ and docs/retrospectives/ to dynamically
    build a monolithic context payload bound to the Architect and Executor.
    """
    root_dir = Path(__file__).resolve().parent.parent

    # 1. Hierarchical Match Rules (Prevent Cross-Domain Glob Collisions)
    # Rank base rules, then infrastructure, then application code to prevent LLM amnesia
    important_rules = [
        root_dir / ".agents" / "rules" / "cli-context-mandate.md",
        root_dir / ".agents" / "rules" / "nextflow-orchestration.md",
        root_dir / ".agents" / "rules" / "infrastructure-as-code.md"
    ]
    all_rules_path = root_dir / ".agents" / "rules" / "*.md"
    other_rule_files = [Path(p) for p in glob.glob(str(all_rules_path)) if Path(p) not in important_rules]
    
    rule_files = [str(p) for p in (important_rules + other_rule_files) if p.exists()]

    # 2. Extract Latest 4 Retrospectives
    retros_path = root_dir / "docs" / "retrospectives" / "*.md"
    retro_files = sorted(glob.glob(str(retros_path)), reverse=True)[:4]

    compiled_payload = "### INJECTED CONTEXT AXIOMS ###\n\n"

    for filepath in retro_files + rule_files:
        with open(filepath, 'r') as f:
            compiled_payload += f"==== {Path(filepath).name} ====\n"
            compiled_payload += f.read() + "\n\n"

    # Export to the Telemetry Bus (which is RO for Architect, RW for Executor)
    output_target = root_dir / ".agents" / "compiled_context.md"
    with open(output_target, "w") as out:
        out.write(compiled_payload)
    print(f"Context successfully compiled to {output_target}")

if __name__ == "__main__":
    compile_context()
