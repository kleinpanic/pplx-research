# Research Modes

`pplx-research` supports three explicit modes plus an `--auto` classifier.

## Decision Tree

```
Is your query a simple fact or definition?         → quick
Does it involve comparison or "X vs Y"?            → synthesis
Is it complex/multi-part/research-grade?           → deep
Not sure?                                          → --auto
```

## Mode Reference

### quick

Single Perplexity Sonar call. Returns an answer, a summary paragraph, and a source list.
Best for: facts, definitions, "what is X", current events, single-question lookups.
API calls: **1**

```bash
pplx-research "what is the CAP theorem" --quiet
pplx-research "current Python version" --quiet --format summary
pplx-research "FastAPI vs Flask" --mode quick --site docs.python.org --quiet
```

### deep

Iterative gap-filling loop. Each iteration identifies unanswered sub-questions and issues
follow-up queries until the depth limit is reached or gaps are exhausted.
Best for: technical deep-dives, research reports, multi-part topics, anything where one
call would leave important questions unanswered.
API calls: up to `depth × source_types` (default depth 3).

```bash
pplx-research "transformer architecture advances 2024" --mode deep --quiet
pplx-research "Kubernetes networking internals" --mode deep --depth 5 --sources academic --quiet
pplx-research "Rust memory model" --mode deep --depth 2 --output rust-memory.md --quiet
```

**Depth guide:**

| `--depth` | API calls (approx) | Use when |
|-----------|-------------------|----------|
| 1 | ~2 | Fast iteration, rough draft |
| 2 | ~4 | Balanced speed vs coverage |
| 3 | ~6 | Default — good for most topics |
| 4 | ~8 | Thorough coverage |
| 5 | ~10 | Comprehensive final report |

### synthesis

Issues parallel sub-queries across multiple source types (academic, news, forums, docs, code),
then synthesizes a unified multi-perspective answer.
Best for: comparisons, debates, pros/cons, "X vs Y", topics where community, academic, and
industry perspectives differ.
API calls: `sources × depth` (can be many — use `--quiet` and be patient).

```bash
pplx-research "Rust vs Go for systems programming" --mode synthesis --quiet
pplx-research "microservices vs monolith tradeoffs" --mode synthesis --format json --quiet
pplx-research "PostgreSQL vs MySQL 2024" --mode synthesis --sources academic,forums --quiet
```

### --auto

Runs a fast classifier query first, then routes to `quick`, `deep`, or `synthesis` with
automatically chosen depth and sources. Use this when you are unsure which mode fits.

```bash
pplx-research "compare gRPC vs REST" --auto --quiet
pplx-research "what is QUIC" --auto --quiet
```

`--auto` overrides any explicit `--mode`, `--depth`, or `--sources` flags — those are
ignored when `--auto` is set.

## Choosing Sources

The `--sources` flag narrows which source types are queried in deep/synthesis mode:

| Value | What it searches |
|-------|-----------------|
| `academic` | arXiv, Google Scholar, ACM, IEEE, PubMed |
| `news` | Reuters, BBC, TechCrunch, Ars Technica, HN |
| `docs` | Official documentation sites, MDN, ReadTheDocs |
| `forums` | Reddit, Stack Overflow, Hacker News, Discord |
| `code` | GitHub, GitLab, Sourcegraph |
| `all` | All of the above (default) |

Combine with commas: `--sources academic,news`
