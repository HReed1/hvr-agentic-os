#!/usr/bin/env bash
# Bootstrap script for the AI Engineering dev environment.
# Sets up wiki, drift tracking, session tracking, and checks dependencies,
# then prints a harness-tailored LLM Ingest Prompt. The agent (not this script)
# implements the four reference guides in docs/reference/.
#
# Harness-agnostic: --harness selects which instruction files and skill
# directories the ingest prompt tells the agent to create.
#
# Portable: resources (reference guides, drift enforcer, wiki DB scripts) are
# located relative to this script, so it works from a clone of hvr-agentic-os
# or from the packaged plugin (plugins/ai-engineering-scaffold/).
#
# Compatible with macOS bash 3.2 (no associative arrays).
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAFFOLD_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

REFERENCE_GUIDES="llm-wiki-antigravity.md drift-registry.md session-workflows.md elephant-goldfish-verification.md"
VALID_HARNESSES="antigravity claude codex copilot"

# ── Defaults ──────────────────────────────────────────────────────────────────
HARNESS_ARGS=""
WIKI_DB="none"
DB_USER="${USER:-$(id -un)}"
DB_NAME="wiki"
DB_HOST="localhost"
DB_PORT="5432"
AUTHOR="$(git config user.name 2>/dev/null || true)"
AUTHOR="${AUTHOR:-${USER:-$(id -un)}}"
TARGET_DIR="."

usage() {
    cat << 'USAGE'
Usage: bootstrap_ai_engineering.sh [options]

Options:
  --harness NAME      Agent harness(es): antigravity | claude | codex | copilot | all.
                      Repeatable or comma-separated (e.g. --harness claude,codex).
                      Default: antigravity.
  --wiki-db MODE      Wiki metadata index: postgres | none. Default: none
                      (markdown-only wiki; the agent skips all DB/MCP/SQL steps).
  --db-user USER      Postgres user for the wiki index. Default: $USER.
  --db-name NAME      Postgres database name. Default: wiki.
  --db-host HOST      Postgres host. Default: localhost.
  --db-port PORT      Postgres port. Default: 5432.
  --author NAME       Author recorded in retrospectives and wiki pages.
                      Default: `git config user.name`, falling back to $USER.
  --target-dir DIR    Project to scaffold. Default: current directory.
  -h, --help          Show this help.

Harness mapping:
  antigravity  AGENTS.md + GEMINI.md          skills in .agents/skills/
  claude       AGENTS.md + CLAUDE.md          skills in .claude/skills/  (CLAUDE.md imports @AGENTS.md)
  codex        AGENTS.md only (< 32 KiB)      skills in .agents/skills/
  copilot      AGENTS.md + .github/copilot-instructions.md   skills in .agents/skills/
USAGE
}

die() { echo "Error: $*" >&2; echo "Run with --help for usage." >&2; exit 1; }

# ── Argument parsing ──────────────────────────────────────────────────────────
while [ $# -gt 0 ]; do
    case "$1" in
        --harness)    [ $# -ge 2 ] || die "--harness requires a value"; HARNESS_ARGS="$HARNESS_ARGS,$2"; shift 2 ;;
        --harness=*)  HARNESS_ARGS="$HARNESS_ARGS,${1#*=}"; shift ;;
        --wiki-db)    [ $# -ge 2 ] || die "--wiki-db requires a value"; WIKI_DB="$2"; shift 2 ;;
        --wiki-db=*)  WIKI_DB="${1#*=}"; shift ;;
        --db-user)    [ $# -ge 2 ] || die "--db-user requires a value"; DB_USER="$2"; shift 2 ;;
        --db-user=*)  DB_USER="${1#*=}"; shift ;;
        --db-name)    [ $# -ge 2 ] || die "--db-name requires a value"; DB_NAME="$2"; shift 2 ;;
        --db-name=*)  DB_NAME="${1#*=}"; shift ;;
        --db-host)    [ $# -ge 2 ] || die "--db-host requires a value"; DB_HOST="$2"; shift 2 ;;
        --db-host=*)  DB_HOST="${1#*=}"; shift ;;
        --db-port)    [ $# -ge 2 ] || die "--db-port requires a value"; DB_PORT="$2"; shift 2 ;;
        --db-port=*)  DB_PORT="${1#*=}"; shift ;;
        --author)     [ $# -ge 2 ] || die "--author requires a value"; AUTHOR="$2"; shift 2 ;;
        --author=*)   AUTHOR="${1#*=}"; shift ;;
        --target-dir) [ $# -ge 2 ] || die "--target-dir requires a value"; TARGET_DIR="$2"; shift 2 ;;
        --target-dir=*) TARGET_DIR="${1#*=}"; shift ;;
        -h|--help)    usage; exit 0 ;;
        *)            die "Unknown option: $1" ;;
    esac
