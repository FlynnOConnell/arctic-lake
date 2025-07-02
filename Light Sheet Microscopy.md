Whole-central nervous system functional imaging
in larval Drosophila
William C. Lemon 1, *, Stefan R. Pulver 1, *, Burkhard Ho¨ckendorf1 , Katie McDole1 , Kristin Branson1 , Jeremy Freeman1
& Philipp J. Keller 

Key takeaways:
- Whole CNS - Brain + Spinal Cord
- 2 -5 Hz (2 photon / 1 photon respectively)
- 20,000 volumes/sample
	- 5 volumes / second / camera
	- 370 images per second
- Spatial alignment of 4 focal planes
- Capability: [400 x 200 x 200]um^3 

Data Strategy:
- Duel channel: functional  (GCaMP6s) , and a reference (tdTomato) 
- Yields two-channel, multi-view image stacks 
	- (~40 images per volume across 2–3 cameras) 
	- ~1.0 μm lateral / 2.5 μm axial resolution in first-instar larvae, and 
	- ~1.6 μm / 5.9 μm in third-instar larvae (larger, more scattering tissue) 
	- Resolution higher in the ventral nerve cord than in the brain lobes due to shorter light paths in the cord

3 challenges to overcome:
1. Microscope
	1. Multi-view: 25-fold better temporal resolution
	2. Move the sheet, not the sample
2. Specamin prep
	1. Up to an hour in non-transparent tissue
3. Computational pipeline
	1. Several TB/experiment
	2. Map functional  activity across CNS during specific behaviors

![[Pasted image 20250701141251.png]]
- The geometry of the specimen is automatically determined from multi-view image data 
- image foreground is stored using lossless compression in a custom block-based file format
- multiple camera views are spatially registered
- multi-view image data are fused
- DF/F representation of the hs-SiMView time-lapse data set is computed
- Locomotor activity patterns are automatically detected and classified
- High-resolution computational maps of CNS-wide activity timing are constructed for multiple fictive behaviours
- In order to quantitatively compare CNS-wide activity maps across multiple nervous systems, a CNS template is constructed from all data sets and subsequently used to transform all image data into a common reference coordinate system using nonlinear spatial registration.

1. Automatically determine the foreground and background
2. Compress out the sparseness in the mostly-empty background
3. Register the different camera views to each other and fuse them
4. Correct for specimen drift
5. Compute DF/F
6. Detect and classify which behavior the animal is producing
7. Map activity in different brain regions to specific behaviors

Additional: Compare CNS to spinal corod via **Nonlinear Image Registration** to create a reference template. 
- Image data from 6 nervous systems
- Variability between CNS locations across preps

![[Pasted image 20250701144529.png]]
![[Pasted image 20250701144401.png]]

1. Information flow of indivudal Neurons
2. Are these regions conserved across animals

- Maximum allowed volume: [800 x 800 x 250 um^3]
- Example: [1300 x 1300 x 1500 um^3] (at expense of frame rate)

- Development system: Why only the 3rd instar? 
- "This system is capable of imaging fruit fly in 3rd instar"

- Label all cell nuclei (nuclear label)
- This provides a "map" of spacial locations (blobs) of neurons 
- I think this is used to separate foreground / background

**Computational Methods**
1. Use 3D geometry to separate foreground / background
	1. Discard background, compress foreground
2. Multi-view fusion
	1. Align foreground image-stacks between cameras (rigid)
	2. Blend images using the geometric model 
		1. Minimize the distance each photon travels
3. Temporal registration
	1. Register each time-point to the midpoint of the recording
	2. No specifics described here
4. Compute DF/F for every voxel
	1. 25th/10th (1p/2p) percentile intensity level 
	2. 70-timepoint sliding window

**Wave Detection** 
- 16 3D rois 
- Classified as foreward (posterior -> anterior) or backwards (vice versa)
- First 120s of activity ignored (non-stationary signal drift)
- Each trace z-scored (F - mean / std)
- Subtract mean response across all segments
	- Highlight relative changes between segments
- Average left/right hemisegments
- Embed in SVD / PCA
	- Amplitude and Phase in 2D space correspond to presence and direction of waves

**Mapping whole-CNS activity timing**
- Measure when / what extent peaks are in sync with waves
- Traces fit using information about timecourse, vs without this information
- How well traces fit a rectangular function with fixed radius r 
![[Pasted image 20250701160553.png]]
**Spatial Registration of Nervous System**
- 6 independent CNS preps
- Get mean-intensity projections over time (Reference Volume)
- Manually mask nerves so it doesn't contribute to registration
- Two step: Affine, iteratively deformable registration
	- Minimize the deformation for any individual CNS prep
