---
description: Activate SMART, the project intelligence orchestrator — builds a verified product model, enforces Vision Lock, maintains durable memory, and installs only the capabilities the next action needs.
argument-hint: [your idea, request, or nothing to resume]
---

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
3. Never ask the user to choose a skill, source, marketplace, package type, or
   command. Bundled companions are installed by SMART itself.
4. No plan and no code before a machine-confirmed Vision Lock.
5. End with the progress-first SMART report in the user's language.
