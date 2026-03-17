#!/usr/bin/env bash
# install.sh — install the pplx-research OpenClaw skill to ~/.openclaw/skills/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR_SRC="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_DEST="$HOME/.openclaw/skills/pplx-research"

SOURCE="$SKILL_DIR_SRC/SKILL.md"

if [[ ! -f "$SOURCE" ]]; then
    echo "ERROR: SKILL.md not found at $SOURCE" >&2
    exit 1
fi

mkdir -p "$SKILL_DEST"
cp "$SOURCE" "$SKILL_DEST/SKILL.md"

echo "✓ pplx-research skill installed to $SKILL_DEST/SKILL.md"
