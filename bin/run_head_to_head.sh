#!/bin/bash
set -e

# Activate the virtual environment
source venv/bin/activate

echo "================================================="
echo "[START] Swarm vs Solo Head-to-Head Benchmarking"
echo "================================================="

for test_file in tests/comparisons/*.test.json; do
    TEST_NAME=$(jq -r --arg default "$test_file" '.eval_set_id // $default' "$test_file")
    
    echo "================================================="
    echo "Task: $TEST_NAME"
    echo "================================================="

    for MODE in "swarm" "solo"; do
        echo ">>> Executing Paradigm: [$MODE MODE] <<<"

        # 1. Clean the staging area before starting
        rm -rf .staging
        
        # 2. Run the evaluation gracefully
        # We catch the exit code natively to differentiate organic failures from user SIGINT traps.
        # Notice ADK_SWARM_MODE=$MODE injected dynamically here
        ACTIVE_TEST_ID="$TEST_NAME" PYTHONUNBUFFERED=1 HEADLESS_EVAL=true ADK_SWARM_MODE=$MODE adk eval agent_app "$test_file"
        EVAL_EXIT=$?
        if [ $EVAL_EXIT -eq 130 ] || [ $EVAL_EXIT -eq 2 ]; then
            echo "[ABORT] Evaluation brutally killed via KeyboardInterrupt. Terminating pipeline."
            exit 130
        fi
        
        # 3. Telemetry Injection
        # Syncing telemetry mapping into appropriately named files (*_swarm_eval, *_solo_eval)
        ACTIVE_TEST_ID="$TEST_NAME" ADK_SWARM_MODE=$MODE python utils/inject_telemetry.py
        
        # 4. The Memory Bridge
        rsync -av .staging/.agents/memory/ .agents/memory/ > /dev/null 2>&1 || true
        
        # 5. Telemetry Preservation
        git add docs/evals/ docs/retrospectives/ .agents/memory/ || true
        
        # 6. Amnesia Sweep
        echo "[SYSTEM] Evaluation complete. Initiating localized amnesia sweep before next paradigm..."
        git checkout -- . > /dev/null 2>&1
        git clean -fd > /dev/null 2>&1
        
        # 7. Sandbox Destruction
        rm -rf .staging
        
        echo ""
        sleep 2
    done
done

echo "================================================="
echo "[AGGREGATING] Compiling Head-to-Head Comparison Scorecard..."
python utils/generate_comparison_report.py

# Track the final scorecard
git add docs/comparisons/HEAD_TO_HEAD_SCORECARD.md || true

echo "================================================="
echo "[SUCCESS] All Head-to-Head benchmarking executed."
echo "Review the benchmark outputs using 'git status'."
