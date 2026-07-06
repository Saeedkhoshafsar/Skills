#!/usr/bin/env bash
# راه‌اندازی حافظه‌ی پروژه در پروژه‌ی هدف
# استفاده: ./init-project-memory.sh /path/to/your/project
set -e
TARGET="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$TARGET/.project-memory"
cp -n "$SCRIPT_DIR/templates/project-memory/"*.md "$TARGET/.project-memory/" 2>/dev/null || true
echo "✅ حافظه‌ی پروژه ساخته شد: $TARGET/.project-memory/"
ls "$TARGET/.project-memory/"
