#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const skillDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = parseArgs(process.argv.slice(2));

if (args.help) {
  printHelp();
  process.exit(0);
}

const outDir = path.resolve(args.out || "codex-capability-report");
const rubricPath = path.resolve(args.rubric || path.join(skillDir, "references", "default-rubric.json"));
const rubric = readJson(rubricPath);
const previous = readJsonIfExists(path.join(outDir, "report.json"), null);
const loaded = args.input
  ? loadInput(path.resolve(args.input))
  : loadLocalHistory(path.resolve(args.codexHome || process.env.CODEX_HOME || path.join(os.homedir(), ".codex")));

const report = buildReport(loaded, rubric, {
  redacted: Boolean(args.redacted),
  includeContext: Boolean(args.includeContext),
  timezone: args.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
  previous,
});

if (!report.coverage.complete) {
  throw new Error(`Coverage reconciliation failed: ${JSON.stringify(report.coverage)}`);
}

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, "report.json"), `${JSON.stringify(report, null, 2)}\n`);
fs.writeFileSync(path.join(outDir, "report.md"), renderMarkdown(report));
fs.writeFileSync(path.join(outDir, "report.html"), renderHtml(report));

console.log(`Capability report written to ${outDir}`);
console.log(`Coverage: ${report.summary.totalTasks}/${report.coverage.expectedTasks} tasks`);
console.log(`Classified: ${report.summary.classifiedTasks}/${report.summary.totalTasks}`);
console.log(`Average maturity signal: ${report.summary.averageScore}/5`);
console.log(`Privacy mode: ${report.meta.redacted ? "redacted" : "private local"}`);

function parseArgs(argv) {
  const parsed = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--redacted") parsed.redacted = true;
    else if (token === "--include-context") parsed.includeContext = true;
    else if (token === "--help" || token === "-h") parsed.help = true;
    else if (["--out", "--input", "--rubric", "--codex-home", "--timezone"].includes(token)) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) throw new Error(`${token} requires a value`);
      const key = token.replace(/^--/, "").replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
      parsed[key] = value;
      index += 1;
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }
  return parsed;
}

function printHelp() {
  console.log(`Usage: build-capability-report.mjs [options]

Options:
  --out <dir>           Output directory (default: ./codex-capability-report)
  --input <json>        Use normalized JSON instead of local Codex state
  --codex-home <dir>    Override CODEX_HOME discovery
  --rubric <json>       Override the default capability rubric
  --redacted            Remove titles, IDs, paths, and request context
  --include-context     Show bounded request context in the private HTML log
  --timezone <zone>     Display timezone (default: system timezone)
  --help                Show this help`);
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function readJsonIfExists(filePath, fallback) {
  if (!fs.existsSync(filePath)) return fallback;
  try {
    return readJson(filePath);
  } catch {
    return fallback;
  }
}

function loadInput(filePath) {
  const payload = readJson(filePath);
  const rows = Array.isArray(payload) ? payload : payload.threads;
  if (!Array.isArray(rows)) throw new Error("Input JSON must be an array or an object with a threads array");
  const byId = new Map();
  rows.forEach((row, index) => {
    const thread = normalizeThread(row, index);
    byId.set(thread.id, thread);
  });
  return {
    threads: [...byId.values()],
    expectedIds: new Set(byId.keys()),
    source: {
      mode: "input",
      label: payload.source || path.basename(filePath),
      appDatabaseTasks: 0,
      sessionIndexTasks: 0,
      inputTasks: byId.size,
      limitations: ["Coverage is measured against the supplied normalized input."],
    },
  };
}

function loadLocalHistory(codexHome) {
  const sessionIndexPath = path.join(codexHome, "session_index.jsonl");
  const appDatabasePath = findLatestSqlite(codexHome);
  const appThreads = appDatabasePath ? readSqliteThreads(appDatabasePath) : new Map();
  const sessionThreads = readSessionIndex(sessionIndexPath);
  const ids = new Set([...appThreads.keys(), ...sessionThreads.keys()]);
  const threads = [...ids].map((id, index) => mergeThread(id, appThreads.get(id), sessionThreads.get(id), index));
  if (!threads.length) {
    throw new Error(`No Codex tasks found under ${codexHome}. Use --input with a normalized JSON export.`);
  }
  return {
    threads,
    expectedIds: ids,
    source: {
      mode: "local-codex",
      label: "Local Codex history",
      appDatabasePath,
      sessionIndexPath: fs.existsSync(sessionIndexPath) ? sessionIndexPath : null,
      appDatabaseTasks: appThreads.size,
      sessionIndexTasks: sessionThreads.size,
      inputTasks: 0,
      limitations: [
        "Local Codex application state is not a stable public API and may change.",
        "Cloud conversations absent from local Codex state are outside the observable scope.",
      ],
    },
  };
}

function findLatestSqlite(codexHome) {
  if (!fs.existsSync(codexHome)) return null;
  return fs.readdirSync(codexHome)
    .filter((name) => /^state_\d+\.sqlite$/.test(name))
    .map((name) => path.join(codexHome, name))
    .sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs)[0] || null;
}

