#!/bin/bash
set -e

# Activate the virtual environment
source venv/bin/activate

echo "================================================="
echo "[START] Swarm vs Solo Head-to-Head Benchmarking"
echo "================================================="

for test_file in tests/adk_evals/comparisons/*.test.json; do
    TEST_NAME=$(jq -r --arg default "$test_file" '.eval_set_id // $default' "$test_file")
    
    echo "================================================="
    echo "Task: $TEST_NAME"
    echo "================================================="

    for MODE in "solo" "swarm"; do
        echo ">>> Executing Paradigm: [$MODE MODE] <<<"

        # 1. Clean the staging area before starting
        rm -rf .staging
        
        # 1.5. Purge Ghost Telemetry
        # Ensures that the Meta-Evaluator and inject_telemetry scripts don't query a bloated SQLite ledger.
        rm -f agent_app/.adk/session.db*
        
        # 2. Run the evaluation gracefully
        # We catch the exit code natively to differentiate organic failures from user SIGINT traps.
        # Notice ADK_SWARM_MODE=$MODE injected dynamically here
        ACTIVE_TEST_ID="$TEST_NAME" PYTHONUNBUFFERED=1 HEADLESS_EVAL=true ADK_SWARM_MODE=$MODE adk eval agent_app "$test_file"
        EVAL_EXIT=$?
        if [ $EVAL_EXIT -eq 130 ] || [ $EVAL_EXIT -eq 2 ]; then
            echo "[ABORT] Evaluation brutally killed via KeyboardInterrupt. Salvaging memory and artifacts before terminating..."
        fi
        
        # 3. Telemetry Injection
        # Syncing telemetry mapping into appropriately named files (*_swarm_eval, *_solo_eval)
        ACTIVE_TEST_ID="$TEST_NAME" ADK_SWARM_MODE=$MODE python utils/inject_telemetry.py
        
        # 4. The Memory Bridge
        rsync -av .staging/.agents/memory/ .agents/memory/ > /dev/null 2>&1 || true
        
        # Playwright Media Bridge
        echo "[SYSTEM] Mirroring Playwright visual artifacts to .agents/memory/..."
        mkdir -p .agents/memory/media
        find . -path "*/test-results/*" -type f \( -name "*.png" -o -name "*.webm" -o -name "*.zip" \) 2>/dev/null | while read media_file; do
            base_name=$(basename "$media_file")
            cp "$media_file" ".agents/memory/media/${MODE}_head2head_${base_name}"
        done
        
        # 5. Telemetry Preservation
        git add docs/evals/ docs/retrospectives/ .agents/memory/ || true
        
        # 5.5 Air-Lock Artifact Discovery vaulting
        ARTIFACT_DIR="docs/comparisons/artifacts_${MODE}_$(basename "${TEST_NAME%.test.json}")"
        rm -rf "$ARTIFACT_DIR" && mkdir -p "$ARTIFACT_DIR"
        
        # Capture modified/untracked files (successfully promoted out of Air-Lock)
        for file in $(git ls-files --others --exclude-standard) $(git diff --name-only); do
            if [[ "$file" == docs/comparisons/artifacts_* ]] || [[ "$file" == docs/evals/artifacts_* ]]; then
                continue
            fi
            if [[ "$file" == api/* ]] || [[ "$file" == tests/* ]] || [[ "$file" == bin/* ]] || [[ "$file" == test-results/* ]] || [[ "$file" == *.py ]]; then
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
                    if [[ "$staged_file" == .venv/* ]] || [[ "$staged_file" == venv/* ]] || [[ "$staged_file" == *__pycache__* ]] || [[ "$staged_file" == *.pytest_cache* ]] || [[ "$staged_file" == .adk/* ]] || [[ "$staged_file" == .git/* ]] || [[ "$staged_file" == session.db* ]] || [[ "$staged_file" == docs/evals/artifacts_* ]] || [[ "$staged_file" == docs/comparisons/artifacts_* ]] || [[ "$staged_file" == docs/comparisons/kanban_artifacts_* ]]; then
                        continue
                    fi
                    
                    # Vault the file if it was explicitly modified or physically created by the Swarm or Solo agent
                    if ! cmp -s "$staged_file" "../$staged_file" 2>/dev/null; then
                        mkdir -p "../$ARTIFACT_DIR/$(dirname "$staged_file")"
                        cp "$staged_file" "../$ARTIFACT_DIR/$staged_file"
                    fi
                done
            )
        fi
        git add "$ARTIFACT_DIR" || true
        
        # 6. Amnesia Sweep
        echo "[SYSTEM] Evaluation complete. Initiating localized amnesia sweep before next paradigm..."
        git checkout -- . > /dev/null 2>&1
        git clean -fd > /dev/null 2>&1
        
        # 7. Sandbox Destruction
        rm -rf .staging
        
        # 8. Hard Pipeline Abort Execution
        if [ $EVAL_EXIT -eq 130 ] || [ $EVAL_EXIT -eq 2 ]; then
            echo "[TERMINATED] Soft-abort complete. Exiting with Code 130."
            exit 130
        fi
        
        echo ""
        sleep 2
    done
done

echo "================================================="
echo "[AGGREGATING] Compiling Head-to-Head Comparison Scorecard..."
python utils/generate_comparison_report.py

# Track the final scorecard
git add docs/comparisons/HEAD_TO_HEAD_SCORECARD.md || true

echo "[AGGREGATING] Compiling global evaluation scorecard..."
python utils/generate_global_eval_report.py
git add docs/evals/GLOBAL_EVAL_SCORECARD.md || true

echo "================================================="
echo "[SUCCESS] All Head-to-Head benchmarking executed."
echo "Review the benchmark outputs using 'git status'."
