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
    # We catch the exit code natively to differentiate organic failures from user SIGINT traps.
    PYTHONUNBUFFERED=1 HEADLESS_EVAL=true adk eval agent_app "$test_file"
    EVAL_EXIT=$?
    if [ $EVAL_EXIT -eq 130 ] || [ $EVAL_EXIT -eq 2 ]; then
        echo "[ABORT] Evaluation brutally killed via KeyboardInterrupt. Terminating pipeline."
        exit 130
    fi
    TEST_NAME=$(jq -r --arg default "$test_file" '.eval_set_id // $default' "$test_file")
    CRITERIA=$(jq -r '.eval_cases[0].conversation[0].user_content.parts[0].text // "Unknown"' "$test_file")
    
    
    # 3. The Memory Bridge (Ref: Evaluator Wrapup Workflow Step 2)
    # Physically reconcile internal swarm memories from the airlock back to the root.
    rsync -av .staging/.agents/memory/ .agents/memory/ > /dev/null 2>&1 || true
    
    # 4. Telemetry Preservation (Ref: Evaluator Wrapup Workflow Step 3)
    # The 'Memory Shield' stages all documentation and reconciled memories for persistence.
    git add docs/evals/ docs/retrospectives/ .agents/memory/ || true
    
    # 5. Amnesia Sweep (Ref: Evaluator Wrapup Workflow Step 4)
    # Physically reset the production root codebase to prevent cross-contamination.
    echo "[SYSTEM] Evaluation complete. Initiating localized amnesia sweep..."
    git checkout -- . > /dev/null 2>&1
    git clean -fd > /dev/null 2>&1
    
    # 6. Sandbox Destruction (Ref: Evaluator Wrapup Workflow Step 5)
    rm -rf .staging
    
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

