---
description: A strategic parsing skill designed to generate targeted interview questions that extract human friction, emotional context, and architectural 'Aha!' moments from the Director.
---

# Narrative Extraction Engine

**Trigger:** Invoked during Phase 1 of the `/blog-publication-pipeline`.

## Execution Logic
When parsing a target commit and its surrounding retrospectives, do not simply summarize the technical changes. You must formulate exactly **3 Targeted Interview Questions** for the Human Director using the following matrix:

1. **Question 1 (The Friction):** Identify the failing state before the commit. Ask the Director to describe the visceral pain, financial anxiety (FinOps), or orchestration chaos (e.g., Zombie Spin-Loops, Race Conditions) that forced the pivot.
2. **Question 2 (The Architecture):** Identify the structural mechanism deployed to fix it. Ask the Director about the philosophical decision-making process (e.g., "Why did you choose ADK 2.0 over oh-my-codex?" or "Why mandate TDAID?").
3. **Question 3 (The Breakthrough):** Identify the moment of resolution. Ask the Director to describe the specific "Aha!" moment when the new constraint or code successfully altered the system's behavior (e.g., the relief of a pipeline self-healing from an Exit 137).

## The Pushback Protocol
If the Director's response to the interview contains fewer than 100 words or consists primarily of Markdown file links, **DO NOT PROCEED TO DRAFTING**. 
Output: `[DIRECTOR OVERRIDE REQUIRED]: The provided context lacks sufficient narrative depth. Please explicitly clarify the human friction and architectural reasoning before I synthesize the draft.`
*Escape Hatch:* If the Director explicitly issues a "Tactical Override", `[EXECUTION APPROVED]`, or orders a force-bypass, immediately yield the pushback constraint and synthesize the draft using the limited context provided.