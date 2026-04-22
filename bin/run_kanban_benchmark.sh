#!/bin/bash
set -e

# Activate the virtual environment
source venv/bin/activate

echo "================================================="
echo "[START] Deep Context Benchmark: Relational Kanban"
echo "================================================="

# Hardcode the target to the Kanaban crucible only
test_file="tests/comparisons/test_compare_fullstack.test.json"
TEST_NAME="test_compare_fullstack"

echo "================================================="
echo "Task: $TEST_NAME"
echo "================================================="

# for MODE in "solo" "swarm"; do
for MODE in "swarm"; do
    echo ">>> Executing Paradigm: [$MODE MODE] <<<"

    # 1. Clean the staging area before starting
    rm -rf .staging
    
    # 2. Run the evaluation gracefully
    ACTIVE_TEST_ID="$TEST_NAME" PYTHONUNBUFFERED=1 HEADLESS_EVAL=true ADK_SWARM_MODE=$MODE adk eval agent_app "$test_file"
    EVAL_EXIT=$?
    if [ $EVAL_EXIT -eq 130 ] || [ $EVAL_EXIT -eq 2 ]; then
        echo "[ABORT] Evaluation brutally killed via KeyboardInterrupt. Terminating pipeline."
        exit 130
    fi
    
    # 3. Telemetry Injection
    ACTIVE_TEST_ID="$TEST_NAME" ADK_SWARM_MODE=$MODE python utils/inject_telemetry.py
    
    # 4. The Memory Bridge
    rsync -av .staging/.agents/memory/ .agents/memory/ > /dev/null 2>&1 || true
    
    # 5. Telemetry Preservation
    git add docs/evals/ docs/retrospectives/ .agents/memory/ || true
    
    # Extract Generated Artifacts Before Amnesia Sweep
    echo "[SYSTEM] Auto-vaulting generated artifacts into docs/comparisons/kanban_artifacts_$MODE/..."
    ARTIFACT_DIR="docs/comparisons/kanban_artifacts_$MODE"
    rm -rf "$ARTIFACT_DIR" && mkdir -p "$ARTIFACT_DIR"
    
    # Capture modified/untracked files (successfully promoted out of Air-Lock)
    for file in $(git ls-files --others --exclude-standard) $(git diff --name-only); do
        if [[ "$file" == api/* ]] || [[ "$file" == tests/* ]] || [[ "$file" == bin/* ]] || [[ "$file" == *.py ]]; then
            mkdir -p "$ARTIFACT_DIR/$(dirname "$file")"
            cp "$file" "$ARTIFACT_DIR/$file" 2>/dev/null || true
        fi
    done
    
    # Capture anything aggressively stranded in the Air-Lock dynamically
    if [ -d ".staging" ]; then
        (
            cd .staging || exit 0
            for staged_file in $(find . -type f | sed 's/^\.\///'); do
                # Aggressively filter out systemic environments and caches
                if [[ "$staged_file" == .venv/* ]] || [[ "$staged_file" == venv/* ]] || [[ "$staged_file" == *__pycache__* ]] || [[ "$staged_file" == *.pytest_cache* ]] || [[ "$staged_file" == .adk/* ]] || [[ "$staged_file" == .git/* ]] || [[ "$staged_file" == session.db* ]] || [[ "$staged_file" == docs/comparisons/kanban_artifacts_* ]]; then
                    continue
                fi
                
                # Vault the file if it was explicitly modified or physically created by the Swarm
                if ! cmp -s "$staged_file" "../$staged_file" 2>/dev/null; then
                    mkdir -p "../$ARTIFACT_DIR/$(dirname "$staged_file")"
                    cp "$staged_file" "../$ARTIFACT_DIR/$staged_file"
                fi
            done
        )
    fi
    
    # Pre-emptively stage the isolated artifact vault so `git clean -fd` doesn't destroy it!
    git add "$ARTIFACT_DIR" || true
    
    # 6. Amnesia Sweep
    echo "[SYSTEM] Evaluation complete. Initiating localized amnesia sweep before next paradigm..."
    git checkout -- . > /dev/null 2>&1
    git clean -fd > /dev/null 2>&1
    
    # 7. Sandbox Destruction
    rm -rf .staging
    
    echo ""
    sleep 2
done

echo "================================================="
echo "[AGGREGATING] Compiling Head-to-Head Comparison Scorecard..."
python utils/generate_comparison_report.py

# Track the final scorecard
git add docs/comparisons/HEAD_TO_HEAD_SCORECARD.md || true

echo "================================================="
echo "[SUCCESS] Kanban benchmark executed."
echo "Review the benchmark outputs using 'git status'."
