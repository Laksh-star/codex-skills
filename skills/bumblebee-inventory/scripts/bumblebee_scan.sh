#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNS_DIR="${BUMBLEBEE_RUNS_DIR:-$(pwd)/bumblebee-runs}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
MODE="${1:-}"

DEFAULT_ROOTS=(
  "$(pwd)"
)

OPTIONAL_ROOTS=(
)

MARKER_NAMES=(
  "package.json"
  "package-lock.json"
  "pnpm-lock.yaml"
  "yarn.lock"
  "bun.lock"
  "go.mod"
  "go.sum"
  "pyproject.toml"
  "requirements.txt"
  "requirements-lock.txt"
  "Gemfile.lock"
  "composer.lock"
  ".mcp.json"
  "mcp.json"
)

usage() {
  cat <<'USAGE'
Usage:
  bumblebee_scan.sh roots [--root PATH ...] [--only-root PATH ...]
  bumblebee_scan.sh inventory [--root PATH ...] [--only-root PATH ...]
  bumblebee_scan.sh exposure --catalog PATH [--root PATH ...] [--only-root PATH ...]

Modes:
  roots      Print curated roots and detected dependency/MCP marker files.
  inventory  Run Bumblebee project-profile inventory scan.
  exposure   Run Bumblebee project-profile scan with --exposure-catalog and --findings-only.

Environment:
  BUMBLEBEE_BIN       Override bumblebee executable path.
  BUMBLEBEE_RUNS_DIR  Override output run directory parent. Defaults to ./bumblebee-runs.
USAGE
}

install_guidance() {
  cat <<'GUIDANCE'
bumblebee is not installed or not on PATH.

Install options:
  1. Prefer a prebuilt release binary from:
     https://github.com/perplexityai/bumblebee/releases
  2. If Go is installed, use:
     go install github.com/perplexityai/bumblebee/cmd/bumblebee@latest

This wrapper does not auto-install tools.
GUIDANCE
}

die() {
  echo "error: $*" >&2
  exit 1
}

existing_roots=()
skipped_roots=()
catalog_path=""
include_optional=0
only_roots=()

if [[ -z "$MODE" || "$MODE" == "-h" || "$MODE" == "--help" ]]; then
  usage
  exit 0
fi

case "$MODE" in
  roots|inventory|exposure)
    shift
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

roots=("${DEFAULT_ROOTS[@]}")