function readSqliteThreads(databasePath) {
  try {
    const columns = querySqliteJson(databasePath, "pragma table_info(threads);");
    const names = new Set(columns.map((column) => column.name));
    if (!names.has("id")) throw new Error("threads table does not expose an id column");
    const select = [
      "id",
      names.has("name") ? "name" : "null as name",
      names.has("title") ? "title" : "null as title",
      names.has("recency_at_ms") ? "recency_at_ms" : "null as recency_at_ms",
      names.has("updated_at_ms") ? "updated_at_ms" : "null as updated_at_ms",
      names.has("updated_at") ? "updated_at" : "null as updated_at",
      names.has("archived") ? "archived" : "0 as archived",
      names.has("is_pinned") ? "is_pinned" : "0 as is_pinned",
    ];
    const rows = querySqliteJson(databasePath, `select ${select.join(", ")} from threads where id is not null;`);
    return new Map(rows.map((row, index) => {
      const title = cleanText(row.name || row.title || `Task ${index + 1}`);
      const searchText = cleanText(row.title || row.name || title).slice(0, 1600);
      return [String(row.id), {
        id: String(row.id),
        title,
        searchText,
        updatedAt: timestampToIso(row.recency_at_ms || row.updated_at_ms || row.updated_at),
        archived: Boolean(row.archived),
        pinned: Boolean(row.is_pinned),
        sources: ["app_state_db"],
      }];
    }));
  } catch (error) {
    console.warn(`Warning: app database unavailable (${error.message}); continuing with session_index.jsonl.`);
    return new Map();
  }
}

function querySqliteJson(databasePath, query) {
  const stdout = execFileSync("sqlite3", ["-json", databasePath, query], {
    encoding: "utf8",
    maxBuffer: 32 * 1024 * 1024,
  });
  return JSON.parse(stdout || "[]");
}

function readSessionIndex(filePath) {
  const byId = new Map();
  if (!fs.existsSync(filePath)) return byId;
  for (const line of fs.readFileSync(filePath, "utf8").split(/\r?\n/)) {
    if (!line.trim()) continue;
    try {
      const row = JSON.parse(line);
      if (!row.id) continue;
      const thread = {
        id: String(row.id),
        title: cleanText(row.thread_name || row.title || row.id),
        searchText: cleanText(row.thread_name || row.title || row.id),
        updatedAt: timestampToIso(row.updated_at),
        archived: Boolean(row.archived),
        pinned: Boolean(row.pinned),
        sources: ["session_index"],
      };
      const prior = byId.get(thread.id);
      if (!prior || dateValue(thread.updatedAt) >= dateValue(prior.updatedAt)) byId.set(thread.id, thread);
    } catch {
      // One malformed JSONL row must not invalidate the full local scan.
    }
  }
  return byId;
}

function mergeThread(id, appThread, sessionThread, index) {
  const appDate = dateValue(appThread?.updatedAt);
  const sessionDate = dateValue(sessionThread?.updatedAt);
  return normalizeThread({
    id,
    title: sessionThread?.title || appThread?.title || `Task ${index + 1}`,
    searchText: appThread?.searchText || sessionThread?.searchText || sessionThread?.title || appThread?.title,
    updatedAt: appDate >= sessionDate ? appThread?.updatedAt : sessionThread?.updatedAt,
    archived: appThread?.archived ?? sessionThread?.archived ?? false,
    pinned: appThread?.pinned ?? sessionThread?.pinned ?? false,
    sources: [...new Set([...(sessionThread?.sources || []), ...(appThread?.sources || [])])],
  }, index);
}

