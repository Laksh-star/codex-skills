# Review Session Contract

## Directory layout

All paths are relative to `OPENCUT_AGENT_ROOT`.

```text
opencut-projects/interview-highlights/
├── review-session.json
├── captions/
│   ├── hook-first.srt
│   ├── concise-core.srt
│   └── context-rich.srt
└── candidates/
    ├── hook-first/
    │   └── edit-plan.json
    ├── concise-core/
    │   └── edit-plan.json
    └── context-rich/
        └── edit-plan.json
```

The source may live elsewhere under the same root. Do not place large media in the OpenCut code repository.

## Session manifest

```json
{
  "version": "1",
  "id": "interview-highlights",
  "title": "Choose an interview highlight",
  "sourceAssets": [
    {
      "id": "source",
      "label": "Original interview",
      "path": "source-video.mp4"
    }
  ],
  "candidates": [
    {
      "id": "hook-first",
      "title": "Hook-first",
      "summary": "Fast opening and immediate payoff",
      "strategy": "distinct-moment",
      "rationale": "Chosen as a separate source moment with the strongest opening line and fastest payoff.",
      "clipRationales": [
        {
          "clipId": "opening",
          "note": "Starts after the setup and ends before the speaker changes topic."
        }
      ],
      "planPath": "opencut-projects/interview-highlights/candidates/hook-first/edit-plan.json",
      "revision": 1,
      "status": "ready-for-review"
    },
    {
      "id": "concise-core",
      "title": "Concise core",
      "summary": "Shortest self-contained explanation",
      "planPath": "opencut-projects/interview-highlights/candidates/concise-core/edit-plan.json",
      "status": "ready-for-review"
    },
    {
      "id": "context-rich",
      "title": "Context-rich",
      "summary": "More setup and speaker context",
      "planPath": "opencut-projects/interview-highlights/candidates/context-rich/edit-plan.json",
      "status": "ready-for-review"
    }
  ],
  "reviewerNotes": [],
  "events": [],
  "renderBatches": [],
  "exportPackages": [],
  "updatedAt": "2026-01-01T00:00:00.000Z"
}
```

Candidate status is one of:

- `ready-for-review`
- `selected`
- `previewing`
- `preview-ready`
- `queued`
- `rendering`
- `rendered`
- `failed`

Omit `selectedCandidateId` until the human selects a candidate.

Candidate `strategy` is optional for older sessions and should be one of:

- `distinct-moment` for separate candidate clips from different source moments;
- `narrative-segment` for one longer idea intentionally split into hook/body/payoff sections;
- `social-variant` for the same moment in a different format, style, aspect ratio, or preset;
- `archive-summary` for context-preserving reference clips;
- `manual` for reviewer-created candidates.

New generated sessions should include `strategy`, `rationale`, and
`clipRationales`. Every `clipRationales[].clipId` must reference a real primary
`timeline.clips[].id` in that candidate's plan.

`renderBatches` is optional for a fresh session and should normally start as
`[]`. The bridge appends entries after an explicit **Approve batch** action:

```json
{
  "id": "00000000-0000-4000-8000-000000000000",
  "status": "completed",
  "requestedAt": "2026-01-01T00:00:00.000Z",
  "completedAt": "2026-01-01T00:02:00.000Z",
  "items": [
    {
      "candidateId": "hook-first",
      "revision": 1,
      "status": "rendered",
      "outputPath": "opencut-projects/interview-highlights/candidates/hook-first/renders/output.mp4"
    }
  ]
}
```

Batch status is one of `queued`, `rendering`, `completed`, `partial`, or
`failed`. Batch item status is one of `queued`, `rendering`, `rendered`, or
`failed`. Agents should not pre-populate batch entries; they are reviewer action
records.

`exportPackages` is optional for a fresh session and should normally start as
`[]`. The bridge appends entries after a local export package is created for
rendered candidates:

