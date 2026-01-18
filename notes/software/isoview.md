---
title: IsoView Processing
tags: [isoview, light-sheet-microscopy, image-fusion]
---

# IsoView Processing

multi-view light-sheet microscopy pipeline for functional imaging

[Github: IsoView-Processing](https://github.com/MillerBrainObservatory/IsoView-Processing)

---

## Terminology

- **SiMView**: Simultaneous MultiView
- **SPIM**: Selective Plane Illumination Microscopy
- **diSPIM**: Dual-view, Inverted SPIM

---

## Pipeline Overview

```
clusterPT → clusterMF → localAP → clusterTF → clusterFR → localEC → clusterCS → clusterRS → localCR → clusterCD
```

### Processing Modes

| Cameras | Channels | Mode | Name | Example Config |
|---------|----------|------|------|----------------|
| 2 | 2 | 0 | 4-view fusion | `_CM00_CM01_CHN00_CHN01` |
| 1 | 2 | 1 | 2-view channel fusion | `_CM00_CHN00_CHN01` |
| 2 | 1 | 2 | 2-view camera fusion | `_CM00_CM01_CHN01` |
| 1 | 1 | 3 | single-view | `_CM00_CHN01` |

### Fusion Types

| Type | Method | Notes |
|------|--------|-------|
| 0 | adaptive blending | default, recommended |
| 1 | geometrical blending | similar to adaptive |
| 2 | wavelet fusion | computationally expensive, can have ringing artifacts, maintains SNR throughout volume |
| 3 | arithmetic averaging | comparable to blending, better for sparse labeling |

generally recommend blending (types 0/1). averaging is simpler but image quality is inferior to blending methods

---

## Script Reference

| Script | Description |
|--------|-------------|
| `clusterPT.m` | deadpixel correction, segmentation, compression |
| `clusterMF.m` | multiview fusion (per timepoint) via `multiFuse.m` |
| `localAP.m` | generate LUTs for time-fusion via `analyzeParameters.m` |
| `clusterTF.m` | temporal fusion via `timeFuse.m` |
| `clusterFR.m` | gaussian filtering, background subtraction, MIPs |
| `localCP.m` | collect and stack MIPs into time-sequence |
| `localEC.m` | pre-drift correction, phase correlation |
| `clusterCS.m` | drift correction, intensity normalization |
| `clusterRS.m` | functional data registration (x/y translation) |
| `localCR.m` | reference baseline calculation |
| `clusterCD.m` | compute dF/F values |
| `clusterIS.m` | 3D interpolation for isotropic pixel size |

---

## Output Directory Structure

### File Naming Convention

all output files follow this pattern:
```
SPM{specimen:02d}_TM{timepoint:06d}_CM{camera1:02d}[_CM{camera2:02d}]_CHN{channel1:02d}[_CHN{channel2:02d}]{suffix}.{ext}
```

common suffixes:
- `.fusedStack` - fused 3D volume
- `_xyProjection` - max projection along Z
- `_xzProjection` - max projection along Y
- `_yzProjection` - max projection along X
- `.minIntensity.mat` - minimum intensity for correction
- `.configuration.mat` - processing configuration
- `.shifts.mat` - registration shifts
- `.baseline` - baseline reference for dF/F
- `.filtered_N` - filtered with kernel size N
- `.corrected` - drift/intensity corrected
- `_jobCompleted.txt` - completion marker

### Stage 1: clusterPT Output

**input:** raw microscopy data
**output suffix:** `.corrected`

```
{dataset}.corrected/
├── SPM00/
│   ├── TM000000/
│   │   ├── SPM00_TM000000.configuration.mat
│   │   ├── SPM00_TM000000_CHN00.xml
│   │   ├── SPM00_TM000000_CHN01.xml
│   │   ├── SPM00_TM000000_CM00_CHN01.klb
│   │   ├── SPM00_TM000000_CM00_CHN01.minIntensity.mat
│   │   ├── SPM00_TM000000_CM01_CHN01.klb
│   │   ├── SPM00_TM000000_CM01_CHN01.minIntensity.mat
│   │   ├── SPM00_TM000000_CM02_CHN00.klb
│   │   ├── SPM00_TM000000_CM02_CHN00.minIntensity.mat
│   │   ├── SPM00_TM000000_CM03_CHN00.klb
│   │   └── SPM00_TM000000_CM03_CHN00.minIntensity.mat
│   ├── TM000001/
│   │   └── ...
│   └── ...
└── ...

{dataset}.corrected.projections/
├── SPM00_TM000000_CM00_CHN01.xyProjection.klb
├── SPM00_TM000000_CM00_CHN01.xzProjection.klb
├── SPM00_TM000000_CM00_CHN01.yzProjection.klb
└── ... (all cameras/channels/timepoints)
```

### Stage 2: clusterMF Output

**input:** clusterPT output
**output suffix:** `.TM######_multiFused{outputID}`

```
{outputString}.TM000000_multiFused_blending/
├── SPM00_TM000000_CM00_CM01_CHN01_jobCompleted.txt
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack.klb
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xyProjection.klb
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xzProjection.klb
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_yzProjection.klb
├── SPM00_TM000000_CM00_CM01_CHN01.transformation.mat
├── SPM00_TM000000_CM00_CM01_CHN01.globalMask.klb         # optional
├── SPM00_TM000000_CM00_CM01_CHN01.localMask.klb          # optional
├── SPM00_TM000000_CM00_CM01_CHN01.transformedMask.klb    # optional
├── SPM00_TM000000_CM00_CM01_CHN01.weights.klb            # optional
└── SPM00_TM000000_CM00_CM01_CHN01.offsets.mat

jobParameters.multiFuse.{timestamp}.mat  # saved to working directory
```

### Stage 3: localAP Output

**input:** clusterMF output
**output suffix:** `_analyzeParameters`

```
{outputString}_analyzeParameters/
├── lookUpTable.mat
├── transformations.mat
├── intensityCorrections.mat
├── offsets_smoothed.mat
├── angles_smoothed.mat
├── intensityFactors_smoothed.mat
├── plot_offsets.png
├── plot_angles.png
└── plot_intensityFactors.png
```

### Stage 4: clusterTF Output

**input:** clusterPT + clusterMF + localAP lookUpTable
**output suffix:** `.TM######_timeFused{outputID}`

```
{outputString}.TM000000_timeFused_blending/
├── SPM00_TM000000_CM00_CM01_CHN01_jobCompleted.txt
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack.klb
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xyProjection.klb
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xzProjection.klb
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_yzProjection.klb
└── ... (optional intermediate stacks)

jobParameters.timeFuse.{timestamp}.mat
```

### Stage 5: clusterFR Output

**input:** clusterMF or clusterTF output

```
{outputDir}{header}.TM000000_timeFused_blending/
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack.filtered_100.klb
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xyProjection.filtered_100.klb
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xyBProjection.filtered_100.klb  # back
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xyFProjection.filtered_100.klb  # front
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xzProjection.filtered_100.klb
└── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_yzProjection.filtered_100.klb

jobParameters.filterResults.{timestamp}.mat
```

### Stage 6: localEC Output

**input:** clusterMF/clusterTF projections
**output:** to configRoot

```
{configRoot}/
├── dimensions.mat
├── dimensionsMax.mat
├── dimensionsDeltas.mat
├── driftTable.mat                              # final [t, x, y, z]
├── driftDatabase.mat
├── driftStep1_pairwiseOffsets.png
├── driftStep2_pairwiseOffsetsCumulative.png
├── driftStep3_specimenCenters.png              # if globalMode=1
├── driftStep4_driftFluctuations.png            # if globalMode=1 && correlationFlag=1
├── driftStep5_driftFluctuationsFiltered.png
├── driftStep6_finalOffsets.png
├── xyMasks.klb                                 # if globalMode=1
├── xzMasks.klb
├── yzMasks.klb
├── xyGamma.klb                                 # if gamma != 1
├── xzGamma.klb
├── yzGamma.klb
├── intensityThreshold.mat                      # if intensityFlag=1
├── intensityBackgrounds.mat
├── intensityCenters.mat
├── intensityFactors.mat
├── intensityStep1_intensityBackgrounds.png
├── intensityStep2_intensityCenters.png
└── intensityStep3_intensityFactors.png
```

### Stage 7: clusterCS Output

**input:** clusterMF/clusterTF + localEC config

```
{outputRoot}/{headerPattern}/
├── SPM00_TM000000_CM00_CM01_CHN00_CHN01.fusedStack.corrected.klb
├── SPM00_TM000000_CM00_CM01_CHN00_CHN01.fusedStack_xyProjection.corrected.klb
├── SPM00_TM000000_CM00_CM01_CHN00_CHN01.fusedStack_xzProjection.corrected.klb
└── SPM00_TM000000_CM00_CM01_CHN00_CHN01.fusedStack_yzProjection.corrected.klb

jobParameters.correctStack.{timestamp}.mat
```

### Stage 8: clusterRS Output

**input:** clusterPT/clusterMF/clusterTF output
**output suffix:** `.registered`

```
{inputString}.registered/
├── Reference/
│   ├── SPM00_CM00_CM01_CHN01.referenceStack.klb
│   ├── SPM00_CM00_CM01_CHN01.reference_xyProjection.klb
│   ├── SPM00_CM00_CM01_CHN01.reference_xzProjection.klb
│   └── SPM00_CM00_CM01_CHN01.reference_yzProjection.klb
│
├── {header}.TM000000{footer}/                   # for fused data (dataType=1)
│   ├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack.klb
│   ├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xyProjection.klb
│   ├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xzProjection.klb
│   ├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_yzProjection.klb
│   └── SPM00_TM000000_CM00_CM01_CHN01.shifts.mat
│
└── SPM00/TM000000/                              # for unfused data (dataType=0)
    ├── SPM00_TM000000_CM00_CHN01.klb
    └── SPM00_TM000000_CM00_CHN01.shifts.mat

jobParameters.registerStacks.{timestamp}.mat
```

### Stage 9: localCR Output

**input:** clusterRS output
**output:** added to `.registered` folders

```
{inputString}.registered/{header}.TM######{footer}/
├── ... (existing clusterRS files)
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_medianFiltered.klb
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_baseline.klb         # at tick timepoints
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_baseline.xyProjection.klb
├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_baseline.xzProjection.klb
└── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_baseline.yzProjection.klb
```

### Stage 10: clusterCD Output

**input:** clusterRS + localCR output
**output suffix:** `.processed`

```
{inputString}.processed/
├── Reference/
│   └── SPM00_CM00_CM01_CHN01.referenceOffset.mat
│
├── {header}.TM000000{footer}/                   # for fused data
│   ├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack.klb              # dF/F stack
│   ├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xyProjection.klb
│   ├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_xzProjection.klb
│   ├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_yzProjection.klb
│   └── (if medianFlag=1):
│       ├── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_medianFiltered.klb
│       └── SPM00_TM000000_CM00_CM01_CHN01.fusedStack_medianFiltered.xyProjection.klb
│
└── SPM00/TM000000/                              # for unfused data
    └── ...

jobParameters.calculateDelta.{timestamp}.mat
```

### Stage 11: localCP Output

**input:** clusterMF/clusterTF/clusterFR output
**output:** stacked projection time-series

```
{folder}/
├── SPM00_CM00_CM01_CHN01_xyProjections_{outputString}.klb   # time x Y x X
├── SPM00_CM00_CM01_CHN01_xzProjections_{outputString}.klb   # time x Z x X
└── SPM00_CM00_CM01_CHN01_yzProjections_{outputString}.klb   # time x Z x Y
```

### Stage 12: clusterIS Output

**input:** clusterMF/clusterTF output
**output suffix:** `.Interpolated`

```
{rootFolder}.Interpolated/
├── {inputHeader1}0000{inputHeader2}/
│   └── {inputHeader3}0000{inputFooter}.klb
├── {inputHeader1}0001{inputHeader2}/
│   └── {inputHeader3}0001{inputFooter}.klb
└── ...

jobParameters.interpolateStack.{timestamp}.mat
```

---

## Detailed Processing Steps

### Step 1: Compression (`clusterPT.m`)

- deadpixel correction
- foreground segmentation
- lossless compression to `.klb`

### Step 2: Image Fusion (`clusterMF.m` / `multiFuse.m`)

the first step of multiFuse is aligning channels - we skip this for processingMode=2 (2 camera, single channel)

#### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `maskFusion=0` | use for small animal, high confidence both cameras see same thing |
| `maskFusion=1` | use for large specimens with different spatial coverage |
| `blending=[20,4]` | blending ranges [channels, cameras] |

#### 2.1 Preprocessing - Filter, Threshold

- load 3D stacks from both cameras
- apply anisotropic gaussian smoothing to each volume
- estimate mean intensity above threshold
- save smoothed volumes as `.transformedGauss`

#### 2.2 Mask Computation

**3D mask (`mask3D`)**:
- threshold smoothed stack based on intensity level
- where image > `minIntensity + (meanIntensity - minIntensity)`
- remove small connected components (optional)

**2D mask (`mask2D`)**:
- collapse `mask3D` to slice index map (`averageMask`)
- mean z-signal gives (X, Y) image in `sliceMask`

```matlab
referenceMinIntensity = max(referenceMinIntensity, minIntensity);
```

mask fusion:
- `maskFusion=0`: consider only regions that exist in both masks
- `maskFusion=1`: consider regions that exist in either mask

![[Pasted image 20250720155137.png]]

average mask creation:
1. fusionType=0: mean-z-index where both masks have signal (nonzero), set everything else to 0
2. fusionType=1: start with average mask, fill in remaining pixels from either z-plane

![[Pasted image 20250722113838.png]]
![[Pasted image 20250722114149.png]]

remove small anomalies:
```matlab
averageMask(averageMask > (zSize - blending(2))) = 0;
averageMask(averageMask < blending(2)) = 0;
```

blending parameter effects:
- blending = 4: ![[Pasted image 20250722115759.png]]
- blending = [10, 15, 20]: ![[Pasted image 20250722120217.png]]

#### 2.3 Align Cam1 to Cam2

background subtraction first:
- computed `intensityOffset = 100`
- subtract cam2 background from cam1

![[Pasted image 20250722121500.png]]
![[Pasted image 20250722121620.png]]
![[Pasted image 20250722121751.png]]

median filter applied:
![[Pasted image 20250722122842.png]]

**coarse registration**:
- sweep x/y shifts (-50 to 50 in 11 steps)
- compute correlation on pixelwise product
- top 4 best-aligned shifts shown below (each column = one shift, top row = shifted Cam2, middle = fixed Cam1, bottom = product)

![[Pasted image 20250722123844.png]]

correlation score surface:
![[Pasted image 20250722124603.png|400]]

**fine registration**:
- optimize subpixel x/y offsets + in-plane rotation
- initial point: `x0 = [x-offset, y-offset, rotation_degrees]`
- typical output: bestXOffset=47.36, bestYOffset=35.42, bestRotation=-0.51

![[Pasted image 20250722132309.png]]

mean Z correlation over planes:
![[Pasted image 20250722133255.png|400]]

outputs:
- `.transformation.mat`: optimal `[xOffset, yOffset, rotation]`
- `.transformedStack`: aligned volume from Cam2
- `.transformedSlice`: aligned registration slab from Cam2

| Code Block | Variable | Scope | Purpose |
|------------|----------|-------|---------|
| first block | `correlationSlice` | small slab | align slab used for computing transform |
| second block | `transformedStack` | full 3D stack | apply final transform to entire volume |

![[Pasted image 20250722134035.png|500]]

#### 2.4 Fuse Cameras

outputs:
- `.xyMaskTransformed`: 2D summary mask for Cam2 after alignment
- `.transformedMask3D`: binary 3D mask for Cam2 post-filter/threshold
- `.transformedMask2D`: slice-wise mean Z projection from 3D mask

![[Pasted image 20250722134818.png|400]]

recompute average, thresholded, combined mask:
![[Pasted image 20250722140852.png|400]]
![[Pasted image 20250722141441.png|400]]
![[Pasted image 20250722141717.png|400]]

padding options (all on same colormap):
- padding=0: no padding ![[Pasted image 20250722142751.png|400]]
- padding=1: fill ![[Pasted image 20250722142846.png|400]]
- padding=2: dilate+interpolate ![[Pasted image 20250722142929.png|400]]

background subtraction for fusion (`fusionDataSlice.klb`):
- analyzing residual intensity mismatch across cameras prior to fusion

![[Pasted image 20250722143741.png]]

intensity correction:
```matlab
correctionFactor = intensitySum1 / intensitySum2;
% intensityCorrection = [0.0000, 1.0990, 0.7682, 0.0000, 0.0000]
```

saved to `.intensityCorrection.mat` and `.correctedStack.klb`

![[Pasted image 20250722144338.png]]

**fusion outputs** (`.fusedStack.klb`):
- fusionType=0/1 (weighted blending): ![[Pasted image 20250722144737.png|600]]
- fusionType=2 (wavelet): ![[Pasted image 20250722144946.png|600]]
- fusionType=3 (averaging): ![[Pasted image 20250722145044.png|600]]

### Step 3: Temporal Parameters (`localAP.m` / `analyzeParameters.m`)

quick script - be careful to match the same `MultiFused_NNN` directory name used in multiFuse

process:
1. initialize arrays: `transformations`, `intensityCorrections`, `lookUpTable`
2. loop through timepoints, load `.transformation.mat` and `.intensityCorrection.mat`
3. apply robust local regression (`rloess`) smoothing across timepoints
4. build LUT with smoothed values, interpolate missing timepoints
5. compute `medianTable` and `meanTable` by sliding window smoothing

staticMode: if true, set mean/median to global average

output plots:

| Plot | Description |
|------|-------------|
| factors.png | raw intensity correction needed to match dynamic range |
| angles.png | frame-by-frame rotation angle in degrees |
| offsets.png | combined translation offset over time |
| final_bestYOffset.png | Y displacement to optimize correlation |
| final_bestXOffset.png | X displacement to optimize correlation |
| final_bestRotation.png | rotation to optimize correlation |
| final_correctionFactor.png | per-frame intensity correction (blue=raw, red=smoothed) |

![[factors.png|300]] ![[angles.png|300]] ![[offsets.png|300]]
![[final_bestYOffset.png|300]] ![[final_bestXOffset.png|300]]
![[final_bestRotation.png|300]] ![[final_correctionFactor.png|300]]

### Step 4: Time-Fused Fusion (`clusterTF.m` / `timeFuse.m`)

same operations as multiFuse but uses smoothed parameters from analyzeParameters

be careful to match the same `MultiFused_NNN` directory name

**affine transformation** (always `.transformedStack.klb`):
![[Pasted image 20250723142817.png]]

**background intensity normalization**:
![[Pasted image 20250723144729.png|400]]

the red dashed line marks 5th percentile of combined nonzero background - conservative threshold that won't subtract true signal

**averageMask capture** (`stitchedMask.klb` optional):
![[Pasted image 20250723145845.png]]
![[Pasted image 20250723145909.png]]

interpretation:
- **averageMask**: average mask values defining region of interest for fusion
- **channelMask**: binary mask indicating which camera contributes at each voxel (white=cam1, black=cam2)
- **averageMask > 0**: logical version showing included regions
- **Cam1/Cam2 (masked)**: raw images with red overlay showing contribution regions
- **Fused Slice (masked)**: final blending result

**fused stack output** (`.fusedStack.klb`):
![[Pasted image 20250723152808.png|400]]
![[Pasted image 20250723153039.png|400]]
![[Pasted image 20250723153155.png|400]]
![[Pasted image 20250723153242.png|400]]
![[fusedStack.gif]]

### Step 5: Drift Correction (`localEC.m`)

#### Process Overview

1. **global volume dimensions**: get stack height/width from each timepoint's projections, max over all timepoints, compute deltas for padding

2. **intensity normalization**: sample full 3D stack or projection to build histogram, compute background (mean over corner ROI), compute "center" of high-end histogram, save per-timepoint factors

3. **global mask building** (if automatic drift correction): gaussian-smooth each projection, threshold to leave specimen region, stack through time

4. **correlation-based pairwise drift estimation** (optional): read (possibly zero-padded) projections, apply optional gamma-correction, compute rigid shifts via phase-correlation in XY/XZ/YZ, record `driftOffsets(n,:) = [dx, dy, dz]`

5. **global drift correction**: integrate pairwise shifts to get cumulative offsets
   - mode 0: skip
   - mode 1 (automatic): compute specimen centroid in each smoothed mask, subtract from cumulative offsets
   - mode 2 (manual): use user-supplied drift vectors to interpolate correction

6. **smoothing & final offsets**: apply rloess smoother to drift fluctuations, compute `finalDriftOffsets = cumulativeDriftOffsets - smoothedError`

it appears as though only X displacements are needed for most samples

![[Pasted image 20250723165359.png]]
![[Pasted image 20250723170048.png]]
![[Pasted image 20250723170114.png]]

with globalMode, expect line @ 0 because it iteratively corrects drifts:
![[Pasted image 20250723170855.png]]

### Step 6: dF/F Computation

- registration: `clusterRS.m`
- reference baseline: `localCR.m`
- dF/F calculation: `clusterCD.m`

---

## Dead Pixel Correction

MATLAB: `correctInsensitivePixels()` in `processTimepoint_RC.m`
Python: `correct_dead_pixels()` in `isoview/corrections.py`

basic idea:
- get std projection along z
- get mean projection
- median filter both
- dead pixels = where raw deviates too much from filtered

threshold from linear fit of deviation vs mean, take max distance from line

**note**: MATLAB does `medfilt2` per z-slice, python does `scipy.ndimage.median_filter` on whole volume - slightly different results at edges

---

## Foreground Segmentation

anisotropic gaussian filter first:
```python
sigma_z = max(1, kernel_sigma / scaling)
```

both implementations do slab processing (10 slabs default) for memory

**BIG DIFFERENCE**: MATLAB uses `multithresh` (otsu), python uses percentile threshold - this is probably where most output differences come from

coordinate masks - average coordinates weighted by binary mask, same logic both sides

---

## Geometric Transforms

rotation is 90 degree increments only

clockwise:
```python
volume = np.transpose(volume, (0, 2, 1))[:, ::-1, :]
```

counterclockwise: same but flip other axis

remember MATLAB is 1-indexed (y,x,z), python is 0-indexed (z,y,x)

---

## MATLAB vs Python Differences

| Parameter | MATLAB | Python |
|-----------|--------|--------|
| gaussian sigma xy | kernelSigma | kernel_sigma |
| gaussian sigma z | max(1, kernelSigma/scaling) | same |
| median kernel | [3,3] | (3,3) |
| threshold | otsu | mask_percentile (default 50) |
| slabs | 10 | splitting param |
| background | 100 | background_value |

typical diff is ~60 mean absolute (0.09% of uint16 range), but can hit 65535 at mask edges

things that cause differences:
- median filter implementations: medfilt2 vs scipy.ndimage.median_filter, boundary handling
- gaussian filter: imgaussfilt3 vs scipy gaussian_filter
- **thresholding is the big one**: otsu vs percentile gives different masks
- float precision: MATLAB defaults to float64, python needs explicit casting

---

## Code Snippets

### Offset and Rotation
```matlab
RR = [cosd(bestRotation) sind(bestRotation); -sind(bestRotation) cosd(bestRotation)];
[XI ZI] = meshgrid(1:xSize, 1:zSize);
cc = [(xSize + 1) / 2.0 (zSize + 1) / 2.0];
XI = XI' - cc(1);
ZI = ZI' - cc(2);
XZaux = (RR * [XI(:) ZI(:) .* scaling]')';
XI = reshape(XZaux(:, 1) + cc(1), size(XI));
ZI = reshape(XZaux(:, 2) ./ scaling + cc(2), size(ZI));
ZI = ZI - bestOffset;
```

### Background Normalization

subsamples 3D stacks, removes zeros, concatenates, estimates background using percentile (e.g. 5th percentile of merged intensities)

```matlab
if correction(1) ~= 0
    if dataType == 1
        minIntensityName = [inputFolder '/' inputHeader '_CM' num2str(camera, '%.2d') '_CHN' num2str(tChannels(1), '%.2d') '.minIntensity.mat'];
        load(minIntensityName, 'minIntensity');
        backgroundIntensity1 = minIntensity(end);
    else
        backgroundArray1 = primaryDataArray{currentCamera, 1}(1:subSampling:end);
        backgroundArray2 = primaryDataArray{currentCamera, 2}(1:subSampling:end);
        background = prctile(cat(2, backgroundArray1(backgroundArray1 > 0), backgroundArray2(backgroundArray2 > 0)), percentile);
    end
end
```

### Gaussian Smoothing (slab processing)
```matlab
if splitting > 1
    gaussStack = zeros(xSize, ySize, zSize, 'uint16');
    splittingMargin = 2 * kernelSize;

    for i = 1:splitting
        xSlabStart = max(1, round((i - 1) * xSize / splitting + 1 - splittingMargin));
        xSlabStop = min(xSize, round(i * xSize / splitting + splittingMargin));
        if preciseGauss
            convolvedSlab = uint16(imgaussianAnisotropy(double(primaryDataArray{currentCamera, 2}(xSlabStart:xSlabStop, :, :)), kernelSigmaArray, kernelSizeArray));
        else
            convolvedSlab = imgaussianAnisotropy(primaryDataArray{currentCamera, 2}(xSlabStart:xSlabStop, :, :), kernelSigmaArray, kernelSizeArray);
        end
        % handle slab boundaries with splittingMargin overlap
    end
end
```

### Fuse Two Masks
```matlab
if maskFusion == 0
    % consider only regions that exist in both masks
    overlap = (sliceArray{1} > 0) & (sliceArray{2} > 0);
    averageMask = uint16((double(sliceArray{1}) .* double(overlap) + double(sliceArray{2}) .* double(overlap)) ./ 2);
else
    % consider regions that exist in either of the two masks
    overlap = (sliceArray{1} > 0) & (sliceArray{2} > 0);
    averageMask = uint16((double(sliceArray{1}) .* double(overlap) + double(sliceArray{2}) .* double(overlap)) ./ 2);
    averageMask = averageMask + ...
        uint16(double(sliceArray{1}) .* double(sliceArray{1} > 0) .* double(averageMask == 0)) + ...
        uint16(double(sliceArray{2}) .* double(sliceArray{2} > 0) .* double(averageMask == 0));
end
```

### Affine Registration
```matlab
[XI YI] = meshgrid(1:size(sliceArray{2}, 1), 1:size(sliceArray{2}, 2));
RR = [cosd(bestRotation) sind(bestRotation); -sind(bestRotation) cosd(bestRotation)];
cc = [(size(sliceArray{2}, 1) + 1) / 2.0, (size(sliceArray{2}, 2) + 1) / 2.0];
XI = XI' - cc(1);
YI = YI' - cc(2);
XZaux = (RR * [XI(:), YI(:)]')';
XI = reshape(XZaux(:, 1) + cc(1), size(XI));
YI = reshape(XZaux(:, 2) + cc(2), size(YI));
XI = XI - bestXOffset;
YI = YI - bestYOffset;
```

---

## Registration Notes

alignment won't be perfect - light refractive index differs between samples

### Approaches
- **intensity based**: slow for large volumes, hard to validate (correlation doesn't always mean better alignment)
- **bead based**: embed beads in agarose (rigid medium)
- **segmentation based**: look for sample intensities, ROIs like nuclei/membranes

### Geometric Local Descriptor
- each bead represented by nearest 3 neighbors
- for soma, only match 3/4 neighbors

### ICP (Iterative Closest Point)
- compare all views against each other
- fix first view, don't map back
- affine transformation model

### Parameters

| Parameter | Typical Value | Notes |
|-----------|---------------|-------|
| redundancy | 2-3 (max 4) | increase if not enough matches |
| significance | 2 | 1 = take whichever is best |
| allowed error | 5px | defines how big error is allowed |
| max distance | 20px | |
| sigma | 2.486 | |
| threshold | 0.01623 | |

source: [Bill Lemon: Registration of Light Sheet Microscopy](https://www.youtube.com/watch?v=IupXS_On2rg)

---

## Aim 2: Opposing View Visualization and Deconvolution

### Visualization and Registration

use BigDataViewer and BigStitcher to register Ch0 and Ch1 views (opposing axes)

for multi-view images:
- geometric local descriptor matching (affine)
- iterative closest point (affine)
- iterative closest point (non-rigid)

### SimpleITK approach

issues rotating CHN00 (moving) to match CHN01 (reference):
- rotate around Y axis 90deg
- resample moving → reference grid space
- linear interpolation, remove out of bounds
- flip order of Z-axis: `::-1`

### Multi-View Deconvolution

use Hari Shroff's MVD software: [PubMed 32601431](https://pubmed.ncbi.nlm.nih.gov/32601431/)

---

## Aim 3: Four-Camera and Three-Camera Fusion

### 4-Camera Processing
1. visualize all cameras in BDV
2. register opposing cameras
3. rotate Ch1 to match Ch0
4. deconvolve using MVD

### 3-Camera Deconvolution
1. drop noisy camera
2. deconvolve remaining three using MVD

---

## Metadata

### KLB Header
```matlab
headerInformation = readKLBheader(fullFilePath);
% xyzct: [752 2048 79 1 1]
% pixelSize: [1 1 1 1 1]
% dataType: 1
% compressionType: 1
% blockSize: [96 96 8 1 1]
% metadata: ''
% headerVersion: 2
```

### XML Metadata Fields

| Field | Example |
|-------|---------|
| software_version | 3.0.0817 |
| data_header | Dre_HuC_H2BGCaMP6s_0-1 |
| specimen_name | sample |
| timestamp | 7:59:39.667 PM 7/9/2015 |
| time_point | 0 |
| specimen_XYZT | X=1130.000_Y=1045.000_Z=-205.000_T=-1.0 |
| camera_index | 2 |
| camera_type | C11440-22C,C11440-22C |
| camera_roi | 648_1400_0_2048,648_1400_0_2048 |
| wavelength | 488 |
| illumination_arms | 3 (ch1), 12 (ch2) |
| laser_power | 2.00 |
| exposure_time | 4.8 |
| detection_filter | BP525/50 |
| dimensions | 2048x752x79,2048x752x79 |
| z_step | 5.130 |
| detection_objective | Zeiss 20x/1.00,Zeiss 20x/1.00 |

---

## Notes

- check whether to HFlip or VFlip (dorsal/ventral typically needs vflip)
- double check which camera is dominant
- GCaMP6s has better (less) light scattering
- can view single z-slice timelapse before clusterTF to check temporal sampling
- background intensity matching: when subtracting cam2 background from cam1, there doesn't appear to be much difference

### TODO
- should python use otsu instead of percentile? would make outputs match better
- boundary handling on filters might matter for edge ROIs
- check if coordinate mask NaN→0 casting causes issues downstream

---

## Future Extensions

- deep-learning-based aberration compensation: [Nature Communications 2024](https://www.nature.com/articles/s41467-024-55267-x)
- format support extensions via `readImage.m` / `writeImage.m`:
  - Zarr v2: [MathWorks Zarr Support](https://github.com/mathworks/MATLAB-support-for-Zarr-files)
  - cpp-tiff: [github](https://github.com/abcucberkeley/cpp-tiff)
  - cpp-zarr: [github](https://github.com/abcucberkeley/cpp-zarr)

---

## Resources

- [AIC Knowledge Base](https://knowledge.aicjanelia.org/)
- [File Format Guidelines](https://datastandards.janelia.org/posts/file_formats_introduction.html)
- [ClearMap 2.1](https://github.com/ClearAnatomics/ClearMap)
- [AIC BDV/BigStitcher Tutorial](https://knowledge.aicjanelia.org/posts/20210706-simview-reconstruction/)
- Loic's Python Open-SiMView pipeline (Zarr format) - not complete for functional data

### References
1. Bill Lemon: Lecture on multi-view light-sheet microscopy
2. Lemon et al., 2015: Supplementary 2 - Functional SiMView processing details

---

## Links

- [[calcium-imaging]] - main index
- [[file-formats]] - OME-Zarr, BigDataViewer, KLB
