# Global Claude Config: [YOUR NAME]

<!--
TEMPLATE. scripts/link.sh symlinks this file to ~/.claude/CLAUDE.md, so it loads in
EVERY Claude Code session. Replace every [BRACKETED PLACEHOLDER], delete what you
don't want, and keep it short: every line here costs context in every session.
-->

This file lives in `~/Projects/retrieval-system` (symlinked to `~/.claude/CLAUDE.md`) and loads in **every** session. It's the hub: agents, skills, loop protocols, and a graphify-indexed knowledge vault.

## Who I am
<!-- PLACEHOLDER: 2 to 4 lines. What you do, what kinds of projects you run, your usual stack, your pronouns if you want them used. -->
- [ROLE, e.g. "Backend engineer; side projects in X and Y."]
- [MAIN PROJECTS OR CLIENT TYPES, no credentials]
- [PRONOUNS, or "use they/them"]

## Session protocol
1. **Start**: read `~/Projects/retrieval-system/protocols/session-start.md`. If the task touches anything non-trivial, skim `~/Projects/retrieval-system/graphify-out/GRAPH_REPORT.md` for context.
2. **During**: to learn about my projects, clients, past decisions, or workflows, query the vault (`graphify query "<question>"` run from `~/Projects/retrieval-system`) before grepping the vault's markdown by hand.
3. **End**: follow `protocols/session-end.md`: capture decisions/open threads into `vault/`, then `/vault-sync`.

## The vault (`~/Projects/retrieval-system/vault/`)
- `sources/<project>/` read-only mirrors of other repos' `context/` docs (synced by `scripts/sync-sources.sh`; edit the originals, not the mirror) and converted documents (`scripts/ingest-docs.sh`).
- `projects/` one note per project · `people-and-clients/` · `decisions/` ADR-style log · `workflows/` how-I-do-X · `plans/` · `research/` · `inbox/` unsorted captures.
<!-- PLACEHOLDER: add your own folders here (e.g. a writing folder, a reading-notes folder) and say what feeds them. -->
- Every note has YAML frontmatter (`title`, `type`, `tags`, `updated`) and links with `[[wiki-links]]`. Conventions: `vault/README.md`.
- Add notes with `/vault-add`. Never put credentials in the vault.
- Visual map: `open ~/Projects/retrieval-system/graphify-out/vault-graph.html` (say "open my graph").

## Agents (in `agents/`, available everywhere)
- `web-reviewer`: Next.js/Supabase/Vercel code review + pre-deploy sanity.
- `web-debugger`: log-driven debugging via Vercel runtime logs and Supabase advisors/logs.
- `content-producer`: brief to Canva / Higgsfield / Figma assets.
- `researcher`: web + docs research; writes findings into `vault/research/`.
- `planner`: goal to phased plan in `vault/plans/`.
- `ops-assistant`: email / calendar / Drive triage and drafting (read-first, confirm before sending).
<!-- PLACEHOLDER: delete agents whose tools you don't have connected; add your own. -->

## Skills
- `/vault-add` · `/vault-sync` · `/daily-loop` (see `protocols/loop-templates.md` for recurring recipes).
- `/graphify` (installed by `graphify install`): build, update and query the graph from inside Claude Code.

## Working preferences
<!-- PLACEHOLDER: these are working defaults that suit a solo builder. Keep, edit or delete each one. -->
- [PERSONAL BOUNDARIES, optional: e.g. working hours.]
- Be direct; lead with the answer. Short recaps at the end of work.
- Confirm before anything outward-facing (sending email, publishing, deploying to prod, deleting).
- Push back when something doesn't make sense; don't just agree.
- Prefer editing existing files over creating new ones; don't add docs unless asked.
- Reference code as `path:line`.
- **Attempt it before you assess it.** "I can't" is only for things genuinely outside reach (credentials I don't have, an account you're not in). Inside the real limits, go at it properly; if it fails, say exactly where it broke. Read `--help` before accepting a blocker.
- **Delegate planning and hard work.** For planning, architecture, gnarly debugging and audits, dispatch a subagent (`planner`, or a general agent with `model: "opus"`) rather than grinding it out inline.
- **Always run a review pass and a cleanup pass.** Before any PR, send the diff to `web-reviewer` (or `/code-review`). After a stretch of building, run `/simplify`. They are part of finishing, not extras.
- **Branch per feature.** Never commit straight to `main`; one branch and one coherent commit per logical change, then a PR. Exception: vault commits from `/vault-sync` and `/vault-add` in this repo go straight to `main`.
- **When the right call is clear, make it.** Asking is for genuine forks, not for confirmation of what you already know.
- **Verify against the artifact, not a proxy.** Before concluding from a scan, ask what a negative result would actually prove. Prefer ground truth: does the request succeed, what does the live URL serve.
- **Email me progress updates** (optional). For multi-step or loop tasks, send a short email at each checkpoint with `~/Projects/retrieval-system/scripts/notify-email.sh "<subject>" "<body>"` (needs `NOTIFY_TO`, `NOTIFY_FROM` and a Resend key; see the script header). Delete this line if you don't set it up.
