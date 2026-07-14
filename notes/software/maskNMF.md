---
title: MaskNMF
tags: [calcium-imaging, masknmf, denoising]
---

# MaskNMF

end-to-end system for functional imaging data analysis

---

## Overview

enhanced performance and interpretability over Suite2p, CaImAn, EXTRACT

### Key Features

1. **Motion Correction** - rigid and piecewise nonrigid, subpixel scan-phase correction (planned)
2. **Denoising + Compression** - boosts SNR, reveals dim signals otherwise undetectable
3. **Demixing** - separates true neural signal from background contamination
4. **Visualization** - GPU-accelerated via fastplotlib, all intermediates viewable
5. **Speed** - fast processing with optional GPU acceleration

---

## Comparison to Existing Tools

| Feature | MaskNMF | Suite2p | CaImAn | EXTRACT |
|---------|---------|---------|--------|---------|
| subpixel motion correction | planned | no | no | no |
| denoising before demixing | yes | no | no | no |
| interactive intermediate viz | yes | no | no | no |
| GPU-native processing | yes | partial | no | no |

---

## Current Status for LBM

~80% complete toward user-friendly pipeline

- inputs: `Txy` timeseries (compatible with mbo_utilities)
- easy visualization of intermediates using fastplotlib
- excellent demixing results when motion is stable

### Missing Features

- manual curation UI (accept/reject cells)
- signal quality thresholds (e.g., adjustable SNR slider)
- documentation

---

## LBM Use Cases

- evaluate minimum imaging resolution where demixing remains feasible
- automatically detect and visualize data problems:
  - scan-phase artifacts
  - residual motion
- inform data acquisition strategies
- long-term goal: package as real-time microscope module

---

## Data Quality Notes

### PMD (Penalized Matrix Decomposition)

- essentially run SVD in blocks, where each block has only local background to deal with
- after PMD + mean subtraction, artifacts become visible that are hidden in raw data:
  - line artifacts
  - scan-phase-induced "wobble" in active cells
- consequences: ROI-based signal extraction will be contaminated, undetected in traditional pipelines

### Current Issue

neuronal jitter visible in mean-subtracted timeseries - registration with suite2p didn't help

---

## Philosophy

- fastplotlib is core to visual transparency: helps users identify problems early
- emphasis on modular design: each step can be debugged and tuned independently
- goal is not just automation, but interpretable analysis

---

## Links

- [calcium-imaging](../tags/calcium-imaging.md) - main index
- [suite2p](suite2p.md) - alternative pipeline
- [caiman](caiman.md) - alternative pipeline
