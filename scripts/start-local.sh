#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

API_PORT="${PRIZEPILOT_API_PORT:-8080}"
WEB_PORT="${PRIZEPILOT_WEB_PORT:-5173}"
API_URL="http://127.0.0.1:${API_PORT}"
WEB_URL="http://127.0.0.1:${WEB_PORT}"

if [ ! -x ".venv/bin/uvicorn" ]; then
  echo "Creating Python virtual environment and installing backend dependencies..."
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

if ! curl -fsS "${API_URL}/health" >/dev/null 2>&1; then
  echo "Starting PrizePilot API on ${API_URL}..."
  PYTHONPATH=backend .venv/bin/uvicorn prizepilot.main:app \
    --host 127.0.0.1 \
    --port "${API_PORT}" \
    > /tmp/prizepilot-api.log 2>&1 &
else
  echo "PrizePilot API is already running on ${API_URL}."
fi

for _ in {1..30}; do
  if curl -fsS "${API_URL}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsSI "${WEB_URL}" >/dev/null 2>&1; then
  echo "Starting PrizePilot web app on ${WEB_URL}..."
  VITE_API_BASE_URL="${API_URL}" npm run dev -- --port "${WEB_PORT}" \
    > /tmp/prizepilot-web.log 2>&1 &
else
  echo "PrizePilot web app is already running on ${WEB_URL}."
fi

for _ in {1..30}; do
  if curl -fsSI "${WEB_URL}" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo
echo "PrizePilot is ready:"
echo "  Web app: ${WEB_URL}"
echo "  API:     ${API_URL}"
echo
echo "Logs:"
echo "  API: /tmp/prizepilot-api.log"
echo "  Web: /tmp/prizepilot-web.log"

open "${WEB_URL}" >/dev/null 2>&1 || true

