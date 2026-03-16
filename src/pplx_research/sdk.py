"""
Perplexity SDK Wrapper with OpenRouter fallback.

Supports all Perplexity Sonar API features including:
- Chat completions with citations
- Search with filters
- Streaming responses
- All advanced parameters (search_domain_filter, reasoning_effort, etc.)
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any, Optional, Union, Generator
from dataclasses import dataclass, field
from enum import Enum

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class SearchMode(str, Enum):
    WEB = "web"
    ACADEMIC = "academic"
    SEC = "sec"


class ReasoningEffort(str, Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StreamMode(str, Enum):
    FULL = "full"
    CONCISE = "concise"


@dataclass
class WebSearchOptions:
    """Options for web search behavior."""
    search_context_size: str = "medium"  # low, medium, high
    use_autoprompt: bool = True
    search_after_date: Optional[str] = None
    search_before_date: Optional[str] = None


@dataclass 
class ChatCompletionRequest:
    """Type-safe chat completion request."""
    model: str
    messages: List[Dict[str, str]]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stream: bool = False
    stream_mode: StreamMode = StreamMode.FULL
    
    # Search controls
    search_mode: Optional[SearchMode] = None
    search_domain_filter: Optional[List[str]] = None
    search_recency_filter: Optional[str] = None  # hour, day, week, month, year
    search_after_date_filter: Optional[str] = None
    search_before_date_filter: Optional[str] = None
    search_language_filter: Optional[List[str]] = None
    
    # Reasoning
    reasoning_effort: Optional[ReasoningEffort] = None
    
    # Output options
    return_images: bool = False
    return_related_questions: bool = False
    enable_search_classifier: bool = True
    disable_search: bool = False
    language_preference: Optional[str] = None
    
    # Response format
    response_format: Optional[Dict[str, Any]] = None
    
    # Web search options object
    web_search_options: Optional[WebSearchOptions] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API payload dict."""
        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": self.stream,
        }
        
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.top_p is not None:
            payload["top_p"] = self.top_p
        if self.stream_mode:
            payload["stream_mode"] = self.stream_mode.value
        if self.search_mode:
            payload["search_mode"] = self.search_mode.value
        if self.search_domain_filter:
            payload["search_domain_filter"] = self.search_domain_filter
        if self.search_recency_filter:
            payload["search_recency_filter"] = self.search_recency_filter
        if self.search_after_date_filter:
            payload["search_after_date_filter"] = self.search_after_date_filter
        if self.search_before_date_filter:
            payload["search_before_date_filter"] = self.search_before_date_filter
        if self.search_language_filter:
            payload["search_language_filter"] = self.search_language_filter
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort.value
        if self.return_images:
            payload["return_images"] = True
        if self.return_related_questions:
            payload["return_related_questions"] = True
        if not self.enable_search_classifier:
            payload["enable_search_classifier"] = False
        if self.disable_search:
            payload["disable_search"] = True
        if self.language_preference:
            payload["language_preference"] = self.language_preference
        if self.response_format:
            payload["response_format"] = self.response_format
        if self.web_search_options:
            payload["web_search_options"] = {
                "search_context_size": self.web_search_options.search_context_size,
                "use_autoprompt": self.web_search_options.use_autoprompt,
            }
            if self.web_search_options.search_after_date:
                payload["web_search_options"]["search_after_date"] = self.web_search_options.search_after_date
            if self.web_search_options.search_before_date:
                payload["web_search_options"]["search_before_date"] = self.web_search_options.search_before_date
        
        return payload


