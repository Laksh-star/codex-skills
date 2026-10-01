#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const builder = path.join(path.dirname(fileURLToPath(import.meta.url)), 'build-capability-report.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'profiler-regression-'));
let passed = 0;
const input = path.join(tmp, 'source.json');
const markers = ['PRIVATE_SOURCE_SENTINEL', 'PRIVATE_TITLE_SENTINEL', 'PRIVATE_CONTEXT_SENTINEL', 'PRIVATE_ID_SENTINEL', 'PRIVATE_PATH_SENTINEL'];
fs.writeFileSync(input, JSON.stringify({source: markers[0], threads: [
  {id: markers[3], title: markers[1], searchText: `${markers[2]} /${markers[4]}/subagents`, updatedAt: '2025-01-02T03:04:05Z', archived: true},
  {id: 'synthetic-2', title: 'Build tests', searchText: '<script>window.INJECTED=true</script>'},
]}));

function run(args, ok = true, env = process.env) {
  const result = spawnSync(process.execPath, [builder, ...args], {encoding: 'utf8', env});
  assert.equal(result.status === 0, ok, result.stderr || result.stdout);
  return result;
}
function report(dir) { return JSON.parse(fs.readFileSync(path.join(dir, 'report.json'), 'utf8')); }
function contents(dir) { return ['json','md','html'].map(ext => fs.readFileSync(path.join(dir, `report.${ext}`), 'utf8')).join('\n'); }
function check(name, test) { test(); passed += 1; console.log(`PASS ${name}`); }

try {
  const privateDir = path.join(tmp, 'private');
  run(['--input', input, '--out', privateDir]);
  check('default mode omits request context from every output', () => {
    assert(!contents(privateDir).includes(markers[2]));
    assert(!report(privateDir).threads.some(t => 'searchText' in t));
    assert.equal(report(privateDir).threads.find(t => t.id === markers[3]).capabilities.length, 0);
  });
  const contextDir = path.join(tmp, 'context');
  run(['--input', input, '--out', contextDir, '--include-context']);
  check('explicit context mode retains evidence and changes classification', () => {
    assert(contents(contextDir).includes(markers[2]));
    assert(report(contextDir).threads.find(t => t.id === markers[3]).capabilities.length > 0);
    assert(!fs.readFileSync(path.join(contextDir,'report.html'),'utf8').includes('<script>window.INJECTED'));
  });
  const redactedDir = path.join(tmp, 'redacted');
  run(['--input', input, '--out', redactedDir, '--redacted', '--include-context']);
  check('redacted JSON Markdown HTML and DOM remove identifying evidence', () => {
    const text = contents(redactedDir);
    for (const marker of markers) assert(!text.includes(marker), marker);
    assert(!text.includes('2025-01-02'));
    assert(report(redactedDir).threads.every(t => !('id' in t) && !('searchText' in t) && t.updatedAt === null));
    assert.equal(report(redactedDir).summary.totalTasks, 2);
  });
  check('switching privacy modes cannot overwrite the other report', () => {
    const before = contents(privateDir);
    run(['--input', input, '--out', privateDir, '--redacted'], false);
    assert.equal(contents(privateDir), before);
  });
  check('source input cannot be overwritten by output', () => {
    const dir = path.join(tmp, 'overwrite'); fs.mkdirSync(dir);
    const src = path.join(dir, 'report.json'); fs.copyFileSync(input, src);
    const before = fs.readFileSync(src,'utf8');
    run(['--input', src, '--out', dir], false);
    assert.equal(fs.readFileSync(src,'utf8'), before);
  });
  check('duplicate IDs empty inputs and malformed rows fail clearly', () => {
    for (const payload of [[], null, [{id:'same'},{id:'same'}], [null]]) {
      const src = path.join(tmp,'bad.json'); fs.writeFileSync(src,JSON.stringify(payload));
      run(['--input',src,'--out',path.join(tmp,'bad-out')],false);
    }
    assert(!fs.existsSync(path.join(tmp,'bad-out','report.json')));
  });
  check('database failure is distinguished from successful ID reconciliation', () => {
    const home = path.join(tmp,'fallback'); fs.mkdirSync(home);
    fs.writeFileSync(path.join(home,'state_99.sqlite'),'invalid database');
    fs.writeFileSync(path.join(home,'session_index.jsonl'),JSON.stringify({id:'index-1',thread_name:'Build tests'})+'\nnot json\n');
    const dir = path.join(tmp,'fallback-report');
    run(['--codex-home',home,'--out',dir]);
    const r=report(dir); assert(r.coverage.complete); assert.equal(r.meta.sourceScope,'reduced-local');
    assert(r.meta.sourceWarnings.length >= 2); assert(contents(dir).includes('Reduced source coverage'));
  });
  check('missing SQLite uses the index without claiming database coverage', () => {
    const dir=path.join(tmp,'no-sqlite-report');
    run(['--codex-home',path.join(tmp,'fallback'),'--out',dir],true,{...process.env,PATH:tmp});
    assert.equal(report(dir).meta.sourceScope,'reduced-local');
    assert.equal(report(dir).coverage.appDatabaseTasks,0);
  });
  check('empty local source stops instead of producing a zero-task success', () => {
    run(['--codex-home',path.join(tmp,'missing-home'),'--out',path.join(tmp,'missing-report')],false);
  });
  check('untrusted markup is inert in HTML and Markdown titles', () => {
    const src=path.join(tmp,'hostile.json');
    fs.writeFileSync(src,JSON.stringify([{id:'hostile',title:'<script>window.INJECTED=true</script> | title'}]));
    const dir=path.join(tmp,'hostile-report');run(['--input',src,'--out',dir]);
    for(const ext of ['html','md']) assert(!fs.readFileSync(path.join(dir,`report.${ext}`),'utf8').includes('<script>window.INJECTED'));
  });
  check('trend resets when the rubric or evidence mode changes', () => {
    run(['--input',input,'--out',contextDir]);
    assert.equal(report(contextDir).summary.scoreDelta,null);
    run(['--input',input,'--out',contextDir]);
    assert.equal(report(contextDir).summary.scoreDelta,0);
  });
  const sqlite = spawnSync('sqlite3',['--version'],{encoding:'utf8'});
  if(sqlite.status===0) check('SQLite and index IDs reconcile including archived tasks without altering the database', () => {
    const home=path.join(tmp,'sqlite-home');fs.mkdirSync(home);const db=path.join(home,'state_1.sqlite');
    const setup=spawnSync('sqlite3',[db,"create table threads(id text,title text,archived integer,updated_at integer); insert into threads values('db-1','Build tests',1,1700000000); insert into threads values('both','Review memory',0,1700000001);"],{encoding:'utf8'});assert.equal(setup.status,0);
    fs.writeFileSync(path.join(home,'session_index.jsonl'),[JSON.stringify({id:'both',thread_name:'Review memory'}),JSON.stringify({id:'index-1',thread_name:'Build release'})].join('\n'));
    const before=fs.readFileSync(db);const dir=path.join(tmp,'sqlite-report');run(['--codex-home',home,'--out',dir]);
    assert.deepEqual(fs.readFileSync(db),before);const r=report(dir);assert.equal(r.summary.totalTasks,3);assert.equal(r.coverage.appDatabaseTasksRepresented,2);assert.equal(r.coverage.archivedTasks,1);assert.equal(r.meta.sourceScope,'local-sources');
  });
  console.log(`${passed} release behavior checks passed.`);
} finally { fs.rmSync(tmp,{recursive:true,force:true}); }
