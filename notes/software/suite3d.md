---
title: Suite3D
tags: [calcium-imaging, suite3d, volumetric]
---

# Suite3D

[paper](https://www.biorxiv.org/content/10.1101/2025.03.26.645628v1) | [github](https://github.com/alihaydaroglu/suite3d) | Carandini Lab, UCL

volumetric cell detection for two-photon microscopy

---

## Overview

extends suite2p to 3D - same FFT-based registration algorithm

### Key Differences from Suite2p

- collects volumetric reference image, not plane-by-plane
- for inter-plane shifts, uses subset ~200-400 frames
- extends spatially tapered masks to 3D

### Benefits of Volumetric Registration

1. reduced noise
2. improved estimates of brain motion

![[Pasted image 20250918100132.png]]

---

## Core Processing Steps

### 1. 3D Motion Correction
- lateral and axial brain movements (XYZ)

### 2. 3D Cell Detection
- spatial/temporal filtering
- normalization
- thresholding

![[Pasted image 20250918100732.png]]

### 3. 3D Segmentation
- voxels assigned to distinct ROIs

---

## Crosstalk Removal

suite3d has built-in crosstalk removal:

- scan values of `m ∈ [0.01, 1.0]`
- compute negative log-likelihood per value
- choose `m` minimizing NLL

---

## Status

preliminary exploration - tuning in progress

---

## Links

- [[calcium-imaging]] - main index
- [[suite2p]] - 2D predecessor
