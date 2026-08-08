#!/bin/bash
# setup.sh - one-time onboarding: run this once after cloning.
# Installs dependencies and activates the pre-commit safety net (secret
# scanning, lint, commit-message format) so it's on by default, not
# something to remember as a separate step.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Installing dependencies..."
pip install -r "$PROJECT_ROOT/requirements.txt"

echo "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

echo ""
echo "Setup complete. Every 'git commit' now runs secret-scanning, lint, and"
echo "commit-message checks automatically. Run './scripts/run_local.sh' to"
echo "start the app."
