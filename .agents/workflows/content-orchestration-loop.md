---
description: The high-level orchestration loop that manages multi-post content campaigns, tracks publication state, and sequences the pipeline.
---

# Content Orchestration Loop

**Trigger:** Invoked when the Director requests a batch content generation session (e.g., "Let's document Era 4").

## Workflow Execution Steps
1. **State Discovery:** Read `master_index.json`. Scan the `docs/blog/conversations/` directory natively. 
2. **Gap Analysis:** Cross-reference the index against the existing markdown drafts. Identify which `pivots` are currently missing a corresponding `.md` file.
3. **Sequential Targeting:** Select the oldest missing pivot chronologically. Output to the Director: `[CAMPAIGN STATUS]: Identified missing narrative for Era [X], Pivot [Y]: "[TITLE]". Initiating /blog-publication-pipeline...`
4. **Handoff:** Yield control exclusively to the `/blog-publication-pipeline` for that specific commit. The Orchestration Loop MUST enter a paused state and wait for the Pipeline's `Patience Loop` interactions to conclude.
5. **Campaign Recursion:** Upon successful validation and physical markdown creation of the draft (passing the Technical Authenticity Audit), evaluate if the Director wishes to proceed to the next missing pivot, or pause the campaign.