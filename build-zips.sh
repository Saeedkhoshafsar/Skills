#!/usr/bin/env bash
# ساخت ZIP هر اسکیل جداگانه (برای آپلود در claude.ai) + ZIP کل مخزن
set -e
cd "$(dirname "$0")"
rm -rf dist && mkdir -p dist

for d in skills/*/; do
  name=$(basename "$d")
  (cd skills && zip -qr "../dist/${name}.zip" "$name" -x "*.DS_Store")
  echo "✅ dist/${name}.zip"
done

zip -qr dist/dev-team-skills-full.zip skills templates README.md AGENT_PROMPT.md init-project-memory.sh -x "*.DS_Store"
echo "✅ dist/dev-team-skills-full.zip (کل مخزن)"
