---
title: Calcium Imaging
tags: [calcium-imaging, pipelines, overview]
category: index
---

# Calcium Imaging

index for calcium imaging analysis tools and concepts

## Pipeline Comparison

| Pipeline   | Registration | Segmentation | 3D Support | Status |
|------------|--------------|--------------|------------|--------|
| CaImAn     | rigid + pw-rigid | CNMF/CNMFe | partial | maintained, inactive |
| Suite2p    | rigid + nonrigid | correlation-based | no | actively developed |
| Suite3D    | volumetric | 3D detection | yes | early stage |
| EXTRACT    | none | robust regression | no | usable |
| MaskNMF    | rigid + pw-nonrigid | PMD + NMF | planned | ~80% complete |

## Analysis Pipelines

- [[caiman]] - CNMF-based source extraction, NormCorre motion correction
- [[suite2p]] - correlation-based ROI detection
- [[suite3d]] - volumetric extension of suite2p
- [[extract]] - robust regression segmentation
- [[maskNMF]] - PMD + NMF approach

## Concepts

- [[gcamp_indicators]] - indicator dynamics and tau selection
- [[rastermap]] - neural activity visualization

## Related

- [[cellpose]] - deep learning cell segmentation
- [[isoview]] - light-sheet multi-view fusion
- [[file-formats]] - OME-Zarr, BigDataViewer formats

for full package list see [[index|software index]]
