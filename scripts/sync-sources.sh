#!/usr/bin/env bash
# Mirror context docs from other projects into vault/sources/<project>/ so graphify indexes them.
# Add a `sync` line per project at the bottom. Re-run any time (idempotent); /vault-sync calls this.
# The mirror is read-only: edit the originals in each project, not the copies here.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
P="${PROJECTS_DIR:-$HOME/Projects}"
sync() { # project  path...
  local proj="$1"; shift
  local dst="$REPO/vault/sources/$proj"; mkdir -p "$dst"
  for src in "$@"; do
    [ -e "$P/$proj/$src" ] || { echo "skip $proj/$src (missing)"; continue; }
    if [ -d "$P/$proj/$src" ]; then rsync -a --delete --include='*/' --include='*.md' --include='*.txt' --exclude='*' "$P/$proj/$src/" "$dst/$src/"
    else cp "$P/$proj/$src" "$dst/$src"; fi
  done
  echo "synced $proj"
}

# ---- your projects (examples; uncomment and edit) ----
# sync my-web-app context
# sync my-other-app context.md DEPLOY.md
