# retrieval-system

> Shared to learn from and fork on GitHub. All rights reserved. No license is granted to reuse, modify or redistribute outside GitHub without permission.


A personal knowledge vault plus a Claude Code setup that reads from it, writes to it, and routes work to specialist agents. Clone it, point it at your own notes, and every Claude Code session on your machine starts with the same memory.

It is four things wired together:

1. **A vault**: plain markdown notes with frontmatter and `[[wiki-links]]`, in `vault/`.
2. **A knowledge graph over the vault**, built by [graphify](https://github.com/Graphify-Labs/graphify), so Claude asks the graph a question instead of grepping files.
3. **A global `CLAUDE.md`** (symlinked into `~/.claude/`) that tells every session to consult the graph at the start, and write back to the vault at the end.
4. **Agents and skills** (also symlinked into `~/.claude/`) that do the delegated work and keep the vault current.

| Path | Purpose |
|---|---|
| `CLAUDE.md` | Global instructions template (linked to `~/.claude/CLAUDE.md`). Fill in the placeholders. |
| `agents/` | Subagent definitions (linked to `~/.claude/agents`) |
| `skills/` | Slash commands: `/vault-add`, `/vault-sync`, `/daily-loop` (linked to `~/.claude/skills`) |
| `protocols/` | Session start, session end, and recurring loop recipes |
| `vault/` | The knowledge base. Ships with one fake example note per folder; conventions in `vault/README.md` |
| `graphify-out/` | Generated graph (`graph.json`, `GRAPH_REPORT.md`, `vault-graph.html`). Created on first build. |
| `scripts/` | Linking, syncing, ingesting, graph view, optional auto-sync and email notifications |
| `settings.example.json` | Optional Stop hook that runs the auto-sync after every turn |

## How retrieval works

**Build.** Run from the repo root, the build reads everything under the repo, mostly `vault/`, and extracts a graph: notes and the concepts in them become nodes; wiki-links, mentions and inferred relations become edges, each tagged `EXTRACTED`, `INFERRED` or `AMBIGUOUS`. It then clusters the graph into communities. Inside Claude Code, `/graphify .` does all of that in one go. On the command line it is two steps: `graphify .` (extract, writes `graph.json`) then `graphify cluster-only .` (communities, report, HTML). Either way you get:

- `graphify-out/graph.json`: the graph itself, which queries traverse.
- `graphify-out/GRAPH_REPORT.md`: a plain-language summary: hub ("god") nodes, communities, surprising connections. Skimmed at the start of broad tasks.
- `graphify-out/graph.html`, plus `vault-graph.html` from `scripts/build-graph-view.py`: a searchable visual map.

Markdown needs an LLM for semantic extraction. Either export an API key (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, ...) and run the CLI, or run `/graphify .` inside Claude Code, which uses the session itself. Once `graph.json` exists, `graphify .` is incremental and re-extracts only changed files (inside Claude Code, `/graphify . --update`). Code files are parsed locally and need no key (`--code-only`).

**Query.** `graphify query "<question>"` finds the nodes that match the question and walks outward (breadth-first by default, `--dfs` for a specific chain) capped in size (`--budget`, default 2000). The answer is a compact subgraph: the relevant notes, how they connect, and the source file of each. Claude reads that, then opens only the notes it points to. Other entry points: `graphify path "A" "B"`, `graphify explain "X"`, `graphify god-nodes`.

**The loop that keeps it current.**

```
session start ──> graphify query "<project> status, open items, decisions"
      │                       (protocols/session-start.md)
      v
    work  ──> agents write plans/research into vault/
      │
      v
session end ──> /vault-add decisions, open threads, workflows
      │         /vault-sync: sync sources, ingest docs, rebuild graph,     
      v                      rebuild vault-graph.html, commit
next session queries a graph that already knows what happened
```

`scripts/sync-sources.sh` mirrors other repos' `context/` folders into `vault/sources/<project>/`, and `scripts/ingest-docs.sh` converts PDFs, .docx, .pptx and .tex into markdown, so those land in the graph too. `scripts/convert-claude-export.py` turns the `conversations.json` from a claude.ai data export into vault notes under `vault/sources/claude-webapp/`.

## How agent delegation works

Claude Code reads every file in `~/.claude/agents/` as a subagent type. Because `scripts/link.sh` points that folder at `agents/` here, these agents exist in every project. Each file has frontmatter:

```yaml
---
name: planner
description: Turns a goal into a phased plan ... Use for "plan X", "break this down".
tools: Read, Grep, Glob, Bash, Write
model: sonnet        # optional; omit to inherit the main session's model
---
<system prompt: the agent's process and output format>
```

Routing is by `description`. When a request matches it ("plan the reminders feature", "why is /api/book 500ing"), the main session hands the task to that agent through the Agent tool. The agent runs in its own context window with only the listed tools, and returns a short result: a plan path, a ranked list of findings, a TL;DR. The main session keeps the conclusion, not the file dumps. You can also name an agent outright ("use web-reviewer on this diff").

| Agent | Routed to when | Writes |
|---|---|---|
| `planner` | "plan X", "how should we build Y" | `vault/plans/<date>-<slug>.md` |
| `researcher` | "research X", "compare A vs B" | `vault/research/<date>-<slug>.md` |
| `web-reviewer` | "review", "is this safe to ship", before any PR | findings only |
| `web-debugger` | "why is X failing in prod" | findings only |
| `ops-assistant` | "what's in my inbox", "prep me for tomorrow" | drafts only; never sends |
| `content-producer` | "make a graphic/video/post" | asset links |

Agents that write into the vault feed the next query: a plan or research note written today is a node in tomorrow's graph. `CLAUDE.md` adds standing routing rules on top (review before every PR, delegate hard planning). Agents that use MCP tools (Vercel, Supabase, Google, Canva, Higgsfield, Figma, context7) need those connectors enabled in your Claude account or Claude Code config; delete the agents you won't connect.

Skills work the same way: `~/.claude/skills/<name>/SKILL.md` becomes `/<name>`, and its `description` lets Claude invoke it unprompted ("remember this" triggers `/vault-add`).

## Setup from zero

Requirements: macOS (Linux works with `xdg-open` in place of `open`, and without the keychain fallback in `notify-email.sh`), git, Python 3, [Claude Code](https://claude.com/claude-code), and [uv](https://docs.astral.sh/uv/) (or pipx) to install graphify. Optional: `pdftotext` (`brew install poppler`) for PDF ingestion.

1. **Clone.** The scripts and docs assume this path; if you use another, search-and-replace `~/Projects/retrieval-system` across `CLAUDE.md`, `agents/`, `skills/`, `protocols/` and `settings.example.json`.
   ```bash
   git clone <this repo> ~/Projects/retrieval-system
   cd ~/Projects/retrieval-system
   git remote remove origin   # important: /vault-sync pushes when a remote exists, and your vault is private
   # later, to back it up: create your own PRIVATE repo, then
   # git remote add origin <your-private-repo> && git push -u origin HEAD
   ```
2. **Install graphify.**
   ```bash
   uv tool install graphifyy      # the PyPI package name has two y's; the command is `graphify`
   graphify --help
   ```
3. **Link into Claude Code.** This symlinks `~/.claude/CLAUDE.md`, `~/.claude/agents` and `~/.claude/skills` to this repo. Anything already there is moved to `~/.claude/backups/link-<timestamp>/` first, so merge your old `CLAUDE.md` and skills back in afterwards if you had any.
   ```bash
   ./scripts/link.sh
   graphify install --platform claude   # adds the /graphify skill (lands in skills/graphify/, gitignored)
   ```
4. **Make `CLAUDE.md` yours.** Fill in every `[PLACEHOLDER]` and delete what doesn't apply.
5. **Replace the example vault.** Read `vault/README.md`, delete the example notes (or keep them until you have real ones), and add a first note per project. `/vault-add` does this from inside Claude Code.
6. **Point the sync scripts at your stuff (optional).** Add `sync <project> context` lines to `scripts/sync-sources.sh` (projects are looked up under `~/Projects`, or `$PROJECTS_DIR` if set) and `put <folder> <file>` lines to `scripts/ingest-docs.sh`.
7. **Build the graph.** Without an API key: open Claude Code in the repo and run `/graphify .`. With one exported: `graphify . && graphify cluster-only .`. Then:
   ```bash
   python3 scripts/build-graph-view.py
   open graphify-out/vault-graph.html
   graphify query "what projects are active?"
   ```
8. **Commit your first vault.** `/vault-sync`, or `git add -A && git commit -m "vault: first notes"`.
9. **Optional extras.**
   - Auto-sync after every turn: merge `settings.example.json` into `~/.claude/settings.json`. It runs `scripts/auto-vault-sync.sh` in the background (code-only graph update, refuses to commit anything that looks like a credential, pushes only if a remote with an upstream exists). Log: `~/.cache/retrieval-system/auto-vault-sync.log`.
   - Email progress updates: set `NOTIFY_TO`, `NOTIFY_FROM` and a Resend key as described at the top of `scripts/notify-email.sh`.
   - Daily brief: `/loop 1d /daily-loop`. More recipes in `protocols/loop-templates.md`.

## Daily use

- `/vault-add <what to remember>`: file a note with the right folder and frontmatter.
- `/vault-sync`: refresh sources, rebuild the graph, commit.
- `/daily-loop`: morning brief into `vault/plans/daily/`.
- `graphify query "..."`: ask the vault from any shell.
- `open graphify-out/vault-graph.html`: the visual map.

## Privacy

The vault is plain text in a git repo. Keep the repo private if your notes are, never write credentials into it (say where they live instead), and remember that `graphify .` with an API key sends note text to that LLM provider for extraction.
