#!/usr/bin/env bash
# SMART trusted capability installer: lockfile + quarantine + explicit activation.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
STATE_HELPER="$SCRIPT_DIR/installer-state.py"
SCANNER="$SCRIPT_DIR/skill-security-scan.sh"
TARGET_DIR_DEFAULT=".claude/skills"
GIT_BASE_URL="${SMART_GIT_BASE_URL:-https://github.com}"
GITHUB_API_BASE_URL="${SMART_GITHUB_API_BASE_URL:-https://api.github.com}"

# repo|requested-ref|skills-root; first matching source wins.
SOURCES=(
  "Saeedkhoshafsar/Skills|main|skills"
  "anthropics/skills|main|skills"
  "obra/superpowers|main|skills"
  "Saeedkhoshafsar/ruflo|main|.claude/skills"
  "Saeedkhoshafsar/claude-plugins-official|main|plugins/claude-code-setup/skills"
  "nextlevelbuilder/ui-ux-pro-max-skill|main|.claude/skills"
  "coreyhaines31/marketingskills|main|skills"
)

# skill|repo|requested-ref|full path
ALIASES=(
  "smart|Saeedkhoshafsar/Skills|main|skills/smart/skills/smart"
  "project-planner|Saeedkhoshafsar/Skills|main|skills/project-planner/skills/project-planner"
  "project-memory|Saeedkhoshafsar/Skills|main|skills/project-memory/skills/project-memory"
  "step-pilot|Saeedkhoshafsar/Skills|main|skills/step-pilot/skills/step-pilot"
  "code-review|Saeedkhoshafsar/Skills|main|skills/code-review/skills/code-review"
  "debug-detective|Saeedkhoshafsar/Skills|main|skills/debug-detective/skills/debug-detective"
  "security-check|Saeedkhoshafsar/Skills|main|skills/security-check/skills/security-check"
  "playground|Saeedkhoshafsar/claude-plugins-official|main|plugins/playground/skills/playground"
  "session-report|Saeedkhoshafsar/claude-plugins-official|main|plugins/session-report/skills/session-report"
  "project-artifact|Saeedkhoshafsar/claude-plugins-official|main|plugins/project-artifact/skills/project-artifact"
  "claude-md-improver|Saeedkhoshafsar/claude-plugins-official|main|plugins/claude-md-management/skills/claude-md-improver"
  "writing-hookify-rules|Saeedkhoshafsar/claude-plugins-official|main|plugins/hookify/skills/writing-rules"
  "math-olympiad|Saeedkhoshafsar/claude-plugins-official|main|plugins/math-olympiad/skills/math-olympiad"
  "skill-development|Saeedkhoshafsar/claude-plugins-official|main|plugins/plugin-dev/skills/skill-development"
  "plugin-structure|Saeedkhoshafsar/claude-plugins-official|main|plugins/plugin-dev/skills/plugin-structure"
  "plugin-settings|Saeedkhoshafsar/claude-plugins-official|main|plugins/plugin-dev/skills/plugin-settings"
  "mcp-integration|Saeedkhoshafsar/claude-plugins-official|main|plugins/plugin-dev/skills/mcp-integration"
  "hook-development|Saeedkhoshafsar/claude-plugins-official|main|plugins/plugin-dev/skills/hook-development"
  "command-development|Saeedkhoshafsar/claude-plugins-official|main|plugins/plugin-dev/skills/command-development"
  "agent-development|Saeedkhoshafsar/claude-plugins-official|main|plugins/plugin-dev/skills/agent-development"
  "build-mcp-server|Saeedkhoshafsar/claude-plugins-official|main|plugins/mcp-server-dev/skills/build-mcp-server"
  "build-mcp-app|Saeedkhoshafsar/claude-plugins-official|main|plugins/mcp-server-dev/skills/build-mcp-app"
  "build-mcpb|Saeedkhoshafsar/claude-plugins-official|main|plugins/mcp-server-dev/skills/build-mcpb"
  "stop-slop|hardikpandya/stop-slop|main|."
  "remotion-video|wshuyi/remotion-video-skill|main|."
  "scroll-world|oso95/scroll-world|main|skills/scroll-world"
)

