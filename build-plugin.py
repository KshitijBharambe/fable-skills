#!/usr/bin/env python3
"""Convert category/topic.md knowledge files into an installable Claude Code plugin.

Creates:
  skills/<topic>/SKILL.md   (frontmatter + original content)
  .claude-plugin/plugin.json
  .claude-plugin/marketplace.json

Original category/*.md files are left untouched.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
SKILLS_DIR = ROOT / "skills"
MANIFEST_DIR = ROOT / ".claude-plugin"

PLUGIN_NAME = "kshtj-expert-skills"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESC = "50 expert software-engineering skills across AI, backend, frontend, architecture, security, UX, and more."
AUTHOR = "KshitijBharambe"
REPO = "KshitijBharambe/fable-skills"  # GitHub owner/repo the marketplace is pushed to

# Skip these top-level dirs / files
IGNORE_DIRS = {"skills", ".claude-plugin", "memory", ".git"}


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s


def extract_when_to_use(text: str) -> str:
    """Pull the '## When to use' bullet list into a single-line description."""
    m = re.search(r"##\s*When to use\s*\n(.*?)(?:\n##\s|\Z)", text, re.S | re.I)
    if not m:
        return ""
    block = m.group(1)
    bullets = re.findall(r"^\s*[-*]\s+(.*)$", block, re.M)
    # Clean bullets: strip markdown, trailing periods, collapse whitespace
    cleaned = []
    for b in bullets:
        b = re.sub(r"[`*]", "", b).strip().rstrip(".")
        b = re.sub(r"\s+", " ", b)
        if b:
            cleaned.append(b)
    if not cleaned:
        return ""
    joined = "; ".join(cleaned)
    desc = f"Use when {joined[0].lower()}{joined[1:]}"
    # Keep descriptions reasonable length for the picker
    if len(desc) > 480:
        desc = desc[:477].rstrip() + "..."
    return desc


def title_of(text: str, fallback: str) -> str:
    m = re.search(r"^\s*#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else fallback


def yaml_escape(s: str) -> str:
    # Quote if it contains characters that break YAML flow, escape quotes
    if re.search(r'[:#\[\]{}\n]', s) or s.strip() != s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def main():
    SKILLS_DIR.mkdir(exist_ok=True)
    MANIFEST_DIR.mkdir(exist_ok=True)

    md_files = []
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in IGNORE_DIRS:
            continue
        if p.name in {"MEMORY.md", "README.md"}:
            continue
        md_files.append(p)

    made = []
    for p in md_files:
        text = p.read_text(encoding="utf-8")
        topic = slugify(p.stem)
        # Disambiguate collisions by prefixing category
        skill_slug = topic
        skill_path = SKILLS_DIR / skill_slug
        if skill_path.exists():
            skill_slug = f"{slugify(p.parent.name)}-{topic}"
            skill_path = SKILLS_DIR / skill_slug
        skill_path.mkdir(parents=True, exist_ok=True)

        desc = extract_when_to_use(text) or f"{title_of(text, p.stem)} — expert guidance."
        fm = (
            "---\n"
            f"name: {skill_slug}\n"
            f"description: {yaml_escape(desc)}\n"
            "---\n\n"
        )
        (skill_path / "SKILL.md").write_text(fm + text, encoding="utf-8")
        made.append((skill_slug, desc))

    # plugin.json
    (MANIFEST_DIR / "plugin.json").write_text(json.dumps({
        "name": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "description": PLUGIN_DESC,
        "author": {"name": AUTHOR},
    }, indent=2) + "\n", encoding="utf-8")

    # marketplace.json
    (MANIFEST_DIR / "marketplace.json").write_text(json.dumps({
        "name": f"{AUTHOR}-marketplace",
        "owner": {"name": AUTHOR},
        "plugins": [
            {
                "name": PLUGIN_NAME,
                "source": "./",
                "description": PLUGIN_DESC,
            }
        ],
    }, indent=2) + "\n", encoding="utf-8")

    print(f"Created {len(made)} skills under skills/")
    print(f"Wrote .claude-plugin/plugin.json and marketplace.json")
    print("\nSample descriptions:")
    for slug, desc in made[:5]:
        print(f"  {slug}: {desc[:90]}...")


if __name__ == "__main__":
    main()
