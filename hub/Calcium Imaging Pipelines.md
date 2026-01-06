---
title: Calcium Imaging Pipelines
tags: [calcium-imaging, pipelines, overview]
category: summary
---
## Overview

| Pipeline        | 2D / 3D Registration | 2D / 3D Segmentation | Comments |
| --------------- | -------------------- | -------------------- | -------- |
| CaImAn (MATLAB) | Yes, Partial         | Yes, Partial         |          |
| CaImAn (Python) | Yes, Partial         | Yes, Partial         |          |
| Suite2p         | Yes, No              | Yes, No              |          |
| EXTRACT         | No, No               | Yes, No              |          |
| Suite3D         | Yes, Yes             | Yes, Yes             |          |

## CaImAn
[github](https://github.com/flatironinstitute/CaImAn)

1. Spatial downsampling
2. Frequency Filter / FFT
3. NormCorre Motion Correction
4. CNMFe
5. Extract dF/F
6. Event Detection, if necessary

### NormCorre: Matlab vs Python

| Feature/Property                                | Matlab                                                        | Python                                          |
| ----------------------------------------------- | ------------------------------------------------------------- | ----------------------------------------------- |
| online template updating                        | Yes                                                           | No                                              |
| available shifts                                | FFT, cubic linear                                             | FFT, cubic                                      |
| handles 3d data                                 | Yes                                                           | No                                              |
| optical flow calculation                        | No                                                            | Yes                                             |
| FFT windowing                                   | Yes                                                           | No                                              |
| parallelization method                          | for each mini batch process <br> different frames in parallel | process different <br> mini batches in parallel |
| variable for grid size                          | `grid_size`                                                   | `strides`                                       |
| overlap included in grid size                   | No                                                            | yes                                             |
| total size of each patch                        | `grid_size + 2×overlap`                                       | `strides + overlap`                             |
| option for phase correlation                    | Yes                                                           | ❌                                               |
| offset correction due to bidirectional scanning | ✅                                                             | ❌                                               |

### When to Use 3D vs 2D Registration

Use **3D registration** when:
- ROIs span across adjacent z-planes
- z-motion is comparable to inter-plane spacing

Use **2D registration per plane** when:
- z-motion is minimal or planes are far apart
- Forcing uniform x-y motion degrades results

---

## LBM-CaImAn-Python

### Quantitative Registration

Smoothness metric:
```python
np.gradient(np.mean(m, 0))  # Gradient of mean image
```

- Sum of squared gradients measures pixel-to-pixel variation

---

## Rastermap

- `locality` controls global vs local structure balance
- Lower heatmap = earlier activity

![[hub/literature/rastermap/notes|notes]]

## Cellpose

tag:: cellpose

[Marius Pachitariu](https://forum.image.sc/u/Marius_Pachitariu)

[May 9](https://forum.image.sc/t/cellpose4-cellpose-sam-tests/112080/20 "Post date")

One thing to point out is that the speed comparisons in the paper are done including the size model for Cellpose3, which approximately doubles runtimes, especially for small images. I know almost no one uses that, but we have to use it for papers every time to do fair comparisons to other methods without size models.

[@stefanhahmann](https://forum.image.sc/u/stefanhahmann) We have not yet explored run times thoroughly in 3D, but observed it being slower overall compared to 2D because the neural network is a larger fraction of compute in 3D (compared to post-processing, like running the flows or checking mask quality, etc). Your example seems a little worse than I would think, but we'll be investigating this over the next few weeks. The RTX 6000 Ada should be pretty good, doesn't get much better than that. We haven't yet enabled FP16 or FP8 inference, but we might do that as an option if there is a need for speed in 3D.

[@stefanhahmann](https://forum.image.sc/u/stefanhahmann) There are indeed no more individual models. A single set of weights works well across datasets (see paper), which was in fact already true in Cellpose3.

[@bnorthan](https://forum.image.sc/u/bnorthan) Is that image in the train or validation set? I manually eliminated 50% of the images in the train set (~500) which had bad annotations, but maybe I was still not conservative enough. We might scrap that dataset altogether, since the good parts are very similar to data available elsewhere anyway (like Tissuenet).

[@bnorthan](https://forum.image.sc/u/bnorthan) The pixelation at diameter 120 is due to running the flows on the downsampled image (nothing to do with Cellpose-SAM) and we will revert this soon.

---

## Crosstalk

### Suite3d removal strategy:
- Scan values of `m ∈ [0.01, 1.0]`
- Compute negative log-likelihood per value
- Choose `m` minimizing NLL

### Crosstalk types
1. **Spectral**
2. **Excitation** – multiple fluorophores excited
3. **Emission** – overlapping output wavelengths

![[Pasted image 20250917181651.png|500]]  ![[Pasted image 20250917181722.png|500]]

Sources:
[Huygens](https://svi.nl/CrossTalk)
[EvidentScientific](https://evidentscientific.com/en/microscope-resource/knowledge-hub/techniques/confocal/bleedthrough)

_Check for chromatic aberration?_

---

## Suite2p Helpful Issues

- [Issue #921](https://github.com/MouseLand/suite2p/issues/921): Black background affects registration; tweak `block_size` / `spatial_taper`
- [Issue #880](https://github.com/MouseLand/suite2p/issues/880): Running on cluster
- [Issue #851](https://github.com/MouseLand/suite2p/issues/851): Overlapping ROIs and `ops['max_overlap']`
- [Issue #837](https://github.com/MouseLand/suite2p/issues/837): `tau` controls temporal binning
- [YouTube: ROI detection explainer](https://youtu.be/NcC0YxQ9o3A)
- [Issue #787](https://github.com/MouseLand/suite2p/issues/787): `threshold_scaling` for dim signals
- [Issue #690](https://github.com/MouseLand/suite2p/issues/690): Multi-channel registration
- [Issue #627](https://github.com/MouseLand/suite2p/issues/627): F and Fneu meaning
- [Issue #758](https://github.com/MouseLand/suite2p/issues/758#issuecomment-956588935): Looping over DBs on cluster
- [Issue #795](https://github.com/MouseLand/suite2p/issues/795): zarr vs NWB
- [Issue #750](https://github.com/MouseLand/suite2p/issues/750): GCaMP8f, `tau=0.1` for fast data
- [Issue #730](https://github.com/MouseLand/suite2p/issues/730): Max image brightness vs `tau`
- [Issue #667](https://github.com/MouseLand/suite2p/issues/667): 4D TIFFs, `sparse_mode` toggle
- [Issue #530](https://github.com/MouseLand/suite2p/issues/530): Units of `F` and `spks`

---

## 3D Segmentation

[PNAS: Spatiotemporal UNet paper ›](https://www.pnas.org/doi/10.1073/pnas.1812995116)

- 3D UNet, outperforming CNMF/Suite2p
- Temporal max pooling, 120-frame batches
- CNMF background = low-rank model → can fail with dynamic background
- 3rd grader trained to segment neurons (lol)
- Demo notebook (Flatiron):
  [demo_caiman_cnmf_3D.ipynb](https://github.com/flatironinstitute/CaImAn/blob/CNMF_3D/demos/notebooks/demo_caiman_cnmf_3D.ipynb)

Notes from Johannes:
- Branch in CaImAn repo with unmerged 3D motion correction
- Anisotropy = common, affects `gSig`, `strides`, `overlap`
- Watch out for memory overload due to `A` matrix size if too many neurons / low FPS

---

## EXTRACT-public

- Basic preprocessing (median filter, regression)
- mk301 plane 7: 300+ cells in 3 min
- SNR plot helpful but no trace ↔ ROI linking
- No pausing / labeling cells interactively
- No 3D support or modular save utilities
- No least-squares filtering for spatial components
- Undocumented features like `plot_stacked_traces_double`

---

## GCaMP[6,7,8] Indicators and Deconvolution Kernel Selection

The goal is to have the kernel **mirror the sensor's dynamics** so that one spike's fluorescence trace is correctly accounted for by the model.

Table 1. Indicator Dynamics and Recommended Kernel (Tau)

| **Indicator**          | **Rise t₁/₂** (ms) | **Decay t₁/₂** (ms)                        | **Single-AP SNR / ΔF**                             | **Recommended Kernel τ** (s)             |
| ---------------------- | ------------------ | ------------------------------------------ | -------------------------------------------------- | ---------------------------------------- |
| **GCaMP6f** (fast)     | ~50 ms             | ~140 ms (≈100 ms 1AP)                      | Low–moderate (smallest 6x ΔF; detects 1 AP)        | **0.7 s** (0.5–0.8)                      |
| **GCaMP6m** (medium)   | ~100 ms            | ~200 ms                                    | High (ΔF larger than 6f, ~2×; good 1 AP SNR)       | **1.0 s** (≈0.8–1.2)                     |
| **GCaMP6s** (slow)     | ~150–200 ms        | ~500 ms (up to 1800 ms for bursts)         | Very high (largest ΔF; ~2–3× 6f; best 6x SNR)      | **1.2–1.5 s** (often ~1.25)              |
| **jGCaMP7f** (fast)    | ~25 ms             | ~180–270 ms (single AP) (≈520 ms multi-AP) | Moderate (improved vs 6f, but lowest of 7x)        | **~1.0 s** (use slightly longer than 6f) |
| **jGCaMP7m** (interm.) | ~50 ms             | ~500–700 ms                                | High (midway 7f–7s; bright baseline, strong ΔF)    | **~1.2 s** (est., compromise value)      |
| **jGCaMP7s** (slow)    | ~100 ms+           | ~1690 ms (1.69 s)                          | Very high (largest 7x ΔF; ~2–3× 7f)                | **1.5–2.0 s** (match slow decay)         |
| **jGCaMP8f** (fast)    | ~7 ms              | ~67 ms                                     | Moderate–high (ΔF ~0.4; >7f, but lowest 8x)        | **~0.5 s** (0.3–0.6 s range)             |
| **jGCaMP8m** (medium)  | ~7 ms              | ~118 ms                                    | High (ΔF ~0.7; ≈7s sensitivity with fast kinetics) | **~0.7 s** (0.5–0.8 s range)             |
| **jGCaMP8s** (slow)    | ~10 ms             | ~307 ms (200–300 ms in vivo)               | Very high (ΔF ~1.1; highest of all; ~2× 7s d′)     | **~1.0 s** (0.8–1.2 s range)             |

### Frame Rate Considerations
- If the frame rate is high relative to the sensor's speed, you'll capture the true kinetics; τ can be set close to the known value.
- If the frame rate is low, fast transients will be under-sampled – they may appear attenuated and stretched over multiple frames.
- At low FPS, lean toward a slightly longer τ to avoid missing spikes

**Example**: jGCaMP8f has an actual half-decay (t½) ~0.07 s, but if you image at 5 Hz (200 ms frame interval), a single-frame spike could drop in one frame.

1. CaImAn [parameters](https://caiman.readthedocs.io/en/latest/Getting_Started.html#parameters)
	1. `decay_time`: Length of typical transient in **seconds**.
	2. Default is `0.4`, appropriate for fast sensors (GCaMP6f)
	3. Slow sensors may use 1 or more.
2. Suite2p [parameters](https://suite2p.readthedocs.io/en/latest/settings.html#main-settings)
		1. `tau`: Fixed, not scaled with frame-rate
		2. 0.7 for GCaMP6f
		3. 1.0 for GCaMP6m
		4. 1.25-1.5 for GCaMP6s

Sources
1. [Spike inference from calcium imaging data acquired with GCaMP8 indicators](https://www.biorxiv.org/content/10.1101/2025.03.03.641129v2.full#F8)
2. [Janelia Calcium Indicators](https://www.janelia.org/jgcamp8-calcium-indicators#:~:text=Max%20dF%2FF%20Half,0.66%C2%B10.18%2010.9%C2%B11.24%2041.6%C2%B18.1%2094.8%C2%B113.3)

## DF/F

---

## Calcium Imaging and Related Resources

### Active Packages

| Package | Lab | Repository | Status |
|--------|-----|------------|--------|
| CaImAn | Flatiron | [github.com/flatironinstitute/CaImAn](https://github.com/flatironinstitute/CaImAn) | Explored – done; maintained but inactive |
| Suite2p | Stringer Lab, Janelia | [github.com/MouseLand/suite2p](https://github.com/MouseLand/suite2p) | Explored – actively developed |
| VR2P | Spruston Lab, Janelia | [vr2p-public](https://github.com/sprustonlab/vr2p-public), [OSM Paper Figures](https://github.com/sprustonlab/OSM_Paper_Figures/tree/main) | Explored – basic suite2p wrapper |
| rastermap | Stringer Lab, Janelia | [github.com/MouseLand/rastermap](https://github.com/MouseLand/rastermap/tree/main/notebooks) | Integrated into LBM-Suite2p-Python |
| OPhysLib | Tolias Lab, Stanford | [github.com/atlab/OPhysLib](https://github.com/atlab/OPhysLib) | Waiting on developer progress |
| MOSAIC-PICASSO | Tolias, Xing, NICA Labs | [atlab](https://github.com/atlab/mosaic-picasso), [xing-lab-pitt](https://github.com/xing-lab-pitt/mosaic-picasso), [NICA](https://github.com/NICALab/PICASSO) | Paused |
| Suite3D | Carandini Lab, UCL | [github.com/alihaydaroglu/suite3d](https://github.com/alihaydaroglu/suite3d) | Preliminary exploration – tuning in progress |
| EXTRACT | Schnitzer Lab, Stanford | [github.com/schnitzer-lab/EXTRACT-public](https://github.com/schnitzer-lab/EXTRACT-public) | Successfully ran – continue development |
| ActSort | Schnitzer Lab, Stanford | [github.com/schnitzer-lab/ActSort-public](https://github.com/schnitzer-lab/ActSort-public) | Good results – continue development |
| SUPPORT | NICA Lab, KAIST | [github.com/NICALab/SUPPORT](https://github.com/NICALab/SUPPORT) | Unexplored |
| deepinterpolation | Allen Institute | [github.com/AllenInstitute/deepinterpolation](https://github.com/AllenInstitute/deepinterpolation) | Integration pending at user request |
| CalciSeg | Yannick (Konstanz/RU 2025) | [github.com/YannickGuenzel/CalciSeg](https://github.com/YannickGuenzel/CalciSeg) | Unexplored |
| NeuroSeg-III | Liao Lab, Chongqing Univ. | [github.com/zimo-k/NeuroSeg3](https://github.com/zimo-k/NeuroSeg3) | Unexplored |
| SUNS | Gong Lab, Duke | [github.com/YijunBao/Shallow-UNet-Neuron-Segmentation_SUNS](https://github.com/YijunBao/Shallow-UNet-Neuron-Segmentation_SUNS) | Unexplored |
| AUTOTUNE | Spencer Smith Lab, UCSB | [github.com/yuyiyi/AUTOTUNE-for-Dendritic-imaging](https://github.com/yuyiyi/AUTOTUNE-for-Dendritic-imaging) | Difficult setup – mostly unexplored |
| CellReg | Ziv Lab, UCLA | [github.com/zivlab/CellReg](https://github.com/zivlab/CellReg/tree/master) | Planned for future |
| CASCADE | Helmchen/Friedrich Labs | [github.com/HelmchenLabSoftware/Cascade](https://github.com/HelmchenLabSoftware/Cascade?tab=readme-ov-file) | Planned for future |
| CIATAH | Bahanonu | [ciatah site](https://bahanonu.github.io/ciatah/) | Unexplored |
| FISSA | Rochefort Lab | [github.com/rochefort-lab/fissa](https://github.com/rochefort-lab/fissa) | Dormant but interesting |

---

## Dormant or Problematic

| Package | Lab | Repository | Notes |
|--------|-----|------------|-------|
| STNeuroNet | Farsiu Lab, Duke | [github.com/soltanianzadeh/STNeuroNet](https://github.com/soltanianzadeh/STNeuroNet) | No commits in 6 years – revisit if cited |
| FIOLA | Giovannucci, UNC | [github.com/nel-lab/FIOLA](https://github.com/nel-lab/FIOLA/tree/master) | Ditched – developer doubts effectiveness |
| CITE-ON | Fellin, IIT | [gitlab.iit.it/fellin-public/cite-on](https://gitlab.iit.it/fellin-public/cite-on) | Buggy – TensorFlow issues on Windows |

## General

Created: `= this.file.ctime`
Last Updated: `= this.file.mtime`
