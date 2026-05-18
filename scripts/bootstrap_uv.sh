#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  uv --version
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to install uv." >&2
  exit 1
fi

python3 -m pip install --user uv
export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv was installed, but ${HOME}/.local/bin is not on PATH." >&2
  echo "Add this to PATH, then rerun: export PATH=\"${HOME}/.local/bin:\$PATH\"" >&2
  exit 1
fi

uv --version
