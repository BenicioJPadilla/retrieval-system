---
name: daily-loop
description: Standing daily check-in loop. Reviews open threads across the vault, inbox triage via ops-assistant, and project status, then writes a short brief. Use when the user says "/daily-loop", "morning brief", or "what should I focus on today".
---
# /daily-loop

Protocol (see `~/Projects/retrieval-system/protocols/loop-templates.md` for the recurring variants):

1. Read `vault/inbox/` for anything added since the last brief (check `git log -1 -- vault/inbox`).
2. `graphify query "what are the open threads and next actions across projects"` from `~/Projects/retrieval-system`.
3. Spawn `ops-assistant` for an inbox/calendar summary (read-only).
4. Write `vault/plans/daily/<yyyy-mm-dd>.md` with: **Top 3 today** · **Open threads** (project, then next action) · **Waiting on** · **Inbox highlights** · **For the vault** (things to `/vault-add`).
5. Print the Top 3 to the user. Then `/vault-sync`.

To run this on a schedule: `/loop 1d /daily-loop` in a long-lived session, or `/schedule` for a cloud routine.
