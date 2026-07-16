# arctic-lake

arctic-lake is just a badass name for a place to keep my notes, literature and stuff.

Personal notes vault (markdown). Editable in Obsidian or VSCode. Private notes live elsewhere but may be referenced.

## Regenerating the index

`INDEX.md` is generated — don't edit it by hand.

```bash
uv run build-index          # rebuild INDEX.md
uv run build-index --check  # verify it's current (used by the pre-commit hook)
```

A git pre-commit hook regenerates it automatically. Enable hooks once with:

```bash
git config core.hooksPath .githooks
```

## Building the static site

```bash
uv run build-docs          # build sphinx site into docs/_build/html
uv run build-docs --serve  # live preview server
uv run build-docs --open   # build and open in browser
```

## Exporting a single note

```bash
uv run export-note notes/some-note.md -o ./exports   # export one note to static HTML
```

Rendered HTML lands in `exports/`, which is gitignored — it's generated output, kept local and never pushed.

## exports.toml

Configure additional content to export.

```toml
# auto-scan markdown directories (converts to HTML)
[[directories]]
source = "Y:/foconnell/notebook/notes/sop"
output_subdir = "sops"
category = "SOPs"
pattern = "*.md"

# copy pre-rendered HTML (jupyter notebooks, etc)
[[html_directories]]
source = "Y:/foconnell/notebook/processing"
output_subdir = "notebooks"
category = "Processing Notebooks"
pattern = "*.html"

# individual pages
[[pages]]
source = "notes/projects/overview.md"
output = "projects/overview.html"
title = "Project Overview"
category = "Projects"
```

## Writing notes

### Images

Store images in an `images/` folder next to the note and reference them relatively:

```markdown
![](./images/example.png)
```

### Literature notes

One folder per paper under `notes/literature/<citekey>/` — folder name = bibtex citekey = `[[wikilink]]` target:

- `<citekey>.md` — the note (start from `templates/literature.md`)
- `paper.pdf` — the source PDF, when available
- `figures/` — paper figures as `figN.<ext>`; generate with `uv run extract-figures notes/literature/<citekey>`
- `source.md` — optional archived full-text (excluded from the index)

Citekey = tool name for tools (`rastermap`, `suite2p`), else `firstauthor_year`. Cross-link the tool note with `paper:` / `papers:` frontmatter; browse everything via [notes/literature/index.md](notes/literature/index.md). Notes on **published** papers live here (public); unpublished/in-press papers and grants stay in the private repo (separate process).

### Collapsible callouts

Use Obsidian callouts for hidden/collapsible content with anchors.

    > [!proposal]- LBM-Suite2p Output Structure
    > content here, supports code blocks

- `-` after the type = collapsed by default (omit for open)
- auto-generates an anchor: `#proposal-lbm-suite2p-output-structure`
- purple accent for `[!proposal]` type
- link to it with `See [output structure](#proposal-lbm-suite2p-output-structure)`

### Task checkboxes

```markdown
- [ ] unchecked (open)
- [x] checked (done, strikethrough)
- [~] partial (orange, in-progress)
```

## PowerShell utilities

Added to profile (`$PROFILE`):

```powershell
nvim-keys                    # list neovim keybindings (normal mode)
nvim-keys -mode v            # visual mode
nvim-keys -filter "leader"   # filter by pattern
nvim-keys-all                # all modes
```

## Directory structure

```
arctic-lake/
├── notes/          # software, sops, literature, personal notes
├── templates/      # note templates (e.g. sop.md)
├── scripts/        # build_index.py, build_docs.py, export_note.py, config.py
├── static/         # shared logos + videos
├── docs/           # sphinx site source
├── private/        # arctic-lake-private repo (nested, gitignored)
├── exports.toml    # export config
├── INDEX.md        # generated vault index
└── references.bib
```
