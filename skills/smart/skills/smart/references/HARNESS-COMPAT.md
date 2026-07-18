# HARNESS-COMPAT — Model ↔ Claude Code friction ledger

> **Purpose:** Durable, cross-session playbook for **runtime mismatches** between
> non-native (or mixed-proxy) models and the Claude Code harness. Lookup first;
> thrash last. Owned by SMART; pointed from always-on `~/.claude/CLAUDE.md`.
>
> **Not for:** API credit exhaustion, rate limits alone, auth key mistakes, ordinary
> product bugs, or “model gave a wrong answer” without a harness-specific root.

## Scope filter (in / out)

| IN (register here) | OUT (do not register) |
|---|---|
| Illegal content blocks (`redacted_thinking`, vendor reasoning) | Empty API balance / quota |
| Wrong tool-call shape / fake XML tools in text | Network blips without harness signature |
| Slash-namespace mistakes (`/smart` vs `/smart:smart`) | Project compile/test failures |
| Terminal/Bash assumptions that break Claude Code tool protocol | User product requirements errors |
| Plugin path / `${CLAUDE_PLUGIN_ROOT}` misuse unique to CC | Pure model quality complaints |
| Message-history replay that poisons the tool loop | Secrets / credentials (never store) |

## How models must use this ledger

1. **On harness friction** (content-type error, tool loop stall, slash dead-end, “this is not how I was trained to call tools”):
   - Search this file by symptom keywords.
   - If a **SOLVED** entry matches → apply `working_recipe` immediately; do not re-explore.
   - If **OPEN** matches → try listed partial notes; do not invent parallel lore.
   - If none → create an **OPEN** entry (schema below), then continue recovery.
2. **When solved** (any model, including a later Anthropic session): fill `working_recipe`,
   set `status: SOLVED`, add `evidence`, keep the wrong assumption visible for others.
3. **Never** store secrets, tokens, personal data, or full chat dumps.
4. **Prefer** promoting durable wire rules into `claude-code-compat` skill when they are
   universal; keep this ledger for **case recipes** and evolving friction.

## Entry schema

```yaml
id: HC-NNN                    # sequential
status: OPEN | SOLVED | SUPERSEDED
surface: content-blocks | tools | slash | bash | plugins | paths | other
symptom: >-
  Exact error text or observable failure (short).
wrong_assumption: >-
  What the model believed (training prior) that Claude Code rejects.
context:
  model_family: grok | gpt | gemini | mimo | claude | mixed-proxy | unknown
  host: claude-code
  notes: optional gateway / version hint (no secrets)
working_recipe: >-
  Concrete steps that restore a clean tool loop. Empty while OPEN.
evidence: path or short note proving the recipe (commit, field session, doc)
added: YYYY-MM-DD
updated: YYYY-MM-DD
```

## Seed entries (field-proven)

### HC-001 — `redacted_thinking` hard reject

```yaml
id: HC-001
status: SOLVED
surface: content-blocks
symptom: >
  Unsupported content type: redacted_thinking (or similar thinking block
  validation failure) after tool turns or model switch.
wrong_assumption: >
  Provider reasoning / encrypted CoT can be serialized as Claude Code
  assistant content blocks and replayed in multi-turn tool history.
context:
  model_family: mixed-proxy
  host: claude-code
  notes: Bifrost / OpenRouter / non-Anthropic models via Anthropic-compatible proxy
working_recipe: >
  1) Emit only text + tool_use on the assistant path that feeds tools.
  2) Never emit redacted_thinking, vendor reasoning, or opaque thought blobs.
  3) Do not replay failed thinking blocks into history; continue with a clean turn.
  4) Load skill `claude-code-compat` (user skill ~/.claude/skills/claude-code-compat)
     for the full wire policy. Slogan: Think private, speak text, act with tools.
evidence: field CTBot + user skill claude-code-compat SKILL.md
added: 2026-07-18
updated: 2026-07-18
```

### HC-002 — Bare `/smart` does not resolve

```yaml
id: HC-002
status: SOLVED
surface: slash
symptom: >
  Invoking /smart does nothing or is not suggested; only /smart:smart works.
wrong_assumption: >
  Plugin skills/commands can be invoked with a bare /name like first-party host
  commands. Claude Code always namespaces plugin surfaces as /plugin:name.
context:
  model_family: any
  host: claude-code
  notes: saeed-skills marketplace SMART plugin
working_recipe: >
  Always invoke SMART as /smart:smart. Document and teach only the namespaced form.
  Bare /smart is not a supported entry path for marketplace plugins.
evidence: code.claude.com plugins docs + Skills v2.5.16 ship
added: 2026-07-17
updated: 2026-07-18
```

### HC-003 — Tool calls pasted as assistant prose

```yaml
id: HC-003
status: SOLVED
surface: tools
symptom: >
  Model writes XML/JSON “tool call” blobs into visible text; harness never executes
  them; task stalls or user sees raw markup.
wrong_assumption: >
  Training patterns that show tools as XML in the completion are valid for Claude
  Code; the harness will parse prose as tools.
context:
  model_family: non-claude
  host: claude-code
working_recipe: >
  Use the harness tool interface only (function/tool_use blocks). Never treat
  pasted fake tool XML/JSON in text as the action. After tool_result, continue with
  text and/or the next tool_use only.
evidence: Claude Code agent loop contract; claude-code-compat
added: 2026-07-18
updated: 2026-07-18
```

### HC-004 — `${CLAUDE_PLUGIN_ROOT}` missing mid-session

```yaml
id: HC-004
status: SOLVED
surface: paths
symptom: >
  Scripts under the SMART plugin fail because CLAUDE_PLUGIN_ROOT is empty/unset
  when the model invents a path or runs outside plugin context.
wrong_assumption: >
  Plugin-relative paths always resolve from cwd or from a guessed cache path.
context:
  model_family: any
  host: claude-code
working_recipe: >
  Prefer ${CLAUDE_PLUGIN_ROOT}/skills/smart/scripts/... when set. If unset, locate
  SMART's installed plugin directory (marketplace cache or repo checkout) and use
  that scripts/ folder. Never invent a path from training memory; verify with ls.
evidence: SMART SKILL.md SENSE/SELECT path rules
added: 2026-07-18
updated: 2026-07-18
```

## Template for new OPEN entries

Copy under **Open / unsolved**, fill fields, leave `working_recipe` empty until proven:

```yaml
id: HC-NNN
status: OPEN
surface: content-blocks | tools | slash | bash | plugins | paths | other
symptom: >
  ...
wrong_assumption: >
  ...
context:
  model_family: unknown
  host: claude-code
  notes: ""
working_recipe: ""
evidence: ""
added: YYYY-MM-DD
updated: YYYY-MM-DD
```

## Open / unsolved

_None seeded. Append newest OPEN entries here; move to Seed when SOLVED._

## Maintainer rules

- Keep entries **short**; link out to skills/docs for long policy.
- One symptom family per id; supersede rather than silently edit meaning.
- Strip secrets on sight.
- Index growth: if this file exceeds ~200 lines of active recipes, split solved archive
  to `HARNESS-COMPAT-ARCHIVE.md` and keep OPEN + top SOLVED here.
