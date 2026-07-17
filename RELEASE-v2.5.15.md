# Release v2.5.15 — resume-check field fix

**Date:** 2026-07-17  
**Pin:** SMART `2.5.15` / marketplace metadata `2.5.15`

## Why

Field-validating host supervision on the real shipped STATE for **2.5.14** showed
`smart-gates.py memory resume-check` **GATE BLOCKED** even though the Resume
packet table was complete. The extractor treated the later
`## Next-session command packet` bash fence as the resume body and reported all
five recovery fields missing.

That is a host-supervision failure: memory-before-amnesia depends on a truthful
resume-check. Compact/handoff must not be blocked by a false RED, and a false
GREEN must never come from a command script fence.

## What changed

- `extract_resume_packet` bounds to the Resume section (next markdown heading).
- Table-form packets accepted; fenced body only when the fence opens near the
  section start.
- Regression test for table packet + later command fence.
- Full suite: **219** tests OK; scenarios still **33** valid.

## Consumer update

```bash
claude plugin marketplace update saeed-skills
claude plugin update smart@saeed-skills
# confirm pin 2.5.15
```

## Verify

```bash
python3 -m unittest discover -s tests -v
python3 skills/smart/skills/smart/evals/validate_behavioral_scenarios.py
python3 skills/smart/skills/smart/scripts/smart-gates.py memory resume-check
```
