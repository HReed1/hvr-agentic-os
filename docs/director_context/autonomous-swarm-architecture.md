# Autonomous Swarm Architecture & Topography

This document maps the exact, flattened execution graph of the `autonomous_swarm` following the Zero-Trust Decapitation refactoring.

## Execution Graph

```mermaid
graph TD
    subgraph "Autonomous Swarm (Sequential Sequence)"
        
        subgraph "Director Loop (Max Iterations: 10)"
            direction TB
            
            director["<b>Director Agent</b><br><b>Tools:</b> list_docs, read_doc, mark_system_complete<br><b>Perms:</b> Root Pipeline Overseer, Workflow Translation"]
            architect["<b>Architect Agent</b><br><b>Tools:</b> list_docs, read_doc, escalate_to_director<br><b>Perms:</b> Blast Radius Evaluation, JSON Task Generation"]
            
            subgraph "Development Loop (Max Iterations: 10)"
                direction LR
                executor["<b>Executor Agent</b><br><b>Tools:</b> escalate_to_director, Executor_MCP<br><b>Perms:</b> Natively Sandboxed file mutations inside .staging/"]
                qa["<b>QA Engineer</b><br><b>Tools:</b> escalate_to_director, mark_qa_passed, AST_Validation_MCP<br><b>Perms:</b> execute_tdaid_test, execute_coverage_report"]
                
                executor <-->|Red / Green Loop| qa
            end
            
            auditor["<b>Auditor Agent</b><br><b>Tools:</b> Auditor_MCP, AST_Validation_MCP, get_user_choice<br><b>Perms:</b> promote_staging_area, teardown_staging_area, McCabe Score"]
            
            director -->|Issues Directive| architect
            architect -->|Emits JSON Task| executor
            qa -->|mark_qa_passed| auditor
            auditor -.->|Escalates PASS/FAIL| director
        end
        
        reporter["Reporting Director<br><b>Tools:</b> write_retrospective<br><b>Perms:</b> Session Timeline Extraction"]
        
        director -->|mark_system_complete| reporter
    end
```

## Security Posture
- **Architect Decapitation:** The Architect physically lacks the `approve_staging_qa` tool and sits outside the backwards-facing evaluation stream. It cannot intercept payloads from QA.
- **QA Isolation:** The QA Engineer physically lacks deployment tools and cannot mutate code. It only controls the cryptographic `.qa_signature` loop gate.
- **Auditor Promotion Guard:** The Auditor operates securely outside the `Development Loop`, enforcing AST bounds natively on test-approved payloads before modifying the host system.
