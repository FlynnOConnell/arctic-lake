#!/usr/bin/env python3
"""
build a static INDEX.md for the vault.

replaces the obsidian dataview dashboard with a plain-markdown index that
VSCode can navigate natively (ctrl/cmd+click on the links). scans frontmatter
for title/category/tags and file mtime for recency.

usage:
    uv run build-index          # regenerate INDEX.md
    uv run build-index --check  # exit 1 if INDEX.md is out of date (for CI/hooks)
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
INDEX_PATH = REPO_ROOT / "INDEX.md"

# directories that are generated, tooling, or not hand-written notes
EXCLUDE_DIRS = {
    ".git", ".obsidian", ".venv", ".claude", "__pycache__", "node_modules",
    "docs", "exports", "processing", "static", "templates", "scripts",
    "private",
}

# files that are not notes / would be self-referential
EXCLUDE_FILES = {"INDEX.md", "README.md"}

RECENT_LIMIT = 15


def iter_notes():
    """yield every markdown note in the vault, excluding tooling/generated dirs."""
    for path in REPO_ROOT.rglob("*.md"):
        rel = path.relative_to(REPO_ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDE_FILES:
            continue
        yield path


def parse_frontmatter(text: str) -> dict:
    """extract the yaml frontmatter block, if any."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def first_h1(text: str) -> str | None:
    """return the first markdown H1, if present."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def load_note(path: Path) -> dict:
    """read a note into a normalized record."""
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    rel = path.relative_to(REPO_ROOT)

    title = fm.get("title") or first_h1(text) or path.stem.replace("_", " ").replace("-", " ")

    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    tags = [str(t) for t in tags if t]

    category = fm.get("category")
    category = str(category) if category else None

    return {
        "path": rel,
        "link": rel.as_posix(),
        "title": str(title).strip(),
        "category": category,
        "tags": tags,
        "folder": rel.parent.as_posix() if rel.parent != Path(".") else "(root)",
        "mtime": path.stat().st_mtime,
    }


def md_link(note: dict) -> str:
    # wrap targets with spaces/parens in angle brackets so the link stays valid
    target = note["link"]
    if any(c in target for c in " ()"):
        target = f"<{target}>"
    return f"[{note['title']}]({target})"


def section_recent(notes: list[dict]) -> list[str]:
    lines = ["## Recently updated", ""]
    recent = sorted(notes, key=lambda n: n["mtime"], reverse=True)[:RECENT_LIMIT]
    for n in recent:
        date = datetime.fromtimestamp(n["mtime"], tz=timezone.utc).strftime("%Y-%m-%d")
        lines.append(f"- `{date}` — {md_link(n)}")
    lines.append("")
    return lines


def section_by_category(notes: list[dict]) -> list[str]:
    categorized = [n for n in notes if n["category"]]
    if not categorized:
        return []
    lines = ["## By category", ""]
    by_cat: dict[str, list[dict]] = {}
    for n in categorized:
        by_cat.setdefault(n["category"], []).append(n)
    for cat in sorted(by_cat, key=str.lower):
        lines.append(f"### {cat}")
        lines.append("")
        for n in sorted(by_cat[cat], key=lambda x: x["title"].lower()):
            lines.append(f"- {md_link(n)}")
        lines.append("")
    return lines


def section_by_tag(notes: list[dict]) -> list[str]:
    by_tag: dict[str, list[dict]] = {}
    for n in notes:
        for tag in n["tags"]:
            by_tag.setdefault(tag, []).append(n)
    if not by_tag:
        return []
    lines = ["## By tag", ""]
    for tag in sorted(by_tag, key=str.lower):
        links = ", ".join(md_link(n) for n in sorted(by_tag[tag], key=lambda x: x["title"].lower()))
        lines.append(f"- **#{tag}** — {links}")
    lines.append("")
    return lines


def section_by_folder(notes: list[dict]) -> list[str]:
    lines = ["## All notes by folder", ""]
    by_folder: dict[str, list[dict]] = {}
    for n in notes:
        by_folder.setdefault(n["folder"], []).append(n)
    for folder in sorted(by_folder, key=str.lower):
        lines.append(f"### `{folder}`")
        lines.append("")
        for n in sorted(by_folder[folder], key=lambda x: x["title"].lower()):
            lines.append(f"- {md_link(n)}")
        lines.append("")
    return lines


def build() -> str:
    notes = [load_note(p) for p in iter_notes()]
    generated = "<!-- generated by scripts/build_index.py — do not edit by hand; run `uv run build-index` -->"

    lines = [
        generated,
        "",
        "# Vault index",
        "",
        f"{len(notes)} notes. Ctrl/Cmd+click any link to open it.",
        "",
    ]
    lines += section_recent(notes)
    lines += section_by_category(notes)
    lines += section_by_tag(notes)
    lines += section_by_folder(notes)

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="generate a static INDEX.md for the vault")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if INDEX.md is out of date instead of writing")
    args = parser.parse_args()

    content = build()

    if args.check:
        current = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""
        if current != content:
            print("INDEX.md is out of date — run `uv run build-index`")
            sys.exit(1)
        print("INDEX.md is up to date")
        return

    INDEX_PATH.write_text(content, encoding="utf-8")
    print(f"wrote {INDEX_PATH.relative_to(REPO_ROOT)} ({content.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
