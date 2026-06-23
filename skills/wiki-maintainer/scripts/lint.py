#!/usr/bin/env python3
"""Lint an LLM Wiki. Pure stdlib. Reports issues; does not modify files.

Checks:
  - broken [[wikilinks]] (target page missing)
  - asymmetric backlinks in '## Related' sections
  - orphan pages (no inbound links)
  - missing required frontmatter keys

Usage:
  python3 lint.py --wiki ./wiki
"""
import argparse
import os
import re
import sys

META = {"index", "inbox", "log", "about", "voice", "sessions", "recommendations"}
REQUIRED_FM = ["title", "created", "source_type", "content_type", "domains", "status"]
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")


def slug(path):
    return os.path.splitext(os.path.basename(path))[0]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k = line.split(":", 1)[0].strip()
            if k:
                fm[k] = line.split(":", 1)[1].strip()
    return fm


def related_links(text):
    out = set()
    for match in re.finditer(r"^##\s+Related\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S):
        out.update(LINK_RE.findall(match.group(1)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", default="./wiki")
    args = ap.parse_args()

    files = [
        os.path.join(args.wiki, f)
        for f in os.listdir(args.wiki)
        if f.endswith(".md")
    ]
    pages = {slug(path): read(path) for path in files}
    articles = {s: text for s, text in pages.items() if s not in META}

    broken, missing_fm = [], []
    inbound = {s: set() for s in articles}
    related = {s: related_links(text) for s, text in articles.items()}

    for s, text in articles.items():
        fm = frontmatter(text)
        miss = [k for k in REQUIRED_FM if k not in fm]
        if miss:
            missing_fm.append((s, miss))
        for target in LINK_RE.findall(text):
            if target not in pages:
                broken.append((s, target))
            elif target in inbound:
                inbound[target].add(s)

    asymmetric = []
    for s, targets in related.items():
        for target in targets:
            if target in related and s not in related[target]:
                asymmetric.append((s, target))

    orphans = [s for s, links in inbound.items() if not links]

    def section(title, rows, fmt):
        print(f"\n{title}: {len(rows)}")
        for row in rows[:50]:
            print("  - " + fmt(row))

    print(f"Wiki: {args.wiki}  |  articles: {len(articles)}")
    section("Broken links", broken, lambda row: f"[[{row[1]}]] in {row[0]}.md")
    section(
        "Asymmetric backlinks",
        asymmetric,
        lambda row: f"{row[0]} -> {row[1]} (no return link)",
    )
    section("Orphan pages (no inbound links)", orphans, lambda row: f"{row}.md")
    section(
        "Missing frontmatter keys",
        missing_fm,
        lambda row: f"{row[0]}.md missing {', '.join(row[1])}",
    )

    total = len(broken) + len(asymmetric) + len(orphans) + len(missing_fm)
    print(f"\nTotal issues: {total}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
