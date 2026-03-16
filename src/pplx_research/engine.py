"""
Research Engine - Core research orchestration logic.

Supports three modes:
- quick: Single query, fast response
- deep: Iterative gap analysis, comprehensive report
- synthesis: Multi-perspective analysis across source types
"""

import re
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from pplx_research.sdk import PerplexitySDK, SearchMode, ReasoningEffort

console = Console()


class ResearchEngine:
    """
    Versatile research engine supporting multiple modes, outputs, and integrations.
    """
    
    SOURCE_PREFIXES = {
        "academic": "site:arxiv.org OR site:scholar.google.com OR site:semanticscholar.org OR site:dl.acm.org OR site:ieeexplore.ieee.org",
        "news": "site:news.google.com OR site:reuters.com OR site:apnews.com OR site:bbc.com OR site:techcrunch.com",
        "docs": "site:docs. OR site:documentation. OR site:readthedocs.io OR site:wiki",
        "forums": "site:reddit.com OR site:stackoverflow.com OR site:discourse.org OR site:news.ycombinator.com",
        "code": "site:github.com OR site:gitlab.com OR site:bitbucket.org OR site:pypi.org",
        "all": "",
    }
    
    TIME_RANGE_MAP = {
        "hour": "hour",
        "day": "day",
        "week": "week",
        "month": "month",
        "year": "year",
    }
    
    def __init__(self, 
                 query: str,
                 mode: str = "quick",
                 output_format: str = "markdown",
                 depth: int = 3,
                 site: Optional[str] = None,
                 exclude: Optional[List[str]] = None,
                 time_range: Optional[str] = None,
                 region: Optional[str] = None,
                 language: Optional[str] = None,
                 sources: Optional[List[str]] = None,
                 output_path: Optional[str] = None,
                 webhook: Optional[str] = None,
                 quiet: bool = False,
                 auto: bool = False,
                 return_images: bool = False,
                 return_related_questions: bool = False,
                 reasoning_effort: Optional[str] = None):
        
        self.query = query
        self.mode = mode
        self.output_format = output_format
        self.depth = max(1, min(5, depth))
        self.site = site
        self.exclude = exclude or []
        self.time_range = time_range
        self.region = region
        self.language = language
        self.sources = sources or ["all"]
        self.output_path = output_path
        self.webhook = webhook
        self.quiet = quiet
        self.auto = auto
        self.return_images = return_images
        self.return_related_questions = return_related_questions
        self.reasoning_effort = reasoning_effort
        
        self.sdk = PerplexitySDK(quiet_mode=quiet)
        self.findings: List[Dict[str, Any]] = []
        self.citations: Dict[str, int] = {}
        self.gaps: List[str] = []
        self.iteration = 0
        self.related_questions: List[str] = []
        
    def _build_search_filters(self) -> Dict[str, Any]:
        """Build search filter parameters for API."""
        filters = {}
        
        if self.site:
            filters["search_domain_filter"] = [self.site]
        
        if self.time_range and self.time_range in self.TIME_RANGE_MAP:
            filters["search_recency_filter"] = self.TIME_RANGE_MAP[self.time_range]
        
        if self.language:
            filters["search_language_filter"] = [self.language]
        
        return filters
    
    def _build_query(self, base_query: str, gap: Optional[str] = None) -> str:
        """Build query with all constraints applied."""
        parts = []
        
        # Source type constraints
        if "all" not in self.sources:
            source_parts = []
            for src in self.sources:
                if src in self.SOURCE_PREFIXES and self.SOURCE_PREFIXES[src]:
                    source_parts.append(self.SOURCE_PREFIXES[src])
            if source_parts:
                combined = " OR ".join(source_parts)
                parts.append(f"({combined})" if len(source_parts) > 1 else source_parts[0])
        
        # Exclude domains
        for exc in self.exclude:
            parts.append(f"-site:{exc}")
        
        # Time range context (for models that don't support filters)
        if self.time_range and self.time_range in ["day", "week", "month", "year"]:
            time_prompts = {
                "day": "in the last 24 hours",
                "week": "in the last week",
                "month": "in the last month",
                "year": "in the last year"
            }
            parts.append(time_prompts[self.time_range])
        
        # Region context
        if self.region:
            parts.append(f"region:{self.region}")
        
        # The actual query
        parts.append(base_query)
        
        # Add gap context if iterative
        if gap:
            parts.append(f"(specifically: {gap})")
        
        return " ".join(parts)
    
    def _parse_citations(self, result: Dict[str, Any]) -> None:
        """Extract and dedupe citations."""
        if "citations" in result:
            for url in result["citations"]:
                if url not in self.citations:
                    self.citations[url] = len(self.citations) + 1
    
    def _parse_related_questions(self, result: Dict[str, Any]) -> None:
        """Extract related questions."""
        if "related_questions" in result:
            for q in result["related_questions"]:
                if q not in self.related_questions:
                    self.related_questions.append(q)
    
    def _analyze_gaps(self, content: str) -> List[str]:
        """Identify knowledge gaps from current findings."""
        gap_prompt = f"""Based on this research summary, identify 2-3 specific questions or knowledge gaps that would make the report more comprehensive:

{content}

Output ONLY the questions, one per line, no numbering or bullets."""
        
        result = self.sdk.chat(gap_prompt, model="sonar-reasoning")
        if "error" not in result:
            gaps_text = result["choices"][0]["message"]["content"]
            self._parse_citations(result)
            return [g.strip().lstrip("- •").strip() for g in gaps_text.split("\n") if g.strip()]
        return []
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """Analyze query and recommend optimal settings."""
        classify_prompt = f"""Analyze this research query and classify it. Output ONLY a JSON object.

Query: "{query}"

Output format (JSON only, no markdown):
{{"mode": "quick or deep or synthesis", "depth": 1-5, "sources": ["one or more: academic,news,docs,forums,code,all"], "time_range": null or "day" or "week" or "month" or "year", "reasoning": "brief explanation"}}

Rules:
- quick: simple factual questions, definitions, current events
- deep: complex topics, how/why questions, research gaps  
- synthesis: comparisons, debates, pros/cons, "vs" queries
- time_range: only if query mentions "latest", "recent", "new", current events
- sources: match intent (paper→academic, bug→forums, tutorial→docs)

JSON object only:"""
        
        result = self.sdk.chat(classify_prompt, model="sonar")
        
        if "error" in result:
            return self._default_classification()
        
        try:
            content = result["choices"][0]["message"]["content"]
            # Extract JSON from response (handle markdown code blocks)
            code_block = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
            if code_block:
                content = code_block.group(1)
            json_match = re.search(r'\{[\s\S]*?\}', content)
            if json_match:
                parsed = json.loads(json_match.group())
                if isinstance(parsed.get("sources"), str):
                    parsed["sources"] = [s.strip() for s in parsed["sources"].split(",")]
                return parsed
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass
        
        return self._default_classification()
    
    def _default_classification(self) -> Dict[str, Any]:
        """Fallback classification."""
        return {
            "mode": "quick",
            "depth": 3,
            "sources": ["all"],
            "time_range": None,
            "reasoning": "default fallback"
        }
    
    def _quick_mode(self) -> Dict[str, Any]:
        """Single query, fast response."""
        query = self._build_query(self.query)
        model = "sonar-pro" if "academic" in self.sources else "sonar"
        
        if not self.quiet:
            console.print(f"[dim]Quick search: {query[:80]}...[/dim]")
        
        # Build API params
        params = self._build_search_filters()
        if self.return_images:
            params["return_images"] = True
        if self.return_related_questions:
            params["return_related_questions"] = True
        
        result = self.sdk.chat(query, model=model, **params)
        
        if "error" in result:
            return {"error": result["error"]}
        
        self._parse_citations(result)
        self._parse_related_questions(result)
        content = result["choices"][0]["message"]["content"]
        
        return {
            "content": content,
            "citations": list(self.citations.keys()),
            "related_questions": self.related_questions,
            "iterations": 1,
            "mode": "quick",
            "usage": result.get("usage", {}),
        }
    
    def _deep_mode(self) -> Dict[str, Any]:
        """Iterative gap analysis."""
        all_content = []
        self.gaps = [self.query]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
            disable=self.quiet
        ) as progress:
            task = progress.add_task("[cyan]Deep research...", total=self.depth)
            
            for i in range(self.depth):
                self.iteration = i + 1
                gap = self.gaps[i] if i < len(self.gaps) else self.gaps[-1]
                query = self._build_query(gap if i > 0 else self.query)
                
                progress.update(task, description=f"[cyan]Iteration {i+1}/{self.depth}[/cyan]")
                
                params = self._build_search_filters()
                if self.reasoning_effort:
                    params["reasoning_effort"] = self.reasoning_effort
                
                result = self.sdk.chat(query, model="sonar-reasoning", **params)
                
                if "error" in result:
                    console.print(f"[red]Error in iteration {i+1}: {result['error']}[/red]")
                    continue
                
                content = result["choices"][0]["message"]["content"]
                self._parse_citations(result)
                all_content.append({
                    "iteration": i + 1,
                    "query": gap,
                    "content": content
                })
                
                if i < self.depth - 1:
                    new_gaps = self._analyze_gaps(content)
                    self.gaps.extend(g for g in new_gaps if g not in self.gaps)
                
                progress.advance(task)
        
        synthesis = self._synthesize(all_content)
        
        return {
            "content": synthesis,
            "citations": list(self.citations.keys()),
            "iterations": self.iteration,
            "gaps_explored": self.gaps,
            "mode": "deep"
        }
    
    def _synthesis_mode(self) -> Dict[str, Any]:
        """Multi-perspective analysis across source types."""
        perspectives = []
        source_types = self.sources if "all" not in self.sources else ["academic", "news", "docs", "forums", "code"]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
            disable=self.quiet
        ) as progress:
            task = progress.add_task("[magenta]Synthesizing perspectives...", total=len(source_types))
            
            for src_type in source_types:
                if src_type not in self.SOURCE_PREFIXES:
                    continue
                    
                query = self._build_query(self.query)
                src_prefix = self.SOURCE_PREFIXES[src_type]
                if src_prefix:
                    query = f"{src_prefix} {query}"
                
                progress.update(task, description=f"[magenta]Analyzing {src_type} sources...[/magenta]")
                
                result = self.sdk.chat(query, model="sonar-reasoning")
                
                if "error" in result:
                    if not self.quiet:
                        console.print(f"[red]Error for {src_type}: {result.get('error', 'unknown')}[/red]")
                    progress.advance(task)
                    continue
                    
                content = result["choices"][0]["message"]["content"]
                self._parse_citations(result)
                perspectives.append({
                    "source_type": src_type,
                    "content": content
                })
                
                progress.advance(task)
        
        final = self._synthesize_perspectives(perspectives)
        
        return {
            "content": final,
            "citations": list(self.citations.keys()),
            "perspectives": perspectives,
            "iterations": len(perspectives),
            "mode": "synthesis"
        }
    
    def _synthesize(self, all_content: List[Dict]) -> str:
        """Synthesize iterations into coherent report."""
        if len(all_content) == 1:
            return all_content[0]["content"]
        
        synthesis_prompt = f"""Synthesize these research iterations into a single, comprehensive report. Remove redundancy, organize by topic, and maintain all factual claims:

{chr(10).join(f"--- ITERATION {c['iteration']}: {c['query']} ---{chr(10)}{c['content']}" for c in all_content)}

Output a well-structured markdown report."""
        
        result = self.sdk.chat(synthesis_prompt, model="sonar-pro")
        if "error" not in result:
            self._parse_citations(result)
            return result["choices"][0]["message"]["content"]
        
        return "\n\n---\n\n".join(c["content"] for c in all_content)
    
    def _synthesize_perspectives(self, perspectives: List[Dict]) -> str:
        """Synthesize multiple source perspectives."""
        if not perspectives:
            return "No perspectives gathered."
        
        if len(perspectives) == 1:
            return perspectives[0]["content"]
        
        synth_prompt = f"""Synthesize these perspectives from different source types into a unified report. Highlight agreements and contradictions:

{chr(10).join(f"--- {p['source_type'].upper()} PERSPECTIVE ---{chr(10)}{p['content']}" for p in perspectives)}

Output a comprehensive markdown report organized by key themes."""
        
        result = self.sdk.chat(synth_prompt, model="sonar-pro")
        if "error" not in result:
            self._parse_citations(result)
            return result["choices"][0]["message"]["content"]
        
        return "\n\n---\n\n".join(f"## {p['source_type'].title()}\n\n{p['content']}" for p in perspectives)
    
    def _format_output(self, result: Dict[str, Any]) -> str:
        """Format result according to output_format."""
        content = result.get("content", "")
        citations = result.get("citations", [])
        
        if self.output_format == "json":
            clean_result = result.copy()
            if "content" in clean_result:
                clean_result["content"] = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', clean_result["content"])
            return json.dumps(clean_result, indent=2, ensure_ascii=False)
        
        elif self.output_format == "summary":
            lines = content.split("\n")
            summary_lines = []
            for line in lines[:20]:
                if line.strip():
                    summary_lines.append(line)
                    if len(summary_lines) >= 5:
                        break
            return "\n".join(summary_lines)
        
        elif self.output_format == "plain":
            plain = re.sub(r'[#*`_\[\]]', '', content)
            return plain
        
        else:  # markdown
            if citations:
                content += "\n\n## Sources\n\n"
                for i, url in enumerate(citations, 1):
                    content += f"{i}. [{url}]({url})\n"
            
            if self.related_questions:
                content += "\n\n## Related Questions\n\n"
                for q in self.related_questions[:5]:
                    content += f"- {q}\n"
            
            content += f"\n\n---\n\n"
            content += f"*Research mode: {result.get('mode', 'unknown')} | "
            content += f"Iterations: {result.get('iterations', 1)} | "
            content += f"Sources: {len(citations)}*\n"
            
            return content
    
    def _save_output(self, output: str) -> None:
        """Save output to file."""
        if self.output_path:
            path = Path(self.output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output)
            if not self.quiet:
                console.print(f"[green]Saved to: {path}[/green]")
    
    def _send_webhook(self, result: Dict[str, Any]) -> None:
        """POST results to webhook."""
        if self.webhook:
            try:
                resp = requests.post(self.webhook, json=result, timeout=10)
                if not self.quiet:
                    console.print(f"[green]Webhook sent: {resp.status_code}[/green]")
            except Exception as e:
                if not self.quiet:
                    console.print(f"[red]Webhook failed: {e}[/red]")
    
    def run(self) -> str:
        """Execute research and return formatted output."""
        
        if self.auto:
            if not self.quiet:
                console.print("[dim]Analyzing query for optimal settings...[/dim]")
            
            classification = self.classify_query(self.query)
            
            self.mode = classification.get("mode", self.mode)
            self.depth = classification.get("depth", self.depth)
            if classification.get("time_range"):
                self.time_range = classification["time_range"]
            if classification.get("sources") and "all" not in classification["sources"]:
                self.sources = classification["sources"]
            
            if not self.quiet:
                console.print(f"[green]Auto-detected: {self.mode} mode, depth {self.depth}, sources: {','.join(self.sources)}[/green]")
                if classification.get("reasoning"):
                    console.print(f"[dim]Reasoning: {classification['reasoning']}[/dim]")
        
        if not self.quiet:
            console.print(Panel.fit(
                f"[bold cyan]PPLX Research[/bold cyan]\n"
                f"Query: {self.query[:60]}{'...' if len(self.query) > 60 else ''}\n"
                f"Mode: {self.mode} | Depth: {self.depth} | Format: {self.output_format}",
                title="🔬 Research"
            ))
        
        if self.mode == "quick":
            result = self._quick_mode()
        elif self.mode == "synthesis":
            result = self._synthesis_mode()
        else:
            result = self._deep_mode()
        
        if "error" in result:
            if not self.quiet:
                console.print(f"[red]Research failed: {result['error']}[/red]")
            return f"Error: {result['error']}"
        
        output = self._format_output(result)
        self._save_output(output)
        self._send_webhook(result)
        
        return output
