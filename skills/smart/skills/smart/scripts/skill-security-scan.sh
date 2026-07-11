#!/usr/bin/env bash
# Conservative static pre-screen for quarantined external skills.
set -euo pipefail

usage() {
  echo "Usage: $0 <quarantined-skill-directory> [report-file]" >&2
  exit 2
}

ROOT="${1:-}"
REPORT="${2:-}"
[ -n "$ROOT" ] || usage
[ -d "$ROOT" ] || { echo "ERROR: scan root is not a directory: $ROOT" >&2; exit 2; }

ROOT_REAL="$(cd "$ROOT" && pwd -P)"
EXPECTED_REPORT="$ROOT_REAL/.smart-scan-report.txt"
if [ -z "$REPORT" ]; then
  REPORT="$EXPECTED_REPORT"
else
  report_parent="$(cd "$(dirname "$REPORT")" 2>/dev/null && pwd -P)" || {
    echo "ERROR: report parent does not exist" >&2
    exit 2
  }
  REPORT="$report_parent/$(basename "$REPORT")"
  [ "$REPORT" = "$EXPECTED_REPORT" ] || {
    echo "ERROR: report must be written as $EXPECTED_REPORT" >&2
    exit 2
  }
fi

MAX_FILES="${SMART_SCAN_MAX_FILES:-2000}"
MAX_BYTES="${SMART_SCAN_MAX_BYTES:-52428800}"
[[ "$MAX_FILES" =~ ^[0-9]+$ ]] && [[ "$MAX_BYTES" =~ ^[0-9]+$ ]] || {
  echo "ERROR: scan limits must be non-negative integers" >&2
  exit 2
}
findings=0
fatal=0

emit() {
  printf '%s\n' "$*" | tee -a "$REPORT"
}

flag() {
  findings=$((findings + 1))
  emit "FINDING [$1] $2"
}

block() {
  fatal=$((fatal + 1))
  emit "BLOCKER [$1] $2"
}

: > "$REPORT"
emit "SMART SKILL STATIC SCAN"
emit "root=$ROOT_REAL"
emit "scanned_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

file_count="$(find "$ROOT_REAL" -xdev -type f | wc -l | tr -d ' ')"
total_bytes="$(find "$ROOT_REAL" -xdev -type f -printf '%s\n' | awk '{s+=$1} END {print s+0}')"
emit "file_count=$file_count"
emit "total_bytes=$total_bytes"

[ "$file_count" -le "$MAX_FILES" ] || block "LIMIT" "file count $file_count exceeds $MAX_FILES"
[ "$total_bytes" -le "$MAX_BYTES" ] || block "LIMIT" "size $total_bytes exceeds $MAX_BYTES bytes"

while IFS= read -r -d '' link; do
  target="$(readlink "$link")"
  block "SYMLINK" "${link#"$ROOT_REAL"/} -> $target"
done < <(find "$ROOT_REAL" -xdev -type l -print0)

while IFS= read -r -d '' file; do
  links="$(stat -c '%h' "$file" 2>/dev/null || printf '1')"
  [ "$links" -le 1 ] || block "HARDLINK" "${file#"$ROOT_REAL"/} has $links links"
  if [ -x "$file" ]; then
    flag "EXECUTABLE" "${file#"$ROOT_REAL"/}"
  fi
  mime="$(file -b --mime-type "$file" 2>/dev/null || printf 'unknown')"
  case "$mime" in
    text/*|application/json|application/xml|application/x-shellscript|application/javascript|inode/x-empty) ;;
    *) flag "NON_TEXT" "${file#"$ROOT_REAL"/} ($mime)" ;;
  esac
done < <(find "$ROOT_REAL" -xdev -type f ! -path "$REPORT" -print0)

PATTERNS=(
  'curl[^#|]*\|[[:space:]]*(ba)?sh'
  'wget[^#|]*\|[[:space:]]*(ba)?sh'
  '(^|[;&|[:space:]])eval[[:space:]]'
  '(^|[;&|[:space:]])sudo[[:space:]]'
  'rm[[:space:]]+-[^[:space:]]*r[^[:space:]]*f[[:space:]]+/'
  '(\.ssh|\.aws|\.gnupg|\.git-credentials)'
  '(GITHUB_TOKEN|ANTHROPIC_API_KEY|OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY)'
  '(base64[[:space:]]+(-d|--decode))'
  '(/etc/|/var/|/usr/|/root/)'
  '(nc|ncat|netcat)[[:space:]]+-'
)

for pattern in "${PATTERNS[@]}"; do
  matches="$(grep -RInE --binary-files=without-match \
    --exclude='.smart-scan-report.txt' --exclude-dir='.git' \
    "$pattern" "$ROOT_REAL" 2>/dev/null || true)"
  if [ -n "$matches" ]; then
    flag "PATTERN" "$pattern"
    while IFS= read -r line; do emit "  ${line#"$ROOT_REAL"/}"; done <<< "$matches"
  fi
done

license_files="$(find "$ROOT_REAL" -maxdepth 2 -type f \( -iname 'LICENSE*' -o -iname 'COPYING*' \) -print 2>/dev/null || true)"
if [ -z "$license_files" ]; then
  flag "LICENSE" "no license file found within two levels"
else
  while IFS= read -r license; do emit "license_file=${license#"$ROOT_REAL"/}"; done <<< "$license_files"
fi

emit "finding_count=$findings"
emit "blocker_count=$fatal"
if [ "$fatal" -gt 0 ]; then
  emit "result=BLOCKED"
  exit 1
fi
if [ "$findings" -gt 0 ]; then
  emit "result=REVIEW_REQUIRED"
else
  emit "result=STATIC_SCAN_PASSED"
fi
emit "note=Static scanning cannot prove safety; manual review is mandatory before activation."