BLACKLIST_PREFIXES=("v3-" "flow-nexus-")
BLACKLIST_EXACT=("dual-mode" "worker-benchmarks" "using-superpowers")

FIRST_PARTY_MARKETPLACE_SOURCE="Saeedkhoshafsar/Skills"
FIRST_PARTY_MARKETPLACE_NAME="saeed-skills"
FIRST_PARTY_CAPABILITIES=(
  "project-planner" "project-memory" "step-pilot"
  "code-review" "debug-detective" "security-check"
)

CEK_MARKETPLACE_SOURCE="NeoLabHQ/context-engineering-kit"
CEK_MARKETPLACE_NAME="context-engineering-kit"
CEK_MARKETPLACE_ID="NeoLabHQ/context-engineering-kit"
CEK_PLUGINS=("reflexion" "review" "git" "tdd" "sadd" "ddd" "sdd" "kaizen" "customaize-agent" "docs" "tech-stack" "mcp" "fpf")
CEK_CAPABILITIES=(
  "reflection|reflexion" "context-reflection|reflexion" "context-review|review"
  "context-git|git" "context-tdd|tdd" "subagent-development|sadd"
  "domain-driven-development|ddd" "spec-driven-development|sdd"
  "continuous-improvement|kaizen" "agent-customization|customaize-agent"
  "documentation-workflow|docs" "tech-stack-guidance|tech-stack"
  "mcp-integration-setup|mcp" "first-principles-reasoning|fpf"
)
PLUGIN_SCOPE="${SMART_PLUGIN_SCOPE:-user}"

usage() {
  cat <<'EOF'
Usage:
  fetch-skill.sh install <skill> [target]       # install locked commit, or quarantine discovered version
  fetch-skill.sh <skill> [target]               # compatibility alias for install
  fetch-skill.sh update <skill> [target]        # resolve latest requested ref into quarantine
  fetch-skill.sh candidate <skill> <owner/repo> <ref> <path> [target]
  fetch-skill.sh approve <skill> [target] --reviewed-by <identity>
  fetch-skill.sh verify <skill> [target]
  fetch-skill.sh status <skill> [target]
  fetch-skill.sh --list
  fetch-skill.sh --installed [target]

Standalone skills never become active immediately. Download and static scan place them
in quarantine. Review SKILL.md, scripts, scan report, provenance, and license; then run
'approve'. Lockfile installs use the exact recorded commit. Only 'update' changes it.
EOF
  exit 2
}

require_deps() {
  local missing=() tool
  for tool in git curl python3 file; do command -v "$tool" >/dev/null 2>&1 || missing+=("$tool"); done
  [ "${#missing[@]}" -eq 0 ] || { echo "ERROR: missing tools: ${missing[*]}" >&2; return 1; }
  [ -x "$STATE_HELPER" ] && [ -x "$SCANNER" ] || { echo "ERROR: installer helper scripts are unavailable." >&2; return 1; }
}

is_blacklisted() {
  local skill="$1" item
  for item in "${BLACKLIST_PREFIXES[@]}"; do [[ "$skill" == "$item"* ]] && return 0; done
  for item in "${BLACKLIST_EXACT[@]}"; do [ "$skill" = "$item" ] && return 0; done
  return 1
}

validate_request() { # skill target -> target<TAB>destination
  local skill="$1" target="$2"
  is_blacklisted "$skill" && { echo "BLOCKED: '$skill' is BLACK-tier." >&2; return 1; }
  python3 "$STATE_HELPER" validate "$skill" "$target"
}

paths_for() { # skill target; sets validated path globals
  local validated
  validated="$(validate_request "$1" "$2")" || return 1
  TARGET_REAL="${validated%%$'\t'*}"
  DEST_REAL="${validated#*$'\t'}"
  PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)"
  PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd -P)"
  LOCKFILE="$PROJECT_ROOT/.smart-lock.json"
  STATE_FILE="$TARGET_REAL/.smart-install-state.json"
  QUARANTINE_ROOT="$TARGET_REAL/.smart-quarantine"
}

