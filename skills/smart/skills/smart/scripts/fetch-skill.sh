#!/usr/bin/env bash
# ============================================================
# fetch-skill.sh — unified on-demand capability installer
# Downloads standalone skills with sparse-checkout or installs structured plugins
# through their native Claude Code marketplace.
# ============================================================
set -euo pipefail

# ---------- skill sources (repo|branch|path-inside-repo) ----------
# Order matters: the FIRST source that has the skill wins (dedup rule).
# If the pinned branch disappears, sparse_copy falls back to the repo's default branch.
SOURCES=(
  "Saeedkhoshafsar/Skills|genspark_ai_developer|skills"
  "anthropics/skills|main|skills"
  "obra/superpowers|main|skills"
  "Saeedkhoshafsar/ruflo|main|.claude/skills"
  "Saeedkhoshafsar/claude-plugins-official|main|plugins/claude-code-setup/skills"
  "nextlevelbuilder/ui-ux-pro-max-skill|main|.claude/skills"
  "coreyhaines31/marketingskills|main|skills"
)

# ---------- aliases: skills living at non-standard nested paths ----------
# format: skill-name|repo|branch|full-path-to-skill-folder
# 1) local skills in this repo use the standard plugin layout skills/<plugin>/skills/<skill>
# 2) claude-plugins-official keeps skills under plugins/<plugin>/skills/<skill>
ALIASES=(
  "smart|Saeedkhoshafsar/Skills|genspark_ai_developer|skills/smart/skills/smart"
  "project-planner|Saeedkhoshafsar/Skills|genspark_ai_developer|skills/project-planner/skills/project-planner"
  "project-memory|Saeedkhoshafsar/Skills|genspark_ai_developer|skills/project-memory/skills/project-memory"
  "step-pilot|Saeedkhoshafsar/Skills|genspark_ai_developer|skills/step-pilot/skills/step-pilot"
  "code-review|Saeedkhoshafsar/Skills|genspark_ai_developer|skills/code-review/skills/code-review"
  "debug-detective|Saeedkhoshafsar/Skills|genspark_ai_developer|skills/debug-detective/skills/debug-detective"
  "security-check|Saeedkhoshafsar/Skills|genspark_ai_developer|skills/security-check/skills/security-check"
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
)

# skills that must NEVER be installed (see SKILLS_CATALOG.md, BLACK tier)
BLACKLIST_PREFIXES=("v3-" "flow-nexus-")
BLACKLIST_EXACT=("dual-mode" "worker-benchmarks" "using-superpowers")

# ---------- structured plugin capabilities ----------
# CEK must stay a native plugin so its agents, commands, hooks, and skills survive.
# SMART selects a capability name; users never need to choose the source or plugin.
CEK_MARKETPLACE_SOURCE="NeoLabHQ/context-engineering-kit"
CEK_MARKETPLACE_NAME="context-engineering-kit"
CEK_MARKETPLACE_ID="NeoLabHQ/context-engineering-kit"
CEK_PLUGINS=("reflexion" "review" "git" "tdd" "sadd" "ddd" "sdd" "kaizen" "customaize-agent" "docs" "tech-stack" "mcp" "fpf")
CEK_CAPABILITIES=(
  "reflection|reflexion"
  "context-reflection|reflexion"
  "context-review|review"
  "context-git|git"
  "context-tdd|tdd"
  "subagent-development|sadd"
  "domain-driven-development|ddd"
  "spec-driven-development|sdd"
  "continuous-improvement|kaizen"
  "agent-customization|customaize-agent"
  "documentation-workflow|docs"
  "tech-stack-guidance|tech-stack"
  "mcp-integration-setup|mcp"
  "first-principles-reasoning|fpf"
)
PLUGIN_SCOPE="${SMART_PLUGIN_SCOPE:-user}"

TARGET_DIR_DEFAULT=".claude/skills"

usage() {
  cat <<'EOF'
fetch-skill.sh — unified on-demand capability installer
Installs a standalone skill or the native plugin that provides the capability.

Usage:
  ./fetch-skill.sh <capability-or-skill> [target-dir]
  ./fetch-skill.sh --list                 # list standalone and plugin capabilities
  ./fetch-skill.sh --installed [dir]      # list installed skills and plugins
  ./fetch-skill.sh --update <name>        # update from the original source

Examples:
  ./fetch-skill.sh sparc-methodology
  ./fetch-skill.sh ui-ux-pro-max
  ./fetch-skill.sh spec-driven-development  # selects and installs CEK's sdd plugin
  ./fetch-skill.sh cek:reflexion             # direct plugin capability, when needed
  ./fetch-skill.sh pdf .claude/skills

Plugin scope defaults to user. Set SMART_PLUGIN_SCOPE=project or local to override.
EOF
  exit 1
}

