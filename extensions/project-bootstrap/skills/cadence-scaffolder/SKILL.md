---
name: cadence-scaffolder
description: Scaffolds the standalone Firestore Cadence CLI (scripts/cadence.py) targeting general-477613, enforcing collection isolation, 3-tier hierarchy, domain phases, and weekly sync rituals.
---

# Cadence Scaffolder

> **Domain:** Engineering & Creative Cadence Engine  
> **Purpose:** Generate a standalone, resilient CLI tool (`scripts/cadence.py`) managing 3-tier goal lifecycles in Google Cloud Firestore (`general-477613`).

## Architectural Invariants

1. **Firestore Collection Isolation**:
   Operates exclusively within `<project_slug>_goals`. Never touches `nexus_goals` or sibling project collections.
2. **Three-Tier Hierarchy**:
   - `monthly`: High-level strategic objectives.
   - `weekly`: Deliverable-focused sprints.
   - `daily`: Atomic work sessions.
3. **Strict Domain Phase Validation**:
   Phase transitions must adhere to valid domain phases for the workspace archetype. Invalid phases exit with status code 1. Cross-domain transitions require `--force`.
4. **Weekly Ritual Automation**:
   - `python3 scripts/cadence.py saturday-sync`: Summarizes week's accomplishments, completed goals, and throughput.
   - `python3 scripts/cadence.py week-plan`: Generates next week's sprint schedule and deliverable roadmap.

## CLI Commands Provided

```bash
# Create a goal
python3 scripts/cadence.py create --title "<Title>" --scope daily --phase <phase> [--parent <parent_id>]

# List goals
python3 scripts/cadence.py list [--scope <scope>] [--status <status>]

# Show goal details
python3 scripts/cadence.py show <goal_id>

# Advance phase
python3 scripts/cadence.py advance <goal_id> --phase <next_phase>

# Complete / Defer / Delete
python3 scripts/cadence.py complete <goal_id>
python3 scripts/cadence.py defer <goal_id> [--reason "<reason>"]
python3 scripts/cadence.py delete <goal_id> [-y]

# Rituals
python3 scripts/cadence.py saturday-sync [--save]
python3 scripts/cadence.py week-plan [--save]
```
