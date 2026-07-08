#!/usr/bin/env bash
# ============================================================
# fetch-skill.sh — دانلود on-demand یک اسکیل از گیت‌هاب
# فقط همان اسکیلی که لازم است دانلود می‌شود؛ نه کل ریپو.
#
# Usage:
#   ./fetch-skill.sh <skill-name> [target-dir]
#   ./fetch-skill.sh --list                 # لیست اسکیل‌های موجود در منابع
#   ./fetch-skill.sh --installed [dir]      # لیست اسکیل‌های نصب‌شده
#
# Examples:
#   ./fetch-skill.sh sparc-methodology
#   ./fetch-skill.sh browser .claude/skills
# ============================================================
set -euo pipefail

# ---------- منابع اسکیل (repo|branch|path-inside-repo) ----------
SOURCES=(
  "Saeedkhoshafsar/Skills|genspark_ai_developer|skills"
  "Saeedkhoshafsar/ruflo|main|.claude/skills"
  "Saeedkhoshafsar/claude-plugins-official|main|plugins/claude-code-setup/skills"
)

TARGET_DIR_DEFAULT=".claude/skills"

usage() { sed -n '3,14p' "$0"; exit 1; }

api_ls() { # api_ls <repo> <branch> <path>  -> نام آیتم‌های داخل مسیر
  curl -fsSL "https://api.github.com/repos/$1/contents/$3?ref=$2" 2>/dev/null \
    | grep -o '"name": *"[^"]*"' | sed 's/"name": *"\(.*\)"/\1/' || true
}

list_available() {
  for src in "${SOURCES[@]}"; do
    IFS='|' read -r repo branch path <<< "$src"
    echo "📦 $repo/$path :"
    api_ls "$repo" "$branch" "$path" | sed 's/^/   ├── /'
  done
}

list_installed() {
  local dir="${1:-$TARGET_DIR_DEFAULT}"
  if [ -d "$dir" ]; then
    echo "🗂  اسکیل‌های نصب‌شده در $dir :"
    ls -1 "$dir" 2>/dev/null | sed 's/^/   ├── /' || echo "   (خالی)"
  else
    echo "🗂  هیچ اسکیلی نصب نشده ($dir وجود ندارد)"
  fi
}

fetch_one() {
  local skill="$1" target="${2:-$TARGET_DIR_DEFAULT}"

  if [ -d "$target/$skill" ]; then
    echo "✅ '$skill' از قبل نصب است: $target/$skill"
    return 0
  fi

  for src in "${SOURCES[@]}"; do
    IFS='|' read -r repo branch path <<< "$src"
    # وجود اسکیل را چک کن
    if api_ls "$repo" "$branch" "$path" | grep -qx "$skill"; then
      echo "⬇️  دانلود '$skill' از $repo ..."
      local tmp
      tmp="$(mktemp -d)"
      # فقط همان زیرپوشه با sparse-checkout
      git clone --quiet --depth 1 --filter=blob:none --sparse \
        "https://github.com/$repo.git" "$tmp/repo"
      git -C "$tmp/repo" sparse-checkout set "$path/$skill" --skip-checks 2>/dev/null \
        || git -C "$tmp/repo" sparse-checkout set "$path/$skill"
      mkdir -p "$target"
      cp -r "$tmp/repo/$path/$skill" "$target/$skill"
      rm -rf "$tmp"
      echo "✅ نصب شد: $target/$skill"
      # ثبت در لاگ نصب
      mkdir -p "$(dirname "$target")"
      echo "$(date -u +%F) $skill <- $repo/$path" >> "$target/.installed.log"
      return 0
    fi
  done

  echo "❌ اسکیل '$skill' در هیچ منبعی یافت نشد. با --list منابع را ببین." >&2
  return 1
}

case "${1:-}" in
  ""|-h|--help) usage ;;
  --list)       list_available ;;
  --installed)  list_installed "${2:-}" ;;
  *)            fetch_one "$1" "${2:-}" ;;
esac
