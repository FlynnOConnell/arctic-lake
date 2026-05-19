---
title: IsoView Python pipeline
tags: [isoview, light-sheet-microscopy, image-fusion, python-port]
---

# IsoView Python pipeline

Internal reference for the Python port of `clusterPT` + `clusterMF`.
Single-color, per-timepoint or per-tile correction and multi-view fusion.
Companion to [notes/software/isoview.md](../notes/software/isoview.md) (MATLAB pipeline reference).

## Scope

Two entry points:

- `isoview.correct_stack(config)` — per-camera correction
  (dead-pixel, segmentation, mask, coordinate masks, projections).
- `isoview.multi_fuse(config)` — per-camera-pair registration, intensity
  correction, blending, optional VW90→VW00 orientation.

Downstream MATLAB stages (`localAP`, `clusterTF`, `clusterFR`, `localCP`,
`localEC`, `clusterCS`, `clusterRS`, `localCR`, `clusterCD`, `clusterIS`)
are not ported.

## Modes

Auto-detected from raw `.stack` filenames `SPC##_TM#####_ANG###_CM#_CHN##_PH#.stack`:

- **timelapse** — multiple TM, single SPC. Output: `<dataset>.corrected/SPM##/TM######/`.
- **tiled** — single TM, multiple SPC. Output: `<dataset>.corrected/SPM##/` (no TM subdir).

Decision in `isoview.io.detect_mode`. `config.tiled` is a computed
property: `len(specimens) > 1 and len(timepoints) <= 1`.

## Pipeline flow

### correct_stack

`isoview/pipeline.py:IsoviewProcessor`

For each specimen (tiled) or each timepoint (timelapse):

1. **Load raw `.stack`** via memmap (`isoview.io.read_volume`, depth from
   filesize + XML W/H).
2. **Dead-pixel correction** (`isoview.corrections.correct_dead_pixels`)
   — only if `median_kernel` is set.
3. **Background-stack percentile** for `minIntensity[1]`.
4. **Segmentation** (`isoview.segmentation.segment_foreground`) when
   `segment_mode == 1`:
   - Anisotropic Gaussian smoothing with slab-margin reassembly.
   - Adaptive threshold from `(min + (mean - min) * threshold)`.
5. **Optional mask application** (`apply_segmentation_mask=True` → `stack *= mask`).
6. **Save** corrected volume → OME-TIFF/OME-Zarr.
7. **Save** xy projection → `SPM##/projections/`.
8. **Save** coordinate masks (xz, xy) from the binary mask.
9. **Optional Tenengrad diagnostic** per camera pair.

### multi_fuse

`isoview/fusion.py:_fuse_camera_pair`

For each `(cam0, cam1)` pair in each tile/timepoint:

1. Load both corrected volumes + segmentation masks (or rebuild masks
   from volumes if missing).
2. Apply per-view crop (`crop_front/depth/top/height/left/width`, keyed
   by view index).
3. Apply flip_z / rotation / flip_h/v to cam1 (and its mask).
4. Estimate XY + rotation transform (`estimate_camera_transform`).
5. Apply transform to cam1 volume and mask.
6. Estimate and apply intensity correction.
7. Build slice masks, average-mask in **overlap mode** (avoids
   union-mode edge artifact), remove anomalies.
8. Blend via `adaptive` (or `geometric`) — auto resolves to adaptive
   when `blending_method="auto"`.
9. Optional per-tile `view_orientation` override for VW90→VW00.
10. Save fused volume + xy/xz/yz projections.

## Output layout

```
<dataset>.corrected/
  SPM##/                            # tiled: files directly here
    SPM##_CM#.ome.tif               # corrected volume
    SPM##_CM#.segmentationMask.ome.tif
    SPM##_CM#.xyMask.tif            # 2D coord mask
    SPM##_CM#.xzMask.tif            # 2D coord mask
    SPM##_CM#.minIntensity.npz
    SPM##_CHN##.xml                 # per-channel metadata copy
    projections/                    # NEW: per-specimen projections dir
      SPM##_CM#.xyProjection.tif
      SPM##_CM#.raw.xyProjection.tif
    correction.log

  SPM##/                            # timelapse: TM subdir per timepoint
    TM######/
      SPM##_TM######_CM#.ome.tif
      ...
    projections/
      SPM##_TM######_CM#.xyProjection.tif
      ...

<dataset>.fused/
  <method>/                         # adaptive | geometric
    SPM##/                          # or TM######/ for timelapse
      SPM##_CM##_CM##_VW##.ome.tif
      SPM##_CM##_CM##_VW##.xyProjection.tif
      SPM##_CM##_CM##_VW##.xzProjection.tif
      SPM##_CM##_CM##_VW##.yzProjection.tif

isoview_config.json                  # at dataset root, tracks all runs
```

