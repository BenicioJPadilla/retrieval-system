---
title: Vault conventions
type: note
tags: [meta, conventions]
updated: 2026-01-01
---
# Vault conventions

This folder is the knowledge base that graphify indexes. Every file here is an
example with made-up content: replace or delete them once you have real notes.

## Folders

| Folder | What goes in it | File name |
|---|---|---|
| `inbox/` | Unsorted captures; file them weekly | `<yyyy-mm-dd>-<slug>.md` |
| `projects/` | One living note per project: status, open threads, next actions | `<project>.md` |
| `people-and-clients/` | One note per person, client or company | `<name>.md` |
| `decisions/` | ADR-style log: what was decided, why, what was rejected | `<yyyy-mm-dd>-<slug>.md` |
| `workflows/` | How-I-do-X: repeatable processes | `<slug>.md` |
| `plans/` | Phased plans written by the `planner` agent; `plans/daily/` holds `/daily-loop` briefs | `<yyyy-mm-dd>-<slug>.md` |
| `research/` | Sourced notes written by the `researcher` agent | `<yyyy-mm-dd>-<slug>.md` |
| `sources/<project>/` | Read-only mirrors of other repos' `context/` docs (`scripts/sync-sources.sh`) and converted documents (`scripts/ingest-docs.sh`). Edit the originals, not the mirror. | as synced |

## Frontmatter (required on every note)

```yaml
---
title: Human-readable title
type: project | person | decision | workflow | research | plan | note
tags: [short, lowercase, tags]
updated: YYYY-MM-DD
---
```

Optional: `sources: [urls]` on research notes, `status:` on projects and plans.

## Links

Link related notes with `[[note-title]]` (the file name without `.md`). Links are
what graphify turns into edges, so a note with no links is an island. Link
liberally; a link to a note that does not exist yet is fine and marks something
worth writing.

## Rules

- No credentials, ever. Write where a key lives ("in the keychain as `x`"), never the key.
- Keep notes short and factual; date anything that will go stale.
- Add notes with `/vault-add`; commit with `/vault-sync`.
