# SMART v2.5.13 — Hermes learning-memory complete

Hermes closed-loop personalization is now part of SMART/project-memory **without**
replacing Project Mind.

## What's new

- **Dual learning memory:** `docs/USER.md` (profile) + `docs/AGENT-MEMORY.md`
  (ops lessons), bounded + threat-scanned
- **Self-learning loop:** interval nudges, memory/skill review, non-blocking
  consolidate
- **Skill self-improve + curator:** patch-on-correction, usage sidecar, archive
  never auto-delete
- **Episodic session search:** FTS5/LIKE under `.smart/sessions`, extract-durable
  before compact
- **Memory providers:** builtin / null / local SQLite; one-external limit;
  `<memory-context>` fence
- **Identity polish:** optional `docs/SOUL.md`, personality presets, dashboard,
  non-destructive migrate
- **Contract:** CLAUDE hard rule 22 — learning memory is not product truth

## Versions

| Package | Version |
|---|---|
| marketplace metadata | 2.5.13 |
| smart | 2.5.13 |
| project-memory | 1.11.0 |

## Evidence

- 217 unit tests OK (offline)
- 31 offline behavioral scenarios valid
- PR validate check GREEN

## Install / update on Claude Code

```bash
# first install
claude plugin marketplace add Saeedkhoshafsar/Skills
claude plugin install smart@saeed-skills

# update an existing install
claude plugin marketplace update saeed-skills && claude plugin update smart@saeed-skills
```

Then **restart the Claude Code session** and confirm `/plugin` shows SMART **2.5.13**.

## Explicitly deferred (Phase 9)

Messaging gateway, always-on cron, kanban multi-agent, cloud mind-clone
providers — not required for local Claude Code; activate only on owner request.
