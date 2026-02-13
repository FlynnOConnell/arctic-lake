#!/usr/bin/env python3
"""
export weekly notes with embedded daily notes as static HTML.

renders a weekly note with all associated daily notes organized by date.
supports building individual weeks or all weeks at once.

usage:
    # export current week
    uv run export-weekly

    # export specific week
    uv run export-weekly 2026-W03

    # export all weeks
    uv run export-weekly --all

    # export to OneDrive (default)
    uv run export-weekly --sync

    # force overwrite (backs up to X: drive)
    uv run export-weekly --sync --force
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tomllib
from datetime import datetime, timedelta
from pathlib import Path

from scripts.export_note import (
    parse_frontmatter,
    convert_obsidian_images,
    convert_standard_images,
    convert_obsidian_videos,
    convert_standard_videos,
    convert_wikilinks,
    strip_frontmatter,
)
from scripts.config import LOCAL_EXPORT_DIR

# onedrive sync destination (main weekly reports)
ONEDRIVE_WEEKLY = Path.home() / "OneDrive - The Rockefeller University" / "MBO_DATA" / "weekly_meeting"

# network share destination (main weekly reports - what boss sees)
NETWORK_WEEKLY = Path("Y:/foconnell/weekly_meeting")

# compute subfolder for notebooks/SOPs
ONEDRIVE_COMPUTE = Path.home() / "OneDrive - The Rockefeller University" / "MBO_DATA" / "weekly_meeting" / "compute"
NETWORK_COMPUTE = Path("Y:/foconnell/weekly_meeting/compute")

# direct processing folder (for links from notebooks/notes)
NETWORK_PROCESSING = Path("Y:/foconnell/processing")

# source repo mirror on network (for SOPs, notes source files)
NETWORK_NOTEBOOK = Path("Y:/foconnell/notebook")

try:
    import markdown
except ImportError:
    print("ERROR: 'markdown' package not found. Install with: pip install markdown")
    sys.exit(1)


def convert_inline_code(text: str) -> str:
    """convert backticks to code tags."""
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', text)


def slugify(text: str) -> str:
    """convert text to url-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text


def convert_callouts(content: str) -> str:
    """convert obsidian callouts to collapsible HTML details elements.

    Handles: > [!type]- Title
             > content lines
    """
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # match callout start: > [!type]- Title or > [!type] Title
        callout_match = re.match(r'^>\s*\[!(\w+)\](-?)\s*(.*)$', line)
        if callout_match:
            callout_type = callout_match.group(1)
            collapsed = callout_match.group(2) == '-'
            title = callout_match.group(3).strip() or callout_type.capitalize()

            # collect callout content
            callout_content = []
            i += 1
            while i < len(lines) and lines[i].startswith('>'):
                # strip the leading > and optional space
                content_line = re.sub(r'^>\s?', '', lines[i])
                callout_content.append(content_line)
                i += 1

            # generate anchor id from title
            anchor_id = f"proposal-{slugify(title)}"

            # convert callout content (may have markdown)
            inner_content = '\n'.join(callout_content)

            # wrap in details element
            open_attr = '' if collapsed else ' open'
            result.append(f'<details class="callout callout-{callout_type}" id="{anchor_id}"{open_attr}>')
            result.append(f'<summary>{title}</summary>')
            result.append(f'<div class="callout-content">')
            result.append(inner_content)
            result.append('</div>')
            result.append('</details>')
            result.append('')
        else:
            result.append(line)
            i += 1

    return '\n'.join(result)


def convert_task_lists(content: str) -> str:
    """convert markdown task lists to styled HTML checkboxes."""

    def make_checked(m):
        indent, text = m.group(1), convert_inline_code(m.group(2))
        return f'{indent}<li class="task-item task-done"><span class="checkbox checked"></span> {text}</li>'

    def make_partial(m):
        indent, text = m.group(1), convert_inline_code(m.group(2))
        return f'{indent}<li class="task-item task-partial"><span class="checkbox partial"></span> {text}</li>'

    def make_open(m):
        indent, text = m.group(1), convert_inline_code(m.group(2))
        return f'{indent}<li class="task-item task-open"><span class="checkbox"></span> {text}</li>'

    # - [x] checked
    content = re.sub(r'^(\s*)- \[x\] ?(.*)$', make_checked, content, flags=re.MULTILINE)
    # - [~] partial/in-progress
    content = re.sub(r'^(\s*)- \[~\] ?(.*)$', make_partial, content, flags=re.MULTILINE)
    # - [ ] unchecked
    content = re.sub(r'^(\s*)- \[ \] ?(.*)$', make_open, content, flags=re.MULTILINE)
    return content


