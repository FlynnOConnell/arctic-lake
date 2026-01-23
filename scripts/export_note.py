#!/usr/bin/env python3
"""
Export Obsidian/Markdown notes and Jupyter notebooks to self-contained HTML and PDF.

All images are embedded as base64 data URIs, making the output
completely portable with no external dependencies.

Usage:
    # Export markdown to project folder (reads 'project' from frontmatter)
    uv run export-note "notes/software/Calcium Imaging Pipelines.md"

    # Export Jupyter notebook
    uv run export-note "2025-12-18_metadata-test.ipynb"

    # Override project destination
    uv run export-note notes/suite3d.md --project lbm

    # Export to specific directory
    uv run export-note notes/weekly.md -o ./exports

    # List available projects
    uv run export-note --list-projects

Frontmatter:
    Add 'project: lbm' (or isoview, explore) to route exports to Y:/projects/{project}/
    For notebooks, frontmatter in the first markdown cell is detected.
"""

import argparse
import base64
import mimetypes
import re
import sys
import yaml
from datetime import datetime
from pathlib import Path

from scripts.config import (
    get_project_path,
    list_available_projects,
    discover_server_projects,
    WEEKLY_MEETING_DIR,
    LOCAL_EXPORT_DIR,
)

try:
    import markdown
    from markdown.extensions import fenced_code, tables, toc
except ImportError:
    print("ERROR: 'markdown' package not found. Install with: pip install markdown")
    sys.exit(1)

try:
    import warnings
    warnings.filterwarnings("ignore", message="IPython3 lexer unavailable")
    from nbconvert import HTMLExporter
    from nbconvert.preprocessors import ExecutePreprocessor
    import nbformat
    NBCONVERT_AVAILABLE = True
except ImportError:
    NBCONVERT_AVAILABLE = False

# Weasyprint is optional - requires GTK on Windows which is complex to set up
WEASYPRINT_AVAILABLE = False
HTML_CLASS = None

def _try_import_weasyprint():
    """Try to import weasyprint, suppressing its verbose error messages."""
    global WEASYPRINT_AVAILABLE, HTML_CLASS
    import os
    import io
    import contextlib

    # Suppress both stdout and stderr during import
    # weasyprint prints verbose GTK errors on Windows
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        from weasyprint import HTML as WeasyHTML
        WEASYPRINT_AVAILABLE = True
        HTML_CLASS = WeasyHTML
    except (ImportError, OSError):
        pass
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

_try_import_weasyprint()


# Image extensions to handle
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'}

# Video extensions to handle
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.avi'}


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from markdown content.

    Returns (frontmatter_dict, content_without_frontmatter)
    """
    if not content.startswith('---'):
        return {}, content

    end = content.find('---', 3)
    if end == -1:
        return {}, content

    frontmatter_text = content[3:end].strip()
    body = content[end + 3:].lstrip()

    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, body


def resolve_output_dir(
    frontmatter: dict,
    cli_project: str | None,
    cli_output_dir: Path | None,
) -> Path:
    """
    Determine output directory from CLI args or frontmatter.

    Priority:
    1. --output-dir (explicit path)
    2. --project (CLI override)
    3. frontmatter 'project' field
    4. Default to local exports
    """
    # Explicit output dir takes precedence
    if cli_output_dir:
        return cli_output_dir

    # CLI project override
    project = cli_project or frontmatter.get('project')

    if project:
        project_path = get_project_path(project)
        if project_path:
            return project_path
        else:
            print(f"WARNING: Unknown project '{project}', using local exports")
            print(f"  Available: {', '.join(list_available_projects())}")

    return LOCAL_EXPORT_DIR

# HTML template with embedded CSS for nice rendering
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
        }}

        * {{
            box-sizing: border-box;
        }}

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

        a {{
            color: var(--link-color);
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        video {{
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

        pre code {{
            background: none;
            padding: 0;
        }}

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

        th {{
            background-color: var(--code-bg);
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background-color: #fafafa;
        }}

        ul, ol {{
            padding-left: 1.5em;
        }}

        li {{
            margin: 0.25em 0;
        }}

        hr {{
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 2em 0;
        }}

        .metadata {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 2em;
            padding-bottom: 1em;
            border-bottom: 1px solid var(--border-color);
        }}

        .missing-image {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 1em;
            border-radius: 4px;
            color: #856404;
            text-align: center;
        }}

        /* Task list styling */
        .task-list-item {{
            list-style-type: none;
            margin-left: -1.5em;
        }}

        .task-list-item input {{
            margin-right: 0.5em;
        }}

        @media print {{
            body {{
                max-width: none;
                padding: 1cm;
            }}

            img {{
                max-height: 400px;
                page-break-inside: avoid;
            }}

            h1, h2, h3 {{
                page-break-after: avoid;
            }}

            pre, blockquote {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="metadata">
        <strong>Source:</strong> {source_file}<br>
        <strong>Exported:</strong> {export_date}
    </div>
    {content}
</body>
</html>
"""


