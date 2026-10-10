---
title: Use Supabase Auth for Example App
type: decision
tags: [decision, auth, example]
updated: 2026-01-01
---
# Use Supabase Auth for Example App

**Context:** [[example-app]] needs logins for staff only, about five users.

**Decision:** use Supabase Auth with magic links. No passwords to store.

**Rejected:** a separate auth provider (one more bill and dashboard for five users).

**Revisit if:** customers need accounts too.
