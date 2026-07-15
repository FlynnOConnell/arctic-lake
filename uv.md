# Self-contained scripts with uv (PEP 723)

How to make a single `.py` file that builds its **own** virtualenv on the fly —
no project, no `pip install`, no "which venv am I in". `uv run script.py` reads an
inline metadata block, resolves + builds an ephemeral env (cached, keyed on the
exact requirement set), and runs the file in it.

This is the pattern behind `neuro-storm/neuro_storm/cli/masknmf_gui.py`, which
pulls a local research package (`masknmf`), overrides one of its transitive pins
to an unreleased git commit, and runs — all from one file.

## The building blocks

### 1. Shebang + PEP 723 metadata block
```python
#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["numpy>=1.26", "tifffile"]
# ///
```
`# /// script ... # ///` is the PEP 723 standard. `dependencies` is a list of
PEP 508 requirements. `uv run file.py` (or `./file.py` via the shebang) builds a
venv containing exactly those + their transitive deps. **Why it works:** uv keeps
a per-requirement-set env under `~/.cache/uv/environments-v2/`, so the first run
resolves/builds and every later run with the same metadata is instant. `env -S`
lets a shebang carry multiple args (`uv run --quiet`).

### 2. A local package as an editable source — `[tool.uv.sources]`
```toml
# [tool.uv.sources]
# masknmf = { path = "/abs/path/to/masknmf-toolbox", editable = true }
```
`dependencies = ["masknmf"]` says *what*; `[tool.uv.sources]` says *where to get
it*. `path = ... editable = true` builds the local source tree in place, so edits
to that repo are picked up without a reinstall. **Why it works:** uv builds it
with its declared build backend (here `flit_core`) into the ephemeral env.
Sources only redirect the location — version/pin constraints from every requirer
still have to be satisfied.

### 3. Forcing a transitive dep to a git commit — `[tool.uv] override-dependencies`
The problem: `masknmf` hard-pins `fastplotlib==0.6.1`, but its current code needs
an API (`fpl.NDWidget`) that only exists on fastplotlib's unreleased `ndwidget`
branch. `[tool.uv.sources]` can't do it, because the git build's dynamic version
isn't `0.6.1`, so the `==0.6.1` pin conflicts.
```toml
# [tool.uv]
# override-dependencies = [
#   "fastplotlib[imgui,notebook] @ git+https://github.com/fastplotlib/fastplotlib@a80884a3b14324407b323b5b6d2b3c80d27ba218",
# ]
```
**Why it works:** `override-dependencies` *discards* every other constraint on
that package (including a downstream `==` pin) and replaces it with this one
requirement. The `name[extras] @ git+URL@<full-sha>` form is a PEP 508 direct
reference — pin to a **full** 40-char commit SHA for reproducibility; extras in
the brackets are preserved (so imgui/notebook deps still install).

### 4. Cloning a git dep that uses git-LFS — `GIT_LFS_SKIP_SMUDGE=1`
fastplotlib stores a docs asset in git-LFS with a missing object on the remote,
so `git reset --hard <sha>` aborts during checkout. Set `GIT_LFS_SKIP_SMUDGE=1`
so git writes LFS pointer files instead of downloading blobs (the package builds
fine without the docs PNG). Bake it into the shebang so `./file.py` just works:
```python
#!/usr/bin/env -S GIT_LFS_SKIP_SMUDGE=1 uv run --quiet
```
`env -S` treats a leading `NAME=VALUE` token as an environment assignment before
the command. Only needed for the *first* clone — uv caches the built git wheel
under `~/.cache/uv/git-v0/`, so later runs reuse it.

## Verifying / iterating
- Run with a lightweight mode first (e.g. a `--print-params` path that imports
  nothing heavy) to check the file parses and the pure-Python layer works.
- `uv run --quiet file.py` re-resolves only when the metadata block changes;
  edit deps → next run rebuilds the env.
- To debug a failing git dep, clear its checkout: `rm -rf ~/.cache/uv/git-v0/checkouts/<hash>`.

## Gotchas hit in practice
- **Undeclared transitive imports.** `masknmf` imports `cv2` but never lists
  opencv. A fresh resolution won't have it — add `opencv-python-headless`
  explicitly to `dependencies`. (Headless avoids Qt/libGL conflicts with the
  wgpu/glfw GUI stack.)
- **Dynamic-version git deps vs `==` pins.** Can't be satisfied by
  `[tool.uv.sources]` alone; use `override-dependencies`.
- **Short SHAs.** uv/git may not resolve a 7-char SHA reliably; use the full
  40-char hash (get it from `https://api.github.com/repos/<o>/<r>/commits/<short>`).
- **A broken editable source breaks import in every mode.** Import the heavy
  package lazily inside the functions that need it, so pure-data/param code still
  runs when the source tree is mid-development.
- **Run it, don't just construct it.** Reading source can miss required
  arguments — the real `pipeline.run()` needed a `frame_rate` positional that a
  source read had reported as absent; only an actual end-to-end run caught it.
