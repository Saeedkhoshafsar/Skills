---
description: Activate SMART, the project intelligence orchestrator — builds a verified product model, enforces Vision Lock, maintains durable memory, and installs only the capabilities the next action needs.
argument-hint: [your idea, request, or nothing to resume]
---

# /smart:smart

Canonical entry: **`/smart:smart`** (plugin `smart` + command/skill `smart`).
Claude Code namespaces plugin commands; bare `/smart` is not a host command and
must not be documented or recommended as working.

Activate the `smart` skill from this plugin and follow its contract exactly.

User input (may be empty — an empty input on an existing project means "resume
from durable memory"; on a fresh project it means "start discovery"):

$ARGUMENTS

Rules for this invocation:

1. Read and obey `skills/smart/SKILL.md` in this plugin as the governing
   contract. Do not summarize it back to the user; act on it.
2. Begin with SENSE: newest resume file first (`docs/STATE2.md` if present,
   else `docs/STATE.md`, else root `STATE.md`), then only what the resume
   packet points to. Choose one operating mode. Prefer the fast path when
   STATE, Vision Lock, plan, and evidence are coherent. On pre-existing
   projects, resume — do not rebuild empty discovery/mind ceremony.
3. **Harness pointer (machine, once):** if home is writable and
   `~/.claude/CLAUDE.md` lacks the current HARNESS-COMPAT managed block, run
   `scripts/ensure-user-claude-md.sh` (idempotent; block-version **2+**). On a
   **soft mid-task** model↔Claude Code signal (first clear failure, or second
   same-class after one clean retry — not API credit alone), open
   `references/HARNESS-COMPAT.md` before thrash recovery; register OPEN when new;
   promote SOLVED same session when fixed.
4. Never ask the user to choose a skill, source, marketplace, package type, or
   command. Bundled companions are installed by SMART itself.
5. No plan and no code before a machine-confirmed Vision Lock.
6. Supervise Claude Code host commands when useful (`/context`, `/compact` after
   resume-check, `/model` on limits, never `/loop` without Vision Lock). Do not ask
   the user to manage the slash menu.
7. End with the progress-first SMART report in the user's language.

### Consumer update path (document for operators)

After each marketplace release, the full path is:

```bash
claude plugin marketplace update saeed-skills
claude plugin update smart@saeed-skills
# prefer installed cache (any cwd); version folder = highest installed SMART:
bash ~/.claude/plugins/cache/saeed-skills/smart/2.5.19/skills/smart/scripts/ensure-user-claude-md.sh
# or from this repo root: bash skills/smart/skills/smart/scripts/ensure-user-claude-md.sh
# restart session
/smart:smart
```