```json
{
  "id": "00000000-0000-4000-8000-000000000001",
  "version": "1",
  "reviewSessionId": "interview-highlights",
  "title": "Choose an interview highlight",
  "status": "created",
  "createdAt": "2026-01-01T00:03:00.000Z",
  "packagePath": "opencut-projects/interview-highlights/exports/2026-01-01T00-03-00-000Z-00000000",
  "manifestPath": "opencut-projects/interview-highlights/exports/2026-01-01T00-03-00-000Z-00000000/manifest.json",
  "summaryPath": "opencut-projects/interview-highlights/exports/2026-01-01T00-03-00-000Z-00000000/summary.md",
  "candidates": [
    {
      "candidateId": "hook-first",
      "revision": 1,
      "title": "Hook-first",
      "durationSeconds": 44.5,
      "outputPath": "opencut-projects/interview-highlights/candidates/hook-first/renders/output.mp4",
      "packagedOutputPath": "opencut-projects/interview-highlights/exports/2026-01-01T00-03-00-000Z-00000000/media/hook-first-output.mp4",
      "outputBytes": 1234567,
      "approvedEditPlanPath": "opencut-projects/interview-highlights/exports/2026-01-01T00-03-00-000Z-00000000/records/hook-first-approved-edit-plan.json",
      "projectRecordPath": "opencut-projects/interview-highlights/exports/2026-01-01T00-03-00-000Z-00000000/records/hook-first-opencut.project.json",
      "captionsPath": "opencut-projects/interview-highlights/exports/2026-01-01T00-03-00-000Z-00000000/captions/hook-first-hook-first.srt",
      "contactSheetPath": "opencut-projects/interview-highlights/exports/2026-01-01T00-03-00-000Z-00000000/contact-sheets/hook-first.jpg"
    }
  ],
  "warnings": []
}
```

Export package status is `created` or `partial`. A `partial` package means the
rendered MP4 was copied but optional metadata or contact-sheet generation
reported warnings. Export packages must not include the original source video.

## Candidate edit plan

Use version 1 for sequential A-roll-only candidates:

```json
{
  "version": "1",
  "project": {
    "name": "Interview highlight — hook-first",
    "width": 1920,
    "height": 1080,
    "frameRate": 30,
    "background": "#000000"
  },
  "assets": [
    {
      "id": "source",
      "path": "source-video.mp4",
      "kind": "video"
    },
    {
      "id": "captions",
      "path": "opencut-projects/interview-highlights/captions/hook-first.srt",
      "kind": "captions"
    }
  ],
  "timeline": {
    "clips": [
      {
        "id": "opening",
        "assetId": "source",
        "sourceStart": 120.5,
        "sourceEnd": 165.0,
        "speed": 1,
        "volume": 1,
        "includeAudio": true
      }
    ],
    "captionsAssetId": "captions"
  },
  "output": {
    "path": "opencut-projects/interview-highlights/candidates/hook-first/renders/output.mp4",
    "overwrite": false
  }
}
```

Use version 2 when the candidate has overlapping video or independent audio.
Version 2 retains `timeline.clips` as the primary A-roll and adds:

