# Loop templates

Recurring recipes. `/loop <interval> <command>` runs in the current session; `/schedule` creates a cloud routine that runs without a terminal open.

| Name | Command | Cadence | Notes |
|---|---|---|---|
| Daily brief | `/loop 1d /daily-loop` | every morning | Writes `vault/plans/daily/<date>.md` |
| Deploy watch | `/loop 5m check the latest Vercel deployment for <project>; stop when READY or ERROR and report` | during deploys | Uses `web-debugger` on ERROR |
| Inbox sweep | `/loop 2h spawn ops-assistant for an inbox summary; only report if something is urgent` | workdays | Read-only |
| Vault gardening | `/loop 1w review vault/inbox, file everything with /vault-add, then /vault-sync` | weekly | Keeps inbox empty |

Rules for any loop:
- Loops are read-only by default; anything outward-facing (send, deploy, publish) requires an explicit per-run confirmation.
- A loop that finds nothing new says nothing (noop). Don't spam.
- Add new recipes here, not in CLAUDE.md.
