#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0.1",
# ]
# ///
"""Project Bootstrapper Master Orchestrator CLI.

Coordinates the end-to-end scaffolding, customization, and verification of a project workspace:
1. Universal + Archetype Directory Structure (Mode 0755)
2. Obsidian Vault Settings and Archetype Markdown Templates
3. Two-Tier Governance Architecture (AGENTS.md, Copilot Instructions, rules/)
4. 3-Tier Cadence Goal Engine (scripts/cadence.py with SQLite or Firestore)
5. Pluggable Wiki Pipeline (scripts/export_wiki.py and sync_wiki_db.py with SQLite or PostgreSQL)
6. Drift Registries and Enforcer (docs/drift_registries/, scripts/drift_enforcer.py)
7. Session Rituals (.agents/skills/ or .github/prompts/)
8. Archetype-Aware 9-Layer Verification Harness and Unit Tests
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Dict

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PLUGIN_ROOT / "skills"

VALID_ARCHETYPES = [
    "creative_operations",
    "software_engineering",
    "agentic_os",
    "data_platform",
    "minimal_research",
]

VALID_FLAVORS = [
    "antigravity",
    "copilot",
    "universal",
]

DEFAULT_PHASES = {
    "creative_operations": "ingest_sync",
    "software_engineering": "discovery",
    "agentic_os": "spec",
    "data_platform": "ingest",
    "minimal_research": "literature_review",
}

NEXT_PHASES = {
    "creative_operations": "rough_cut",
    "software_engineering": "design",
    "agentic_os": "prompt_eng",
    "data_platform": "validation",
    "minimal_research": "hypothesis",
}

DOMAIN_INVARIANTS = {
    "creative_operations": """### Storage & Media Preservation Invariants (The Non-Negotiable Core)
1. **Zero-Mutation Invariant (On-Disk Data Remains 100% Untouched):** Observability and organization are strictly virtual. External volumes (`/Volumes/*`) and cloud storage (`~/Library/CloudStorage/*`) are strictly read-only. Scripts and agents are forbidden from executing `mv`, `rm`, `mkdir`, `touch`, `rsync`, or in-place reorganization on audited media volumes. All taxonomy is tracked in `ledger/`.
2. **Zero-Byte-Shift & Cloud Non-Hydration Invariant:** Never write temp files, audit logs, or metadata to target storage volumes. When inspecting macOS FileProvider cloud repositories (Dropbox, Google Drive), never run commands (`du -sh`, `file`, `xxh64sum`, `md5`, `ffprobe`) that trigger on-demand hydration of cloud stubs.
3. **Master Asset Immutability & 3-2-1 Data Law:** Raw camera originals and project files are strictly read-only. Critical assets must exist in 3 copies across 2 media types with 1 copy offsite. Assets on a single drive must be flagged as unbacked.
4. **Destructive Action Firewall:** Automated batch deletions or volume formatting are strictly prohibited.""",
    "software_engineering": """### Software Engineering & System Security Invariants
1. **API & Webhook Zero-Trust:** All webhook handlers MUST use HMAC-SHA256 with timing-safe comparison (`hmac.compare_digest`). Never use `==` for signature or token checks.
2. **Webhook Replay Protection:** Endpoints and expensive mutations must deduplicate requests deterministically via persistent unique identifiers before execution.
3. **No Committed Secrets:** Secrets are injected at runtime via Secret Manager or environment variables. No `.env` files in production or committed to source control.
4. **Frontend DOM Sanitization (XSS Prevention):** Untrusted or external content must pass through robust sanitization (`DOMPurify`) before rendering into the DOM.
5. **CI/CD Hygiene:** Passing typechecks, lint, and unit test suites are mandatory gates before release.""",
    "agentic_os": """### Autonomous Agent Firewalling & Sandboxing Invariants
1. **Agent Write Budgets & Quotas:** All mutation-capable agents must operate under strict inference write budgets and execution quotas. Unbounded agent loops fail closed.
2. **Prompt Injection Defense:** Dedicated `system_instruction` configuration separation. Untrusted external data is treated strictly as payload content within user blocks.
3. **Tool Sandboxing & Collection Allow-Listing:** Agents may only write to explicitly authorized database collections and directories. Destructive actions require explicit human confirmation.
4. **Deterministic Task Idempotency:** State management uses dynamic UUIDs and deduplication to prevent replay or cross-session state corruption.""",
    "data_platform": """### Data Platform & Lineage Invariants
