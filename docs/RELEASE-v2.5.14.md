# SMART v2.5.14 — Discovery elevation (landscape + budget×quality)

Elevate discovery so real projects research the landscape and set a budget×quality
bar **before** Vision Lock and code — without turning SMART into MetaGPT or a
multi-agent software-company runtime.

## What's new

- **Stage 1.5 — Landscape research** (project-planner): competitors, similar public
  repos, substitutes, cost-of-quality; claims land in `docs/RESEARCH.md` and only
  decision-changing facts promote into Project Mind
- **Budget × quality bar**: money / time / skill floor + quality ceiling;
  best-within-budget, not unlimited excellence
- **Vision Lock gates**: landscape coverage (or explicit N/A) and budget×quality
  when relevant — no plan/code while these are open
- **Specialist routing**: landscape researcher lens; host `/deep-research`,
  `ui-ux-pro-max`, marketing/SEO catalog paths when the decision needs them
- **Non-goal locked**: SMART-shaped protocols only — no permanent agent cast,
  no multi-agent company simulation, max-3 capabilities unchanged

## Versions

| Package | Version |
|---|---|
| marketplace metadata | 2.5.14 |
| smart | 2.5.14 |
| project-planner | 1.4.0 |
| project-memory | 1.11.0 (unchanged) |

## Evidence

- 218 unit tests OK (offline)
- 33 offline behavioral scenarios valid
- PR #23 validate check GREEN
- Merged commit `22b6642`

## Install / update on Claude Code

```bash
# first install
claude plugin marketplace add Saeedkhoshafsar/Skills
claude plugin install smart@saeed-skills

# update an existing install
claude plugin marketplace update saeed-skills && claude plugin update smart@saeed-skills
```

Then **restart the Claude Code session** and confirm `/plugin` shows SMART **2.5.14**.

## Explicitly deferred

- Phase 9 product-surface backlog (messaging, always-on cron, kanban, …) — owner
  opt-in only for local Claude Code
- Optional dedicated DB-schema skill — only if product DB design keeps recurring
- MetaGPT-style multi-agent company runtime — permanent non-goal