## Processing equivalence to MATLAB

Refs: `clusterPT_RC.m`, `processTimepoint_RC.m`, `multiFuse.m`.

### Equivalent (same algorithm)

| Step | MATLAB | Python |
|------|--------|--------|
| Dead-pixel detection | `correctInsensitivePixels` (proc.m:1028) | `correct_dead_pixels` (corrections.py:30) |
| Knee threshold | `determineThreshold` (proc.m:1061) | `_determine_threshold` (corrections.py:80) |
| Anisotropic Gaussian | `imgaussianAnisotropy` (proc.m:1087) | `_imgaussian_anisotropy` (segmentation.py:22) |
| Slab smoothing with margin | proc.m:485-504 | segmentation.py:69-85 |
| Adaptive threshold | proc.m:511-534 | segmentation.py:87-100 |
| Background value | `prctile(sub[>0], 5)` proc.m:466 | `percentile_interp(sub[>0], 5)` pipeline.py:227 |
| Coordinate masks | proc.m:584-668 | `create_coordinate_masks` segmentation.py:111 |
| Camera-pair XY/rot registration | `multiFuse.m` | `estimate_camera_transform` |
| Adaptive / geometric blending | `multiFuse.m` | `blend_views` |

### Intentionally different

| Aspect | MATLAB | Python | Rationale |
|--------|--------|--------|-----------|
| `apply_segmentation_mask` default | On (`stack .* mask` unconditional) | Off | Mask saved separately; gating defers to user. |
| Rotation in correction | `rotationFlag` applied before segmentation | Deferred to fusion | Correction writes raw-orientation data; fusion is the only stage that needs view-aligned volumes. |
| Splitting axis for Gaussian | Splits along rotated first axis (proc.m:489) | Splits along Y of raw volume (segmentation.py:72) | Same anatomical axis at different rotation states. Functionally equivalent. |
| Background image rotation/save | Yes (clusterPT_RC.m:202-209) | No | QC-only; we don't preserve a rotated background image. |
| Percentile for background scalar | `prctile(bg, 3)` hardcoded | `config.background_percentile` (default 5) | Tiny shift in dead-pixel mean-projection subtract; not material. |

### Not implemented

| Feature | MATLAB | Why skipped |
|---------|--------|-------------|
| References / dependents (channel groups sharing masks) | `references=[0;1]; dependents=[2;3]` | Multi-color experiment feature. Our setup is single-channel-per-camera. |
| Cross-channel mask OR-fusion | `references=[0 1]` (single row) | Same as above. |
| 3-pass global temporal mask (`segmentFlag=2 → union → 3`) | `clusterPT_RC.m:526-585`, `proc.m:256-280, 729-732` | Useful for stable-sample timelapses (fixed embryo, etc.). Per-TM masks suffice for current scope; would add a post-pass union helper rather than re-running. |
| Crop-on-read during correction | `multibandread` slicing in proc.m:409-413 | Crops are applied in fusion (`config.crop_*` keyed by view). Trade: more memory during correction, more flexibility downstream. |
| Multi-channel per camera | `for c = cameras, for h = channels` (proc.m:338-341) | Hardware: each CM has one CHN via `camera_view_map`. |
| `correctionDatabase.mat` save | Logging-gated in proc.m:449-457 | Diagnostic only. Add if a camera's dead-pixel pattern needs auditing. |

## File formats

- **Volumes**: OME-TIFF (`.ome.tif`) or OME-Zarr (`.ome.zarr`). Both are
  written as 5D `TCZYX` (singleton T, C for single-channel data). OME-XML
  metadata always written; pixel spacing in physical units (µm) when
  available from XML.
