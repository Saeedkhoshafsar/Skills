#!/usr/bin/env bash
# ============================================================
# fetch-skill.sh — on-demand download of a single skill from GitHub
# Downloads ONLY the requested skill folder (sparse-checkout), never the whole repo.
#
# Usage:
#   ./fetch-skill.sh <skill-name> [target-dir]
#   ./fetch-skill.sh --list                 # list skills available in sources
#   ./fetch-skill.sh --installed [dir]      # list installed skills
#
# Examples:
#   ./fetch-skill.sh sparc-methodology
#   ./fetch-skill.sh browser .claude/skills
# ============================================================
set -euo pipefail

# ---------- skill sources (repo|branch|path-inside-repo) ----------
SOURCES=(
  "Saeedkhoshafsar/Skills|genspark_ai_developer|skills"
  "Saeedkhoshafsar/ruflo|main|.claude/skills"
  "Saeedkhoshafsar/claude-plugins-official|main|plugins/claude-code-setup/skills"
)

TARGET_DIR_DEFAULT=".claude/skills"

usage() { sed -n '3,14p' "$0"; exit 1; }

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

fetch_one() {
  local skill="$1" target="${2:-$TARGET_DIR_DEFAULT}"

  if [ -d "$target/$skill" ]; then
    echo "OK: '$skill' already installed: $target/$skill"
    return 0
  fi

  for src in "${SOURCES[@]}"; do
    IFS='|' read -r repo branch path <<< "$src"
    # check whether this source has the skill
    if api_ls "$repo" "$branch" "$path" | grep -qx "$skill"; then
      echo "Downloading '$skill' from $repo ..."
      local tmp
      tmp="$(mktemp -d)"
      # sparse-checkout: only that subfolder
      git clone --quiet --depth 1 --filter=blob:none --sparse \
        "https://github.com/$repo.git" "$tmp/repo"
      git -C "$tmp/repo" sparse-checkout set "$path/$skill" --skip-checks 2>/dev/null \
        || git -C "$tmp/repo" sparse-checkout set "$path/$skill"
      mkdir -p "$target"
      cp -r "$tmp/repo/$path/$skill" "$target/$skill"
      rm -rf "$tmp"
      echo "OK: installed at $target/$skill"
      # record in install log
      mkdir -p "$(dirname "$target")"
      echo "$(date -u +%F) $skill <- $repo/$path" >> "$target/.installed.log"
      return 0
    fi
  done

  echo "ERROR: skill '$skill' not found in any source. Run --list to see sources." >&2
  return 1
}

case "${1:-}" in
  ""|-h|--help) usage ;;
  --list)       list_available ;;
  --installed)  list_installed "${2:-}" ;;
  *)            fetch_one "$1" "${2:-}" ;;
esac
