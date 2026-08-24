#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_ENV="$PROJECT_DIR/.env"
DEV_ENV="/Users/artem/dev/savenok/back/.env"

set -a
if [[ -f "$LOCAL_ENV" ]]; then
  source "$LOCAL_ENV"
elif [[ -f "$DEV_ENV" ]]; then
  source "$DEV_ENV"
fi
set +a

export YANDEX_MODEL="${YANDEX_MODEL:-aliceai-llm}"

cd "$PROJECT_DIR"
exec .venv/bin/uvicorn poc.main:app --reload --port 8000
