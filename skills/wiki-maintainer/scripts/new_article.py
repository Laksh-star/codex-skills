#!/usr/bin/env python3
"""Scaffold a new wiki article with standard frontmatter. Pure stdlib.

Usage:
  python3 new_article.py --wiki ./wiki --slug forward-deployed-engineer \
      --title "Forward-Deployed Engineer Model" \
      --domains ai-strategy,consulting --source "raw/feeds/fde.md" --type bridge

Refuses to overwrite an existing article.
"""
import argparse
import datetime
import os
import sys

TEMPLATE = """---
title: {title}
tags: [{tags}]
created: {date}
source: "{source}"
source_type: {source_type}
content_type: {ctype}
status: processed
domains: [{domains}]
voice: false
---

## Summary

{summary}

## Notes

## Related

## Sources

- `{source}`
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", default="./wiki")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--domains", default="")
    ap.add_argument("--source", default="")
    ap.add_argument("--source-type", default="web")
    ap.add_argument("--type", dest="ctype", default="informative")
    args = ap.parse_args()

    os.makedirs(args.wiki, exist_ok=True)
    path = os.path.join(args.wiki, f"{args.slug}.md")
    if os.path.exists(path):
        sys.exit(f"refusing to overwrite existing {path}")

    domain_values = [d.strip() for d in args.domains.split(",") if d.strip()]
    domains = ", ".join(domain_values)
    summary = (
        "A bridge between " + " and ".join(domain_values) + ": ..."
        if args.ctype == "bridge"
        else "One or two sentences."
    )
    tags = "bridge" if args.ctype == "bridge" else ""

    with open(path, "w", encoding="utf-8") as f:
        f.write(
            TEMPLATE.format(
                title=args.title,
                tags=tags,
                date=datetime.date.today().isoformat(),
                source=args.source,
                source_type=args.source_type,
                ctype=args.ctype,
                domains=domains,
                summary=summary,
            )
        )
    print(f"created {path}")


if __name__ == "__main__":
    main()