require_deps() {
  local missing=()
  command -v git  >/dev/null 2>&1 || missing+=("git")
  command -v curl >/dev/null 2>&1 || missing+=("curl")
  if [ "${#missing[@]}" -gt 0 ]; then
    echo "ERROR: missing required tools: ${missing[*]} — install them first." >&2
    exit 1
  fi
}

is_cek_plugin() {
  local candidate="$1" plugin
  for plugin in "${CEK_PLUGINS[@]}"; do
    [ "$candidate" = "$plugin" ] && return 0
  done
  return 1
}

resolve_cek_plugin() { # resolve_cek_plugin <capability> -> plugin name, or fail
  local requested="$1" mapping capability plugin
  if [[ "$requested" == cek:* ]]; then
    plugin="${requested#cek:}"
    is_cek_plugin "$plugin" && printf '%s\n' "$plugin" && return 0
    return 1
  fi
  for mapping in "${CEK_CAPABILITIES[@]}"; do
    IFS='|' read -r capability plugin <<< "$mapping"
    [ "$requested" = "$capability" ] && printf '%s\n' "$plugin" && return 0
  done
  return 1
}

require_claude_cli() {
  if ! command -v claude >/dev/null 2>&1; then
    echo "ERROR: this capability is a structured Claude Code plugin and requires the 'claude' CLI." >&2
    echo "Install Claude Code, then run the same SMART command again; no source selection is needed." >&2
    return 1
  fi
}

ensure_cek_marketplace() {
  local marketplaces
  marketplaces="$(claude plugin marketplace list --json 2>/dev/null || printf '[]')"
  if printf '%s' "$marketplaces" | grep -Fq "$CEK_MARKETPLACE_NAME" || \
     printf '%s' "$marketplaces" | grep -Fq "$CEK_MARKETPLACE_SOURCE"; then
    return 0
  fi
  echo "Adding the Context Engineering Kit marketplace ..."
  claude plugin marketplace add --scope "$PLUGIN_SCOPE" "$CEK_MARKETPLACE_SOURCE"
}

install_cek_plugin() { # install_cek_plugin <plugin> [update]
  local plugin="$1" mode="${2:-}" qualified short_qualified installed
  case "$PLUGIN_SCOPE" in
    user|project|local) ;;
    *) echo "ERROR: SMART_PLUGIN_SCOPE must be user, project, or local." >&2; return 1 ;;
  esac
  qualified="$plugin@$CEK_MARKETPLACE_ID"
  short_qualified="$plugin@$CEK_MARKETPLACE_NAME"
  require_claude_cli || return 1
  ensure_cek_marketplace || return 1
  installed="$(claude plugin list --json 2>/dev/null || printf '[]')"
  if printf '%s' "$installed" | grep -Fq "$qualified" || \
     printf '%s' "$installed" | grep -Fq "$short_qualified"; then
    if [ "$mode" = "update" ]; then
      echo "Updating native plugin '$qualified' ..."
      claude plugin update "$qualified"
    else
      echo "OK: native plugin '$qualified' is already installed."
    fi
    return 0
  fi
  echo "Installing native plugin '$qualified' for capability '$plugin' ..."
  claude plugin install --scope "$PLUGIN_SCOPE" "$qualified"
  echo "OK: installed native plugin '$qualified' (restart Claude Code to load it)."
}

is_blacklisted() {
  local s="$1"
  for p in "${BLACKLIST_PREFIXES[@]}"; do [[ "$s" == "$p"* ]] && return 0; done
  for e in "${BLACKLIST_EXACT[@]}"; do [[ "$s" == "$e" ]] && return 0; done
  return 1
}

api_ls() { # api_ls <repo> <branch> <path>  -> item names inside the path
  curl -fsSL "https://api.github.com/repos/$1/contents/$3?ref=$2" 2>/dev/null \
    | grep -o '"name": *"[^"]*"' | sed 's/"name": *"\(.*\)"/\1/' || true
}

