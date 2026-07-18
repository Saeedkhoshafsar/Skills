# Release v2.5.19 — Soft mid-task harness register/promote

**Date:** 2026-07-18  
**SMART pin:** `2.5.19`

## Summary

Harness-compat capture was easy to delay until after long thrash. This release
**softens the trigger**: on the first clear model↔Claude Code signal (or the second
same-class failure after one clean retry), models must **lookup → register OPEN →
recover → promote SOLVED** in the same session — including via always-on
`~/.claude/CLAUDE.md` when SMART is not active.

## What changed

| Area | Change |
|---|---|
| Always-on pointer | `ensure-user-claude-md.sh` **block-version 2** — soft mid-task + same-session promote |
| SMART protocol | Soft mid-task table; register OPEN early; same-session SOLVED; anti thrash-wait / forever-OPEN |
| Ledger | `HARNESS-COMPAT.md` “How models must use” soft loop |
| Contracts | Scenario `harness-compat-soft-midtask-register-promote` (39 total); pin tests **2.5.19** |

## Install / update (canonical four-step path)

Documented in README **Install on Claude Code** and **Updating**. Run **all** steps:

```bash
claude plugin marketplace update saeed-skills
claude plugin update smart@saeed-skills
bash ~/.claude/plugins/cache/saeed-skills/smart/2.5.19/skills/smart/scripts/ensure-user-claude-md.sh
# restart the Claude Code session
/smart:smart
```

```bash
# verify always-on pointer (expect block-version 2):
bash ~/.claude/plugins/cache/saeed-skills/smart/2.5.19/skills/smart/scripts/ensure-user-claude-md.sh --check
```

## Artifacts

| Path | Role |
|---|---|
| `skills/smart/skills/smart/scripts/ensure-user-claude-md.sh` | Block v2 soft-trigger pointer |
| `skills/smart/skills/smart/references/HARNESS-COMPAT.md` | Soft mid-task loop + ledger |
| SMART Harness section | Soft trigger table + same-session promote |
| `skills/smart/skills/smart/evals/scenarios.json` | Soft mid-task scenario |

## Out of scope

API credit, rate limits alone, auth keys, ordinary product bugs — not ledger material.

## Verification

- Offline scenarios: 39 valid
- Unit/contract suite: see CI / local `python3 -m unittest discover -s tests -v`