1. **Raw Store Immutability:** Raw data partitions and bronze tables are strictly read-only. All transformations produce versioned derived datasets.
2. **Privacy & Compliance (PII/PHI):** Personal Identifiable Information and Protected Health Information must be anonymized, hashed, or redacted prior to downstream storage.
3. **Pipeline Idempotency & Schema Validation:** Pipeline tasks must produce deterministic, reproducible outputs from identical inputs. All inputs/outputs must adhere to declared schemas.""",
    "minimal_research": """### Research & Knowledge Synthesis Invariants
1. **Source Layer Immutability:** Documents in `docs/` and `raw/` are human-authored or external sources: READ ONLY — never modify. The agent maintains `wiki/` and `notes/`.
2. **Strict Claims Attribution:** Every claim, definition, or synthesis document must trace back to an attributable source. Contradictions must be explicitly surfaced.""",
}

DOMAIN_RULES_LIST = {
    "creative_operations": """* `.agents/rules/media-preservation.md`: Zero-mutation and virtual taxonomy.
* `.agents/rules/non-hydration.md`: FileProvider cloud stub preservation.
* `.agents/rules/asset-immutability.md`: Raw master immutability and 3-2-1 backup law.""",
    "software_engineering": """* `.agents/rules/api-zero-trust.md`: HMAC timing-safe verification and replay protection.
* `.agents/rules/secrets-management.md`: Credential governance and runtime secret injection.
* `.agents/rules/frontend-governance.md`: DOM sanitization and UI tokens.
* `.agents/rules/cicd-hygiene.md`: Lint, test, and build validation gates.""",
    "agentic_os": """* `.agents/rules/agent-firewalling.md`: Mutation write budgets and rate limits.
* `.agents/rules/prompt-injection-defense.md`: System instruction separation and payload isolation.
* `.agents/rules/tool-sandboxing.md`: Scoped permissions and destructive action firewalls.
* `.agents/rules/deterministic-state.md`: State tokens and task idempotency.""",
    "data_platform": """* `.agents/rules/data-immutability.md`: Raw source immutability and lineage tracking.
* `.agents/rules/privacy-compliance.md`: PII/PHI redaction and access auditing.
* `.agents/rules/pipeline-idempotency.md`: Deterministic transforms and schema validation.""",
    "minimal_research": """* `.agents/rules/source-layer-immutability.md`: Read-only source layers.
* `.agents/rules/citation-governance.md`: Strict attribution and contradiction surfacing.""",
}

ARCHITECTURE_COMPONENTS = {
    "creative_operations": """- **Master Ledgers (`ledger/`):** Clean zero-state production catalogs (`drives.yaml`, `projects.yaml`, `assets.yaml`).
- **Creative Projects (`projects/`) & Syncs (`meetings/`):** Project workspaces and Saturday review notes.""",
    "software_engineering": """- **Source Code (`src/`, `api/`):** Application codebase, endpoints, and frontend components.
- **Automated Tests (`tests/`):** Unit and integration test suites validating system integrity.""",
    "agentic_os": """- **Agent Registry & Specs (`agents/`):** Declarative agent personas, system instructions, and tool bindings.
- **Core Orchestrator (`core/`) & Tools (`tools/`):** Agent runtime, sandboxed tools, and execution harnesses.
- **Evaluation Benchmarks (`evals/`):** Quantitative accuracy and safety evals.""",
    "data_platform": """- **Pipelines (`pipelines/`) & Schemas (`schemas/`):** Data processing DAGs and schema definitions.
- **Data Layers (`data/`) & Notebooks (`notebooks/`):** Partitioned datasets and exploratory analysis.""",
    "minimal_research": """- **Research Corpus (`papers/`, `notes/`):** Primary literature reviews and research notes.