list_available() {
  require_deps
  for src in "${SOURCES[@]}"; do
    IFS='|' read -r repo branch path <<< "$src"
    echo "SOURCE $repo/$path :"
    api_ls "$repo" "$branch" "$path" | sed 's/^/   - /'
  done
  echo "SOURCE aliases (local skills + nested claude-plugins-official) :"
  for a in "${ALIASES[@]}"; do
    IFS='|' read -r name _ _ _ <<< "$a"
    echo "   - $name"
  done
  echo "SOURCE $CEK_MARKETPLACE_SOURCE (native plugins, selected by capability) :"
  local mapping capability plugin
  for mapping in "${CEK_CAPABILITIES[@]}"; do
    IFS='|' read -r capability plugin <<< "$mapping"
    echo "   - $capability -> cek:$plugin"
  done
}

list_installed() {
  local dir="${1:-$TARGET_DIR_DEFAULT}"
  if [ -d "$dir" ]; then
    echo "Installed skills in $dir :"
    ls -1 "$dir" 2>/dev/null | sed 's/^/   - /' || echo "   (empty)"
  else
    echo "No skills installed ($dir does not exist)"
  fi
  if command -v claude >/dev/null 2>&1; then
    echo "Installed Claude Code plugins:"
    claude plugin list --json 2>/dev/null || echo "   (unable to query plugins)"
  else
    echo "Installed Claude Code plugins: (claude CLI unavailable)"
  fi
}

sparse_copy() { # sparse_copy <repo> <branch> <path-in-repo> <dest-dir>
  local repo="$1" branch="$2" path="$3" dest="$4" tmp
  tmp="$(mktemp -d)"
  # try the pinned branch; if it no longer exists, fall back to the repo's default branch
  if ! git clone --quiet --depth 1 --branch "$branch" --filter=blob:none --sparse \
      "https://github.com/$repo.git" "$tmp/repo" 2>/dev/null; then
    if ! git clone --quiet --depth 1 --filter=blob:none --sparse \
        "https://github.com/$repo.git" "$tmp/repo" 2>/dev/null; then
      rm -rf "$tmp"; return 1
    fi
    echo "NOTE: branch '$branch' not found in $repo — used its default branch instead."
  fi
  if [ "$path" = "." ]; then
    git -C "$tmp/repo" sparse-checkout disable 2>/dev/null || true
  else
    git -C "$tmp/repo" sparse-checkout set "$path" --skip-checks 2>/dev/null \
      || git -C "$tmp/repo" sparse-checkout set "$path" 2>/dev/null || true
    if [ ! -d "$tmp/repo/$path" ] || [ -z "$(ls -A "$tmp/repo/$path" 2>/dev/null)" ]; then
      rm -rf "$tmp"; return 1
    fi
  fi
  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  if [ "$path" = "." ]; then
    mkdir -p "$dest"
    cp -r "$tmp/repo"/. "$dest"
    rm -rf "$dest/.git"
  else
    cp -r "$tmp/repo/$path" "$dest"
  fi
  rm -rf "$tmp"
  return 0
}

record_install() { # record_install <target> <skill> <repo> <path>
  local target="$1" skill="$2" repo="$3" path="$4"
  mkdir -p "$target"
  echo "$(date -u +%F) $skill <- $repo|$path" >> "$target/.installed.log"
  ensure_gitignore "$target"
}

ensure_gitignore() { # keep downloaded skills out of the project repo
  local target="$1"
  # only act when we are inside a git work tree and using the default location
  [ "$target" = "$TARGET_DIR_DEFAULT" ] || return 0
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 0
  local root; root="$(git rev-parse --show-toplevel 2>/dev/null)" || return 0
  if ! grep -qxF ".claude/skills/" "$root/.gitignore" 2>/dev/null; then
    echo ".claude/skills/" >> "$root/.gitignore"
    echo "NOTE: added '.claude/skills/' to .gitignore (downloaded skills stay out of the repo)."
  fi
}

installed_source() { # installed_source <target> <skill> -> "repo|path" of the LAST recorded install
  local target="$1" skill="$2"
  [ -f "$target/.installed.log" ] || return 1
  grep " $skill <- " "$target/.installed.log" 2>/dev/null | tail -n1 | sed 's/.* <- //' || return 1
}