- B-spline diffeomorphic image registration
	- Gradient Step 0.1
	- Five subsampling factors (10, 6, 4, 2, full) [px]
	- Cross-correlation with neighbor radius of 6
- Quality assessed via manually annotating 3D landmarks and measuring the distance they moved during registration

**Supplimental Information**
![[Pasted image 20250701160830.png]]
- Illustrates the variable quality between cameras 
- Shows nuclear labeled nuclei
- Maximum-intensity projections

**Spatial Map**

1st instar
![[Pasted image 20250701161912.png|800]]![[Pasted image 20250701161939.png|800]]
vs 2nd instar
![[Pasted image 20250701164046.png]]

These are acquired *after* the functional dual light-sheet imaging,(optimizes for speed), with a single light sheet for highest resolution.
1. After fusing the images, a blob detector gets the centroid positions.
	1. Effectively segmentation 
	2. Very conservative (minimize false +)
	3. This is used as a local "seed"
2. Search for the brightest local pixel
	1. Not correlated pixels, i.e. suite2p 
	2. In a cube, find brightest pixel, accounts for anisotropy/duplicates
3. For each XYZ nucleus, take an intensity profile (cross section) 
	1. Modeled as a gaussian 
	2. Sharper, narrow gaussian indicates higher resolution
	3. std, how spread the brightness is
	4. median of the sigmas (x+ x- y+ y-) gives spread in the plane
	5. mean of z+ z- gives axial resolution
	6. Convert to full-width-half-maximum 
4. Remove ~0.38 um resolution of artifact from light scattering

## Code Analysis
`2048 x 752 pixels` 
`79 z-planes`
`5.13 um z-spacing`
`1 Hz volumetric imaging (Sequential mode)`
- 2 channels, 3 cameras / timepoint
- clusterPT.m (processTimepoint.m)-> clusterMF.m -> clusterMT.m 
	- Workhorse: multiFuse.m
- metadata (dims, exposure time, ) saved as XML
- .klb, .jp2, .tif
- SPMXX/TMYYYYYY/…
1. Data management
	1. Compression/decompression
	2. Cropping, missing timepoints, bg percentile values
	3. read/write tiff stacks
2. Multi-view image fusion 
	1. clusterMF.m (multi-fusion)
		1. Input dual-camera raw 
		2. Fuses camera inputs (2 cameras up to 4? ) -> 3D stack per timepoint
		3. Input: `SPM*/TM*/…klb`
		4. Output: 3D stack for each timepoint `…/multiFused/...` 
		5. What it does
			1. Register cam N to N + 1 (gradient decent)
			2. Split foreground / background
				1. Default percentile is 5% (lowest 5% signal is background)
	2. clusterTF.m (timepoint-fusion)
	3. Match brightness levels 
	4. collectProjections.m
		1. xy, xz, yz
3.  Functional Data Processing

- `multiFuse.m` is run first, for all timepoints independently
- `timeFuse.m` is run afterward to **align each fused volume to a reference timepoint**, using stored transformation offsets and masks
## **multiFuse.m**
- modes: 4-view, 2-view camera, 2-view channel
	- Channels are td-tomato + GCaMP6s
- 1. Align Channels (alignChannels.m)
	- Mask background out of foreground
		- Preprocess: spatial crop + gaussian filter
		- get min intensity from min() or percentile()
		- foreground mask 
			- threshold=min+maskFactor⋅(mean−min)
	- Align slices across cameras
		- Take XZ slice 
	- Channel registratioin 
		- fun = @(x) transformChannel(...);
		- [xSol, ...] = fminuncFA(...);
		- save `.transformation.mat`