```json
{
  "version": "2",
  "project": {
    "name": "Layered highlight",
    "width": 1920,
    "height": 1080,
    "frameRate": 30,
    "background": "#000000"
  },
  "assets": [
    { "id": "source", "path": "source-video.mp4", "kind": "video" },
    { "id": "b-roll", "path": "b-roll.mp4", "kind": "video" },
    { "id": "music", "path": "music.wav", "kind": "audio" },
    { "id": "captions", "path": "captions/layered.srt", "kind": "captions" }
  ],
  "timeline": {
    "clips": [
      { "id": "a-roll-1", "assetId": "source", "sourceStart": 120.5, "sourceEnd": 142 },
      { "id": "a-roll-2", "assetId": "source", "sourceStart": 142, "sourceEnd": 165 }
    ],
    "overlayTracks": [
      {
        "id": "b-roll-track",
        "zIndex": 2,
        "clips": [
          {
            "id": "b-roll-1",
            "assetId": "b-roll",
            "timelineStart": 5,
            "sourceStart": 0,
            "sourceEnd": 4,
            "x": 1280,
            "y": 32,
            "width": 608,
            "height": 342,
            "opacity": 0.9,
            "fit": "cover",
            "includeAudio": false
          }
        ]
      }
    ],
    "audioTracks": [
      {
        "id": "music-track",
        "role": "music",
        "clips": [
          {
            "id": "music-bed",
            "assetId": "music",
            "timelineStart": 0,
            "sourceStart": 0,
            "sourceEnd": 44.5,
            "volume": 0.15
          }
        ]
      }
    ],
    "transitions": [
      {
        "id": "answer-fade",
        "fromClipId": "a-roll-1",
        "toClipId": "a-roll-2",
        "type": "fade",
        "duration": 0.4
      }
    ],
    "titleCards": [
      {
        "id": "intro",
        "template": "intro",
        "timelineStart": 0,
        "duration": 1.5,
        "title": "The central idea",
        "subtitle": "Interview highlight"
      },
      {
        "id": "speaker",
        "template": "lower-third",
        "timelineStart": 2,
        "duration": 2.5,
        "title": "Speaker name"
      }
    ],
    "captionsAssetId": "captions",
    "captionStyle": {
      "mode": "both",
      "preset": "bold",
      "marginV": 48
    },
    "audioMix": {
      "ducking": {
        "enabled": true,
        "threshold": 0.04,
        "ratio": 8,
        "attackMs": 20,
        "releaseMs": 250
      }
    }
  },
  "output": {
    "path": "opencut-projects/interview-highlights/candidates/layered/renders/output.mp4",
    "overwrite": false
  }
}
```

Overlay tracks are composed in ascending `zIndex`. Clips on one overlay track
must not overlap, but clips on different tracks may. Every overlay must fit
inside the project canvas. Audio-track assets may be `audio` or `video`; their
audio is delayed to `timelineStart` and mixed with the primary track. Mark
music beds with `role: "music"`; an enabled ducking block targets all music-role
tracks unless `targetTrackIds` is explicit. The primary dialogue drives a
sidechain compressor, so effects and voiceover remain unchanged by default.

Transitions must connect adjacent primary clips and be shorter than both
clips. Supported types are `fade`, `wipeleft`, `wiperight`, `slideleft`, and
`slideright`. Title templates are `intro`, `outro`, and `lower-third`. Styled
burn-in requires SRT captions; mode `both` also preserves a selectable
`mov_text` stream. Available presets are `clean`, `bold`, and `minimal`.

## Isolation rule

For candidate plan:

```text
opencut-projects/<project>/candidates/<candidate>/edit-plan.json
```

the project portion of `output.path` must be:

```text
opencut-projects/<project>/candidates/<candidate>/
```

The normal output is `renders/output.mp4`. Shared output directories are invalid.

Each candidate also owns immutable `revisions/revision-N.edit-plan.json`
snapshots and revision-specific `renders/preview-rN.mp4` previews. Saving an edit
increments `revision` and clears its previous preview relationship. Final
approval is valid only when `lastPreviewRevision` equals the current `revision`
and that preview file exists.

## Review lifecycle

1. Register `review-session.json` with the local bridge.
2. Open the opaque `?session=<id>` URL.
3. Compare candidates, preview source ranges, and inspect the v2 overlay/audio, transition, title-card, ducking, and caption summary.
4. Select a candidate; this only updates manifest state.
5. Adjust ranges, ordering, speed, volume, or caption inclusion and save a numbered revision.
6. Render and inspect the fast preview for that exact revision.
7. Approve the final render separately; this writes the approved plan, hashes, project record, and high-quality output.
8. Restore the same selection, revision, notes, preview, audit, and rendered state after refresh.

Session IDs and approval tokens are process-local. The manifest and candidate outputs are durable.
