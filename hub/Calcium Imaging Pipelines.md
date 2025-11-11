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
## Rastermap

- `locality` controls global vs local structure balance
- Lower heatmap = earlier activity

## Crosstalk

### Suite3d removal strategy:
- Scan values of `m ∈ [0.01, 1.0]`
- Compute negative log-likelihood per value
- Choose `m` minimizing NLL

### Crosstalk types
1. **Excitation** – multiple fluorophores excited
2. **Emission** – overlapping output wavelengths

![[Pasted image 20250917181651.png|500]]  ![[Pasted image 20250917181722.png|500]]

Sources:
[Huygens]( [from Huygens](https://svi.nl/CrossTalk)
[EvidentScientific](https://evidentscientific.com/en/microscope-resource/knowledge-hub/techniques/confocal/bleedthrough)

---
## GCaMP[6,7,8] Indicators and Deconvolution Kernel Selection

The goal is to have the kernel **mirror the sensor’s dynamics** so that one spike’s fluorescence trace is correctly accounted for by the model.

Table 1. Indicator Dynamics and Recommended Kernel (Tau)

| **Indicator**          | **Rise t₁/₂** (ms) | **Decay t₁/₂** (ms)                        | **Single-AP SNR / ΔF**                             | **Recommended Kernel τ** (s)             |
| ---------------------- | ------------------ | ------------------------------------------ | -------------------------------------------------- | ---------------------------------------- |
| **GCaMP6f** (fast)     | ~50 ms             | ~140 ms (≈100 ms 1AP)                      | Low–moderate (smallest 6x ΔF; detects 1 AP)        | **0.7 s** (0.5–0.8)                      |
| **GCaMP6m** (medium)   | ~100 ms            | ~200 ms                                    | High (ΔF larger than 6f, ~2×; good 1 AP SNR)       | **1.0 s** (≈0.8–1.2)                     |
| **GCaMP6s** (slow)     | ~150–200 ms        | ~500 ms (up to 1800 ms for bursts)         | Very high (largest ΔF; ~2–3× 6f; best 6x SNR)      | **1.2–1.5 s** (often ~1.25)              |
| **jGCaMP7f** (fast)    | ~25 ms             | ~180–270 ms (single AP) (≈520 ms multi-AP) | Moderate (improved vs 6f, but lowest of 7x)        | **~1.0 s** (use slightly longer than 6f) |
| **jGCaMP7m** (interm.) | ~50 ms             | ~500–700 ms                                | High (midway 7f–7s; bright baseline, strong ΔF)    | **~1.2 s** (est., compromise value)      |
| **jGCaMP7s** (slow)    | ~100 ms+           | ~1690 ms (1.69 s)                          | Very high (largest 7x ΔF; ~2–3× 7f)                | **1.5–2.0 s** (match slow decay)         |
| **jGCaMP8f** (fast)    | ~7 ms              | ~67 ms                                     | Moderate–high (ΔF ~0.4; >7f, but lowest 8x)        | **~0.5 s** (0.3–0.6 s range)             |
| **jGCaMP8m** (medium)  | ~7 ms              | ~118 ms                                    | High (ΔF ~0.7; ≈7s sensitivity with fast kinetics) | **~0.7 s** (0.5–0.8 s range)             |
| **jGCaMP8s** (slow)    | ~10 ms             | ~307 ms (200–300 ms in vivo)               | Very high (ΔF ~1.1; highest of all; ~2× 7s d′)     | **~1.0 s** (0.8–1.2 s range)             |

### Frame Rate Considerations
- If the frame rate is high relative to the sensor’s speed, you’ll capture the true kinetics; τ can be set close to the known value. 
- If the frame rate is low, fast transients will be under-sampled – they may appear attenuated and stretched over multiple frames. 
- At low FPS, lean toward a slightly longer τ to avoid missing spikes

**Example**: jGCaMP8f has an actual half-decay (t½) ~0.07 s, but if you image at 5 Hz (200 ms frame interval), a single-frame spike could drop in one frame.

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

