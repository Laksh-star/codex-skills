#!/usr/bin/env python3
"""Validate an OpenCut review-session manifest without modifying it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath


VALID_STATUSES = {
    "ready-for-review",
    "selected",
    "previewing",
    "preview-ready",
    "rendering",
    "rendered",
    "failed",
}


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing JSON file: {path}")
    except json.JSONDecodeError as error:
        fail(f"Invalid JSON in {path}: {error}")
    if not isinstance(value, dict):
        fail(f"Expected an object in {path}")
    return value


def resolve_inside(root: Path, requested: str, *, must_exist: bool = True) -> Path:
    relative = PurePosixPath(requested)
    if relative.is_absolute() or ".." in relative.parts:
        fail(f"Path must be relative and cannot traverse parents: {requested}")
    candidate = (root / Path(*relative.parts)).resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError:
        fail(f"Path escapes the configured root: {requested}")
    if must_exist and not candidate.is_file():
        fail(f"Missing file: {requested}")
    return candidate


def project_directory(output_path: str) -> PurePosixPath:
    output = PurePosixPath(output_path)
    parent = output.parent
    return parent.parent if parent.name == "renders" else parent


def validate_timed_clip(candidate_id: str, clip: object, asset_ids: set[str], clip_ids: set[str]) -> float:
    if not isinstance(clip, dict):
        fail(f"Candidate {candidate_id} has an invalid clip")
    clip_id = clip.get("id")
    asset_id = clip.get("assetId")
    start = clip.get("sourceStart")
    end = clip.get("sourceEnd")
    speed = clip.get("speed", 1)
    if not isinstance(clip_id, str) or not clip_id:
        fail(f"Candidate {candidate_id} has a clip without id")
    if clip_id in clip_ids:
        fail(f"Candidate {candidate_id} has duplicate clip id {clip_id}")
    if asset_id not in asset_ids:
        fail(f"Candidate {candidate_id} clip {clip_id} references unknown asset")
    if not all(isinstance(value, (int, float)) for value in (start, end, speed)):
        fail(f"Candidate {candidate_id} clip {clip_id} has invalid timing")
    if start < 0 or end <= start or speed <= 0:
        fail(f"Candidate {candidate_id} clip {clip_id} has invalid range or speed")
    clip_ids.add(clip_id)
    return (end - start) / speed


def validate(manifest_path: Path, root: Path) -> dict:
    manifest = load_json(manifest_path)
    if manifest.get("version") != "1":
        fail("review-session.json version must be '1'")

    sources = manifest.get("sourceAssets")
    candidates = manifest.get("candidates")
    if not isinstance(sources, list) or not sources:
        fail("sourceAssets must be a non-empty array")
    if not isinstance(candidates, list) or not candidates:
        fail("candidates must be a non-empty array")

    source_ids: set[str] = set()
    source_sizes: dict[str, int] = {}
    for source in sources:
        source_id = source.get("id") if isinstance(source, dict) else None
        source_path = source.get("path") if isinstance(source, dict) else None
        if not isinstance(source_id, str) or not source_id:
            fail("Every source asset needs a non-empty id")
        if source_id in source_ids:
            fail(f"Duplicate source asset id: {source_id}")
        if not isinstance(source_path, str) or not source_path:
            fail(f"Source asset {source_id} needs a path")
        resolved = resolve_inside(root, source_path)
        source_ids.add(source_id)
        source_sizes[source_id] = resolved.stat().st_size

    candidate_ids: set[str] = set()
    summaries: list[dict] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            fail("Every candidate must be an object")
        candidate_id = candidate.get("id")
        plan_path_text = candidate.get("planPath")
        status = candidate.get("status", "ready-for-review")
        if not isinstance(candidate_id, str) or not candidate_id:
            fail("Every candidate needs a non-empty id")
        if candidate_id in candidate_ids:
            fail(f"Duplicate candidate id: {candidate_id}")
        if status not in VALID_STATUSES:
            fail(f"Invalid status for {candidate_id}: {status}")
        if not isinstance(plan_path_text, str) or not plan_path_text:
            fail(f"Candidate {candidate_id} needs planPath")

        plan_path = resolve_inside(root, plan_path_text)
        plan = load_json(plan_path)
        plan_version = plan.get("version")
        if plan_version not in {"1", "2"}:
            fail(f"Candidate {candidate_id} plan version must be '1' or '2'")
        output = plan.get("output")
        output_path = output.get("path") if isinstance(output, dict) else None
        if not isinstance(output_path, str) or not output_path.endswith(".mp4"):
            fail(f"Candidate {candidate_id} output must be an MP4 path")
        resolve_inside(root, output_path, must_exist=False)
        plan_parent = PurePosixPath(plan_path_text).parent
        if project_directory(output_path) != plan_parent:
            fail(
                f"Candidate {candidate_id} must render inside {plan_parent}; "
                f"got {project_directory(output_path)}"
            )

        assets = plan.get("assets")
        timeline = plan.get("timeline")
        clips = timeline.get("clips") if isinstance(timeline, dict) else None
        if not isinstance(assets, list) or not assets:
            fail(f"Candidate {candidate_id} needs assets")
        if not isinstance(clips, list) or not clips:
            fail(f"Candidate {candidate_id} needs timeline clips")

        asset_ids: set[str] = set()
        asset_kinds: dict[str, str] = {}
        for asset in assets:
            asset_id = asset.get("id") if isinstance(asset, dict) else None
            asset_path = asset.get("path") if isinstance(asset, dict) else None
            asset_kind = asset.get("kind") if isinstance(asset, dict) else None
            if not isinstance(asset_id, str) or not asset_id:
                fail(f"Candidate {candidate_id} has an asset without id")
            if asset_id in asset_ids:
                fail(f"Candidate {candidate_id} has duplicate asset id {asset_id}")
            if not isinstance(asset_path, str) or not asset_path:
                fail(f"Candidate {candidate_id} asset {asset_id} needs a path")
            if asset_kind not in {"video", "audio", "captions"}:
                fail(f"Candidate {candidate_id} asset {asset_id} has invalid kind")
            resolve_inside(root, asset_path)
            asset_ids.add(asset_id)
            asset_kinds[asset_id] = asset_kind

        clip_ids: set[str] = set()
        primary_duration = 0.0
        for clip in clips:
            duration = validate_timed_clip(candidate_id, clip, asset_ids, clip_ids)
            if asset_kinds.get(clip["assetId"]) != "video":
                fail(f"Candidate {candidate_id} primary clip {clip['id']} must use video")
            primary_duration += duration

        duration = primary_duration
        layer_duration = 0.0
        overlay_count = 0
        audio_count = 0
        transition_count = 0
        title_count = 0
        burned_captions = False
        ducking_enabled = False
        if plan_version == "2":
            overlay_tracks = timeline.get("overlayTracks", [])
            audio_tracks = timeline.get("audioTracks", [])
            if not isinstance(overlay_tracks, list) or not isinstance(audio_tracks, list):
                fail(f"Candidate {candidate_id} v2 tracks must be arrays")
            track_ids: set[str] = set()
            music_track_ids: set[str] = set()
            for track_kind, tracks in (("overlay", overlay_tracks), ("audio", audio_tracks)):
                for track in tracks:
                    track_id = track.get("id") if isinstance(track, dict) else None
                    track_clips = track.get("clips") if isinstance(track, dict) else None
                    if not isinstance(track_id, str) or not track_id or track_id in track_ids:
                        fail(f"Candidate {candidate_id} has an invalid or duplicate track id")
                    if not isinstance(track_clips, list) or not track_clips:
                        fail(f"Candidate {candidate_id} track {track_id} needs clips")
                    track_ids.add(track_id)
                    if track_kind == "audio":
                        role = track.get("role", "effects")
                        if role not in {"music", "effects", "voiceover"}:
                            fail(f"Candidate {candidate_id} audio track {track_id} has invalid role")
                        if role == "music":
                            music_track_ids.add(track_id)
                    for clip in track_clips:
                        clip_duration = validate_timed_clip(candidate_id, clip, asset_ids, clip_ids)
                        timeline_start = clip.get("timelineStart")
                        if not isinstance(timeline_start, (int, float)) or timeline_start < 0:
                            fail(f"Candidate {candidate_id} clip {clip.get('id')} needs timelineStart")
                        asset_kind = asset_kinds.get(clip["assetId"])
                        if track_kind == "overlay" and asset_kind != "video":
                            fail(f"Candidate {candidate_id} overlay clip {clip['id']} must use video")
                        if track_kind == "audio" and asset_kind not in {"audio", "video"}:
                            fail(f"Candidate {candidate_id} audio clip {clip['id']} must use audio or video")
                        layer_duration = max(layer_duration, timeline_start + clip_duration)
                        overlay_count += track_kind == "overlay"
                        audio_count += track_kind == "audio"

            transitions = timeline.get("transitions", [])
            if not isinstance(transitions, list):
                fail(f"Candidate {candidate_id} transitions must be an array")
            clip_indexes = {clip["id"]: index for index, clip in enumerate(clips)}
            transition_boundaries: set[tuple[str, str]] = set()
            transition_total = 0.0
            for transition in transitions:
                if not isinstance(transition, dict):
                    fail(f"Candidate {candidate_id} has an invalid transition")
                from_id = transition.get("fromClipId")
                to_id = transition.get("toClipId")
                transition_duration = transition.get("duration", 0.5)
                if from_id not in clip_indexes or clip_indexes.get(to_id) != clip_indexes[from_id] + 1:
                    fail(f"Candidate {candidate_id} transition must connect adjacent primary clips")
                boundary = (from_id, to_id)
                if boundary in transition_boundaries:
                    fail(f"Candidate {candidate_id} has duplicate transition boundary {from_id}->{to_id}")
                if not isinstance(transition_duration, (int, float)) or transition_duration < 0.1:
                    fail(f"Candidate {candidate_id} transition has invalid duration")
                transition_boundaries.add(boundary)
                transition_total += transition_duration
                transition_count += 1

            duration = max(primary_duration - transition_total, layer_duration)

            title_cards = timeline.get("titleCards", [])
            if not isinstance(title_cards, list):
                fail(f"Candidate {candidate_id} titleCards must be an array")
            for card in title_cards:
                if not isinstance(card, dict) or not isinstance(card.get("title"), str):
                    fail(f"Candidate {candidate_id} has an invalid title card")
                start = card.get("timelineStart")
                card_duration = card.get("duration")
                if not isinstance(start, (int, float)) or not isinstance(card_duration, (int, float)) or start < 0 or card_duration < 0.5:
                    fail(f"Candidate {candidate_id} title card has invalid timing")
                duration = max(duration, start + card_duration)
                title_count += 1

            caption_style = timeline.get("captionStyle")
            if caption_style is not None:
                if not isinstance(caption_style, dict) or not timeline.get("captionsAssetId"):
                    fail(f"Candidate {candidate_id} captionStyle requires captionsAssetId")
                mode = caption_style.get("mode", "burn-in")
                if mode not in {"selectable", "burn-in", "both"}:
                    fail(f"Candidate {candidate_id} has invalid caption mode")
                burned_captions = mode in {"burn-in", "both"}

            ducking = timeline.get("audioMix", {}).get("ducking") if isinstance(timeline.get("audioMix", {}), dict) else None
            if isinstance(ducking, dict) and ducking.get("enabled", True):
                targets = ducking.get("targetTrackIds", [])
                if not isinstance(targets, list) or any(target not in track_ids for target in targets):
                    fail(f"Candidate {candidate_id} ducking references an unknown track")
                if not targets and not music_track_ids:
                    fail(f"Candidate {candidate_id} ducking needs a music-role or explicit target track")
                ducking_enabled = True

        candidate_ids.add(candidate_id)
        summaries.append(
            {
                "id": candidate_id,
                "status": status,
                "planVersion": plan_version,
                "primaryClips": len(clips),
                "overlayClips": overlay_count,
                "audioClips": audio_count,
                "transitions": transition_count,
                "titleCards": title_count,
                "burnedCaptions": burned_captions,
                "smartDucking": ducking_enabled,
                "durationSeconds": round(duration, 3),
                "outputPath": output_path,
            }
        )

    selected = manifest.get("selectedCandidateId")
    if selected is not None and selected not in candidate_ids:
        fail(f"selectedCandidateId references unknown candidate: {selected}")

    return {
        "ok": True,
        "manifest": str(manifest_path),
        "root": str(root),
        "sourceBytes": source_sizes,
        "selectedCandidateId": selected,
        "candidates": summaries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, help="OPENCUT_AGENT_ROOT")
    arguments = parser.parse_args()

    manifest = arguments.manifest.expanduser().resolve()
    root = (arguments.root or manifest.parent).expanduser().resolve()
    try:
        manifest.relative_to(root)
        result = validate(manifest, root)
    except ValueError as error:
        print(json.dumps({"ok": False, "error": str(error)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
