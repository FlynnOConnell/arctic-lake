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

- [caiman](caiman.md) - CNMF-based source extraction, NormCorre motion correction
- [suite2p](suite2p.md) - correlation-based ROI detection
- [suite3d](suite3d.md) - volumetric extension of suite2p
- [extract](extract.md) - robust regression segmentation
- [maskNMF](maskNMF.md) - PMD + NMF approach

## Concepts

- [gcamp_indicators](gcamp_indicators.md) - indicator dynamics and tau selection
- [rastermap](rastermap.md) - neural activity visualization

## Related

- [cellpose](cellpose.md) - deep learning cell segmentation
- [ome](ome.md) - OME-TIFF, OME-Zarr, BigDataViewer formats

for full package list see [software index](index.md)
