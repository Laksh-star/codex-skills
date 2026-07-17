# Skill Release Checklist

Skill: `opencut-producer`

Date: 2026-07-17

## Scope

- Recurring task: turn a local interview, talk, podcast, webinar, meeting, or other video plus an editorial brief into differentiated OpenCut candidates, captions, an opaque review session, and a human-approved local render.
- Expected users: Codex users and video-workflow builders who want agent assistance without giving up visible selection and approval gates.
- Explicitly not for: silent approval, social publishing, remote media hosting, claiming the FFmpeg adapter is OpenCut's future native Editor API, or uploading source video without separate authorization.

## Files

- [x] `SKILL.md`
- [x] `agents/openai.yaml`
- [x] `references/editorial-workflow.md`
- [x] `references/review-session-contract.md`
- [x] `scripts/validate_session.py`

No assets are required.

## Validation

- [x] `quick_validate.py` passes
- [x] Manual read-through completed
- [x] Tested against a realistic workspace
- [x] Known limitations documented

Realistic validation uses the generated-video, two-candidate OpenCut browser fixture from the candidate-review implementation. The validator must accept its source, isolated plans, rendered status, and selected candidate. A deliberately shared output path is also tested and must fail.

Known limitations:

- Requires a compatible OpenCut checkout with the agent bridge and review-session launcher.
- Requires FFmpeg and FFprobe for media work.
- Transcription quality and external-service availability depend on the user's environment and consent.
- The current renderer supports the version-1 sequential edit-plan contract, not the full future OpenCut Editor API.

## Publishing

- [x] README link added
- [x] No secrets or private paths
- [x] Install instructions checked
- [x] GitHub description/topics updated

No GitHub description or topic changes are required for this incremental skill addition.
