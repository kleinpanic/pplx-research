"""pplx-research MCP server — wraps pplx-research CLI as MCP tools."""

import subprocess
from fastmcp import FastMCP

mcp = FastMCP("pplx-research")


def _run(args: list[str]) -> str:
    """Run pplx-research with the given args; return stdout or raise on failure."""
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"pplx-research exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout


@mcp.tool()
def research_quick(
    query: str,
    format: str = "markdown",
    site: str = "",
    time_range: str = "",
) -> str:
    """Fast single-query research using Perplexity Sonar.

    Best for: facts, definitions, current events, single-question lookups.
    Returns results in ~1-3 seconds. Use research_deep or research_synthesis
    for complex, multi-part, or comparative topics.
    """
    args = ["pplx-research", query, "--quiet", "--mode", "quick", "--format", format]
    if site:
        args += ["--site", site]
    if time_range:
        args += ["--time-range", time_range]
    return _run(args)


@mcp.tool()
def research_deep(
    query: str,
    depth: int = 3,
    sources: str = "all",
    format: str = "markdown",
    reasoning_effort: str = "",
) -> str:
    """Deep iterative research with gap analysis using Perplexity Sonar-Reasoning.

    Best for: complex topics, multi-part questions, research reports, technical deep-dives.
    Runs multiple iterations to identify and fill knowledge gaps.
    depth: 1-5 iterations (higher = more thorough, more API calls).
    sources: comma-separated from academic,news,docs,forums,code,all.
    reasoning_effort: minimal, low, medium, or high (empty = model default).
    """
    args = [
        "pplx-research", query, "--quiet",
        "--mode", "deep",
        "--format", format,
        "--depth", str(depth),
    ]
    if sources and sources != "all":
        args += ["--sources", sources]
    if reasoning_effort:
        args += ["--reasoning-effort", reasoning_effort]
    return _run(args)


@mcp.tool()
def research_synthesis(
    query: str,
    sources: str = "all",
    format: str = "markdown",
) -> str:
    """Multi-perspective synthesis across source types using Perplexity Sonar-Reasoning.

    Best for: comparisons ("X vs Y"), debates, pros/cons, topics where academic,
    community, and industry perspectives meaningfully differ.
    sources: comma-separated from academic,news,docs,forums,code,all.
    Note: synthesis makes multiple parallel API calls — can be slow for broad source sets.
    """
    args = [
        "pplx-research", query, "--quiet",
        "--mode", "synthesis",
        "--format", format,
    ]
    if sources and sources != "all":
        args += ["--sources", sources]
    return _run(args)


@mcp.tool()
def research_auto(
    query: str,
    format: str = "markdown",
) -> str:
    """Auto-classified research: let pplx-research choose the best mode, depth, and sources.

    Best for: general research tasks when you are unsure which mode fits.
    The tool runs a fast classifier first, then routes to quick, deep, or synthesis
    with automatically chosen parameters.
    """
    args = ["pplx-research", query, "--quiet", "--auto", "--format", format]
    return _run(args)


if __name__ == "__main__":
    mcp.run()