- **Masks**: same format as volumes (`.segmentationMask.ome.tif` or
  `.segmentationMask.ome.zarr`). uint16 0/1. Minimal OME wrapper —
  spec-compliant but no rich channel metadata.
- **Coordinate masks** (`xyMask`, `xzMask`): 2D `.tif` (`flat_extension`).
  Not OME-wrapped.
- **Projections**: 2D `.tif`. Not OME-wrapped.
- **Backgrounds**: `Background_*.tif` read for percentile, not rewritten.

## Configuration

`isoview.config.ProcessingConfig` — dataclass. Key fields:

- `input_dir`, `output_suffix` (one user-controlled suffix shared by
  `.corrected_*`, `.fused_*`, `.stitcher_*`).
- `specimens`, `timepoints`, `cameras` — auto-detected from filenames if
  unset.
- `camera_pairs` (default `[(0,1), (2,3)]`), `camera_view_map`
  (default `{0:0, 1:0, 2:90, 3:90}` — Keller IsoView geometry; override
  if your microscope maps cameras differently).
- `crop_*` dicts keyed by view index (0=VW00, 90=VW90).
- `tile_crops` — per-specimen crop overrides; **defined but not yet
  consumed in fusion**. TODO.
- `view_orientation` — per-specimen VW90→VW00 flip/rotation override.
  Used in `_fuse_camera_pair`.
- `segment_mode` (0=off, 1=generate+save masks).
- `apply_segmentation_mask` (default False; flip to True to match MATLAB
  behavior).
- `blending_method` — `adaptive`, `geometric`, `auto` (auto resolves to
  adaptive).
- `output_format` — `tif`, `zarr`, `klb`.

## `isoview_config.json`

Single file at dataset root tracking runs. Keys:

- `paths` — relative paths to raw / corrected.
- `microscope` — XML-derived pixel spacing, objective mag, camera_view_map,
  camera_pairs, wavelength, exposure.
- `corrections.<label>` — keyed by `corrected_suffix.lstrip(".")`. Stores
  `config_diff` (only fields differing from defaults) and `run` summary
  (start/end timestamps, elapsed, success/skipped/failed counts).
- `fusions.<correction_label>/<blending>` — keyed by `(correction_label,
  blending_method)`. **Known issue**: `fused_suffix` is not part of the
  key, so two fusion runs from the same correction with different
  `fused_suffix` collide. Fix planned.

Floats are rounded to 4 decimals on save.

## Known issues / TODO

- **`fused_suffix` key collision** in `IsoviewConfig.add_fusion` (config.py:553).
  Fix: include `fused_suffix` in the registry key.
- **`tile_crops` field defined but never consumed** (config.py:56,
  documented in pipeline/multi_fuse.py:88-98). `_fuse_camera_pair` only
  reads `config.get_crop(channel)` (view-level), not per-tile.
- **`_find_xml_for_stack` picks first matching XML** (io.py:485-500). For
  flat tiled dir with `ch00_spec00.xml` … `ch01_spec07.xml`, always
  returns spec00's. Benign on current data (W/H constant across specs;
  depth comes from filesize) but would silently mislead if any spec had
  different XY dimensions.
- **Heterogeneous Z depths silently accepted** in tiled mode. The 194nm
  beads `tiled_normal` has SPC00 at 224 z-planes and SPC01–07 at 11
  z-planes each. No warning emitted.
- **No global temporal mask workflow**. Would help reduce per-frame mask
  flicker on long timelapses of stable samples.
- **`apply_segmentation_mask` default** — currently False, MATLAB default
  is on. Consider flipping for consistency.

## References

- MATLAB source: `~/repos/IsoView-Processing/src/` (`clusterPT_RC.m`,
  `processTimepoint_RC.m`, `multiFuse.m`).
- Python source: `~/repos/isoview/isoview/` (`pipeline.py`, `fusion.py`,
  `corrections.py`, `segmentation.py`, `io.py`, `config.py`).
- MATLAB pipeline reference (this repo): [../notes/software/isoview.md](../notes/software/isoview.md).