def get_mime_type(path: Path) -> str:
    """Get MIME type for an image file."""
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type:
        return mime_type
    # Fallback based on extension
    ext = path.suffix.lower()
    mime_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
    }
    return mime_map.get(ext, 'application/octet-stream')


def image_to_base64(image_path: Path) -> str | None:
    """Convert an image file to a base64 data URI."""
    if not image_path.exists():
        return None

    try:
        with open(image_path, 'rb') as f:
            data = f.read()

        mime_type = get_mime_type(image_path)
        b64_data = base64.b64encode(data).decode('utf-8')
        return f"data:{mime_type};base64,{b64_data}"
    except Exception as e:
        print(f"  WARNING: Could not read image {image_path}: {e}")
        return None


def find_image(image_name: str, md_file: Path, images_dir: Path) -> Path | None:
    """
    Find an image file given its name or relative path.

    Search order:
    1. Relative path from markdown file's parent directory
    2. Relative path from parent's parent (for notes/sop -> notes/literature)
    3. Just filename in same directory as markdown file
    4. In local images/ subfolder
    5. In global images directory
    6. Recursively in images directory
    """
    image_path = Path(image_name)
    just_name = image_path.name

    # Search locations
    search_paths = [
        md_file.parent / image_name,                    # Relative path from .md dir
        md_file.parent.parent / image_name,             # Relative from parent's parent
        md_file.parent / just_name,                     # Same directory as .md
        md_file.parent / "images" / just_name,          # Local images/ subfolder
        images_dir / just_name,                         # Global images directory
    ]

    for path in search_paths:
        if path.exists():
            return path

    # Search recursively in images directory
    if images_dir.exists():
        for found in images_dir.rglob(just_name):
            return found

    return None


