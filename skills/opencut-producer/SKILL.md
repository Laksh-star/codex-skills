---
name: opencut-producer
description: Turn local video, audio, optional B-roll, and a plain-English editorial brief into multiple isolated OpenCut edit candidates with smart music ducking, transitions, title cards, styled captions, editable production controls, production presets, preflight checks, opaque review sessions, human-approved single or batch local renders, and local export packages. Use when Codex is asked to find highlights in interviews, talks, podcasts, webinars, meetings, or other local video files; produce polished short clips; arrange several generated clips; add B-roll, music, subtitles, intros, outros, or lower thirds; create aspect-ratio variants; handle very large source videos; launch the OpenCut candidate review UI; batch-render approved candidates; package rendered outputs for handoff; or continue a previously created OpenCut review session.
---

# OpenCut Producer

Create candidate edits automatically, but keep selection, preview rendering, single final rendering, batch final rendering, export packaging, and publishing under explicit human control.

Read these references as needed:

- `references/editorial-workflow.md` for candidate diversity, transcription, captions, and large-file handling.
- `references/review-session-contract.md` before writing plans or `review-session.json`.

## Inputs and defaults

Collect or infer:

- source video path;
- editorial goal or topic;
- candidate count, default `3` distinct source moments;
- target duration, default `30–90 seconds`;
- target aspect ratio, default source ratio;
- caption preference, default enabled;
- transcription provider preference, default local Whisper when available; otherwise ask before using OpenAI API, OpenRouter, or any other external service;
- production finish, default `polished` with clean transitions, styled captions, and speech-aware music ducking when a music asset exists;
- production preset, default `clean-interview` for interviews/talks, `bold-social` for short social clips, and `minimal-archive` for archival/reference clips;
- optional B-roll/video overlays and independent audio assets;
- OpenCut checkout path, if it cannot be discovered locally.

Do not stop for optional choices. State sensible defaults and proceed. Ask only when the source is missing, the requested outcome materially conflicts with the source, or external transcription needs consent.

## 1. Establish the local boundary

1. Resolve the source with `realpath` and inspect size and media metadata with FFprobe or `opencut_inspect_media`.
2. Locate an OpenCut checkout containing:
   - `apps/agent-bridge/bin/opencut-review`
   - `apps/agent-bridge/bin/opencut-agent-http`
3. Choose the smallest existing directory that contains both the source and the project output as `OPENCUT_AGENT_ROOT`.
   - Normally use the source file's parent and create `opencut-projects/<project-slug>/` beneath it.
   - Do not copy a multi-gigabyte source merely to satisfy the root boundary.
   - Do not scan, expose, or reference unrelated sibling files.
4. Keep source media and generated artifacts outside the OpenCut source repository.
5. Confirm FFmpeg, FFprobe, the repo-pinned Bun executable, and web dependencies exist. Install only when the user has authorized dependency changes.
6. Run the bridge setup packager once for the chosen root:

```bash
/absolute/path/to/OpenCut/apps/agent-bridge/bin/opencut-setup \
  --root "/absolute/path/to/agent-root"
```

Reuse its generated `.opencut-agent/setup.json` and `codex-mcp.toml`; do not recreate configuration by hand or edit the user's global Codex config silently.

## 2. Transcribe safely

Prefer local transcription when available. Support these provider modes and record
which one was used in the handoff notes:

- `local-whisper`: first choice when a local model/runtime is already available;
- `openai-api`: use only after explicit upload consent;
- `openrouter`: use only after explicit upload consent and model selection;
- `provided-captions`: use when a trusted SRT/VTT or timed transcript already exists.

If transcription sends audio to an external service:

1. Explain which extracted audio will leave the device and which service will receive it.
2. Obtain explicit consent before the first upload.
3. Extract bounded audio chunks locally; never upload the source MP4 or video frames unless separately authorized.
4. Preserve timestamp offsets when combining chunk transcripts.

Skip transcription only when reliable timed text already exists or the requested edit can be made from supplied timestamps.