fetch_one() {
  local skill="$1" target="${2:-$TARGET_DIR_DEFAULT}" force="${3:-}"
  [ -n "$target" ] || target="$TARGET_DIR_DEFAULT"

  if is_blacklisted "$skill"; then
    echo "BLOCKED: '$skill' is BLACK-tier (never install — see SKILLS_CATALOG.md)." >&2
    return 1
  fi

  local cek_plugin
  if cek_plugin="$(resolve_cek_plugin "$skill")"; then
    if [ "$force" = "force" ]; then
      install_cek_plugin "$cek_plugin" update
    else
      install_cek_plugin "$cek_plugin"
    fi
    return $?
  fi
  if [[ "$skill" == cek:* ]]; then
    echo "ERROR: unknown Context Engineering Kit plugin capability '$skill'. Run --list." >&2
    return 1
  fi

  require_deps
  if [ -d "$target/$skill" ] && [ "$force" != "force" ]; then
    echo "OK: '$skill' already installed: $target/$skill (use --update to refresh)"
    return 0
  fi

  # 0) --update: prefer the SAME source recorded at install time (no silent source switch)
  if [ "$force" = "force" ]; then
    local prev
    if prev="$(installed_source "$target" "$skill")" && [ -n "$prev" ]; then
      local prev_repo="${prev%%|*}" prev_path="${prev#*|}" prev_branch=""
      for src in "${SOURCES[@]}"; do
        IFS='|' read -r r b _ <<< "$src"; [ "$r" = "$prev_repo" ] && prev_branch="$b"
      done
      for a in "${ALIASES[@]}"; do
        IFS='|' read -r n r b _ <<< "$a"; [ "$n" = "$skill" ] && [ "$r" = "$prev_repo" ] && prev_branch="$b"
      done
      [ -n "$prev_branch" ] || prev_branch="main"
      echo "Updating '$skill' from its recorded source $prev_repo ($prev_path) ..."
      if sparse_copy "$prev_repo" "$prev_branch" "$prev_path" "$target/$skill"; then
        echo "OK: refreshed at $target/$skill"
        record_install "$target" "$skill" "$prev_repo" "$prev_path"
        return 0
      fi
      echo "WARN: recorded source failed — falling back to the normal source order." >&2
    fi
  fi

  # 1) alias map (nested paths) — no API call needed
  for a in "${ALIASES[@]}"; do
    IFS='|' read -r name repo branch path <<< "$a"
    if [ "$name" = "$skill" ]; then
      echo "Downloading '$skill' from $repo ($path) ..."
      if sparse_copy "$repo" "$branch" "$path" "$target/$skill"; then
        echo "OK: installed at $target/$skill"
        record_install "$target" "$skill" "$repo" "$path"
        return 0
      fi
      echo "ERROR: alias source failed for '$skill'." >&2
      return 1
    fi
  done

  # 2) standard sources — check via API, fall back to blind sparse-checkout
  local api_ok=1
  for src in "${SOURCES[@]}"; do
    IFS='|' read -r repo branch path <<< "$src"
    local listing
    listing="$(api_ls "$repo" "$branch" "$path")"
    [ -z "$listing" ] && api_ok=0
    if echo "$listing" | grep -qx "$skill"; then
      echo "Downloading '$skill' from $repo ..."
      if sparse_copy "$repo" "$branch" "$path/$skill" "$target/$skill"; then
        echo "OK: installed at $target/$skill"
        record_install "$target" "$skill" "$repo" "$path/$skill"
        return 0
      fi
    fi
  done

  # 3) API may be rate-limited — try each source blindly
  if [ "$api_ok" = "0" ]; then
    echo "NOTE: GitHub API unavailable/rate-limited — trying sources directly ..."
    for src in "${SOURCES[@]}"; do
      IFS='|' read -r repo branch path <<< "$src"
      if sparse_copy "$repo" "$branch" "$path/$skill" "$target/$skill"; then
        echo "OK: installed at $target/$skill (from $repo)"
        record_install "$target" "$skill" "$repo" "$path/$skill"
        return 0
      fi
    done
  fi

  echo "ERROR: skill '$skill' not found in any source. Run --list to see sources." >&2
  return 1
}

case "${1:-}" in
  ""|-h|--help) usage ;;
  --list)       list_available ;;
  --installed)  list_installed "${2:-}" ;;
  --update)     [ -n "${2:-}" ] || usage; fetch_one "$2" "${3:-$TARGET_DIR_DEFAULT}" force ;;
  *)            fetch_one "$1" "${2:-}" ;;
esac
