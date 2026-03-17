#!/usr/bin/env bash
# quick-lookup.sh — simple fact lookups with pplx-research
#
# Demonstrates: --auto flag, --format options, piping to file, capturing in a variable

set -euo pipefail

# --- Example 1: Minimal quick lookup (default mode, markdown output) ---
echo "=== Example 1: Basic quick lookup ==="
pplx-research "what is the CAP theorem in distributed systems" --quiet

# --- Example 2: Auto-mode (let the tool pick mode/depth/sources) ---
echo ""
echo "=== Example 2: Auto-mode ==="
pplx-research "current stable version of Python" --auto --quiet

# --- Example 3: Summary format — one paragraph, great for piping ---
echo ""
echo "=== Example 3: Summary format ==="
pplx-research "what is QUIC protocol" --mode quick --format summary --quiet

# --- Example 4: Pipe to a file ---
echo ""
echo "=== Example 4: Save to file ==="
pplx-research "HTTP/3 vs HTTP/2 differences" --quiet --output /tmp/http3-lookup.md
echo "Result saved to /tmp/http3-lookup.md"
cat /tmp/http3-lookup.md

# --- Example 5: Capture in a variable and process ---
echo ""
echo "=== Example 5: Capture in variable ==="
result=$(pplx-research "what is WebAssembly" --format summary --quiet)
echo "Captured result (first 100 chars):"
echo "${result:0:100}..."

# --- Example 6: Restrict to a specific site ---
echo ""
echo "=== Example 6: Site-restricted lookup ==="
pplx-research "asyncio event loop" --mode quick --site docs.python.org --quiet
