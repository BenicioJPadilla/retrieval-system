---
name: vault-sync
description: Rebuild the graphify graph over the vault, then commit (and push, if an upstream is set) the retrieval-system repo. Use at session end or whenever the user says "sync the vault" / "save config".
---
# /vault-sync

Run from `~/Projects/retrieval-system`:

1. Refresh inputs: `./scripts/sync-sources.sh` (mirrors other repos' `context/` docs into `vault/sources/`) and `./scripts/ingest-docs.sh` (converts PDFs, .docx, .pptx, .tex into markdown under `vault/`).
2. Rebuild the graph. Inside Claude Code: `/graphify . --update` (or `/graphify .` if `graphify-out/graph.json` is missing). On the command line with an LLM API key exported: `graphify . && graphify cluster-only .` (extraction is incremental once `graph.json` exists; `cluster-only` rewrites `GRAPH_REPORT.md`).
3. Regenerate the visual map: `python3 scripts/build-graph-view.py` (writes `graphify-out/vault-graph.html`).
4. `git add -A && git status --short`: show what changed.
5. If there are changes: commit with a message summarizing the vault/agent/skill edits (e.g. `vault: add acme invoicing decision; agents: tune web-reviewer`). Push only if the repo has a remote with an upstream (it should be your own private repo).
6. Report: files changed, commit hash, and any graphify warnings.

Abort and tell the user if `git status` shows anything that looks like a credential (API key, password, private key).
