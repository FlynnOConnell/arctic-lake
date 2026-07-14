#!/usr/bin/env python3
"""
build sphinx docs from notes.

stages content from various folders into sphinx docs structure,
then builds the site.

usage:
    uv run build-docs          # build site
    uv run build-docs --serve  # live preview server
    uv run build-docs --open   # build and open in browser
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"
BUILD_DIR = DOCS_DIR / "_build" / "html"

# source directories
SOURCES = {
    "software": REPO_ROOT / "notes" / "software",
    "sop": REPO_ROOT / "notes" / "sop",
}

# image sources
IMAGE_SOURCES = [
    REPO_ROOT / "notes" / "images",
    REPO_ROOT / "static" / "images",
]

# external sources
EXTERNAL_SOURCES = {
    "sop_external": Path("Y:/foconnell/notebook/notes/sop"),
}


def fix_frontmatter(content: str) -> str:
    """remove template: field from frontmatter."""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return content
    frontmatter = match.group(1)
    frontmatter = re.sub(r'^template:.*$\n?', '', frontmatter, flags=re.MULTILINE)
    return f"---\n{frontmatter}---\n" + content[match.end():]


def fix_image_paths(content: str, dest_subdir: str) -> str:
    """fix image paths for sphinx."""
    # calculate relative path to _static/images based on depth
    depth = len(Path(dest_subdir).parts)
    prefix = "../" * depth + "_static/images/"

    # various source patterns -> _static/images/
    content = re.sub(r'\.\./static/images/', prefix, content)
    content = re.sub(r'\.\./notes/images/', prefix, content)
    content = re.sub(r'\.\./\.\./images/', prefix, content)
    content = re.sub(r'notes/images/', prefix, content)

    # obsidian ![[image.png]] -> markdown ![](image.png)
    def fix_obsidian_img(m):
        img = m.group(1)
        return f"![]({prefix}{img})"
    content = re.sub(r'!\[\[([^\]]+\.(png|jpg|jpeg|gif|svg))\]\]', fix_obsidian_img, content, flags=re.IGNORECASE)

    return content


def fix_wikilinks(content: str) -> str:
    """convert wikilinks to plain text."""
    def replace_wikilink(match):
        full = match.group(1)
        if '|' in full:
            _, display = full.split('|', 1)
        else:
            display = full
        return display.strip()
    content = re.sub(r'\[\[([^\]]+)\]\]', replace_wikilink, content)
    return content


def fix_title(content: str, filename: str) -> str:
    """replace first H1 with filename-based title."""
    # use filename as title (without extension)
    title = filename.replace("-", " ").replace("_", " ")
    # replace first # heading with filename title
    content = re.sub(r'^#\s+.+$', f'# {title}', content, count=1, flags=re.MULTILINE)
    return content


def process_markdown(src: Path, dest: Path, dest_subdir: str = ""):
    """copy markdown file with fixes applied."""
    content = src.read_text(encoding='utf-8')
    content = fix_frontmatter(content)
    content = fix_image_paths(content, dest_subdir)
    content = fix_wikilinks(content)
    # use filename as document title
    if src.name != "index.md":
        content = fix_title(content, src.stem)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding='utf-8')


def generate_toctree(section_dir: Path) -> str:
    """generate toctree directive for all md files in a section."""
    files = sorted(section_dir.glob("*.md"), key=lambda f: f.stem.lower())
    files = [f for f in files if f.name != "index.md"]

    if not files:
        return ""

    lines = ["", "```{toctree}", ":maxdepth: 1", ":titlesonly:", ""]
    for f in files:
        display_name = f.stem.replace("-", " ").replace("_", " ")
        lines.append(f"{display_name} <{f.stem}>")
    lines.append("```")
    return "\n".join(lines)


def generate_section_index(section_dir: Path, title: str, description: str = "") -> None:
    """ensure section has an index.md with toctree."""
    if not section_dir.exists():
        return

    index_path = section_dir / "index.md"
    toctree = generate_toctree(section_dir)

    if index_path.exists():
        # check if existing index already has a toctree
        content = index_path.read_text(encoding="utf-8")
        if "```{toctree}" not in content and toctree:
            # append toctree to existing content
            content = content.rstrip() + "\n\n## Pages\n" + toctree
            index_path.write_text(content, encoding="utf-8")
        return

    # no index exists, generate one
    if not toctree:
        return

    lines = [f"# {title}", ""]
    if description:
        lines.extend([description, ""])

    content = "\n".join(lines) + toctree
    index_path.write_text(content, encoding="utf-8")


def stage_content():
    """copy content to docs directory."""
    print("staging content...")

    # copy local sources
    for name, src in SOURCES.items():
        if not src.exists():
            print(f"  skipping {name} (not found)")
            continue

        dest = DOCS_DIR / name
        dest.mkdir(parents=True, exist_ok=True)
        count = 0
        for f in src.glob("*.md"):
            process_markdown(f, dest / f.name, name)
            count += 1
        print(f"  staged: {name} ({count} files)")

    # copy external sources
    for name, src in EXTERNAL_SOURCES.items():
        if not src.exists():
            print(f"  skipping {name} (not found)")
            continue

        dest_name = name.replace("_external", "")
        dest = DOCS_DIR / dest_name
        dest.mkdir(parents=True, exist_ok=True)

        for f in src.glob("*.md"):
            process_markdown(f, dest / f.name, dest_name)
        print(f"  staged external: {name} -> {dest_name}")

    # copy images to _static/images
    images_dest = DOCS_DIR / "_static" / "images"
    images_dest.mkdir(parents=True, exist_ok=True)
    total = 0
    for img_src in IMAGE_SOURCES:
        if not img_src.exists():
            continue
        for img in img_src.glob("*"):
            if img.is_file():
                shutil.copy2(img, images_dest / img.name)
                total += 1
    print(f"  staged: images ({total} files)")

    # generate section indexes
    print("generating indexes...")
    generate_section_index(DOCS_DIR / "software", "Software", "calcium imaging tools, pipelines, and references.")
    generate_section_index(DOCS_DIR / "sop", "SOPs", "standard operating procedures.")


def clean_staged():
    """remove staged content (but keep _static/custom.css and conf.py)."""
    for name in ["software", "sop"]:
        path = DOCS_DIR / name
        if path.exists():
            shutil.rmtree(path)

    # clean images but keep custom.css
    images_dir = DOCS_DIR / "_static" / "images"
    if images_dir.exists():
        shutil.rmtree(images_dir)


def build_site():
    """run sphinx-build."""
    result = subprocess.run(
        ["uv", "run", "sphinx-build", "-b", "html", str(DOCS_DIR), str(BUILD_DIR)],
        cwd=REPO_ROOT,
    )
    return result.returncode == 0


def serve_site():
    """run sphinx autobuild for live preview."""
    try:
        subprocess.run(
            ["uv", "run", "sphinx-autobuild", str(DOCS_DIR), str(BUILD_DIR), "--open-browser"],
            cwd=REPO_ROOT,
        )
    except FileNotFoundError:
        print("sphinx-autobuild not installed, using python http server...")
        import http.server
        import socketserver
        os.chdir(BUILD_DIR)
        with socketserver.TCPServer(("", 8000), http.server.SimpleHTTPRequestHandler) as httpd:
            print(f"serving at http://localhost:8000/")
            httpd.serve_forever()


def open_site():
    """open built site in browser."""
    index = BUILD_DIR / "index.html"
    if not index.exists():
        print(f"site not found: {index}")
        return

    if sys.platform == "win32":
        os.startfile(index)
    elif sys.platform == "darwin":
        subprocess.run(["open", str(index)])
    else:
        subprocess.run(["xdg-open", str(index)])
    print(f"  opened: {index}")


def main():
    parser = argparse.ArgumentParser(description="build sphinx docs from notes")
    parser.add_argument("--serve", "-s", action="store_true", help="start live preview server")
    parser.add_argument("--open", "-o", action="store_true", help="open site in browser after build")
    parser.add_argument("--clean", "-c", action="store_true", help="clean build directories")
    args = parser.parse_args()

    if args.clean:
        print("cleaning...")
        clean_staged()
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
        print("done")
        return

    clean_staged()
    stage_content()

    if args.serve:
        print("building and serving...")
        if build_site():
            serve_site()
    else:
        print("building site...")
        if build_site():
            print(f"\nsite built: {BUILD_DIR}")
            if args.open:
                open_site()
        else:
            print("build failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
