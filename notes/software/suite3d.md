---
tags:
  - suite3d
  - suite2p
  - calcium-imaging
  - segmentation
  - two-photon
category: software
created: 2025-09-18
---

# Suite3D

[paper](https://www.biorxiv.org/content/10.1101/2025.03.26.645628v1) | [github](https://github.com/alihaydaroglu/suite3d) | Carandini Lab, UCL

volumetric cell detection for two-photon microscopy

---

## Overview

extends Suite2p to 3D - same FFT-based registration algorithm

### Key Differences from Suite2p

- collects volumetric reference image, not plane-by-plane
- for inter-plane shifts, uses subset ~200-400 frames
- extends spatially tapered masks to 3D

### Benefits of Volumetric Registration

1. reduced noise
2. improved estimates of brain motion

![Pasted image 20250918100132.png](../images/Pasted%20image%2020250918100132.png)

---

## Crosstalk Removal

Suite3D removal strategy:
- Scan values of `m in [0.01, 1.0]`
- Compute negative log-likelihood per value
- Choose `m` minimizing NLL

### Crosstalk types

1. **Spectral**
2. **Excitation** - multiple fluorophores excited
3. **Emission** - overlapping output wavelengths

![500](../images/Pasted%20image%2020250917181651.png)  ![500](../images/Pasted%20image%2020250917181722.png)

Sources:
- [Huygens](https://svi.nl/CrossTalk)
- [EvidentScientific](https://evidentscientific.com/en/microscope-resource/knowledge-hub/techniques/confocal/bleedthrough)

Check for chromatic aberration?
