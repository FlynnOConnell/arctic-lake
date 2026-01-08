#!/usr/bin/env python3
"""
Export Obsidian/Markdown notes to self-contained HTML and PDF.

All images are embedded as base64 data URIs, making the output
completely portable with no external dependencies.

Usage:
    python export_note.py <markdown_file> [--output-dir <dir>]
    python export_note.py notes/software/IsoView.md
    python export_note.py notes/weekly.md --output-dir "C:/Users/flynn/OneDrive/MBO_DATA/weekly_meeting"

Requirements:
    pip install markdown weasyprint pygments
"""

import argparse
import base64
import mimetypes
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import markdown
    from markdown.extensions import fenced_code, tables, toc
except ImportError:
    print("ERROR: 'markdown' package not found. Install with: pip install markdown")
    sys.exit(1)

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


# Default output directory (OneDrive weekly meeting folder)
DEFAULT_OUTPUT_DIR = Path.home() / "OneDrive" / "MBO_DATA" / "weekly_meeting"

# Image extensions to handle
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'}

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
    Find an image file given its name.

    Search order:
    1. Relative to the markdown file
    2. In the images directory (notes/images/)
    3. In subdirectories of images/
    """
    # Clean up the image name (remove any path components for Obsidian-style links)
    image_name = Path(image_name).name

    # Search locations
    search_paths = [
        md_file.parent / image_name,                    # Same directory as .md
        md_file.parent / "images" / image_name,         # Local images/ subfolder
        images_dir / image_name,                        # Global images directory
    ]

    for path in search_paths:
        if path.exists():
            return path

    # Search recursively in images directory
    if images_dir.exists():
        for found in images_dir.rglob(image_name):
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


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            return content[end + 3:].lstrip()
    return content


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


def main():
    parser = argparse.ArgumentParser(
        description="Export Obsidian/Markdown notes to self-contained HTML and PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python export_note.py notes/weekly.md
    python export_note.py notes/software/IsoView.md --output-dir ./exports
    python export_note.py notes/meeting.md --html-only
    python export_note.py notes/report.md --pdf-only

The script will:
1. Find and embed all images as base64 data URIs
2. Convert Obsidian syntax (![[image.png]]) to standard HTML
3. Generate self-contained HTML and/or PDF files
4. Output to OneDrive/MBO_DATA/weekly_meeting by default
        """
    )

    parser.add_argument(
        'markdown_file',
        type=Path,
        help="Path to the markdown file to export"
    )

    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
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

    args = parser.parse_args()

    # Resolve paths
    md_file = args.markdown_file.resolve()
    output_dir = args.output_dir.resolve()

    # Determine what to generate
    generate_html = not args.pdf_only
    generate_pdf = not args.html_only

    try:
        results = export_note(
            md_file,
            output_dir,
            generate_html=generate_html,
            generate_pdf=generate_pdf
        )

        print("\nExport complete!")
        for fmt, path in results.items():
            print(f"  {fmt.upper()}: {path}")

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
