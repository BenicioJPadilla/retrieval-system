#!/usr/bin/env bash
# Idempotently symlink ~/.claude/{CLAUDE.md,agents,skills} -> this repo. Backs up anything non-empty it replaces.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
CL="$HOME/.claude"
mkdir -p "$CL"
BK="$CL/backups/link-$(date +%Y%m%d-%H%M%S)"
link() { # src target
  local src="$1" dst="$2"
  if [ -L "$dst" ]; then
    [ "$(readlink "$dst")" = "$src" ] && { echo "ok   $dst"; return; }
    rm "$dst"
  elif [ -e "$dst" ]; then
    if [ -d "$dst" ] && [ -z "$(ls -A "$dst")" ]; then rmdir "$dst"
    else mkdir -p "$BK"; mv "$dst" "$BK/"; echo "backed up $dst -> $BK/"; fi
  fi
  ln -s "$src" "$dst"; echo "link $dst -> $src"
}
link "$REPO/CLAUDE.md" "$CL/CLAUDE.md"
link "$REPO/agents"    "$CL/agents"
link "$REPO/skills"    "$CL/skills"