resolve_commit() { # repo ref
  local repo="$1" ref="$2" output commit
  output="$(git ls-remote --exit-code "$GIT_BASE_URL/$repo.git" \
    "refs/heads/$ref" "refs/tags/$ref^{}" "refs/tags/$ref" 2>/dev/null)" || {
      echo "ERROR: requested ref '$ref' does not exist in $repo; no default-branch fallback is allowed." >&2
      return 1
    }
  commit="$(printf '%s\n' "$output" | awk '$2 ~ /\^\{\}$/ {print $1; exit} $2 ~ /^refs\/heads\// {print $1; exit} {candidate=$1} END {if (!found && candidate) print candidate}' | head -n1)"
  [[ "$commit" =~ ^[0-9a-f]{40}$ ]] || { echo "ERROR: could not resolve a full commit SHA for $repo@$ref." >&2; return 1; }
  printf '%s\n' "$commit"
}

api_ls() {
  curl -fsSL "$GITHUB_API_BASE_URL/repos/$1/contents/$3?ref=$2" 2>/dev/null \
    | grep -o '"name": *"[^"]*"' | sed 's/"name": *"\(.*\)"/\1/' || true
}

copy_commit_path() { # repo path commit quarantine
  local repo="$1" source_path="$2" commit="$3" quarantine="$4"
  local work_parent="$TARGET_REAL/.smart-tmp" work
  mkdir -p "$work_parent" "$QUARANTINE_ROOT"
  work="$(mktemp -d "$work_parent/fetch.XXXXXX")"
  trap 'rm -rf -- "${work:-}"' RETURN
  git init -q "$work/repo"
  git -C "$work/repo" remote add origin "$GIT_BASE_URL/$repo.git"
  if ! git -C "$work/repo" fetch -q --depth 1 origin "$commit"; then
    echo "ERROR: locked commit $commit is unavailable from $repo." >&2
    return 1
  fi
  [ "$(git -C "$work/repo" rev-parse FETCH_HEAD)" = "$commit" ] || {
    echo "ERROR: fetched commit does not match requested commit." >&2; return 1;
  }
  git -C "$work/repo" checkout -q --detach FETCH_HEAD
  if [ "$source_path" = "." ]; then
    mkdir -p "$work/payload"
    cp -a "$work/repo"/. "$work/payload"/
    rm -rf -- "$work/payload/.git"
  else
    [ -d "$work/repo/$source_path" ] || { echo "ERROR: path '$source_path' missing at $commit." >&2; return 1; }
    cp -a "$work/repo/$source_path" "$work/payload"
  fi
  [ -f "$work/payload/SKILL.md" ] || { echo "ERROR: candidate has no SKILL.md at its root." >&2; return 1; }
  rm -rf -- "$quarantine"
  mv "$work/payload" "$quarantine"
  rm -rf -- "$work"
  trap - RETURN
}

emit_approval_handoff() { # skill status repo ref path commit quarantine
  python3 - "$@" <<'PY'
import json
import sys

skill, status, repo, ref, source_path, commit, quarantine = sys.argv[1:]
print(json.dumps({
    "smart_event": "third_party_approval_required",
    "capability": skill,
    "status": status,
    "provenance": {
        "repository": repo,
        "requested_ref": ref,
        "resolved_commit": commit,
        "source_path": source_path,
    },
    "evidence": {
        "candidate_path": quarantine,
        "scan_report": f"{quarantine}/.smart-scan-report.txt",
    },
    "risk_notice": "Static scanning does not prove safety.",
    "next_action": (
        "SMART must review and summarize the evidence, then ask the user one "
        "plain-language approve-or-reject question without exposing commands or source choices."
    ),
}, sort_keys=True))
PY
}

