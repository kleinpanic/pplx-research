#!/usr/bin/env bash
# install-skill.sh — meta-installer for pplx-research integrations

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SKILL_INSTALLER="$REPO_ROOT/skills/pplx-research/scripts/install.sh"
MCP_INSTALLER="$REPO_ROOT/mcp/install.sh"

usage() {
    cat <<EOF
pplx-research integration installer

Options:
  --skill    Install OpenClaw skill (default)
  --mcp      Register MCP server in Claude Desktop
  --all      Install both

Usage: bash scripts/install-skill.sh [--skill|--mcp|--all]
EOF
}

install_skill() {
    bash "$SKILL_INSTALLER"
}

install_mcp() {
    bash "$MCP_INSTALLER"
}

# Default: --skill
if [[ $# -eq 0 ]]; then
    install_skill
    exit 0
fi

case "$1" in
    --skill)
        install_skill
        ;;
    --mcp)
        install_mcp
        ;;
    --all)
        install_skill
        install_mcp
        ;;
    --help|-h)
        usage
        ;;
    *)
        echo "Unknown option: $1" >&2
        echo "" >&2
        usage >&2
        exit 1
        ;;
esac
