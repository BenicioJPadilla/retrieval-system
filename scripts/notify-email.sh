#!/usr/bin/env bash
# Email yourself a progress/milestone update via Resend (https://resend.com).
# Usage: scripts/notify-email.sh "<subject>" "<body text>"
# Config (environment, never committed):
#   NOTIFY_TO       recipient address (required)
#   NOTIFY_FROM     sender, on a domain verified in Resend (required), e.g. "Claude <notify@example.com>"
#   RESEND_API_KEY  the key; if unset, read from the macOS keychain item named by NOTIFY_KEYCHAIN_ITEM
#                   (default "resend-notify"): security add-generic-password -s resend-notify -a "$USER" -w
# This repo holds no credentials: keep the key in the keychain or your shell environment.
set -euo pipefail
TO="${NOTIFY_TO:?set NOTIFY_TO to your email address}"
FROM="${NOTIFY_FROM:?set NOTIFY_FROM to a sender on your verified Resend domain}"
KEY="${RESEND_API_KEY:-}"
[ -n "$KEY" ] || KEY=$(security find-generic-password -s "${NOTIFY_KEYCHAIN_ITEM:-resend-notify}" -w 2>/dev/null || true)
[ -n "$KEY" ] || { echo "notify-email: no RESEND_API_KEY found" >&2; exit 1; }
PAYLOAD=$(python3 -c 'import sys,json; print(json.dumps({"from":sys.argv[1],"to":[sys.argv[2]],"subject":sys.argv[3],"text":sys.argv[4]}))' "$FROM" "$TO" "$1" "$2")
RESP=$(curl -sS -w '\n%{http_code}' -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -A "claude-code-notify/1.0" --max-time 20 --data "$PAYLOAD")
CODE=$(printf '%s' "$RESP" | tail -n1)
if [ "$CODE" = "200" ] || [ "$CODE" = "201" ]; then
  echo "notify-email: sent ($CODE)"
else
  echo "notify-email: resend error $CODE: $(printf '%s' "$RESP" | sed '$d' | head -c 300)" >&2; exit 1
fi
