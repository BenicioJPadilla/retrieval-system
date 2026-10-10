#!/usr/bin/env bash
# Optional: run a lightweight /vault-sync unattended after every Claude Code turn (Stop hook, backgrounded).
# See settings.example.json for the hook. One run at a time; exits early when nothing changed;
# refuses to commit anything that looks like a credential. Pushes only if the branch has an upstream.
# Log: ~/.cache/retrieval-system/auto-vault-sync.log
set -uo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$HOME/.cache/retrieval-system"
LOCK="$LOG_DIR/auto-vault-sync.lock"
mkdir -p "$LOG_DIR"
exec >>"$LOG_DIR/auto-vault-sync.log" 2>&1

# One at a time: mkdir is atomic. A lock older than 30 min is a crashed run.
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +30 2>/dev/null)" ]; then
    rm -rf "$LOCK" && mkdir "$LOCK" || exit 0
  else
    exit 0
  fi
fi
trap 'rm -rf "$LOCK"' EXIT

cd "$REPO" || exit 1
echo "=== $(date '+%F %T') auto-vault-sync"

./scripts/sync-sources.sh >/dev/null || echo "sync-sources failed"
./scripts/ingest-docs.sh >/dev/null || echo "ingest-docs failed"

if [ -z "$(git status --porcelain)" ]; then
  echo "no changes"
  exit 0
fi

# No LLM key assumed when unattended: index code only here; a manual /vault-sync does the full semantic pass.
graphify . --code-only >/dev/null && graphify cluster-only . --no-label >/dev/null || echo "graphify update failed"
[ -f graphify-out/graph.json ] && { python3 scripts/build-graph-view.py >/dev/null || echo "graph view failed"; }

git add -A
if git diff --cached -- . ':!scripts/auto-vault-sync.sh' | grep -E '^\+' | grep -qiE '(sk-[a-z0-9_-]{20,}|sk_live_|rk_live_|re_[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{30,}\.|-----BEGIN [A-Z ]*PRIVATE KEY|(api[_-]?key|secret|password|token)["'\'' ]*[:=]["'\'' ]*[A-Za-z0-9/+_-]{16,})'; then
  git reset -q
  echo "ABORTED: staged diff looks like it contains a credential; nothing committed"
  [ -n "${NOTIFY_TO:-}" ] && "$REPO/scripts/notify-email.sh" "vault auto-sync aborted: possible credential" "The per-turn vault sync found something that looks like a credential and committed nothing. Check git status in $REPO." >/dev/null 2>&1
  exit 1
fi

files=$(git diff --cached --name-only | sed 's#.*/##' | head -5 | paste -sd, - | sed 's/,/, /g')
git commit -qm "vault: auto-sync ($files)" && echo "committed $(git rev-parse --short HEAD)"
git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1 && { git push -q && echo "pushed" || echo "push failed"; }
exit 0