# paths relative to this script's parent (docs repo root)
DOCS_ROOT = Path(__file__).parent.parent
WEEKLY_DIR = DOCS_ROOT / "weekly"
DAILY_DIR = DOCS_ROOT / "daily"
IMAGES_DIR = DOCS_ROOT / "notes" / "images"
EXPORTS_CONFIG = DOCS_ROOT / "exports.toml"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-color: #121212;
            --surface-color: #1e1e1e;
            --text-color: #e0e0e0;
            --text-muted: #9e9e9e;
            --border-color: #333;
            --link-color: #82aaff;
            --link-hover: #b0c4ff;
            --heading-color: #ffffff;
            --accent-color: #82aaff;
            --code-bg: #0d1117;
            --code-text: #c9d1d9;
            --inline-code-bg: #161b22;
            color-scheme: dark;
        }}

        * {{ box-sizing: border-box; }}

        body {{
            font-family: 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--heading-color);
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
        }}

        h1 {{
            font-size: 1.8em;
            text-decoration: underline;
            border: none;
            padding-bottom: 0;
        }}

        h2 {{
            font-size: 1.4em;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.2em;
        }}

        h3 {{ font-size: 1.2em; }}

        a {{ color: var(--link-color); text-decoration: none; }}
        a:hover {{ color: var(--link-hover); text-decoration: underline; }}

        img {{
            max-width: 550px;
            height: auto;
            display: block;
            margin: 1em auto;
            border-radius: 4px;
        }}

        video {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
            border-radius: 4px;
        }}

        code {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.82rem;
            background-color: var(--inline-code-bg);
            color: var(--code-text);
            padding: 2px 6px;
            border-radius: 4px;
        }}

        pre {{
            background-color: var(--code-bg);
            padding: 12px 24px;
            border-radius: 4px;
            overflow-x: auto;
            border: none;
            font-size: 0.82rem;
        }}

        pre code {{
            background: transparent;
            padding: 0;
        }}

        blockquote {{
            border-left: 3px solid var(--accent-color);
            margin-left: 0;
            padding-left: 1em;
            color: var(--text-muted);
        }}

        table {{
            background-color: var(--surface-color);
            border-collapse: collapse;
            width: 100%;
            margin: 0.5em 0;
            border-radius: 4px;
            overflow: hidden;
            font-size: 0.78rem;
            line-height: 1.3;
        }}

        thead {{
            background-color: #2d2d2d;
            border-bottom: 1px solid #424242;
        }}

        th {{
            background-color: #2d2d2d;
            color: #fff;
            font-weight: 600;
            padding: 5px 6px;
            text-align: left;
            border: none;
            font-size: 0.78rem;
        }}

        tbody tr {{
            background-color: var(--surface-color);
            border-bottom: 1px solid #2a2a2a;
        }}

        tbody tr:nth-child(even) {{
            background-color: #252525;
        }}

        tbody tr:hover {{
            background-color: #333;
        }}

        td {{
            color: var(--text-color);
            padding: 3px 6px;
            border: none;
            vertical-align: top;
            font-size: 0.78rem;
        }}

        ul, ol {{ padding-left: 1.5em; }}
        li {{ margin: 0.25em 0; }}

        hr {{
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 2em 0;
        }}

        .weekly-section {{
            margin-bottom: 3em;
        }}

        .daily-section {{
            margin-top: 3em;
            padding-top: 2em;
            border-top: 2px solid var(--accent-color);
        }}

        .daily-note {{
            margin-bottom: 1em;
            background-color: var(--surface-color);
            border-radius: 6px;
            border-left: 3px solid var(--accent-color);
        }}

        .daily-note summary {{
            padding: 0.8em 1em;
            cursor: pointer;
            font-weight: 600;
            color: var(--accent-color);
            list-style: none;
            display: flex;
            align-items: center;
            gap: 0.5em;
        }}

        .daily-note summary::-webkit-details-marker {{
            display: none;
        }}

        .daily-note summary::before {{
            content: '▶';
            font-size: 0.7em;
            transition: transform 0.2s;
        }}

        .daily-note[open] summary::before {{
            transform: rotate(90deg);
        }}

        .daily-note summary:hover {{
            background-color: #252525;
            border-radius: 6px 6px 0 0;
        }}

        .daily-content {{
            padding: 0 1.5em 1em 1.5em;
        }}

        .daily-note-empty {{
            color: var(--text-muted);
            font-style: italic;
        }}

        .task-item {{
            list-style-type: none;
            margin-left: -1em;
            display: flex;
            align-items: flex-start;
            gap: 0.5em;
        }}

        .checkbox {{
            display: inline-block;
            width: 16px;
            height: 16px;
            min-width: 16px;
            border: 2px solid var(--text-muted);
            border-radius: 3px;
            margin-top: 3px;
            position: relative;
        }}

        .checkbox.checked {{
            background-color: #4caf50;
            border-color: #4caf50;
        }}

        .checkbox.checked::after {{
            content: '';
            position: absolute;
            left: 4px;
            top: 1px;
            width: 4px;
            height: 8px;
            border: solid #fff;
            border-width: 0 2px 2px 0;
            transform: rotate(45deg);
        }}

        .checkbox.partial {{
            background-color: #ff9800;
            border-color: #ff9800;
        }}

        .checkbox.partial::after {{
            content: '';
            position: absolute;
            left: 2px;
            top: 5px;
            width: 8px;
            height: 2px;
            background-color: #fff;
        }}

        .task-done {{
            color: var(--text-muted);
        }}

        .task-partial {{
            color: #ffcb6b;
        }}

        .callout {{
            margin: 1em 0;
            background-color: var(--surface-color);
            border-radius: 6px;
            border-left: 3px solid var(--accent-color);
        }}

        .callout summary {{
            padding: 0.8em 1em;
            cursor: pointer;
            font-weight: 600;
            color: var(--accent-color);
            list-style: none;
            display: flex;
            align-items: center;
            gap: 0.5em;
        }}

        .callout summary::-webkit-details-marker {{
            display: none;
        }}

        .callout summary::before {{
            content: '▶';
            font-size: 0.7em;
            transition: transform 0.2s;
        }}

        .callout[open] summary::before {{
            transform: rotate(90deg);
        }}

        .callout summary:hover {{
            background-color: #252525;
            border-radius: 6px 6px 0 0;
        }}

        .callout-content {{
            padding: 0 1.5em 1em 1.5em;
        }}

        .callout-proposal {{
            border-left-color: #c792ea;
        }}

        .callout-proposal summary {{
            color: #c792ea;
        }}

        .callout-backlog {{
            border-left-color: #ff5370;
            margin-top: 2em;
        }}

        .callout-backlog summary {{
            color: #ff5370;
        }}

        .callout-backlog h4 {{
            margin: 0.8em 0 0.3em 0;
            color: var(--text-muted);
            font-size: 0.9em;
        }}

        .missing-image {{
            background-color: #332b00;
            border: 1px solid #665500;
            padding: 1em;
            border-radius: 4px;
            color: #ffcb6b;
            text-align: center;
        }}

        .week-nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1em 0;
            margin-bottom: 1em;
            border-bottom: 1px solid var(--border-color);
        }}

        .week-nav:last-of-type {{
            margin-top: 2em;
            margin-bottom: 0;
            border-bottom: none;
            border-top: 1px solid var(--border-color);
        }}

        .week-nav a {{
            color: var(--link-color);
            text-decoration: none;
            padding: 0.5em 1em;
            border-radius: 4px;
            background-color: var(--surface-color);
        }}

        .week-nav a:hover {{
            background-color: #333;
        }}

        .nav-prev, .nav-next {{
            min-width: 100px;
        }}

        .nav-index {{
            font-weight: 600;
        }}

        .links-section {{
            margin-top: 2em;
            padding-top: 1em;
            border-top: 1px solid var(--border-color);
        }}

        .links-section ul {{
            list-style: none;
            padding-left: 0;
        }}

        .links-section li {{
            padding: 0.5em 0;
            border-bottom: 1px solid #252525;
        }}

        .links-section a {{
            font-weight: 500;
        }}

        .index-meta {{
            color: var(--text-muted);
            font-size: 0.9em;
            margin-bottom: 2em;
        }}

        .week-list {{
            list-style: none;
            padding: 0;
        }}

        .week-item {{
            padding: 1em;
            margin-bottom: 0.5em;
            background-color: var(--surface-color);
            border-radius: 6px;
            border-left: 3px solid var(--accent-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .week-item:hover {{
            background-color: #252525;
        }}

        .week-item a {{
            font-weight: 600;
            font-size: 1.1em;
        }}

        .week-range {{
            color: var(--text-muted);
        }}

        @media print {{
            body {{
                max-width: none;
                padding: 1cm;
                background-color: #fff;
                color: #000;
            }}
            .daily-note {{
                background-color: #f5f5f5;
                border-left-color: #333;
            }}
            img {{ max-height: 400px; page-break-inside: avoid; }}
            h1, h2, h3 {{ page-break-after: avoid; }}
            pre, blockquote {{ page-break-inside: avoid; }}
            .daily-note {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""


def get_week_dates(year: int, week: int) -> tuple[datetime, datetime]:
    """get start (monday) and end (sunday) dates for an ISO week."""
    jan4 = datetime(year, 1, 4)
    start_of_week1 = jan4 - timedelta(days=jan4.isoweekday() - 1)
    monday = start_of_week1 + timedelta(weeks=week - 1)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def parse_week_id(week_id: str) -> tuple[int, int]:
    """parse a week identifier like '2026-W03' into (year, week)."""
    match = re.match(r'^(\d{4})-W(\d{2})$', week_id)
    if not match:
        raise ValueError(f"invalid week format: {week_id} (expected YYYY-Www)")
    return int(match.group(1)), int(match.group(2))


def get_current_week_id() -> str:
    """get current week as 'YYYY-Www' format."""
    now = datetime.now()
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def find_weekly_note(week_id: str) -> Path | None:
    """find the weekly note file for a given week."""
    weekly_file = WEEKLY_DIR / f"{week_id}.md"
    return weekly_file if weekly_file.exists() else None


def find_daily_notes(year: int, week: int) -> list[tuple[datetime, Path]]:
    """find all daily notes that belong to a given ISO week."""
    monday, sunday = get_week_dates(year, week)
    daily_notes = []

    if not DAILY_DIR.exists():
        return daily_notes

    for daily_file in DAILY_DIR.glob("*.md"):
        try:
            date = datetime.strptime(daily_file.stem, "%Y-%m-%d")
            if monday <= date <= sunday:
                daily_notes.append((date, daily_file))
        except ValueError:
            continue

    return sorted(daily_notes, key=lambda x: x[0])


def discover_all_weeks() -> list[str]:
    """discover all available weekly notes."""
    if not WEEKLY_DIR.exists():
        return []

    weeks = []
    for weekly_file in WEEKLY_DIR.glob("*.md"):
        try:
            parse_week_id(weekly_file.stem)
            weeks.append(weekly_file.stem)
        except ValueError:
            continue

    return sorted(weeks)


def filter_empty_sections(content: str) -> str:
    """remove sections that have no meaningful content (just '-' or whitespace)."""
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # check if this is a header line
        header_match = re.match(r'^(#+)\s+', line)
        if header_match:
            section_header = line
            section_content = []
            i += 1

            # collect content lines until ANY next header
            while i < len(lines):
                next_line = lines[i]
                if re.match(r'^#+\s+', next_line):
                    break
                section_content.append(next_line)
                i += 1

            # check if section has meaningful content
            non_empty = [l.strip() for l in section_content if l.strip()]
            is_empty = not non_empty or all(l == '-' for l in non_empty)

            # also check if next header is a subheader (deeper level = more #s)
            header_level = len(header_match.group(1))
            next_header_match = re.match(r'^(#+)\s+', lines[i]) if i < len(lines) else None
            has_subheader = next_header_match and len(next_header_match.group(1)) > header_level

            if not is_empty or has_subheader:
                result.append(section_header)
                result.extend(section_content)
        else:
            result.append(line)
            i += 1

    return '\n'.join(result)


def extract_links_from_daily_notes(daily_notes: list[tuple[datetime, Path]]) -> list[dict]:
    """extract external links from daily note content."""
    link_pattern = re.compile(r'\[([^\]]+)\]\((https?://[^)]+)\)')
    links = []

    for date, daily_file in daily_notes:
        content = daily_file.read_text(encoding='utf-8')
        content = strip_frontmatter(content)

        for match in link_pattern.finditer(content):
            links.append({
                'text': match.group(1),
                'url': match.group(2),
                'source': date.strftime('%b %d'),
                'date': date
            })

    return sorted(links, key=lambda x: x['date'])


def remove_dataviewjs_links_section(content: str) -> str:
    """remove the Links section with dataviewjs block (rendered separately at bottom)."""
    # remove the entire ## Links section including the dataviewjs block
    # use [\s\S] instead of . to reliably match across newlines
    pattern = re.compile(
        r'^## Links\s*\n```dataviewjs[\s\S]*?```\s*\n?',
        re.MULTILINE
    )
    return pattern.sub('', content)


def process_markdown(content: str, source_file: Path, output_dir: Path | None = None) -> str:
    """process markdown content, converting images/videos and obsidian syntax."""
    content = strip_frontmatter(content)
    content = filter_empty_sections(content)
    content = convert_obsidian_images(content, source_file, IMAGES_DIR)
    content = convert_standard_images(content, source_file, IMAGES_DIR)
    if output_dir:
        content = convert_obsidian_videos(content, source_file, output_dir)
        content = convert_standard_videos(content, source_file, output_dir)
    content = convert_wikilinks(content)
    content = convert_callouts(content)
    content = convert_task_lists(content)
    return content


def render_markdown(content: str) -> str:
    """convert markdown to HTML."""
    md = markdown.Markdown(
        extensions=['fenced_code', 'tables', 'toc', 'nl2br', 'sane_lists']
    )
    return md.convert(content)


def build_weekly_report(
    week_id: str,
    output_dir: Path,
    prev_week: str | None = None,
    next_week: str | None = None
) -> str | None:
    """
    build a complete HTML report for a week.

    returns HTML string or None if no content found.
    """
    year, week = parse_week_id(week_id)
    monday, sunday = get_week_dates(year, week)
    week_range = f"{monday.strftime('%B %d')} - {sunday.strftime('%B %d, %Y')}"

    weekly_file = find_weekly_note(week_id)
    daily_notes = find_daily_notes(year, week)

    if not weekly_file and not daily_notes:
        return None

    parts = []

    # navigation header
    nav_parts = ['<nav class="week-nav">']
    if prev_week:
        nav_parts.append(f'<a href="{prev_week}.html" class="nav-prev">← {prev_week}</a>')
    else:
        nav_parts.append('<span class="nav-prev"></span>')
    nav_parts.append('<a href="index.html" class="nav-index">Index</a>')
    if next_week:
        nav_parts.append(f'<a href="{next_week}.html" class="nav-next">{next_week} →</a>')
    else:
        nav_parts.append('<span class="nav-next"></span>')
    nav_parts.append('</nav>')
    parts.append(''.join(nav_parts))

    # extract links from daily notes
    daily_links = extract_links_from_daily_notes(daily_notes)
    if daily_links:
        print(f"  found {len(daily_links)} links in daily notes")

    # weekly notes section (contains its own h1 title)
    if weekly_file:
        print(f"  processing weekly: {weekly_file.name}")
        weekly_content = weekly_file.read_text(encoding='utf-8')

        # replace {{week_range}} placeholder if present
        weekly_content = weekly_content.replace('{{week_range}}', week_range)

        # remove dataviewjs Links section (rendered separately below daily notes)
        weekly_content = remove_dataviewjs_links_section(weekly_content)

        processed = process_markdown(weekly_content, weekly_file, output_dir)
        html = render_markdown(processed)

        parts.append(f'''
<div class="weekly-section" id="weekly-notes">
    {html}
</div>
''')

    # daily notes section (collapsible)
    if daily_notes:
        parts.append('<div class="daily-section" id="daily-notes">')
        parts.append('<h2>Daily Notes</h2>')

        for date, daily_file in daily_notes:
            anchor = date.strftime("%Y-%m-%d")
            label = date.strftime("%A, %B %d, %Y")
            print(f"  processing daily: {daily_file.name}")

            daily_content = daily_file.read_text(encoding='utf-8')
            processed = process_markdown(daily_content, daily_file, output_dir)

            if processed.strip():
                html = render_markdown(processed)
                parts.append(f'''
<details class="daily-note" id="{anchor}">
    <summary>{label}</summary>
    <div class="daily-content">
    {html}
    </div>
</details>
''')
            else:
                parts.append(f'''
<details class="daily-note" id="{anchor}">
    <summary>{label}</summary>
    <div class="daily-content">
    <p class="daily-note-empty">No notes recorded.</p>
    </div>
</details>
''')

        parts.append('</div>')

    # links section (after daily notes)
    if daily_links:
        parts.append('<div class="links-section" id="links">')
        parts.append('<h2>Links</h2>')
        parts.append('<ul>')
        for link in daily_links:
            parts.append(f'<li><a href="{link["url"]}" target="_blank">{link["text"]}</a> <em>({link["source"]})</em></li>')
        parts.append('</ul>')
        parts.append('</div>')

    # backlog section (unchecked items from previous weeks)
    backlog = collect_backlog(week_id)
    if backlog:
        total = sum(len(b['items']) for b in backlog)
        parts.append(f'''
<details class="callout callout-backlog" id="backlog">
<summary>Backlog ({total} items from {len(backlog)} weeks)</summary>
<div class="callout-content">''')
        for entry in backlog:
            parts.append(f'<h4>{entry["week"]}</h4>')
            parts.append('<ul>')
            for item in entry['items']:
                parts.append(f'<li class="task-item task-open"><span class="checkbox"></span> {convert_inline_code(item)}</li>')
            parts.append('</ul>')
        parts.append('</div>')
        parts.append('</details>')

    # bottom navigation
    parts.append(''.join(nav_parts))

    return HTML_TEMPLATE.format(
        title=f"Weekly Meeting – {week_range}",
        content="".join(parts)
    )


def get_adjacent_weeks(week_id: str, all_weeks: list[str]) -> tuple[str | None, str | None]:
    """get previous and next week IDs from list of available weeks."""
    if week_id not in all_weeks:
        return None, None

    idx = all_weeks.index(week_id)
    prev_week = all_weeks[idx - 1] if idx > 0 else None
    next_week = all_weeks[idx + 1] if idx < len(all_weeks) - 1 else None
    return prev_week, next_week


def export_week(
    week_id: str,
    output_dir: Path,
    all_weeks: list[str] | None = None,
    force: bool = False
) -> Path | None:
    """export a single week to HTML."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{week_id}.html"

    # check if file exists and handle overwrite
    if output_file.exists() and not force:
        print(f"  skipping {week_id} (already exists, use --force to overwrite)")
        return output_file

    print(f"building report for {week_id}...")

    # get adjacent weeks for navigation
    prev_week, next_week = None, None
    if all_weeks:
        prev_week, next_week = get_adjacent_weeks(week_id, all_weeks)

    html = build_weekly_report(week_id, output_dir, prev_week, next_week)
    if html is None:
        print(f"  no content found for {week_id}")
        return None

    output_file.write_text(html, encoding='utf-8')
    print(f"  created: {output_file}")
    return output_file


def export_all_weeks(output_dir: Path, force: bool = False) -> list[Path]:
    """export all available weeks to HTML with navigation links."""
    weeks = discover_all_weeks()
    if not weeks:
        print("no weekly notes found")
        return []

    print(f"found {len(weeks)} weekly notes")
    results = []

    for week_id in weeks:
        result = export_week(week_id, output_dir, all_weeks=weeks, force=force)
        if result:
            results.append(result)

    return results


def build_index(output_dir: Path) -> Path | None:
    """build an index.html linking to all weekly reports."""
    html_files = sorted(output_dir.glob("????-W??.html"), reverse=True)
    if not html_files:
        return None

    items = []
    for html_file in html_files:
        week_id = html_file.stem
        try:
            year, week = parse_week_id(week_id)
            monday, sunday = get_week_dates(year, week)
            week_range = f"{monday.strftime('%B %d')} - {sunday.strftime('%B %d, %Y')}"
            items.append(f'''
<li class="week-item">
    <a href="{html_file.name}">{week_id}</a>
    <span class="week-range">{week_range}</span>
</li>''')
        except ValueError:
            items.append(f'<li class="week-item"><a href="{html_file.name}">{week_id}</a></li>')

    # check if compute folder exists
    compute_link = ""
    if (output_dir / "compute").exists():
        compute_link = '<p><a href="compute/index.html">→ Compute (SOPs, Processing Notebooks)</a></p>'

    index_html = HTML_TEMPLATE.format(
        title="Weekly Meeting Notes",
        content=f'''
<h1>Weekly Meeting Notes</h1>
<p class="index-meta">Last updated: {datetime.now().strftime("%B %d, %Y at %H:%M")}</p>
{compute_link}
<ul class="week-list">
    {"".join(items)}
</ul>
'''
    )

    index_file = output_dir / "index.html"
    index_file.write_text(index_html, encoding='utf-8')
    print(f"created index: {index_file}")
    return index_file


def load_exports_config() -> dict:
    """load exports.toml configuration."""
    if not EXPORTS_CONFIG.exists():
        return {"pages": []}
    with open(EXPORTS_CONFIG, "rb") as f:
        return tomllib.load(f)


def export_page(source: Path, output_file: Path, title: str) -> Path | None:
    """export a single markdown page to HTML."""
    if not source.exists():
        print(f"  skipping {source} (not found)")
        return None

    output_file.parent.mkdir(parents=True, exist_ok=True)

    content = source.read_text(encoding='utf-8')
    processed = process_markdown(content, source)
    html = render_markdown(processed)

    # wrap in template with back link
    full_html = HTML_TEMPLATE.format(
        title=title,
        content=f'''
<nav class="week-nav">
    <span class="nav-prev"></span>
    <a href="../index.html" class="nav-index">Index</a>
    <span class="nav-next"></span>
</nav>
<div class="weekly-section">
    <h1>{title}</h1>
    {html}
</div>
<nav class="week-nav">
    <span class="nav-prev"></span>
    <a href="../index.html" class="nav-index">Index</a>
    <span class="nav-next"></span>
</nav>
'''
    )

    output_file.write_text(full_html, encoding='utf-8')
    print(f"  created: {output_file}")
    return output_file


def parse_notebook_title(filename: str) -> str:
    """parse title from notebook filename like 2025-11-04_kbarber_suite2p-comparison_20260107.html"""
    stem = Path(filename).stem
    parts = stem.split('_')
    if len(parts) >= 4:
        # format: date_author_title_exportdate (4+ parts)
        date = parts[0]
        author = parts[1]
        title = '_'.join(parts[2:-1])
        title = title.replace('-', ' ').title()
        return f"{title} ({author}, {date})"
    elif len(parts) == 3:
        # could be date_title_exportdate or date_author_title
        date = parts[0]
        title = parts[1].replace('-', ' ').title()
        return f"{title} ({date})"
    return stem.replace('-', ' ').replace('_', ' ').title()


def parse_sop_title(filename: str) -> str:
    """parse title from SOP filename like sop_agarose_bead-prep.md"""
    stem = Path(filename).stem
    # remove sop_ prefix if present
    if stem.lower().startswith('sop_'):
        stem = stem[4:]
    return stem.replace('-', ' ').replace('_', ' ').title()


def export_directory_markdown(source_dir: Path, output_dir: Path, subdir: str, category: str, pattern: str = "*.md", title_parser=None) -> list[dict]:
    """scan directory for markdown files and export them."""
    exported = []
    if not source_dir.exists():
        print(f"  skipping {source_dir} (not found)")
        return exported

    out_path = output_dir / subdir
    out_path.mkdir(parents=True, exist_ok=True)

    for md_file in sorted(source_dir.glob(pattern)):
        if title_parser:
            title = title_parser(md_file.name)
        else:
            title = md_file.stem.replace('-', ' ').replace('_', ' ').title()
        output_file = out_path / f"{md_file.stem}.html"

        result = export_page(md_file, output_file, title)
        if result:
            exported.append({
                "path": f"{subdir}/{md_file.stem}.html",
                "title": title,
                "category": category
            })

    return exported


def copy_html_directory(source_dir: Path, output_dir: Path, subdir: str, category: str, pattern: str = "*.html") -> list[dict]:
    """copy pre-rendered HTML files and add to index."""
    exported = []
    if not source_dir.exists():
        print(f"  skipping {source_dir} (not found)")
        return exported

    out_path = output_dir / subdir
    out_path.mkdir(parents=True, exist_ok=True)

    for html_file in sorted(source_dir.glob(pattern), reverse=True):
        dest = out_path / html_file.name
        shutil.copy2(html_file, dest)
        print(f"  copied: {dest}")

        title = parse_notebook_title(html_file.name)
        exported.append({
            "path": f"{subdir}/{html_file.name}",
            "title": title,
            "category": category
        })

    return exported


def copy_media_directory(source_dir: Path, output_dir: Path, subdir: str, category: str, pattern: str = "*.mp4") -> list[dict]:
    """copy media files and create viewer pages."""
    exported = []
    if not source_dir.exists():
        print(f"  skipping {source_dir} (not found)")
        return exported

    out_path = output_dir / subdir
    out_path.mkdir(parents=True, exist_ok=True)

    for media_file in sorted(source_dir.glob(pattern), reverse=True):
        dest = out_path / media_file.name
        shutil.copy2(media_file, dest)
        print(f"  copied media: {dest}")

        # create simple viewer page
        title = media_file.stem.replace('-', ' ').replace('_', ' ').title()
        viewer_html = HTML_TEMPLATE.format(
            title=title,
            content=f'''
<nav class="week-nav">
    <span class="nav-prev"></span>
    <a href="../../compute/index.html" class="nav-index">← Back</a>
    <span class="nav-next"></span>
</nav>
<h1>{title}</h1>
<video src="{media_file.name}" controls style="max-width:100%;"></video>
'''
        )
        viewer_path = out_path / f"{media_file.stem}.html"
        viewer_path.write_text(viewer_html, encoding='utf-8')

        exported.append({
            "path": f"{subdir}/{media_file.stem}.html",
            "title": title,
            "category": category
        })

    return exported


def export_additional_pages(output_dir: Path) -> list[dict]:
    """export additional pages from exports.toml config."""
    config = load_exports_config()
    exported = []

    # individual pages
    for page in config.get("pages", []):
        source = Path(page["source"])
        if not source.is_absolute():
            source = DOCS_ROOT / source
        output_file = output_dir / page["output"]
        title = page.get("title", source.stem)
        category = page.get("category", "Other")

        result = export_page(source, output_file, title)
        if result:
            exported.append({
                "path": page["output"],
                "title": title,
                "category": category
            })

    # markdown directories
    for dir_config in config.get("directories", []):
        source_dir = Path(dir_config["source"])
        subdir = dir_config.get("output_subdir", "pages")
        category = dir_config.get("category", "Other")
        pattern = dir_config.get("pattern", "*.md")

        # use SOP title parser for sop directories
        title_parser = parse_sop_title if "sop" in subdir.lower() else None

        print(f"scanning {source_dir} for {pattern}...")
        exported.extend(export_directory_markdown(source_dir, output_dir, subdir, category, pattern, title_parser))

    # pre-rendered HTML directories
    for dir_config in config.get("html_directories", []):
        source_dir = Path(dir_config["source"])
        subdir = dir_config.get("output_subdir", "html")
        category = dir_config.get("category", "Other")
        pattern = dir_config.get("pattern", "*.html")

        print(f"copying HTML from {source_dir}...")
        exported.extend(copy_html_directory(source_dir, output_dir, subdir, category, pattern))

    # media directories (videos, etc)
    for dir_config in config.get("media_directories", []):
        source_dir = Path(dir_config["source"])
        subdir = dir_config.get("output_subdir", "media")
        category = dir_config.get("category", "Media")
        pattern = dir_config.get("pattern", "*.mp4")

        print(f"copying media from {source_dir}...")
        exported.extend(copy_media_directory(source_dir, output_dir, subdir, category, pattern))

    return exported


def build_index_with_categories(output_dir: Path, additional_pages: list[dict] = None) -> Path | None:
    """build index.html with weekly reports and additional pages by category."""
    html_files = sorted(output_dir.glob("????-W??.html"), reverse=True)

    items = []

    # weekly reports section
    if html_files:
        items.append('<h2>Weekly Reports</h2>')
        items.append('<ul class="week-list">')
        for html_file in html_files:
            week_id = html_file.stem
            try:
                year, week = parse_week_id(week_id)
                monday, sunday = get_week_dates(year, week)
                week_range = f"{monday.strftime('%B %d')} - {sunday.strftime('%B %d, %Y')}"
                items.append(f'''
<li class="week-item">
    <a href="{html_file.name}">{week_id}</a>
    <span class="week-range">{week_range}</span>
</li>''')
            except ValueError:
                items.append(f'<li class="week-item"><a href="{html_file.name}">{week_id}</a></li>')
        items.append('</ul>')

    # additional pages by category
    if additional_pages:
        by_category = {}
        for page in additional_pages:
            cat = page["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(page)

        for category, pages in sorted(by_category.items()):
            items.append(f'<h2>{category}</h2>')
            items.append('<ul class="week-list">')
            for page in pages:
                items.append(f'''
<li class="week-item">
    <a href="{page["path"]}">{page["title"]}</a>
</li>''')
            items.append('</ul>')

    if not items:
        return None

    index_html = HTML_TEMPLATE.format(
        title="Weekly Meeting Notes",
        content=f'''
<h1>Weekly Meeting Notes</h1>
<p class="index-meta">Last updated: {datetime.now().strftime("%B %d, %Y at %H:%M")}</p>
{"".join(items)}
'''
    )

    index_file = output_dir / "index.html"
    index_file.write_text(index_html, encoding='utf-8')
    print(f"created index: {index_file}")
    return index_file


def sync_to_destination(weekly_dest: Path, compute_dest: Path, force: bool = False) -> list[Path]:
    """export weekly reports to main folder, compute to subfolder."""
    if not weekly_dest.parent.exists():
        print(f"ERROR: path not found: {weekly_dest.parent}")
        return []

    weekly_dest.mkdir(parents=True, exist_ok=True)
    compute_dest.mkdir(parents=True, exist_ok=True)

    print(f"syncing weekly to: {weekly_dest}")
    results = export_all_weeks(weekly_dest, force=force)

    # export additional pages to compute subfolder
    print(f"syncing compute to: {compute_dest}")
    additional = export_additional_pages(compute_dest)

    # build clean index with just weekly reports
    build_index(weekly_dest)

    # build compute index
    if additional:
        build_compute_index(compute_dest, additional)

    return results


def build_compute_index(output_dir: Path, pages: list[dict]) -> Path | None:
    """build index for compute (notebooks, SOPs)."""
    if not pages:
        return None

    by_category = {}
    for page in pages:
        cat = page["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(page)

    items = []
    for category, cat_pages in sorted(by_category.items()):
        items.append(f'<h2>{category}</h2>')
        items.append('<ul class="week-list">')
        for page in cat_pages:
            # path is relative to compute folder
            items.append(f'''
<li class="week-item">
    <a href="{page["path"]}">{page["title"]}</a>
</li>''')
        items.append('</ul>')

    index_html = HTML_TEMPLATE.format(
        title="Compute",
        content=f'''
<nav class="week-nav">
    <span class="nav-prev"></span>
    <a href="../index.html" class="nav-index">← Weekly Reports</a>
    <span class="nav-next"></span>
</nav>
<h1>Compute</h1>
<p class="index-meta">SOPs, Processing Notebooks, and other documentation</p>
{"".join(items)}
'''
    )

    index_file = output_dir / "index.html"
    index_file.write_text(index_html, encoding='utf-8')
    print(f"created compute index: {index_file}")
    return index_file


def sync_to_onedrive(force: bool = False) -> list[Path]:
    """export all weeks to OneDrive."""
    return sync_to_destination(ONEDRIVE_WEEKLY, ONEDRIVE_COMPUTE, force)


def sync_processing_direct(dest: Path) -> None:
    """copy processing notebooks directly to Y:/foconnell/processing/ for direct links."""
    import shutil
    source = Path.home() / "repos" / "docs" / "processing"
    if not source.exists():
        return

    dest.mkdir(parents=True, exist_ok=True)
    for html_file in source.glob("*.html"):
        shutil.copy2(html_file, dest / html_file.name)
        print(f"  synced: {dest / html_file.name}")


def mirror_repo_to_network() -> bool:
    """mirror local docs repo to Y:/foconnell/notebook using robocopy."""
    source = Path.home() / "repos" / "docs"
    dest = NETWORK_NOTEBOOK

    if not source.exists():
        print(f"ERROR: source not found: {source}")
        return False

    if not dest.parent.exists():
        print(f"ERROR: network path not found: {dest.parent}")
        return False

    print(f"mirroring {source} -> {dest}")

    # robocopy with mirror mode, excluding .git, .venv, .obsidian, exports
    result = subprocess.run([
        "robocopy",
        str(source),
        str(dest),
        "/MIR",  # mirror mode
        "/XD", ".git", ".venv", ".obsidian", "exports", "docs", "__pycache__",  # exclude dirs
        "/XF", "*.pyc", ".env",  # exclude files
        "/NFL", "/NDL",  # reduce output noise
        "/NJH", "/NJS",  # no job header/summary
        "/NC", "/NS",  # no class/size
        "/R:1", "/W:1",  # reduce retries
    ], capture_output=True, text=True)

    # robocopy returns 0-7 for success, 8+ for errors
    if result.returncode >= 8:
        print(f"ERROR: robocopy failed with code {result.returncode}")
        print(result.stderr)
        return False

    print(f"  mirrored to: {dest}")
    return True


def sync_to_network(force: bool = False) -> list[Path]:
    """export all weeks to network share (Y: drive)."""
    results = sync_to_destination(NETWORK_WEEKLY, NETWORK_COMPUTE, force)

    # also copy processing notebooks directly to Y:/foconnell/processing/
    print(f"syncing processing to: {NETWORK_PROCESSING}")
    sync_processing_direct(NETWORK_PROCESSING)

    return results


def sync_all(force: bool = False) -> list[Path]:
    """sync to both OneDrive and network share."""
    results = []

    # mirror source repo first
    print("=" * 50)
    print("MIRRORING SOURCE REPO")
    print("=" * 50)
    mirror_repo_to_network()

    # sync to OneDrive
    print()
    print("=" * 50)
    print("SYNCING TO ONEDRIVE")
    print("=" * 50)
    results.extend(sync_to_onedrive(force))

    # sync to network
    print()
    print("=" * 50)
    print("SYNCING TO NETWORK (Y: drive)")
    print("=" * 50)
    results.extend(sync_to_network(force))

    return results


def load_resolved_backlog() -> set[str]:
    """load resolved items from backlog.md."""
    backlog_file = DOCS_ROOT / "backlog.md"
    if not backlog_file.exists():
        return set()

    resolved = set()
    content = backlog_file.read_text(encoding='utf-8')
    for line in content.split('\n'):
        match = re.match(r'^-\s*\[[xX]\]\s*(.+)$', line.strip())
        if match:
            resolved.add(match.group(1).strip())
    return resolved


def is_resolved(item: str, resolved: set[str]) -> bool:
    """check if a backlog item matches any resolved item (substring matching)."""
    item_lower = item.lower()
    for r in resolved:
        r_lower = r.lower()
        # exact match, or either contains the other
        if item_lower == r_lower or item_lower in r_lower or r_lower in item_lower:
            return True
    return False


def collect_backlog(current_week_id: str) -> list[dict]:
    """collect unchecked TO-DO items from all previous weeks.

    filters out items resolved in backlog.md or checked in any week.
    uses substring matching so slightly different wording still resolves.
    returns list of dicts with 'week', 'items' keys, oldest first.
    """
    all_weeks = discover_all_weeks()
    resolved = load_resolved_backlog()

    # also collect all checked items from all weeks as resolved
    for wid in all_weeks:
        weekly_file = find_weekly_note(wid)
        if not weekly_file:
            continue
        content = weekly_file.read_text(encoding='utf-8')
        for line in content.split('\n'):
            match = re.match(r'^-\s*\[[xX]\]\s*(.+)$', line.strip())
            if match:
                resolved.add(match.group(1).strip())

    backlog = []

    for wid in all_weeks:
        if wid >= current_week_id:
            break

        weekly_file = find_weekly_note(wid)
        if not weekly_file:
            continue

        content = weekly_file.read_text(encoding='utf-8')

        # find all TO-DO sections (previous, next, or just "TO DO")
        todo_pattern = re.compile(
            r'##\s*(?:\((?:previous|next)\)\s*)?TO-?DO.*?\n(.*?)(?=\n##|\Z)',
            re.IGNORECASE | re.DOTALL
        )

        unchecked = []
        for match in todo_pattern.finditer(content):
            section = match.group(1)
            for line in section.split('\n'):
                task_match = re.match(r'^-\s*\[ \]\s*(.+)$', line.strip())
                if task_match:
                    item = task_match.group(1).strip()
                    if item and not is_resolved(item, resolved):
                        unchecked.append(item)

        if unchecked:
            backlog.append({'week': wid, 'items': unchecked})

    return backlog


def extract_next_todos(week_id: str) -> list[str]:
    """extract TO-DO items from a week's (Next) TO-DO section."""
    weekly_file = find_weekly_note(week_id)
    if not weekly_file:
        return []

    content = weekly_file.read_text(encoding='utf-8')

    # find (Next) TO-DO section
    pattern = re.compile(
        r'##\s*\(Next\)\s*TO-?DO.*?\n(.*?)(?=\n##|\Z)',
        re.IGNORECASE | re.DOTALL
    )
    match = pattern.search(content)
    if not match:
        return []

    section = match.group(1)
    todos = []
    for line in section.split('\n'):
        # match task items (checked or unchecked)
        task_match = re.match(r'^-\s*\[.\]\s*(.+)$', line.strip())
        if task_match:
            todos.append(task_match.group(1).strip())

    return todos


def get_next_week_id(week_id: str) -> str:
    """get the next week's ID."""
    year, week = parse_week_id(week_id)
    # handle year rollover
    next_week = week + 1
    next_year = year
    if next_week > 52:
        # check if week 53 exists for this year
        dec_31 = datetime(year, 12, 31)
        max_week = dec_31.isocalendar()[1]
        if next_week > max_week:
            next_week = 1
            next_year = year + 1
    return f"{next_year}-W{next_week:02d}"


def create_next_week_note(current_week_id: str) -> Path | None:
    """create next week's note with current week's TO-DO items as Previous TO-DO."""
    next_week_id = get_next_week_id(current_week_id)
    next_file = WEEKLY_DIR / f"{next_week_id}.md"

    if next_file.exists():
        print(f"  {next_week_id}.md already exists")
        return next_file

    # get current week's TO-DO items
    todos = extract_next_todos(current_week_id)

    # calculate date range for next week
    year, week = parse_week_id(next_week_id)
    monday, sunday = get_week_dates(year, week)
    week_range = f"{monday.strftime('%B %d')} - {sunday.strftime('%B %d, %Y')}"
    following_week_id = get_next_week_id(next_week_id)

    # build the note content
    todo_items = '\n'.join(f"- [ ] {todo}" for todo in todos) if todos else "- [ ]"

    content = f"""---
tags: [weekly, meeting, log]
template: Weekly Meetings
date: {monday.strftime('%Y-%m-%d')}
---

# Weekly Meeting – {week_range}

## (previous) TO-DO
*from [[{current_week_id}]]*
{todo_items}

## Weekly Overview


## Main Projects

#### mbo_utilities
-

#### LBM-Suite2p-Python
-

#### IsoView
-

## Offshoot Projects
-

## Collaborations
-

## Compute/Storage Server Usage
-

## Data: `MBO_DATA`
-

## Research Papers / Packages
-

## Misc
-

## (Next) TO-DO
*for [[{following_week_id}]]*
- [ ]
"""

    next_file.write_text(content, encoding='utf-8')
    print(f"  created: {next_file}")
    return next_file


def open_in_firefox(path: Path) -> None:
    """open a file in Firefox."""
    if not path.exists():
        print(f"  cannot open: {path} (not found)")
        return
    # try common Firefox locations on Windows
    firefox_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ]
    for firefox in firefox_paths:
        if os.path.exists(firefox):
            subprocess.Popen([firefox, str(path)])
            print(f"  opened in Firefox: {path}")
            return
    # fallback to system default
    import sys
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])
    print(f"  opened: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="export weekly notes with embedded daily notes as static HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
examples:
    # export current week to local exports
    uv run export-weekly

    # export specific week
    uv run export-weekly 2026-W03

    # sync all weeks to OneDrive (won't overwrite existing)
    uv run export-weekly --sync

    # force overwrite (backs up existing to X: drive)
    uv run export-weekly --sync --force

    # export all to custom directory
    uv run export-weekly --all -o ./exports

    # create next week's note with current TO-DOs
    uv run export-weekly --next

destinations:
    local:    {LOCAL_EXPORT_DIR / 'weekly'}
    onedrive: {ONEDRIVE_WEEKLY}
    network:  {NETWORK_WEEKLY}
        """
    )

    parser.add_argument(
        'week',
        type=str,
        nargs='?',
        metavar='YYYY-Www',
        help="week to export (default: current week)"
    )

    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help="export all available weeks"
    )

    parser.add_argument(
        '--sync', '-s',
        action='store_true',
        help="sync to both OneDrive and network share (Y: drive)"
    )

    parser.add_argument(
        '--onedrive',
        action='store_true',
        help="sync to OneDrive only"
    )

    parser.add_argument(
        '--network',
        action='store_true',
        help="sync to network share only (Y:/foconnell/weekly_meeting)"
    )

    parser.add_argument(
        '--mirror', '-m',
        action='store_true',
        help="mirror source repo to Y:/foconnell/notebook (included in --sync)"
    )

    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help="overwrite existing files"
    )

    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=None,
        help=f"output directory (default: {LOCAL_EXPORT_DIR / 'weekly'})"
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help="list available weeks and exit"
    )

    parser.add_argument(
        '--next', '-n',
        action='store_true',
        help="create next week's note with current week's TO-DOs (local only)"
    )

    parser.add_argument(
        '--open',
        action='store_true',
        help="open the index.html in Firefox after export"
    )

    args = parser.parse_args()

    # handle --list
    if args.list:
        weeks = discover_all_weeks()
        if weeks:
            print("available weeks:")
            for week_id in weeks:
                year, week = parse_week_id(week_id)
                monday, sunday = get_week_dates(year, week)
                daily_count = len(find_daily_notes(year, week))
                print(f"  {week_id}: {monday.strftime('%b %d')} - {sunday.strftime('%b %d, %Y')} ({daily_count} daily notes)")
        else:
            print("no weekly notes found")
        return

    # handle --next (create next week's note locally)
    if args.next:
        current_week = args.week or get_current_week_id()
        try:
            parse_week_id(current_week)
        except ValueError as e:
            print(f"ERROR: {e}")
            sys.exit(1)

        result = create_next_week_note(current_week)
        if result:
            todos = extract_next_todos(current_week)
            print(f"\ncreated next week's note with {len(todos)} TO-DO items from {current_week}")
        return

    # handle --sync (export to OneDrive)
    # handle sync options
    if args.sync:
        sync_all(force=args.force)
        print(f"\nsynced to:")
        print(f"  Mirror:   {NETWORK_NOTEBOOK}")
        print(f"  OneDrive: {ONEDRIVE_WEEKLY}")
        print(f"  Network:  {NETWORK_WEEKLY}")
        if args.open:
            open_in_firefox(NETWORK_WEEKLY / "index.html")
        return

    if args.onedrive:
        sync_to_onedrive(force=args.force)
        print(f"\nsynced to OneDrive: {ONEDRIVE_WEEKLY}")
        if args.open:
            open_in_firefox(ONEDRIVE_WEEKLY / "index.html")
        return

    if args.network:
        sync_to_network(force=args.force)
        print(f"\nsynced to network: {NETWORK_WEEKLY}")
        if args.open:
            open_in_firefox(NETWORK_WEEKLY / "index.html")
        return

    if args.mirror:
        mirror_repo_to_network()
        print(f"\nmirrored to: {NETWORK_NOTEBOOK}")
        return

    # determine output directory
    output_dir = args.output_dir or (LOCAL_EXPORT_DIR / "weekly")
    compute_dir = output_dir / "compute"

    if args.all:
        results = export_all_weeks(output_dir, force=args.force)
        if results:
            # export additional pages (software, sops, processing)
            additional = export_additional_pages(compute_dir)
            build_index(output_dir)
            if additional:
                build_compute_index(compute_dir, additional)
            print(f"\nexported {len(results)} weeks to: {output_dir}")
            if args.open:
                open_in_firefox(output_dir / "index.html")
    else:
        week_id = args.week or get_current_week_id()
        try:
            parse_week_id(week_id)
        except ValueError as e:
            print(f"ERROR: {e}")
            sys.exit(1)

        weeks = discover_all_weeks()
        result = export_week(week_id, output_dir, all_weeks=weeks, force=args.force)
        if result:
            # export additional pages (software, sops, processing)
            additional = export_additional_pages(compute_dir)
            build_index(output_dir)
            if additional:
                build_compute_index(compute_dir, additional)
            print(f"\nexported to: {result}")
            if args.open:
                open_in_firefox(output_dir / "index.html")
        else:
            print(f"no content found for {week_id}")
            sys.exit(1)


if __name__ == "__main__":
    main()
