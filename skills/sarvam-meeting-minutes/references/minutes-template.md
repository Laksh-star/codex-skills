# Professional Meeting Minutes Template

Use this structure for polished minutes from Sarvam transcripts. The actual meeting minutes should stay with the user's output folder; this reusable template belongs in the skill.

The final deliverable should read like professional internal meeting notes, not like a transcription report. Keep Sarvam/transcript details in provenance unless the user asks for audit-first minutes.

```markdown
# Meeting Minutes: <title>

## Executive Summary

<2-4 concise paragraphs. Explain the central purpose of the meeting, what changed, why it matters, and what requires follow-up. Do not merely list topics.>

## Key Outcomes

- <Outcome, framed as a result or alignment point>

## Decisions

| Decision | Owner | Notes |
| --- | --- | --- |
| <decision> | <owner or Not stated> | <short context, dependency, or evidence if needed> |

## Action Register

| Priority | Action | Owner | Timing |
| --- | --- | --- | --- |
| <High/Medium/Low> | <specific next step> | <owner or Unassigned> | <date, next step, or Not stated> |

## Discussion Summary

### <Theme 1>

<Synthesize the discussion. Consolidate repeated points. Do not expose raw diarization labels unless needed for a caveat.>

### <Theme 2>

<Synthesize the discussion.>

## Open Questions

- <question>

## Suggested Next Agenda

1. <next meeting item>

## Provenance Notes

- Recordings: <recording paths or filenames>
- Transcript files: <paths>
- Transcription: Sarvam Saaras <version>, mode=<mode>, language=<auto or code>, diarization=<yes/no>
- Speaker context: <user-confirmed attendees/count, context-derived attendees, or unconfirmed>
- Transcript caveats: <language, diarization, timestamp, overlap, or audio-quality notes>
```

## Style Rules

- Write for a professional internal audience.
- Lead with synthesis and implications, then provide supporting detail.
- Merge duplicated discussion across recording parts.
- Do not assign real speaker names from diarization unless the user provides a mapping.
- Do not infer actual speaker count from diarization labels alone.
- When user-confirmed speaker count conflicts with diarization labels, use the user-confirmed count in the main minutes and note diarization over-splitting in provenance.
- Use `Not stated` or `Unassigned` instead of guessing owners, dates, or decisions.
- Keep transcript quality caveats at the end unless they affect a decision or action.
