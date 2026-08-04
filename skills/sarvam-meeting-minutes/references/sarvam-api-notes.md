# Sarvam API Notes

Use Sarvam Saaras v3 for new speech-to-text integrations.

## Endpoint Choice

- Meeting recordings: use Batch Speech-to-Text through the Sarvam Python SDK.
- Short clips under the REST limit: direct `/speech-to-text` REST calls are possible, but this skill defaults to batch for consistency.
- Legacy `/speech-to-text-translate` with `saaras:v2.5` is not the preferred new path. Use `/speech-to-text` with `model="saaras:v3"` and `mode="translate"` for English translation.

## Saaras v3 Modes

- `transcribe`: same-language transcript.
- `translate`: transcript translated to English.
- `verbatim`: includes fillers and repetitions when a more literal record matters.
- `translit`: Romanized output.
- `codemix`: natural code-mixed output for mixed-language conversations.

## Batch Defaults

- Use `with_diarization=True` for meetings unless the user does not want speaker labels.
- Use `num_speakers` only when the user knows the expected number of speakers; otherwise omit it.
- Poll until completion and download successful output files.
- Treat failed file-level results as transcript gaps; report the failure details in the minutes provenance.

## Privacy

Sarvam processing sends the recording to an external API. Confirm user intent before sending sensitive recordings if the instruction is ambiguous. Never log API keys.