quarantine_source() { # skill repo ref path commit
  local skill="$1" repo="$2" ref="$3" source_path="$4" commit="$5"
  python3 "$STATE_HELPER" validate-source "$skill" "$repo" "$ref" "$source_path" >/dev/null
  local quarantine="$QUARANTINE_ROOT/$skill-$commit" tree_hash scan_report_hash scan_status
  echo "Downloading '$skill' from $repo@$commit into quarantine ..."
  copy_commit_path "$repo" "$source_path" "$commit" "$quarantine" || return 1
  tree_hash=""
  scan_report_hash=""
  python3 "$STATE_HELPER" state-put "$STATE_FILE" "$skill" QUARANTINED \
    "$repo" "$ref" "$source_path" "$commit" "$tree_hash" "$scan_report_hash" "$quarantine"
  if "$SCANNER" "$quarantine" "$quarantine/.smart-scan-report.txt"; then
    scan_status="$(sed -n 's/^result=//p' "$quarantine/.smart-scan-report.txt" | tail -n1)"
    [ "$scan_status" = "STATIC_SCAN_PASSED" ] || scan_status="REVIEW_REQUIRED"
    tree_hash="$(python3 "$STATE_HELPER" manifest "$quarantine")"
    scan_report_hash="$(python3 "$STATE_HELPER" file-sha256 "$quarantine/.smart-scan-report.txt")"
  else
    scan_status="BLOCKED"
    scan_report_hash="$(python3 "$STATE_HELPER" file-sha256 "$quarantine/.smart-scan-report.txt")"
  fi
  python3 "$STATE_HELPER" state-put "$STATE_FILE" "$skill" "$scan_status" \
    "$repo" "$ref" "$source_path" "$commit" "$tree_hash" "$scan_report_hash" "$quarantine"
  if [ "$scan_status" = "BLOCKED" ]; then
    echo "BLOCKED: static scan found a hard failure. See $quarantine/.smart-scan-report.txt" >&2
    return 1
  fi
  echo "QUARANTINED: $quarantine"
  echo "Status: $scan_status. Handing evidence back to SMART for review and a plain-language user decision."
  emit_approval_handoff "$skill" "$scan_status" "$repo" "$ref" \
    "$source_path" "$commit" "$quarantine"
}

lock_entry() { python3 "$STATE_HELPER" lock-get "$LOCKFILE" "$1"; }
state_entry() { python3 "$STATE_HELPER" state-get "$STATE_FILE" "$1"; }

install_skill() {
  local skill="$1" target="${2:-$TARGET_DIR_DEFAULT}" locked repo ref source_path commit locked_tree status
  paths_for "$skill" "$target" || return 1
  require_deps || return 1
  if [ -d "$DEST_REAL" ]; then
    verify_skill "$skill" "$target" && { echo "OK: '$skill' is already active and matches its lock."; return 0; }
    echo "ERROR: active destination exists but fails lock verification; refusing overwrite." >&2
    return 1
  fi
  if locked="$(lock_entry "$skill")"; then
    IFS=$'\t' read -r repo ref source_path commit locked_tree _ status <<< "$locked"
    [ "$status" = "VERIFIED" ] && [ -n "$locked_tree" ] || { echo "ERROR: lock entry is incomplete or not VERIFIED." >&2; return 1; }
    quarantine_source "$skill" "$repo" "$ref" "$source_path" "$commit"
    return $?
  fi
  discover_skill "$skill"
}

discover_skill() {
  local skill="$1" alias name repo ref source_path source listing commit api_failed=0
  for alias in "${ALIASES[@]}"; do
    IFS='|' read -r name repo ref source_path <<< "$alias"
    if [ "$name" = "$skill" ]; then
      commit="$(resolve_commit "$repo" "$ref")" || return 1
      quarantine_source "$skill" "$repo" "$ref" "$source_path" "$commit"
      return $?
    fi
  done
  for source in "${SOURCES[@]}"; do
    IFS='|' read -r repo ref source_path <<< "$source"
    listing="$(api_ls "$repo" "$ref" "$source_path")"
    [ -n "$listing" ] || api_failed=1
    if printf '%s\n' "$listing" | grep -qxF "$skill"; then
      commit="$(resolve_commit "$repo" "$ref")" || return 1
      quarantine_source "$skill" "$repo" "$ref" "$source_path/$skill" "$commit"
      return $?
    fi
  done
  [ "$api_failed" -eq 0 ] || echo "ERROR: source discovery API unavailable; use 'candidate' with an explicit reviewed source." >&2
  echo "ERROR: skill '$skill' not found in curated sources." >&2
  return 1
}

