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
  "updatedAt": "2026-01-01T00:00:00.000Z"
}
```

Candidate status is one of:

- `ready-for-review`
- `selected`
- `previewing`
- `preview-ready`
- `rendering`
- `rendered`
- `failed`

Omit `selectedCandidateId` until the human selects a candidate.

## Candidate edit plan

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
3. Compare candidates and preview source ranges.
4. Select a candidate; this only updates manifest state.
5. Adjust ranges, ordering, speed, volume, or caption inclusion and save a numbered revision.
6. Render and inspect the fast preview for that exact revision.
7. Approve the final render separately; this writes the approved plan, hashes, project record, and high-quality output.
8. Restore the same selection, revision, notes, preview, audit, and rendered state after refresh.

Session IDs and approval tokens are process-local. The manifest and candidate outputs are durable.