done

case "$WIKI_DB" in
    postgres|none) ;;
    *) die "Invalid --wiki-db '$WIKI_DB' (expected: postgres | none)" ;;
esac

# Normalize harnesses: aliases, 'all', de-duplication, canonical order.
[ -n "$HARNESS_ARGS" ] || HARNESS_ARGS="antigravity"
REQUESTED=" "
for raw in $(echo "$HARNESS_ARGS" | tr ',' ' '); do
    h="$(echo "$raw" | tr '[:upper:]' '[:lower:]')"
    case "$h" in
        gemini|agy) h="antigravity" ;;
        claude-code|claude_code) h="claude" ;;
        openai|openai-codex) h="codex" ;;
        github-copilot) h="copilot" ;;
    esac
    if [ "$h" = "all" ]; then
        REQUESTED=" $VALID_HARNESSES "
        continue
    fi
    case " $VALID_HARNESSES " in
        *" $h "*) REQUESTED="$REQUESTED$h " ;;
        *) die "Unknown harness '$raw' (expected: $VALID_HARNESSES | all)" ;;
    esac
done
HARNESSES=""
for h in $VALID_HARNESSES; do
    case "$REQUESTED" in *" $h "*) HARNESSES="$HARNESSES $h" ;; esac
done
HARNESSES="${HARNESSES# }"
has_harness() { case " $HARNESSES " in *" $1 "*) return 0 ;; esac; return 1; }

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"
TARGET_ABS="$(pwd)"

# Detect existing project context BEFORE creating anything, so the ingest prompt
# can tell the agent to integrate (existing repo) or start fresh (new repo).
IS_GIT=0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 && IS_GIT=1
EXISTING_INSTRUCTIONS=""
for f in AGENTS.md CLAUDE.md GEMINI.md .github/copilot-instructions.md; do
    [ -f "$f" ] && EXISTING_INSTRUCTIONS="$EXISTING_INSTRUCTIONS \`$f\`"
done
EXISTING_INSTRUCTIONS="${EXISTING_INSTRUCTIONS# }"
REPO_MODE="new"
if [ -n "$EXISTING_INSTRUCTIONS" ] || [ -f README.md ] || [ -f wiki/index.md ]; then
    REPO_MODE="existing"
elif [ "$IS_GIT" = 1 ] && [ -n "$(git ls-files 2>/dev/null | head -n 1)" ]; then
    REPO_MODE="existing"
fi

DB_SUMMARY="$WIKI_DB"
[ "$WIKI_DB" = "postgres" ] && DB_SUMMARY="postgres ($DB_USER@$DB_HOST:$DB_PORT/$DB_NAME)"

echo "================================================="
echo "[BOOTSTRAP] Initializing AI Engineering Scaffold..."
echo "  Target:   $TARGET_ABS"
echo "  Harness:  $HARNESSES"
echo "  Wiki DB:  $DB_SUMMARY"
echo "  Author:   $AUTHOR"
echo "  Repo:     $REPO_MODE$( [ "$IS_GIT" = 1 ] || echo " (not a git repository)" )"
echo "================================================="

