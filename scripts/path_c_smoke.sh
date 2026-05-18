#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

"$ROOT_DIR/scripts/bootstrap_uv.sh" >/dev/null
export PATH="${HOME}/.local/bin:${PATH}"

OUTPUT_ROOT="${1:-/tmp/profusion-path-c-smoke}"
WORKFLOW_SLUG="support-triage-human-review"

rm -rf "$OUTPUT_ROOT"
mkdir -p "$OUTPUT_ROOT"

uv run profusion m8 demo "$WORKFLOW_SLUG" --output-dir "$OUTPUT_ROOT"

RECEIPT_HTML="$(find "$OUTPUT_ROOT" -type f -name workflow_receipt.html -print -quit)"
if [[ -z "$RECEIPT_HTML" ]]; then
  echo "Path C smoke failed: workflow_receipt.html was not generated." >&2
  exit 1
fi

PACKET_DIR="$(dirname "$RECEIPT_HTML")"
required_files=(
  artifact_manifest.json
  m8_observation.json
  workflow_receipt.json
  workflow_receipt.md
  workflow_receipt.html
)

for file in "${required_files[@]}"; do
  if [[ ! -s "$PACKET_DIR/$file" ]]; then
    echo "Path C smoke failed: missing or empty $PACKET_DIR/$file" >&2
    exit 1
  fi
done

if [[ ! -d "$PACKET_DIR/artifacts" ]]; then
  echo "Path C smoke failed: missing artifacts directory in $PACKET_DIR" >&2
  exit 1
fi

uv run pytest tests/test_m8_gtm_receipt_harness.py -q

echo "Path C smoke passed: $PACKET_DIR"
