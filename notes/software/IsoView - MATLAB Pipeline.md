---
created: <% tp.file.creation_date("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - image-processing
  - light-sheet-microscopy
  - software
aliases:
  - image-fusion
---

#  Image Fusion
- Generally recommend blending
	- Adaptive/Geometric are both stitching methods
- Wavelet fusion
	- Computationally expensive
	- Fusion artifacts (ringing)
	- Maintains SNR throughout volume
- Averaging is comparable to blending, better for sparse labeling
	- Image quality is inferior to blending methods


- **Step 1:** `clusterMF.m (multiFuse.m)` – Per-timepoint multiview fusion 
- **Step 2:** `localAP.m`, `analyzeParameters.m` – Temporal transformation parameters  
- **Step 3:** `clusterTF.m` – Time-fused multiview fusion
## `clusterMF.m` / `multiFuse.m`

### Notes
- The first step of multiFuse.m is aligning channels
- We don't do this because processingMode=2 (2 camera, single channel)
- `maskFusion`: 
	- use 0 for small animal, high confidence that all info from camera 1 is also in camera 2
	- use 1 for large specimin where they will have different "spatial coverage"
- Background intensity matching: When subtracting background from Cam2 out of Cam1, there doesn't appear to be much of a difference

### Overview 
#### Preprocessing - Filter, Threshold
- Load 3D stacks from both cameras.
- Apply anisotropic Gaussian smoothing to each volume.
- Estimate mean intensity above a threshold.
- Save smoothed volumes as `.transformedGauss`.
#### Mask Computation
- **3D mask (`mask3D`)**:
  - Threshold smoothed stack based on intensity level.
  - Remove small connected components (optional).
- **2D mask (`mask2D`)**:
  - Collapse `mask3D` to slice index map (`averageMask`).
#### Align Cam1 to Cam2
- Subtract Cam2 from Cam1 in overlapping Z regions.
- First pass, **Coarse**:
  - Sweep x/y shifts.
  - Compute correlation on pixelwise product.
- Second pass, **Fine**:
  - Optimize subpixel x/y offsets and in-plane rotation.
  - Save `bestXOffset`, `bestYOffset`, `bestRotation`.
####  Transform Cam2 Volume
- Apply **affine** transform to Cam2 stack using interpolation.
- Mask out invalid (out-of-bounds) regions.
- Save registered stack as `.transformedStack`.
#### Fusion Mask Creation
- Generate `averageMask` (Z indices of signal overlap).
- Apply optional padding:
  - Fill gaps via dilation or interpolation.
- Clamp to avoid blending near Z edges.
#### Data Slice Extraction
- Subtract background intensity.
- Extract small slab (± `intSizes(2)`) around `averageMask`.
- Save as `fusionDataSlice` for both cameras.
#### Intensity Correction (Optional)
- Apply correction factor to one stack.
- Clip negative values to zero.
- Save corrected stacks.
#### Fusion
- **Fusion type 0/1**:
  - Weighted blend around `averageMask`.
- **Fusion type 2**:
  - Wavelet-based fusion (per-slice).
- **Fusion type 3**:
  - Direct averaging.
- Save final `fusedStack` and XY/XZ/YZ projections.
### 1. Align Cameras

#### **Purpose**
- Compute and apply **spatial alignment** between the two cameras' image stacks.
- Generate transformation parameters (shifts + rotation) to co-register Cam2 with Cam1.
#### **Main Outputs**
- `.transformation.mat`: optimal `[xOffset, yOffset, rotation]`
- `.transformedStack`: aligned volume from Cam2
- `.transformedSlice`: aligned registration slab from Cam2

#### Code Walkthrough
-  calculate min-intensities and spatially convolve (smooth)
-  threshold smoothed 3D image to values above the min intensity
	- Where image > `minIntensity + (meanIntensity - minIntensity)`
	- this is 3D mask `mask3D`
-  The min intensity only
``` matlab
referenceMinIntensity = max(referenceMinIntensity, minIntensity);
```

![[Pasted image 20250722113501.png]]
- mean z-signal -> (X, Y) image
	- this is a slice-wise 2D map in `sliceMask`
- `maskFusion=0`  consider only regions that exist in both masks
	- otherwise consider regions that exist in either of the two masks
![[Pasted image 20250720155137.png]]

- mask3d -> (spatial filter, norm intensity, mean-z-signal) -> mask2d
- take camera 1 mask2d, camera 2 mask2d -> fuse
1. Average mask (fusionType=0) 
	- mean-z-index where both masks have signal (nonzero)
	- set everything else to 0
	- Use when sample is small
	 ![[Pasted image 20250722113838.png]]
2. Average mask (fusionType=1) 
	1. Start with average mask
	2. Fill in the remaining pixels from either z-plane
	 ![[Pasted image 20250722114149.png]]
- Remove small anomolies 
	- `averageMask(averageMask > (zSize - blending(2))) = 0;`
	- `averageMask(averageMask < blending(2)) = 0;`
	- blending is normally small int, here its `4`
	- `blending  = [20 4];    % blending ranges (channels, cameras)`
	- Blending = 4:
		 ![[Pasted image 20250722115759.png]]
	 - Blending = [10, 15, 20]
		 ![[Pasted image 20250722120217.png]]
- Prepare background pixels
	- `Computed intensityOffset = 100`
		![[Pasted image 20250722121500.png]]
- Middle z-slice before subtraction:
	![[Pasted image 20250722121620.png]]
- Subtraction:
	![[Pasted image 20250722121751.png]]
	- Cam1: 
		![[Pasted image 20250722122448.png]]
	- Cam2:
		![[Pasted image 20250722122513.png]]
- Median Filter
	![[Pasted image 20250722122842.png]]
- Apply X/Y Transformations (First ***course*** registration)
	- transforming x-offsets -50 to 50 in 11 steps and y-offsets -50 to 50 in 11 steps
	- `xOffsets =   -50   -40   -30   -20   -10     0    10    20    30    40    50`
	- `yOffsets = -50   -40   -30   -20   -10     0    10    20    30    40    50`
	- The top 4 best-aligned shifts
		- Each column = one `(xOffset, yOffset)` shift
		- Top row: shifted Cam2 slice
		- Middle row: fixed Cam1 slice
		- Bottom row: pixel-wise product (visual proxy for correlation)
	![[Pasted image 20250722123844.png]]
	- Correlation score: Which offset leads to the highest correlation
	 ![[Pasted image 20250722124603.png|400]]
- Fine registration 
	- Define a function that will be minimized by optimizer
	- initial point: 
		- `x0(1) = x-offset1
		- `x0(2) = y-offset`
		- `x0(3) = rotation around z in degrees`
	- refining the shift and estimating a small **in-plane rotation** (`x(3)`).
	- We now have:
		- bestXOffset = 47.3611
		-  bestYOffset = 35.4155
		-  bestRotation = -0.5124
		![[Pasted image 20250722132309.png]]
	 ![[isoview_alignment_comparison.mp4]]
	- Mean Z: Correlation over Z-planes
		![[Pasted image 20250722133255.png | 400]] 

| **Code Block**   | **Variable**           | **Scope**                 | **Purpose**                                                                     |
| ---------------- | ---------------------- | ------------------------- | ------------------------------------------------------------------------------- |
| **First block**  | `correlationSlice`     | Small slab (`dataSlice2`) | Align just the slab used for computing the transform (used in registration)     |
| **Second block** | `transformedStack`     | Full 3D stack             | Apply final transform to entire volume from Camera 2 for later fusion or output |
| **Z-extent**     | `size(dataSlice2, 3)`  | Slab only                 | e.g., 7 slices                                                                  |
|                  | `zSize`                | Entire volume             | e.g., 79 slices                                                                 |
| **Output**       | `transformedSliceName` | `.transformedSlice` file  | Used for alignment and correlation                                              |
|                  | `transformedStackName` | `.transformedStack` file  | Used for full transformed stack output                                          |
`transformedStack`: 
	![[Pasted image 20250722134035.png|500]]

**End of Align Cameras**

---
### 2. Fuse Cameras
#### **Purpose**
- Use **transformed and masked data** from both cameras to produce a **fused mask/image** (per z-slice or 3D).
- Combine Cam1 and Cam2's signals intelligently (depending on `fusionType`, etc.).
#### **Main Outputs**
- `.xyMaskTransformed`: 2D summary mask for Cam2 after alignment
- `.transformedMask3D`: binary 3D mask for Cam2 post-filter and threshold
- `.transformedMask2D`: slice-wise mean Z projection from the 3D mask
![[Pasted image 20250722134818.png | 400]]
#### Code Walkthrough

- Raw input
- Recompute average, thresholded, combined mask
	![[Pasted image 20250722140852.png|400]]
	![[Pasted image 20250722141441.png|400]]
	![[Pasted image 20250722141717.png|400]]
- Padding (all on same colormap)
	- Padding = 0: No padding
		![[Pasted image 20250722142751.png|400]]
	- Padding = 1: Fill
		![[Pasted image 20250722142846.png|400]]
	- Padding = 2: Dilate+Interpolate
		![[Pasted image 20250722142929.png|400]]
- Background subtraction `fusionDataSlice.klb`
	- analyzing residual intensity mismatch across cameras prior to fusion
	- slices from Camera 1 and Camera 2 after background intensity subtraction
	![[Pasted image 20250722143741.png]]
	- Correct for difference in signal intensity
		- `correctionFactor = intensitySum1 / intensitySum2;`
		- `intensityCorrection = 0.0000    1.0990    0.7682    0.0000    0.0000`
		- `.intensityCorrection.mat`
		- It looks like there isn't a huge difference with/without bg subtraction
		- `correctedStack.klb`
		![[Pasted image 20250722144338.png]]
- Fuse Cameras -> `.fusedStack.klb`
	- fusionType = 0/1: Weighted blending
		![[Pasted image 20250722144737.png|600]]
	- fusionType = 2: Wavelet transform
		![[Pasted image 20250722144946.png|600]]
	- fusionType = 3: Averaging
		![[Pasted image 20250722145044.png|600]]


## `localAP.m / analyzeParameters.m`

### Notes
- Quick and simple script
- Be careful to match the same `MutliFused_NNN` directory name used in `multiFuse`
### Overview
-  **Initialize data arrays**
	- `transformations`: stores [time, x-offset, y-offset, angle] per `timepoint`
	- `intensityCorrections`: stores [time, correctionFactor, correctionFlag]
	- `lookUpTable`: final output array of size `length(fullInterval) x 6`
-  **Loop through each `timepoint`**
	- Load:
		- `.transformation.mat` files for each camera and the fused result
		- `.intensityCorrection.mat` files and extracts multiplicative correction factors
	- Save:
		- `transformations.mat`
		- `intensityCorrections.mat` (if `readFactors`)
	- Smooth:
		- Applies robust local regression (`rloess`) smoothing across timepoints
		- Smooths both geometric and intensity parameters
		- Same gaussian code block as `multiFuse`
	- Build LUT
		- Fills rows of `lookUpTable` with smoothed values for each `fullInterval` timepoint
		- If a timepoint is missing in `transformations`, it uses weighted interpolation from the nearest earlier and later points, or nearest available point
	- MedianTable / MeanTable
		- compute `medianTable` and `meanTable` by sliding window smoothing:
			- `offsetRange`, `angleRange`, `intRange` control window sizes
	- StaticMode: If true, set mean/median to global average
		- Why?
	

| Raw intensity correction needed to match dynamic range between Cam 1 and Cam 2          | <br>![[factors.png\|300]]            |
| --------------------------------------------------------------------------------------- | ------------------------------------ |
| Frame-by-frame rotation angle in degrees                                                | ![[angles.png\|300]]                 |
| Combined (?) translation offset (x and y?) over time.                                   | ![[offsets.png\|300]]                |
| Amount of displacement in Y needed to optimize the correlation between Cam 1 and Cam 2. | ![[final_bestYOffset.png\|300]]      |
| Amount of displacement in X needed to optimize the correlation between Cam 1 and Cam 2. | ![[final_bestXOffset.png\|300]]      |
| Amount of rotation needed to optimize the correlation between Cam 1 and Cam 2.          | ![[final_bestRotation.png\|300]]     |
| Final per-frame intensity correction factor (blue = raw, red = smoothed)                | ![[final_correctionFactor.png\|300]] |

## `clusterTF.m / timeFuse.m`

### Notes
- Make sure your camera / channel  / filename configuration
- Performs the same operations in `multiFuse.m`
	- Uses `smoothed` parameters from `analyzeParameters`
	- Best X/Y Offset and Rotation
- Be careful to match the same `MutliFused_NNN` directory name used in `multiFuse`
### Overview

## Code Walkthrough
- Fuse Cameras
	- Affine transformation 
		- These transformation are always `.transformedStack.klb`
		- Transformed Slice is the correction applied to Cam 2, to match Cam 1
		![[Pasted image 20250723142817.png]]
- Align Cameras
	- Background intensity normalization
		![[Pasted image 20250723144729.png|400]]
	- The red dashed line marks the 5th percentile of the combined nonzero background data
	- Almost all background values fall _above_ this threshold, suggesting:
	    - This threshold will exclude only the lowest ~5% of background intensities
	    - it's a conservative threshold, won't subtracting true signal
	- Capture the `averageMask` -> `stitchedMask.klb (optional)`
		![[Pasted image 20250723145845.png]]
		![[Pasted image 20250723145909.png]]
		- ***Top Panel***
			- **averageMask**:
			    - Shows the average mask values used to define the region of interest for fusion.
			    - Brighter areas indicate stronger agreement or overlap between input stacks.
			    - This mask defines the **total extent** of the fused region (`averageMask > 0`).
			- **channelMask**:
			    - A binary mask (`uint16(1:zSize) <= averageMask`) indicating which camera’s data contributes at each voxel.
			    - White = voxels pulled from camera 1 (typically the _rear_ view).
			    - Black = voxels pulled from the base layer camera.
			- **averageMask > 0**:
			    - Logical version of the average mask to show which regions are actually included in the fused stack.
			    - Should closely match `channelMask`, but lacks z-depth dependency. It's used to define valid areas in the fused output.
		- ***Bottom Panel***
			- **Cam1 (masked)**:
			    - Gray-scale raw image from camera 1.
			    - Red overlay (`averageMask > 0`) shows the region where `averageMask` is positive — this is where data from cam1 contributes in the fused result **if `frontFlag == 0`**.
			    - Black/dark areas are either outside the field of view or unused in fusion.
			- **Cam2 (masked)**:
			    - Similar structure for camera 2.
			    - The right border's solid band in cam2 suggests it contributes heavily there.
			    - If `frontFlag == 1`, this is the base layer, overwritten where `channelMask == 1`.
			- **Fused Slice (masked)**:
			    - The actual fused output.
			    - Shows final blending based on:
			        - `averageMask > 0` to define the total extent
			        - `channelMask` to select the donor channel (cam1 or cam2) for each voxel.
			    - Red overlay confirms that data is retained mostly inside the mask area.
- Fused Stack -> `.fusedStack.klb`
	![[Pasted image 20250723152808.png|400]]
	![[Pasted image 20250723153039.png|400]]
	![[Pasted image 20250723153155.png|400]]
	![[Pasted image 20250723153242.png|400]]
	![[fusedStack.gif]]

## `localEC`
### Overview
- **Global volume dimensions**
    - Get stack height/width from each time point’s fused stack projections (XY, XZ, YZ)
    - Max over all timepoints 
	    - How much smaller each individual volume is (the “deltas”)
	    - Used to pad the volume (presumably later)
- **Intensity normalization**
    - For each timepoint, samples either the full 3D stack or its 2D projection to build a histogram above a brightness threshold.
    - Computes a background value (mean over a corner ROI) and a “center” of the high‐end histogram.
    - Saves per‑timepoint backgrounds, centers, and the derived multiplicative “intensityFactors” that would bring every timepoint to the same brightness scale.
- **Global mask building (if using automatic drift correction)**
    - Gaussian‑smooths each projection (large σ relative to structure size), thresholds to leave only the specimen region, and stacks them through time.
    - These masks let you visualize and verify that you’re tracking the same specimen geometry over the entire sequence.
- **Correlation‑based pairwise drift estimation (optional)**
    - For each consecutive timepoint pair, reads the (possibly zero‑padded) projections, applies an optional γ‑correction, and computes rigid shifts via phase‑correlation in XY, XZ and YZ.
    - Records these as `driftOffsets(n,:) = [Δx, Δy, Δz]` per timepoint.
- **Global drift correction**
    - Integrates the pairwise shifts to get “cumulativeDriftOffsets.”
    - Depending on `globalMode`:
        - **Mode 0:** skip.
        - **Mode 1 (automatic):** also compute the specimen’s centroid in each smoothed mask (`driftCenters`) and subtract that from your cumulative offsets to remove any residual wobble around the specimen’s center.
        - **Mode 2 (manual):** use user‑supplied drift vectors at chosen reference timepoints to interpolate a “static” correction curve.
- **Smoothing & final offsets**
    - Optionally applies an rloess smoother to drift fluctuations (over the window you chose).
    - Computes `finalDriftOffsets = cumulativeDriftOffsets – smoothedError`.
    - Saves out a `driftTable.mat` (time vs final [x y z]), plus figures showing:
        - raw pairwise offsets
        - cumulative offsets
        - specimen‑center drift
        - smoothed fluctuations
        - final corrected offsets
- **Outputs & diagnostics**
    - Writes `dimensions.mat`, `dimensionsMax.mat`, (and `dimensionsDeltas.mat`) 
    - Saves intensity background/center/factor files if used.
    - Saves mask stacks (if automatic global) and γ‑corrected projections (if used).
    - Dumps a series of PNG plots in your `configRoot` so you can inspect intensity vs time and drift curves.

### Notes
- It appears as though only X displacements are needed

![[Pasted image 20250723165359.png]]
![[Pasted image 20250723170048.png]]
![[Pasted image 20250723170114.png]]

- With globalMode, we expect the line @ 0 because it iteratively corrects the drifts?
	![[Pasted image 20250723170855.png]]

## Metadata

#### HEADER 
``` matlab
%'SPM00_TM000000_CM00_CHN01.klb'

headerInformation = readKLBheader(fullFilePath);
disp(headerInformation);

xyzct: [752 2048 79 1 1]
pixelSize: [1 1 1 1 1]
dataType: 1
compressionType: 1
blockSize: [96 96 8 1 1]
metadata: ''
headerVersion: 2
```

#### XML 

| **Field**                            | **Channel 1**                                    | **Channel 2**                                    |
| ------------------------------------ | ------------------------------------------------ | ------------------------------------------------ |
| **software_version**                 | 3.0.0817                                         | 3.0.0817                                         |
| **data_header**                      | Dre_HuC_H2BGCaMP6s_0-1                           | Dre_HuC_H2BGCaMP6s_0-1                           |
| **output_root**                      | (empty)                                          | (empty)                                          |
| **specimen_name**                    | sample                                           | sample                                           |
| **timestamp**                        | 7:59:39.667 PM 7/9/2015                          | 7:59:39.667 PM 7/9/2015                          |
| **time_point**                       | 0                                                | 0                                                |
| **specimen_XYZT**                    | X=1130.000_Y=1045.000_Z=-205.000_T=-1.0          | X=1130.000_Y=1045.000_Z=-205.000_T=-1.0          |
| **specimen_drift**                   | N/A                                              | N/A                                              |
| **angle**                            | -1.0                                             | -1.0                                             |
| **camera_index**                     | 2                                                | 2                                                |
| **camera_type**                      | C11440-22C,C11440-22C                            | C11440-22C,C11440-22C                            |
| **camera_roi**                       | 648_1400_0_2048,648_1400_0_2048                  | 648_1400_0_2048,648_1400_0_2048                  |
| **time_step**                        | 1                                                | 1                                                |
| **wavelength**                       | 488                                              | 488                                              |
| **illumination_arms**                | 3                                                | 12                                               |
| **illumination_filter**              | ND1.0                                            | ND1.0                                            |
| **laser_power**                      | 2.00                                             | 2.00                                             |
| **exposure_time**                    | 4.8                                              | 4.8                                              |
| **detection_filter**                 | BP525/50                                         | BP525/50                                         |
| **dimensions**                       | 2048x752x79,2048x752x79                          | 2048x752x79,2048x752x79                          |
| **z_step**                           | 5.130                                            | 5.130                                            |
| **planes**                           | 0-78,0-78                                        | 0-78,0-78                                        |
| **z_offset_planes**                  | #planes=1; Sync_index=N/A; Z=-290.0:(42.0, 42.0) | #planes=1; Sync_index=N/A; Z=-290.0:(-5.0, 94.0) |
| **detection_objective**              | Zeiss 20x/1.00,Zeiss 20x/1.00                    | Zeiss 20x/1.00,Zeiss 20x/1.00                    |
| **background_subtraction**           | n,n                                              | n,n                                              |
| **SI**                               | n                                                | n                                                |
| **experiment_notes**                 | (empty)                                          | (empty)                                          |
| **custom_pre_script**                | (empty)                                          | (empty)                                          |
| **custom_pre_commands**              | (empty)                                          | (empty)                                          |
| **custom_post_script**               | (empty)                                          | (empty)                                          |
| **custom_post_commands**             | (empty)                                          | (empty)                                          |
| **action: custom_pre_script**        | n                                                | n                                                |
| **action: si_reconstruction**        | n                                                | n                                                |
| **action: deconvolution**            | n                                                | n                                                |
| **action: registration**             | n                                                | n                                                |
| **action: fusion**                   | n                                                | n                                                |
| **action: image_compression**        | n                                                | n                                                |
| **action: segmentation**             | n                                                | n                                                |
| **action: object_space_compression** | n                                                | n                                                |
| **action: tracking**                 | n                                                | n                                                |
| **action: custom_post_script**       | n                                                | n                                                |
| **action: V3D**                      | n                                                | n                                                |
