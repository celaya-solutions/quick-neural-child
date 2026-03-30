#!/bin/bash
# Auto-publish — Commits and pushes all changes to GitHub.
# Called after each day completes (via lifecycle.sh or manually).

set -euo pipefail
cd "$(dirname "$0")/.."

DAY=$(grep '^current_day:' psyche/age.md 2>/dev/null | sed 's/current_day: *//' | tr -d '[:space:]')
DAY=${DAY:-0}

git add -A
git diff --cached --quiet && { echo "No changes to publish."; exit 0; }
git commit -m "Day ${DAY} — Neural Child life update"
git push 2>/dev/null || echo "Push failed — will retry next day."
echo "Published day ${DAY} to GitHub."