update_skill() {
  local skill="$1" target="${2:-$TARGET_DIR_DEFAULT}" locked repo ref source_path old_commit _ new_commit
  paths_for "$skill" "$target" || return 1
  require_deps || return 1
  locked="$(lock_entry "$skill")" || { echo "ERROR: no lock entry; use install or candidate first." >&2; return 1; }
  IFS=$'\t' read -r repo ref source_path old_commit _ _ _ <<< "$locked"
  new_commit="$(resolve_commit "$repo" "$ref")" || return 1
  if [ "$new_commit" = "$old_commit" ]; then echo "OK: '$skill' is already locked to the latest $ref commit."; return 0; fi
  quarantine_source "$skill" "$repo" "$ref" "$source_path" "$new_commit"
}

candidate_skill() {
  [ "$#" -ge 4 ] && [ "$#" -le 5 ] || usage
  local skill="$1" repo="$2" ref="$3" source_path="$4" target="${5:-$TARGET_DIR_DEFAULT}" commit
  paths_for "$skill" "$target" || return 1
  require_deps || return 1
  python3 "$STATE_HELPER" validate-source "$skill" "$repo" "$ref" "$source_path" >/dev/null
  commit="$(resolve_commit "$repo" "$ref")" || return 1
  quarantine_source "$skill" "$repo" "$ref" "$source_path" "$commit"
}

approve_skill() {
  local skill="$1" target="$2" reviewer="$3" entry status repo ref source_path commit expected_hash expected_report_hash quarantine actual_hash actual_report_hash backup
  [[ "$reviewer" =~ ^[A-Za-z0-9][A-Za-z0-9@._-]{1,127}$ ]] || {
    echo "ERROR: --reviewed-by requires a 2-128 character accountable identity." >&2
    return 1
  }
  paths_for "$skill" "$target" || return 1
  require_deps || return 1
  [ ! -L "$TARGET_REAL/.installed.log" ] || { echo "ERROR: install log may not be a symlink." >&2; return 1; }
  [ ! -L "$PROJECT_ROOT/.gitignore" ] || { echo "ERROR: project .gitignore may not be a symlink." >&2; return 1; }
  entry="$(state_entry "$skill")" || { echo "ERROR: no quarantined candidate for '$skill'." >&2; return 1; }
  IFS=$'\t' read -r status repo ref source_path commit expected_hash expected_report_hash quarantine <<< "$entry"
  case "$status" in STATIC_SCAN_PASSED|REVIEW_REQUIRED) ;; *) echo "ERROR: candidate status '$status' cannot be approved." >&2; return 1 ;; esac
  [ -d "$quarantine" ] && [[ "$quarantine" == "$QUARANTINE_ROOT/"* ]] || { echo "ERROR: invalid quarantine path." >&2; return 1; }
  actual_hash="$(python3 "$STATE_HELPER" manifest "$quarantine")"
  [ "$actual_hash" = "$expected_hash" ] || { echo "ERROR: candidate changed after scanning; re-download and review it." >&2; return 1; }
  actual_report_hash="$(python3 "$STATE_HELPER" file-sha256 "$quarantine/.smart-scan-report.txt")"
  [ "$actual_report_hash" = "$expected_report_hash" ] || { echo "ERROR: scan report changed after scanning; re-download and review it." >&2; return 1; }
  backup="$TARGET_REAL/.smart-backup-$skill-$$"
  [ ! -e "$backup" ] || { echo "ERROR: backup path collision." >&2; return 1; }
  if [ -e "$DEST_REAL" ]; then mv "$DEST_REAL" "$backup"; fi
  if ! mv "$quarantine" "$DEST_REAL"; then [ ! -e "$backup" ] || mv "$backup" "$DEST_REAL"; return 1; fi
  if ! python3 "$STATE_HELPER" lock-put "$LOCKFILE" "$skill" "$repo" "$ref" "$source_path" "$commit" "$actual_hash" "$actual_report_hash" "$reviewer"; then
    mv "$DEST_REAL" "$quarantine"
    [ ! -e "$backup" ] || mv "$backup" "$DEST_REAL"
    return 1
  fi
  python3 "$STATE_HELPER" state-put "$STATE_FILE" "$skill" ACTIVE "$repo" "$ref" "$source_path" "$commit" "$actual_hash" "$actual_report_hash" ""
  rm -rf -- "$backup"
  printf '%s %s <- %s|%s@%s reviewer=%s\n' "$(date -u +%F)" "$skill" "$repo" "$source_path" "$commit" "$reviewer" >> "$TARGET_REAL/.installed.log"
  ensure_gitignore "$TARGET_REAL"
  echo "ACTIVE: '$skill' at $DEST_REAL"
  echo "Lock updated: $LOCKFILE"
}