## 3. Generate differentiated candidates

Create candidates with distinct editorial intent and usually distinct source
moments, not trivial timestamp variations and not one long clip split into
hook/body/close unless the user explicitly requests a single narrative clip.
For three candidates, default to:

1. **Hook-first:** strongest opening and fastest payoff.
2. **Concise core:** cleanest self-contained explanation.
3. **Context-rich:** enough setup to preserve meaning and speaker intent.

Use the `strategy` metadata to make this explicit:

- `distinct-moment`: default for separate candidate clips from different source moments;
- `narrative-segment`: use only when one longer idea is intentionally split into hook/body/payoff sections;
- `social-variant`: same editorial moment, different style/aspect/preset;
- `archive-summary`: more context and less aggressive social editing;
- `manual`: reviewer-supplied or manually adjusted candidate.

For every candidate:

- verify that speech starts and ends cleanly;
- avoid materially misleading cuts;
- keep source ranges within probed duration;
- map captions onto output-timeline time, not absolute source time;
- write an isolated `edit-plan.json` and unique output path;
- add a short title and decision-useful summary;
- add `strategy`, `rationale`, and `clipRationales` in `review-session.json`;
- make `rationale` explain why this candidate exists and how it differs from the other candidates;
- make every `clipRationales[].clipId` reference a real primary `timeline.clips[].id`.

Use plan version `1` for a strictly sequential single-source edit with only a
selectable caption track. Use version `2` when the user supplies or requests
B-roll, picture-in-picture, independent music/audio, transitions, title cards,
or burned-in styling. Keep
the main story in `timeline.clips`; place visual layers in `overlayTracks` and
secondary audio in `audioTracks`. Never fake an asset that was not supplied or
authorized.

For a polished v2 candidate:

- mark music tracks with `role: "music"` and enable `audioMix.ducking` so primary speech drives `sidechaincompress`;
- use one restrained transition only at a real adjacent clip boundary;
- use `intro`, `outro`, or `lower-third` title cards only when they add orientation or identity;
- prefer `captionStyle.mode: "both"` so the visual treatment is burned in while an accessible selectable subtitle stream remains;
- keep all generated title/caption graphics under the bridge-managed `.opencut-agent/render-assets/` directory.

Follow `references/editorial-workflow.md` for scoring and caption rules.

## 4. Build the review session

Use the directory and JSON contracts in `references/review-session-contract.md`.

Required structure:

```text
<project>/
├── review-session.json
├── captions/
└── candidates/
    ├── hook-first/edit-plan.json
    ├── concise-core/edit-plan.json
    └── context-rich/edit-plan.json
```

Each plan must render inside its own candidate directory:

```text
candidates/<candidate-id>/renders/output.mp4
```

Set every new candidate to `ready-for-review`, revision `1`, with empty reviewer-note and event arrays. Record the creating agent/model when known, but never store credentials or full prompts. Do not preselect a candidate unless the user already made an explicit choice.

## 5. Validate before launch

When OpenCut MCP tools are available:

1. Call `opencut_capabilities`.
2. Inspect the source with `opencut_inspect_media`.
3. Validate every plan with `opencut_validate_edit_plan`.
4. Use `opencut_upgrade_edit_plan` when an existing v1 candidate needs v2 layers.
5. Compile every v2 plan and inspect the returned `overlay`, `amix`, `sidechaincompress`, `xfade`, and `acrossfade` graph before saving it.
6. Save plans only inside the chosen root.
7. When available, use `opencut_preflight_review_session` as a read-only check for saved review sessions before preview, final, batch, or export actions. Treat `block` results as blocking and report `warn` results plainly.

Always run the bundled session validator, resolving its path relative to this `SKILL.md`:

```bash
python3 <opencut-producer-skill>/scripts/validate_session.py \
  /absolute/path/to/review-session.json \
  --root /absolute/path/to/agent-root
```

Treat any shared output directory, missing asset, escaping path, duplicate ID, or invalid duration as blocking.

