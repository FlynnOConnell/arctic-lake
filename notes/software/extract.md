---
tags:
  - extract
  - calcium-imaging
  - segmentation
  - matlab
category: software
created: 2025-09-17
---

# EXTRACT

[github](https://github.com/schnitzer-lab/EXTRACT-public) | Schnitzer Lab, Stanford

robust regression-based cell extraction for calcium imaging

---

## Overview

- basic preprocessing (median filter, regression)
- mk301 plane 7: 300+ cells in 3 min
- SNR plot helpful but no trace ↔ ROI linking
- no pausing / labeling cells interactively
- no 3D support or modular save utilities
- undocumented features like `plot_stacked_traces_double`

---

## Why Robust Regression?

**problem with naive averaging**: if two cells overlap, averaging activity inside cells causes the inactive cell to show activity from the active one

![Pasted image 20250917165439.png](../images/Pasted%20image%2020250917165439.png)

**least-squares regression** fixes this - what CaImAn and Suite2p use

![Pasted image 20250917165736.png](../images/Pasted%20image%2020250917165736.png)

**robust regression** goes further - handles outliers better

![Pasted image 20250917165904.png](../images/Pasted%20image%2020250917165904.png)

results superior to CNMF in their benchmarks:

![Pasted image 20250917170033.png](../images/Pasted%20image%2020250917170033.png)

---

## ActSort

companion tool for active learning-based cell sorting

![Pasted image 20250917170303.png](../images/Pasted%20image%2020250917170303.png)

- pick a cell, computer suggests which cells to review next
- achieves good results by sorting ~1% of the dataset
- generalizes to rest of dataset

---

## Pipeline Demo

### Installation

1. install [mbo_utilities](https://millerbrainobservatory.github.io/mbo_utilities/install.html)
2. install [EXTRACT-public](https://github.com/MillerBrainObservatory/EXTRACT-public?tab=readme-ov-file#installation)

### Data Preparation

EXTRACT takes planar timeseries in `.h5` format as input

organize data so each z-plane is saved separately:
```
D:/tests/data/EXTRACT/
├── plane1.h5
├── plane2.h5
├── ...
```

using mbo_utilities to convert from tiffs:
```python
import mbo_utilities as mbo

volume = mbo.imread(r"path/to/raw_tiffs")
# volume.shape = (5632, 14, 448, 448)

# option 1: stitch ROIs before saving
mbo.imwrite(volume, "D://extract_demo//stitched_rois", planes=[4, 7, 11, 14], ext="h5")

# option 2: save individual ROIs
volume.roi = 2
mbo.imwrite(volume, "D://extract_demo", planes=[4, 7, 11, 14], ext="h5")
```

### Run EXTRACT

```matlab
% set path to data folder
data_path = "D://extract_demo//";
runEXTRACT(data_path);
```

runs each `*plane*.h5` (skips files with `output` in filename)

note: overwrites data in root directory each run

### `runEXTRACT.m` API

```matlab
runEXTRACT(rootDir)
runEXTRACT(rootDir, savePlots, cfg)
```

| Argument | Type | Description |
|----------|------|-------------|
| `rootDir` | string | root directory containing `plane*.h5` files |
| `savePlots` | logical | save PNG cell mask images (default: true) |
| `cfg` | struct | partial EXTRACT config, only valid fields applied |

each `plane*.h5` must contain dataset at path `//mov` shaped `(Y, X, T)`

### Key Config Values

| Parameter | Description |
|-----------|-------------|
| `thresholds.T_min_snr` | increase to suppress noise (e.g., 3.5 → 5.0) |
| `cellfind_min_snr` | lower to pick up more low-SNR cells |
| `use_gpu` | set to 0 to disable GPU |
| `adaptive_kappa` | enables dynamic thresholding in spatial extraction |

### Outputs

for each `plane*.h5`:
- `outputs/planeN_outputs.h5` - extracted data
- `outputs/planeN_masks.png` - cell masks (if savePlots=true)

note: output plot during cellfinding uses red-to-gray colormap (bright values are red)

### Examples

```matlab
% defaults
runEXTRACT('/data/session1')

% no plotting
runEXTRACT('/data/session1', false)

% custom config
cfg = struct();
cfg.cellfind_min_snr = 1.5;
cfg.thresholds = struct();
cfg.thresholds.T_min_snr = 4.0;
cfg.use_gpu = 0;
runEXTRACT('/data/session1', true, cfg)
```

---

## Limitations

- no least-squares filtering for spatial components
- no 3D support
- no modular save utilities

---

## Links

- [calcium-imaging](../tags/calcium-imaging.md) - main index
- [caiman](caiman.md) - alternative with CNMF
- [suite2p](suite2p.md) - alternative pipeline
