# pplx-research Skill

The `pplx-research` skill wraps the `pplx-research` CLI as an OpenClaw/Claude skill, giving any
MCP-capable agent one-command access to Perplexity Sonar web research — facts, deep reports, and
multi-perspective synthesis — without writing a single line of Python.

## Prerequisites

```bash
pip install pplx-research
export PERPLEXITY_API_KEY="pplx-..."   # get one at https://www.perplexity.ai/settings/api
```

The key can also live in `~/.env` (loaded automatically via python-dotenv).

## Install

### Option A — OpenClaw skill

```bash
bash skills/pplx-research/scripts/install.sh
```

This copies `SKILL.md` into `~/.openclaw/skills/pplx-research/` so OpenClaw picks it up
automatically the next time it starts.

### Option B — MCP server (Claude Desktop / Claude Code / Cursor / Windsurf)

```bash
bash mcp/install.sh
```

This registers the FastMCP server in your Claude Desktop config. See `mcp/README.md` for
configuration details for other MCP clients.

## Quick Test

```bash
bash skills/pplx-research/scripts/verify.sh
```

Checks that `pplx-research` is in PATH, `PERPLEXITY_API_KEY` is set, and a live test call
succeeds. Exits 0 on success, 1 on any failure.

## Reference

| Doc | What it covers |
|-----|----------------|
| `references/modes.md` | When to use quick / deep / synthesis / --auto, with a decision tree |
| `references/output-formats.md` | Concrete example output for every `--format` value |
| `references/api-reference.md` | Models, env vars, source types, rate limits |

## Examples

| Script | What it shows |
|--------|---------------|
| `examples/quick-lookup.sh` | Simple fact lookup with `--auto`, piping to file |
| `examples/deep-research.sh` | Deep mode with `--depth 5 --sources academic --output` |
| `examples/synthesis-compare.sh` | Synthesis mode comparison with `--format json` |
| `examples/agent-workflow.sh` | How an agent calls it and parses JSON in a loop |