# copy_resource <relative-path>: copy from the scaffold source if missing here.
copy_resource() {
    local rel="$1" src="$SCAFFOLD_ROOT/$1"
    if [ -f "$rel" ]; then
        echo "  Skipped: $rel already exists."
    elif [ -f "$src" ]; then
        mkdir -p "$(dirname "$rel")"
        cp "$src" "$rel"
        echo "  Copied $rel"
    else
        echo "  [WARN] $rel not found in scaffold source ($SCAFFOLD_ROOT). Copy it manually."
    fi
}

# 1. Wiki directory structure
echo "Setting up wiki structure..."
mkdir -p wiki/entities wiki/concepts wiki/synthesis

if [ ! -f wiki/index.md ]; then
    cat << 'EOF' > wiki/index.md
---
title: Wiki Index
type: index
---

# Wiki Index

| Concept/Entity | Type | Status | Link |
|----------------|------|--------|------|
EOF
    echo "  Created wiki/index.md"
else
    echo "  Skipped: wiki/index.md already exists."
fi

if [ ! -f wiki/log.md ]; then
    cat << 'EOF' > wiki/log.md
# Wiki Log

EOF
    echo "  Created wiki/log.md"
else
    echo "  Skipped: wiki/log.md already exists."
fi

if [ ! -f wiki/overview.md ]; then
    cat << 'EOF' > wiki/overview.md
---
title: Project Overview
type: overview
---

# Project Overview
EOF
    echo "  Created wiki/overview.md"
else
    echo "  Skipped: wiki/overview.md already exists."
fi

# 2. Drift registries
echo "Setting up drift registries..."
mkdir -p docs/drift_registries/

if [ ! -f docs/drift_registries/wiki.json ]; then
    cat << 'EOF' > docs/drift_registries/wiki.json
{
  "domain": "wiki",
  "entries": []
}
EOF
    echo "  Created docs/drift_registries/wiki.json"
else
    echo "  Skipped: docs/drift_registries/wiki.json already exists."
fi

# 3. Reference docs (copied from the scaffold source when available)
echo "Setting up reference docs..."
mkdir -p docs/reference/
if [ "$SCAFFOLD_ROOT" = "$TARGET_ABS" ]; then
    echo "  Running inside the scaffold source repository; reference guides already present."
else
    for guide in $REFERENCE_GUIDES; do
        copy_resource "docs/reference/$guide"
    done
fi

# 4. Session & Persona infrastructure
echo "Setting up session and Goldfish persona infrastructure..."
SKILL_DIRS=""
if has_harness antigravity || has_harness codex || has_harness copilot; then
    SKILL_DIRS="$SKILL_DIRS .agents/skills"
fi
if has_harness claude; then
    SKILL_DIRS="$SKILL_DIRS .claude/skills"
fi
SKILL_DIRS="${SKILL_DIRS# }"
mkdir -p docs/retrospectives/ docs/decisions/ .agents/rules/ .agents/personas/
for d in $SKILL_DIRS; do mkdir -p "$d"; done
echo "  Created session, decisions, rules, personas, and skills ($SKILL_DIRS) directories."

# 5. Scripts
echo "Setting up scripts directory..."
mkdir -p scripts/
if [ "$SCAFFOLD_ROOT" != "$TARGET_ABS" ]; then
    copy_resource "scripts/drift_enforcer.py"
    if [ "$WIKI_DB" = "postgres" ]; then
        copy_resource "scripts/wiki_db_init.py"
        copy_resource "scripts/wiki_db_backfill.py"
    fi
fi
if [ ! -f scripts/drift_enforcer.py ]; then
    echo "  [WARN] scripts/drift_enforcer.py not found. Consider adding it."
else
    echo "  Found scripts/drift_enforcer.py"
