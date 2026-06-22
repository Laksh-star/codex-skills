---
name: competitive-intelligence-agent
description: Run or extend an agent-first competitive intelligence workflow backed by local sample data, MCP tools, optional live Tavily/OpenRouter/CocoIndex/Postgres ingestion, and generated briefs or dashboards. Use when asked to set up, demonstrate, test, package, or operate a competitive-intelligence agent; expose competitor intelligence to Claude, Codex, or other MCP clients; run sample-first demos; or switch live ingestion to arbitrary competitor names.
---

# Competitive Intelligence Agent

Use this skill to operate a competitive-intelligence repo as an agent tool system, not just a report script. Prefer a reliable sample-first path, then opt into live CocoIndex only when credentials and Postgres are ready.

## Workflow

1. Find the repo root. Look for `mcp_server.py`, `local_intel.py`, `watchlist.json`, and optional `docker-compose.yml`.
2. Inspect current state before editing: `git status --short`, `rg -n "run_cocoindex_update|FastMCP|CocoIndex|COMPETITORS" .`.
3. Use sample mode first unless the user explicitly asks for live ingestion.
4. For live mode, verify `.env` has `COCOINDEX_DATABASE_URL`, `TAVILY_API_KEY`, and `OPENAI_API_KEY`; never print secret values.
5. Keep generated briefs, dashboards, and JSON/CSV report artifacts out of commits unless the repo explicitly tracks samples.
6. Run focused tests before committing.

## Sample Demo

Use this path for a reliable demo without API keys:

```bash
python3 local_intel.py --dashboard --slug demo
python3 agent_demo.py --slug demo-agent
python3 -m unittest test_local_intel.py
```

Expected outputs usually land in `reports/`:

- Markdown brief
- JSON/CSV event export
- static HTML dashboard
- deterministic agent transcript, if `agent_demo.py` exists

## MCP Tool Demo

Start the MCP server from the repo environment:

```bash
python3 mcp_server.py
```

For client setup, prefer a repo-provided `mcp-config.example.json`. Use an absolute Python path and an absolute `mcp_server.py` path. If the repo is also packaged as a Codex plugin, keep plugin-specific local paths out of public docs.

Useful agent calls:

```text
get_trending_competitors(limit=5)
search_events(query="enterprise customers", limit=5)
create_brief(slug="board-brief")
create_dashboard(slug="demo-dashboard")
```

## Live CocoIndex

Use live ingestion only when explicitly requested. Start Postgres if the repo provides Docker support:

```bash
docker compose up -d postgres
```

Run with explicit per-call competitors instead of editing `.env` for every scenario:

```text
run_cocoindex_update(
  live=true,
  competitors="Apple,Microsoft",
  max_results=2,
  event_query="(product launch OR partnership)",
  search_days_back=14
)
```

Then query the indexed data:

```text
search_events(mode="cocoindex", competitor="Apple", limit=5)
get_trending_competitors(mode="cocoindex", days=7)
create_brief(mode="cocoindex", slug="apple-microsoft-live")
create_dashboard(mode="cocoindex", slug="apple-microsoft-live")
```

`competitors` may be a comma-separated string or a JSON array. Treat `.env` values as defaults, not fixed behavior.

## Validation

For code changes, run:

```bash
python3 -m py_compile main.py mcp_server.py providers.py local_intel.py
python3 -m unittest test_local_intel.py
```

For live changes, add one small credential-gated smoke:

```bash
python3 live_demo_check.py \
  --slug live-smoke \
  --competitors "Apple" \
  --max-results 1 \
  --event-query "(product launch)"
```

Report whether live mode used sample data, local Postgres, or a remote database. Be explicit when live checks were skipped because credentials, Docker, network, or API quota were unavailable.

## References

Read `references/cocoindex-agent-demo.md` when adding docs, README sections, plugin instructions, or MCP client examples for this workflow.
