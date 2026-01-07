# # Suite3D: Volumetric cell detection for two-photon microscopy

https://www.biorxiv.org/content/10.1101/2025.03.26.645628v1

## Registration

- Takes the same FFT-based registration algorithm from Suite2p -> Extends to 3D
- Collects a volumetric reference image, rather than plane-by-plane
- For inter-plane shifts, uses subset ~200-400 frames
- Extend spatially tapered masks to 3D as well

***Volumetric registration leads to:***
1. reduced noise
2. improved estimates of brain motion

![[Pasted image 20250918100132.png]]

Volumetric Cell Detection
![[Pasted image 20250918100732.png]]

## Core Processing Steps
1. 3D Motion Correction
	1. lateral and axial brain movements (XYZ)
2. 3D Cell Detection
	1. spatial/temporal filtering
	2. normalization
	3. thresholding
3. 3D Segmentation
	1. Voxels assigned to distinct ROI's

