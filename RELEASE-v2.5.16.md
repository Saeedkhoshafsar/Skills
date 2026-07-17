# Release v2.5.16 — scroll-world catalog + `/smart:smart` honesty

**Date:** 2026-07-17  
**Pin:** SMART `2.5.16` / marketplace metadata `2.5.16`

## Why

1. **Capability gap:** SMART should select cinematic scroll-scrubbed world landings by
   capability name, not invent WebGL/Three or misuse Remotion. Upstream
   [oso95/scroll-world](https://github.com/oso95/scroll-world) already ships a complete
   Higgsfield + frame-lock + portable scrub-engine skill.
2. **Slash honesty:** Claude Code **always namespaces** plugin skills/commands as
   `/<plugin>:<name>`. Bare `/smart` never resolved; docs that claimed it did confused
   users. Canonical entry is **`/smart:smart`**.

## What changed

- `fetch-skill.sh` alias: `scroll-world` → `oso95/scroll-world@main` path `skills/scroll-world`
- Full YELLOW SMART profile in `SKILLS_CATALOG.md` (when/not-when, prereqs, cost, seam rule,
  architecture A/B, complements, safety)
- Duplicate resolution vs `remotion-video` / hand-rolled WebGL
- SMART lifecycle defaults + design lens triggers
- README / CLAUDE.md / catalog / `commands/smart.md` / SMART playbook: **`/smart:smart` only**
- Contract tests for alias + slash-entry honesty + pin
- SMART + marketplace pin **2.5.16**

## Consumer update

```bash
claude plugin marketplace update saeed-skills
claude plugin update smart@saeed-skills
# confirm pin 2.5.16, then restart the session
# invoke: /smart:smart   (NOT bare /smart)
```

After update, SMART can install via:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/smart/scripts/fetch-skill.sh" install scroll-world
# third-party → quarantine → review → approve (SMART asks one plain-language question)
```

## Operator notes for SMART

| Trigger phrases | Capability |
|---|---|
| scroll world, fly through, diorama landing, scroll cinematic, 3D world hero, continuous camera landing | `scroll-world` |
| Remotion / React video timeline / subtitles | `remotion-video` |
| full design system palette/type/pattern | `ui-ux-pro-max` |

**Hard constraints when selecting `scroll-world`:**

1. YELLOW — state the trigger and reason.
2. Prerequisites: Higgsfield CLI authenticated + credits; `ffmpeg`/`ffprobe`; optional Codex for stills.
3. Budget: state estimate (≈N stills + 2N−1 videos; mobile ≈2×) and get go-ahead before gens.
4. Third-party install remains quarantine → review → explicit approve; never silent activate.
5. Do not substitute Remotion or invent a WebGL world when this skill fits.

## Verify

```bash
bash -n skills/smart/skills/smart/scripts/fetch-skill.sh
python3 -m unittest discover -s tests -v
python3 skills/smart/skills/smart/evals/validate_behavioral_scenarios.py
```