verify_skill() {
  local skill="$1" target="${2:-$TARGET_DIR_DEFAULT}" locked repo ref source_path commit expected_hash expected_report_hash status actual_hash actual_report_hash
  paths_for "$skill" "$target" || return 1
  locked="$(lock_entry "$skill")" || { echo "ERROR: no lock entry for '$skill'." >&2; return 1; }
  IFS=$'\t' read -r repo ref source_path commit expected_hash expected_report_hash status <<< "$locked"
  [ "$status" = "VERIFIED" ] && [ -d "$DEST_REAL" ] || { echo "ERROR: '$skill' is not active and VERIFIED." >&2; return 1; }
  actual_hash="$(python3 "$STATE_HELPER" manifest "$DEST_REAL")"
  [ "$actual_hash" = "$expected_hash" ] || { echo "ERROR: tree checksum mismatch for '$skill'." >&2; return 1; }
  actual_report_hash="$(python3 "$STATE_HELPER" file-sha256 "$DEST_REAL/.smart-scan-report.txt")"
  [ "$actual_report_hash" = "$expected_report_hash" ] || { echo "ERROR: scan report checksum mismatch for '$skill'." >&2; return 1; }
  echo "VERIFIED: $skill repo=$repo ref=$ref path=$source_path commit=$commit tree_sha256=$actual_hash scan_report_sha256=$actual_report_hash"
}

status_skill() {
  local skill="$1" target="${2:-$TARGET_DIR_DEFAULT}" entry
  paths_for "$skill" "$target" || return 1
  if entry="$(state_entry "$skill")"; then printf '%s\n' "$entry"; else echo "UNKNOWN: no lifecycle state for '$skill'"; return 1; fi
}

ensure_gitignore() {
  local target="$1" root
  [ "$target" = "$(cd "$PROJECT_ROOT/$TARGET_DIR_DEFAULT" 2>/dev/null && pwd -P || printf '%s' "$PROJECT_ROOT/$TARGET_DIR_DEFAULT")" ] || return 0
  root="$PROJECT_ROOT"
  if ! grep -qxF ".claude/skills/" "$root/.gitignore" 2>/dev/null; then
    printf '.claude/skills/\n' >> "$root/.gitignore"
  fi
}

is_first_party_capability() {
  local candidate="$1" capability
  for capability in "${FIRST_PARTY_CAPABILITIES[@]}"; do
    [ "$candidate" = "$capability" ] && return 0
  done
  return 1
}

first_party_cache_dir() { # capability -> prints newest cached plugin dir, if present
  local capability="$1" cache_root="${SMART_CLAUDE_PLUGIN_CACHE:-$HOME/.claude/plugins/cache}"
  local base version
  base="$cache_root/$FIRST_PARTY_MARKETPLACE_NAME/$capability"
  [ -d "$base" ] || return 1
  version="$(find "$base" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | sort -V | tail -n 1)"
  [ -n "$version" ] && [ -f "$base/$version/.claude-plugin/plugin.json" ] || return 1
  printf '%s\n' "$base/$version"
}

