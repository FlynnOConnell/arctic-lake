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

    # serve locally and auto-rebuild on changes
    uv run export-weekly --watch

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
            --sidebar-width: 240px;
            --toc-width: 200px;
            color-scheme: dark;
        }}

        * {{ box-sizing: border-box; }}

        body {{
            font-family: 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            margin: 0;
            padding: 0;
            display: flex;
            min-height: 100vh;
        }}

        /* mobile header bar */
        .mobile-header {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 48px;
            background: var(--surface-color);
            border-bottom: 1px solid var(--border-color);
            z-index: 100;
            align-items: center;
            padding: 0 1rem;
        }}

        .hamburger {{
            background: none;
            border: none;
            color: var(--text-color);
            font-size: 1.4rem;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 4px;
        }}

        .hamburger:hover {{ background: var(--border-color); }}

        .mobile-title {{
            margin-left: 0.75rem;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--heading-color);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* left sidebar (page nav) */
        .sidebar-left {{
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            width: var(--sidebar-width);
            background: var(--surface-color);
            border-right: 1px solid var(--border-color);
            overflow-y: auto;
            padding: 1rem 0;
            z-index: 90;
            font-size: 0.82rem;
        }}

        .sidebar-left::-webkit-scrollbar {{ width: 4px; }}
        .sidebar-left::-webkit-scrollbar-thumb {{ background: var(--border-color); border-radius: 2px; }}

        .sidebar-brand {{
            padding: 0.25rem 1rem 0.75rem;
            font-weight: 700;
            font-size: 0.9rem;
            color: var(--heading-color);
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 0.5rem;
        }}

        .sidebar-brand a {{
            color: var(--heading-color);
            text-decoration: none;
        }}

        .sidebar-brand a:hover {{ color: var(--accent-color); }}

        .nav-section {{
            margin-bottom: 0.1rem;
        }}

        .nav-section-title {{
            padding: 0.35rem 0.5rem 0.35rem 0.75rem;
            font-weight: 600;
            font-size: 0.78rem;
            color: var(--text-color);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.3rem;
            user-select: none;
            border-radius: 3px;
        }}

        .nav-section-title:hover {{ background: rgba(255,255,255,0.04); }}

        .nav-section-title::before {{
            content: '';
            width: 0;
            height: 0;
            border-style: solid;
            border-width: 4px 0 4px 6px;
            border-color: transparent transparent transparent var(--text-muted);
            transition: transform 0.12s;
            flex-shrink: 0;
            margin-right: 0.15rem;
        }}

        .nav-section.open .nav-section-title::before {{
            transform: rotate(90deg);
        }}

        .nav-section-items {{
            display: none;
            padding: 0 0 0 0.85rem;
            margin: 0.1rem 0 0.25rem 0.85rem;
            list-style: none;
            border-left: 1px solid var(--border-color);
        }}

        .nav-section.open .nav-section-items {{
            display: block;
        }}

        .nav-item a {{
            display: block;
            padding: 0.2rem 0.5rem 0.2rem 0.75rem;
            color: var(--text-muted);
            text-decoration: none;
            border-left: 2px solid transparent;
            margin-left: -1px;
            transition: background 0.08s, color 0.08s;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 0.8rem;
            border-radius: 0 3px 3px 0;
        }}

        .nav-item a:hover {{
            color: var(--text-color);
            background: rgba(255,255,255,0.04);
        }}

        .nav-item.active a {{
            color: var(--accent-color);
            border-left-color: var(--accent-color);
            background: rgba(130,170,255,0.1);
            font-weight: 600;
        }}

        /* overlay for mobile sidebar */
        .sidebar-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            z-index: 85;
        }}

        /* center content */
        .content-wrapper {{
            margin-left: var(--sidebar-width);
            margin-right: var(--toc-width);
            flex: 1;
            min-width: 0;
            padding: 2rem 2.5rem;
            max-width: 900px;
        }}

        /* right sidebar (table of contents) */
        .sidebar-right {{
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            width: var(--toc-width);
            background: var(--bg-color);
            border-left: 1px solid var(--border-color);
            overflow-y: auto;
            padding: 1.5rem 0.75rem;
            font-size: 0.75rem;
            z-index: 80;
        }}

        .sidebar-right::-webkit-scrollbar {{ width: 4px; }}
        .sidebar-right::-webkit-scrollbar-thumb {{ background: var(--border-color); border-radius: 2px; }}

        .toc-title {{
            font-weight: 700;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            padding-bottom: 0.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
        }}

        .toc-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .toc-list a {{
            display: block;
            padding: 0.2rem 0;
            color: var(--text-muted);
            text-decoration: none;
            border-left: 2px solid transparent;
            padding-left: 0.5rem;
            transition: color 0.1s;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .toc-list a:hover {{ color: var(--text-color); }}

        .toc-list a.active {{
            color: var(--accent-color);
            border-left-color: var(--accent-color);
        }}

        .toc-list .toc-h3 {{
            padding-left: 1.2rem;
            font-size: 0.7rem;
        }}

        /* standard content styles */
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

        /* distinct bullet styles per nesting level (like VSCode) */
        ul {{ list-style-type: disc; }}
        ul ul {{ list-style-type: circle; }}
        ul ul ul {{ list-style-type: square; }}
        ul ul ul ul {{ list-style-type: disc; }}

        ul > li::marker {{ color: var(--accent-color); }}
        ul ul > li::marker {{ color: var(--text-muted); }}
        ul ul ul > li::marker {{ color: var(--text-muted); }}

        /* collapsible nested lists */
        .collapsible-li {{
            list-style: none;
            margin-left: -1em;
        }}

        .collapsible-li > .list-toggle {{
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.4em;
        }}

        .collapsible-li > .list-toggle::before {{
            content: '▶';
            font-size: 0.6em;
            transition: transform 0.15s;
            color: var(--text-muted);
        }}

        .collapsible-li.expanded > .list-toggle::before {{
            transform: rotate(90deg);
        }}

        .collapsible-li > .list-toggle:hover::before {{
            color: var(--accent-color);
        }}

        .collapsible-li > ul {{
            display: none;
            margin-top: 0.25em;
        }}

        .collapsible-li.expanded > ul {{
            display: block;
        }}

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

        /* responsive: hide right TOC below 1100px */
        @media (max-width: 1100px) {{
            .sidebar-right {{ display: none; }}
            .content-wrapper {{ margin-right: 0; }}
        }}

        /* responsive: slide-in left sidebar below 800px */
        @media (max-width: 800px) {{
            .mobile-header {{ display: flex; }}
            .sidebar-left {{
                transform: translateX(-100%);
                transition: transform 0.2s ease;
            }}
            .sidebar-left.open {{
                transform: translateX(0);
            }}
            .sidebar-overlay.open {{
                display: block;
            }}
            .content-wrapper {{
                margin-left: 0;
                padding: 60px 1.5rem 2rem;
            }}
        }}

        @media print {{
            .sidebar-left, .sidebar-right, .mobile-header, .sidebar-overlay {{ display: none !important; }}
            .content-wrapper {{
                margin: 0;
                padding: 1cm;
                max-width: none;
            }}
            body {{
                background-color: #fff;
                color: #000;
                display: block;
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
    <div class="mobile-header">
        <button class="hamburger" onclick="toggleSidebar()" aria-label="Toggle navigation">☰</button>
        <span class="mobile-title">{title}</span>
    </div>
    <div class="sidebar-overlay" onclick="toggleSidebar()"></div>
    <nav class="sidebar-left">
        <div class="sidebar-brand"><a href="index.html">Weekly Notes</a></div>
        {sidebar_nav}
    </nav>
    <main class="content-wrapper">
        {content}
    </main>
    <aside class="sidebar-right">
        <div class="toc-title">On this page</div>
        <ul class="toc-list" id="toc-list"></ul>
    </aside>
    <script>
    // toggle mobile sidebar
    function toggleSidebar() {{
        document.querySelector('.sidebar-left').classList.toggle('open');
        document.querySelector('.sidebar-overlay').classList.toggle('open');
    }}

    // build TOC from h2/h3 in content
    (function() {{
        var wrapper = document.querySelector('.content-wrapper');
        var toc = document.getElementById('toc-list');
        if (!wrapper || !toc) return;
        var headings = wrapper.querySelectorAll('h2, h3');
        if (headings.length === 0) {{ document.querySelector('.sidebar-right').style.display = 'none'; return; }}
        headings.forEach(function(h) {{
            if (!h.id) h.id = h.textContent.trim().toLowerCase().replace(/[^\\w]+/g, '-');
            var li = document.createElement('li');
            if (h.tagName === 'H3') li.className = 'toc-h3';
            var a = document.createElement('a');
            a.href = '#' + h.id;
            a.textContent = h.textContent;
            li.appendChild(a);
            toc.appendChild(li);
        }});
        // scroll-spy via IntersectionObserver
        var links = toc.querySelectorAll('a');
        var observer = new IntersectionObserver(function(entries) {{
            entries.forEach(function(e) {{
                if (e.isIntersecting) {{
                    links.forEach(function(l) {{ l.classList.remove('active'); }});
                    var match = toc.querySelector('a[href="#' + e.target.id + '"]');
                    if (match) match.classList.add('active');
                }}
            }});
        }}, {{ rootMargin: '0px 0px -70% 0px', threshold: 0 }});
        headings.forEach(function(h) {{ observer.observe(h); }});
    }})();

    // auto-open nav section containing active page
    (function() {{
        var active = document.querySelector('.nav-item.active');
        if (active) {{
            var section = active.closest('.nav-section');
            if (section) section.classList.add('open');
        }}
    }})();

    // make nested lists collapsible
    (function() {{
        var content = document.querySelector('.content-wrapper');
        if (!content) return;

        // find all li elements that have nested ul children
        var items = content.querySelectorAll('li');
        items.forEach(function(li) {{
            var nestedUl = li.querySelector(':scope > ul');
            if (!nestedUl) return;

            li.classList.add('collapsible-li');

            // wrap the text content in a toggle span
            var toggle = document.createElement('span');
            toggle.className = 'list-toggle';

            // move all direct child nodes except ul into the toggle
            var nodesToMove = [];
            li.childNodes.forEach(function(node) {{
                if (node !== nestedUl && node.nodeType !== 8) {{
                    nodesToMove.push(node);
                }}
            }});
            nodesToMove.forEach(function(node) {{
                toggle.appendChild(node);
            }});
            li.insertBefore(toggle, nestedUl);

            // click handler to toggle
            toggle.addEventListener('click', function(e) {{
                li.classList.toggle('expanded');
            }});

            // determine depth: count parent ul elements
            var depth = 0;
            var parent = li.parentElement;
            while (parent && parent !== content) {{
                if (parent.tagName === 'UL') depth++;
                parent = parent.parentElement;
            }}

            // expand only top-level items (depth 1 = first ul in content)
            if (depth === 1) {{
                li.classList.add('expanded');
            }}
        }});
    }})();
    </script>
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


def normalize_list_indentation(content: str) -> str:
    """normalize 2-space indentation to 4-space for markdown list parsing."""
    lines = content.split('\n')
    result = []
    for line in lines:
        # match lines starting with spaces followed by - or * or digit.
        match = re.match(r'^( +)([-*]|\d+\.) ', line)
        if match:
            spaces = match.group(1)
            # count indent level based on 2-space or 4-space increments
            # convert to 4-space increments for markdown parser
            if len(spaces) % 4 == 0:
                # already 4-space, keep as is
                result.append(line)
            else:
                # assume 2-space indentation, convert to 4-space
                indent_level = len(spaces) // 2
                new_indent = '    ' * indent_level
                result.append(new_indent + line.lstrip())
        else:
            result.append(line)
    return '\n'.join(result)


def process_markdown(content: str, source_file: Path, output_dir: Path | None = None) -> str:
    """process markdown content, converting images/videos and obsidian syntax."""
    content = strip_frontmatter(content)
    content = normalize_list_indentation(content)
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


def discover_additional_pages() -> list[dict]:
    """scan exports.toml to enumerate pages as metadata (no file I/O)."""
    config = load_exports_config()
    pages = []

    for page in config.get("pages", []):
        source = Path(page["source"])
        if not source.is_absolute():
            source = DOCS_ROOT / source
        pages.append({
            "path": page["output"],
            "title": page.get("title", source.stem),
            "category": page.get("category", "Other"),
        })

    for dir_config in config.get("directories", []):
        source_dir = Path(dir_config["source"])
        subdir = dir_config.get("output_subdir", "pages")
        category = dir_config.get("category", "Other")
        pattern = dir_config.get("pattern", "*.md")
        title_parser = parse_sop_title if "sop" in subdir.lower() else None
        if source_dir.exists():
            for md_file in sorted(source_dir.glob(pattern)):
                title = title_parser(md_file.name) if title_parser else md_file.stem.replace('-', ' ').replace('_', ' ').title()
                pages.append({
                    "path": f"{subdir}/{md_file.stem}.html",
                    "title": title,
                    "category": category,
                })

    for dir_config in config.get("html_directories", []):
        source_dir = Path(dir_config["source"])
        subdir = dir_config.get("output_subdir", "html")
        category = dir_config.get("category", "Other")
        pattern = dir_config.get("pattern", "*.html")
        if source_dir.exists():
            html_files = list(source_dir.glob(pattern))
            # sort by date: leading YYYY-MM-DD or trailing _YYYYMMDD, newest first
            def _nb_sort_key(f):
                stem = f.stem
                leading = re.match(r'^(\d{4}-\d{2}-\d{2})', stem)
                if leading:
                    return leading.group(1)
                trailing = re.search(r'_(\d{8})$', stem)
                if trailing:
                    d = trailing.group(1)
                    return f"{d[:4]}-{d[4:6]}-{d[6:]}"
                return "0000-00-00"
            for html_file in sorted(html_files, key=_nb_sort_key, reverse=True):
                pages.append({
                    "path": f"{subdir}/{html_file.stem}.html",
                    "title": parse_notebook_title(html_file.name),
                    "category": category,
                })

    for dir_config in config.get("media_directories", []):
        source_dir = Path(dir_config["source"])
        subdir = dir_config.get("output_subdir", "media")
        category = dir_config.get("category", "Media")
        pattern = dir_config.get("pattern", "*.mp4")
        if source_dir.exists():
            for media_file in sorted(source_dir.glob(pattern), reverse=True):
                pages.append({
                    "path": f"{subdir}/{media_file.stem}.html",
                    "title": media_file.stem.replace('-', ' ').replace('_', ' ').title(),
                    "category": category,
                })

    return pages


def build_nav_tree(weeks: list[str], additional_pages: list[dict]) -> dict[str, list[dict]]:
    """organize pages into {category: [page_dicts]} for sidebar rendering.

    all paths are stored root-relative (from the serve root).
    weekly reports: "2026-W08.html"
    additional pages: "compute/software/webknossos.html"
    """
    tree: dict[str, list[dict]] = {}

    if weeks:
        tree["Weekly Reports"] = [
            {"path": f"{w}.html", "title": w} for w in reversed(weeks)
        ]

    for page in additional_pages:
        cat = page["category"]
        if cat not in tree:
            tree[cat] = []
        # prefix with compute/ so paths are root-relative
        root_path = page["path"]
        if not root_path.startswith("compute/"):
            root_path = f"compute/{root_path}"
        tree[cat].append({"path": root_path, "title": page["title"]})

    return tree


def render_sidebar_html(nav_tree: dict[str, list[dict]], current_page_path: str) -> str:
    """render left sidebar HTML with active state and collapsible sections.

    computes relative hrefs from the current page to each target.
    """
    import posixpath

    current_dir = posixpath.dirname(current_page_path)

    parts = []
    for category, pages in nav_tree.items():
        has_active = any(p["path"] == current_page_path for p in pages)
        open_cls = " open" if has_active else ""

        parts.append(f'<div class="nav-section{open_cls}">')
        parts.append(f'<div class="nav-section-title" onclick="this.parentElement.classList.toggle(\'open\')">{category}</div>')
        parts.append('<ul class="nav-section-items">')
        for page in pages:
            active = " active" if page["path"] == current_page_path else ""
            href = posixpath.relpath(page["path"], current_dir)
            parts.append(f'<li class="nav-item{active}"><a href="{href}">{page["title"]}</a></li>')
        parts.append('</ul>')
        parts.append('</div>')

    return "\n".join(parts)


def build_weekly_report(
    week_id: str,
    output_dir: Path,
    prev_week: str | None = None,
    next_week: str | None = None,
    sidebar_nav: str = "",
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

    # backlog section (flat priority list from backlog.md)
    backlog = collect_backlog(week_id)
    if backlog:
        parts.append(f'''
<details class="callout callout-backlog" id="backlog">
<summary>Backlog ({len(backlog)} items)</summary>
<div class="callout-content">
<ul>''')
        for item in backlog:
            if item['status'] == '~':
                css = 'task-partial'
                checkbox = '<span class="checkbox partial"></span>'
            else:
                css = 'task-open'
                checkbox = '<span class="checkbox"></span>'
            week_tag = f' <em>(W{item["origin_week"]})</em>' if item.get('origin_week') else ''
            parts.append(f'<li class="task-item {css}">{checkbox} {convert_inline_code(item["text"])}{week_tag}</li>')
        parts.append('</ul>')
        parts.append('</div>')
        parts.append('</details>')

    # bottom navigation
    parts.append(''.join(nav_parts))

    return HTML_TEMPLATE.format(
        title=f"Weekly Meeting – {week_range}",
        content="".join(parts),
        sidebar_nav=sidebar_nav,
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
    force: bool = False,
    sidebar_nav: str = "",
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

    html = build_weekly_report(week_id, output_dir, prev_week, next_week, sidebar_nav=sidebar_nav)
    if html is None:
        print(f"  no content found for {week_id}")
        return None

    output_file.write_text(html, encoding='utf-8')
    print(f"  created: {output_file}")
    return output_file


def export_all_weeks(output_dir: Path, force: bool = False, nav_tree: dict | None = None) -> list[Path]:
    """export all available weeks to HTML with navigation links."""
    weeks = discover_all_weeks()
    if not weeks:
        print("no weekly notes found")
        return []

    print(f"found {len(weeks)} weekly notes")
    results = []

    for week_id in weeks:
        sidebar_nav = render_sidebar_html(nav_tree, f"{week_id}.html") if nav_tree else ""
        result = export_week(week_id, output_dir, all_weeks=weeks, force=force, sidebar_nav=sidebar_nav)
        if result:
            results.append(result)

    return results


def build_index(output_dir: Path, sidebar_nav: str = "") -> Path | None:
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
        sidebar_nav=sidebar_nav,
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


def export_page(source: Path, output_file: Path, title: str, sidebar_nav: str = "") -> Path | None:
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
        sidebar_nav=sidebar_nav,
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
    """parse title from notebook filename.

    filenames follow: {name}_{YYYYMMDD}.html where the last _YYYYMMDD is the export date.
    if the name part already starts with a YYYY-MM-DD date, use that as the date.
    otherwise format the export date suffix as the date.
    """
    stem = Path(filename).stem
    # extract trailing _YYYYMMDD export date
    date_match = re.search(r'_(\d{4})(\d{2})(\d{2})$', stem)
    export_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else ""
    stripped = re.sub(r'_\d{8}$', '', stem)

    # check if name starts with YYYY-MM-DD date
    leading_date = re.match(r'^(\d{4}-\d{2}-\d{2})[_-](.+)$', stripped)
    if leading_date:
        date_str = leading_date.group(1)
        name = leading_date.group(2).replace('-', ' ').replace('_', ' ').title()
    else:
        date_str = export_date
        name = stripped.replace('-', ' ').replace('_', ' ').title()

    if date_str:
        return f"{name} ({date_str})"
    return name


def parse_sop_title(filename: str) -> str:
    """parse title from SOP filename like sop_agarose_bead-prep.md"""
    stem = Path(filename).stem
    # remove sop_ prefix if present
    if stem.lower().startswith('sop_'):
        stem = stem[4:]
    return stem.replace('-', ' ').replace('_', ' ').title()


def export_directory_markdown(source_dir: Path, output_dir: Path, subdir: str, category: str, pattern: str = "*.md", title_parser=None, nav_tree: dict | None = None) -> list[dict]:
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

        page_path = f"compute/{subdir}/{md_file.stem}.html"
        sidebar_nav = render_sidebar_html(nav_tree, page_path) if nav_tree else ""
        result = export_page(md_file, output_file, title, sidebar_nav=sidebar_nav)
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

    # sort by date: leading YYYY-MM-DD or trailing _YYYYMMDD, newest first
    html_files = list(source_dir.glob(pattern))
    def _nb_date(f):
        stem = f.stem
        leading = re.match(r'^(\d{4}-\d{2}-\d{2})', stem)
        if leading:
            return leading.group(1)
        trailing = re.search(r'_(\d{8})$', stem)
        if trailing:
            d = trailing.group(1)
            return f"{d[:4]}-{d[4:6]}-{d[6:]}"
        return "0000-00-00"

    for html_file in sorted(html_files, key=_nb_date, reverse=True):
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


def copy_media_directory(source_dir: Path, output_dir: Path, subdir: str, category: str, pattern: str = "*.mp4", nav_tree: dict | None = None) -> list[dict]:
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
        page_path = f"compute/{subdir}/{media_file.stem}.html"
        sidebar_nav = render_sidebar_html(nav_tree, page_path) if nav_tree else ""
        viewer_html = HTML_TEMPLATE.format(
            title=title,
            sidebar_nav=sidebar_nav,
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


def export_additional_pages(output_dir: Path, nav_tree: dict | None = None) -> list[dict]:
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

        page_root_path = page["output"]
        if not page_root_path.startswith("compute/"):
            page_root_path = f"compute/{page_root_path}"
        sidebar_nav = render_sidebar_html(nav_tree, page_root_path) if nav_tree else ""
        result = export_page(source, output_file, title, sidebar_nav=sidebar_nav)
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
        exported.extend(export_directory_markdown(source_dir, output_dir, subdir, category, pattern, title_parser, nav_tree=nav_tree))

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
        exported.extend(copy_media_directory(source_dir, output_dir, subdir, category, pattern, nav_tree=nav_tree))

    return exported


def build_index_with_categories(output_dir: Path, additional_pages: list[dict] = None, sidebar_nav: str = "") -> Path | None:
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
        sidebar_nav=sidebar_nav,
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

    # build nav tree for sidebar
    weeks = discover_all_weeks()
    additional_meta = discover_additional_pages()
    nav_tree = build_nav_tree(weeks, additional_meta)

    # if any source week is missing from destination, force-rebuild all
    # so sidebars on existing files include the new week
    if not force:
        existing = {f.stem for f in weekly_dest.glob("*.html") if f.stem.startswith("20")}
        new_weeks = set(weeks) - existing
        if new_weeks:
            print(f"  detected {len(new_weeks)} new week(s) ({', '.join(sorted(new_weeks))}) — forcing rebuild to refresh sidebars")
            force = True

    print(f"syncing weekly to: {weekly_dest}")
    results = export_all_weeks(weekly_dest, force=force, nav_tree=nav_tree)

    # export additional pages to compute subfolder
    print(f"syncing compute to: {compute_dest}")
    additional = export_additional_pages(compute_dest, nav_tree=nav_tree)

    # build clean index with just weekly reports
    index_sidebar = render_sidebar_html(nav_tree, "index.html")
    build_index(weekly_dest, sidebar_nav=index_sidebar)

    # build compute index
    if additional:
        compute_sidebar = render_sidebar_html(nav_tree, "compute/index.html")
        build_compute_index(compute_dest, additional, sidebar_nav=compute_sidebar)

    return results


def build_compute_index(output_dir: Path, pages: list[dict], sidebar_nav: str = "") -> Path | None:
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
        sidebar_nav=sidebar_nav,
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


def normalize_item_text(text: str) -> str:
    """normalize item text for deduplication.

    strips leading parenthetical tags like (Example datasets), lowercases,
    collapses whitespace, removes trailing punctuation.
    """
    # strip leading parenthetical tags like (Critical), (Example datasets?), (~2h, 5%)
    text = re.sub(r'^\([^)]*\)\s*', '', text)
    # lowercase, collapse whitespace
    text = ' '.join(text.lower().split())
    # strip trailing punctuation
    text = text.rstrip('.,;:!?')
    return text


def parse_backlog() -> list[dict]:
    """parse backlog.md into a list of item dicts.

    returns list of {text, status, origin_week, normalized} dicts.
    items above ## Done are active, items below are done.
    """
    backlog_file = DOCS_ROOT / "backlog.md"
    if not backlog_file.exists():
        return []

    content = backlog_file.read_text(encoding='utf-8')
    items = []
    item_re = re.compile(r'^-\s*\[([xX~ ])\]\s*(.+?)(?:\s*\(W(\d+)\))?\s*$')

    for line in content.split('\n'):
        m = item_re.match(line.strip())
        if not m:
            continue
        marker = m.group(1)
        text = m.group(2).strip()
        origin = m.group(3) or ""

        if marker in ('x', 'X'):
            status = 'x'
        elif marker == '~':
            status = '~'
        else:
            status = ' '

        items.append({
            'text': text,
            'status': status,
            'origin_week': origin,
            'normalized': normalize_item_text(text),
        })

    return items


def _extract_weekly_todos(week_id: str) -> list[dict]:
    """extract all todo items from a week's previous and next TO-DO sections.

    returns list of {text, status, section, week_id, normalized} dicts.
    """
    weekly_file = find_weekly_note(week_id)
    if not weekly_file:
        return []

    content = weekly_file.read_text(encoding='utf-8')
    # match week number from id like 2026-W07 -> 07
    week_num = week_id.split('-W')[1] if '-W' in week_id else ''

    items = []

    # find TO-DO sections with their type (previous/next/unmarked)
    section_re = re.compile(
        r'##\s*(?:\((\w+)\)\s*)?TO-?DO.*?\n(.*?)(?=\n##|\Z)',
        re.IGNORECASE | re.DOTALL
    )

    for m in section_re.finditer(content):
        section_type = (m.group(1) or '').lower()  # 'previous', 'next', or ''
        section_body = m.group(2)

        for line in section_body.split('\n'):
            line = line.strip()
            # match checkbox items: - [x], - [~], - [ ]
            task_m = re.match(r'^-\s*\[([xX~ ])\]\s*(.+)$', line)
            if task_m:
                marker = task_m.group(1)
                text = task_m.group(2).strip()
                if marker in ('x', 'X'):
                    status = 'x'
                elif marker == '~':
                    status = '~'
                else:
                    status = ' '
            else:
                # match plain list items (no checkbox) like in W05
                plain_m = re.match(r'^-\s+(.+)$', line)
                if plain_m:
                    text = plain_m.group(1).strip()
                    # skip reference lines like *from [[...]]* and empty-ish items
                    if text.startswith('*') or len(text) < 3:
                        continue
                    status = ' '
                else:
                    continue

            items.append({
                'text': text,
                'status': status,
                'section': section_type,
                'week_id': week_id,
                'week_num': week_num,
                'normalized': normalize_item_text(text),
            })

    return items


def _status_rank(status: str) -> int:
    """status progression rank: ' ' < '~' < 'x'."""
    return {' ': 0, '~': 1, 'x': 2}.get(status, 0)


def _find_matching_key(normalized: str, key_set: dict) -> str | None:
    """find an existing key that fuzzy-matches.

    checks exact match, substring containment, and long prefix match.
    catches reworded duplicates and items with typos.
    """
    if normalized in key_set:
        return normalized
    for existing_key in key_set:
        # substring containment
        if normalized in existing_key or existing_key in normalized:
            return existing_key
        # prefix match: if both are long and share a 40-char prefix, treat as same
        if len(normalized) > 40 and len(existing_key) > 40:
            if normalized[:40] == existing_key[:40]:
                return existing_key
    return None


def sync_backlog() -> Path:
    """sync backlog.md with todo items from all weekly files.

    backlog.md is the single source of truth. this function:
    1. reads existing backlog.md
    2. scans all weekly files for todo items
    3. deduplicates and merges
    4. writes updated backlog.md
    """
    backlog_file = DOCS_ROOT / "backlog.md"

    # 1. read existing backlog
    existing = parse_backlog()
    existing_map = {}  # normalized -> item dict
    existing_order = []  # preserve user ordering
    for item in existing:
        key = item['normalized']
        if key not in existing_map:
            existing_order.append(key)
        existing_map[key] = item

    # 2. scan all weekly files
    all_weeks = discover_all_weeks()
    # collect best status per normalized item across all weeks
    weekly_items = {}  # normalized -> {text, status, origin_week}
    for wid in all_weeks:
        week_todos = _extract_weekly_todos(wid)
        for item in week_todos:
            key = item['normalized']
            # skip junk items
            if not key or len(key) < 5 or key.startswith('ignore previous'):
                continue
            # check for fuzzy match with existing weekly items
            match_key = _find_matching_key(key, weekly_items)
            if match_key:
                prev = weekly_items[match_key]
                # take higher status (one-way progression)
                if _status_rank(item['status']) > _status_rank(prev['status']):
                    weekly_items[match_key] = {
                        'text': item['text'],
                        'status': item['status'],
                        'origin_week': item['week_num'],
                        'normalized': match_key,
                    }
                # if same status, prefer later week's text (more recent wording)
                elif item['status'] == prev['status']:
                    weekly_items[match_key]['text'] = item['text']
                    weekly_items[match_key]['origin_week'] = item['week_num']
            else:
                weekly_items[key] = {
                    'text': item['text'],
                    'status': item['status'],
                    'origin_week': item['week_num'],
                    'normalized': key,
                }

    # 3. merge: update existing items, add new ones
    for key, weekly_item in weekly_items.items():
        match_key = _find_matching_key(key, existing_map)
        if match_key:
            # update status if weekly has higher progression
            if _status_rank(weekly_item['status']) > _status_rank(existing_map[match_key]['status']):
                existing_map[match_key]['status'] = weekly_item['status']
            # update origin week if not set
            if not existing_map[match_key]['origin_week'] and weekly_item['origin_week']:
                existing_map[match_key]['origin_week'] = weekly_item['origin_week']
        else:
            # new item, append at bottom
            existing_map[key] = weekly_item
            existing_order.append(key)

    # 4. write backlog.md
    active = []
    done = []
    for key in existing_order:
        item = existing_map[key]
        if item['status'] == 'x':
            done.append(item)
        else:
            active.append(item)

    write_backlog(active, done, backlog_file)
    return backlog_file


def write_backlog(active: list[dict], done: list[dict], path: Path) -> None:
    """write backlog.md with active items first, then done items."""
    lines = ['# Backlog', '']

    for item in active:
        marker = '~' if item['status'] == '~' else ' '
        week_tag = f" (W{item['origin_week']})" if item.get('origin_week') else ''
        lines.append(f'- [{marker}] {item["text"]}{week_tag}')

    if done:
        lines.append('')
        lines.append('## Done')
        lines.append('')
        for item in done:
            week_tag = f" (W{item['origin_week']})" if item.get('origin_week') else ''
            lines.append(f'- [x] {item["text"]}{week_tag}')

    lines.append('')  # trailing newline
    path.write_text('\n'.join(lines), encoding='utf-8')


def collect_backlog(current_week_id: str) -> list[dict]:
    """collect backlog items for display in weekly report.

    reads from backlog.md (single source of truth).
    returns in-progress items first, then open items, in priority order.
    excludes done items.
    """
    items = parse_backlog()
    # filter to open and in-progress only
    active = [i for i in items if i['status'] != 'x']
    if not active:
        return []

    # sort: in-progress first, then open, preserving order within each group
    in_progress = [i for i in active if i['status'] == '~']
    open_items = [i for i in active if i['status'] == ' ']

    return in_progress + open_items


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


SERVE_PORT = 8787


def _open_browser(url: str) -> None:
    """open url in default browser without spawning a visible python window."""
    if sys.platform == "win32":
        os.startfile(url)
    else:
        import webbrowser
        webbrowser.open(url)


def _is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return False
        except OSError:
            return True


def _start_server(serve_dir: Path) -> None:
    """spawn a detached HTTP server process."""
    cmd = [
        sys.executable, "-c",
        f"from http.server import HTTPServer, SimpleHTTPRequestHandler; "
        f"from functools import partial; "
        f"h = partial(SimpleHTTPRequestHandler, directory=r'{serve_dir}'); "
        f"s = HTTPServer(('127.0.0.1', {SERVE_PORT}), h); "
        f"s.serve_forever()"
    ]

    if sys.platform == "win32":
        subprocess.Popen(
            cmd,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )


def serve_and_open(serve_dir: Path) -> None:
    """start background HTTP server and open browser."""
    url = f"http://localhost:{SERVE_PORT}"

    if _is_port_in_use(SERVE_PORT):
        print(f"  server already running at {url}")
    else:
        _start_server(serve_dir)
        print(f"  serving at {url} (background process)")

    _open_browser(url)


def _collect_mtimes(dirs: list[Path], patterns: list[str] = None) -> dict[Path, float]:
    """snapshot mtime for all matching files in the given directories."""
    if patterns is None:
        patterns = ["*.md"]
    mtimes = {}
    for d in dirs:
        if d.exists():
            for pat in patterns:
                for f in d.glob(pat):
                    mtimes[f] = f.stat().st_mtime
    return mtimes


def watch_and_rebuild(output_dir: Path, poll_interval: float = 30.0) -> None:
    """poll source directories for changes and rebuild on change.

    runs the HTTP server in the background, then loops until ctrl+c.
    """
    import time

    url = f"http://localhost:{SERVE_PORT}"

    if not _is_port_in_use(SERVE_PORT):
        _start_server(output_dir)
    print(f"  serving at {url}")
    _open_browser(url)

    watch_dirs = [WEEKLY_DIR, DAILY_DIR, DOCS_ROOT / "notes" / "software", DOCS_ROOT / "notes" / "sop"]
    watch_patterns = ["*.md"]

    # also watch exports.toml
    config_file = EXPORTS_CONFIG
    config_mtime = config_file.stat().st_mtime if config_file.exists() else 0

    prev = _collect_mtimes(watch_dirs, watch_patterns)
    print(f"  watching {len(prev)} files for changes (ctrl+c to stop)")

    try:
        while True:
            time.sleep(poll_interval)
            curr = _collect_mtimes(watch_dirs, watch_patterns)
            curr_config = config_file.stat().st_mtime if config_file.exists() else 0

            changed = curr != prev or curr_config != config_mtime
            if not changed:
                continue

            # figure out what changed
            new_files = set(curr) - set(prev)
            removed = set(prev) - set(curr)
            modified = {f for f in set(curr) & set(prev) if curr[f] != prev[f]}

            for f in new_files:
                print(f"  + {f.name}")
            for f in modified:
                print(f"  ~ {f.name}")
            for f in removed:
                print(f"  - {f.name}")
            if curr_config != config_mtime:
                print(f"  ~ exports.toml")

            print("  rebuilding...")
            prev = curr
            config_mtime = curr_config

            try:
                sync_backlog()
                weeks = discover_all_weeks()
                additional_meta = discover_additional_pages()
                nav_tree = build_nav_tree(weeks, additional_meta)
                compute_dir = output_dir / "compute"

                export_all_weeks(output_dir, force=True, nav_tree=nav_tree)
                additional = export_additional_pages(compute_dir, nav_tree=nav_tree)
                index_sidebar = render_sidebar_html(nav_tree, "index.html")
                build_index(output_dir, sidebar_nav=index_sidebar)
                if additional:
                    compute_sidebar = render_sidebar_html(nav_tree, "compute/index.html")
                    build_compute_index(compute_dir, additional, sidebar_nav=compute_sidebar)
                print(f"  done — reload browser to see changes")
            except Exception as e:
                print(f"  rebuild error: {e}")

    except KeyboardInterrupt:
        print("\n  stopped watching")


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
        help="open in browser after export"
    )

    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help="serve and auto-rebuild on source file changes"
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

    # sync backlog before any export path
    sync_backlog()

    # handle --sync (export to OneDrive)
    # handle sync options
    if args.sync:
        sync_all(force=args.force)
        print(f"\nsynced to:")
        print(f"  Mirror:   {NETWORK_NOTEBOOK}")
        print(f"  OneDrive: {ONEDRIVE_WEEKLY}")
        print(f"  Network:  {NETWORK_WEEKLY}")
        if not args.watch:
            if args.open:
                serve_and_open(NETWORK_WEEKLY)
            return

    if args.onedrive:
        sync_to_onedrive(force=args.force)
        print(f"\nsynced to OneDrive: {ONEDRIVE_WEEKLY}")
        if args.open:
            serve_and_open(ONEDRIVE_WEEKLY)
        return

    if args.network:
        sync_to_network(force=args.force)
        print(f"\nsynced to network: {NETWORK_WEEKLY}")
        if args.open:
            serve_and_open(NETWORK_WEEKLY)
        return

    if args.mirror:
        mirror_repo_to_network()
        print(f"\nmirrored to: {NETWORK_NOTEBOOK}")
        return

    # determine output directory
    output_dir = args.output_dir or (LOCAL_EXPORT_DIR / "weekly")
    compute_dir = output_dir / "compute"

    # handle --watch: initial build then watch loop
    if args.watch:
        weeks = discover_all_weeks()
        additional_meta = discover_additional_pages()
        nav_tree = build_nav_tree(weeks, additional_meta)

        results = export_all_weeks(output_dir, force=True, nav_tree=nav_tree)
        additional = export_additional_pages(compute_dir, nav_tree=nav_tree)
        index_sidebar = render_sidebar_html(nav_tree, "index.html")
        build_index(output_dir, sidebar_nav=index_sidebar)
        if additional:
            compute_sidebar = render_sidebar_html(nav_tree, "compute/index.html")
            build_compute_index(compute_dir, additional, sidebar_nav=compute_sidebar)
        print(f"\nexported {len(results or [])} weeks to: {output_dir}")
        watch_and_rebuild(output_dir)
        return

    # phase 1: discover all content
    weeks = discover_all_weeks()
    additional_meta = discover_additional_pages()

    # phase 2: build nav tree and render sidebar
    nav_tree = build_nav_tree(weeks, additional_meta)

    if args.all:
        # phase 3: export all pages with sidebar
        results = export_all_weeks(output_dir, force=args.force, nav_tree=nav_tree)
        if results:
            additional = export_additional_pages(compute_dir, nav_tree=nav_tree)
            index_sidebar = render_sidebar_html(nav_tree, "index.html")
            build_index(output_dir, sidebar_nav=index_sidebar)
            if additional:
                compute_sidebar = render_sidebar_html(nav_tree, "compute/index.html")
                build_compute_index(compute_dir, additional, sidebar_nav=compute_sidebar)
            print(f"\nexported {len(results)} weeks to: {output_dir}")
            if args.open:
                serve_and_open(output_dir)
    else:
        week_id = args.week or get_current_week_id()
        try:
            parse_week_id(week_id)
        except ValueError as e:
            print(f"ERROR: {e}")
            sys.exit(1)

        # phase 3: export single week with sidebar
        week_sidebar = render_sidebar_html(nav_tree, f"{week_id}.html")
        result = export_week(week_id, output_dir, all_weeks=weeks, force=args.force, sidebar_nav=week_sidebar)
        if result:
            additional = export_additional_pages(compute_dir, nav_tree=nav_tree)
            index_sidebar = render_sidebar_html(nav_tree, "index.html")
            build_index(output_dir, sidebar_nav=index_sidebar)
            if additional:
                compute_sidebar = render_sidebar_html(nav_tree, "compute/index.html")
                build_compute_index(compute_dir, additional, sidebar_nav=compute_sidebar)
            print(f"\nexported to: {result}")
            if args.open:
                serve_and_open(output_dir)
        else:
            print(f"no content found for {week_id}")
            sys.exit(1)


if __name__ == "__main__":
    main()
