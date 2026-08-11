#!/bin/bash
# Bootstrap script for the AI Engineering dev environment.
# Sets up wiki, drift tracking, session tracking, and checks dependencies.
set -e

echo "================================================="
echo "[BOOTSTRAP] Initializing AI Engineering Scaffold..."
echo "================================================="

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

# 3. Reference docs
echo "Setting up reference docs directory..."
mkdir -p docs/reference/
echo "  Note: Reference files must be manually copied here."

# 4. Session infrastructure
echo "Setting up session infrastructure..."
mkdir -p docs/retrospectives/ .agents/workflows/ .agents/rules/ .agents/skills/
echo "  Created session directories."

# 5. Scripts
echo "Setting up scripts directory..."
mkdir -p scripts/
if [ ! -f scripts/drift_enforcer.py ]; then
    echo "  [WARN] scripts/drift_enforcer.py not found. Consider adding it."
else
    echo "  Found scripts/drift_enforcer.py"
fi

# 6. Postgres wiki-db
echo "Checking optional PostgreSQL dependencies..."
if command -v psql >/dev/null 2>&1; then
    # Check if 'wiki' db exists using psql list
    if psql -lqt | cut -d \| -f 1 | grep -qw wiki; then
        echo "  PostgreSQL 'wiki' database exists."
    else
        echo "  [INFO] PostgreSQL 'wiki' database does not exist."
        echo "         To create it, run: createdb wiki"
    fi
else
    echo "  [INFO] 'psql' not found in PATH. Skipping PostgreSQL checks."
fi

# 7. LLM Ingest Prompt
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
cat << 'PROMPT'
Initialize this project's AI Engineering scaffold by reading and implementing the following three reference guides, in order:

1. Read `docs/reference/llm-wiki-antigravity.md` first.
   - This sets up the LLM Wiki: a persistent, agent-maintained knowledge base.
   - Create the GEMINI.md wiki protocol sections (or equivalent agent instructions).
   - Initialize wiki/index.md, wiki/log.md, and wiki/overview.md with project context.

2. Read `docs/reference/drift-registry.md` second.
   - This sets up the Drift Registry: cross-file dependency tracking.
   - Create the GEMINI.md drift protocol sections.
   - Register initial dependencies in docs/drift_registries/.
   - Verify scripts/drift_enforcer.py is present and functional.

3. Read `docs/reference/session-workflows.md` third.
   - This sets up Session Workflows: structured open-work-close lifecycle.
   - Create .agents/workflows/session-start.md and session-wrapup.md.
   - Create the GEMINI.md session lifecycle sections.

After completing all three, run `/session-start` to begin your first structured session.
PROMPT
echo ""
echo "┌──────────────────────────────────────────────────┐"
echo "│  END OF PROMPT                                   │"
echo "└──────────────────────────────────────────────────┘"

