---
title: Calcium Imaging
tags: [calcium-imaging, pipelines, overview]
category: index
---

# Calcium Imaging

main index for calcium imaging analysis tools and concepts

## Pipeline Comparison

| Pipeline   | Registration | Segmentation | 3D Support | Status |
|------------|--------------|--------------|------------|--------|
| CaImAn     | rigid + pw-rigid | CNMF/CNMFe | partial | maintained, inactive |
| Suite2p    | rigid + nonrigid | correlation-based | no | actively developed |
| Suite3D    | volumetric | 3D detection | yes | early stage |
| EXTRACT    | none | robust regression | no | usable |
| MaskNMF    | rigid + pw-nonrigid | PMD + NMF | planned | ~80% complete |

see individual notes: [[caiman]], [[suite2p]], [[suite3d]], [[extract]], [[masknmf]]

---

## When to Use 3D vs 2D Registration

**3D registration** when:
- ROIs span across adjacent z-planes
- z-motion is comparable to inter-plane spacing

**2D registration per plane** when:
- z-motion is minimal or planes are far apart
- forcing uniform x-y motion degrades results

---

## GCaMP Indicators and Deconvolution Kernels

the goal is to have the kernel mirror the sensor's dynamics so that one spike's fluorescence trace is correctly accounted for by the model

| Indicator | Rise t½ (ms) | Decay t½ (ms) | Recommended τ (s) |
|-----------|--------------|---------------|-------------------|
| GCaMP6f   | ~50          | ~140          | 0.7 (0.5-0.8)     |
| GCaMP6m   | ~100         | ~200          | 1.0 (0.8-1.2)     |
| GCaMP6s   | ~150-200     | ~500          | 1.2-1.5           |
| jGCaMP7f  | ~25          | ~180-270      | ~1.0              |
| jGCaMP7s  | ~100+        | ~1690         | 1.5-2.0           |
| jGCaMP8f  | ~7           | ~67           | ~0.5 (0.3-0.6)    |
| jGCaMP8m  | ~7           | ~118          | ~0.7 (0.5-0.8)    |
| jGCaMP8s  | ~10          | ~307          | ~1.0 (0.8-1.2)    |

### Frame Rate Considerations

- high fps relative to sensor speed: τ can be set close to known value
- low fps: fast transients under-sampled, appear stretched
- at low fps, lean toward slightly longer τ to avoid missing spikes

**Example**: jGCaMP8f has t½ ~0.07s, but at 5Hz (200ms frame interval), a spike could drop in one frame

### Pipeline Parameters

| Parameter | CaImAn | Suite2p |
|-----------|--------|---------|
| name | `decay_time` | `tau` |
| default | 0.4 | - |
| GCaMP6f | 0.4 | 0.7 |
| GCaMP6m | - | 1.0 |
| GCaMP6s | 1.0+ | 1.25-1.5 |

sources:
- [Spike inference from GCaMP8](https://www.biorxiv.org/content/10.1101/2025.03.03.641129v2.full)
- [Janelia jGCaMP8](https://www.janelia.org/jgcamp8-calcium-indicators)

---

## Crosstalk

### Types
1. **Spectral** - overlapping excitation/emission spectra
2. **Excitation** - multiple fluorophores excited by same wavelength
3. **Emission** - overlapping output wavelengths

### Suite3D Removal Strategy
- scan values of `m ∈ [0.01, 1.0]`
- compute negative log-likelihood per value
- choose `m` minimizing NLL

sources: [Huygens](https://svi.nl/CrossTalk), [EvidentScientific](https://evidentscientific.com/en/microscope-resource/knowledge-hub/techniques/confocal/bleedthrough)

---

## Active Packages

| Package | Lab | Status |
|---------|-----|--------|
| [CaImAn](https://github.com/flatironinstitute/CaImAn) | Flatiron | explored - maintained but inactive |
| [Suite2p](https://github.com/MouseLand/suite2p) | Stringer/Janelia | explored - actively developed |
| [Suite3D](https://github.com/alihaydaroglu/suite3d) | Carandini/UCL | preliminary exploration |
| [EXTRACT](https://github.com/schnitzer-lab/EXTRACT-public) | Schnitzer/Stanford | successfully ran |
| [ActSort](https://github.com/schnitzer-lab/ActSort-public) | Schnitzer/Stanford | good results |
| [rastermap](https://github.com/MouseLand/rastermap) | Stringer/Janelia | integrated into LBM-Suite2p-Python |
| [VR2P](https://github.com/sprustonlab/vr2p-public) | Spruston/Janelia | basic suite2p wrapper |
| [OPhysLib](https://github.com/atlab/OPhysLib) | Tolias/Stanford | waiting on developer |
| [MOSAIC-PICASSO](https://github.com/atlab/mosaic-picasso) | Tolias/Xing/NICA | paused |
| [SUPPORT](https://github.com/NICALab/SUPPORT) | NICA/KAIST | unexplored |
| [deepinterpolation](https://github.com/AllenInstitute/deepinterpolation) | Allen Institute | integration pending |
| [CalciSeg](https://github.com/YannickGuenzel/CalciSeg) | Konstanz/RU | unexplored |
| [NeuroSeg-III](https://github.com/zimo-k/NeuroSeg3) | Liao/Chongqing | unexplored |
| [SUNS](https://github.com/YijunBao/Shallow-UNet-Neuron-Segmentation_SUNS) | Gong/Duke | unexplored |
| [CellReg](https://github.com/zivlab/CellReg) | Ziv/UCLA | planned |
| [CASCADE](https://github.com/HelmchenLabSoftware/Cascade) | Helmchen/Friedrich | planned |
| [CIATAH](https://bahanonu.github.io/ciatah/) | Bahanonu | unexplored |
| [FISSA](https://github.com/rochefort-lab/fissa) | Rochefort | dormant but interesting |

### Dormant/Problematic

| Package | Notes |
|---------|-------|
| [STNeuroNet](https://github.com/soltanianzadeh/STNeuroNet) | no commits in 6 years |
| [FIOLA](https://github.com/nel-lab/FIOLA) | developer doubts effectiveness |
| [CITE-ON](https://gitlab.iit.it/fellin-public/cite-on) | buggy TensorFlow issues |
| [AUTOTUNE](https://github.com/yuyiyi/AUTOTUNE-for-Dendritic-imaging) | difficult setup |

---

## 3D Segmentation

[PNAS: Spatiotemporal UNet](https://www.pnas.org/doi/10.1073/pnas.1812995116)

- 3D UNet outperforming CNMF/Suite2p
- temporal max pooling, 120-frame batches
- CNMF background = low-rank model → can fail with dynamic background

notes from Johannes:
- branch in CaImAn repo with unmerged 3D motion correction
- anisotropy = common, affects `gSig`, `strides`, `overlap`
- watch out for memory overload due to `A` matrix size if too many neurons / low FPS

demo: [demo_caiman_cnmf_3D.ipynb](https://github.com/flatironinstitute/CaImAn/blob/CNMF_3D/demos/notebooks/demo_caiman_cnmf_3D.ipynb)

---

## Rastermap

- `locality` controls global vs local structure balance
- lower heatmap = earlier activity

---

## Related Tools

- [[cellpose]] - deep learning cell segmentation
- [[isoview]] - light-sheet multi-view fusion
- [[file-formats]] - OME-Zarr, BigDataViewer formats
