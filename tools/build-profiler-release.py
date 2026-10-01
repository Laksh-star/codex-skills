#!/usr/bin/env python3
"""Validate local package structure and create a deterministic, allowlisted ZIP.

This is a developer check, not an OpenAI submission validator. It never scans
user history or includes generated reports. Uses only the Python standard library.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ROOT_FILES = {
    "plugin.json", ".codex-plugin/plugin.json", "LICENSE", "README.md",
    "PRIVACY.md", "SUPPORT.md", "assets/icon.svg", "assets/logo.svg",
}
DEV_FILES = {"assets/capability-profiler-dashboard.png"}
SKILL_FILES = {
    "SKILL.md", "agents/openai.yaml", "assets/sample-threads.json",
    "references/data-sources.md", "references/default-rubric.json",
    "scripts/build-capability-report.mjs", "scripts/smoke-test.sh",
    "scripts/test-release-behavior.mjs",
}
PREFIX = "skills/codex-capability-profiler/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def build(package, output):
    allowed = ROOT_FILES | {PREFIX + name for name in SKILL_FILES}
    files = {str(p.relative_to(package)) for p in package.rglob("*") if p.is_file()}
    require(files == allowed | DEV_FILES, f"Package allowlist mismatch: extra={files - allowed - DEV_FILES}, missing={(allowed | DEV_FILES) - files}")
    require(not any(p.is_symlink() for p in package.rglob("*")), "Symlinks are not allowed")
    portable = json.loads((package / "plugin.json").read_text())
    compat = json.loads((package / ".codex-plugin/plugin.json").read_text())
    for key in ("name", "version", "description", "author", "homepage", "repository", "license", "keywords"):
        require(portable[key] == compat[key], f"Manifest mismatch: {key}")
    require(re.fullmatch(r"\d+\.\d+\.\d+", portable["version"]), "Expected release semver")
    require(portable["name"] == "codex-capability-profiler", "Unexpected identity")
    extension = portable["extensions"]["com.openai"]
    require(extension["interface"] == compat["interface"], "Interface metadata disagrees")
    require(extension["onboardingSkill"] == compat["extensions"]["com.openai"]["onboardingSkill"], "Onboarding paths disagree")
    interface = extension["interface"]
    require("screenshots" not in interface, "Skills-only submission must not declare screenshots")
    for key in ("displayName", "shortDescription"):
        require(0 < len(interface[key]) <= 30, f"Invalid {key} length")
    for reference in [interface["logo"], interface["composerIcon"], extension["onboardingSkill"]]:
        require(reference.startswith("./") and reference[2:] in allowed, f"Invalid asset reference: {reference}")
    for name in ("assets/logo.svg", "assets/icon.svg"):
        svg = ElementTree.parse(package / name).getroot()
        width, height = float(svg.attrib["width"]), float(svg.attrib["height"])
        require(width == height and width >= 48, f"Invalid icon dimensions: {name}")
    fixture = json.loads((package / (PREFIX + "assets/sample-threads.json")).read_text())
    tasks = fixture if isinstance(fixture, list) else fixture["threads"]
    require(len(tasks) == 24, "Synthetic fixture must have 24 tasks")
    for name in allowed:
        if name.endswith((".md", ".json", ".yaml", ".mjs", ".sh", ".svg")):
            data = (package / name).read_text()
            require("/Users/ln-mini" not in data, f"Local user path in package: {name}")
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{portable['name']}-{portable['version']}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(allowed):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if name.endswith(".sh") else 0o644
            info.external_attr = (0o100000 | mode) << 16
            z.writestr(info, (package / name).read_bytes())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    receipt = {
        "name": portable["name"], "version": portable["version"], "sha256": digest,
        "archive": archive.name, "bytes": archive.stat().st_size, "files": sorted(allowed),
        "status": "Local structural checks passed; OpenAI portal review remains pending",
    }
    (output / "package-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    (output / "SHA256SUMS").write_text(f"{digest}  {archive.name}\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parents[1] / "plugins/codex-capability-profiler")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.package.resolve(), args.out.resolve())
