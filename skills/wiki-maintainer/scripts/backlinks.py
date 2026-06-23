#!/usr/bin/env python3
"""Detect and optionally fix asymmetric backlinks in '## Related' sections.

If article A's '## Related' links to B, then B's '## Related' should link to A.
With --fix, the missing reciprocal link is appended to the target's Related
section. A '## Related' section is created if absent.

Usage:
  python3 backlinks.py --wiki ./wiki
  python3 backlinks.py --wiki ./wiki --fix
"""
import argparse
import os
import re

META = {"index", "inbox", "log", "about", "voice", "sessions", "recommendations"}
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
REL_RE = re.compile(r"^##\s+Related\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)


def slug(path):
    return os.path.splitext(os.path.basename(path))[0]


def related(text):
    out = set()
    for match in REL_RE.finditer(text):
        out.update(LINK_RE.findall(match.group(1)))
    return out


def add_related(text, target):
    line = f"- [[{target}]]\n"
    match = REL_RE.search(text)
    if match:
        insert = match.end(1)
        return text[:insert] + line + text[insert:]
    sep = "" if text.endswith("\n") else "\n"
    return text + f"{sep}\n## Related\n\n{line}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", default="./wiki")
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args()

    paths = {
        slug(os.path.join(args.wiki, f)): os.path.join(args.wiki, f)
        for f in os.listdir(args.wiki)
        if f.endswith(".md") and slug(f) not in META
    }
    texts = {s: open(path, encoding="utf-8").read() for s, path in paths.items()}
    rel = {s: related(text) for s, text in texts.items()}

    fixes = 0
    for s, targets in list(rel.items()):
        for target in targets:
            if target in rel and s not in rel[target]:
                if args.fix:
                    texts[target] = add_related(texts[target], s)
                    rel[target].add(s)
                    open(paths[target], "w", encoding="utf-8").write(texts[target])
                    print(f"fixed: added [[{s}]] to {target}.md")
                else:
                    print(f"asymmetric: {s} -> {target} (no return link)")
                fixes += 1

    print(f"\n{'Repaired' if args.fix else 'Found'} {fixes} asymmetric link(s).")


if __name__ == "__main__":
    main()
