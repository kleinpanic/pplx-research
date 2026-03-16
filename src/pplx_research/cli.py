#!/usr/bin/env python3
"""
PPLX Research CLI - Monolithic, versatile research tool powered by Perplexity.

Modes:
  quick      - Single query, fast response
  deep       - Iterative gap analysis, comprehensive report
  synthesis  - Multi-perspective analysis across source types

Usage:
  pplx-research <query> [options]
  pplx-research "quantum computing" --mode deep --sources academic --format markdown
  pplx-research "React vs Vue" --auto
"""

import argparse
import sys

from rich.console import Console

from pplx_research.engine import ResearchEngine
from pplx_research.sdk import PerplexitySDK

console = Console()


def main():
    parser = argparse.ArgumentParser(
        prog="pplx-research",
        description="Monolithic, versatile research CLI powered by Perplexity Sonar API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "quantum computing breakthroughs" --mode deep --sources academic
  %(prog)s "Python asyncio patterns" --mode quick --format summary
  %(prog)s "microservices best practices" --mode synthesis --depth 4
  %(prog)s "local hiking trails" --site alltrails.com --region US
  %(prog)s "compare React vs Vue performance" --auto
  %(prog)s "latest news about Apple" --auto --quiet

Modes:
  quick      Fast single-query lookup (default)
  deep       Iterative gap analysis for comprehensive reports
  synthesis  Multi-perspective analysis across different source types

For more info: https://github.com/kleinpanic/pplx-research
        """
    )
    
    parser.add_argument("query", help="Research topic or question")
    
    # Mode
    parser.add_argument("--mode", "-m", 
                       choices=["quick", "deep", "synthesis"],
                       default="quick",
                       help="Research mode (default: quick)")
    
    # Output format
    parser.add_argument("--format", "-f",
                       choices=["markdown", "json", "summary", "plain"],
                       default="markdown",
                       help="Output format (default: markdown)")
    
    # Scope
    parser.add_argument("--site", "-s",
                       help="Constrain search to specific domain")
    parser.add_argument("--exclude", "-e",
                       action="append",
                       help="Exclude domain(s) from results (can use multiple times)")
    parser.add_argument("--time-range", "-t",
                       choices=["hour", "day", "week", "month", "year"],
                       help="Time range for results")
    parser.add_argument("--region", "-r",
                       help="Country/region code (e.g., US, UK, JP)")
    parser.add_argument("--language", "-l",
                       help="Language filter (ISO 639-1 code, e.g., en, de, ja)")
    
    # Depth
    parser.add_argument("--depth", "-d",
                       type=int,
                       default=3,
                       help="Iteration depth for deep/synthesis modes (1-5, default: 3)")
    
    # Source types
    parser.add_argument("--sources",
                       default="all",
                       help="Comma-separated: academic,news,docs,forums,code,all (default: all)")
    
    # Reasoning
    parser.add_argument("--reasoning-effort",
                       choices=["minimal", "low", "medium", "high"],
                       help="Reasoning effort level (sonar-reasoning only)")
    
    # Output options
    parser.add_argument("--return-images",
                       action="store_true",
                       help="Include image results in response")
    parser.add_argument("--return-related-questions",
                       action="store_true",
                       help="Include related follow-up questions")
    
    # Integration
    parser.add_argument("--output", "-o",
                       help="Save output to file")
    parser.add_argument("--webhook", "-w",
                       help="POST results to webhook URL on completion")
    parser.add_argument("--quiet", "-q",
                       action="store_true",
                       help="Suppress progress output (for piping)")
    parser.add_argument("--auto", "-a",
                       action="store_true",
                       help="Auto-classify query and select optimal mode/depth/sources")
    
    args = parser.parse_args()
    
    # Parse sources
    sources = [s.strip().lower() for s in args.sources.split(",")]
    
    # Run research
    engine = ResearchEngine(
        query=args.query,
        mode=args.mode,
        output_format=args.format,
        depth=args.depth,
        site=args.site,
        exclude=args.exclude,
        time_range=args.time_range,
        region=args.region,
        language=args.language,
        sources=sources,
        output_path=args.output,
        webhook=args.webhook,
        quiet=args.quiet,
        auto=args.auto,
        return_images=args.return_images,
        return_related_questions=args.return_related_questions,
        reasoning_effort=args.reasoning_effort,
    )
    
    output = engine.run()
    
    # Print output
    if args.quiet:
        print(output)
    else:
        console.print(output)


if __name__ == "__main__":
    main()