fi

# 6. Postgres wiki-db (only when selected)
if [ "$WIKI_DB" = "postgres" ]; then
    echo "Checking PostgreSQL dependencies ($DB_USER@$DB_HOST:$DB_PORT/$DB_NAME)..."
    if command -v psql >/dev/null 2>&1; then
        if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
            echo "  PostgreSQL '$DB_NAME' database exists."
        else
            echo "  [INFO] PostgreSQL '$DB_NAME' database not found (or not reachable as '$DB_USER')."
            echo "         To create it, run: createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME"
        fi
    else
        echo "  [INFO] 'psql' not found in PATH. Install PostgreSQL or re-run with --wiki-db none."
    fi
else
    echo "Wiki DB: none (markdown-only wiki). Re-run with --wiki-db postgres to add the metadata index."
fi

# 7. Record the scaffold configuration for the agent and future runs
CFG_DB_USER=""; CFG_DB_NAME=""; CFG_DB_HOST=""; CFG_DB_PORT=""
if [ "$WIKI_DB" = "postgres" ]; then
    CFG_DB_USER="$DB_USER"; CFG_DB_NAME="$DB_NAME"; CFG_DB_HOST="$DB_HOST"; CFG_DB_PORT="$DB_PORT"
fi
AUTHOR_JSON="$(printf '%s' "$AUTHOR" | sed 's/\\/\\\\/g; s/"/\\"/g')"
cat << EOF > .agents/scaffold-config.json
{
  "harnesses": "$HARNESSES",
  "skill_dirs": "$SKILL_DIRS",
  "repo_mode": "$REPO_MODE",
  "wiki_db": "$WIKI_DB",
  "db_user": "$CFG_DB_USER",
  "db_name": "$CFG_DB_NAME",
  "db_host": "$CFG_DB_HOST",
  "db_port": "$CFG_DB_PORT",
  "author": "$AUTHOR_JSON"
}
EOF
echo "  Wrote .agents/scaffold-config.json"

