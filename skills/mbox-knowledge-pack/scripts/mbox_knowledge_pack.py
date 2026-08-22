#!/usr/bin/env python3
"""Create a local knowledge pack from an mbox export."""

from __future__ import annotations

import argparse
import email
import hashlib
import html
import json
import mailbox
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from email.header import decode_header, make_header
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s<>()\"']+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9+-]{2,}")
HTML_TAG_RE = re.compile(r"<[^>]+>")
FORWARDED_RE = re.compile(r"^-{2,}\s*Forwarded message\s*-{2,}", re.I | re.M)

DEFAULT_THEMES = {
    "tools_and_models": ["chatgpt", "claude", "gemini", "grok", "openai", "anthropic", "perplexity", "llm", "agent", "agents"],
    "workflow_and_automation": ["workflow", "automation", "prompt", "prompts", "template", "process", "checklist", "summary"],
    "writing_and_media": ["article", "script", "video", "audio", "voice", "image", "content", "newsletter", "podcast"],
    "verification_and_governance": ["verify", "fact", "source", "credit", "copyright", "privacy", "policy", "risk", "review"],
    "learning_and_strategy": ["learn", "training", "education", "strategy", "business", "management", "decision", "framework"],
    "personal_reflection": ["i think", "my view", "my take", "i believe", "we should", "lesson", "learned"],
}


def clean_header(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value))).replace("\r", " ").replace("\n", " ").strip()
    except Exception:
        return value.replace("\r", " ").replace("\n", " ").strip()


def parse_people(value: str | None) -> list[dict[str, str]]:
    people = []
    for name, addr in getaddresses([value or ""]):
        if name or addr:
            people.append({"name": clean_header(name), "email": addr.lower()})
    return people


def parse_date(value: str | None) -> tuple[str, str]:
    if not value:
        return "", ""
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat(), dt.date().isoformat()
    except Exception:
        return "", ""


def split_labels(value: str | None) -> list[str]:
    labels = []
    for item in (value or "").replace("\r\n", " ").split(","):
        item = re.sub(r"\s+", " ", item).strip()
        if item:
            labels.append(item)
    return sorted(set(labels))


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def html_to_text(text: str) -> str:
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p>", "\n\n", text)
    text = HTML_TAG_RE.sub(" ", text)
    return normalize_text(html.unescape(text))


def decode_part(part: email.message.Message) -> str:
    payload = part.get_payload(decode=True)
    if payload is None:
        raw = part.get_payload()
        return raw if isinstance(raw, str) else ""
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, "replace")
    except LookupError:
        return payload.decode("utf-8", "replace")


def extract_body(msg: email.message.Message) -> tuple[str, str]:
    plain, html_parts = [], []
    for part in msg.walk():
        if part.is_multipart() or (part.get_content_disposition() or "") == "attachment":
            continue
        ctype = part.get_content_type()
        if ctype == "text/plain":
            plain.append(decode_part(part))
        elif ctype == "text/html":
            html_parts.append(decode_part(part))
    text = normalize_text("\n\n".join(plain))
    if text:
        return text, "text/plain"
    html_text = html_to_text("\n\n".join(html_parts)) if html_parts else ""
    return html_text, "text/html-fallback" if html_text else ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_id(*parts: str) -> str:
    basis = "\n".join(part or "" for part in parts)
    return "mbox_" + hashlib.sha256(basis.encode("utf-8", "replace")).hexdigest()[:16]


def domain_for(url: str) -> str:
    try:
        return (urlparse(url).netloc or "").lower().removeprefix("www.")
    except Exception:
        return ""


def extract_urls(text: str) -> list[str]:
    return [match.rstrip(".,;:!?)\"]}'") for match in URL_RE.findall(text)]


def tokenize(text: str) -> list[str]:
    stop = {"the", "and", "for", "that", "this", "with", "from", "are", "was", "you", "your", "have", "has", "not", "but", "can", "will", "about", "into", "https", "com", "www", "mail", "gmail", "subject", "message", "forwarded"}
    return [word.lower() for word in WORD_RE.findall(text) if word.lower() not in stop]


def theme_hits(subject: str, body: str, themes: dict[str, list[str]]) -> dict[str, int]:
    haystack = f"{subject}\n{body}".lower()
    hits = {}
    for theme, terms in themes.items():
        count = 0
        for term in terms:
            if " " in term:
                count += haystack.count(term)
            else:
                count += len(re.findall(rf"\b{re.escape(term)}\b", haystack))
        if count:
            hits[theme] = count
    return hits


