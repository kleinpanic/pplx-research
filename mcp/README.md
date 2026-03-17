# pplx-research MCP Server

Exposes `pplx-research` as four MCP tools so any MCP-capable client (Claude Desktop,
Claude Code, Cursor, Windsurf, etc.) can call it directly.

## Tools

| Tool | Best for |
|------|----------|
| `research_quick` | Facts, definitions, current events — fast, ~1 API call |
| `research_deep` | Complex topics, research reports, multi-part questions |
| `research_synthesis` | Comparisons ("X vs Y"), debates, pros/cons |
| `research_auto` | General research when you are unsure which mode fits |

### research_quick

```
research_quick(query, format="markdown", site="", time_range="")
```

Fast single-query lookup via Perplexity Sonar. Optional `site` restricts to one domain;
`time_range` accepts `hour|day|week|month|year`.

### research_deep

```
research_deep(query, depth=3, sources="all", format="markdown", reasoning_effort="")
```

Iterative gap-filling research. `depth` (1–5) controls iterations; `sources` is a
comma-separated list from `academic,news,docs,forums,code,all`. `reasoning_effort`
accepts `minimal|low|medium|high`.

### research_synthesis

```
research_synthesis(query, sources="all", format="markdown")
```

Multi-perspective synthesis across source types. Good for "X vs Y" comparisons and
topics with differing academic, community, and industry views.

### research_auto

```
research_auto(query, format="markdown")
```

Auto-classifies the query and selects mode/depth/sources automatically.

---

## Setup

### Prerequisites

```bash
pip install pplx-research
export PERPLEXITY_API_KEY="pplx-..."   # https://www.perplexity.ai/settings/api

pip install -r mcp/requirements.txt
```

### Quick test (stdio MCP server)

```bash
python mcp/server.py
```

---

## Client Configuration

### Claude Desktop

Config file locations:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pplx-research": {
      "command": "python",
      "args": ["/absolute/path/to/mcp/server.py"],
      "env": {
        "PERPLEXITY_API_KEY": "pplx-..."
      }
    }
  }
}
```

Run `bash mcp/install.sh` to add this automatically.

### Claude Code / Codex CLI

Add to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "pplx-research": {
      "command": "python",
      "args": ["<absolute-path-to-repo>/mcp/server.py"]
    }
  }
}
```

`PERPLEXITY_API_KEY` must be set in the shell environment where Claude Code runs.

### Cursor

1. Open **Settings → MCP**
2. Click **Add Server**
3. Command: `python`
4. Args: `<absolute-path-to-repo>/mcp/server.py`
5. Add env var `PERPLEXITY_API_KEY`

### Windsurf

1. Open **Settings → Model Context Protocol**
2. Click **Add MCP Server**
3. Command: `python <absolute-path-to-repo>/mcp/server.py`
4. Add `PERPLEXITY_API_KEY` to the environment section

### Any other MCP client

The server speaks stdio MCP. Point your client at:

```
python /path/to/mcp/server.py
```

with `PERPLEXITY_API_KEY` in the environment.

---

## Output Formats

All tools accept `format` parameter:

| Value | Description |
|-------|-------------|
| `markdown` | Headers, bullets, sources section (default) |
| `json` | `{"content": "...", "citations": [...], "iterations": N, "mode": "...", "usage": {...}}` |
| `summary` | Single concise paragraph |
| `plain` | Unformatted text, no markdown symbols |
