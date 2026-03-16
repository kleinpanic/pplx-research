#!/bin/bash
# Install pplx-research CLI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing pplx-research..."

# Create venv if needed
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Install package in development mode
"$SCRIPT_DIR/venv/bin/pip" install -e "$SCRIPT_DIR[dev]"

echo "✓ Installed pplx-research"
echo "  Run: $SCRIPT_DIR/venv/bin/pplx-research --help"
