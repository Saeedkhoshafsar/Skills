#!/usr/bin/env bash
# ensure-user-claude-md.sh — idempotent always-on harness pointer for Claude Code.
#
# Writes/updates ~/.claude/CLAUDE.md with a bounded HARNESS-COMPAT block so every
# project session (with or without /smart:smart) knows:
#   1) lookup model↔Claude Code friction in the SMART ledger
#   2) escalate harness mismatches to /smart:smart
#
# Safe defaults:
#   - creates ~/.claude if missing
#   - never deletes user content outside the managed markers
#   - replaces only the block between BEGIN/END markers when present
#   - appends the block if markers are absent
#   - does not touch project CLAUDE.md files
#
# Usage:
#   bash ensure-user-claude-md.sh           # ensure / update
#   bash ensure-user-claude-md.sh --check   # exit 0 if block present and current, else 1
#   bash ensure-user-claude-md.sh --print   # print managed block to stdout

set -euo pipefail

MARKER_BEGIN="<!-- BEGIN saeed-skills HARNESS-COMPAT -->"
MARKER_END="<!-- END saeed-skills HARNESS-COMPAT -->"
BLOCK_VERSION="1"

TARGET_DIR="${HOME}/.claude"
TARGET_FILE="${TARGET_DIR}/CLAUDE.md"

managed_block() {
  cat <<EOF
${MARKER_BEGIN}
<!-- managed-by: saeed-skills smart | block-version: ${BLOCK_VERSION} | do not edit inside markers -->

# Harness compatibility (all projects)

You are running inside **Claude Code**. Models that are not first-party Anthropic
(or that arrive via a proxy) often hit **runtime mismatches** with this harness.

## Always-on rules

1. **Wire dialect:** Assistant turns that feed tools may use only harness-legal
   content (\`text\` + \`tool_use\`). Never emit \`redacted_thinking\`, vendor
   reasoning blobs, or fake tool XML/JSON in prose. Prefer skill
   \`claude-code-compat\` when present (\`~/.claude/skills/claude-code-compat\`).
2. **Plugin slash names are namespaced:** e.g. SMART is **\`/smart:smart\`**, not bare \`/smart\`.
3. **On model↔Claude Code friction** (content-type errors, tool-loop stalls, slash
   dead-ends, path/plugin protocol surprises — **not** API credit/rate-limit alone):
   - Search the durable ledger:
     - Plugin path: \`\${CLAUDE_PLUGIN_ROOT}/skills/smart/references/HARNESS-COMPAT.md\`
     - Or the installed SMART skill's \`references/HARNESS-COMPAT.md\`
   - If a **SOLVED** entry matches → apply its \`working_recipe\` immediately.
   - If missing → register an **OPEN** entry (schema in that file), then recover.
   - Invoke **\`/smart:smart\`** so SMART owns lookup, recovery, and ledger updates.
4. **Do not thrash.** Do not burn the session on long trial-and-error when the
   ledger or SMART can short-circuit the same class of failure.

SMART remains the project control brain; this block only guarantees the pointer
loads even when SMART was not invoked yet.

${MARKER_END}
EOF
}

ensure_dir() {
  mkdir -p "${TARGET_DIR}"
}

has_current_block() {
  [[ -f "${TARGET_FILE}" ]] || return 1
  grep -qF "${MARKER_BEGIN}" "${TARGET_FILE}" || return 1
  grep -qF "${MARKER_END}" "${TARGET_FILE}" || return 1
  grep -qF "block-version: ${BLOCK_VERSION}" "${TARGET_FILE}" || return 1
}

replace_or_append_block() {
  local block
  block="$(managed_block)"
  BLOCK="${block}" BEGIN="${MARKER_BEGIN}" END="${MARKER_END}" TARGET="${TARGET_FILE}" \
    python3 - <<'PY'
import os
from pathlib import Path

path = Path(os.environ["TARGET"])
begin = os.environ["BEGIN"]
end = os.environ["END"]
block = os.environ["BLOCK"]
if not block.endswith("\n"):
    block += "\n"

if not path.exists():
    header = (
        "# CLAUDE.md — user-level always-on instructions\n\n"
        "Personal defaults for every Claude Code project on this machine.\n\n"
    )
    path.write_text(header + block, encoding="utf-8")
    print(f"CREATED: {path}")
    raise SystemExit(0)

text = path.read_text(encoding="utf-8")
b = text.find(begin)
e = text.find(end)
if b >= 0 and e >= 0 and e >= b:
    e_end = e + len(end)
    if e_end < len(text) and text[e_end] == "\n":
        e_end += 1
    path.write_text(text[:b] + block + text[e_end:], encoding="utf-8")
    print(f"UPDATED: {path}")
else:
    sep = "" if text.endswith("\n") else "\n"
    path.write_text(text + sep + "\n" + block, encoding="utf-8")
    print(f"APPENDED: {path}")
PY
}

cmd_print() {
  managed_block
}

cmd_check() {
  if has_current_block; then
    echo "OK: ${TARGET_FILE} has HARNESS-COMPAT block v${BLOCK_VERSION}"
    exit 0
  fi
  echo "MISSING_OR_STALE: ${TARGET_FILE} lacks current HARNESS-COMPAT block v${BLOCK_VERSION}" >&2
  exit 1
}

cmd_ensure() {
  ensure_dir
  replace_or_append_block
}

main() {
  local mode="${1:-ensure}"
  case "${mode}" in
    --print | print) cmd_print ;;
    --check | check) cmd_check ;;
    --ensure | ensure | "") cmd_ensure ;;
    -h | --help | help)
      sed -n '2,20p' "$0"
      ;;
    *)
      echo "usage: $0 [--ensure|--check|--print]" >&2
      exit 2
      ;;
  esac
}

main "${1:-ensure}"
