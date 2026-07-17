# Editorial Workflow

## Candidate design

Make candidate differences legible to a human reviewer.

| Candidate | Optimize for | Avoid |
| --- | --- | --- |
| Hook-first | Immediate curiosity and fast payoff | A dramatic opener with missing context |
| Concise core | Self-contained clarity | Choppy sentence boundaries |
| Context-rich | Accuracy, setup, and speaker intent | Slow or redundant preamble |

When the user requests a different number of candidates, preserve diversity:

- `1`: strongest balanced edit;
- `2`: concise versus contextual;
- `3`: hook-first, concise core, context-rich;
- `4+`: add a distinct theme, audience, duration, or aspect-ratio treatment rather than near-duplicates.

Score each candidate privately on:

1. relevance to the brief;
2. opening strength;
3. self-contained meaning;
4. clean source boundaries;
5. factual and tonal fidelity;
6. duration fit.

Do not expose invented numeric confidence as objective truth. Use the score only to improve candidate diversity and summaries.

## Transcription

- Probe media before extraction.
- Use compact audio chunks when an external service has size or duration limits.
- Record each chunk's source offset.
- Merge transcript timestamps back into source time.
- Re-transcribe promising boundaries at finer resolution when coarse timestamps could clip words.
- Keep raw and cleaned transcript text distinguishable.
- Never claim word-level accuracy unless the transcription result actually provides it.

## Source selection

- Start after breath/noise when possible without cutting the first phoneme.
- End after the semantic conclusion and natural cadence.
- Prefer complete clauses.
- Avoid cuts that alter the speaker's meaning.
- Keep small contextual bridges when a pronoun or claim would otherwise become ambiguous.
- Use multiple clips only when the join is editorially coherent.

## Captions

- Convert source timestamps to output-timeline timestamps after trims and speed changes.
- Keep cues readable, normally one or two lines.
- Correct obvious transcription artifacts without rewriting the speaker's meaning.
- Use SRT or VTT; the current renderer muxes captions into MP4 as a selectable subtitle track.
- Verify the final caption cue does not extend beyond the rendered duration.

## Large local videos

- Do not load the full media file into model context.
- Do not base64-encode the source.
- Do not repeatedly copy or reattach a multi-gigabyte file.
- Let OpenCut serve authorized media with HTTP byte ranges from the loopback bridge.
- Keep `OPENCUT_AGENT_ROOT` as narrow as practical and reference only the source named by the user.

## Revision policy

Preserve provenance:

- never mutate `approved-edit-plan.json`;
- create a new candidate ID for a materially different revision;
- use titles and summaries that explain the tradeoff;
- keep rejected candidates until the user explicitly asks to clean them up.
