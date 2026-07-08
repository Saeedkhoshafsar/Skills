---
name: project-planner
description: >
  Professional project planning from zero. Interviews the user with targeted
  questions, assesses project size (S/M/L), selects the required layers from a
  13-layer checklist, and produces docs/PLAN.md with atomic tasks + acceptance
  criteria + an executable verify command per task. Use when the project is
  empty or the user asks for a plan / roadmap / "پلن".
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Project Planner

**Output:** `docs/PLAN.md` — an ordered list of atomic tasks that a memory-less agent can pick up and build correctly.

## Execution Cycle

### Step 1 — Interview (max 7 questions, ask ALL in one message)

| # | Topic | Question |
|---|---|---|
| 1 | What | What is the product? What end-user problem does it solve? |
| 2 | Who | Who are the users? How many? (scale) |
| 3 | Where | Web / mobile / bot / CLI / API? |
| 4 | Scope | MVP or full product? Deadline? |
| 5 | Stack | Preferred stack or agent's choice? |
| 6 | Money | Payments/subscriptions? (drives Auth + Security layers) |
| 7 | Future | Growth vision? (drives Scaling layers) |

### Step 2 — Size the project (pick one from the answers)

| Size | Meaning | Layers |
|---|---|---|
| S | Personal script/tool | 3-4 layers |
| M | MVP / small product | 6-8 layers |
| L | Serious/commercial product | up to 13 layers |

### Step 3 — Select layers from the 13-layer checklist

For each layer decide: needed? in which phase?

| # | Layer | Covers |
|---|---|---|
| 1 | Frontend | UI/UX |
| 2 | APIs & Backend Logic | server logic |
| 3 | Database & Storage | product data |
| 4 | Auth & Permissions | login and access levels |
| 5 | Hosting & Deployment | where it runs |
| 6 | Cloud & Compute | compute resources |
| 7 | CI/CD & Version Control | git and pipelines |
| 8 | Security & RLS | data security |
| 9 | Rate Limiting | abuse prevention |
| 10 | Caching & CDN | speed |
| 11 | Load Balancing & Scaling | scale |
| 12 | Error Tracking & Logs | error visibility |
| 13 | Availability & Recovery | backup and restore |

Layer selection by size:
- **S**: layers 2, 3, 7 (+1 if it has a UI)
- **M**: S layers + 1, 4, 5, 12
- **L**: all — but phased (layers 9-11, 13 in the last phases)

### Step 4 — Write docs/PLAN.md using the atomic template

```markdown
# <Project Name> — Execution Plan

> Ordered list of atomic tasks. Each task: Files + Accept criteria + Verify command.
> A memory-less agent must be able to pick the "-> current" task from docs/STATE.md and build it.

## Locked Stack
| Package | Version | Role |
|---|---|---|

## Task ID convention: `P<phase>-T<number>`

# PHASE 0 — Foundation
### P0-T1 - <task title>
**Files:** <exact files to create/modify>
**Accept:**
- <measurable criterion 1>
- <measurable criterion 2>
**Verify:** `<executable command, e.g. npm run verify>`
```

## Plan Quality Rules

1. Every task must be completable in **one working session** (atomic).
2. Every task has an **executable Verify** — never "looks good".
3. Phase 0 is always: skeleton + type contracts + database + test runner.
4. After user approval, immediately invoke `project-memory` to create STATE.md.
