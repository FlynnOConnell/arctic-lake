# IsoView Python port: status and processing parity

A narrow Python port of the IsoView per-timepoint correction (`clusterPT` /
`processTimepoint_RC`) and multi-view fusion (`clusterMF` / `multiFuse`).
Two stages, one entry point each: `correct_stack(config)` and
`multi_fuse(config)`. Same OME-conformant output for TIFF and Zarr.

## What's the same as MATLAB

Image-processing math is preserved end-to-end:

| Step | Algorithm |
|------|-----------|
| Dead-pixel detection | std-projection + mean-projection, knee-detection threshold (max distance from line), median-filter replacement. Identical to `correctInsensitivePixels`. |
| Knee threshold | Subsample-at-50k, distance-from-line. Identical to `determineThreshold`. |
| Anisotropic Gaussian | Separable 3D, kernels `[k, k, max(1, k/scaling)]`. Identical to `imgaussianAnisotropy`. |
| Slab smoothing | `margin = 2 * kernelSize`, crop-interior reassembly. Same scheme. |
| Adaptive threshold | `level = minI + (meanI - minI) * threshold`, mean over voxels above `minI`. Identical. |
| Background value | `prctile(stack[>0], 5)` from subsampled volume. Same. |
| Coordinate masks (xz, xy) | NaN-mean of coordinate volume where mask==0, slab-batched. Same construction. |
| Mask storage | uint16 0/1. Same. |

The Python and MATLAB pipelines should produce numerically very close
corrected stacks, masks, and coordinate masks for the same input.

## What's intentionally different or omitted

| Feature | MATLAB | Python | Why |
|---------|--------|--------|-----|
| References / dependents (channel groups share masks) | Yes (`references=[0;1]`, `dependents=[2;3]`) | No | Not used for our single-color experiments. |
| Cross-channel mask OR-fusion | Yes (single-row `references`) | No | Same — multi-channel feature. |
| 3-pass global temporal mask (`segmentFlag=2 → union → 3`) | Yes | No | Skipped; per-TM masks only. Worth revisiting for stable-sample timelapses. |
| Crop-on-read during correction | Yes (`multibandread` slicing) | No | Python loads full stack; crops applied in fusion. More memory but more flexible. |
| `apply_segmentation_mask` default | On | Off | Python writes unmasked corrected stacks by default; mask is saved separately. Toggle via config. |
| Multi-channel per camera | Yes (nested `for c, for h`) | No | Our hardware: one channel per camera (`camera_view_map`). |
| Correction diagnostics save | Optional | No | Stats stay in memory. |
| Rotation in correction | Yes | Deferred to fusion | Correction writes raw-orientation data; fusion applies rotation/flips. |

## Scope of the Python pipeline today

- **Correction** (`isoview.correct_stack`): dead-pixel, segmentation, mask save, optional mask application, coordinate masks, projections. Per-camera, per-timepoint or per-specimen (tiled mode auto-detected from `SPC##` / `TM######` counts).
- **Fusion** (`isoview.multi_fuse`): per-pair camera registration (X/Y + rotation), intensity correction, adaptive/geometric blending, per-tile `view_orientation` override for VW90→VW00 alignment.
- **Modes**: timelapse (`SPM##/TM######/`) and tiled (`SPM##/`, flat per-tile). Auto-detected.
- **Output**: OME-TIFF (`.ome.tif`) or OME-Zarr (`.ome.zarr`) with multiscales pyramids; per-specimen `projections/` subdir for QC.

## Verification

- Side-by-side correction on the 194nm beads dataset produces matching dead-pixel maps and segmentation masks to within expected boundary differences (`medfilt2` per-Z vs `scipy.ndimage.median_filter` over volume).
- Fusion blending crossover and adaptive-mask logic match the MATLAB `geometric` and `adaptive` paths (validated on overlap-mode masks; union-mode edge-artifact bug fixed in the Python `_fuse_camera_pair`).
- Tiled multi-specimen handling exists end-to-end; the demo dataset (8 SPCs in one flat dir, heterogeneous Z depths) processes without errors.

## Not implemented (downstream of fusion)

`localAP`, `clusterTF`, `clusterFR`, `localCP`, `localEC`, `clusterCS`,
`clusterRS`, `localCR`, `clusterCD`, `clusterIS` — temporal fusion, drift
correction, dF/F, isotropic interpolation. Out of scope for the current
port.
