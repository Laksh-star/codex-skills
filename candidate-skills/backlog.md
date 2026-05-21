# Candidate Skills Backlog

These are local or project-derived skills that may be worth publishing later. They are not listed under `skills/` because they have not been cleaned, reviewed, and validated for public reuse in this repo.

## Promotion Standard

A candidate can move into `skills/` only after it:

- has valid skill frontmatter and `agents/openai.yaml`
- has no secrets, private paths, or machine-specific assumptions
- has clear install/setup expectations
- has a narrow, reusable trigger description
- has been validated with `quick_validate.py`
- has been tested against at least one realistic workspace or task

## Candidates

| Candidate | Local source observed | Why it may be useful | Cleanup needed before publishing |
| --- | --- | --- | --- |
| `cfo-triage-lite` | `/Users/ln-mini/Downloads/files_cfo/5-fuse-triage/skill` | Financial distress triage workflow for SMEs. | Review branding, add financial disclaimers, remove non-public positioning, and confirm it is appropriate for public release. |
| `content-creator` | `/Users/ln-mini/Documents/New project/content-creator` | General research-to-video production workflow with formats, sourcing, composition, and review loops. | Audit VideoDB/API dependencies, simplify public setup, remove project-specific assumptions, and decide whether bundled references are too large. |
| `financial-news-video-agent` | `/Users/ln-mini/Documents/New project/financial-market-analysis/skills/financial-news-video-agent` | Proof-first financial news recap video workflow using articles, screenshots, charts, and selected clips. | Add finance/news disclaimers, verify source-citation rules, document required video tooling, and remove local run-folder assumptions. |
| `cinema-management-video-agent` | `/Users/ln-mini/Documents/New project/cinema-management` | Turns indexed film scenes into management training videos. | Review rights/content assumptions, Twelve Labs and VideoDB setup, example index IDs, and whether this belongs in a public generic skills repo. |
| `news-digest-video-agent` | `/Users/ln-mini/Documents/New project/news-digest` | Multi-source news digest video workflow using real clips, tweets, articles, narration, and overlays. | Audit browser/video dependencies, remove bundled media if rights are unclear, add source-verification rules, and simplify setup. |

## Current Decision

Do not publish these as validated skills yet. Treat them as candidates for a separate cleanup pass, one at a time.