- **Synthesis Layer (`drafts/`, `wiki/synthesis/`):** Cross-cutting analysis and publication drafts.""",
}

DOMAIN_AUTONOMY_RULES = {
    "creative_operations": """3. **No In-Place Modifications of Audited Volumes**: External media and cloud storage are strictly virtualized in `ledger/`.""",
    "software_engineering": """3. **No Unsanitized DOM Insertion**: External text must pass through sanitizers before DOM rendering.""",
    "agentic_os": """3. **No Unbounded Agent Loops**: Autonomous agent executions must respect explicit write budgets and iteration caps.""",
    "data_platform": """3. **No In-Place Mutation of Raw Stores**: Ingested data is strictly immutable.""",
    "minimal_research": """3. **No Modification of docs/ or raw/**: External source materials are read-only.""",
}


def slugify(text: str) -> str:
    """Convert string to kebab-case slug."""
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-")


def render_template(template_text: str, context: Dict[str, str]) -> str:
    """Render double-curly braces {{key}} with context values."""
    res = template_text
    for k, v in context.items():
        res = res.replace(f"{{{{{k}}}}}", str(v))
    return res


def ensure_dir(path: Path, mode: int = 0o755) -> None:
    """Create directory with explicit mode."""
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, mode)


def scaffold_workspace(
    target_dir: Path,
    name: str,
    slug: str,
    archetype: str,
    flavor: str = "antigravity",
    cadence_backend: str = "firestore",
    wiki_backend: str = "postgres",
    firestore_collection: str = "",
    postgres_repo_key: str = "",
    author: str = "Harrison Reed",
    task_prompt: str = "",
    skip_git: bool = False,
    skip_network: bool = False,
    verbose: bool = False,
) -> bool:
    """Execute end-to-end workspace scaffolding."""
    if archetype not in VALID_ARCHETYPES:
        print(
            f"Error: Invalid archetype '{archetype}'. Must be one of: {', '.join(VALID_ARCHETYPES)}"
        )
        return False

    if flavor not in VALID_FLAVORS:
        print(
            f"Error: Invalid flavor '{flavor}'. Must be one of: {', '.join(VALID_FLAVORS)}"
        )
        return False

    fs_col = firestore_collection or f"{slug.replace('-', '_')}_goals"
    pg_key = postgres_repo_key or slug

    print("\n========================================================")
    print(f"BOOTSTRAPPING WORKSPACE: {name} ({slug})")
    print(f"Target Directory: {target_dir}")
    print(f"Archetype: {archetype} | Flavor: {flavor}")
    print(f"Cadence Backend: {cadence_backend} ({fs_col})")
    print(f"Wiki DB Backend: {wiki_backend} ({pg_key})")
    if task_prompt:
        print(f"Task Prompt: {task_prompt}")
    print("========================================================\n")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cycle = datetime.now(timezone.utc).strftime("%Y-W%W")
    year = datetime.now(timezone.utc).strftime("%Y")

    context = {
        "project_name": name,
        "project_slug": slug,
        "project_slug_upper": slug.upper().replace("-", "_"),
        "archetype": archetype,
        "flavor": flavor,
        "cadence_backend": cadence_backend,
        "wiki_backend": wiki_backend,
        "firestore_collection": fs_col,
        "postgres_repo_key": pg_key,
        "author_name": author,
        "date": today,
        "cycle": cycle,
        "year": year,
        "default_phase": DEFAULT_PHASES.get(archetype, "planning"),
        "next_phase": NEXT_PHASES.get(archetype, "in_progress"),
        "initial_commit": "initial",
        "domain_invariants": DOMAIN_INVARIANTS.get(archetype, ""),
        "domain_rules_list": DOMAIN_RULES_LIST.get(archetype, ""),
        "architecture_components": ARCHITECTURE_COMPONENTS.get(archetype, ""),
        "domain_autonomy_rules": DOMAIN_AUTONOMY_RULES.get(archetype, ""),
        "feature_name": "Core Foundation",
        "decision_title": "Architecture Baseline Selection",
        "agent_name": "Primary Coordinator",
        "tool_name": "workspace_inspector",
        "eval_suite_name": "baseline_accuracy",
        "target_agent": "Primary Coordinator",
        "pipeline_name": "main_ingest",
        "schema_name": "event_log",
        "paper_title": "Foundation Review",
        "experiment_name": "initial_baseline",
    }

    # 1. Directory Structure (Mode 0755)
    print("[1/8] Creating directory hierarchy (mode 0755)...")
    common_dirs = [
        target_dir / "wiki" / "entities",
        target_dir / "wiki" / "concepts",
        target_dir / "wiki" / "synthesis",
        target_dir / "wiki" / "retro",
        target_dir / "scripts",
        target_dir / "templates",
        target_dir / ".obsidian",
        target_dir / "tests",
        target_dir / "docs" / "drift_registries",
        target_dir / ".agents" / "rules",
    ]

    if flavor in ("antigravity", "universal"):
        common_dirs.extend(
            [
                target_dir / ".agents" / "skills" / "session-start",
                target_dir / ".agents" / "skills" / "session-wrapup",
            ]
        )

    if flavor in ("copilot", "universal"):
        common_dirs.extend(
            [
                target_dir / ".github",
                target_dir / ".github" / "prompts",
            ]
        )

    if cadence_backend == "sqlite":
        common_dirs.append(target_dir / ".cadence")
    if wiki_backend == "sqlite":
        common_dirs.append(target_dir / ".wiki")

    archetype_dir_map = {
        "creative_operations": [
            target_dir / "ledger" / "attachments",
            target_dir / "projects",
            target_dir / "meetings",
            target_dir / "templates" / "examples",
        ],
        "software_engineering": [
            target_dir / "src",
            target_dir / "api",
            target_dir / "docs",
        ],
        "agentic_os": [
            target_dir / "agents",
            target_dir / "core",
            target_dir / "tools",
            target_dir / "evals",
            target_dir / "docs",
        ],
        "data_platform": [
            target_dir / "pipelines",
            target_dir / "data",
            target_dir / "schemas",
            target_dir / "notebooks",
        ],
        "minimal_research": [
            target_dir / "papers",
            target_dir / "notes",
            target_dir / "drafts",
        ],
    }

    dirs_to_create = common_dirs + archetype_dir_map.get(archetype, [])
    for d in dirs_to_create:
        ensure_dir(d)

    # 2. Obsidian Vault Configuration
    print("[2/8] Installing Obsidian configuration JSONs...")
    obsidian_src = SKILLS_DIR / "workspace-scaffolder" / "templates" / "obsidian"
    for jf in obsidian_src.glob("*.json"):
        dest = target_dir / ".obsidian" / jf.name
        content = render_template(jf.read_text(encoding="utf-8"), context)
        dest.write_text(content, encoding="utf-8")

    # 3. Templates & Clean Zero-State Ledgers
    print("[3/8] Scaffolding universal & archetype markdown templates...")
    univ_tmpl_src = (
        SKILLS_DIR / "workspace-scaffolder" / "templates" / "templates_universal"
    )
    if univ_tmpl_src.is_dir():
        for tf in univ_tmpl_src.glob("*.md"):
            dest = target_dir / "templates" / tf.name
            content = render_template(tf.read_text(encoding="utf-8"), context)
            dest.write_text(content, encoding="utf-8")

    arch_tmpl_src = (
        SKILLS_DIR
        / "workspace-scaffolder"
        / "templates"
        / "archetypes"
        / archetype
        / "templates"
    )
    if arch_tmpl_src.is_dir():
        for tf in arch_tmpl_src.glob("*.md"):
            dest = target_dir / "templates" / tf.name
            content = render_template(tf.read_text(encoding="utf-8"), context)
            dest.write_text(content, encoding="utf-8")

    if archetype == "creative_operations":
        ledger_src = (
            SKILLS_DIR
            / "workspace-scaffolder"
            / "templates"
            / "archetypes"
            / "creative_operations"
            / "ledger"
        )
        if ledger_src.is_dir():
            for lf in ledger_src.iterdir():
                if lf.is_file():
                    dest = target_dir / "ledger" / lf.name
                    content = render_template(lf.read_text(encoding="utf-8"), context)
                    dest.write_text(content, encoding="utf-8")
        ex_src = (
            SKILLS_DIR
            / "workspace-scaffolder"
            / "templates"
            / "archetypes"
            / "creative_operations"
            / "examples"
        )
        if ex_src.is_dir():
            for ef in ex_src.iterdir():
                if ef.is_file():
                    dest = target_dir / "templates" / "examples" / ef.name
                    shutil.copy2(ef, dest)

    wiki_src = SKILLS_DIR / "workspace-scaffolder" / "templates" / "wiki"
    for wf in wiki_src.rglob("*.md"):
        rel = wf.relative_to(wiki_src)
        dest = target_dir / "wiki" / rel
        ensure_dir(dest.parent)
        content = render_template(wf.read_text(encoding="utf-8"), context)
        dest.write_text(content, encoding="utf-8")

    # 4. Governance Architecture
    print("[4/8] Installing governance constitutions and safety rules...")
    gov_src = SKILLS_DIR / "governance-architect" / "templates"

    readme_txt = render_template(
        (gov_src / "README.md.template").read_text(encoding="utf-8"), context
    )
    (target_dir / "README.md").write_text(readme_txt, encoding="utf-8")

    agents_txt = render_template(
        (gov_src / "AGENTS.md.template").read_text(encoding="utf-8"), context
    )
    (target_dir / "AGENTS.md").write_text(agents_txt, encoding="utf-8")

    gemini_txt = render_template(
        (gov_src / "GEMINI.md.template").read_text(encoding="utf-8"), context
    )
    (target_dir / "GEMINI.md").write_text(gemini_txt, encoding="utf-8")

    univ_rules_dir = gov_src / "rules" / "universal"
    for rf in univ_rules_dir.glob("*.template"):
        clean_name = rf.stem
        dest = target_dir / ".agents" / "rules" / clean_name
        content = render_template(rf.read_text(encoding="utf-8"), context)
        dest.write_text(content, encoding="utf-8")

    arch_rules_dir = gov_src / "rules" / "archetypes" / archetype
    if arch_rules_dir.is_dir():
        for rf in arch_rules_dir.glob("*.template"):
            clean_name = rf.stem
            dest = target_dir / ".agents" / "rules" / clean_name
            content = render_template(rf.read_text(encoding="utf-8"), context)
            dest.write_text(content, encoding="utf-8")

    if flavor in ("copilot", "universal"):
        copilot_src = gov_src / "copilot"
        copilot_instr = render_template(
            (copilot_src / "copilot-instructions.md.template").read_text(
                encoding="utf-8"
            ),
            context,
        )
        (target_dir / ".github" / "copilot-instructions.md").write_text(
            copilot_instr, encoding="utf-8"
        )

        for pf in (copilot_src / "prompts").glob("*.template"):
            clean_name = pf.stem
            dest = target_dir / ".github" / "prompts" / clean_name
            content = render_template(pf.read_text(encoding="utf-8"), context)
            dest.write_text(content, encoding="utf-8")

    # 5. Cadence Goal Engine
    print(f"[5/8] Generating scripts/cadence.py CLI (backend: {cadence_backend})...")
    cadence_tmpl = (
        SKILLS_DIR / "cadence-scaffolder" / "templates" / "cadence.py.template"
    )
    cadence_dest = target_dir / "scripts" / "cadence.py"
    cadence_content = render_template(cadence_tmpl.read_text(encoding="utf-8"), context)
    cadence_dest.write_text(cadence_content, encoding="utf-8")
    os.chmod(cadence_dest, 0o755)

    # 6. Multi-Tenant Wiki Pipeline
    print(f"[6/8] Generating wiki pipeline scripts (backend: {wiki_backend})...")
    wiki_pipe_src = SKILLS_DIR / "wiki-db-scaffolder" / "templates"

    exp_dest = target_dir / "scripts" / "export_wiki.py"
    exp_dest.write_text(
        render_template(
            (wiki_pipe_src / "export_wiki.py.template").read_text(encoding="utf-8"),
            context,
        ),
        encoding="utf-8",
    )
    os.chmod(exp_dest, 0o755)

    sync_dest = target_dir / "scripts" / "sync_wiki_db.py"
    sync_dest.write_text(
        render_template(
            (wiki_pipe_src / "sync_wiki_db.py.template").read_text(encoding="utf-8"),
            context,
        ),
        encoding="utf-8",
    )
    os.chmod(sync_dest, 0o755)

    # 7. Drift Registries & Enforcer
    print("[7/8] Generating drift registries and scripts/drift_enforcer.py...")
    drift_src = SKILLS_DIR / "drift-registry-scaffolder" / "templates"
    for dr_tmpl in drift_src.glob("*.json.template"):
        dr_dest = target_dir / "docs" / "drift_registries" / dr_tmpl.stem
        dr_dest.write_text(
            render_template(dr_tmpl.read_text(encoding="utf-8"), context),
            encoding="utf-8",
        )

    drift_enforcer_dest = target_dir / "scripts" / "drift_enforcer.py"
    drift_enforcer_dest.write_text(
        render_template(
            (drift_src / "drift_enforcer.py.template").read_text(encoding="utf-8"),
            context,
        ),
        encoding="utf-8",
    )
    os.chmod(drift_enforcer_dest, 0o755)

    # Session Rituals Skills (Antigravity)
    if flavor in ("antigravity", "universal"):
        rituals_src = SKILLS_DIR / "session-rituals-scaffolder" / "templates"
        start_skill_dest = (
            target_dir / ".agents" / "skills" / "session-start" / "SKILL.md"
        )
        start_skill_dest.write_text(
            render_template(
                (rituals_src / "session-start.SKILL.md.template").read_text(
                    encoding="utf-8"
                ),
                context,
            ),
            encoding="utf-8",
        )

        wrapup_skill_dest = (
            target_dir / ".agents" / "skills" / "session-wrapup" / "SKILL.md"
        )
        wrapup_skill_dest.write_text(
            render_template(
                (rituals_src / "session-wrapup.SKILL.md.template").read_text(
                    encoding="utf-8"
                ),
                context,
            ),
            encoding="utf-8",
        )

    # 8. Verification Harness & Test Suite
    print(
        "[8/8] Generating archetype-aware 9-layer verification harness and unit tests..."
    )
    harness_src = SKILLS_DIR / "harness-scaffolder" / "templates"

    verify_dest = target_dir / "scripts" / "verify_bootstrap.py"
    verify_dest.write_text(
        render_template(
            (harness_src / "verify_bootstrap.py.template").read_text(encoding="utf-8"),
            context,
        ),
        encoding="utf-8",
    )
    os.chmod(verify_dest, 0o755)

    for tf in harness_src.glob("test_*.py.template"):
        t_dest = target_dir / "tests" / tf.stem
        t_dest.write_text(
            render_template(tf.read_text(encoding="utf-8"), context), encoding="utf-8"
        )

    # Initial export & sync of wiki bundle
    print("Compiling initial wiki_bundle.json...")
    subprocess.run([sys.executable, str(exp_dest)], cwd=target_dir, check=True)
    print(f"Syncing initial wiki to database ({wiki_backend})...")
    try:
        subprocess.run([sys.executable, str(sync_dest)], cwd=target_dir, check=False)
    except Exception as exc:
        print(f"Warning: sync_wiki_db.py skipped: {exc}")

    # If sqlite cadence backend, initialize test goal so CLI is verified
    if cadence_backend == "sqlite":
        print("Initializing SQLite Cadence goal store...")
        subprocess.run(
            [
                sys.executable,
                str(cadence_dest),
                "create",
                "--title",
                f"Initial Sprint Setup: {name}",
                "--scope",
                "daily",
            ],
            cwd=target_dir,
            check=True,
        )

    # Git Initialization and Baseline
    if not skip_git:
        git_dir = target_dir / ".git"
        if not git_dir.is_dir():
            print("Initializing git repository...")
            subprocess.run(["git", "init"], cwd=target_dir, check=True)
            gitignore_content = "__pycache__/\n*.pyc\n.DS_Store\nnode_modules/\n*.log\n.env*\n!.env.example\n*.db\n.cadence/\n.wiki/\n"
            (target_dir / ".gitignore").write_text(gitignore_content, encoding="utf-8")

        print("Creating initial baseline commit...")
        subprocess.run(["git", "add", "."], cwd=target_dir, check=True)
        commit_res = subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"feat({slug}): initial workspace bootstrap baseline",
            ],
            cwd=target_dir,
            capture_output=True,
            text=True,
        )
        if commit_res.returncode == 0 or "nothing to commit" in commit_res.stdout:
            print("Stamping initial drift registry baseline...")
            subprocess.run(
                [sys.executable, str(drift_enforcer_dest), "--stamp"],
                cwd=target_dir,
                check=True,
            )
            subprocess.run(
                ["git", "add", "docs/drift_registries/"], cwd=target_dir, check=True
            )
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    f"chore({slug}): stamp initial drift registry baseline",
                ],
                cwd=target_dir,
                capture_output=True,
                text=True,
            )

    print("\nRunning 9-Layer Verification Harness...")
    verify_cmd = [sys.executable, str(verify_dest), "--verbose"]
    if skip_network:
        verify_cmd.append("--skip-network")
    v_res = subprocess.run(verify_cmd, cwd=target_dir)

    if v_res.returncode == 0:
        print("\n========================================================")
        print(f"SUCCESSFULLY BOOTSTRAPPED & VERIFIED: {name}")
        print(f"Archetype: {archetype} | Flavor: {flavor}")
        print(f"Cadence Backend: {cadence_backend} | Wiki Backend: {wiki_backend}")
        print(f"Workspace Location: {target_dir}")
        print("========================================================\n")
        return True
    else:
        print("\nVerification harness detected errors. Review output above.")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Antigravity Workspace Bootstrapper Orchestrator."
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Human-readable project name (e.g. Wonder, Work Service).",
    )
    parser.add_argument(
        "--slug",
        default=None,
        help="Kebab-case project slug (defaults to slugified name).",
    )
    parser.add_argument(
        "--target-dir", required=True, help="Absolute path to target directory."
    )
    parser.add_argument(
        "--archetype",
        default="software_engineering",
        choices=VALID_ARCHETYPES,
        help="Workspace archetype.",
    )
    parser.add_argument(
        "--flavor",
        default="antigravity",
        choices=VALID_FLAVORS,
        help="Agent flavor: antigravity (default), copilot, or universal.",
    )
    parser.add_argument(
        "--cadence-backend",
        default=None,
        choices=["firestore", "sqlite"],
        help="Goal storage backend: firestore or sqlite.",
    )
    parser.add_argument(
        "--wiki-backend",
        default=None,
        choices=["postgres", "sqlite"],
        help="Wiki index backend: postgres or sqlite.",
    )
    parser.add_argument(
        "--task-prompt",
        default="",
        help="Description of the project's purpose and requirements.",
    )
    parser.add_argument(
        "--firestore-collection", default=None, help="Firestore collection name."
    )
    parser.add_argument(
        "--postgres-repo-key", default=None, help="PostgreSQL repo partition key."
    )
    parser.add_argument(
        "--author", default="Harrison Reed", help="Author/Facilitator name."
    )
    parser.add_argument(
        "--skip-git", action="store_true", help="Skip git initialization and commit."
    )
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Skip live network checks in verification.",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging.")

    args = parser.parse_args()

    slug = args.slug or slugify(args.name)
    target = Path(args.target_dir).resolve()

    # Smart defaults based on flavor
    if args.flavor == "copilot":
        cadence_backend = args.cadence_backend or "sqlite"
        wiki_backend = args.wiki_backend or "sqlite"
    else:
        cadence_backend = args.cadence_backend or "firestore"
        wiki_backend = args.wiki_backend or "postgres"

    success = scaffold_workspace(
        target_dir=target,
        name=args.name,
        slug=slug,
        archetype=args.archetype,
        flavor=args.flavor,
        cadence_backend=cadence_backend,
        wiki_backend=wiki_backend,
        firestore_collection=args.firestore_collection
        or f"{slug.replace('-', '_')}_goals",
        postgres_repo_key=args.postgres_repo_key or slug,
        author=args.author,
        task_prompt=args.task_prompt,
        skip_git=args.skip_git,
        skip_network=args.skip_network,
        verbose=args.verbose,
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
