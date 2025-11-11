### General

https://stephango.com/ramblings

- Ruo - Columbia, astrophysicist
	- https://veritas.astro.columbia.edu/people/ruo-yu-shang

Data types for images

- The images are normalized from raw float values to the [0, 1] range using percentiles:
``` python
mimg = (mimg - mimg1) / (mimg99 - mimg1)
mimg = np.clip(mimg, 0, 1)
```

- Then scaled to [0, 255] and cast to `uint8`:
``` python
mimg = (mimg * 255).astype(np.uint8)
```

## OME / Zarr

#ome-zarr #light-sheet-microscopy #big-data-viewer

This package provides OME-Zarr reading support to bigdataviewer and BigStitcher. In addition to the OME-NGFF json metadata, a bigdataviewer `dataset.xml` dataset definition is required that refers to the image format `bdv.multimg.zarr`. Currently, two basic loader classes are provided: `XmlIoZarrImageLoader` and `ZarrImageLoader`.

The OME-NGFF layouts supported by this package is limited. Most notably:
- Only OME-NGFF v0.4. is supported.
- Only full, 5 dimensional OME-Zarr (t,ch,z,y,x axes) images are supported.
- In bigdataviewer the image is reduced to 3 dimensions at `t=0`, `ch=0`.
- In case of multiple images, all images in one `ViewSetup` must have the same data type and the same resolution levels.
- `unit` in `axes` definitions in `.zattrs` are ignored. The same units are implicitly assumed across images. Use `voxelSize` in `dataset.xml` to define physical units.
- For multi-resolution images, the first dataset defined in the `.zattrs` must be the raw (finest) resolution. Anisotropy defined for the raw resolution in `.zattrs` are ignored, use `voxelSize` in `dataset.xml` instead. Downsampling factors are determined from `coordinateTransformations` compared to the raw resolution. Only factor of 2 downsampling sequences have been tested.
- Multiple images must be located in separate zgroup folders. Only one image per top level `.zattrs` file is allowed (multiple entries in the `multiscales` section are disregarded).


|              | Volume | Planar |
| ------------ | ------ | ------ |
| Uncompressed | 16.6   |        |
| Compressed   | 18.2   |        |

## Yao Wang
- MAX-HR
- MAX-EX upgrade to 2p-ram
- PSF1 and 14 look very similar
	- Axial: 6mm theory, 5.99 +/- 0.08 mm
	- Lateral: 240um theory, 240.6 
	- Aim is 4% power falloff, measured 6.21 +/- 0.44
- More abberation on edge beads than in the center beads
	- Cavity A/B are identicle (roughly)
- Separation should be 1um, but we're getting 1.48um +/- 0.18 um
- PSF stays relatively consistent through the cavities

## Kalyan 09/16/25
Discriminablity index (d')
- D' = 3 = 93% accurate spike detection
## Arash 09/09/25
- Memory, working memory in M2
- Interested in duration of responses following a visual task - correlate of working memory
	- How long is the delay of "persistent activity"
- Odor association task, A/B + C/D = Lick, otherwise don't, fast learning ~5-10 days
- L5 ~500um
- L5 is highly delayed in choice selective neurons 
- Thursday @4pm, Imaging Journal club to finish this up

## Kevin 8/26
- Arash, collab with JinKun
- M2, supplimentary motor cortex
- Intra-trial level, multi-trial level, session level
- Task scales, behavioral scales, representational scales
- Multiple Scales
	- Task Scales
		- stimulus, choice, outcome
	- Session Level
		- Repeated trials
		- Mice might fluctuate decision making strategies 
	- Multi-Trial Level
	- Behavioral Scales
		- Different stim strengths, contrasts effect response time
	- Representational Scales
- SVM classifier to distinguish behvaiors at the choice epoch
- Identify choice-selective neurons
- Tensor-component AAnalysis, trial dimension normally collapsed
- Choice selective neurons, binned by session (session 11-5, 6-12 etc..
	- Initially, many reward selective neurons
	- After outcome, activity of that population is provoked
	- After learning, that ratio of the error neurons > reward active neurons
	- Reinforcement learning / expectation conflict?
- GLM, log scaled based on contrast, negative sign = left / right trial, 1 or 0 for choice to left or right
	- Win-stay, lose-switch strategy
	- Gives the weights that apply to the full session
	- How well does this model predict mouse performance
	- Evaluate with per-trial log-likelyhood
	- -0.04 log likelyhood
	- static over movie, need something dynamic (Hidden marcov)
- Latent neural embeddings to guide model selection? 
- SPARKS (sequential predictive autoencoder;)

# Fourier Ring Correlation
![[Pasted image 20250827120427.png]]
- Define a cut-off frequency, above which there are no details to discern structures
- Normalized cross -correlation histrogram
- While rotating around Y axis, calculate resolutions at each orientation (XY, XZ)
![[Pasted image 20250827120328.png]]

## WHOLISTIC

![[Pasted image 20250903084016.png]]

## microImageLib

### Goals
- Fix memory error
- Update to CUDA version compatible with Windows Server 2022

**Main issues:**
1. Breaking change to textures introduced in CUDA 11.3
2. CUDA 10.0 (target) not available for Windows Server 2022

[NVIDIA Forum Post about Textures](https://forums.developer.nvidia.com/t/texture-is-not-a-template/47442/2?u=adlinge.pa)

[Github Issue bout CUDA 11.x / 12.x](https://github.com/NVIDIA/cuda-samples/issues/212)

Fixing 2:
1. Change all targets in .vcxproj from 10.0.* to 11.8.*
2. Retarget for Visual Studio <Version> (auto detected)
3. libAPI: Properties -> CUDA/C++ -> Command Line -> Additional Options: -allow-unsupported-compiler

Only FG/BG for sharpness
- what are superfluous 
- 

![[Pasted image 20250924145420.png]]

