---
title: Deploy checklist
type: workflow
tags: [workflow, deploy, example]
updated: 2026-01-01
---
# Deploy checklist

Example workflow note: a process you repeat, written down once.

1. Branch per change, open a PR.
2. Run the `web-reviewer` agent over the diff.
3. Merge; watch the Vercel deployment until READY (`/loop 5m` recipe in `protocols/loop-templates.md`).
4. On ERROR, hand the logs to `web-debugger`.

Used by: [[example-app]].
