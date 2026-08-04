---
name: sarvam-meeting-minutes
description: Transcribe meeting recordings with Sarvam AI speech models and turn the transcript into structured meeting minutes. Use when Codex needs to process local audio or video recordings, especially Indian-language, English, Hindi, regional-language, or code-mixed meetings, interviews, calls, webinars, or voice notes; run Sarvam Saaras transcription/translation, preserve speaker/timestamp evidence, and draft decisions, action items, owners, risks, and follow-ups.
---

# Sarvam Meeting Minutes

## Core Workflow

1. Confirm the recording path, desired output language, and whether the user wants same-language transcription (`transcribe`), English translation (`translate`), natural code-mixed output (`codemix`), word-for-word transcript (`verbatim`), or Romanized output (`translit`). Omit `--language-code` unless the user explicitly wants a manual language hint; Sarvam performs automatic language detection by default.
2. Never print or persist the Sarvam API key. Prefer `SARVAM_API_KEY` in the shell environment.
3. Use `scripts/sarvam_transcribe.py` for meeting-length recordings. It uses Sarvam's Python SDK, batch speech-to-text jobs, Saaras v3, optional diarization, polling, and output download.
4. Inspect the downloaded JSON/text outputs before drafting minutes. Preserve uncertainty when diarization is missing, speaker labels are generic, or audio quality appears poor.
5. Draft minutes from transcript evidence and user-provided context, not from unsupported inference. Include short timestamp references when they help accountability, but keep them out of the main narrative when they make the output feel like a transcript artifact.
6. Save transcript and minutes beside the user's chosen output directory unless they ask for a different destination.

## Quick Commands

Install the SDK only if it is missing:

```bash
python3 -m pip install -U sarvamai
```

Run transcription for a typical meeting:

```bash
python3 /path/to/sarvam-meeting-minutes/scripts/sarvam_transcribe.py \
  --audio /path/to/meeting.mp3 \
  --out-dir /path/to/output \
  --mode transcribe \
  --diarization \
  --num-speakers 4
```

Translate Indic-language audio to English:

```bash
python3 /path/to/sarvam-meeting-minutes/scripts/sarvam_transcribe.py \
  --audio /path/to/meeting.m4a \
  --out-dir /path/to/output \
  --mode translate \
  --diarization
```

Use `--dry-run` first when checking setup without sending audio to Sarvam.

## Minutes Format

Produce a professional Markdown artifact. Prefer synthesis over transcript-shaped notes:

- Title and executive summary first; put source recordings, transcript provenance, Sarvam mode/model, language setting, and diarization status in a final provenance section unless the user asks for audit-first notes.
- Executive summary: 2-4 paragraphs that explain what changed, why it matters, and what needs follow-up.
- Key outcomes: 5-8 bullets capturing substantive outcomes, not every discussed topic.
- Discussion notes: grouped by theme, with repeated or overlapping recording segments consolidated.
- Decisions: table with decision, owner, and concise notes. Include evidence only when it is important for accountability.
- Action register: table with priority, owner, action, due date, and notes.
- Risks/watch items and open questions.
- Suggested follow-up agenda when the conversation implies another meeting.
- Provenance/transcript notes at the end.

Avoid making the output sound like a raw checklist. Hide transcription machinery from the main body, normalize speaker labels only from user-provided or reliable meeting context, and keep the main narrative polished and readable.

## Quality Rules

- For recordings longer than short clips, prefer Batch API through the helper script.
- Use `translate` only when the user wants English minutes from non-English audio. Use `transcribe` or `codemix` when retaining original language and code-mixing is important.
- Do not claim speaker names from diarization alone. Diarization identifies speaker turns, not identities.
- Do not infer actual speaker count from diarization labels alone. If the user confirms speaker count or attendee names, use that context; otherwise say the speaker count is unconfirmed. If diarization over-splits a two-person meeting into `speaker_id` values such as `0`, `1`, `2`, or `3`, state that in transcript notes and use neutral participant labels in the main minutes.
- Note gaps explicitly: missing audio sections, failed files, low-confidence passages, no timestamps, no diarization, or incomplete polling/downloads.
- If the user provides multiple recordings from the same meeting, process all files and merge minutes chronologically when timestamps or filenames make order clear.

## References

- Read `references/sarvam-api-notes.md` when choosing Sarvam endpoint/mode details or handling longer batch jobs.
- Read `references/minutes-template.md` when drafting the final minutes artifact.
