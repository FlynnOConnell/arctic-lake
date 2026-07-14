# docs repo usage

markdown notes vault, editable in Obsidian or VSCode. daily/weekly meeting notes
now live in the private `notes_pvt` repo (`~/repos/notes_pvt/mbo/`).

## navigating

- **[INDEX.md](INDEX.md)** — generated index of every note; ctrl/cmd+click to open.
- `Ctrl+P` — fuzzy quick-open by filename.
- `Ctrl+Shift+F` — full-text search.
- `uv run build-index` — regenerate `INDEX.md` (also runs via the pre-commit hook).

## building the static site

```bash
uv run build-docs          # build sphinx site into docs/_build/html
uv run build-docs --serve  # live preview server
uv run build-docs --open   # build and open in browser
```

## exporting a single note

```bash
uv run export-note notes/some-note.md -o ./exports   # export one note to static HTML
```

## exports.toml

configure additional content to export.

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

## collapsible callouts

use obsidian callouts for hidden/collapsible content with anchors.

```markdown
> [!proposal]- LBM-Suite2p Output Structure
> content here, supports code blocks:
> ```
> results/
> ├── zplane01_tp00001-05000/
> │   ├── data_raw.bin
> │   └── ...
> ```
```

- `-` after type = collapsed by default (omit for open)
- auto-generates anchor: `#proposal-lbm-suite2p-output-structure`
- purple accent for `[!proposal]` type

**linking to callouts:**
```markdown
See [output structure](#proposal-lbm-suite2p-output-structure)
```

## task checkboxes

```markdown
- [ ] unchecked (open)
- [x] checked (done, strikethrough)
- [~] partial (orange, in-progress)
```

## powershell utilities

added to profile (`$PROFILE`):

```powershell
# list neovim keybindings
nvim-keys                    # normal mode (default)
nvim-keys -mode v            # visual mode
nvim-keys -mode i            # insert mode
nvim-keys -filter "leader"   # filter by pattern
nvim-keys-all                # all modes
```

## directory structure

```
docs/
├── notes/                   # software, sops, literature, personal notes
├── templates/
│   └── sop.md               # SOP template
├── scripts/
│   ├── build_index.py       # generate INDEX.md
│   ├── build_docs.py        # sphinx site build
│   ├── export_note.py       # single note export
│   └── config.py            # paths config
├── exports/                 # local HTML output
├── exports.toml             # additional export config
├── INDEX.md                 # generated vault index
└── usage.md                 # this file
```

## notebook naming convention

processing notebooks use format: `YYYY-MM-DD_author_title_YYYYMMDD.html`

example: `2025-12-03_wsnyder_behavior-averaging_20260107.html`
→ displays as: "Behavior Averaging (wsnyder, 2025-12-03)"
