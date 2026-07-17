---
name: opencut-producer
description: Turn local video, audio, optional B-roll, and a plain-English editorial brief into multiple isolated OpenCut edit candidates with smart music ducking, transitions, title cards, styled captions, an opaque review session, and a human-approved local render. Use when Codex is asked to find highlights in interviews, talks, podcasts, webinars, meetings, or other local video files; produce polished short clips; arrange several generated clips; add B-roll, music, subtitles, intros, outros, or lower thirds; create aspect-ratio variants; handle very large source videos; launch the OpenCut candidate review UI; or continue a previously created OpenCut review session.
---

# OpenCut Producer

Create candidate edits automatically, but keep selection, preview rendering, final rendering, and publishing under explicit human control.

Read these references as needed:

- `references/editorial-workflow.md` for candidate diversity, transcription, captions, and large-file handling.
- `references/review-session-contract.md` before writing plans or `review-session.json`.

## Inputs and defaults

Collect or infer:

- source video path;
- editorial goal or topic;
- candidate count, default `3`;
- target duration, default `30–90 seconds`;
- target aspect ratio, default source ratio;
- caption preference, default enabled;
- production finish, default `polished` with clean transitions, styled captions, and speech-aware music ducking when a music asset exists;
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

Prefer local transcription when available. If transcription sends audio to an external service:

1. Explain which extracted audio will leave the device and which service will receive it.
2. Obtain explicit consent before the first upload.
3. Extract bounded audio chunks locally; never upload the source MP4 or video frames unless separately authorized.
4. Preserve timestamp offsets when combining chunk transcripts.

Skip transcription only when reliable timed text already exists or the requested edit can be made from supplied timestamps.

## 3. Generate differentiated candidates

Create candidates with distinct editorial intent, not trivial timestamp variations. For three candidates, default to:

1. **Hook-first:** strongest opening and fastest payoff.
2. **Concise core:** cleanest self-contained explanation.
3. **Context-rich:** enough setup to preserve meaning and speaker intent.

For every candidate:

- verify that speech starts and ends cleanly;
- avoid materially misleading cuts;
- keep source ranges within probed duration;
- map captions onto output-timeline time, not absolute source time;
- write an isolated `edit-plan.json` and unique output path;
- add a short title and decision-useful summary.

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
title, and caption treatment. The current UI edits the primary A-roll and
displays the complete production summary; the compiled preview is the review
artifact for the read-only secondary layers and styling.

## 7. Preserve the human gate

- Candidate selection is not render approval.
- Review edits must be saved as a new numbered revision; never silently mutate an approved plan.
- A fast preview applies only to the exact revision that produced it. Any later edit invalidates it.
- Never call the preview or final-approval endpoints or reuse the action token on the user's behalf.
- Preview rendering must begin from the visible **Render preview** action.
- Final rendering must begin from the separate visible **Approve final** action, after the reviewer inspects the current preview.
- Never upload or publish a rendered clip as part of this skill.
- Treat publishing as a separate workflow with destination-specific approval.

## 8. Verify the result

After the UI reports completion:

1. Confirm the selected candidate status is `rendered`, and that the audit history contains preview and final-render events for the approved revision.
2. Inspect `opencut.project.json` and `approved-edit-plan.json` inside that candidate directory.
3. Confirm the project record contains the candidate revision, plan hash, source hashes, creating agent/model when supplied, and the latest reviewer note.
4. Run FFprobe on the MP4 and report duration, resolution, codecs, subtitle stream, and size.
5. For v2, verify overlay timing/placement, mixed audio inputs, ducking, transitions, title cards, and caption styling in the compiled graph and rendered preview.
6. Preserve all non-selected candidates for later comparison unless the user asks to remove them.
7. Report exact output paths and any transcription or rendering limitations.

## Failure handling

- If the bridge cannot bind locally, retry with the required loopback permission; do not weaken the host binding.
- If a source lies outside the configured root, choose a safe common root or ask before making a large copy.
- If output already exists, restore the rendered state rather than overwriting it.
- If candidate quality is weak, revise the editorial evidence and create a new candidate ID; do not silently mutate an approved plan.
- If native OpenCut APIs are unavailable, describe the current bridge as an FFmpeg-backed adapter, not the future OpenCut Editor API.
