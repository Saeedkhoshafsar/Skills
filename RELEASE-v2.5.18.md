# Release v2.5.18 — Harness compatibility ledger

**Date:** 2026-07-18  
**SMART pin:** `2.5.18`

## Summary

Non-Anthropic and mixed-proxy models running inside Claude Code often hit **runtime
mismatches** (illegal content blocks, tool-loop shape, slash namespaces, plugin paths).
This release makes recovery **lookup-first and durable**:

1. Always-on pointer in `~/.claude/CLAUDE.md` (every project, no SMART invoke required)
2. SMART-owned ledger `references/HARNESS-COMPAT.md` (SOLVED recipes + OPEN capture)
3. Protocol: search → apply → register → promote (including by a later harness-fluent model)

## Install / update (canonical four-step path)

Documented in README **Install on Claude Code** and **Updating**. Run **all** steps:

```bash
claude plugin marketplace update saeed-skills
claude plugin update smart@saeed-skills
bash skills/smart/skills/smart/scripts/ensure-user-claude-md.sh
# restart the Claude Code session
/smart:smart
```

```bash
# verify always-on pointer:
bash skills/smart/skills/smart/scripts/ensure-user-claude-md.sh --check
```

## Artifacts

| Path | Role |
|---|---|
| `skills/smart/skills/smart/references/HARNESS-COMPAT.md` | Friction ledger |
| `skills/smart/skills/smart/scripts/ensure-user-claude-md.sh` | Idempotent user pointer |
| SMART invariant 14 + Harness section | Operating protocol |

## Out of scope

API credit, rate limits alone, auth keys, ordinary product bugs — not ledger material.

## Verification

- Offline scenarios: 38 valid
- Unit/contract suite: see CI / local `python3 -m unittest discover -s tests -v`
