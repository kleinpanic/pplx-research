#!/usr/bin/env bash
# install.sh — register the pplx-research MCP server in Claude Desktop config

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_PATH="$SCRIPT_DIR/server.py"

# --- Detect OS and locate claude_desktop_config.json ---
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "linux"* ]]; then
    CONFIG_DIR="$HOME/.config/claude"
else
    echo "Unsupported OS: $OSTYPE" >&2
    echo "Manually add the following to your Claude Desktop config:" >&2
    echo ""
    echo '  "mcpServers": {'
    echo '    "pplx-research": {'
    echo "      \"command\": \"python\","
    echo "      \"args\": [\"$SERVER_PATH\"],"
    echo '      "env": {"PERPLEXITY_API_KEY": "pplx-..."}'
    echo '    }'
    echo '  }'
    exit 1
fi

CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

# --- Check python3 is available ---
if ! command -v python3 &>/dev/null; then
    echo "python3 not found — cannot update config automatically" >&2
    echo "Manually add to $CONFIG_FILE:" >&2
    echo ""
    echo '  "mcpServers": {'
    echo '    "pplx-research": {'
    echo "      \"command\": \"python\","
    echo "      \"args\": [\"$SERVER_PATH\"],"
    echo '      "env": {"PERPLEXITY_API_KEY": "pplx-..."}'
    echo '    }'
    echo '  }'
    exit 1
fi

# --- Create or update the config ---
mkdir -p "$CONFIG_DIR"

python3 - <<PYEOF
import json, os, sys

config_file = "$CONFIG_FILE"
server_path = "$SERVER_PATH"

# Load existing config or start fresh
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            print(f"WARNING: {config_file} contains invalid JSON — creating backup and overwriting", file=sys.stderr)
            import shutil
            shutil.copy(config_file, config_file + ".bak")
            config = {}
else:
    config = {}

# Add/update the pplx-research server entry
if "mcpServers" not in config:
    config["mcpServers"] = {}

config["mcpServers"]["pplx-research"] = {
    "command": "python",
    "args": [server_path],
    "env": {
        "PERPLEXITY_API_KEY": os.environ.get("PERPLEXITY_API_KEY", "pplx-YOUR_KEY_HERE")
    }
}

with open(config_file, "w") as f:
    json.dump(config, f, indent=2)
    f.write("\n")

print(f"Config written to {config_file}")
PYEOF

echo "✓ MCP server registered in Claude Desktop config"
echo ""
echo "Next steps:"
echo "  1. Set PERPLEXITY_API_KEY in the env section of $CONFIG_FILE"
echo "     (or re-run with PERPLEXITY_API_KEY exported to auto-fill it)"
echo "  2. Restart Claude Desktop"
