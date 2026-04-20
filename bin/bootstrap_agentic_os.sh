#!/bin/bash
set -e

echo "================================================="
echo "[BOOTSTRAP] Initializing Agentic OS Memory Paths..."
echo "================================================="

# 1. Director Context Source of Truth
mkdir -p docs/director_context
if [ ! -f docs/director_context/README.md ]; then
    echo "# Architectural Source of Truth" > docs/director_context/README.md
    echo "This directory is intentionally exposed to the ADK Director via the 'list_docs' tool. Add your explicit API schemas, database bounds, and infrastructure specifications here so the Swarm has a comparative baseline to identify architectural drift." >> docs/director_context/README.md
    echo "Created docs/director_context/README.md"
else
    echo "Skipped: docs/director_context/README.md already exists."
fi

# 2. Retrospectives and Evals Paths
mkdir -p docs/evals/retrospectives
mkdir -p docs/retrospectives
echo "Created evaluation and retrospective directories."

# 3. Agents Memory Logic & State
mkdir -p .agents/memory
if [ ! -f .agents/memory/executor_handoff.md ]; then
    echo "# Ephemeral State Ledger" > .agents/memory/executor_handoff.md
    echo "The Executor is mandated to natively read this file between sandbox mutations to combat ephemeral amnesia. Append learned anti-patterns here." >> .agents/memory/executor_handoff.md
    echo "Created .agents/memory/executor_handoff.md"
else
    echo "Skipped: .agents/memory/executor_handoff.md already exists."
fi

if [ ! -f .agents/memory/vertex_rag_config.txt ]; then
    echo "YOUR_GCP_CORPUS_ID_HERE" > .agents/memory/vertex_rag_config.txt
    echo "Created .agents/memory/vertex_rag_config.txt (Update securely with your Vertex Context ID)"
else
    echo "Skipped: .agents/memory/vertex_rag_config.txt already exists."
fi

# 4. Artifacts Exchange State Route
mkdir -p artifacts
echo "Created artifacts/ handoff directory."

# 5. Staging Airlock
mkdir -p .staging
echo "Created .staging/ temporary Executor containment directory."

# 6. Testing Matrix Baseline
mkdir -p tests
if [ ! -f tests/test_baseline.py ]; then
    cat << 'INNEREOF' > tests/test_baseline.py
def test_system_baseline():
    """Baseline test to prevent pytest from exiting with exit code 5 (no tests collected)."""
    assert True
INNEREOF
    echo "Created tests/test_baseline.py for systemic Pytest verification."
else
    echo "Skipped: tests/test_baseline.py already exists."
fi

# 7. Project Workspaces
mkdir -p src
mkdir -p api
echo "Created src/ and api/ canonical output directories."

echo "================================================="
echo "[SUCCESS] Zero-Trust Operating System Bootstrapped."
echo "You may now configure your .env file and wake up the Swarm."
