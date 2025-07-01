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

3 challanges to overcome:
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
**Terminology:**
hemisegments, new favorite word
neurite - only used in developmental biology!!!!

**Computational References** 
- [nonlinear (diffeomorphic) registration](https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2013.00039/full)
	- Curved, nonrigid deformations
	- Models smooth warps
	- Local: individual voxels are deformed
	- Gaussian -> B-Spline basis function
	- [ANTS: Github](https://github.com/ANTsX/ANTs)


