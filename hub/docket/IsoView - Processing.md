---
created_date: <% tp.file.creation_date("YYYY-MM-DD") %>
updated_date: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - isoview
  - light-sheet-microscopy
  - mbo
---
# IsoView Functional Imaging Pipeline

[Github Branch for testing and changes](https://github.com/MillerBrainObservatory/IsoView-Processing/pull/1)

| Cameras | Channels | Mode | Name                     | Example `configurationString` |
| ------- | -------- | ---- | ------------------------ | ----------------------------- |
| 2       | 1        | 2    | **2-view camera fusion** | `_CM00_CM01_CHN01`            |
## General notes
SiMView : **S**imultaneous **M**ulti**V**iew 
SPIM : **S**elective **P**lane **I**llumination **M**icroscopy
diSPIM : **D**ual-view, **I**nverted, **S**elective **P**lane **I**llumination **M**icroscopy
- What is the purpose of clusterPT -> clusterRS (skipping image fusion)
1. Make sure you know whether to HFlip or VFlip. I
	1. I would think that dorsal/ventral would need to be vflipped, and that was defaulted in the script 
2. Double check which camera is dominant
3. GCamP6s
- better (less) light scattering in these samples
- Power falloff comparison between light beads and this data
- Can we view a single z-Slice time-lapse before running clusterTF to see if temporal sampling is high enough or if there are any points of large drift?

## Ideas for Other Pipelines
- Calculates a lot of metadata needed downstream
	- Volumetric dims XYZ 
	- Mean/Min intensity correction
## Aim 1: Functional Image Processing of IsoView Recording 

### 1. Lossless Compression and Conversion to `.klb`
- **Script:** `clusterPT.m`
- **Function:** Deadpixel correction, foreground segmentation, lossless compression
### 2. Image Fusion
- **Step 1:** `clusterMF.m` – Per-timepoint multiview fusion  
- **Step 1: Pre-processing:** `localEC.m`
- **Step 2: Drift Correction:** `clusterCS.m`
- Suite2p 


- **Step 2:** `localAP.m`, `analyzeParameters.m` – Temporal transformation parameters  
- **Step 3:** `clusterTF.m` – Time-fused multiview fusion
### 3. Image Registration and Drift Correction
- **Step 1: Pre-processing:** `localEC.m`
- **Step 2: Drift Correction:** `clusterCS.m`
### 4. Functional Imaging and dF/F Computation
- **Registration:** `clusterRS.m`
- **Reference Baseline:** `localCR.m`
- **dF/F Calculation:** `clusterCD.m`

---
## Aim 2: Opposing View Visualization and Deconvolution

### 2.1 Visualization and Registration
- Use **BigDataViewer** and **BigStitcher**
- Register Ch0 and Ch1 views (opposing axes)

#### Notes
- For Multi-View Images
	- Geometric Local Descriptor Matching (Affine)
	- Iterative Closest Point (Affine)
	- Iterative Closest Point (Non-rigid)
- Issues rotating CHN00 (moving) to match CHN01 (reference)
- Using python / SimpleITK
	- Rotate around Y axis 90deg
	- Resample moving -> reference grid space
	- Linear interpolation -> Remove out of bounds 
	- Flip order of Z-axis: `::-1`

### 2.2 Multi-View Deconvolution
- Use **Hari Shroff’s MVD software**
- Reference: [PubMed 32601431](https://pubmed.ncbi.nlm.nih.gov/32601431/)

---

## Aim 3: Four-Camera and Three-Camera Fusion and Deconvolution

### 3.1 4-Camera Processing
- Visualize all cameras in **BDV**
- Register opposing cameras
- Rotate Ch1 to match Ch0
- Deconvolve using **MVD**

### 3.2 3-Camera Deconvolution
- Drop noisy camera
- Deconvolve remaining three using **MVD**

---
## Script Descriptions

| Script                | Description                                                                       |
| --------------------- | --------------------------------------------------------------------------------- |
| `clusterPT.m`         | Deadpixel correction, segmentation, compression (generates input for `clusterMF`) |
| `clusterMF.m`         | Multiview fusion (per timepoint) using `multiFuse.m`, `fInterpolate.mexw64`       |
| `localAP.m`           | Generate LUTs for time-fusion                                                     |
| `analyzeParameters.m` | Parameter evaluation for `clusterTF.m`                                            |
| `clusterTF.m`         | Temporal fusion using `timeFuse.m`                                                |
| `clusterFR.m`         | Adaptive local background subtraction                                             |
| `localCP.m`           | Collect and stack MIPs                                                            |
| `localEC.m`           | Pre-drift correction, phase correlation                                           |
| `clusterCS.m`         | Drift correction, intensity normalization                                         |
| `clusterRS.m`         | Functional data registration (x/y translation)                                    |
| `localCR.m`           | Reference baseline calculation                                                    |
| `clusterCD.m`         | Compute dF/F values                                                               |
| `clusterIS.m`<br>     | Isotropic 3D stack generation                                                     |

---

## File/Folder Outputs

- `.registered/` — from `clusterRS.m`
- `.baseline_??Projection.klb` — from `localCR.m`
- `.processed/` — from `clusterCD.m`
- `.medianFilter.klb` — sampled timepoints for registration

---

## Upcoming

**Wait for above steps to complete.** Then:

### Format Support Extensions (via `readImage.m`, `writeImage.m`)
- [ ] Zarr v2: [MathWorks Zarr Support](https://github.com/mathworks/MATLAB-support-for-Zarr-files)
- [ ] CPP-TIFF: [cpp-tiff GitHub](https://github.com/abcucberkeley/cpp-tiff)
- [ ] CPP-Zarr: [cpp-zarr GitHub](https://github.com/abcucberkeley/cpp-zarr)

### Opposing View Fusion
- Fuse views to 0° and 90°
- Then apply MVD (Hari’s software)

---
- [ ] 
## Future Extensions
- Deep-learning-based aberration compensation  
  ([Nature Communications 2024](https://www.nature.com/articles/s41467-024-55267-x))

---

## Resources
- [AIC Knowledge Base](https://knowledge.aicjanelia.org/)
- [File Format Guidelines](https://datastandards.janelia.org/posts/file_formats_introduction.html)
- [ClearMap 2.1 Toolbox](https://github.com/ClearAnatomics/ClearMap)
- Loic’s Python Open-SiMView pipeline (Zarr format) – *not complete for functional data*

---

## References
1. Bill Lemon: Lecture on multi-view light-sheet microscopy  
2. [AIC BDV/BigStitcher Tutorial](https://knowledge.aicjanelia.org/posts/20210706-simview-reconstruction/)  
3. Lemon et al., 2015: Supplementary 2 – Functional SiMView processing details  
4. [[2015 Lemon Keller|2015 Lemon Keller]]