# 8. Build the harness-tailored ingest prompt pieces
HARNESS_LABELS=""
INSTRUCTION_LINES=""
GOLDFISH_LINES=""
for h in $HARNESSES; do
    case "$h" in
        antigravity)
            HARNESS_LABELS="$HARNESS_LABELS, Antigravity"
            INSTRUCTION_LINES="$INSTRUCTION_LINES
   - \`GEMINI.md\` (Antigravity): only Antigravity-specific notes (e.g. MCP server config), plus a line telling the agent to follow \`AGENTS.md\`."
            GOLDFISH_LINES="$GOLDFISH_LINES
   - Antigravity: \`invoke_subagent\` with \`TypeName: \"research\"\` (read-only), three in parallel."
            ;;
        claude)
            HARNESS_LABELS="$HARNESS_LABELS, Claude Code"
            INSTRUCTION_LINES="$INSTRUCTION_LINES
   - \`CLAUDE.md\` (Claude Code): first line must be \`@AGENTS.md\` (Claude Code does not read AGENTS.md on its own), followed by Claude-specific notes only."
            GOLDFISH_LINES="$GOLDFISH_LINES
   - Claude Code: three parallel subagents via the Task tool, using a read-only agent type (e.g. \`Explore\`, or a custom agent limited to Read/Grep/Glob)."
            ;;
        codex)
            HARNESS_LABELS="$HARNESS_LABELS, OpenAI Codex"
            INSTRUCTION_LINES="$INSTRUCTION_LINES
   - Codex reads \`AGENTS.md\` only: it must be self-contained and stay under 32 KiB (Codex silently truncates beyond \`project_doc_max_bytes\`). Move long detail into rules/skills and link to it."
            GOLDFISH_LINES="$GOLDFISH_LINES
   - Codex: three independent sessions, \`codex exec --sandbox read-only --ephemeral \"<prompt>\"\`, run in parallel."
            ;;
        copilot)
            HARNESS_LABELS="$HARNESS_LABELS, GitHub Copilot"
            INSTRUCTION_LINES="$INSTRUCTION_LINES
   - \`.github/copilot-instructions.md\` (GitHub Copilot): a short pointer to \`AGENTS.md\` plus Copilot-specific notes only."
            GOLDFISH_LINES="$GOLDFISH_LINES
   - GitHub Copilot: a fresh chat session per Goldfish (no prior history, Ask/read-only mode), attaching only the persona file and the target file."
            ;;
    esac
done
HARNESS_LABELS="${HARNESS_LABELS#, }"

SKILL_TARGETS=""
for d in $SKILL_DIRS; do SKILL_TARGETS="$SKILL_TARGETS \`$d/<name>/SKILL.md\` and"; done
SKILL_TARGETS="${SKILL_TARGETS% and}"
SKILL_TARGETS="${SKILL_TARGETS# }"
SKILL_MIRROR_NOTE=""
if has_harness claude && [ "$SKILL_DIRS" != ".claude/skills" ]; then
    SKILL_MIRROR_NOTE="
   - Treat \`.agents/skills/\` as canonical and keep \`.claude/skills/\` byte-identical; register each mirror as a dependency in \`docs/drift_registries/agent.json\`."
fi

if [ "$WIKI_DB" = "postgres" ]; then
    DB_SETTING="PostgreSQL database \`$DB_NAME\` on \`$DB_HOST:$DB_PORT\`, user \`$DB_USER\`"
    DB_STEP="   - Wiki database is PostgreSQL. Initialize it with \`python3 scripts/wiki_db_init.py --database $DB_NAME --host $DB_HOST --port $DB_PORT --user $DB_USER\`, and use exactly these connection settings (\`psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME\`) everywhere — never another username."
else
    DB_SETTING="none — markdown-only wiki"
    DB_STEP="   - Wiki database is NONE: skip every database, MCP server, SQL, and backfill step in the guide. The markdown wiki (index.md, log.md) is the only index."
fi

# 9. LLM Ingest Prompt
if [ "$REPO_MODE" = "existing" ]; then
    MERGE_LINE="- Put new protocol sections in \`AGENTS.md\` as the harness mapping says (create it if missing, append if it exists)."
    if [ -n "$EXISTING_INSTRUCTIONS" ]; then
        MERGE_LINE="$MERGE_LINE In the existing instruction files ($EXISTING_INSTRUCTIONS), only add the pointer/import lines the mapping requires."
    fi
    REPO_BLOCK="Existing repository: this project already has content. Integrate the scaffold; do not replace anything:
$MERGE_LINE Never delete or rewrite existing content; if existing guidance conflicts with the guides, keep mine and flag the conflict to me.
- Investigate the repository and its available documentation, and ask me clarifying questions about the project's architecture, domain, or priorities alongside your investigation.
- Seed the wiki from what already exists (README.md, docs/, the code layout) plus my answers: write wiki/overview.md and initial entity/concept pages covering the main areas of the repo, cite their sources, and record the ingest in wiki/log.md. Keep this initial bootstrap seed high-level so we preserve context window budget — a deeper, comprehensive wiki and drift-registry ingest should happen in the next clean session.
- Register the initial cross-file dependencies you find (e.g. README commands <-> scripts, config <-> code) in docs/drift_registries/.
- Finish with a list of every pre-existing file you modified."
else
    REPO_BLOCK="New repository: there is no existing project content yet. Before writing wiki/overview.md, ask me for a short description of what this project will build or manage."
fi
if [ "$IS_GIT" = 0 ]; then
    REPO_BLOCK="$REPO_BLOCK
- This directory is not a git repository. Run \`git init\` and make an initial commit before verifying the drift enforcer (it relies on git history)."
    echo ""
    echo "[WARN] $TARGET_ABS is not a git repository. The drift enforcer needs git: run 'git init' and commit."
fi
echo ""
echo "================================================="
echo "[SUCCESS] AI Engineering Scaffold Bootstrapped."
echo "================================================="
echo ""
echo "Next step: Feed the reference guides to your LLM agent."
echo "Copy the prompt below and paste it into your agent session:"
echo ""
echo "┌──────────────────────────────────────────────────┐"
echo "│                                                  │"
echo "│  COPY EVERYTHING BELOW THIS LINE                 │"
echo "│                                                  │"
echo "└──────────────────────────────────────────────────┘"
echo ""
cat << PROMPT
Initialize this project's AI Engineering scaffold by reading and implementing the following four reference guides, in order.

Project settings (chosen at bootstrap; also recorded in \`.agents/scaffold-config.json\` — use them, do not substitute your own):
- Agent harness(es): $HARNESS_LABELS
- Author: $AUTHOR (use this name in retrospectives, decisions, and wiki frontmatter)
- Wiki database: $DB_SETTING
- Task tracking: none configured. Do not assume Firestore, Cadence, Jira, or any other external service unless I ask for one.

$REPO_BLOCK

Harness mapping (the guides were written for Antigravity; apply this translation throughout):
1. Instruction files: put every protocol section the guides tell you to add to "GEMINI.md" (or "CLAUDE.md / AGENTS.md") into \`AGENTS.md\` — the single, harness-neutral source of truth. Then:$INSTRUCTION_LINES
2. Skills: wherever a guide says \`.agents/workflows/<name>.md\`, create $SKILL_TARGETS instead, with YAML frontmatter (\`name\`, \`description\`).$SKILL_MIRROR_NOTE
3. Rules and personas live in \`.agents/rules/\` and \`.agents/personas/\`. List every rule file in \`AGENTS.md\` so harnesses that do not auto-load that folder still follow them.
4. Goldfish reviewers must start with zero conversation history and be read-only:$GOLDFISH_LINES

1. Read \`docs/reference/llm-wiki-antigravity.md\` first.
   - This sets up the LLM Wiki: a persistent, agent-maintained knowledge base.
   - Add the wiki protocol sections to \`AGENTS.md\`.
   - Initialize wiki/index.md, wiki/log.md, and wiki/overview.md with project context.
$DB_STEP

2. Read \`docs/reference/drift-registry.md\` second.
   - This sets up the Drift Registry: cross-file dependency tracking.
   - Add the drift protocol sections to \`AGENTS.md\`.
   - Register initial dependencies in docs/drift_registries/ (including the instruction files and skills you create).
   - Verify scripts/drift_enforcer.py is present and functional (\`python3 scripts/drift_enforcer.py\`).

3. Read \`docs/reference/session-workflows.md\` third.
   - This sets up Session Workflows: structured open-work-close lifecycle.
   - Create the session-start and session-wrapup skills ($SKILL_TARGETS).
   - Add the session lifecycle sections to \`AGENTS.md\`.

4. Read \`docs/reference/elephant-goldfish-verification.md\` fourth.
   - This sets up Elephant-Goldfish Epistemic Verification: stateless read-only subagent review.
   - Create .agents/rules/no-glazing-and-epistemic-hygiene.md.
   - Create .agents/personas/goldfish-comprehension.md, goldfish-critic.md, and goldfish-readiness.md.
   - Create the goldfish-review skill ($SKILL_TARGETS), using the harness-specific Goldfish spawning method above.

After completing all four, verify \`python3 scripts/drift_enforcer.py\` executes cleanly, summarize what was created, and recommend starting a fresh, clean session (beginning with the session-start skill) for deep wiki and drift-registry ingestion before auditing issues or building new features.
PROMPT
echo ""
echo "┌──────────────────────────────────────────────────┐"
echo "│  END OF PROMPT                                   │"
echo "└──────────────────────────────────────────────────┘"
