#!/usr/bin/env bash
set -euo pipefail
BASE="${1:-http://127.0.0.1:8000}"
KEY="${KOSI_API_KEY:-}"

echo "Health:"
curl -sS "$BASE/health" | head -c 500
echo
echo

HDR=()
if [[ -n "$KEY" ]]; then
  HDR=(-H "Authorization: Bearer $KEY")
fi

echo "Chat (non-stream):"
curl -sS "${HDR[@]}" -H "Content-Type: application/json" \
  -d '{"model":"kosi","stream":false,"messages":[{"role":"user","content":"Who are you in one sentence?"}]}' \
  "$BASE/v1/chat/completions" | head -c 1200
echo
