#!/usr/bin/env python3
"""Validate JSONL expert-judgment datasets for enum and split hygiene."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def read_allowed_labels(path: str | None) -> set[str] | None:
    if not path:
        return None
    labels = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value and not value.startswith("#"):
            labels.add(value)
    return labels


def fingerprint(record: dict, text_fields: list[str]) -> str:
    chunks = []
    source = record.get("input") if isinstance(record.get("input"), dict) else record
    for field in text_fields:
        value = source.get(field, "")
        if value is None:
            value = ""
        chunks.append(str(value).strip().lower())
    text = "\n".join(chunks)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path: str, split: str, label_field: str, text_fields: list[str]) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
    seen_ids = set()
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{split}:{line_no}: invalid JSON: {exc}")
                continue
            record_id = record.get("id")
            if not record_id:
                errors.append(f"{split}:{line_no}: missing id")
            elif record_id in seen_ids:
                errors.append(f"{split}:{line_no}: duplicate id within split: {record_id}")
            seen_ids.add(record_id)
            if label_field not in record:
                errors.append(f"{split}:{line_no}: missing label field {label_field!r}")
            record["_split"] = split
            record["_line_no"] = line_no
            record["_fingerprint"] = fingerprint(record, text_fields)
            records.append(record)
    return records, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train")
    parser.add_argument("--validation")
    parser.add_argument("--test")
    parser.add_argument("--holdout")
    parser.add_argument("--label-field", default="final_label")
    parser.add_argument("--allowed-labels", help="Text file with one allowed label per line.")
    parser.add_argument("--text-fields", nargs="+", default=["headline", "summary", "text"])
    args = parser.parse_args()

    split_paths = {
        "train": args.train,
        "validation": args.validation,
        "test": args.test,
        "holdout": args.holdout,
    }
    split_paths = {split: path for split, path in split_paths.items() if path}
    if not split_paths:
        parser.error("provide at least one split path")

    allowed_labels = read_allowed_labels(args.allowed_labels)
    all_records = []
    errors = []
    for split, path in split_paths.items():
        records, split_errors = load_jsonl(path, split, args.label_field, args.text_fields)
        all_records.extend(records)
        errors.extend(split_errors)

    labels = Counter()
    ids_to_splits = defaultdict(set)
    fingerprints_to_splits = defaultdict(set)
    examples_by_fingerprint = defaultdict(list)

    for record in all_records:
        label = record.get(args.label_field)
        if label is not None:
            labels[str(label)] += 1
            if allowed_labels is not None and label not in allowed_labels:
                errors.append(
                    f"{record['_split']}:{record['_line_no']}: invalid label {label!r}"
                )
        record_id = record.get("id")
        if record_id:
            ids_to_splits[record_id].add(record["_split"])
        fp = record["_fingerprint"]
        fingerprints_to_splits[fp].add(record["_split"])
        examples_by_fingerprint[fp].append(record)

    for record_id, splits in ids_to_splits.items():
        if len(splits) > 1:
            errors.append(f"id leakage across splits: {record_id} in {sorted(splits)}")

    for fp, splits in fingerprints_to_splits.items():
        if len(splits) > 1:
            examples = examples_by_fingerprint[fp][:3]
            ids = [str(example.get("id")) for example in examples]
            errors.append(f"text fingerprint leakage across splits {sorted(splits)} ids={ids}")

    summary = {
        "ok": not errors,
        "splits": {split: sum(1 for r in all_records if r["_split"] == split) for split in split_paths},
        "label_counts": dict(labels),
        "errors": errors,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