def convert_obsidian_images(content: str, md_file: Path, images_dir: Path) -> str:
    """
    Convert Obsidian-style image embeds to standard markdown with base64 data URIs.

    Handles:
    - ![[image.png]]
    - ![[image.png|alt text]]
    - ![[image.png|width]]
    """
    # Pattern for Obsidian image embeds: ![[filename]] or ![[filename|alt/size]]
    obsidian_pattern = r'!\[\[([^\]|]+)(?:\|([^\]]*))?\]\]'

    def replace_obsidian_image(match):
        image_name = match.group(1).strip()
        alt_or_size = match.group(2) or ""

        # Skip non-image embeds (like note links)
        if not any(image_name.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
            return match.group(0)  # Return unchanged

        image_path = find_image(image_name, md_file, images_dir)

        if image_path:
            data_uri = image_to_base64(image_path)
            if data_uri:
                alt_text = alt_or_size if alt_or_size and not alt_or_size.isdigit() else image_name
                print(f"  Embedded: {image_name}")
                return f'![{alt_text}]({data_uri})'

        print(f"  WARNING: Image not found: {image_name}")
        return f'<div class="missing-image">Missing image: {image_name}</div>'

    return re.sub(obsidian_pattern, replace_obsidian_image, content)


def convert_standard_images(content: str, md_file: Path, images_dir: Path) -> str:
    """
    Convert standard markdown images to base64 data URIs.

    Handles: ![alt](path/to/image.png)
    """
    # Pattern for standard markdown images (skip already-converted data URIs)
    std_pattern = r'!\[([^\]]*)\]\((?!data:)([^)]+)\)'

    def replace_std_image(match):
        alt_text = match.group(1)
        image_ref = match.group(2).strip()

        # Skip URLs
        if image_ref.startswith(('http://', 'https://', '//')):
            return match.group(0)

        # Try to find the image
        image_path = find_image(image_ref, md_file, images_dir)

        if image_path:
            data_uri = image_to_base64(image_path)
            if data_uri:
                print(f"  Embedded: {image_ref}")
                return f'![{alt_text}]({data_uri})'

        print(f"  WARNING: Image not found: {image_ref}")
        return f'<div class="missing-image">Missing image: {image_ref}</div>'

    return re.sub(std_pattern, replace_std_image, content)


def find_video(video_name: str, md_file: Path, media_dirs: list[Path] | None = None) -> Path | None:
    """Find a video file given its name or path."""
    video_path = Path(video_name)
    just_name = video_path.name

    search_paths = [
        md_file.parent / video_name,
        md_file.parent / just_name,
        md_file.parent / "media" / just_name,
        Path("Y:/foconnell/media") / just_name,
        Path("Y:/foconnell/media/development") / just_name,
    ]

    if media_dirs:
        for d in media_dirs:
            search_paths.append(d / just_name)

    for path in search_paths:
        if path.exists():
            return path

    return None


def convert_obsidian_videos(content: str, md_file: Path, output_dir: Path) -> str:
    """Convert Obsidian-style video embeds to HTML video tags."""
    import shutil
    obsidian_pattern = r'!\[\[([^\]|]+)(?:\|([^\]]*))?\]\]'

    def replace_video(match):
        video_name = match.group(1).strip()

        if not any(video_name.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            return match.group(0)

        video_path = find_video(video_name, md_file)

        if video_path and video_path.exists():
            # copy video to output directory
            media_dir = output_dir / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            dest = media_dir / video_path.name
            if not dest.exists():
                shutil.copy2(video_path, dest)
            print(f"  Copied video: {video_path.name}")
            return f'<video src="media/{video_path.name}" controls></video>'

        print(f"  WARNING: Video not found: {video_name}")
        return f'<div class="missing-image">Missing video: {video_name}</div>'

    return re.sub(obsidian_pattern, replace_video, content)


def convert_standard_videos(content: str, md_file: Path, output_dir: Path) -> str:
    """Convert standard markdown video links to HTML video tags."""
    import shutil
    std_pattern = r'!\[([^\]]*)\]\((?!data:)([^)]+)\)'

    def replace_video(match):
        alt_text = match.group(1)
        video_ref = match.group(2).strip()

        if not any(video_ref.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            return match.group(0)

        if video_ref.startswith(('http://', 'https://', '//')):
            return f'<video src="{video_ref}" controls></video>'

        video_path = find_video(video_ref, md_file)

        if video_path and video_path.exists():
            media_dir = output_dir / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            dest = media_dir / video_path.name
            if not dest.exists():
                shutil.copy2(video_path, dest)
            print(f"  Copied video: {video_path.name}")
            return f'<video src="media/{video_path.name}" controls></video>'

        print(f"  WARNING: Video not found: {video_ref}")
        return f'<div class="missing-image">Missing video: {video_ref}</div>'

    return re.sub(std_pattern, replace_video, content)


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    _, body = parse_frontmatter(content)
    return body


def convert_wikilinks(content: str) -> str:
    """Convert Obsidian wikilinks to plain text (since they won't work in static export)."""
    # [[Link|Display]] -> Display
    content = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', content)
    # [[Link]] -> Link
    content = re.sub(r'\[\[([^\]]+)\]\]', r'\1', content)
    return content


def convert_task_lists(content: str) -> str:
    """Convert Obsidian/GFM task lists to HTML checkboxes."""
    # - [ ] unchecked
    content = re.sub(
        r'^(\s*)- \[ \] (.+)$',
        r'\1<li class="task-list-item"><input type="checkbox" disabled> \2</li>',
        content,
        flags=re.MULTILINE
    )
    # - [x] checked
    content = re.sub(
        r'^(\s*)- \[x\] (.+)$',
        r'\1<li class="task-list-item"><input type="checkbox" checked disabled> \2</li>',
        content,
        flags=re.MULTILINE
    )
    return content


def markdown_to_html(md_content: str, title: str, source_file: str) -> str:
    """Convert markdown content to a complete HTML document."""
    # Configure markdown extensions
    md = markdown.Markdown(
        extensions=[
            'fenced_code',
            'tables',
            'toc',
            'nl2br',
            'sane_lists',
        ]
    )

    html_content = md.convert(md_content)

    # Build final HTML
    return HTML_TEMPLATE.format(
        title=title,
        source_file=source_file,
        export_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        content=html_content
    )


def export_note(
    md_file: Path,
    output_dir: Path,
    generate_html: bool = True,
    generate_pdf: bool = True
) -> dict:
    """
    Export a markdown note to HTML and/or PDF with embedded images.

    Returns dict with paths to generated files.
    """
    if not md_file.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_file}")

    # Determine the images directory (assumes notes/images/ structure)
    # Walk up to find the 'notes' directory
    images_dir = md_file.parent / "images"
    current = md_file.parent
    while current.parent != current:
        candidate = current / "images"
        if candidate.exists():
            images_dir = candidate
            break
        candidate = current / "notes" / "images"
        if candidate.exists():
            images_dir = candidate
            break
        current = current.parent

    print(f"Processing: {md_file}")
    print(f"Images directory: {images_dir}")

    # Read and process markdown
    content = md_file.read_text(encoding='utf-8')

    # Strip frontmatter
    content = strip_frontmatter(content)

    # Convert Obsidian-style images to base64
    content = convert_obsidian_images(content, md_file, images_dir)

    # Convert any remaining standard markdown images
    content = convert_standard_images(content, md_file, images_dir)

    # Convert wikilinks to plain text
    content = convert_wikilinks(content)

    # Convert task lists
    content = convert_task_lists(content)

    # Generate title from filename
    title = md_file.stem.replace('-', ' ').replace('_', ' ')

    # Convert to HTML
    html_content = markdown_to_html(content, title, md_file.name)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    base_name = f"{md_file.stem}_{timestamp}"

    results = {}

    # Write HTML
    if generate_html:
        html_path = output_dir / f"{base_name}.html"
        html_path.write_text(html_content, encoding='utf-8')
        results['html'] = html_path
        print(f"Created HTML: {html_path}")

    # Write PDF
    if generate_pdf:
        if WEASYPRINT_AVAILABLE and HTML_CLASS:
            pdf_path = output_dir / f"{base_name}.pdf"
            try:
                HTML_CLASS(string=html_content).write_pdf(pdf_path)
                results['pdf'] = pdf_path
                print(f"Created PDF: {pdf_path}")
            except Exception as e:
                print(f"ERROR creating PDF: {e}")
        else:
            print("Skipping PDF (weasyprint not available - requires GTK on Windows)")
            print("  HTML file can be printed to PDF from any browser")

    return results


def embed_notebook_images(nb_file: Path, notebook) -> None:
    """
    Pre-process notebook markdown cells to embed images as base64.

    Handles:
    - ![alt](path/to/image.png) - standard markdown
    - ![alt](../relative/path.png) - relative paths
    - Resolves paths relative to notebook location
    """
    images_dir = nb_file.parent / "images"

    # find images dir by walking up
    current = nb_file.parent
    while current.parent != current:
        candidate = current / "images"
        if candidate.exists():
            images_dir = candidate
            break
        current = current.parent

    for cell in notebook.cells:
        if cell.cell_type != 'markdown':
            continue

        content = cell.source

        # pattern for markdown images (skip data URIs and URLs)
        pattern = r'!\[([^\]]*)\]\((?!data:)(?!http)([^)]+)\)'

        def replace_image(match):
            alt_text = match.group(1)
            image_ref = match.group(2).strip()

            # try to find the image
            image_path = find_image(image_ref, nb_file, images_dir)

            if image_path:
                data_uri = image_to_base64(image_path)
                if data_uri:
                    print(f"  Embedded: {image_ref}")
                    return f'![{alt_text}]({data_uri})'

            print(f"  WARNING: Image not found: {image_ref}")
            return match.group(0)

        cell.source = re.sub(pattern, replace_image, content)


def export_notebook(
    nb_file: Path,
    output_dir: Path,
    generate_html: bool = True,
    generate_pdf: bool = True
) -> dict:
    """
    Export a Jupyter notebook to HTML and/or PDF.

    Returns dict with paths to generated files.
    """
    if not NBCONVERT_AVAILABLE:
        print("ERROR: nbconvert not available. Install with: pip install nbconvert")
        return {}

    if not nb_file.exists():
        raise FileNotFoundError(f"Notebook file not found: {nb_file}")

    print(f"Processing notebook: {nb_file}")

    # read notebook
    with open(nb_file, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    # embed images from markdown cells
    embed_notebook_images(nb_file, notebook)

    # configure HTML exporter
    html_exporter = HTMLExporter()
    html_exporter.embed_images = True

    # convert to HTML
    html_content, resources = html_exporter.from_notebook_node(notebook)

    # ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    base_name = f"{nb_file.stem}_{timestamp}"

    results = {}

    # write HTML
    if generate_html:
        html_path = output_dir / f"{base_name}.html"
        html_path.write_text(html_content, encoding='utf-8')
        results['html'] = html_path
        print(f"Created HTML: {html_path}")

    # write PDF
    if generate_pdf:
        if WEASYPRINT_AVAILABLE and HTML_CLASS:
            pdf_path = output_dir / f"{base_name}.pdf"
            try:
                HTML_CLASS(string=html_content).write_pdf(pdf_path)
                results['pdf'] = pdf_path
                print(f"Created PDF: {pdf_path}")
            except Exception as e:
                print(f"ERROR creating PDF: {e}")
        else:
            print("Skipping PDF (weasyprint not available - requires GTK on Windows)")
            print("  HTML file can be printed to PDF from any browser")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Export Obsidian/Markdown notes and Jupyter notebooks to self-contained HTML and PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Export markdown using frontmatter 'project' field
    uv run export-note notes/software/Calcium\\ Imaging\\ Pipelines.md

    # Export Jupyter notebook
    uv run export-note 2025-12-18_metadata-test.ipynb

    # Override project destination
    uv run export-note notes/suite3d.md --project lbm

    # Export to specific directory
    uv run export-note notes/weekly.md -o ./exports

    # List configured projects
    uv run export-note --list-projects

Frontmatter example (markdown or first notebook cell):
    ---
    project: lbm
    title: My Analysis Notes
    ---

The script will:
- Read 'project' from frontmatter to route to Y:/projects/{project}/
- Embed all images as base64 (fully portable, no broken links)
- Convert Obsidian syntax to standard HTML (markdown files)
- Convert Jupyter notebooks with embedded outputs
        """
    )

    parser.add_argument(
        'markdown_file',
        type=Path,
        nargs='?',
        metavar='FILE',
        help="Path to the markdown (.md) or notebook (.ipynb) file to export"
    )

    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=None,
        help="Output directory (overrides project routing)"
    )

    parser.add_argument(
        '--project', '-p',
        type=str,
        default=None,
        help="Project name (overrides frontmatter). Routes to Y:/projects/{project}/"
    )

    parser.add_argument(
        '--list-projects',
        action='store_true',
        help="List available projects and exit"
    )

    parser.add_argument(
        '--html-only',
        action='store_true',
        help="Generate only HTML output"
    )

    parser.add_argument(
        '--pdf-only',
        action='store_true',
        help="Generate only PDF output"
    )

    parser.add_argument(
        '--weekly', '-w',
        action='store_true',
        help="Export to processing folder for weekly report (shortcut for --project processing)"
    )

    args = parser.parse_args()

    # --weekly is shortcut for --project processing
    if args.weekly:
        args.project = "processing"

    # Handle --list-projects
    if args.list_projects:
        print("Configured projects:")
        for proj in list_available_projects():
            path = get_project_path(proj)
            status = "OK" if path and path.exists() else "not mounted"
            print(f"  {proj}: {path} ({status})")

        print("\nServer projects (Y:/projects/):")
        server_projects = discover_server_projects()
        if server_projects:
            for proj in server_projects:
                print(f"  {proj}")
        else:
            print("  (Y: drive not mounted)")
        return

    # Require input file if not listing projects
    if not args.markdown_file:
        parser.error("input file is required")

    # Resolve input path
    input_file = args.markdown_file.resolve()

    if not input_file.exists():
        print(f"ERROR: File not found: {input_file}")
        sys.exit(1)

    # Detect file type
    is_notebook = input_file.suffix.lower() == '.ipynb'

    # Read frontmatter to determine project
    frontmatter = {}
    if is_notebook:
        # try to extract project from first markdown cell
        if NBCONVERT_AVAILABLE:
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    nb = nbformat.read(f, as_version=4)
                for cell in nb.cells:
                    if cell.cell_type == 'markdown':
                        frontmatter, _ = parse_frontmatter(cell.source)
                        break
            except Exception:
                pass
    else:
        content = input_file.read_text(encoding='utf-8')
        frontmatter, _ = parse_frontmatter(content)

    # Resolve output directory
    output_dir = resolve_output_dir(
        frontmatter,
        cli_project=args.project,
        cli_output_dir=args.output_dir,
    )

    # Determine what to generate
    generate_html = not args.pdf_only
    generate_pdf = not args.html_only

    try:
        if is_notebook:
            results = export_notebook(
                input_file,
                output_dir,
                generate_html=generate_html,
                generate_pdf=generate_pdf
            )
        else:
            results = export_note(
                input_file,
                output_dir,
                generate_html=generate_html,
                generate_pdf=generate_pdf
            )

        print(f"\nExported to: {output_dir}")
        for fmt, path in results.items():
            print(f"  {fmt.upper()}: {path.name}")

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