class PerplexitySDK:
    """
    Unified SDK for Perplexity with OpenRouter fallback.
    
    Features:
    - Full Perplexity Sonar API support
    - Automatic quota fallback to OpenRouter
    - Streaming support
    - Type-safe request building
    """
    
    # Model name mapping: canonical -> (perplexity_name, openrouter_name)
    MODELS = {
        "sonar": ("sonar", "perplexity/sonar"),
        "sonar-pro": ("sonar-pro", "perplexity/sonar-pro"),
        "sonar-reasoning": ("sonar-reasoning-pro", "perplexity/sonar-reasoning-pro"),
        "sonar-deep-research": ("sonar-deep-research", "perplexity/sonar-deep-research"),
    }
    
    AVAILABLE_MODELS = list(MODELS.keys())
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 openrouter_key: Optional[str] = None,
                 env_path: Optional[str] = None,
                 quiet_mode: bool = False):
        """
        Initialize SDK.
        
        Args:
            api_key: Perplexity API key (or from PERPLEXITY_API_KEY env)
            openrouter_key: OpenRouter API key (or from OPENROUTER_API_KEY env)
            env_path: Path to .env file to load
            quiet_mode: Suppress fallback messages
        """
        # Load env file if specified
        if env_path and load_dotenv:
            load_dotenv(env_path)
        elif load_dotenv:
            # Try default locations
            for loc in [".env", os.path.expanduser("~/.openclaw/.env")]:
                if os.path.exists(loc):
                    load_dotenv(loc)
                    break
        
        self.pplx_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.or_key = openrouter_key or os.getenv("OPENROUTER_API_KEY")
        self.use_openrouter = False
        self.base_url = "https://api.perplexity.ai"
        self.api_key = self.pplx_key
        self.quiet_mode = quiet_mode
        
    def _resolve_model(self, model: str) -> str:
        """Resolve model name for current API."""
        if model in self.MODELS:
            pplx_name, or_name = self.MODELS[model]
            return or_name if self.use_openrouter else pplx_name
        
        # No mapping - if using openrouter and not already prefixed, add prefix
        if self.use_openrouter and not model.startswith("perplexity/"):
            return f"perplexity/{model}"
        return model
    
    def _call(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make API call with fallback."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if "model" in payload:
            payload["model"] = self._resolve_model(payload["model"])
        
        try:
            resp = requests.post(
                f"{self.base_url}/{endpoint}", 
                headers=headers, 
                json=payload, 
                timeout=120
            )
            
            # Quota fallback
            if resp.status_code == 401 and "quota" in resp.text.lower() and not self.use_openrouter:
                if not self.quiet_mode:
                    print("[yellow]Perplexity quota exceeded, falling back to OpenRouter...[/yellow]", file=sys.stderr)
                self.use_openrouter = True
                self.api_key = self.or_key
                self.base_url = "https://openrouter.ai/api/v1"
                # Re-resolve model for OpenRouter
                if "model" in payload:
                    payload["model"] = self._resolve_model(payload["model"].replace("perplexity/", ""))
                return self._call(endpoint, payload)
            
            resp.raise_for_status()
            return resp.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e), 
                "status_code": getattr(e.response, 'status_code', 500) if hasattr(e, 'response') and e.response else 500
            }
    
    def chat(self, 
             query: str, 
             model: str = "sonar", 
             messages: Optional[List[Dict]] = None,
             **kwargs) -> Dict[str, Any]:
        """
        Sonar chat completion.
        
        Args:
            query: User query
            model: Model name (sonar, sonar-pro, sonar-reasoning, sonar-deep-research)
            messages: Optional message history
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            API response dict with 'choices', 'citations', 'usage'
        """
        if not messages:
            messages = [{"role": "user", "content": query}]
        
        payload = {"model": model, "messages": messages}
        payload.update(kwargs)
        
        return self._call("chat/completions", payload)
    
    def chat_typed(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        """
        Type-safe chat completion using ChatCompletionRequest.
        
        Args:
            request: ChatCompletionRequest object with all parameters
        
        Returns:
            API response dict
        """
        return self._call("chat/completions", request.to_dict())
    
    def search(self, 
               query: str, 
               limit: int = 10,
               search_mode: SearchMode = SearchMode.WEB,
               recency: Optional[str] = None) -> Dict[str, Any]:
        """
        Raw web search results.
        
        Args:
            query: Search query
            limit: Max results
            search_mode: web, academic, or sec
            recency: hour, day, week, month, year
        
        Returns:
            Search results with citations
        """
        payload = {"query": query, "limit": limit}
        if search_mode:
            payload["search_mode"] = search_mode.value
        if recency:
            payload["search_recency_filter"] = recency
        
        # Use sonar model for search
        return self.chat(query, model="sonar", **payload)
    
    def stream(self, 
               query: str, 
               model: str = "sonar",
               **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Streaming chat completion.
        
        Yields SSE events as they arrive.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self._resolve_model(model),
            "messages": [{"role": "user", "content": query}],
            "stream": True,
            **kwargs
        }
        
        try:
            with requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                stream=True,
                timeout=120
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            try:
                                yield json.loads(data)
                            except json.JSONDecodeError:
                                continue
        except requests.exceptions.RequestException as e:
            yield {"error": str(e)}


# Backward compatibility
PerplexityMonolithic = PerplexitySDK
