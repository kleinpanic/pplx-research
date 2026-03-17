# API Reference

## Environment Variables

### PERPLEXITY_API_KEY (required)

Your Perplexity API key. Get one at https://www.perplexity.ai/settings/api

```bash
export PERPLEXITY_API_KEY="pplx-..."
```

The tool also loads this from `~/.env` automatically via `python-dotenv`, so you can
store it there instead of exporting it every session:

```
# ~/.env
PERPLEXITY_API_KEY=pplx-...
```

If the key is absent from both the environment and `~/.env`, `pplx-research` exits with
a non-zero code and an error message on stderr.

---

## Models

`pplx-research` selects the model automatically based on mode. You cannot override this
directly via CLI flags — the selection is intentional to match cost and capability to need.

### sonar

- **Used for:** `quick` mode
- **Characteristics:** Fast, cost-efficient, good for single-question factual lookups
- **Underlying model:** `sonar` (Perplexity's base web-search model)
- **Latency:** ~1–3 seconds per call
- **Best when:** You need a fast answer and don't require deep reasoning

### sonar-pro

- **Used for:** `deep` mode with `--sources academic`
- **Characteristics:** Premium tier, stronger reasoning, higher context window
- **Underlying model:** `sonar-pro`
- **Latency:** ~3–8 seconds per call
- **Best when:** Academic or technical research requiring nuanced synthesis

### sonar-reasoning

- **Used for:** `deep` mode (default) and `synthesis` mode
- **Characteristics:** Chain-of-thought reasoning, iterative gap-filling, highest quality
- **Underlying model:** `sonar-reasoning`
- **Latency:** ~5–15 seconds per call
- **Best when:** Complex multi-part research, cross-perspective synthesis

The `--reasoning-effort` flag controls how much thinking the model does per iteration:

| Value | Tokens used | Use when |
|-------|-------------|----------|
| `minimal` | Fewest | Speed priority |
| `low` | Low | Faster deep runs |
| `medium` | Moderate | Default balance |
| `high` | Most | Maximum quality |

---

## Source Types

The `--sources` flag maps to Perplexity's internal search filter configuration:

| Value | What it queries | Examples |
|-------|----------------|---------|
| `academic` | Academic databases and preprint servers | arXiv, Google Scholar, ACM Digital Library, IEEE Xplore, PubMed, Semantic Scholar |
| `news` | News outlets and tech media | Reuters, BBC, TechCrunch, Ars Technica, The Verge, Hacker News |
| `docs` | Official documentation and reference sites | MDN Web Docs, ReadTheDocs, official language/framework docs |
| `forums` | Community discussion platforms | Reddit, Stack Overflow, Hacker News, Discord (public), dev.to |
| `code` | Code hosting and code search | GitHub, GitLab, Sourcegraph |
| `all` | All of the above | (default) |

Combine with commas: `--sources academic,news` restricts to only academic and news sources.

---

## Rate Limits

Rate limits depend on your Perplexity API plan tier and are not enforced by `pplx-research`
itself. Check your current limits at https://www.perplexity.ai/settings/api

General guidance:
- **Free tier:** Very limited, suitable for testing only
- **Pro tier:** Moderate limits, suitable for regular development use
- **Business tier:** Higher limits, suitable for production agent workloads

`pplx-research` makes one API call per iteration per source type in deep/synthesis mode.
A `--depth 5 --sources academic,news` synthesis run will make approximately 10 API calls.
Budget accordingly against your plan's per-minute and per-day limits.

---

## CLI Flags Quick Reference

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--mode` | `-m` | `quick\|deep\|synthesis` | `quick` | Research strategy |
| `--format` | `-f` | `markdown\|json\|summary\|plain` | `markdown` | Output format |
| `--auto` | `-a` | flag | off | Auto-classify query |
| `--depth` | `-d` | int 1–5 | `3` | Iterations for deep/synthesis |
| `--sources` | — | csv | `all` | Source type filter |
| `--site` | `-s` | domain | — | Restrict to one domain |
| `--exclude` | `-e` | domain | — | Exclude domain (repeatable) |
| `--time-range` | `-t` | `hour\|day\|week\|month\|year` | — | Recency filter |
| `--region` | `-r` | ISO country | — | e.g. `US`, `JP` |
| `--language` | `-l` | ISO 639-1 | — | e.g. `en`, `de` |
| `--reasoning-effort` | — | `minimal\|low\|medium\|high` | — | sonar-reasoning effort |
| `--return-images` | — | flag | off | Include image URLs |
| `--return-related-questions` | — | flag | off | Include follow-up questions |
| `--output` | `-o` | path | — | Also write to file |
| `--webhook` | `-w` | URL | — | POST result to URL when done |
| `--quiet` | `-q` | flag | off | Suppress progress output |
