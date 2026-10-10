# Session start

1. Identify the project you're in (`pwd`, its `CLAUDE.md`, `context/` or `context.md` if present).
2. Check the vault for that project: `cd ~/Projects/retrieval-system && graphify query "<project name> status, open items, decisions"`. If the vault has nothing, say so and carry on. Don't invent context.
3. Look at `vault/plans/` for an active plan touching this work; continue it rather than starting fresh.
4. Confirm scope with the user in one line.
5. **Decide the branch split before writing code.** One branch off `main` per logical change, one coherent commit each, merged by PR. Never straight to `main`, never unrelated work in one commit. Then work.

Don't re-read `graphify-out/GRAPH_REPORT.md` in full every session: only when the task is broad (planning, cross-project, "what should I work on").
