# Skill Release Checklist

Skill: `sarvam-meeting-minutes`

Date: 2026-08-04

## Scope

- Recurring task: transcribe local meeting recordings with Sarvam Saaras and turn diarized transcripts into structured meeting minutes.
- Expected user/community: Codex users processing Indian-language, English, Telugu, Hindi, regional-language, or code-mixed calls, interviews, webinars, and meeting recordings.
- Explicitly not for: bypassing consent/privacy review, storing API keys in skill files, speaker identity claims from diarization alone, or guaranteed legal/compliance records.

## Files

- [x] `SKILL.md`
- [x] `agents/openai.yaml`
- [x] `references/` files, if needed
- [x] scripts/assets, if needed

## Validation

- [x] `quick_validate.py` passes
- [x] Manual read-through completed
- [x] Tested against a realistic workspace
- [x] Known limitations documented

## Publishing

- [x] README link added
- [x] No secrets or private paths
- [x] Install instructions checked
- [ ] GitHub description/topics updated

## Validation Notes

- Created and installed a local `sarvam-meeting-minutes` skill.
- Installed the official `sarvamai` SDK in a workspace virtualenv for live testing.
- Ran Sarvam batch transcription with automatic language detection, `mode=codemix`, and diarization on two `.m4a` meeting recordings.
- Confirmed both output JSON transcript files downloaded successfully.
- Generated an evidence-backed meeting minutes artifact from the diarized transcript.
- Fixed a helper metadata serialization issue discovered during the live test.
- API keys were loaded from `.env` and were not printed or committed.
