# Release v2.5.17 — Depth Reprocess + evidence-rooted trees

**Date:** 2026-07-18  
**Pin:** SMART `2.5.17` / marketplace metadata `2.5.17`  
**Companions:** step-pilot `1.3.0`, project-planner `1.5.0`

## Why

1. A coherent first pass is not a maxed result (multi-layer reprocess when stakes are real).
2. Fluent “logic trees” without proof roots are false confidence — training-frequency is
   not evidence. Creativity must stay free but must never be mislabeled as truth.

## What changed

- SMART **Depth Reprocess** (L0→L4, optional L5) with triggers, stop conditions, budget lever
- SMART **Evidence-rooted thought trees**: truth trunk vs creative trunk; label-at-birth;
  promotion requires a root; root check before commit
- Step Pilot: depth self-critique before DONE on generative depth work
- Project-planner Stage 1.5: budget lever + creative/paid-gen depth note
- 3 offline scenarios + contract tests
- Pin **2.5.17**

## Consumer update

```bash
claude plugin marketplace update saeed-skills
claude plugin update smart@saeed-skills
# also update companions if installed:
claude plugin update step-pilot@saeed-skills
claude plugin update project-planner@saeed-skills
# restart session; invoke:
/smart:smart
```

## Verify

```bash
python3 -m unittest discover -s tests -v
python3 skills/smart/skills/smart/evals/validate_behavioral_scenarios.py
```