- 2: Fuse Channels (fuseChannels.m)
	- Load X-Z slices `*.xzMask`, `*.mask2D`
	- Apply the rigid transformation saved previously
		- Affine transform with rotation + z-offset 
	- Check for / re-apply the mask/guassian filtering in step 1
	- Normalize Channels: compute a correction factor that will match the dynamic range of the two channels
	- Blending
		- If fusionType=0/1 (linear blending)
			- For each pixel, which channel dominates the mask, choose that pixel? 
			- `fused = chan1 * weight1 + chan2 * weight2 ` `
		- if fusionType = 2: Wavelet Function
			- `wfusimg(..., 'db4', 5, 'mean', 'max')` 
		- if fusionType = 3: Average
		- `fused = (stack1 + stack2) / 2`
	- Save fused stacks
- 3: Camera alignment (alignCameras.m)
	- Gaussian smooth, mask background
	- Load substack, normalize intensities
	- Iteratively shift and score normalized cross-correlation
		- `scores(x, y, 3) = sum(data1 .* shifted_data2) / (sum1 * sum2)` 
	- X shift, Y shift, Z rotation
		- Z-rotation accounts for camera mounting? 
- 4: Fuse Cameras (fuseCameras.m)
	- Compute average mask
		- maskFusion=0: overlap, intersection of both masks
		- maskFusion=1: union of only valid regions
	- (optional) Intensity correction
	- if fusionType = 0/1: 
		- weight = [0 → 0.5] for fading camera
		- weight = [1 → 0.5] for dominant camera
	- if fusionType = 2: wavelet per z-plane
	- if fusionType = 3: average both stacks at each voxel
	-  `.fusedStack`: the full fused 3D volume
	- `*_xyProjection`, `*_xzProjection`, `*_yzProjection`: max projections

### Inputs:
`parameterDatabase` or `*.mat` with: camera IDs, channels, masks, stack paths, correction params

- `*.xyMask`, `*.transformedMask3D`, `*.transformedMask2D`: 2D/3D masks computed during alignment (from `alignCameras.m` or earlier)
- `*.minIntensity.mat`: for background estimation (if `dataType == 1`)

### Intermediates:

| File                     | Purpose                                                  |
| ------------------------ | -------------------------------------------------------- |
| `*.transformation.mat`   | Coarse-to-fine XY/rotation alignment between views       |
| `*.fusionDataSlice`      | Local fusion slabs used to estimate intensity correction |
| `*.stitchedStack`        | Fused stack without blending (pre-blend version)         |
| `*.transformedGauss`     | Gaussian-filtered stack for mask creation                |
| `*.transformedMask3D/2D` | Output of thresholding + cleanup for 3D segmentation     |
### Outputs:

|                             |                                                           |
| --------------------------- | --------------------------------------------------------- |
| `*.fusedStack`              | Final fused 3D volume                                     |
| `*.fusedStack_xyProjection` | Max-Z XY projection                                       |
| `*.fusedStack_xzProjection` | Max-Y XZ projection                                       |
| `*.fusedStack_yzProjection` | Max-X YZ projection                                       |
| `*.fusionMask`              | `averageMask(x,y)`: Z-index of fusion per pixel           |
| `*.correctedStack`          | Background-corrected + intensity-scaled per-camera stacks |
| `*.intensityCorrection.mat` | Background values, intensity sums, correction factor      |
|                             |                                                           |
## **timeFuse.m**
- Rigid alignment (rotation + translation)
- Intensity correction
- Channel fusion (within each camera)
- Camera fusion (between cameras)
- Adaptive spatial blending
- Optional wavelet or averaging fusion strategies
- Similar setup to `multiFuse.m`

| Variable            | Description                               |
| ------------------- | ----------------------------------------- |
| `parameterDatabase` | `.mat` file storing pipeline parameters   |
| `t`                 | Time index into the `timepoints` array    |
| `memoryEstimate`    | Memory allocation hint used in processing |


### Inputs

| Variable            | Description                               |
| ------------------- | ----------------------------------------- |
| `parameterDatabase` | `.mat` file storing pipeline parameters   |
| `t`                 | Time index into the `timepoints` array    |
| `memoryEstimate`    | Memory allocation hint used in processing |
### Intermediates

| Variable                 | Description                                       |
| ------------------------ | ------------------------------------------------- |
| `primaryDataArray`       | Raw and processed image stacks (camera × channel) |
| `fusedStack`             | Final fused output volume                         |
| `averageMask`            | Adaptive mask for blending regions                |
| `currentTransformations` | Transform/correction values from lookup table     |
| `xSize, ySize, zSize`    | Stack dimensions after cropping                   |

### Outputs 
- `.fusedStack.klb` (main output)
- Intermediate stacks:
    - `.stack`, `.transformedStack`, `.correctedStack`, `.stitchedStack`
- Projection images (`XY`, `XZ`, `YZ`)
- `*.intensityCorrection.mat`
- `*.fusionDataSlice.klb`
- `_jobCompleted.txt` marker


### Reused in timeFuse:
- `.fusedStack` (used as reference source)
- `.fusionMask` (used for adaptive blending)
- `.intensityCorrection.mat` (may be reused or recomputed)
- `.correctedStack`, `.transformedStack` (used if not skipping steps)

## **Terminology:**
hemisegments, new favorite word
neurite - only used in developmental biology!!!!

## **Computational References** 
- [nonlinear (diffeomorphic) registration](https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2013.00039/full)
	- Curved, nonrigid deformations
	- Models smooth warps
	- Local: individual voxels are deformed
	- Gaussian -> B-Spline basis function
	- [ANTS: Github](https://github.com/ANTsX/ANTs)



