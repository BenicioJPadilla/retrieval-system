---
name: vault-add
description: File a note into the knowledge vault (~/Projects/retrieval-system/vault/) with proper frontmatter and wiki-links, then rebuild the graph. Use when the user says "remember this", "add to the vault", "note that...", or hands you a fact/decision/contact worth keeping.
---
# /vault-add

Arguments: free text describing what to capture. `$ARGUMENTS`

1. Decide the folder by type:
   - project facts: `vault/projects/<project>.md` (append to the existing note if one exists)
   - person/client/company: `vault/people-and-clients/<name>.md`
   - a decision and its rationale: `vault/decisions/<yyyy-mm-dd>-<slug>.md`
   - a repeatable process: `vault/workflows/<slug>.md`
   - research findings: `vault/research/<yyyy-mm-dd>-<slug>.md`
   - unclear: `vault/inbox/<yyyy-mm-dd>-<slug>.md`
2. Frontmatter (required):
   ```yaml
   ---
   title: ...
   type: project | person | decision | workflow | research | plan | note
   tags: [..]
   updated: YYYY-MM-DD
   ---
   ```
3. Body: concise, factual, dated where relevant. Link related notes with `[[note-title]]`. No credentials (API keys, passwords): say where they live instead.
4. Rebuild: inside Claude Code, `/graphify . --update`. On the command line with an LLM API key exported: `cd ~/Projects/retrieval-system && graphify . && graphify cluster-only .` (extraction is incremental once `graph.json` exists).
5. Report the path written and a one-line summary. Don't commit: that's `/vault-sync`.
