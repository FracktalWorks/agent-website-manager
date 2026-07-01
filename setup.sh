#!/bin/bash
echo "Setting up: agent-website-manager"
python3 -m venv .venv 2>/dev/null || python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
[ ! -f ".env" ] && [ -f ".env.example" ] && cp .env.example .env \
    && echo "Created .env from .env.example — EDIT WITH YOUR API KEYS!"
echo "SETUP COMPLETE!"
