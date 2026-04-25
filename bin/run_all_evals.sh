#!/bin/bash
set -e

# Activate the virtual environment
source venv/bin/activate

# Loop over every .test.json file defined in the testing bounds
for test_file in tests/adk_evals/*.test.json; do
    echo "================================================="
    echo "Starting Evaluation Runner: $test_file"
    echo "================================================="
    
    # 1. Clean the staging area before starting
    rm -rf .staging
    
    # 2. Run the evaluation gracefully
    TEST_NAME=$(jq -r --arg default "$test_file" '.eval_set_id // $default' "$test_file")
    CRITERIA=$(jq -r '.eval_cases[0].conversation[0].user_content.parts[0].text // "Unknown"' "$test_file")
    
    # 2. Run the evaluation gracefully
    # We catch the exit code natively to differentiate organic failures from user SIGINT traps.
    ACTIVE_TEST_ID="$TEST_NAME" PYTHONUNBUFFERED=1 HEADLESS_EVAL=true adk eval agent_app "$test_file"
    EVAL_EXIT=$?
    if [ $EVAL_EXIT -eq 130 ] || [ $EVAL_EXIT -eq 2 ]; then
        echo "[ABORT] Evaluation brutally killed via KeyboardInterrupt. Salvaging memory and artifacts before terminating..."
    fi
    
    # 2.5 Ensure organic post-evaluation trace data is merged natively into the static md structure
    ACTIVE_TEST_ID="$TEST_NAME" python utils/inject_telemetry.py
    
    
    # 3. The Memory Bridge (Ref: Evaluator Wrapup Workflow Step 2)
    # Physically reconcile internal swarm memories from the airlock back to the root.
    rsync -av .staging/.agents/memory/ .agents/memory/ > /dev/null 2>&1 || true
    
    # Playwright Media Bridge
    echo "[SYSTEM] Mirroring Playwright visual artifacts to .agents/memory/..."
    mkdir -p .agents/memory/media
    find . -path "*/test-results/*" -type f \( -name "*.png" -o -name "*.webm" -o -name "*.zip" \) 2>/dev/null | while read media_file; do
        base_name=$(basename "$media_file")
        cp "$media_file" ".agents/memory/media/global_eval_${base_name}"
    done
    
    # 4. Telemetry Preservation (Ref: Evaluator Wrapup Workflow Step 3)
    # The 'Memory Shield' stages all documentation and reconciled memories for persistence.
    git add docs/evals/ docs/retrospectives/ .agents/memory/ || true
    
    # 4.5 Air-Lock Artifact Discovery vaulting
    ARTIFACT_DIR="docs/evals/artifacts_$(basename "${TEST_NAME%.test.json}")"
    rm -rf "$ARTIFACT_DIR" && mkdir -p "$ARTIFACT_DIR"
    
    # Capture modified/untracked files (successfully promoted out of Air-Lock)
    for file in $(git ls-files --others --exclude-standard) $(git diff --name-only); do
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
                if [[ "$staged_file" == .venv/* ]] || [[ "$staged_file" == venv/* ]] || [[ "$staged_file" == *__pycache__* ]] || [[ "$staged_file" == *.pytest_cache* ]] || [[ "$staged_file" == .adk/* ]] || [[ "$staged_file" == .git/* ]] || [[ "$staged_file" == session.db* ]] || [[ "$staged_file" == docs/evals/artifacts_* ]] || [[ "$staged_file" == docs/comparisons/kanban_artifacts_* ]]; then
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
    git add "$ARTIFACT_DIR" || true
    
    # 5. Amnesia Sweep (Ref: Evaluator Wrapup Workflow Step 4)
    # Physically reset the production root codebase to prevent cross-contamination.
    echo "[SYSTEM] Evaluation complete. Initiating localized amnesia sweep..."
    git checkout -- . > /dev/null 2>&1
    git clean -fd > /dev/null 2>&1
    
    # 6. Sandbox Destruction (Ref: Evaluator Wrapup Workflow Step 5)
    rm -rf .staging
    
    # 7. Hard Pipeline Abort Execution
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
python utils/generate_global_eval_report.py

# Ensure the scorecard is tracked so it doesn't get wiped by future cleanups
git add docs/evals/GLOBAL_EVAL_SCORECARD.md || true

echo "================================================="
echo "[SUCCESS] All evaluations executed."
echo "You may now review the preserved Evaluation Artifacts using 'git status'."