## 6. Launch OpenCut review

Start the launcher in a retained terminal session:

```bash
OPENCUT_AGENT_ROOT="/absolute/path/to/agent-root" \
  /absolute/path/to/OpenCut/apps/agent-bridge/bin/opencut-review \
  /absolute/path/to/agent-root/opencut-projects/<project>/review-session.json
```

Return or open the printed `?session=<opaque-id>` URL. The browser should stream the local source through HTTP byte ranges; never ask the user to select the same large video again.

Keep the launcher alive while the user reviews candidates. If the bridge restarts, register the manifest again and use the new opaque URL; selection and rendered state remain in the manifest.

For v2 plans, make the candidate summary name the B-roll, music, transition,
title, caption treatment, and production preset. Make the candidate rationale
state whether the choice is a distinct moment or a format/style variant. The
current UI edits the primary A-roll plus existing overlay, audio, transition,
title-card, caption-style, and ducking fields, can apply coordinated production
presets, and includes a WYSIWYG preview-monitor surface for existing visual
layers. Reviewers can drag/resize/nudge overlay and title boxes and drag
burned-in captions between safe top/middle/bottom placement zones. The compiled
preview remains the approval artifact for the exact saved revision; the
WYSIWYG surface is an editing aid, not final-render approval.

## 7. Preserve the human gate

- Candidate selection is not render approval.
- Batch selection is not render approval.
- Review edits must be saved as a new numbered revision; never silently mutate an approved plan.
- A fast preview applies only to the exact revision that produced it. Any later edit invalidates it.
- Never call the preview or final-approval endpoints or reuse the action token on the user's behalf.
- Preview rendering must begin from the visible **Render preview** action.
- Final rendering must begin from the separate visible **Approve final** action, after the reviewer inspects the current preview.
- Batch rendering must begin from the separate visible **Approve batch** action, and only for candidates whose current revision already has a preview.
- Export packaging must happen only after candidates are rendered and only when the user asked for a handoff/package or the workflow requires final delivery artifacts.
- Never upload or publish a rendered clip as part of this skill.
- Treat publishing as a separate workflow with destination-specific approval.

## 8. Verify the result

After the UI reports completion:

1. Confirm the selected or batch-approved candidate status is `rendered`, and that the audit history contains preview and final-render events for the approved revision.
2. For a batch, confirm the latest `renderBatches` entry is `completed`; if it is `partial` or `failed`, report the failed candidate IDs and do not hide successful outputs.
3. Inspect `opencut.project.json` and `approved-edit-plan.json` inside every rendered candidate directory.
4. Confirm each project record contains the candidate revision, plan hash, source hashes, creating agent/model when supplied, and the latest reviewer note.
5. Run FFprobe on each MP4 and report duration, resolution, codecs, subtitle stream, and size.
6. For v2, verify overlay timing/placement, mixed audio inputs, ducking, transitions, title cards, and caption styling in the compiled graph and rendered preview.
7. If a local handoff is requested, create or confirm an export package with rendered MP4 copies, approved plans, project records, captions, contact sheets when available, `manifest.json`, and `summary.md`; never copy the original source video into the package.
8. Preserve all non-selected candidates for later comparison unless the user asks to remove them.
9. Report exact output paths, export package paths, and any transcription, preflight, packaging, or rendering limitations.

## Failure handling

- If the bridge cannot bind locally, retry with the required loopback permission; do not weaken the host binding.
- If a source lies outside the configured root, choose a safe common root or ask before making a large copy.
- If output already exists, restore the rendered state rather than overwriting it.
- If candidate quality is weak, revise the editorial evidence and create a new candidate ID; do not silently mutate an approved plan.
- If the user expected three different clips but the candidates are one clip split into parts, create a fresh session with `distinct-moment` candidates unless the user confirms they wanted a single narrative segmentation.
- If native OpenCut APIs are unavailable, describe the current bridge as an FFmpeg-backed adapter, not the future OpenCut Editor API.
