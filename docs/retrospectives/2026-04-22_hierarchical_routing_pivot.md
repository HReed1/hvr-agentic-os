# Retrospective: The Hierarchical Routing Pivot
**Date**: April 22, 2026
**Theme**: Escaping the Token Tax via Native ADK `SequentialAgent` Structuring.

## 1. The Bottleneck: The "Token Tax" Paradox
During our recent Fullstack Kanban Benchmarks outlined in our [Swarm Crucible Retrospective](file:///Users/harrisonreed/Projects/hvr-agentic-os/docs/retrospectives/2026-04-22_the_swarm_crucible_retrospective.md), we discovered a fatal flaw in the legacy Swarm architecture.

Our original design relied on forcing all entities (Architect, Executor, QA Engineer) into a single, massive recursive `LoopAgent`. While this allowed the agents to converse dynamically, the underlying framework appended the entire JSON conversational trace payload recursively down the graph on every single turn. This context bloat mathematically shattered the `get_latest_adk_session` tool constraints during Meta-Evaluations and led to severe operational "Token Tax" timeouts on smaller models natively.

To bypass this temporarily, we forged a "Hybrid Executor" class—fusing the QA Engineer and Executor into a single massive prompt to reduce node-to-node chatter. But this sacrificed the philosophical boundary of Test-Driven AI isolation.

## 2. Research Breakthrough: The `SequentialAgent` Pattern
Relying on the [Implementation Plan](file:///Users/harrisonreed/.gemini/antigravity/brain/d68dd00e-e92f-43b3-a9d5-e4b697237f5c/implementation_plan.md), the Orchestrator (Antigravity) analyzed the official ADK `hierarchical-workflow-automation` examples.

We identified a native framework superpower:

* **Explicit Sub-Routing (`transfer_to_`)**: Instead of relying on string parsing and custom python interceptors (like our legacy `.qa_signature` overrides), ADK natively supports `transfer_to_` graph mappings dynamically generated based on parent-child `sub_agent` relationships.
* **The `SequentialAgent`**: Rather than a `LoopAgent` encapsulating chatter, a `SequentialAgent` structurally cascades the output of one agent as the direct execution input to the next organically.

## 3. The Re-Architecture Sequence

### The Surgical Handoff
To build the tree natively, we executed a clean, targeted `git checkout cdc2673~1` targeting precisely `agent_app/agents.py`, `agent_app/prompts.py`, `agent_app/tools.py`, and `agent_app/zero_trust.py`. This safely resurrected our dedicated QA Engineer organically without triggering an `Amnesia Sweep` protocol that would have vaporized our `.agents/memory` and global retrospectives.

### Wiring The Tree (`agent_app/agents.py`)
We fundamentally shifted the global array from loops to a natively nested execution tree:

1. **Nested Validation Loop**: We explicitly positioned the QA Engineer underneath the Executor as an inner loop node.
   `executor_agent = Agent(..., sub_agents=[qa_engineer])`
2. **The Sequential Workflow**: We decoupled the core development matrix to inherently run strictly side-by-side using the native sequential graph.
   `development_workflow = SequentialAgent(..., sub_agents=[architect_agent, executor_agent])`
3. **The Director Router**: Finally, we nested the execution branches under the top-level orchestration nodes.
   `director_agent = Agent(..., sub_agents=[development_workflow, auditor_agent])`

### Purging Zero-Trust Bloat
With true native state cascading, we no longer required the brute-force python interceptors `approve_staging_qa` and `mark_qa_passed`. The framework implicitly returns `[SUCCESS]` up the routing tree organically. 

These bespoke constraints were aggressively ripped out of `.agents/rules/`, `.agents/workflows/`, and `agent_app/zero_trust.py`, synchronizing the markdown memory array strictly to the native Python constraints (`transfer_to_development_workflow`).

## 4. Next Actions
Executing Phase 4. We will deploy the Swarm against the Fullstack Kanban E2E suite to structurally verify that Hierarchical Routing achieves the performance of a Solo Agent while retaining structural Zero-Trust segmentation.
