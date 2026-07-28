#!/usr/bin/env bash
# Usage: scripts/check_no_refs.sh <regex> [<regex> ...]
# Fails (exit 1) if any KEPT code still references the given pattern(s).
set -euo pipefail
cd "$(dirname "$0")/.."
PATHS=$(grep -v '^\s*$' scripts/kept_paths.txt | tr '\n' ' ')
status=0
for pat in "$@"; do
  echo "── checking for: $pat"
  if grep -rn --include='*.py' -E "$pat" ${PATHS}; then
    echo "❌ still referenced: $pat"
    status=1
  else
    echo "✅ clean: $pat"
  fi
done
exit $status
