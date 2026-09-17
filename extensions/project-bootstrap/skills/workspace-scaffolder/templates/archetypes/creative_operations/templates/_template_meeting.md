---
title: "Sync: {{date}}"
date: "{{date}}"
category: meeting
meeting_type: sync
cadence_cycle: "{{cycle}}"
facilitator: "{{author_name}}"
attendees:
  - "{{author_name}}"
cadence_scope: weekly
active_milestone_ids:
  - goal_monthly_milestone_01
active_sprint_ids:
  - goal_weekly_sprint_01
active_project_ids:
  - "[[projects/project-name]]"
goals_completed_count: 0
goals_in_progress_count: 0
goals_deferred_count: 0
tags:
  - meeting
  - cadence
  - ritual
sources:
  - "[[wiki/overview.md]]"
---

# Ritual: Progress Sync — {{date}}

> **Sync Abstract**: Periodic operational review analyzing throughput, phase progression, Cadence accounting, and technical debt.

---

## 1. Strategic Cadence Alignment (`{{firestore_collection}}`)

| Cadence Tier | Active Goal Title | Document ID | Current Status |
|---|---|---|---|
| **Monthly Milestone** | Core Milestone 01 | `goal_monthly_milestone_01` | `in_progress` |
| **Weekly Sprint** | Weekly Sprint 01 | `goal_weekly_sprint_01` | `in_progress` |

---

## 2. Production & Phase Progression

| Project | Pipeline | Phase Advanced | Deliverable Accomplished |
|---|---|---|---|
| `[[projects/project-name]]` | Main Pipeline | `phase_start` $\rightarrow$ `phase_target` | Core deliverables advanced |

---

## 3. Cadence Goal Accounting

### Completed Goals
- [x] **Goal `[goal_id_01]`**: Initialized deliverables.

### In-Progress Goals
- [/] **Goal `[goal_id_02]`**: Continuing active execution.

---

## 4. Risks, Blockers & Open Items
- Note any storage, permission, or dependency blockers.