while [[ $# -gt 0 ]]; do
  case "$1" in
    --include-optional)
      include_optional=1
      shift
      ;;
    --root)
      [[ $# -ge 2 ]] || die "--root requires a path"
      roots+=("$2")
      shift 2
      ;;
    --only-root)
      [[ $# -ge 2 ]] || die "--only-root requires a path"
      only_roots+=("$2")
      shift 2
      ;;
    --catalog|--exposure-catalog)
      [[ $# -ge 2 ]] || die "$1 requires a path"
      catalog_path="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

if [[ "$include_optional" -eq 1 ]]; then
  roots+=("${OPTIONAL_ROOTS[@]}")
fi
if [[ "${#only_roots[@]}" -gt 0 ]]; then
  roots=("${only_roots[@]}")
fi

unique_roots=()
for root in "${roots[@]}"; do
  already_seen=0
  if [[ "${#unique_roots[@]}" -gt 0 ]]; then
    for existing in "${unique_roots[@]}"; do
      if [[ "$existing" == "$root" ]]; then
        already_seen=1
        break
      fi
    done
  fi
  if [[ "$already_seen" -eq 0 ]]; then
    unique_roots+=("$root")
  fi
done
roots=("${unique_roots[@]}")

for root in "${roots[@]}"; do
  if [[ -d "$root" ]]; then
    existing_roots+=("$root")
  else
    skipped_roots+=("$root")
  fi
done

print_roots() {
  echo "# Bumblebee curated roots"
  echo
  echo "Skill: $SKILL_DIR"
  echo
  echo "## Existing roots"
  if [[ "${#existing_roots[@]}" -eq 0 ]]; then
    echo "- none"
  else
    for root in "${existing_roots[@]}"; do
      echo "- $root"
      find "$root" \
        \( -path '*/node_modules' -o -path '*/.venv' -o -path '*/venv' -o -path '*/.next' -o -path '*/.vite' -o -path '*/vendor' \) -prune \
        -o -type f \( \
          -name package.json -o -name package-lock.json -o -name pnpm-lock.yaml -o -name yarn.lock -o -name bun.lock \
          -o -name go.mod -o -name go.sum -o -name pyproject.toml -o -name requirements.txt -o -name requirements-lock.txt \
          -o -name Gemfile.lock -o -name composer.lock -o -name .mcp.json -o -name mcp.json \
        \) -print |
        sed "s#^$root/#  - #"
    done
  fi
  echo
  echo "## Skipped missing roots"
  if [[ "${#skipped_roots[@]}" -eq 0 ]]; then
    echo "- none"
  else
    printf -- "- %s\n" "${skipped_roots[@]}"
  fi
}

write_reports() {
  local out_dir="$1"
  local records_file="$2"
  local diagnostics_file="$3"
  local summary_file="$4"
  local report_file="$5"
  local summary_args=("$out_dir" "$records_file" "$diagnostics_file" "$summary_file" "$report_file")
  if [[ "${#existing_roots[@]}" -gt 0 ]]; then
    summary_args+=("${existing_roots[@]}")
  fi
  summary_args+=("--")
  if [[ "${#skipped_roots[@]}" -gt 0 ]]; then
    summary_args+=("${skipped_roots[@]}")
  fi
  python3 - "${summary_args[@]}" <<'PY'
import html
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

out_dir = Path(sys.argv[1])
records_file = Path(sys.argv[2])
diagnostics_file = Path(sys.argv[3])
summary_file = Path(sys.argv[4])
report_file = Path(sys.argv[5])
sep = sys.argv.index("--")
roots = sys.argv[6:sep]
skipped = sys.argv[sep + 1:]

record_types = Counter()
ecosystems = Counter()
by_root = defaultdict(lambda: Counter())
findings = []
mcp_records = []
high_confidence = 0
packages_by_root = defaultdict(list)
diagnostics = []

def root_for(path):
    if not path:
        return "unknown"
    for root in sorted(roots, key=len, reverse=True):
        if path == root or path.startswith(root.rstrip("/") + "/"):
            return root
    return "unknown"

if records_file.exists():
    with records_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                record_types["unparseable"] += 1
                continue
            record_type = row.get("record_type", "unknown")
            record_types[record_type] += 1
            ecosystem = row.get("ecosystem")
            if ecosystem:
                ecosystems[ecosystem] += 1
            source_file = row.get("source_file") or row.get("project_path") or ""
            root = root_for(source_file)
            by_root[root][record_type] += 1
            if ecosystem:
                by_root[root][f"ecosystem:{ecosystem}"] += 1
            if row.get("confidence") == "high":
                high_confidence += 1
            if record_type == "finding":
                findings.append(row)
            if record_type == "package":
                packages_by_root[root].append(row)
            if row.get("source_type") == "mcp-config" or ecosystem == "mcp":
                mcp_records.append(row)

diagnostic_counts = Counter()
if diagnostics_file.exists():
    with diagnostics_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                diagnostic_counts["unparseable"] += 1
                diagnostics.append({"level": "unparseable", "message": line})
                continue
            level = row.get("level") or row.get("severity") or row.get("record_type") or "diagnostic"
            diagnostic_counts[str(level)] += 1
            diagnostics.append(row)

lines = [
    "# Bumblebee Scan Summary",
    "",
    f"Output directory: `{out_dir}`",
    f"Records: `{records_file}`",
    f"Diagnostics: `{diagnostics_file}`",
    "",
    "## Totals",
    "",
    f"- Package records: {record_types.get('package', 0)}",
    f"- Finding records: {record_types.get('finding', 0)}",
    f"- Scan summaries: {record_types.get('scan_summary', 0)}",
    f"- MCP config records: {len(mcp_records)}",
    f"- High-confidence records: {high_confidence}",
    f"- Diagnostics: {sum(diagnostic_counts.values())}",
    "",
    "## Ecosystems",
    "",
]

if ecosystems:
    for name, count in sorted(ecosystems.items()):
        lines.append(f"- {name}: {count}")
else:
    lines.append("- none")

lines.extend(["", "## Roots", ""])
for root in roots:
    counts = by_root.get(root, Counter())
    ecosystem_names = sorted(k.split(":", 1)[1] for k in counts if k.startswith("ecosystem:"))
    ecosystems_text = ", ".join(ecosystem_names) if ecosystem_names else "none"
    lines.append(f"- `{root}`")
    lines.append(f"  - packages: {counts.get('package', 0)}")
    lines.append(f"  - findings: {counts.get('finding', 0)}")
    lines.append(f"  - ecosystems: {ecosystems_text}")

if by_root.get("unknown") and (by_root["unknown"].get("package", 0) or by_root["unknown"].get("finding", 0)):
    counts = by_root["unknown"]
    lines.append("- `unknown`")
    lines.append(f"  - packages: {counts.get('package', 0)}")
    lines.append(f"  - findings: {counts.get('finding', 0)}")

lines.extend(["", "## Findings", ""])
if findings:
    for row in findings[:50]:
        name = row.get("package_name") or row.get("normalized_name") or "unknown"
        version = row.get("version") or "(no version)"
        severity = row.get("severity") or "unknown"
        source = row.get("source_file") or row.get("project_path") or "unknown source"
        lines.append(f"- {severity}: {name} {version} in `{source}`")
    if len(findings) > 50:
        lines.append(f"- truncated: {len(findings) - 50} more findings in raw NDJSON")
else:
    lines.append("- none")

lines.extend(["", "## Diagnostics", ""])
if diagnostic_counts:
    for name, count in sorted(diagnostic_counts.items()):
        lines.append(f"- {name}: {count}")
else:
    lines.append("- none")

lines.extend(["", "## Skipped roots", ""])
if skipped:
    lines.extend(f"- `{root}`" for root in skipped)
else:
    lines.append("- none")

summary_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

def esc(value):
    return html.escape("" if value is None else str(value))

def badge(text, kind="muted"):
    return f'<span class="badge {kind}">{esc(text)}</span>'

def severity_class(value):
    value = (value or "").lower()
    if value in {"critical", "high"}:
        return "bad"
    if value in {"medium", "warning", "warn"}:
        return "warn"
    return "muted"

def run_git(root, *args):
    try:
        result = subprocess.run(
            ["git", "-C", root, *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return ""

def github_base_from_remote(remote):
    if remote.startswith("https://github.com/"):
        base = remote[:-4] if remote.endswith(".git") else remote
        return base
    if remote.startswith("git@github.com:"):
        repo = remote.removeprefix("git@github.com:")
        repo = repo[:-4] if repo.endswith(".git") else repo
        return f"https://github.com/{repo}"
    return ""

tracked_cache = {}

def is_tracked(root, rel):
    if not rel or rel == ".":
        return True
    key = (root, rel)
    if key not in tracked_cache:
        try:
            subprocess.run(
                ["git", "-C", root, "ls-files", "--error-unmatch", "--", rel],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            tracked_cache[key] = True
        except Exception:
            tracked_cache[key] = False
    return tracked_cache[key]

repo_meta = {}
for root in roots:
    remote = run_git(root, "remote", "get-url", "origin")
    commit = run_git(root, "rev-parse", "HEAD")
    github_base = github_base_from_remote(remote)
    repo_meta[root] = {
        "root": root,
        "remote": remote,
        "commit": commit,
        "github_base": github_base,
        "public": bool(github_base and commit),
    }

def public_path(path):
    if not path:
        return {"path": "", "root": "", "url": ""}
    path = str(path)
    for root in sorted(roots, key=len, reverse=True):
        prefix = root.rstrip("/")
        if path == prefix:
            meta = repo_meta.get(root, {})
            url = meta.get("github_base", "")
            if url and meta.get("commit"):
                url = f"{url}/tree/{meta['commit']}"
            return {"path": ".", "root": root, "url": url}
        if path.startswith(prefix + "/"):
            rel = path[len(prefix) + 1:]
            meta = repo_meta.get(root, {})
            url = ""
            if meta.get("github_base") and meta.get("commit") and is_tracked(root, rel):
                encoded = "/".join(quote(part) for part in rel.split("/"))
                url = f"{meta['github_base']}/blob/{meta['commit']}/{encoded}"
            return {"path": rel, "root": root, "url": url}
    return {"path": "[outside scanned repo]", "root": "", "url": ""}

def sanitize_record(row):
    keep = dict(row)
    keep.pop("endpoint", None)
    keep.pop("run_id", None)
    for key in ("source_file", "project_path"):
        if key in keep:
            info = public_path(keep.get(key))
            keep[key] = info["path"]
            if info["url"]:
                keep[f"{key}_url"] = info["url"]
    if isinstance(keep.get("roots"), list):
        sanitized_roots = []
        for root_entry in keep["roots"]:
            if isinstance(root_entry, dict):
                sanitized_entry = dict(root_entry)
                info = public_path(sanitized_entry.get("path"))
                sanitized_entry["path"] = info["path"]
                if info["url"]:
                    sanitized_entry["path_url"] = info["url"]
                sanitized_roots.append(sanitized_entry)
            else:
                sanitized_roots.append(root_entry)
        keep["roots"] = sanitized_roots
    root = root_for(row.get("source_file") or row.get("project_path") or "")
    meta = repo_meta.get(root)
    if meta and meta.get("public"):
        keep["repository"] = {
            "remote": meta["github_base"],
            "commit": meta["commit"],
        }
    return keep

sanitized_records_file = out_dir / "sanitized-inventory.ndjson"
public_summary_file = out_dir / "public-summary.md"
agent_notes_file = out_dir / "agent-notes.md"
public_report_file = out_dir / "public-report.html"

sanitized_rows = []
if records_file.exists():
    with records_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                sanitized_rows.append(sanitize_record(json.loads(line)))
            except json.JSONDecodeError:
                continue

with sanitized_records_file.open("w", encoding="utf-8") as f:
    for row in sanitized_rows:
        f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

public_repos = [meta for meta in repo_meta.values() if meta.get("public")]
public_repo_text = ", ".join(f"[{meta['github_base']}]({meta['github_base']}/tree/{meta['commit']})" for meta in public_repos) or "No public GitHub remote detected."
public_lines = [
    "# Public Bumblebee Scan Summary",
    "",
    f"Repository: {public_repo_text}",
    f"Scanner: Bumblebee {next((row.get('scanner_version') for row in sanitized_rows if row.get('scanner_version')), 'unknown')}",
    "",
    "## Plain-English Summary",
    "",
    f"This run scanned public repository metadata and dependency files with Bumblebee's project profile. It found {record_types.get('package', 0)} package records across {len(ecosystems)} ecosystem(s), including {len(mcp_records)} MCP config record(s). It found {record_types.get('finding', 0)} exposure finding(s).",
    "",
    "This was an inventory run, not an advisory-specific vulnerability scan. To check exposure to a specific campaign or compromised version list, rerun in exposure mode with a reviewed catalog.",
    "",
    "## Results",
    "",
    f"- Package records: {record_types.get('package', 0)}",
    f"- MCP config records: {len(mcp_records)}",
    f"- Exposure findings: {record_types.get('finding', 0)}",
    f"- Ecosystems: {', '.join(sorted(ecosystems)) if ecosystems else 'none'}",
    f"- Diagnostics: {sum(diagnostic_counts.values())}",
    "",
    "## Public Artifacts",
    "",
    "- `public-report.html`: visual report with public repository links",
    "- `sanitized-inventory.ndjson`: machine-readable sanitized records",
    "- `agent-notes.md`: AI coding agent handoff notes",
    "",
]
public_summary_file.write_text("\n".join(public_lines), encoding="utf-8")

mcp_note_lines = []
for row in mcp_records:
    info = public_path(row.get("source_file"))
    mcp_note_lines.append(
        f"- Inspect MCP config `{info['path']}`"
        + (f" ({info['url']})" if info["url"] else "")
        + f"; server `{row.get('server_name') or row.get('package_name')}`, confidence `{row.get('confidence')}`."
    )
if not mcp_note_lines:
    mcp_note_lines.append("- No MCP config records were detected in this run.")

agent_lines = [
    "# AI Coding Agent Notes",
    "",
    "Use these notes with the sanitized report, not the raw local NDJSON.",
    "",
    "## Context",
    "",
    f"- Scan profile: `project`",
    f"- Package records: `{record_types.get('package', 0)}`",
    f"- MCP config records: `{len(mcp_records)}`",
    f"- Exposure findings: `{record_types.get('finding', 0)}`",
    f"- Public repo(s): {', '.join(meta['github_base'] for meta in public_repos) if public_repos else 'none detected'}",
    "",
    "## Recommended Actions",
    "",
    "- Treat this as package/MCP inventory, not a vulnerability verdict.",
    "- Run exposure mode with a reviewed Bumblebee catalog when checking a named advisory.",
    "- Review MCP config records because they describe developer-tool execution surfaces.",
    "- Compare lockfile-derived records with installed `node_modules` records if dependency drift matters.",
    "- Prefer repo-relative paths and GitHub blob URLs in public writeups; avoid raw local paths and endpoint fields.",
    "",
    "## MCP Follow-Up",
    "",
    *mcp_note_lines,
]
agent_notes_file.write_text("\n".join(agent_lines) + "\n", encoding="utf-8")

cards = [
    ("Package records", record_types.get("package", 0)),
    ("Finding records", record_types.get("finding", 0)),
    ("MCP config records", len(mcp_records)),
    ("High-confidence records", high_confidence),
    ("Diagnostics", sum(diagnostic_counts.values())),
]

root_rows = []
for root in roots:
    counts = by_root.get(root, Counter())
    ecosystem_names = sorted(k.split(":", 1)[1] for k in counts if k.startswith("ecosystem:"))
    root_rows.append(
        "<tr>"
        f"<td><code>{esc(root)}</code></td>"
        f"<td>{counts.get('package', 0)}</td>"
        f"<td>{counts.get('finding', 0)}</td>"
        f"<td>{', '.join(esc(x) for x in ecosystem_names) if ecosystem_names else 'none'}</td>"
        "</tr>"
    )

ecosystem_rows = [
    f"<tr><td>{esc(name)}</td><td>{count}</td></tr>"
    for name, count in sorted(ecosystems.items())
]
if not ecosystem_rows:
    ecosystem_rows = ["<tr><td colspan='2'>none</td></tr>"]

mcp_rows = []
for row in mcp_records:
    mcp_rows.append(
        "<tr>"
        f"<td>{esc(row.get('server_name') or row.get('package_name') or row.get('normalized_name'))}</td>"
        f"<td>{esc(row.get('package_name'))}</td>"
        f"<td>{esc(row.get('requested_spec') or row.get('version'))}</td>"
        f"<td><code>{esc(row.get('source_file'))}</code></td>"
        f"<td>{badge(row.get('confidence') or 'unknown')}</td>"
        "</tr>"
    )
if not mcp_rows:
    mcp_rows = ["<tr><td colspan='5'>No MCP config records found.</td></tr>"]

finding_rows = []
for row in findings:
    severity = row.get("severity") or "unknown"
    finding_rows.append(
        "<tr>"
        f"<td>{badge(severity, severity_class(severity))}</td>"
        f"<td>{esc(row.get('package_name') or row.get('normalized_name'))}</td>"
        f"<td>{esc(row.get('version') or '(no version)')}</td>"
        f"<td>{esc(row.get('catalog_id') or '')}</td>"
        f"<td>{esc(row.get('evidence') or '')}</td>"
        f"<td><code>{esc(row.get('source_file') or row.get('project_path'))}</code></td>"
        "</tr>"
    )
if not finding_rows:
    finding_rows = ["<tr><td colspan='6'>No exposure findings in this run.</td></tr>"]

package_rows = []
for root in roots:
    for row in packages_by_root.get(root, [])[:250]:
        package_rows.append(
            "<tr>"
            f"<td><code>{esc(root)}</code></td>"
            f"<td>{esc(row.get('ecosystem'))}</td>"
            f"<td>{esc(row.get('package_name') or row.get('normalized_name'))}</td>"
            f"<td>{esc(row.get('version'))}</td>"
            f"<td>{badge(row.get('confidence') or 'unknown')}</td>"
            f"<td><code>{esc(row.get('source_file'))}</code></td>"
            "</tr>"
        )
if not package_rows:
    package_rows = ["<tr><td colspan='6'>No package records found.</td></tr>"]

diag_rows = []
for row in diagnostics[:200]:
    level = row.get("level") or row.get("severity") or row.get("record_type") or "diagnostic"
    message = row.get("message") or row.get("error") or json.dumps(row, sort_keys=True)
    diag_rows.append(
        "<tr>"
        f"<td>{badge(level, severity_class(level))}</td>"
        f"<td>{esc(message)}</td>"
        "</tr>"
    )
if not diag_rows:
    diag_rows = ["<tr><td colspan='2'>No diagnostics.</td></tr>"]

html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bumblebee Scan Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #162033;
      --muted: #667085;
      --line: #d9dee8;
      --accent: #0f766e;
      --bad: #b42318;
      --warn: #b54708;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    header {{
      padding: 28px 32px 18px;
      background: #10243f;
      color: white;
    }}
    header h1 {{ margin: 0 0 8px; font-size: 28px; letter-spacing: 0; }}
    header p {{ margin: 0; color: #d5deea; }}
    main {{ padding: 24px 32px 40px; max-width: 1440px; margin: 0 auto; }}
    section {{ margin: 0 0 24px; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px; }}
    .metric {{ font-size: 28px; font-weight: 700; margin-top: 4px; }}
    .label {{ color: var(--muted); }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #eef2f7; color: #344054; font-weight: 650; }}
    tr:last-child td {{ border-bottom: 0; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 2px 8px; font-size: 12px; background: #eef2f7; color: #344054; }}
    .badge.bad {{ background: #fee4e2; color: var(--bad); }}
    .badge.warn {{ background: #fef0c7; color: var(--warn); }}
    .links a {{ color: var(--accent); text-decoration: none; margin-right: 16px; }}
    .links a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <h1>Bumblebee Scan Report</h1>
    <p>{esc(out_dir)}</p>
  </header>
  <main>
    <section class="grid">
      {''.join(f'<div class="card"><div class="label">{esc(label)}</div><div class="metric">{value}</div></div>' for label, value in cards)}
    </section>
    <section class="card links">
      <h2>Raw Outputs</h2>
      <a href="{esc(records_file.name)}">inventory.ndjson</a>
      <a href="{esc(diagnostics_file.name)}">diagnostics.ndjson</a>
      <a href="{esc(summary_file.name)}">summary.md</a>
    </section>
    <section>
      <h2>Roots</h2>
      <table><thead><tr><th>Root</th><th>Packages</th><th>Findings</th><th>Ecosystems</th></tr></thead><tbody>{''.join(root_rows)}</tbody></table>
    </section>
    <section>
      <h2>Ecosystems</h2>
      <table><thead><tr><th>Ecosystem</th><th>Records</th></tr></thead><tbody>{''.join(ecosystem_rows)}</tbody></table>
    </section>
    <section>
      <h2>MCP Config Records</h2>
      <table><thead><tr><th>Server</th><th>Package</th><th>Requested Spec</th><th>Source</th><th>Confidence</th></tr></thead><tbody>{''.join(mcp_rows)}</tbody></table>
    </section>
    <section>
      <h2>Findings</h2>
      <table><thead><tr><th>Severity</th><th>Package</th><th>Version</th><th>Catalog</th><th>Evidence</th><th>Source</th></tr></thead><tbody>{''.join(finding_rows)}</tbody></table>
    </section>
    <section>
      <h2>Package Records</h2>
      <table><thead><tr><th>Root</th><th>Ecosystem</th><th>Package</th><th>Version</th><th>Confidence</th><th>Source</th></tr></thead><tbody>{''.join(package_rows)}</tbody></table>
    </section>
    <section>
      <h2>Diagnostics</h2>
      <table><thead><tr><th>Level</th><th>Message</th></tr></thead><tbody>{''.join(diag_rows)}</tbody></table>
    </section>
  </main>
</body>
</html>
"""
report_file.write_text(html_doc, encoding="utf-8")

public_root_rows = []
for root in roots:
    counts = by_root.get(root, Counter())
    meta = repo_meta.get(root, {})
    label = meta.get("github_base") or public_path(root)["path"] or "unknown"
    if meta.get("github_base") and meta.get("commit"):
        label_html = f'<a href="{esc(meta["github_base"] + "/tree/" + meta["commit"])}">{esc(label)}</a>'
    else:
        label_html = esc(label)
    ecosystem_names = sorted(k.split(":", 1)[1] for k in counts if k.startswith("ecosystem:"))
    public_root_rows.append(
        "<tr>"
        f"<td>{label_html}</td>"
        f"<td><code>{esc(meta.get('commit', '')[:12])}</code></td>"
        f"<td>{counts.get('package', 0)}</td>"
        f"<td>{counts.get('finding', 0)}</td>"
        f"<td>{', '.join(esc(x) for x in ecosystem_names) if ecosystem_names else 'none'}</td>"
        "</tr>"
    )

public_mcp_rows = []
for row in mcp_records:
    info = public_path(row.get("source_file"))
    source_html = f'<a href="{esc(info["url"])}"><code>{esc(info["path"])}</code></a>' if info["url"] else f'<code>{esc(info["path"])}</code>'
    public_mcp_rows.append(
        "<tr>"
        f"<td>{esc(row.get('server_name') or row.get('package_name') or row.get('normalized_name'))}</td>"
        f"<td>{esc(row.get('package_name'))}</td>"
        f"<td>{esc(row.get('requested_spec') or row.get('version'))}</td>"
        f"<td>{source_html}</td>"
        f"<td>{badge(row.get('confidence') or 'unknown')}</td>"
        "</tr>"
    )
if not public_mcp_rows:
    public_mcp_rows = ["<tr><td colspan='5'>No MCP config records found.</td></tr>"]

public_finding_rows = []
for row in findings:
    severity = row.get("severity") or "unknown"
    info = public_path(row.get("source_file") or row.get("project_path"))
    source_html = f'<a href="{esc(info["url"])}"><code>{esc(info["path"])}</code></a>' if info["url"] else f'<code>{esc(info["path"])}</code>'
    public_finding_rows.append(
        "<tr>"
        f"<td>{badge(severity, severity_class(severity))}</td>"
        f"<td>{esc(row.get('package_name') or row.get('normalized_name'))}</td>"
        f"<td>{esc(row.get('version') or '(no version)')}</td>"
        f"<td>{esc(row.get('catalog_id') or '')}</td>"
        f"<td>{esc(row.get('evidence') or '')}</td>"
        f"<td>{source_html}</td>"
        "</tr>"
    )
if not public_finding_rows:
    public_finding_rows = ["<tr><td colspan='6'>No exposure findings in this inventory run.</td></tr>"]

public_package_rows = []
for row in sanitized_rows:
    if row.get("record_type") != "package":
        continue
    source = row.get("source_file", "")
    source_url = row.get("source_file_url", "")
    source_html = f'<a href="{esc(source_url)}"><code>{esc(source)}</code></a>' if source_url else f'<code>{esc(source)}</code>'
    public_package_rows.append(
        "<tr>"
        f"<td>{esc(row.get('ecosystem'))}</td>"
        f"<td>{esc(row.get('package_name') or row.get('normalized_name'))}</td>"
        f"<td>{esc(row.get('version'))}</td>"
        f"<td>{badge(row.get('confidence') or 'unknown')}</td>"
        f"<td>{source_html}</td>"
        "</tr>"
    )
    if len(public_package_rows) >= 250:
        break
if not public_package_rows:
    public_package_rows = ["<tr><td colspan='5'>No package records found.</td></tr>"]

public_html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Public Bumblebee Scan Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #162033;
      --muted: #667085;
      --line: #d9dee8;
      --accent: #0f766e;
      --bad: #b42318;
      --warn: #b54708;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--bg); }}
    header {{ padding: 28px 32px 18px; background: #10243f; color: white; }}
    header h1 {{ margin: 0 0 8px; font-size: 28px; letter-spacing: 0; }}
    header p {{ margin: 0; color: #d5deea; }}
    main {{ padding: 24px 32px 40px; max-width: 1440px; margin: 0 auto; }}
    section {{ margin: 0 0 24px; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; }}
    p {{ margin: 0 0 10px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px; }}
    .metric {{ font-size: 28px; font-weight: 700; margin-top: 4px; }}
    .label, .muted {{ color: var(--muted); }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #eef2f7; color: #344054; font-weight: 650; }}
    tr:last-child td {{ border-bottom: 0; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 2px 8px; font-size: 12px; background: #eef2f7; color: #344054; }}
    .badge.bad {{ background: #fee4e2; color: var(--bad); }}
    .badge.warn {{ background: #fef0c7; color: var(--warn); }}
    .links a {{ margin-right: 16px; }}
  </style>
</head>
<body>
  <header>
    <h1>Public Bumblebee Scan Report</h1>
    <p>Sanitized report for public writeups and AI coding agent handoff.</p>
  </header>
  <main>
    <section class="card">
      <h2>Brief Summary</h2>
      <p>This run scanned public repository metadata and dependency files with Bumblebee's project profile. It found <strong>{record_types.get('package', 0)}</strong> package records, <strong>{len(mcp_records)}</strong> MCP config record, and <strong>{record_types.get('finding', 0)}</strong> exposure findings.</p>
      <p class="muted">This is an inventory report, not an advisory-specific vulnerability verdict. Local endpoint identity and absolute filesystem paths are removed from this public view.</p>
    </section>
    <section class="grid">
      {''.join(f'<div class="card"><div class="label">{esc(label)}</div><div class="metric">{value}</div></div>' for label, value in cards)}
    </section>
    <section class="card links">
      <h2>Public Artifacts</h2>
      <a href="{esc(public_summary_file.name)}">public-summary.md</a>
      <a href="{esc(agent_notes_file.name)}">agent-notes.md</a>
      <a href="{esc(sanitized_records_file.name)}">sanitized-inventory.ndjson</a>
    </section>
    <section>
      <h2>Repositories</h2>
      <table><thead><tr><th>Repository</th><th>Commit</th><th>Packages</th><th>Findings</th><th>Ecosystems</th></tr></thead><tbody>{''.join(public_root_rows)}</tbody></table>
    </section>
    <section>
      <h2>MCP Config Records</h2>
      <table><thead><tr><th>Server</th><th>Package</th><th>Requested Spec</th><th>Source</th><th>Confidence</th></tr></thead><tbody>{''.join(public_mcp_rows)}</tbody></table>
    </section>
    <section>
      <h2>Findings</h2>
      <table><thead><tr><th>Severity</th><th>Package</th><th>Version</th><th>Catalog</th><th>Evidence</th><th>Source</th></tr></thead><tbody>{''.join(public_finding_rows)}</tbody></table>
    </section>
    <section>
      <h2>Package Records</h2>
      <table><thead><tr><th>Ecosystem</th><th>Package</th><th>Version</th><th>Confidence</th><th>Source</th></tr></thead><tbody>{''.join(public_package_rows)}</tbody></table>
    </section>
  </main>
</body>
</html>
"""
public_report_file.write_text(public_html_doc, encoding="utf-8")
PY
}

if [[ "$MODE" == "roots" ]]; then
  print_roots
  exit 0
fi

if [[ "${#existing_roots[@]}" -eq 0 ]]; then
  die "no configured roots exist"
fi

BUMBLEBEE_BIN="${BUMBLEBEE_BIN:-bumblebee}"
if ! command -v "$BUMBLEBEE_BIN" >/dev/null 2>&1; then
  install_guidance >&2
  exit 127
fi

if [[ "$MODE" == "exposure" ]]; then
  [[ -n "$catalog_path" ]] || die "exposure mode requires --catalog PATH"
  [[ -e "$catalog_path" ]] || die "catalog not found: $catalog_path"
fi

out_dir="$RUNS_DIR/$TIMESTAMP-$MODE"
mkdir -p "$out_dir"
records_file="$out_dir/inventory.ndjson"
diagnostics_file="$out_dir/diagnostics.ndjson"
summary_file="$out_dir/summary.md"
report_file="$out_dir/report.html"
roots_file="$out_dir/roots.txt"

printf "%s\n" "${existing_roots[@]}" > "$roots_file"

cmd=("$BUMBLEBEE_BIN" scan --profile project)
for root in "${existing_roots[@]}"; do
  cmd+=(--root "$root")
done

if [[ "$MODE" == "exposure" ]]; then
  cmd+=(--exposure-catalog "$catalog_path" --findings-only)
fi

"${cmd[@]}" >"$records_file" 2>"$diagnostics_file"
write_reports "$out_dir" "$records_file" "$diagnostics_file" "$summary_file" "$report_file"

echo "Bumblebee $MODE run complete"
echo "Output directory: $out_dir"
echo "Summary: $summary_file"
echo "HTML report: $report_file"
echo "Public summary: $out_dir/public-summary.md"
echo "Public HTML report: $out_dir/public-report.html"
echo "Agent notes: $out_dir/agent-notes.md"
echo "Sanitized records: $out_dir/sanitized-inventory.ndjson"
echo "Records: $records_file"
echo "Diagnostics: $diagnostics_file"
