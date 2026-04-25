#!/bin/bash
set -e

# Run only the failed evaluations identified by GLOBAL_EVAL_SCORECARD.md
# Usage: ./bin/run_failed_evals.sh

source venv/bin/activate

SCORECARD="docs/evals/GLOBAL_EVAL_SCORECARD.md"

if [ ! -f "$SCORECARD" ]; then
    echo "[ERROR] No scorecard found at $SCORECARD. Run ./bin/run_all_evals.sh first."
    exit 1
fi

# Extract failed test names from the scorecard
# macOS grep doesn't support -P, so we use sed for extraction
FAILED_TESTS=$(grep "❌ FAIL" "$SCORECARD" | sed 's/.*`\(.*\)`.*/\1/' | sed 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_//' | sed 's/_swarm_eval\.md$//' | sed 's/_solo_eval\.md$//')

if [ -z "$FAILED_TESTS" ]; then
    echo "[SUCCESS] No failed evaluations found. All tests passed!"
    exit 0
fi

echo "================================================="
echo "[RETRY] Re-running failed evaluations only:"
for name in $FAILED_TESTS; do
    echo "  - $name"
done
echo "================================================="
echo ""

for name in $FAILED_TESTS; do
    test_file="tests/adk_evals/${name}.test.json"
    
    if [ ! -f "$test_file" ]; then
        echo "[WARN] Test file not found: $test_file — skipping."
        continue
    fi
    
    echo "================================================="
    echo "Starting Evaluation Runner: $test_file"
    echo "================================================="
    
    # 1. Clean the staging area
    rm -rf .staging
    
    # 2. Run the evaluation
    TEST_NAME=$(jq -r --arg default "$test_file" '.eval_set_id // $default' "$test_file")
    
    ACTIVE_TEST_ID="$TEST_NAME" PYTHONUNBUFFERED=1 HEADLESS_EVAL=true adk eval agent_app "$test_file"
    EVAL_EXIT=$?
    if [ $EVAL_EXIT -eq 130 ] || [ $EVAL_EXIT -eq 2 ]; then
        echo "[ABORT] Evaluation killed via KeyboardInterrupt."
    fi
    
    # 2.5 Merge telemetry
    ACTIVE_TEST_ID="$TEST_NAME" python scripts/inject_telemetry.py
    
    # 3. Memory Bridge
    rsync -av .staging/.agents/memory/ .agents/memory/ > /dev/null 2>&1 || true
    
    # Playwright Media Bridge
    echo "[SYSTEM] Mirroring Playwright visual artifacts to .agents/memory/..."
    mkdir -p .agents/memory/media
    find . -path "*/test-results/*" -type f \( -name "*.png" -o -name "*.webm" -o -name "*.zip" \) 2>/dev/null | while read media_file; do
        base_name=$(basename "$media_file")
        cp "$media_file" ".agents/memory/media/global_eval_${base_name}"
    done
    
    # 4. Telemetry Preservation
    git add docs/evals/ docs/retrospectives/ .agents/memory/ || true
    
    # 4.5 Artifact vaulting
    ARTIFACT_DIR="docs/evals/artifacts_$(basename "${TEST_NAME%.test.json}")"
    rm -rf "$ARTIFACT_DIR" && mkdir -p "$ARTIFACT_DIR"
    
    for file in $(git ls-files --others --exclude-standard) $(git diff --name-only); do
        if [[ "$file" == api/* ]] || [[ "$file" == tests/* ]] || [[ "$file" == bin/* ]] || [[ "$file" == test-results/* ]] || [[ "$file" == *.py ]]; then
            mkdir -p "$ARTIFACT_DIR/$(dirname "$file")"
            cp "$file" "$ARTIFACT_DIR/$file" 2>/dev/null || true
        fi
    done
    
    if [ -d ".staging" ]; then
        (
            cd .staging || exit 0
            for staged_file in $(find . -type f | sed 's/^\.\///'); do
                if [[ "$staged_file" == .venv/* ]] || [[ "$staged_file" == venv/* ]] || [[ "$staged_file" == *__pycache__* ]] || [[ "$staged_file" == *.pytest_cache* ]] || [[ "$staged_file" == .adk/* ]] || [[ "$staged_file" == .git/* ]] || [[ "$staged_file" == session.db* ]] || [[ "$staged_file" == docs/evals/artifacts_* ]] || [[ "$staged_file" == docs/comparisons/kanban_artifacts_* ]]; then
                    continue
                fi
                if ! cmp -s "$staged_file" "../$staged_file" 2>/dev/null; then
                    mkdir -p "../$ARTIFACT_DIR/$(dirname "$staged_file")"
                    cp "$staged_file" "../$ARTIFACT_DIR/$staged_file"
                fi
            done
        )
    fi
    git add "$ARTIFACT_DIR" || true
    
    # 5. Amnesia Sweep
    echo "[SYSTEM] Evaluation complete. Initiating localized amnesia sweep..."
    git checkout -- . > /dev/null 2>&1
    git clean -fd > /dev/null 2>&1
    
    # 6. Sandbox Destruction
    rm -rf .staging
    
    # 7. Abort check
    if [ $EVAL_EXIT -eq 130 ] || [ $EVAL_EXIT -eq 2 ]; then
        echo "[TERMINATED] Soft-abort complete. Exiting with Code 130."
        exit 130
    fi
    
    echo "Workspace fully reset. Moving to next evaluation."
    echo ""
    sleep 2
done

echo "================================================="
echo "[AGGREGATING] Compiling global evaluation scorecard..."
python scripts/generate_global_eval_report.py

git add docs/evals/GLOBAL_EVAL_SCORECARD.md || true

echo "================================================="
echo "[SUCCESS] Failed evaluation retries complete."
echo "You may now review the preserved Evaluation Artifacts using 'git status'."