install_first_party_plugin() {
  local capability="$1" mode="${2:-}" qualified installed marketplaces cached
  qualified="$capability@$FIRST_PARTY_MARKETPLACE_NAME"
  case "$PLUGIN_SCOPE" in user|project|local) ;; *) echo "ERROR: invalid SMART_PLUGIN_SCOPE." >&2; return 1 ;; esac
  # A companion already present in the Claude plugin cache (e.g. installed
  # manually through the plugin UI) is installed — recognize it even when the
  # `claude` CLI is not on this shell's PATH (common in Codespaces/containers).
  if [ "$mode" != update ] && cached="$(first_party_cache_dir "$capability")"; then
    echo "OK: bundled capability '$capability' already installed (plugin cache: $cached)."
    return 0
  fi
  command -v claude >/dev/null 2>&1 || {
    if [ "$mode" = update ] && cached="$(first_party_cache_dir "$capability")"; then
      echo "OK: '$capability' present in plugin cache ($cached); update requires the Claude Code CLI — run 'claude plugin update $qualified' from a shell where 'claude' is available." >&2
      return 0
    fi
    echo "ERROR: bundled capability '$capability' requires Claude Code CLI, and no cached plugin was found under \${SMART_CLAUDE_PLUGIN_CACHE:-\$HOME/.claude/plugins/cache}." >&2
    return 1
  }
  marketplaces="$(claude plugin marketplace list --json 2>/dev/null || printf '[]')"
  if ! printf '%s' "$marketplaces" | grep -Fq "$FIRST_PARTY_MARKETPLACE_NAME"; then
    claude plugin marketplace add --scope "$PLUGIN_SCOPE" "$FIRST_PARTY_MARKETPLACE_SOURCE"
  fi
  installed="$(claude plugin list --json 2>/dev/null || printf '[]')"
  if printf '%s' "$installed" | grep -Fq "$qualified"; then
    [ "$mode" = update ] && claude plugin update "$qualified" || echo "OK: bundled capability already installed."
  else
    claude plugin install --scope "$PLUGIN_SCOPE" "$qualified"
  fi
}

is_cek_plugin() { local candidate="$1" plugin; for plugin in "${CEK_PLUGINS[@]}"; do [ "$candidate" = "$plugin" ] && return 0; done; return 1; }
resolve_cek_plugin() {
  local requested="$1" mapping capability plugin
  if [[ "$requested" == cek:* ]]; then plugin="${requested#cek:}"; is_cek_plugin "$plugin" && printf '%s\n' "$plugin" && return 0; return 1; fi
  for mapping in "${CEK_CAPABILITIES[@]}"; do IFS='|' read -r capability plugin <<< "$mapping"; [ "$requested" = "$capability" ] && printf '%s\n' "$plugin" && return 0; done
  return 1
}
install_cek_plugin() {
  local plugin="$1" mode="${2:-}" qualified installed marketplaces
  qualified="$plugin@$CEK_MARKETPLACE_ID"
  case "$PLUGIN_SCOPE" in user|project|local) ;; *) echo "ERROR: invalid SMART_PLUGIN_SCOPE." >&2; return 1 ;; esac
  command -v claude >/dev/null 2>&1 || { echo "ERROR: native plugin requires Claude Code CLI." >&2; return 1; }
  marketplaces="$(claude plugin marketplace list --json 2>/dev/null || printf '[]')"
  if ! printf '%s' "$marketplaces" | grep -Fq "$CEK_MARKETPLACE_NAME"; then claude plugin marketplace add --scope "$PLUGIN_SCOPE" "$CEK_MARKETPLACE_SOURCE"; fi
  installed="$(claude plugin list --json 2>/dev/null || printf '[]')"
  if printf '%s' "$installed" | grep -Fq "$qualified"; then [ "$mode" = update ] && claude plugin update "$qualified" || echo "OK: native plugin already installed."; else claude plugin install --scope "$PLUGIN_SCOPE" "$qualified"; fi
}

