# arctic-lake

arctic-lake is just a badass name for a place to keep my notes, literature and stuff.

Personal notes vault (markdown). Editable in Obsidian or VSCode.

## Navigating in VSCode

- **[INDEX.md](INDEX.md)** — generated index of every note, grouped by recency, category, tag, and folder. Ctrl/Cmd+click any link to open.
- `Ctrl+P` — fuzzy quick-open by filename.
- `Ctrl+Shift+F` — full-text search across the vault.
- Install the recommended **Foam** extension (prompted on open, see `.vscode/extensions.json`) to make `[[wikilinks]]` clickable and get backlinks + a graph.

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
