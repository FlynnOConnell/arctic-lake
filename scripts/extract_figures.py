#!/usr/bin/env python3
"""
extract raster figures from a paper PDF into a sibling ``figures/`` folder.

replaces the manual screenshot / CDN-hotlink workflow for literature notes.
given a paper folder (or a pdf path) it pulls the embedded images out of the
pdf, writes them as ``figures/figNN.png``, and prints paste-ready markdown
embeds for the note.

usage:
    uv run extract-figures notes/literature/amat_keller_2015            # folder w/ paper.pdf
    uv run extract-figures notes/literature/amat_keller_2015/paper.pdf  # explicit pdf
    uv run extract-figures <pdf> --min-kb 30                            # raise size filter

note: pdf figure extraction is best-effort. papers whose figures are stored as
vector art (many Adobe-Illustrator sourced PDFs) or multi-panel plates may not
extract cleanly — for those, drop the publisher image into ``figures/`` by hand.
the point is that every reference ends up local, not hotlinked.
"""

import argparse
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    sys.exit("PyMuPDF not installed — run `uv sync` (pyproject lists pymupdf).")


def resolve_pdf(target: Path) -> Path:
    """accept a folder containing paper.pdf, or a direct .pdf path."""
    if target.is_dir():
        pdf = target / "paper.pdf"
        if not pdf.exists():
            pdfs = sorted(target.glob("*.pdf"))
            if not pdfs:
                sys.exit(f"no pdf found in {target}")
            pdf = pdfs[0]
        return pdf
    if target.suffix.lower() != ".pdf":
        sys.exit(f"not a pdf or folder: {target}")
    return target


def extract(pdf: Path, out_dir: Path, min_kb: int) -> list[Path]:
    """write each sufficiently-large embedded image to out_dir/figNN.png."""
    doc = fitz.open(pdf)
    out_dir.mkdir(parents=True, exist_ok=True)
    seen: set[int] = set()
    written: list[Path] = []
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen:
                continue
            seen.add(xref)
            pix = fitz.Pixmap(doc, xref)
            if pix.n - pix.alpha >= 4:  # CMYK / other -> RGB
                pix = fitz.Pixmap(fitz.csRGB, pix)
            data = pix.tobytes("png")
            if len(data) < min_kb * 1024:  # skip logos, rules, icons
                continue
            path = out_dir / f"fig{len(written) + 1:02d}.png"
            path.write_bytes(data)
            written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="extract raster figures from a paper pdf")
    parser.add_argument("target", type=Path, help="paper folder (with paper.pdf) or a pdf path")
    parser.add_argument("--min-kb", type=int, default=25,
                        help="skip images smaller than this many KB (default: 25)")
    args = parser.parse_args()

    pdf = resolve_pdf(args.target)
    out_dir = pdf.parent / "figures"
    written = extract(pdf, out_dir, args.min_kb)

    if not written:
        print(f"no raster figures ≥ {args.min_kb} KB found in {pdf.name} — "
              f"likely vector art; add figures to {out_dir}/ by hand.")
        return

    rel = out_dir.name
    print(f"wrote {len(written)} figure(s) to {out_dir}/\n")
    for p in written:
        print(f"![{p.stem}]({rel}/{p.name})")


if __name__ == "__main__":
    main()
