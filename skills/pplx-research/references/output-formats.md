# Output Formats

Pass `--format <value>` (or `-f <value>`) to control how results are rendered.
Always combine with `--quiet` when capturing output programmatically.

---

## markdown (default)

Structured with section headers, bullet lists, and a sources block at the bottom.
Best for: human reading, saving to `.md` files, rendering in Notion/Obsidian/GitHub.

```
# gRPC vs REST: A Comparison

## Overview
gRPC and REST are two dominant paradigms for building APIs. gRPC uses Protocol Buffers
over HTTP/2, while REST typically uses JSON over HTTP/1.1.

## Performance
- **gRPC** is significantly faster for high-throughput scenarios due to binary
  serialization and multiplexed streams.
- **REST** has higher latency per request but is universally supported.

## When to Choose

| Factor | gRPC | REST |
|--------|------|------|
| Browser clients | Limited | Native |
| Streaming | Bidirectional | SSE/WebSockets |
| Schema enforcement | Strict (proto) | Optional (OpenAPI) |

## Sources
1. https://grpc.io/docs/what-is-grpc/overview/
2. https://www.redhat.com/en/topics/api/what-is-a-rest-api
3. https://docs.microsoft.com/en-us/dotnet/architecture/cloud-native/grpc
```

---

## json

Machine-readable JSON with content, citations, metadata.
Best for: programmatic parsing, agent pipelines, extracting sources separately.

```json
{
  "content": "gRPC uses Protocol Buffers over HTTP/2 for high-performance RPC...",
  "citations": [
    "https://grpc.io/docs/what-is-grpc/overview/",
    "https://www.redhat.com/en/topics/api/what-is-a-rest-api"
  ],
  "iterations": 1,
  "mode": "quick",
  "usage": {
    "prompt_tokens": 312,
    "completion_tokens": 487,
    "total_tokens": 799
  }
}
```

**Parsing in bash:**
```bash
result=$(pplx-research "gRPC vs REST" --format json --quiet)
content=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['content'])")
first_citation=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['citations'][0])")
```

**Parsing in Python:**
```python
import subprocess, json
result = subprocess.run(
    ["pplx-research", "gRPC vs REST", "--format", "json", "--quiet"],
    capture_output=True, text=True, check=True
)
data = json.loads(result.stdout)
print(data["content"])
print(data["citations"])
```

---

## summary

A single concise paragraph — no headers, no bullets, no source list.
Best for: quick agent consumption, passing to the next pipeline step, short answers.

```
gRPC is a high-performance RPC framework from Google that uses Protocol Buffers for
serialization and HTTP/2 for transport, offering bidirectional streaming and strong
schema contracts. REST uses JSON over HTTP/1.1, is universally supported by browsers,
and is simpler to debug. Choose gRPC for internal microservice communication where
performance matters; choose REST for public-facing APIs that need broad client support.
```

---

## plain

Unformatted text with no markdown symbols (no `#`, `*`, `-`, backticks, or tables).
Best for: piping to tools that strip markdown, plain-text email, terminal display without
a markdown renderer.

```
gRPC vs REST Comparison

gRPC uses Protocol Buffers over HTTP/2 while REST uses JSON over HTTP/1.1.

Performance: gRPC is faster due to binary serialization. REST has wider compatibility.

Use gRPC for internal microservices and high-throughput streaming scenarios.
Use REST for public APIs, browser clients, and when broad tooling support is needed.

Sources:
- https://grpc.io/docs/what-is-grpc/overview/
- https://www.redhat.com/en/topics/api/what-is-a-rest-api
```

---

## Format Selection Guide

| Use case | Best format |
|----------|-------------|
| Save to file, read later | `markdown` |
| Parse in script/agent | `json` |
| One-line answer to pass on | `summary` |
| Pipe to grep/sed/awk | `plain` |
| Render in Notion/GitHub | `markdown` |
