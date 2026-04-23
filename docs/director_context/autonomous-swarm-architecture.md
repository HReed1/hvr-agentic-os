# Autonomous Swarm Architecture & Topography

This document maps the exact execution graph of the `autonomous_swarm` following the deployment of the **Iterative Macro-Loop** paradigm.

## Execution Graph

```mermaid
graph TD
    subgraph "Autonomous Swarm (SequentialAgent Spine)"
        
        director["<b>Director Agent</b> [LlmAgent]<br><b>Tools:</b> list_docs, read_doc, mark_system_complete<br><b>Perms:</b> Pipeline Overseer, Macro-Loop Router"]
        
        subgraph executor_loop["LoopAgent: Max 15"]
            direction LR
            executor["<b>Executor Agent</b> [LlmAgent]<br><b>Tools:</b> escalate_to_director, transfer_to_qa_engineer, Executor_MCP<br><b>Perms:</b> Natively Sandboxed file mutations inside .staging/"]
            qa["<b>QA Engineer</b> [sub_agent]<br><b>Tools:</b> escalate_to_director, execute_tdaid_test, execute_playwright_test<br><b>Perms:</b> TDAID Validation & Cryptographic Tracing"]
            
            executor -->|transfer_to_qa_engineer| qa
            qa -->|"[QA REJECTED] / [QA PASSED]"| executor
        end
        
        auditor["<b>Auditor Agent</b> [LlmAgent]<br><b>Tools:</b> Auditor_MCP, AST_Validation_MCP, get_user_choice<br><b>Perms:</b> promote_staging_area, teardown_staging_area, McCabe Score"]
        
        reporter["<b>Reporting Director</b> [LlmAgent]<br><b>Tools:</b> write_retrospective<br><b>Perms:</b> Trace Extraction & Narrative Synthesis"]
        
        director -->|Issues Directive| executor
        executor -->|"[EXECUTION COMPLETE]"| auditor
        
        auditor -->|"[AUDIT FAILED] (In-Situ Trace)"| director
        auditor -->|"[AUDIT PASSED] (promote_staging_area)"| director
        
        director -->|mark_system_complete| reporter
    end

    subgraph "Legend: ADK Classes"
        direction TB
        L1["[SequentialAgent] = Outer Routing Spine"]
        L2["[LoopAgent] = Iterative Evaluation Boundary"]
        L3["[LlmAgent] = Core Stateful Intelligence Node"]
        L4["[sub_agent] = Restricted Isolated Tasker"]
    end
```

## ADK Architecture Bindings

Our overarching Swarm topography is formally woven directly into execution constraints provided natively by the Google Agent Development Kit (ADK) framework:

- **`SequentialAgent` (The Spine)**: The primary execution pathway (`Director` → `Executor Loop` → `Auditor` → `Reporting Director`) is deployed cleanly as Python sequential boundaries, guaranteeing linear logical progression and trace isolation.
- **`LlmAgent` (The Nodes)**: The core nodes (`Director`, `Auditor`, `Reporter`) are strictly mapped as native intelligence pods bounded with specific, exclusive tool schemas.
- **`LoopAgent` (The Crucible)**: The `Executor Agent` is tightly sealed inside a distinct iteration configuration natively clamped to 15 max attempts, explicitly protecting the surrounding runtime from recursive token degradation loops.
- **`sub_agent` Delegation**: The `QA Engineer` is entirely decoupled from the central Python sequence. It operates flawlessly as a nested `sub_agent` bound to the Executor, trapping execution tracebacks localized to the testing sandbox until functional clearance resolves.

## Security Posture & Control Flows

- **The Architect Deprecation**: The legacy `Architect Agent` was structurally decommissioned. Removing the middleman explicitly prevented contextual degradation and JSON parsing bottlenecks, allowing the Director to cleanly orchestrate directives straight to the Executor.
- **The Red/Green Executor Loop**: Rather than relying on frail sequence routing, the `Executor Agent` is tightly bound within an ADK `LoopAgent`. The `QA Engineer` is mapped entirely as a specialized `sub_agent`. The Executor iterates locally upon `[QA REJECTED]` and physically controls sequence propagation by explicitly yielding `[EXECUTION COMPLETE]` only after QA clears the test suite. 
- **Auditor In-Situ Override**: The Auditor operates securely outside the localized Development Loop, enforcing AST bounds and calculating McCabe Cyclomatic Complexity directly on test-approved payloads. If an anomaly is hit (e.g., Code Complexity > 5), the Auditor outputs `[AUDIT FAILED]` but is strictly blocked from executing a full `.staging/` teardown.
- **Director Macro-Loop**: The Director natively traps `[AUDIT FAILED]` signals emitted from the Auditor and spins them back out down the execution chain. This recursive bypass is known as **In-Situ Patching**, empowering the Executor to surgically refactor functional logic iteratively directly based on the Auditor's feedback without the destructive memory wipe of earlier Swarm paradigms.
- **Zero-Trust Hard Intercept:** The overarching swarm middleware actively traps Paradox Escalations (like `escalate_to_director`). When unresolvable environment locks or logic loops are detected, the system natively aborts Swarm momentum and hard-escalates authority explicitly to the External Human Observer.