function normalizeThread(row, index) {
  return {
    id: String(row.id || `input-${index + 1}`),
    title: cleanText(row.title || row.thread_name || `Task ${index + 1}`),
    searchText: cleanText(row.searchText || row.search_text || row.title || row.thread_name || "").slice(0, 1600),
    updatedAt: timestampToIso(row.updatedAt || row.updated_at),
    archived: Boolean(row.archived),
    pinned: Boolean(row.pinned),
    sources: Array.isArray(row.sources) ? [...new Set(row.sources.map(String))] : ["input"],
  };
}

function timestampToIso(value) {
  if (!value) return null;
  if (typeof value === "number" || /^\d+$/.test(String(value))) {
    let timestamp = Number(value);
    if (timestamp < 1e12) timestamp *= 1000;
    const date = new Date(timestamp);
    return Number.isNaN(date.getTime()) ? null : date.toISOString();
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function dateValue(value) {
  const parsed = Date.parse(value || 0);
  return Number.isNaN(parsed) ? 0 : parsed;
}

function cleanText(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function buildReport(loaded, rubricData, options) {
  const now = new Date();
  const sorted = loaded.threads
    .map((thread) => ({ ...thread, capabilities: classify(thread, rubricData.capabilities) }))
    .sort((a, b) => dateValue(b.updatedAt) - dateValue(a.updatedAt));
  const logIds = new Set(sorted.map((thread) => thread.id));
  const missingIds = [...loaded.expectedIds].filter((id) => !logIds.has(id));
  const appExpected = loaded.source.appDatabaseTasks || 0;
  const appRepresented = sorted.filter((thread) => thread.sources.includes("app_state_db")).length;
  const coverage = {
    complete: missingIds.length === 0 && appRepresented >= appExpected,
    expectedTasks: loaded.expectedIds.size,
    threadLogTasks: sorted.length,
    missingTasks: missingIds.length,
    appDatabaseTasks: appExpected,
    appDatabaseTasksRepresented: appRepresented,
    sessionIndexTasks: loaded.source.sessionIndexTasks || 0,
    archivedTasks: sorted.filter((thread) => thread.archived).length,
  };
  const capabilities = rubricData.capabilities.map((capability) => {
    const matches = sorted.filter((thread) => thread.capabilities.includes(capability.id));
    const recentMatches = matches.filter((thread) => now.getTime() - dateValue(thread.updatedAt) <= 90 * 86400000).length;
    const pct = sorted.length ? round1((matches.length / sorted.length) * 100) : 0;
    const score = scoreCapability(matches.length, pct, recentMatches);
    return {
      id: capability.id,
      label: capability.label,
      mapping: capability.mapping,
      question: capability.question,
      score,
      level: scoreLevel(score),
      threadCount: matches.length,
      threadPct: pct,
      recentThreadCount: recentMatches,
      confidence: matches.length >= 12 ? "high" : matches.length >= 4 ? "medium" : matches.length ? "low" : "none",
      examples: options.redacted ? [] : matches.slice(0, 5).map((thread) => thread.title),
    };
  });
  const averageScore = round1(capabilities.reduce((sum, item) => sum + item.score, 0) / Math.max(1, capabilities.length));
  const priorAverage = Number(options.previous?.summary?.averageScore);
  const delta = Number.isFinite(priorAverage) ? round1(averageScore - priorAverage) : null;
  const displayThreads = sorted.map((thread, index) => options.redacted
    ? {
      title: `Task ${String(index + 1).padStart(3, "0")}`,
      updatedAt: thread.updatedAt,
      archived: thread.archived,
      sources: ["local"],
      capabilities: thread.capabilities,
    }
    : {
      id: thread.id,
      title: thread.title,
      searchText: thread.searchText,
      updatedAt: thread.updatedAt,
      archived: thread.archived,
      sources: thread.sources,
      capabilities: thread.capabilities,
    });

  return {
    meta: {
      generatedAt: now.toISOString(),
      rubricVersion: rubricData.version,
      sourceMode: loaded.source.mode,
      sourceLabel: loaded.source.label,
      redacted: options.redacted,
      includeContext: options.includeContext && !options.redacted,
      timezone: options.timezone,
      limitations: loaded.source.limitations,
    },
    summary: {
      totalTasks: sorted.length,
      classifiedTasks: sorted.filter((thread) => thread.capabilities.length).length,
      unclassifiedTasks: sorted.filter((thread) => !thread.capabilities.length).length,
      activeTasks: sorted.filter((thread) => !thread.archived).length,
      archivedTasks: coverage.archivedTasks,
      averageScore,
      previousAverageScore: Number.isFinite(priorAverage) ? priorAverage : null,
      scoreDelta: delta,
    },
    coverage,
    capabilities,
    threads: displayThreads,
  };
}

function classify(thread, capabilities) {
  const text = `${thread.title} ${thread.searchText}`.toLowerCase();
  return capabilities
    .filter((capability) => capability.keywords.some((keyword) => text.includes(String(keyword).toLowerCase())))
    .map((capability) => capability.id);
}

function scoreCapability(count, pct, recentCount) {
  if (count === 0) return 0;
  let score = 1;
  if (count >= 2) score = 2;
  if (count >= 5 || pct >= 5) score = 3;
  if (count >= 10 && pct >= 10) score = 4;
  if (count >= 20 && pct >= 25 && recentCount >= 3) score = 5;
  return score;
}

function scoreLevel(score) {
  return ["No signal", "Exploring", "Ad hoc", "Operational", "Advanced", "Productized"][score] || "Unknown";
}

function round1(value) {
  return Math.round(Number(value || 0) * 10) / 10;
}

function renderMarkdown(report) {
  const lines = [
    "# Codex Capability Maturity",
    "",
    `Generated: ${report.meta.generatedAt}`,
    `Privacy mode: ${report.meta.redacted ? "redacted" : "private local"}`,
    "",
    "## Summary",
    "",
    `- Average maturity signal: ${report.summary.averageScore} / 5`,
    `- Tasks indexed: ${report.summary.totalTasks}`,
    `- Tasks classified: ${report.summary.classifiedTasks}`,
    `- Tasks unclassified: ${report.summary.unclassifiedTasks}`,
    `- Coverage reconciliation: ${report.coverage.complete ? "complete" : "incomplete"} (${report.coverage.threadLogTasks}/${report.coverage.expectedTasks})`,
    `- Archived tasks included: ${report.coverage.archivedTasks}`,
    "",
    "> This is a heuristic workflow-signal report, not a standardized expertise benchmark.",
    "",
    "## Capability Matrix",
    "",
    "| Capability | Feature mapping | Score | Level | Task signals | Confidence |",
    "| --- | --- | ---: | --- | ---: | --- |",
    ...report.capabilities.map((item) => `| ${item.label} | ${item.mapping} | ${item.score}/5 | ${item.level} | ${item.threadCount} (${item.threadPct}%) | ${item.confidence} |`),
    "",
    "## Latest Tasks",
    "",
    "| Updated | Task | Lifecycle | Capability signals |",
    "| --- | --- | --- | --- |",
    ...report.threads.slice(0, 12).map((thread) => `| ${thread.updatedAt || "unknown"} | ${escapeMarkdown(thread.title)} | ${thread.archived ? "Archived" : "Active"} | ${thread.capabilities.join(", ") || "unclassified"} |`),
    "",
  ];
  return `${lines.join("\n")}\n`;
}

function renderHtml(report) {
  const capabilityOptions = report.capabilities.map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.label)}</option>`).join("");
  const capabilityRows = report.capabilities.map((item) => `
    <tr>
      <td><strong>${escapeHtml(item.label)}</strong><span class="sub">${escapeHtml(item.question)}</span></td>
      <td>${escapeHtml(item.mapping)}</td>
      <td><span class="score score-${item.score}">${item.score}</span></td>
      <td>${escapeHtml(item.level)}</td>
      <td>${item.threadCount} <span class="muted">${item.threadPct}%</span></td>
      <td>${escapeHtml(item.confidence)}</td>
    </tr>`).join("");
  const bars = report.capabilities.map((item) => `
    <div class="bar-row">
      <span>${escapeHtml(item.label)}</span>
      <div class="track"><div class="fill score-bg-${item.score}" style="width:${item.score * 20}%"></div></div>
      <strong>${item.score}.0</strong>
    </div>`).join("");
  const threadRows = report.threads.map((thread) => {
    const classified = thread.capabilities.length ? "classified" : "unclassified";
    const lifecycle = thread.archived ? "archived" : "active";
    const searchText = report.meta.redacted ? thread.title : `${thread.title} ${thread.searchText || ""}`;
    const context = report.meta.includeContext && thread.searchText && thread.searchText !== thread.title
      ? `<span class="sub context">${escapeHtml(truncate(thread.searchText, 180))}</span>`
      : "";
    return `
      <tr data-classification="${classified}" data-lifecycle="${lifecycle}" data-capabilities="${escapeHtml(thread.capabilities.join(" "))}" data-search="${escapeHtml(searchText)}">
        <td>${escapeHtml(formatDate(thread.updatedAt, report.meta.timezone))}</td>
        <td><strong>${escapeHtml(thread.title)}</strong>${context}</td>
        <td><span class="status ${lifecycle}">${lifecycle}</span></td>
        <td>${escapeHtml(thread.capabilities.map(shortCapability).join(", ") || "unclassified")}</td>
      </tr>`;
  }).join("");
  const deltaText = report.summary.scoreDelta === null
    ? "First recorded baseline"
    : `${report.summary.scoreDelta >= 0 ? "+" : ""}${report.summary.scoreDelta} since the previous run`;

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Codex Capability Profiler</title>
  <style>
    :root { --ink:#17202a; --muted:#66717e; --line:#dce2e8; --panel:#f5f7f8; --teal:#087e8b; --green:#26734d; --amber:#b66a16; --coral:#c84d42; --navy:#23354d; }
    * { box-sizing:border-box; }
    html,body { max-width:100%; overflow-x:hidden; }
    body { margin:0; background:#fff; color:var(--ink); font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; letter-spacing:0; }
    header { border-bottom:1px solid var(--line); background:#fff; }
    .topbar { max-width:1180px; margin:0 auto; padding:22px 28px 18px; display:flex; justify-content:space-between; gap:24px; align-items:flex-start; }
    .brand { display:flex; gap:14px; align-items:center; }
    .mark { width:42px; height:42px; display:grid; place-items:center; background:var(--teal); color:#fff; border-radius:7px; font-weight:800; }
    h1 { font-size:24px; margin:0; line-height:1.15; }
    .eyebrow { color:var(--teal); font-size:12px; font-weight:750; text-transform:uppercase; margin-bottom:5px; }
    .privacy { border:1px solid var(--line); background:var(--panel); padding:8px 10px; border-radius:6px; font-size:12px; color:var(--muted); }
    main { max-width:1180px; margin:0 auto; padding:24px 28px 44px; }
    .intro { display:flex; justify-content:space-between; gap:24px; align-items:end; margin-bottom:22px; }
    .intro > div { min-width:0; }
    .intro strong { overflow-wrap:anywhere; }
    .intro p { max-width:720px; margin:7px 0 0; color:var(--muted); line-height:1.5; }
    .timestamp { color:var(--muted); font-size:12px; white-space:nowrap; }
    .metrics { display:grid; grid-template-columns:repeat(5,1fr); border:1px solid var(--line); border-radius:7px; overflow:hidden; margin-bottom:22px; }
    .metric { padding:16px; border-right:1px solid var(--line); min-width:0; }
    .metric:last-child { border-right:0; }
    .metric strong { display:block; font-size:28px; line-height:1; margin-bottom:7px; }
    .metric span { color:var(--muted); font-size:12px; }
    .coverage { border-left:4px solid var(--green); background:#f4faf7; padding:13px 15px; margin-bottom:22px; }
    .coverage strong { font-size:14px; }
    .coverage span { color:var(--muted); font-size:13px; margin-left:8px; }
    .tabs { display:flex; gap:22px; border-bottom:1px solid var(--line); margin-bottom:20px; }
    .tab { border:0; border-bottom:3px solid transparent; background:transparent; padding:10px 1px 9px; color:var(--muted); font:inherit; font-size:13px; font-weight:700; cursor:pointer; }
    .tab[aria-selected="true"] { color:var(--ink); border-color:var(--teal); }
    [hidden] { display:none !important; }
    .overview-grid { display:grid; grid-template-columns:minmax(0,1.12fr) minmax(330px,.88fr); gap:18px; }
    .panel { border:1px solid var(--line); border-radius:7px; padding:17px; background:#fff; }
    .panel h2 { font-size:15px; margin:0 0 14px; }
    .bar-row { display:grid; grid-template-columns:minmax(165px,230px) 1fr 38px; gap:12px; align-items:center; margin:11px 0; font-size:12px; }
    .track { height:10px; background:#e7ecef; overflow:hidden; border-radius:2px; }
    .fill { height:100%; }
    .score-bg-0,.score-bg-1 { background:var(--coral); } .score-bg-2 { background:var(--amber); } .score-bg-3 { background:var(--navy); } .score-bg-4,.score-bg-5 { background:var(--teal); }
    .run-note { display:grid; gap:12px; }
    .run-note div { padding-bottom:12px; border-bottom:1px solid var(--line); }
    .run-note div:last-child { border:0; padding:0; }
    .run-note strong { display:block; font-size:13px; margin-bottom:4px; }
    .run-note span { color:var(--muted); font-size:12px; line-height:1.4; }
    h2.section { font-size:16px; margin:25px 0 12px; }
    table { width:100%; border-collapse:collapse; border:1px solid var(--line); font-size:12px; }
    th,td { padding:10px 11px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
    th { background:var(--panel); color:var(--muted); font-weight:700; }
    .sub { display:block; color:var(--muted); margin-top:4px; font-size:11px; line-height:1.35; max-width:480px; }
    .context { max-width:580px; }
    .score { width:27px; height:27px; border-radius:50%; display:inline-grid; place-items:center; font-weight:800; background:#eaf2f3; color:var(--teal); }
    .score-0,.score-1 { color:var(--coral); background:#fbefed; } .score-2 { color:var(--amber); background:#fff5e8; }
    .muted { color:var(--muted); }
    .controls { display:flex; flex-wrap:wrap; gap:10px; align-items:end; margin-bottom:12px; }
    label { display:grid; gap:5px; color:var(--muted); font-size:11px; font-weight:700; }
    select,input { min-height:35px; border:1px solid var(--line); border-radius:5px; padding:6px 8px; background:#fff; color:var(--ink); font:inherit; font-size:12px; min-width:180px; }
    input { min-width:270px; }
    #log-count { margin-left:auto; color:var(--muted); font-size:12px; }
    .status { display:inline-block; padding:3px 6px; border-radius:4px; font-size:10px; font-weight:750; text-transform:uppercase; }
    .status.active { background:#eaf5ef; color:var(--green); } .status.archived { background:#eef1f4; color:var(--muted); }
    .footnote { margin-top:18px; color:var(--muted); font-size:11px; line-height:1.5; }
    @media (max-width:820px) {
      .topbar,main { padding-left:20px; padding-right:20px; }
      .topbar,.intro { align-items:flex-start; flex-direction:column; }
      .intro > div { width:100%; }
      .metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
      .metric { border-bottom:1px solid var(--line); }
      .coverage span { display:block; margin:5px 0 0; }
      .overview-grid { grid-template-columns:1fr; }
      .bar-row { grid-template-columns:minmax(0,1fr) 84px 30px; gap:8px; }
      table { display:block; overflow:auto; }
    }
  </style>
</head>
<body>
  <header><div class="topbar"><div class="brand"><div class="mark">CP</div><div><div class="eyebrow">Local workflow intelligence</div><h1>Codex Capability Profiler</h1></div></div><div class="privacy">${report.meta.redacted ? "Redacted shareable report" : "Private local report"}</div></div></header>
  <main>
    <section class="intro"><div><strong>Capability maturity, grounded in observable task signals.</strong><p>Maps recurring Codex workflows to ten capability areas. Scores are heuristic and designed for longitudinal self-review, not cross-user ranking.</p></div><span class="timestamp">Generated ${escapeHtml(formatDate(report.meta.generatedAt, report.meta.timezone))}</span></section>
    <section class="metrics">
      <div class="metric"><strong>${report.summary.averageScore}</strong><span>Average signal / 5</span></div>
      <div class="metric"><strong>${report.summary.totalTasks}</strong><span>Tasks indexed</span></div>
      <div class="metric"><strong>${report.summary.classifiedTasks}</strong><span>Classified tasks</span></div>
      <div class="metric"><strong>${report.summary.unclassifiedTasks}</strong><span>Review queue</span></div>
      <div class="metric"><strong>${report.coverage.archivedTasks}</strong><span>Archived included</span></div>
    </section>
    <section class="coverage"><strong>${report.coverage.complete ? "Complete source reconciliation" : "Coverage gap detected"}</strong><span>${report.coverage.threadLogTasks} of ${report.coverage.expectedTasks} indexed task IDs are represented in the log.</span></section>
    <nav class="tabs" role="tablist"><button class="tab" role="tab" aria-selected="true" aria-controls="overview">Overview</button><button class="tab" role="tab" aria-selected="false" aria-controls="thread-log">Thread Log</button></nav>
    <section id="overview" role="tabpanel">
      <div class="overview-grid">
        <section class="panel"><h2>Capability profile</h2>${bars}</section>
        <section class="panel"><h2>Run context</h2><div class="run-note"><div><strong>${escapeHtml(deltaText)}</strong><span>Repeat the same rubric to make trend comparisons meaningful.</span></div><div><strong>${report.summary.activeTasks} active, ${report.summary.archivedTasks} archived</strong><span>Archived tasks remain included in maturity evidence and can be filtered in the log.</span></div><div><strong>${escapeHtml(report.meta.sourceLabel)}</strong><span>${escapeHtml(report.meta.limitations.join(" "))}</span></div></div></section>
      </div>
      <h2 class="section">Capability matrix</h2>
      <table><thead><tr><th>Capability</th><th>Mapping</th><th>Score</th><th>Level</th><th>Signals</th><th>Confidence</th></tr></thead><tbody>${capabilityRows}</tbody></table>
    </section>
    <section id="thread-log" role="tabpanel" hidden>
      <div class="controls">
        <label>Classification<select id="classification-filter"><option value="all">All tasks</option><option value="classified">Classified</option><option value="unclassified">Unclassified</option></select></label>
        <label>Lifecycle<select id="lifecycle-filter"><option value="all">All states</option><option value="active">Active</option><option value="archived">Archived</option></select></label>
        <label>Capability<select id="capability-filter"><option value="all">All capabilities</option>${capabilityOptions}</select></label>
        <label>Search<input id="task-search" type="search" placeholder="Search tasks and local context"></label>
        <span id="log-count"></span>
      </div>
      <table id="thread-table"><thead><tr><th>Updated</th><th>Task</th><th>Lifecycle</th><th>Capability signals</th></tr></thead><tbody>${threadRows}</tbody></table>
    </section>
    <p class="footnote">Coverage means every task exposed by the selected local source reached this report. Classification remains keyword-based evidence and should be reviewed before publication or comparison.</p>
  </main>
  <script>
    const tabs = [...document.querySelectorAll('[role="tab"]')];
    for (const tab of tabs) tab.addEventListener('click', () => {
      for (const item of tabs) item.setAttribute('aria-selected', String(item === tab));
      for (const panel of document.querySelectorAll('[role="tabpanel"]')) panel.hidden = panel.id !== tab.getAttribute('aria-controls');
    });
    const classification = document.getElementById('classification-filter');
    const lifecycle = document.getElementById('lifecycle-filter');
    const capability = document.getElementById('capability-filter');
    const search = document.getElementById('task-search');
    const count = document.getElementById('log-count');
    const rows = [...document.querySelectorAll('#thread-table tbody tr')];
    function filterRows() {
      const query = search.value.trim().toLowerCase();
      let visible = 0;
      for (const row of rows) {
        const show = (classification.value === 'all' || row.dataset.classification === classification.value)
          && (lifecycle.value === 'all' || row.dataset.lifecycle === lifecycle.value)
          && (capability.value === 'all' || row.dataset.capabilities.split(' ').includes(capability.value))
          && (!query || row.dataset.search.toLowerCase().includes(query));
        row.hidden = !show;
        if (show) visible += 1;
      }
      count.textContent = visible + ' / ' + rows.length + ' tasks';
    }
    for (const control of [classification, lifecycle, capability, search]) control.addEventListener(control === search ? 'input' : 'change', filterRows);
    filterRows();
  </script>
</body>
</html>`;
}

function shortCapability(value) {
  return value.replace(/_/g, " ");
}

function truncate(value, limit) {
  const text = cleanText(value);
  return text.length > limit ? `${text.slice(0, limit - 3)}...` : text;
}

function formatDate(value, timezone) {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  try {
    return date.toLocaleString("en-GB", {
      timeZone: timezone,
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  } catch {
    return date.toISOString();
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeMarkdown(value) {
  return String(value ?? "").replace(/\|/g, "\\|").replace(/\r?\n/g, " ");
}