def redact(text: str) -> str:
    return EMAIL_RE.sub("[email]", text)


def parse_mbox(mbox_path: Path, themes: dict[str, list[str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    mb = mailbox.mbox(mbox_path, create=False)
    messages, links, attachments = [], [], []
    body_hash_counts: Counter[str] = Counter()

    for index, msg in enumerate(mb, start=1):
        subject = clean_header(msg.get("Subject"))
        message_id = clean_header(msg.get("Message-ID"))
        thread_id = clean_header(msg.get("X-GM-THRID")) or clean_header(msg.get("Thread-Index")) or f"missing-thread-{index}"
        date_iso, date_day = parse_date(msg.get("Date"))
        body, body_source = extract_body(msg)
        normalized_body = re.sub(r"\s+", " ", body.lower()).strip()
        body_hash = hashlib.sha256(normalized_body.encode("utf-8", "replace")).hexdigest()
        body_hash_counts[body_hash] += 1
        msg_id = stable_id(message_id, date_iso, subject, str(index))
        urls = extract_urls(body)
        domains = sorted(set(filter(None, (domain_for(url) for url in urls))))
        msg_attachments = []
        for part_index, part in enumerate(msg.walk(), start=1):
            if part.is_multipart():
                continue
            filename = clean_header(part.get_filename())
            disposition = part.get_content_disposition() or ""
            if not filename and disposition != "attachment":
                continue
            payload = part.get_payload(decode=True) or b""
            att = {
                "message_id": msg_id,
                "thread_id": thread_id,
                "part_index": part_index,
                "filename": filename,
                "content_type": part.get_content_type(),
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest() if payload else "",
            }
            attachments.append(att)
            msg_attachments.append(att)
        for url_index, url in enumerate(urls, start=1):
            pos = body.find(url)
            start = max(0, pos - 120) if pos >= 0 else 0
            end = min(len(body), pos + len(url) + 120) if pos >= 0 else 240
            links.append({"message_id": msg_id, "thread_id": thread_id, "url_index": url_index, "url": url, "domain": domain_for(url), "context": redact(re.sub(r"\s+", " ", body[start:end]).strip())})
        words = tokenize(body)
        messages.append({
            "id": msg_id,
            "source_index": index,
            "message_id_header": message_id,
            "thread_id": thread_id,
            "date": date_iso,
            "date_day": date_day,
            "year_month": date_day[:7] if date_day else "",
            "from": parse_people(msg.get("From")),
            "to": parse_people(msg.get("To")),
            "cc": parse_people(msg.get("Cc")),
            "subject": subject,
            "labels": split_labels(msg.get("X-Gmail-Labels")),
            "content_type": msg.get_content_type(),
            "body_source": body_source,
            "body": body,
            "body_preview": redact(normalize_text(body)[:600]),
            "body_char_count": len(body),
            "body_word_count": len(words),
            "body_sha256": body_hash,
            "url_count": len(urls),
            "urls": urls,
            "domains": domains,
            "attachment_count": len(msg_attachments),
            "attachments": msg_attachments,
            "theme_hits": theme_hits(subject, body, themes),
            "top_terms": Counter(words).most_common(12),
            "forwarded": bool(subject.lower().startswith(("fwd:", "fw:")) or FORWARDED_RE.search(body)),
        })
    for msg in messages:
        msg["duplicate_body_count"] = body_hash_counts[msg["body_sha256"]]
        msg["duplicate_body"] = body_hash_counts[msg["body_sha256"]] > 1
    return messages, links, attachments


def build_threads(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for msg in messages:
        grouped[msg["thread_id"]].append(msg)
    threads = []
    for thread_id, items in grouped.items():
        items.sort(key=lambda m: m["date"] or "")
        theme_counter: Counter[str] = Counter()
        domains: Counter[str] = Counter()
        labels = set()
        for msg in items:
            theme_counter.update(msg["theme_hits"])
            domains.update(msg["domains"])
            labels.update(msg["labels"])
        body_chars = sum(m["body_char_count"] for m in items)
        url_count = sum(m["url_count"] for m in items)
        attachment_count = sum(m["attachment_count"] for m in items)
        forwarded_count = sum(1 for m in items if m["forwarded"])
        duplicate_count = sum(1 for m in items if m["duplicate_body"])
        original_signal = sum(1 for phrase in ["i think", "my view", "my take", "i believe", "we should", "lesson"] if phrase in "\n".join(m["body"].lower() for m in items))
        score = min(body_chars / 700, 8) + min(url_count, 8) * 0.6 + len(theme_counter) * 1.3 + original_signal * 1.4 + (0 if forwarded_count == len(items) else 2) - duplicate_count * 0.8
        if body_chars < 300 or not theme_counter:
            bucket, reason = "exclude", "Too little analyzable theme-related body text."
        elif score >= 14 and duplicate_count < len(items):
            bucket, reason = "import", "High-signal thread suitable for synthesis or wiki/raw-packet use."
        elif score < 7 or forwarded_count == len(items) or duplicate_count == len(items):
            bucket, reason = "exclude", "Mostly duplicate/forwarded material or weak original signal."
        else:
            bucket, reason = "defer", "Potentially useful but needs source, privacy, or attachment review."
        if attachment_count and bucket == "import":
            bucket, reason = "defer", "Strong candidate, but attachments need manual review."
        threads.append({
            "id": "thread_" + hashlib.sha256(thread_id.encode()).hexdigest()[:16],
            "thread_id": thread_id,
            "message_ids": [m["id"] for m in items],
            "message_count": len(items),
            "date_start": items[0]["date_day"],
            "date_end": items[-1]["date_day"],
            "title": items[0]["subject"] or "(no subject)",
            "labels": sorted(labels),
            "body_char_count": body_chars,
            "url_count": url_count,
            "attachment_count": attachment_count,
            "theme_hits": dict(theme_counter),
            "primary_themes": [theme for theme, _ in theme_counter.most_common(5)],
            "domains": [domain for domain, _ in domains.most_common(10)],
            "score": round(score, 2),
            "recommendation_bucket": bucket,
            "recommendation_reason": reason,
            "evidence_message_ids": [m["id"] for m in items[:3]],
        })
    return sorted(threads, key=lambda t: (t["date_start"], t["title"]))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_sqlite(path: Path, messages: list[dict[str, Any]], threads: list[dict[str, Any]], links: list[dict[str, Any]], attachments: list[dict[str, Any]]) -> None:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE messages (id TEXT PRIMARY KEY, source_index INTEGER, thread_id TEXT, date_day TEXT, subject TEXT, body TEXT, body_char_count INTEGER, url_count INTEGER, attachment_count INTEGER, theme_hits_json TEXT);
    CREATE TABLE threads (id TEXT PRIMARY KEY, thread_id TEXT, title TEXT, date_start TEXT, date_end TEXT, message_count INTEGER, score REAL, recommendation_bucket TEXT, primary_themes_json TEXT, message_ids_json TEXT);
    CREATE TABLE links (message_id TEXT, thread_id TEXT, url TEXT, domain TEXT, context TEXT);
    CREATE TABLE attachments (message_id TEXT, thread_id TEXT, filename TEXT, content_type TEXT, size_bytes INTEGER, sha256 TEXT);
    CREATE INDEX idx_messages_thread ON messages(thread_id);
    CREATE INDEX idx_threads_bucket ON threads(recommendation_bucket);
    """)
    for m in messages:
        cur.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?,?)", (m["id"], m["source_index"], m["thread_id"], m["date_day"], m["subject"], m["body"], m["body_char_count"], m["url_count"], m["attachment_count"], json.dumps(m["theme_hits"], ensure_ascii=False)))
    for t in threads:
        cur.execute("INSERT INTO threads VALUES (?,?,?,?,?,?,?,?,?,?)", (t["id"], t["thread_id"], t["title"], t["date_start"], t["date_end"], t["message_count"], t["score"], t["recommendation_bucket"], json.dumps(t["primary_themes"], ensure_ascii=False), json.dumps(t["message_ids"], ensure_ascii=False)))
    cur.executemany("INSERT INTO links VALUES (?,?,?,?,?)", [(l["message_id"], l["thread_id"], l["url"], l["domain"], l["context"]) for l in links])
    cur.executemany("INSERT INTO attachments VALUES (?,?,?,?,?,?)", [(a["message_id"], a["thread_id"], a["filename"], a["content_type"], a["size_bytes"], a["sha256"]) for a in attachments])
    con.commit(); con.close()


def summary(messages, threads, links, attachments) -> dict[str, Any]:
    months = Counter(m["year_month"] for m in messages if m["year_month"])
    themes = Counter()
    for t in threads:
        themes.update(t["theme_hits"])
    return {
        "message_count": len(messages),
        "thread_count": len(threads),
        "link_count": len(links),
        "attachment_count": len(attachments),
        "date_min": min((m["date_day"] for m in messages if m["date_day"]), default=""),
        "date_max": max((m["date_day"] for m in messages if m["date_day"]), default=""),
        "month_counts": dict(sorted(months.items())),
        "theme_counts": themes.most_common(),
        "domain_counts": Counter(l["domain"] for l in links if l["domain"]).most_common(40),
        "thread_bucket_counts": dict(Counter(t["recommendation_bucket"] for t in threads)),
    }


def report_md(s: dict[str, Any], threads: list[dict[str, Any]]) -> str:
    top = sorted([t for t in threads if t["recommendation_bucket"] == "import"], key=lambda t: t["score"], reverse=True)[:30]
    lines = ["# Mbox Knowledge Pack Report", "", "## Corpus Profile", "", f"- Messages: {s['message_count']}", f"- Threads: {s['thread_count']}", f"- Date range: {s['date_min']} to {s['date_max']}", f"- Links: {s['link_count']}", f"- Attachments: {s['attachment_count']}", "", "## Recommendation Buckets", ""]
    for k, v in sorted(s["thread_bucket_counts"].items()):
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Top Themes", ""])
    for theme, count in s["theme_counts"][:12]:
        lines.append(f"- {theme}: {count}")
    lines.extend(["", "## Top Import Candidates", ""])
    for t in top:
        lines.append(f"- `{t['id']}` ({t['date_start']}, score {t['score']}): {t['title']}")
    lines.extend(["", "## Evidence Limits", "", "This report is deterministic extraction plus heuristic scoring. Links are not fetched. Attachments are inventoried only."])
    return "\n".join(lines) + "\n"


def write_fine_tune_prep(out: Path, messages: list[dict[str, Any]], threads: list[dict[str, Any]]) -> None:
    ft = out / "fine-tune-prep"
    ft.mkdir(parents=True, exist_ok=True)
    import_threads = [thread for thread in sorted(threads, key=lambda x: x["score"], reverse=True) if thread.get("recommendation_bucket") == "import"]
    by_msg = {m["id"]: m for m in messages}
    candidates = []
    for t in import_threads[:100]:
        sample = next((by_msg[mid] for mid in t["evidence_message_ids"] if mid in by_msg), None)
        if not sample or sample["body_word_count"] < 80:
            continue
        task = "email_to_management_insight"
        candidates.append({
            "id": "ft_" + t["id"],
            "task": task,
            "input": redact(sample["body"][:3000]),
            "output": "needs_human_written_target",
            "source_thread_id": t["id"],
            "source_message_ids": t["evidence_message_ids"],
            "review_status": "needs_human_review",
            "redaction": "email_addresses_masked",
        })
    write_jsonl(ft / "candidates.jsonl", candidates)
    (ft / "dataset-card.md").write_text(f"""# Fine-Tune Prep Dataset Card

This folder contains candidate examples only. They are not training-ready until a human writes or approves the target outputs and validates privacy.

- Candidate examples: {len(candidates)}
- Default task: email_to_management_insight
- Review status: needs_human_review

Use these for supervised fine-tuning only after selecting examples, redacting sensitive context, writing final outputs, and splitting train/validation/holdout.
""", encoding="utf-8")
    (ft / "audit-report.md").write_text("# Fine-Tune Prep Audit\n\nGenerated candidate rows from import-ranked threads. No train/validation/holdout files were created because human-approved target outputs are still required.\n", encoding="utf-8")



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mbox", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--fine-tune-prep", action="store_true")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    messages, links, attachments = parse_mbox(args.mbox, DEFAULT_THEMES)
    threads = build_threads(messages)
    s = summary(messages, threads, links, attachments)
    manifest = {"generatedAt": datetime.now(timezone.utc).isoformat(), "source": str(args.mbox), "source_sha256": sha256_file(args.mbox), "source_size_bytes": args.mbox.stat().st_size, "counts": {"messages": len(messages), "threads": len(threads), "links": len(links), "attachments": len(attachments)}}
    (args.out / "attachments").mkdir(exist_ok=True)
    (args.out / "reports").mkdir(exist_ok=True)
    write_jsonl(args.out / "messages.jsonl", messages)
    write_jsonl(args.out / "threads.jsonl", threads)
    write_jsonl(args.out / "links.jsonl", links)
    write_jsonl(args.out / "attachments" / "manifest.jsonl", attachments)
    write_sqlite(args.out / "analysis.sqlite", messages, threads, links, attachments)
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.out / "summary.json").write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.out / "reports" / "analysis.md").write_text(report_md(s, threads), encoding="utf-8")
    if args.fine_tune_prep:
        write_fine_tune_prep(args.out, messages, threads)
    print(json.dumps({"ok": True, "out": str(args.out), **manifest["counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
