# docs repo usage

export obsidian notes to static HTML for sharing via OneDrive.

## quick start

```bash
# export current week to local exports/
uv run export-weekly

# sync to both OneDrive AND network share (Y: drive)
uv run export-weekly --sync

# sync to network only (accessible from all lab computers)
uv run export-weekly --network

# force overwrite (backs up existing to X: drive)
uv run export-weekly --sync --force

# create next week's note with current TO-DOs
uv run export-weekly --next
```

**or double-click:** `sync-notes.bat` to sync everything

## cli options

| flag | description |
|------|-------------|
| `2026-W03` | export specific week |
| `--all`, `-a` | export all available weeks |
| `--sync`, `-s` | sync to both OneDrive AND network share |
| `--onedrive` | sync to OneDrive only |
| `--network` | sync to network share only (Y: drive) |
| `--force`, `-f` | overwrite existing files (creates backup first) |
| `--next`, `-n` | create next week's note with current TO-DOs |
| `--list` | list available weeks |
| `--output-dir`, `-o` | custom output directory |

## destinations

- **local**: `exports/weekly/`
- **network**: `Y:/foconnell/weekly_meeting_static/` → `\\RBO-S1\mbospace\foconnell\weekly_meeting_static`
- **onedrive**: `OneDrive - The Rockefeller University/MBO_DATA/weekly_meeting_static/`
- **backup**: `X:/backups/foconnell/weekly_meeting/`

## accessing from other computers

anyone on the network can open the notes at:
```
\\RBO-S1\mbospace\foconnell\weekly_meeting_static\index.html
```

or if Y: drive is mapped:
```
Y:\foconnell\weekly_meeting_static\index.html
```

## exports.toml

configure additional content to export alongside weekly notes.

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

## weekly note template

located at `templates/weekly.md`. sections with only `-` are auto-filtered from export.

```markdown
## (previous) TO-DO
*from [[2026-W03]]*
- [ ] item from last week

## Weekly Overview
summary of the week

## Main Projects
#### mbo_utilities
- work done

## (Next) TO-DO
*for [[2026-W05]]*
- [ ] items for next week
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

## links extraction

links from daily notes are automatically extracted and shown at the bottom of weekly HTML exports. no need for dataviewjs in the weekly template.

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
├── daily/                   # daily notes (YYYY-MM-DD.md)
├── weekly/                  # weekly notes (YYYY-Www.md)
├── templates/
│   ├── weekly.md            # weekly meeting template
│   ├── daily.md             # daily note template
│   └── sop.md               # SOP template
├── scripts/
│   ├── export_weekly.py     # main export script
│   ├── export_note.py       # single note export
│   └── config.py            # paths config
├── exports/                  # local HTML output
│   └── weekly/
├── exports.toml             # additional export config
└── usage.md                 # this file
```

## workflow

1. write daily notes in `daily/YYYY-MM-DD.md`
2. write weekly summary in `weekly/YYYY-Www.md`
3. run `uv run export-weekly --sync` to publish
4. run `uv run export-weekly --next` to create next week's note

## notebook naming convention

processing notebooks use format: `YYYY-MM-DD_author_title_YYYYMMDD.html`

example: `2025-12-03_wsnyder_behavior-averaging_20260107.html`
→ displays as: "Behavior Averaging (wsnyder, 2025-12-03)"
