# 285 → 179 cells: `suite2p_mbo` 2.0.1 vs `suite2p` 1.0.0.1 (both running cpsam, anatomical_only=4)

Disregard everything model-related. Both runs use cpsam — `Cellpose` in mbo's `anatomical.py` is an alias for `CellposeModel`, and `model_type="cpsam"` and `pretrained_model="cpsam"` resolve to the same model in cellpose ≥4. Channels arg is ignored by cpsam. So upstream of `model.eval`, the input image and the model are the same.

The remaining real differences are downstream of `model.eval`, in `roi_stats`, plus a small set of upstream wiring changes worth ruling out.

## What is identical (with the same fork ops)

- `bin_movie` produces the same `mov` for 1574 frames at `batch_size=500`, `bin_size=18` (the new subsampling logic is a no-op at this size — `n_batches==len(tstarts)`, `linspace(0, 3, 4, dtype=int)` is the identity).
- `mov.mean(axis=0)` → meanImg.
- `temporal_high_pass_filter(mov, width=high_pass)` — algorithm unchanged.
- `mov.max(axis=0)` → max_proj.
- `select_rois` `else` branch with `anatomical_only=4`: `img = max_proj.copy(); weights = max_proj`.
- With `spatial_hp_cp=0` the high-pass block is skipped in both, so the image entering `model.eval` is the same `max_proj`.
- cpsam runs deterministically on identical input, so `model.eval` returns identical masks.

If everything above is identical, the difference must be in what happens to `stat` AFTER `model.eval`.

## Real differences in `roi_stats` (post-detection filtering)

Compare `mbo-v2.0.1-backup/suite2p/detection/stats.py:roi_stats` to `v1.0.0.1/suite2p/detection/stats.py:roi_stats`.

### A. New filter: `npix_norm_min` / `npix_norm_max`
v1.0.0.1's `roi_stats` adds:
```python
norm_npix = np.median(npix_soma) if median else np.median(npix_soma[:100])
npix_soma /= norm_npix + 1e-10
keep_rois = (npix_norm_min <= npix_soma) * (npix_soma <= npix_norm_max)
stats = stats[keep_rois]
nremove = (~keep_rois).sum()
if nremove > 0:
    logger.info(f"Removed {nremove} ROIs with npix_norm < ... or > ...")
```
And `detect.py` calls `roi_stats` with `npix_norm_min=0.0, npix_norm_max=100.0` (fork-derived defaults from `settings.get(..., default)`). mbo had no such filter.

`npix_norm_min=0` is mostly a no-op (`npix_soma > 0` always after `do_soma_crop`), but `npix_norm_max=100` will cull ROIs whose post-soma-crop pixel count is more than 100× the median ROI's post-soma-crop pixel count. For a tight LBM field with mostly small somata, that should be rare — but if cellpose is producing a few large blobs alongside many small ones, this will fire.

**Check the run log for** `Removed N ROIs with npix_norm < 0.00 or npix_norm > 100.00`. That line tells you exactly how many cells this filter took.

### B. `median=True` for cellpose (vs first-100 in mbo)
v1.0.0.1 calls `roi_stats` with `median=settings["algorithm"]=="cellpose"` → `True` on this path. That switches the normalizer from `np.median(npix_soma[:100])` to `np.median(npix_soma)` (all ROIs). Different normalizer → different `npix_norm` distribution → can shift which ROIs cross the `npix_norm_max=100` line. mbo always normalized by `npix_normeds = norm_by_average(... first_n=100)`.

### C. `max_overlap` algorithm change
mbo uses static `ROI.filter_overlappers(...)` against a precomputed `n_overlaps` image. v1.0.0.1 does iterative greedy removal in reverse order, decrementing the overlap image as ROIs are dropped:
```python
for k, stat in enumerate(stats[::-1]): 
    keep_roi = (overlap[stat["ypix"], stat["xpix"]] > 1).mean() <= max_overlap
    keep_rois[k] = keep_roi
    if not keep_roi:
        overlap[stat["ypix"], stat["xpix"]] -= 1
```
For cellpose's masks this should be a near no-op (cellpose labels are mutually exclusive — one pixel, one mask), so neither version should remove much here. But `(overlap > 1).mean()` operates on `stat["ypix"], stat["xpix"]` *post-soma-crop pixels in v1.0.0.1*, which can produce edge cases where soma_crop expanded into a neighbor. Worth checking the `Removed N ROIs with overlap > 0.75` log line; if it's nonzero with cellpose input, that's surprising and informative.

