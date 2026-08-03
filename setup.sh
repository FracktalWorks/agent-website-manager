#!/bin/bash
# agent-website-manager — first-run setup. Safe to run on every folder open.
# Parity with setup.ps1; see that file for why this is fingerprinted and why
# pip's exit code is checked rather than assumed.
set -u

echo "agent-website-manager — environment"

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo "ERROR: Python not found on PATH" >&2
    exit 1
fi
PY=$(command -v python3 || command -v python)

if [ ! -d .venv ]; then
    echo "  creating .venv ..."
    "$PY" -m venv .venv || { echo "ERROR: could not create .venv" >&2; exit 1; }
fi
# shellcheck disable=SC1091
. .venv/bin/activate

# The marker lives inside .venv, so deleting the venv forces a reinstall.
HASH=$(sha256sum requirements.txt 2>/dev/null | cut -d' ' -f1 \
       || shasum -a 256 requirements.txt | cut -d' ' -f1)
MARKER=".venv/.deps-$HASH"

if [ -f "$MARKER" ]; then
    echo "  dependencies up to date"
else
    echo "  installing dependencies (first run for this requirements.txt)"
    pip install --upgrade pip --quiet
    if ! pip install -r requirements.txt; then
        echo "ERROR: pip failed - the environment is INCOMPLETE" >&2
        exit 1
    fi
    rm -f .venv/.deps-* 2>/dev/null || true
    touch "$MARKER"
    echo "  dependencies installed"
fi

if python -c "import requests, PIL, segno, bs4, dotenv" 2>/dev/null; then
    echo "  core imports ok"
else
    echo "  WARNING: a core module will not import" >&2
    python -c "import requests, PIL, segno, bs4, dotenv" || true
fi

if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
    echo "  created .env from .env.example - ADD YOUR KEYS"
fi

echo "  optional ML extras (2.5GB, media auto-tagging only):"
echo "    pip install -r requirements-ml.txt"
