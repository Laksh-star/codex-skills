#!/usr/bin/env python3
"""Transcribe meeting recordings with Sarvam batch speech-to-text."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


VALID_MODES = {"transcribe", "translate", "verbatim", "translit", "codemix"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a Sarvam Saaras v3 batch speech-to-text job and download outputs."
    )
    parser.add_argument(
        "--audio",
        action="append",
        required=True,
        help="Audio/video recording path. Repeat for multiple files.",
    )
    parser.add_argument("--out-dir", required=True, help="Directory for Sarvam outputs.")
    parser.add_argument("--mode", default="transcribe", choices=sorted(VALID_MODES))
    parser.add_argument("--language-code", default=None, help="Optional BCP-47 code, e.g. en-IN or hi-IN.")
    parser.add_argument("--api-key-env", default="SARVAM_API_KEY")
    parser.add_argument("--model", default="saaras:v3")
    parser.add_argument("--diarization", action="store_true", help="Request speaker diarization.")
    parser.add_argument("--num-speakers", type=int, default=None, help="Expected speaker count.")
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--dry-run", action="store_true", help="Validate arguments without API calls.")
    return parser.parse_args()


def fail(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def json_safe(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return json_safe(value.model_dump(mode="json"))
    if hasattr(value, "dict"):
        return json_safe(value.dict())
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return value


def main() -> None:
    args = parse_args()
    audio_paths = [Path(path).expanduser().resolve() for path in args.audio]
    missing = [str(path) for path in audio_paths if not path.is_file()]
    if missing:
        fail("missing audio file(s): " + ", ".join(missing))

    out_dir = Path(args.out_dir).expanduser().resolve()
    plan = {
        "audio": [str(path) for path in audio_paths],
        "out_dir": str(out_dir),
        "model": args.model,
        "mode": args.mode,
        "language_code": args.language_code,
        "diarization": args.diarization,
        "num_speakers": args.num_speakers,
        "poll_interval": args.poll_interval,
        "timeout": args.timeout,
    }

    if args.dry_run:
        print(json.dumps({"dry_run": True, **plan}, indent=2, ensure_ascii=False))
        return

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        fail(f"set {args.api_key_env} before running")

    try:
        from sarvamai import SarvamAI
    except ImportError:
        fail("missing dependency: run `python3 -m pip install -U sarvamai`")

    out_dir.mkdir(parents=True, exist_ok=True)
    client = SarvamAI(api_subscription_key=api_key)

    kwargs: dict[str, Any] = {
        "model": args.model,
        "mode": args.mode,
        "with_diarization": args.diarization,
    }
    if args.language_code:
        kwargs["language_code"] = args.language_code
    if args.num_speakers is not None:
        kwargs["num_speakers"] = args.num_speakers

    job = client.speech_to_text_job.create_job(**kwargs)
    job.upload_files(file_paths=[str(path) for path in audio_paths])
    start_status = job.start()
    completion_status = job.wait_until_complete(poll_interval=args.poll_interval, timeout=args.timeout)

    results = job.get_file_results()
    downloaded = job.download_outputs(output_dir=str(out_dir))

    metadata = {
        "start_status": json_safe(start_status),
        "completion_status": json_safe(completion_status),
        "results": json_safe(results),
        "downloaded": downloaded,
        "plan": plan,
    }
    metadata_path = out_dir / "sarvam-job-metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({"out_dir": str(out_dir), "metadata": str(metadata_path)}, indent=2))


if __name__ == "__main__":
    main()