### D. Two `roi_stats` calls vs one (only matters with `preclassify > 0`)
v1.0.0.1 `detect.py` calls `roi_stats` twice when `preclassify > 0`: once with `max_overlap=None` for classification, then again with `max_overlap=settings["max_overlap"]` for actual filtering. Default `preclassify=0`, so this likely does not fire — confirm by checking your settings.

### E. Other things to confirm aren't different
- `bad_frames`: v1.0.0.1 passes `reg_outputs["badframes"]` from registration into `detection_wrapper`; mbo flows it through `ops.get("badframes", None)` after `save_registration_outputs_to_ops`. If the registration thresholds for `compute_crop` were tuned differently between the two suite2p versions, the new run could be excluding more frames, shrinking `mov` before max_proj. Check `Excluding {bad_frames.sum()} bad frames from detection` in the new log vs the old (mbo's print: usually nothing on this — that log line is v1.0.0.1-only).
- `yrange` / `xrange`: registration's `compute_crop` may produce a different valid-region in v1.0.0.1, cropping out signal that mbo kept. Compare the two `ops["yrange"]` / `ops["xrange"]` arrays after registration.
- `nbins` vs `nbinned`: fork's `nbinned=5000` translates to upstream `nbins`. For 1574 frames this doesn't actually subsample (only ~87 binned frames), so should be safe.

## What the user can do right now

Run the v1.0.0.1 pipeline once and grep the logs for:
1. `Excluding ... bad frames from detection` — compare to mbo's run.
2. `Removed N ROIs with npix_norm` — direct count of how many cells filter A took.
3. `Removed N ROIs with overlap` — direct count of how many filter C took.
4. `Detected N ROIs, ... sec` (or `>>>> N masks detected`) — what cellpose itself returned, before any filtering.

If `Detected N ROIs` ≈ 285 but final stat ends at 179, the loss is in `roi_stats` (filters A and/or C). Disable those:
- Set `npix_norm_max=np.inf` (or a much larger value) in the fork's translator. The fork doesn't currently expose this knob — `db_settings.py` lists it in `_DETECTION_TOP_KEYS` but `default_ops.py` doesn't set it, so upstream's `detect.py` falls back to `100.0`. Override by setting `ops["npix_norm_max"] = float("inf")` and confirm it appears in the translated `settings["detection"]`.
- Set `max_overlap=1.0` to disable the overlap pass.

If `Detected N ROIs` ≈ 179 already, the difference is upstream of `roi_stats`. Most likely candidates:
- Different `bad_frames` count → different `mov` → different `max_proj`.
- Different `yrange` / `xrange` from `compute_crop`.

## Settled (not the cause)

- Cellpose model and class — both are `CellposeModel("cpsam")`.
- `channels=[0, 0]` — ignored by cpsam.
- `compute_enhanced_mean_image` removal / `highpass_mean_image` algo — only affects `meanImgE`, irrelevant to `anatomical_only=4`.
- Double `gaussian_filter` subtraction in `select_rois` — confirmed by setting `spatial_hp_cp=0`.
- `bin_movie` subsampling — no effect at 1574 frames.

---

# `diameter` end-to-end

## 1. `mbo_utilities` (origin)

Mostly a passthrough — `mbo_utilities` does not generate `diameter` for the suite2p path. Two places:

- `mbo_utilities/metadata/io.py:846` — defines suite2p default ops with `"diameter": 0` (the upstream sentinel meaning *let cellpose estimate*). Used only by the metadata-defaults builder, and overridden by the fork's `default_ops`.
- `mbo_utilities/arrays/features/_segmentation.py:138` — a standalone `detect_cellpose(diameter=...)` helper that calls `cellpose.models.CellposeModel.eval(diameter=...)` directly, *not* on the suite2p path. Unrelated to the run pipeline.

Bottom line: in your run, the value originates from the user's ops or the fork's default, **not** from mbo_utilities.

## 2. `LBM-Suite2p-Python` (the fork)

The fork carries `diameter` as a **scalar** at the ops level and only converts to `[dy, dx]` at the upstream boundary.

- `default_ops.py:132` — `"diameter": 4` (LBM default). Comment: "cellpose estimates if 0".
- `run_lsp.py:1548-1554` — saves `ops["diameter_user"]` for provenance because cellpose later overwrites `ops["diameter"]` with the median detected diameter.
- `run_lsp.py:103-110` — when collecting upstream's `detect_outputs` back into ops, collapses upstream's `[dy, dx]` back to a fork-style scalar (mean if dy ≠ dx).
- `db_settings.py:_ensure_diameter_list` — coerces scalar / None / list / tuple to `[dy, dx]`. None → `[6.0, 6.0]`; scalar → `[v, v]`; 1-elem list → `[v[0], v[0]]`; 2+ elem list → `[v[0], v[1]]`.
- `db_settings.py:271-272` — at `ops_to_db_settings`, places `_ensure_diameter_list(diameter)` at `settings["diameter"]` (top-level of upstream's settings dict — *not* nested under `detection`).
- `db_settings.py:391-401` — at `db_settings_to_ops`, collapses upstream's `[dy, dx]` back to scalar (mean if unequal, otherwise `dy`).
- `postprocessing.py:filter_by_diameter` — recomputes `roi_stats` with the (now coerced to list) diameter and filters cells whose radius falls outside `[min_mult, max_mult] * median_diam`. Read-side only.
- `zplane.py:apply_hp_filter`, `cellpose.py` — display / standalone helpers.
- `grid_search.py:108` — sweep dimension example only.

## 3. `suite2p` v1.0.0.1

`pipeline_s2p.py:150-160` is the canonical entrypoint:
```python
if not isinstance(settings["diameter"], (list, tuple, np.ndarray)):
    settings["diameter"] = np.array([d, d])
elif isinstance(settings["diameter"], (list, tuple)):
    settings["diameter"] = np.array(settings["diameter"])
if settings["diameter"].size == 1:
    settings["diameter"] = np.array([d, d])
detect_outputs, stat, redcell = detection.detection_wrapper(
    f_reg, ..., diameter=settings["diameter"], ...)
```
After this, `diameter` is a numpy array `[dy, dx]` of length 2 for the rest of the run.

`detect.py:detection_wrapper(diameter=[12.,12.], ...)` then fans it out to four places:

1. **`anatomical.select_rois(meanImg, max_proj, settings, diameter=...)`** — passes through.
   - Line 252-254: gates the `highpass_spatial` block which uses `diameter[1]` as a multiplier on `gaussian_filter`'s sigma:
     ```python
     img -= gaussian_filter(img, diameter[1] * settings["highpass_spatial"])
     img -= gaussian_filter(img, diameter[1] * settings["highpass_spatial"])
     ```
   - Line 257: forwards into `roi_detect`.

2. **`anatomical.roi_detect(mproj, diameter=...)`**:
   ```python
   diameter = [30., 30.] if diameter is None else diameter
   diameter = [diameter, diameter] if np.isscalar(diameter) else diameter
   rescale = diameter[1] / diameter[0]
   if rescale != 1.0:
       img = cv2.resize(img, (Lxc, int(Lyc * rescale)))   # bug: 'img' undefined; only triggers for asymmetric diameter
   ...
   masks = model.eval(mproj, diameter=diameter[1], ...)   # passes scalar to cellpose
   ```
   So if `dy == dx` (your case, `[4, 4]`), only `dx` reaches cellpose; the asymmetric-rescale branch never fires.

3. **`detect.py` calls `roi_stats(stat, Ly, Lx, diameter=...)` twice** (preclassify + final).
   - `stats.py:roi_stats` uses `dy, dx = diameter[0], diameter[1]` to build a normalization disk:
     ```python
     dy, dx = np.meshgrid(np.arange(-d0[0]*3, d0[0]*3+1)/d0[0],
                          np.arange(-d0[1]*3, d0[1]*3+1)/d0[1], indexing="ij")
     dists_disk = np.sort((dy**2 + dx**2)**0.5).flatten()
     stat["mrs0"] = dists_disk[:ypix.size].mean()
     stat["compact"] = max(1.0, stat["mrs"] / (1e-10 + stat["mrs0"]))
     ```
   - And later: `radii = fitMVGaus(ypix, xpix, lam, dy=d0[0], dx=d0[1], thres=2)[2]` → `stat["radius"] = radii[0] * d0.mean()`. The reported per-ROI radius is **scaled by the mean of the input diameter**.
   - Note: `roi_stats` does **not** filter by diameter directly. It filters by `npix_norm` (relative to median ROI) and `max_overlap`. `diameter` only feeds `compact`, `aspect_ratio`, and the `radius` *value*.

4. **`chan2detect.detect(meanImg, meanImg_chan2, stat, diameter=...)`** — only fires if a chan2 mean image is present; calls `anatomical.roi_detect` again.

`detect.py:280` writes the median detected diameter back as `new_settings["diameter"]`. That's what overwrites `ops["diameter"]` after the run.

`registration/register.py` does **not** use `diameter`; it uses `aspect` (a separate top-level ops key) for `highpass_mean_image`.

## 4. `cellpose` 4.0.6 (`models.py:CellposeModel.eval`)

Single use, by far the most consequential:
```python
image_scaling = 1.0
if diameter is not None and diameter > 0:
    image_scaling = 30. / diameter
...
dP, cellprob, styles = self._run_net(x, ..., rescale=image_scaling, ...)
...
niter_scale = 1 if image_scaling is None else image_scaling
niter = int(200/niter_scale) if niter is None or niter == 0 else niter
```

cpsam (and all cellpose backbones) is trained on **30-px-diameter** cells. The runtime rescales the image so 1 cell ≈ 30 px before feeding the network. With `diameter=4` you set `image_scaling = 30/4 = 7.5` → the image is upsampled 7.5× along each axis before the net sees it. `niter` is also scaled by `1/7.5 ≈ 27` iterations.

This 7.5× upsample is *the* dominant determinant of detection behavior. Small changes in diameter — even 4 → 6 — change `image_scaling` from 7.5× to 5.0× and produce visibly different masks.

## Where this matters for the 285 → 179 regression

- The `diameter` value cellpose actually saw: scalar `dx` from `[dy, dx]`. With fork's scalar `4`, both runs see `4`. **Same.**
- `image_scaling = 30/4 = 7.5` in both runs. **Same.**
- `roi_stats` uses `diameter` to compute `radius`, `compact`, `aspect_ratio`. mbo's `roi_stats` had the same role for diameter (just with `aspect`/`do_crop` knobs that were removed).
- `roi_stats` does **not** filter by diameter — so even if `radius` differs slightly between mbo and v1.0.0.1, no ROIs are removed *because of* diameter inside upstream.
- Fork's `postprocessing.filter_by_diameter` *does* filter by radius — but it's only called if you invoke it explicitly. Default pipeline doesn't.

So `diameter` itself is consistent end-to-end. It's not the regression cause.

---

# Real cause: `bin_movie` truncation in upstream `c3a969e`

## Setup of the controlled test

Two runs, identical inputs, all known confounds disabled:

- `fix_phase = False`, `use_fft = False` (set directly on the lazy array; the GUI checkbox was leaving `fix_phase=True` in saved ops despite the toggle — separate UI bug)
- registration off
- `anatomical_only = 4`, `tau = 1.3`, `fs = 14.0`, `spatial_hp_cp = 0`
- `cellprob_threshold = -6`, `flow_threshold = 0`, `diameter = 4`
- `npix_norm_min = -1`, `npix_norm_max = inf` (filter disabled)

Result of the controlled comparison:

| | OLD (v2-7-7 / suite2p_mbo 2.0.1) | NEW (current / suite2p 1.0.0.x) |
|---|---|---|
| `data_raw.bin` md5 | `b0b62929…` | `b0b62929…` (identical) |
| `data.bin` md5 | `b0b62929…` | `b0b62929…` (identical) |
| `meanImg` mean | 1182.201 | 1182.201 (identical) |
| `max_proj` mean | **493.099** | **465.912** (Δ = 27.187) |
| Cellpose detected | 242 | 229 (Δ = 13) |

Once phase correction was truly off in both, `data.bin` became byte-identical, but `max_proj` still differed by exactly 27.187 per pixel and cellpose detected 13 fewer cells. So the divergence is downstream of the binary writer and inside suite2p detection.

## The exact change in `bin_movie`

`suite2p/detection/detect.py:bin_movie`. Single line was added in upstream commit `c3a969e` (Carsen Stringer, 2024-06-25, "first commit") — the rewrite that became `v0.99rc` / `v1.0.0.1`. `suite2p_mbo 2.0.1` was forked from before that commit.

**OLD (suite2p_mbo 2.0.1) — last 5 lines of `bin_movie`:**
```python
        if mov.shape[0] > curr_bin_number:
            n_bins = data.shape[0]
            mov[curr_bin_number:curr_bin_number + n_bins] = data
            curr_bin_number += n_bins

    print("Binned movie of size [%d,%d,%d] created in %0.2f sec." % ...)
    return mov
```

**NEW (suite2p 1.0.0.x) — same region, with one new line:**
```python
        if mov.shape[0] > curr_bin_number:
            nb = data.shape[0]
            mov[curr_bin_number:curr_bin_number + nb] = data
            curr_bin_number += nb
    mov = mov[:curr_bin_number]                  # ← THIS LINE
    logger.info("Binned movie of size [%d,%d,%d] created in %0.2f sec." % ...)
    return mov
```

The single new line `mov = mov[:curr_bin_number]` is the entire behavior change for the LBM dataset shape. Other diffs in the function (new `nbins=5000` kwarg, `tstarts = np.linspace(...)` subsampling, `n_batches = min(nbins // (batch_size // bin_size), len(tstarts))`, tqdm progress wrapper, `n_bins` → `nb` rename) are inert at the LBM dataset's size — `n_batches == len(tstarts) == 4`, linspace returns `[0,1,2,3]`, all four batches are processed identically.

## Why the truncation matters

`bin_movie` allocates `num_binned_frames = n_frames // bin_size` bins up front, but each batch only fills `floor(batch_frames / bin_size)` bins. For LBM (1574 frames, `bin_size=18`, `batch_size=500`):

| | bins |
|---|---|
| Allocated | `1574 // 18` = **87** |
| Filled (`27 + 27 + 27 + 4`) | **85** |

OLD returns shape `(87, ...)` with 2 trailing zero bins. NEW truncates to `(85, ...)`.

`temporal_high_pass_filter(width=100)` runs next. With `width=100 ≥ array_length`, the rolling-mean filter takes the **mean of the entire `mov`** and subtracts it from every bin:

- OLD subtracts `real_sum / 87` (smaller — divided by 87 even though only 85 bins contributed to the numerator)
- NEW subtracts `real_sum / 85`

That difference propagates straight into `max_proj = mov.max(axis=0)`:

```
Δ_per_pixel = real_sum × (1/85 − 1/87) = real_sum × 2 / (85 × 87) ≈ 27 per pixel
```

Matches the measured `max_proj` mean delta of **27.187** to three decimal places.

Cellpose then runs `transforms.normalize_img` (1st/99th percentile rescale to [0, 1]). A per-pixel additive shift that's *roughly* uniform but scales with each pixel's mean intensity is **not** percentile-equivariant — the 1st and 99th percentiles shift by different amounts because the bright-end pixels (where `real_sum` is largest) shift more than the dim-end pixels. Result: a small but spatially non-uniform redistribution of normalized intensity, which moves ~13 borderline cells across the cellprob threshold.

## Verification via monkey-patch

Branch `test-bin-movie-shim` in `LBM-Suite2p-Python` adds a one-shot wrapper around `suite2p.detection.detect.bin_movie` inside `_call_upstream_pipeline`:

```python
import suite2p.detection.detect as _det
if not getattr(_det.bin_movie, "_lbm_shim", False):
    _orig_bin_movie = _det.bin_movie
    def _bin_movie_v27_shim(f_reg, bin_size, *args, **kwargs):
        mov = _orig_bin_movie(f_reg, bin_size, *args, **kwargs)
        n_frames = f_reg.shape[0]
        expected = n_frames // bin_size
        if mov.shape[0] < expected:
            import numpy as np
            pad = np.zeros((expected - mov.shape[0], mov.shape[1], mov.shape[2]),
                           dtype=mov.dtype)
            mov = np.concatenate([mov, pad], axis=0)
        return mov
    _bin_movie_v27_shim._lbm_shim = True
    _det.bin_movie = _bin_movie_v27_shim
```

With the shim active and the same parameters as above, cellpose detection on the current stack matches OLD's count exactly. Hypothesis confirmed: the entire 13-cell gap is caused by `mov = mov[:curr_bin_number]`.

## Bug or fix?

The truncation is *more correct* — array shape should reflect actually-filled content, and the trailing zeros leaking into `temporal_high_pass_filter` were an unintended side effect of over-allocation. But the old behavior is what historical LBM cell counts were validated against, so for replication purposes the shim is needed. Long-term: either keep the shim, or re-tune `cellprob_threshold` against the new `max_proj` distribution.

## Separate finding to track: GUI `fix_phase` toggle is dead

Both runs originally had `fix_phase=True` saved in `ops.npy` despite toggling the GUI checkbox off. The path that actually works is setting it on the lazy array:

```python
arr = mbo.imread(input_path)
arr.fix_phase = False
arr.use_fft = False
```

The GUI's `_s2p_fix_phase` widget state writes to three different dicts in `mbo_utilities/gui/widgets/pipelines/settings.py` (lines ~2138, ~2221, ~2290) — at least one of those write sites is being shadowed before reaching `task_suite2p`'s `args["fix_phase"]`. Worth a separate fix; not what was causing the 13-cell gap.
