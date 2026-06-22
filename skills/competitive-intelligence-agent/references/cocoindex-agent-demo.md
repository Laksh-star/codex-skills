# CocoIndex Agent Demo Reference

Use this reference when documenting or packaging an agent-first competitive-intelligence repo.

## Positioning

Frame the project as:

- agent-first competitive intelligence
- MCP tools for interoperability across Codex, Claude, and other agents
- sample-first by default for reliable demos
- CocoIndex-backed live mode for credible ingestion, indexing, and Postgres persistence

Avoid implying that sample JSON is a live feed. Avoid implying live mode ran unless the command completed against Tavily, an LLM provider, CocoIndex, and Postgres.

## Architecture

```text
Tavily Search -> CocoIndex Flow -> Postgres Tables -> MCP Tools -> Agent
                         |
                         v
              Sample JSON -> Local Analyzer -> Reports/Dashboard
```

## Agent-Facing Tools

Expected MCP tools:

- `analyze_saved_articles`
- `search_events`
- `get_trending_competitors`
- `create_brief`
- `create_dashboard`
- `run_cocoindex_update`

Prefer structured JSON-friendly return values. Include paths for generated artifacts and non-secret effective config for live runs.

## Competitor Arguments

Live updates should accept explicit competitor names per call:

```text
run_cocoindex_update(
  live=true,
  competitors="Perplexity,Glean",
  max_results=2,
  event_query="(product launch OR partnership)",
  search_days_back=14
)
```

Implementation guidance:

- Accept comma-separated strings for broad MCP compatibility.
- Accept JSON arrays when the server framework supports them.
- Keep `.env` as default configuration only.
- Do not mutate `.env` for one-off demos unless the user asks for persistent defaults.
- Return effective non-secret config so the calling agent can see what ran.

## README Checklist

A polished public README should include:

- concise project promise above the fold
- badges for Python, MCP, CocoIndex, and status
- sample-first quick start
- MCP client configuration example
- live CocoIndex setup with Docker/Postgres
- example agent prompts
- arbitrary competitor examples, not only AI-lab defaults
- testing commands
- clear note that generated `reports/` are ignored

## Demo Script

Recommended live demo sequence:

1. Run sample mode and open the generated dashboard.
2. Start MCP server or plugin-backed MCP tools.
3. Ask for trends and a brief from local data.
4. Start Postgres and run a minimal live update with one competitor and one result.
5. Query `mode="cocoindex"` and generate a live dashboard.
6. Explain that the same MCP surface works for Claude, Codex, and other MCP clients.
