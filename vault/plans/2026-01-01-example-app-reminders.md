---
title: Example App email reminders plan
type: plan
tags: [plan, example]
status: draft
updated: 2026-01-01
---
# Example App email reminders

Example of what the `planner` agent writes.

**Context:** clients of [[example-app]] forget bookings.

**Approach:** a daily scheduled function that emails tomorrow's bookings.

**Phases**
1. Add a `reminder_sent_at` column. Done when the migration runs locally.
2. Scheduled function sends and stamps. Done when a test booking gets one email, once.

**Risks:** double sends on retry; guard with the stamp.

**Verification:** create a booking for tomorrow, run the function twice, see one email.
