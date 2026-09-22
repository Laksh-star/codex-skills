#!/usr/bin/env bash
set -euo pipefail

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

node --check "$skill_dir/scripts/build-capability-report.mjs"
node "$skill_dir/scripts/build-capability-report.mjs" --input "$skill_dir/assets/sample-threads.json" --out "$tmp_dir/private"
node "$skill_dir/scripts/build-capability-report.mjs" --input "$skill_dir/assets/sample-threads.json" --out "$tmp_dir/redacted" --redacted

node - "$tmp_dir" <<'NODE'
const fs = require("node:fs");
const path = require("node:path");
const root = process.argv[2];
const privateReport = JSON.parse(fs.readFileSync(path.join(root, "private", "report.json"), "utf8"));
const redactedJson = fs.readFileSync(path.join(root, "redacted", "report.json"), "utf8");
const redactedHtml = fs.readFileSync(path.join(root, "redacted", "report.html"), "utf8");

if (!privateReport.coverage.complete) throw new Error("fixture coverage audit failed");
if (privateReport.summary.totalTasks !== 24) throw new Error("unexpected fixture task count");
if (!privateReport.threads.some((thread) => thread.title === "Build release verification workflow")) throw new Error("expected fixture task missing");
if (redactedJson.includes("Build release verification workflow") || redactedHtml.includes("Build release verification workflow")) throw new Error("redacted output leaked a fixture title");
if (!redactedJson.includes("Task 001")) throw new Error("redacted task labels missing");
console.log("Capability profiler smoke test passed.");
NODE
