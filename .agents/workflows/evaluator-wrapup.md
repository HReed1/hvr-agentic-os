# Evaluator Wrapup Workflow

**Purpose**: Natively automate the transition between an active evaluation and the clean system reset ('Amnesia') while preventing agentic amnesia via the Memory Bridge.

## Execution Steps

### 1. Pre-Flight Reporting `[AGENT DUTY]`
- **The Meta-Evaluator**: 
    - MUST call `write_eval_report`.
    - MUST explicitly determine the `is_passing: bool` technical verdict.
- **The Reporting Director**:
    - MUST call `write_retrospective` to synthesize the narrative engineering summary.
- **Handoff Finality**: The last agent in the sequence must output the termination string: `[EVALUATION COMPLETE]`.

---

### 2. The Memory Bridge `[SYSTEM AUTOMATION]`
- **Action**: `rsync -av .staging/.agents/memory/ .agents/memory/ || true`
- **Goal**: Synchronize any memories generated inside the throwaway sandbox back to the project root before the sandbox is destroyed.
- **Context**: This ensures that even failed swarms leave their experience behind for future iterations.

### 3. Telemetry Preservation `[SYSTEM AUTOMATION]`
- **Targets**: `docs/evals/`, `docs/retrospectives/`, `.agents/memory/`.
- **Action**: `git add <targets>` to stage documentation and memories for persistence.

### 4. Amnesia Sweep `[SYSTEM AUTOMATION]`
- **Target**: Entire root workspace.
- **Action 1**: `git checkout -- .` (Purges promoted code changes and reverted mutations).
- **Action 2**: `git clean -fd` (Purges untracked test files and orphaned logs).

### 5. Sandbox Destruction `[SYSTEM AUTOMATION]`
- **Action**: `rm -rf .staging` to ensure safe, zero-trust cleanup for the next case.

---

## Legend
- **`[AGENT DUTY]`**: These steps are performed by the Meta-Evaluator during its execution turn.
- **`[SYSTEM AUTOMATION]`**: These steps are hard-coded in the bash environment (`bin/run_all_evals.sh`) and execute automatically AFTER the agent process terminates.

> [!CAUTION]
> The Meta-Evaluator is strictly forbidden from attempting `[SYSTEM AUTOMATION]` steps. Attempting to manage the physical workspace reset via LLM tool calls will cause race conditions and telemetry corruption.