list_available() {
  local source repo ref source_path mapping capability plugin
  require_deps
  echo "BUNDLED SMART CAPABILITIES:"
  for capability in "${FIRST_PARTY_CAPABILITIES[@]}"; do echo "  - $capability -> $capability@$FIRST_PARTY_MARKETPLACE_NAME"; done
  for source in "${SOURCES[@]}"; do IFS='|' read -r repo ref source_path <<< "$source"; echo "SOURCE $repo@$ref/$source_path:"; api_ls "$repo" "$ref" "$source_path" | sed 's/^/  - /'; done
  echo "NATIVE PLUGINS:"
  for mapping in "${CEK_CAPABILITIES[@]}"; do IFS='|' read -r capability plugin <<< "$mapping"; echo "  - $capability -> cek:$plugin"; done
}

list_installed() {
  local target="${1:-$TARGET_DIR_DEFAULT}" capability cached
  [ -d "$target" ] && find "$target" -mindepth 1 -maxdepth 1 -type d ! -name '.smart-*' -printf '%f\n' | sort || true
  [ -f "$target/.smart-install-state.json" ] && cat "$target/.smart-install-state.json" || true
  for capability in "${FIRST_PARTY_CAPABILITIES[@]}"; do
    if cached="$(first_party_cache_dir "$capability")"; then
      echo "bundled:$capability INSTALLED (plugin cache: $cached)"
    fi
  done
  command -v claude >/dev/null 2>&1 && claude plugin list --json 2>/dev/null || true
}

# Backward-compatible old flags are accepted, but lifecycle verbs are preferred.
command="${1:-}"
case "$command" in
  ""|-h|--help) usage ;;
  --list) list_available ;;
  --installed) list_installed "${2:-$TARGET_DIR_DEFAULT}" ;;
  --update)
    [ -n "${2:-}" ] || usage
    if is_first_party_capability "$2"; then install_first_party_plugin "$2" update
    elif plugin="$(resolve_cek_plugin "$2")"; then install_cek_plugin "$plugin" update
    else update_skill "$2" "${3:-$TARGET_DIR_DEFAULT}"
    fi
    ;;
  install)
    [ -n "${2:-}" ] || usage
    if is_first_party_capability "$2"; then install_first_party_plugin "$2"
    elif plugin="$(resolve_cek_plugin "$2")"; then install_cek_plugin "$plugin"
    else install_skill "$2" "${3:-$TARGET_DIR_DEFAULT}"
    fi
    ;;
  update)
    [ -n "${2:-}" ] || usage
    if is_first_party_capability "$2"; then install_first_party_plugin "$2" update
    elif plugin="$(resolve_cek_plugin "$2")"; then install_cek_plugin "$plugin" update
    else update_skill "$2" "${3:-$TARGET_DIR_DEFAULT}"
    fi
    ;;
  candidate) shift; candidate_skill "$@" ;;
  approve)
    [ -n "${2:-}" ] || usage
    skill="$2"
    if [ "${3:-}" = "--reviewed-by" ]; then
      target="$TARGET_DIR_DEFAULT"; reviewer="${4:-}"; [ "$#" -eq 4 ] || usage
    else
      target="${3:-$TARGET_DIR_DEFAULT}"; [ "${4:-}" = "--reviewed-by" ] || usage
      reviewer="${5:-}"; [ "$#" -eq 5 ] || usage
    fi
    approve_skill "$skill" "$target" "$reviewer"
    ;;
  verify) [ -n "${2:-}" ] || usage; verify_skill "$2" "${3:-$TARGET_DIR_DEFAULT}" ;;
  status) [ -n "${2:-}" ] || usage; status_skill "$2" "${3:-$TARGET_DIR_DEFAULT}" ;;
  *)
    if is_first_party_capability "$command"; then install_first_party_plugin "$command"
    elif plugin="$(resolve_cek_plugin "$command")"; then install_cek_plugin "$plugin"
    else install_skill "$command" "${2:-$TARGET_DIR_DEFAULT}"
    fi
    ;;
esac
