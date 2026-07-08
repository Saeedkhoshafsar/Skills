#!/usr/bin/env bash
# ============================================================
# fetch-skill.sh — on-demand download of a single skill from GitHub
# Downloads ONLY the requested skill folder (sparse-checkout), never the whole repo.
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
)

# skills that must NEVER be installed (see SKILLS_CATALOG.md, BLACK tier)
BLACKLIST_PREFIXES=("v3-" "flow-nexus-")
BLACKLIST_EXACT=("dual-mode" "worker-benchmarks" "using-superpowers")

TARGET_DIR_DEFAULT=".claude/skills"

usage() {
  cat <<'EOF'
fetch-skill.sh — on-demand download of a single skill from GitHub
Downloads ONLY the requested skill folder (sparse-checkout), never the whole repo.

Usage:
  ./fetch-skill.sh <skill-name> [target-dir]
  ./fetch-skill.sh --list                 # list skills available in sources
  ./fetch-skill.sh --installed [dir]      # list installed skills
  ./fetch-skill.sh --update <skill-name>  # re-download an installed skill (same source)

Examples:
  ./fetch-skill.sh sparc-methodology
  ./fetch-skill.sh test-driven-development
  ./fetch-skill.sh ui-ux-pro-max
  ./fetch-skill.sh pdf .claude/skills
  ./fetch-skill.sh --update frontend-design
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
}

list_installed() {
  local dir="${1:-$TARGET_DIR_DEFAULT}"
  if [ -d "$dir" ]; then
    echo "Installed skills in $dir :"
    ls -1 "$dir" 2>/dev/null | sed 's/^/   - /' || echo "   (empty)"
  else
    echo "No skills installed ($dir does not exist)"
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
  git -C "$tmp/repo" sparse-checkout set "$path" --skip-checks 2>/dev/null \
    || git -C "$tmp/repo" sparse-checkout set "$path" 2>/dev/null || true
  if [ ! -d "$tmp/repo/$path" ] || [ -z "$(ls -A "$tmp/repo/$path" 2>/dev/null)" ]; then
    rm -rf "$tmp"; return 1
  fi
  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  cp -r "$tmp/repo/$path" "$dest"
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

require_deps
case "${1:-}" in
  ""|-h|--help) usage ;;
  --list)       list_available ;;
  --installed)  list_installed "${2:-}" ;;
  --update)     [ -n "${2:-}" ] || usage; fetch_one "$2" "${3:-$TARGET_DIR_DEFAULT}" force ;;
  *)            fetch_one "$1" "${2:-}" ;;
esac
