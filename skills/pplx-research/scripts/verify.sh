#!/usr/bin/env bash
# verify.sh — check that pplx-research is correctly installed and working
#
# Exit codes:
#   0 — everything is working
#   1 — something is missing or broken

set -uo pipefail

FAIL=0

# --- Step 1: Check pplx-research is in PATH ---
if ! command -v pplx-research &>/dev/null; then
    echo "✗ pplx-research not found in PATH" >&2
    echo "  Install with: pip install pplx-research" >&2
    FAIL=1
else
    echo "✓ pplx-research found: $(command -v pplx-research)"
fi

# --- Step 2: Check PERPLEXITY_API_KEY is set or in ~/.env ---
KEY_FOUND=0

if [[ -n "${PERPLEXITY_API_KEY:-}" ]]; then
    KEY_FOUND=1
    echo "✓ PERPLEXITY_API_KEY is set in environment"
fi

if [[ $KEY_FOUND -eq 0 && -f "$HOME/.env" ]]; then
    if grep -q "PERPLEXITY_API_KEY" "$HOME/.env" 2>/dev/null; then
        KEY_FOUND=1
        echo "✓ PERPLEXITY_API_KEY found in ~/.env"
    fi
fi

if [[ $KEY_FOUND -eq 0 ]]; then
    echo "✗ PERPLEXITY_API_KEY not set" >&2
    echo "  Set it with: export PERPLEXITY_API_KEY=\"pplx-...\"" >&2
    echo "  Or add it to ~/.env: echo 'PERPLEXITY_API_KEY=pplx-...' >> ~/.env" >&2
    FAIL=1
fi

# --- Step 3: Run a live test call (only if steps 1 and 2 passed) ---
if [[ $FAIL -eq 0 ]]; then
    echo "Running connectivity test..."
    if pplx-research "test connectivity" --quiet --format summary &>/dev/null; then
        echo "✓ Live test call succeeded"
    else
        echo "✗ Live test call failed (check your API key and network)" >&2
        FAIL=1
    fi
fi

# --- Summary ---
echo ""
if [[ $FAIL -eq 0 ]]; then
    echo "✓ pplx-research is set up and working"
    exit 0
else
    echo "✗ One or more checks failed — see errors above" >&2
    exit 1
fi
