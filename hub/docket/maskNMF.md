---
tags:
  - "#pipelines"
  - image-processing
  - calcium-imaging
updated_date: <% tp.date.now("YYYY-MM-DD") %>
---
# maskNMF
- Registration with Suite2p did not help
- pmd: Penalized Matrix Decomposition
	- Essentially run SVD in blocks, where each block has only the local background to deal with

## MaskNMF Overview

**MaskNMF** is an end-to-end system for functional imaging data analysis, offering enhanced performance and interpretability over traditional pipelines such as Suite2p, CaImAn, and EXTRACT.

### Key Features

1. **Motion Correction**
   - Rigid and piecewise nonrigid correction
   - Includes subpixel scan-phase correction (to be implemented)

2. **Denoising + Compression**
   - Boosts SNR and reveals dim signals otherwise undetectable
   - Essential step that mainstream pipelines lack

3. **Demixing**
   - Separates true neural signal from background contamination and noise
   - Enhanced by high-quality preprocessing

4. **Visualization**
   - GPU-accelerated (via **fastplotlib**)
   - Enables visualization of all intermediates (e.g. mean-subtracted frames)
   - Data never leaves the GPU; CPU mode available if CUDA is not present

5. **Speed**
   - Fast processing with optional GPU acceleration

---

## Comparison to Existing Tools

| Feature                  | MaskNMF | Suite2p | CaImAn | EXTRACT |
|--------------------------|---------|---------|--------|---------|
| Subpixel motion correction | ✔ (planned) | ✘       | ✘      | ✘       |
| Denoising before demixing | ✔       | ✘       | ✘      | ✘       |
| Interactive intermediate visualizations | ✔ | ✘       | ✘      | ✘       |
| GPU-native processing     | ✔       | Partial | ✘      | ✘       |

---

## Current Status for LBM Datasets

- **~80% complete** toward a user-friendly pipeline
- Inputs: `Txy` time series (compatible with `mbo_utilities`)
- Easy visualization of intermediate stages using `fastplotlib`
- Excellent demixing results when motion is stable

### Missing Features
- Manual curation UI (accept/reject cells)
- Signal quality thresholds (e.g., adjustable SNR slider)
- Documentation

---

## LBM Use Cases and Benefits

- Evaluate **minimum imaging resolution** at which demixing remains feasible
- Automatically detect and visualize data problems:
  - Scan-phase artifacts
  - Residual motion
- Inform **data acquisition strategies**
- Long-term goal: package MaskNMF as a **real-time microscope module**

---

## Data Quality Observations

### Demixing Video 1
- Shows successful demixing under stable motion

### Demixing Video 2
- Highlights artifacts such as:
  - Line artifacts
  - Scan-phase-induced "wobble" in active cells
- These are only visible after **PMD + mean subtraction**, not in raw data
- Consequences:
  - ROI-based signal extraction will be contaminated
  - Undetected by users in traditional pipelines

---

## Task Tracker

| Task                                                 | Assignee | ETA             |
| ---------------------------------------------------- | -------- | --------------- |
| Build a volumetric demixing UI (T over Z-planes)     | —        | —               |
| Fix 2 bugs reported by Flynn (issues open on GitHub) | Amol     | Week of June 16 |
| Add NN denoiser on top of PMD for Light Beads        | Amol     | Week of June 16 |
| Provide IBL demixing results for Raghav              | Amol     | Week of June 16 |
| Fix signal space demixing widget                     | Amol     | Week of June 16 |

---

## Notes

- Fastplotlib is core to visual transparency: helps users identify problems early
- Emphasis on modular design: each step can be debugged and tuned independently
- Goal is not just automation, but **interpretable analysis**
