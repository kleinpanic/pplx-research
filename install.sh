#!/bin/bash
# Install pplx-research CLI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing pplx-research..."

# Create venv if needed
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Install package
"$SCRIPT_DIR/venv/bin/pip" install -e "$SCRIPT_DIR[dev]"

# Create CLI wrapper
mkdir -p ~/.local/bin
cat > ~/.local/bin/pplx-research << 'WRAPPER'
#!/bin/bash
exec /home/broklein/codeWS/Python/PerplexityDeepResearch/venv/bin/pplx-research "$@"
WRAPPER
chmod +x ~/.local/bin/pplx-research

echo "✓ Installed pplx-research to ~/.local/bin/"
echo "  Run: pplx-research --help"
