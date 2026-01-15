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

    # export to specific directory
    uv run export-weekly -o ./exports
"""

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

from scripts.export_note import (
    parse_frontmatter,
    convert_obsidian_images,
    convert_standard_images,
    convert_wikilinks,
    convert_task_lists,
    strip_frontmatter,
)
from scripts.config import LOCAL_EXPORT_DIR

try:
    import markdown
except ImportError:
    print("ERROR: 'markdown' package not found. Install with: pip install markdown")
    sys.exit(1)


# paths relative to this script's parent (docs repo root)
DOCS_ROOT = Path(__file__).parent.parent
WEEKLY_DIR = DOCS_ROOT / "weekly"
DAILY_DIR = DOCS_ROOT / "daily"
IMAGES_DIR = DOCS_ROOT / "notes" / "images"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-color: #ffffff;
            --text-color: #1a1a1a;
            --code-bg: #f5f5f5;
            --border-color: #e0e0e0;
            --link-color: #0066cc;
            --heading-color: #111111;
            --accent-color: #4a90d9;
        }}

        * {{ box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
            font-size: 2em;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.3em;
        }}

        h2 {{
            font-size: 1.5em;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.2em;
        }}

        a {{ color: var(--link-color); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}

        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        code {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            background-color: var(--code-bg);
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }}

        pre {{
            background-color: var(--code-bg);
            padding: 1em;
            border-radius: 6px;
            overflow-x: auto;
            border: 1px solid var(--border-color);
        }}

        pre code {{ background: none; padding: 0; }}

        blockquote {{
            border-left: 4px solid var(--border-color);
            margin-left: 0;
            padding-left: 1em;
            color: #666;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}

        th, td {{
            border: 1px solid var(--border-color);
            padding: 0.5em 1em;
            text-align: left;
        }}

        th {{ background-color: var(--code-bg); font-weight: 600; }}
        tr:nth-child(even) {{ background-color: #fafafa; }}

        ul, ol {{ padding-left: 1.5em; }}
        li {{ margin: 0.25em 0; }}

        hr {{
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 2em 0;
        }}

        .header {{
            margin-bottom: 2em;
            padding-bottom: 1em;
            border-bottom: 2px solid var(--accent-color);
        }}

        .header h1 {{
            margin: 0;
            border: none;
        }}

        .header .meta {{
            color: #666;
            font-size: 0.9em;
            margin-top: 0.5em;
        }}

        .toc {{
            background-color: var(--code-bg);
            padding: 1em 1.5em;
            border-radius: 6px;
            margin-bottom: 2em;
        }}

        .toc h2 {{
            margin-top: 0;
            font-size: 1.1em;
            border: none;
        }}

        .toc ul {{
            margin: 0;
            padding-left: 1.2em;
        }}

        .toc li {{ margin: 0.3em 0; }}
        .toc a {{ color: var(--text-color); }}
        .toc a:hover {{ color: var(--link-color); }}

        .weekly-section {{
            margin-bottom: 3em;
        }}

        .daily-section {{
            margin-top: 3em;
            padding-top: 2em;
            border-top: 3px solid var(--accent-color);
        }}

        .daily-note {{
            margin-bottom: 2em;
            padding: 1.5em;
            background-color: #fafafa;
            border-radius: 8px;
            border-left: 4px solid var(--accent-color);
        }}

        .daily-note h3 {{
            margin-top: 0;
            color: var(--accent-color);
        }}

        .daily-note-empty {{
            color: #999;
            font-style: italic;
        }}

        .task-list-item {{
            list-style-type: none;
            margin-left: -1.5em;
        }}

        .task-list-item input {{
            margin-right: 0.5em;
        }}

        .missing-image {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 1em;
            border-radius: 4px;
            color: #856404;
            text-align: center;
        }}

        @media print {{
            body {{ max-width: none; padding: 1cm; }}
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


def process_markdown(content: str, source_file: Path) -> str:
    """process markdown content, converting images and obsidian syntax."""
    content = strip_frontmatter(content)
    content = convert_obsidian_images(content, source_file, IMAGES_DIR)
    content = convert_standard_images(content, source_file, IMAGES_DIR)
    content = convert_wikilinks(content)
    content = convert_task_lists(content)
    return content


def render_markdown(content: str) -> str:
    """convert markdown to HTML."""
    md = markdown.Markdown(
        extensions=['fenced_code', 'tables', 'toc', 'nl2br', 'sane_lists']
    )
    return md.convert(content)


def build_weekly_report(week_id: str) -> str | None:
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

    # header
    parts.append(f'''
<div class="header">
    <h1>Week {week} Report</h1>
    <div class="meta">{week_range}</div>
</div>
''')

    # table of contents
    toc_items = []
    if weekly_file:
        toc_items.append('<li><a href="#weekly-notes">Weekly Notes</a></li>')
    if daily_notes:
        toc_items.append('<li><a href="#daily-notes">Daily Notes</a>')
        toc_items.append('<ul>')
        for date, _ in daily_notes:
            anchor = date.strftime("%Y-%m-%d")
            label = date.strftime("%A, %B %d")
            toc_items.append(f'<li><a href="#{anchor}">{label}</a></li>')
        toc_items.append('</ul></li>')

    if toc_items:
        parts.append(f'''
<div class="toc">
    <h2>Contents</h2>
    <ul>
        {"".join(toc_items)}
    </ul>
</div>
''')

    # weekly notes section
    if weekly_file:
        print(f"  processing weekly: {weekly_file.name}")
        weekly_content = weekly_file.read_text(encoding='utf-8')

        # replace {{week_range}} placeholder if present
        weekly_content = weekly_content.replace('{{week_range}}', week_range)

        processed = process_markdown(weekly_content, weekly_file)
        html = render_markdown(processed)

        parts.append(f'''
<div class="weekly-section" id="weekly-notes">
    {html}
</div>
''')

    # daily notes section
    if daily_notes:
        parts.append('<div class="daily-section" id="daily-notes">')
        parts.append('<h2>Daily Notes</h2>')

        for date, daily_file in daily_notes:
            anchor = date.strftime("%Y-%m-%d")
            label = date.strftime("%A, %B %d, %Y")
            print(f"  processing daily: {daily_file.name}")

            daily_content = daily_file.read_text(encoding='utf-8')
            processed = process_markdown(daily_content, daily_file)

            if processed.strip():
                html = render_markdown(processed)
                parts.append(f'''
<div class="daily-note" id="{anchor}">
    <h3>{label}</h3>
    {html}
</div>
''')
            else:
                parts.append(f'''
<div class="daily-note" id="{anchor}">
    <h3>{label}</h3>
    <p class="daily-note-empty">No notes recorded.</p>
</div>
''')

        parts.append('</div>')

    return HTML_TEMPLATE.format(
        title=f"Week {week} Report - {week_range}",
        content="".join(parts)
    )


def export_week(week_id: str, output_dir: Path) -> Path | None:
    """export a single week to HTML."""
    print(f"building report for {week_id}...")

    html = build_weekly_report(week_id)
    if html is None:
        print(f"  no content found for {week_id}")
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{week_id}.html"
    output_file.write_text(html, encoding='utf-8')

    print(f"  created: {output_file}")
    return output_file


def export_all_weeks(output_dir: Path) -> list[Path]:
    """export all available weeks to HTML."""
    weeks = discover_all_weeks()
    if not weeks:
        print("no weekly notes found")
        return []

    print(f"found {len(weeks)} weekly notes")
    results = []

    for week_id in weeks:
        result = export_week(week_id, output_dir)
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
            items.append(f'<li><a href="{html_file.name}">{week_id}</a> - {week_range}</li>')
        except ValueError:
            items.append(f'<li><a href="{html_file.name}">{week_id}</a></li>')

    index_html = HTML_TEMPLATE.format(
        title="Weekly Reports Index",
        content=f'''
<div class="header">
    <h1>Weekly Reports</h1>
    <div class="meta">Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
</div>
<ul>
    {"".join(items)}
</ul>
'''
    )

    index_file = output_dir / "index.html"
    index_file.write_text(index_html, encoding='utf-8')
    print(f"created index: {index_file}")
    return index_file


def main():
    parser = argparse.ArgumentParser(
        description="export weekly notes with embedded daily notes as static HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
    # export current week
    uv run export-weekly

    # export specific week
    uv run export-weekly 2026-W03

    # export all weeks
    uv run export-weekly --all

    # export to specific directory
    uv run export-weekly -o ./exports
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

    # determine output directory
    output_dir = args.output_dir or (LOCAL_EXPORT_DIR / "weekly")

    if args.all:
        results = export_all_weeks(output_dir)
        if results:
            build_index(output_dir)
            print(f"\nexported {len(results)} weeks to: {output_dir}")
    else:
        week_id = args.week or get_current_week_id()
        try:
            parse_week_id(week_id)
        except ValueError as e:
            print(f"ERROR: {e}")
            sys.exit(1)

        result = export_week(week_id, output_dir)
        if result:
            print(f"\nexported to: {result}")
        else:
            print(f"no content found for {week_id}")
            sys.exit(1)


if __name__ == "__main__":
    main()
