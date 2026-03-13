# diSPIMFusion vs regDeconProject: Pipeline Comparison

## Overview

Both repositories process dual-view light sheet microscopy data using the same CUDA backend (`libapi` from `microImageLib`). They differ in scope, frontend, and supported modalities.

| Aspect | diSPIMFusion | regDeconProject |
|--------|-------------|-----------------|
| Frontend | ImageJ macros / Python | MATLAB GUIs |
| Backend | Standalone CUDA executables | CUDA DLL called via MATLAB `calllib` |
| Modalities | Dual-view diSPIM | Dual, quad, reflective diSPIM, lattice light-sheet |
| Tissue stitching | No | Yes (Stitch_GUI) |
| Deep learning | No | Yes (DenseDeconNet, TensorFlow) |
| PSF generation | External (Python port of BackProjector) | Built-in BackProjector.m |
| Platforms | Windows, Linux | Windows (MATLAB required) |
| Documentation | User-Gudie PDFs | Nature Biotech paper + Code_description.pdf |

## diSPIMFusion

**Language:** ImageJ macros (frontend) + pre-compiled CUDA binaries (backend)

**Scope:** Focused pipeline for dual-view diSPIM registration and joint deconvolution.

### Entry Points

- **diSPIMFusion_UI.ijm** - main fusion GUI macro for ImageJ/Fiji
- **diSPIM_Preprocessing.ijm** - preprocessing macro (background subtract, deskew, crop, MIP)
- **cmd_\*.bat / sh_\*.sh** - command-line batch scripts in `cudaLib/`
- **run_isoview_fusion.py** - Python wrapper with PSF generation for non-standard geometries

### CUDA Executables (`cudaLib/bin/`)

| Binary | Purpose |
|--------|---------|
| spimFusionBatch | batch processing of multiple image pairs |
| spimFusion | single image pair fusion (registration + deconvolution) |
| reg3D | 3D registration only |
| deconSingleView | single-view deconvolution |
| deconDualView | dual-view joint deconvolution |
| checkGPUDevice | GPU device query |

### Pipeline Flow

```
raw diSPIM images (SPIMA, SPIMB)
  -> preprocessing macro (background subtract, deskew, crop, interpolate)
  -> fusion macro -> spimFusionBatch.exe with CLI args
    -> reg3D: 2D MIP init -> progressive affine (3->6->9->12 DOF)
    -> joint deconvolution: CUDA/FFT iterative (RL or WB)
    -> MIP projections
  -> output: fused 3D volumes + projections + transform matrices
```

### Key Parameters

- `OBJx`: objective type (40=40x/0.8NA, 10=10x/0.3NA, 50=adiSPIM 50x/1.1NA)
- `pixelSize{A,B}{x,y,z}`: voxel dimensions in micrometers
- `regChoice`: registration mode (0=none/reuse, 1=single, 2=dependent, 3=independent, 4=2D MIP init)
- `imRotation`: SPIMB rotation (0=none, 1=+90 Y, -1=-90 Y)
- `iteration`: deconvolution iterations (default 10)
- `-bp1`/`-bp2`: optional Wiener-Butterworth back projector PSFs (omit for traditional RL)

### Strengths

- self-contained, no MATLAB dependency
- cross-platform (Windows + Linux)
- simple deployment: copy folder into Fiji
- lightweight Python scripting option

## regDeconProject

**Language:** MATLAB (frontend + processing logic) + same CUDA `libapi` backend

**Scope:** Broader toolkit covering multiple microscope modalities, tissue stitching, and deep learning refinement.

**Reference:** Min Guo et al., "Rapid image deconvolution and multiview fusion for optical microscopy," *Nature Biotechnology* 38(11): 1337-1346 (2020)

### Modules

#### RegistrationFusion/
3D registration and joint deconvolution for dual-view time-lapse data.

| Function | Purpose |
|----------|---------|
| Registration.m | GUI-driven 3D registration (translation -> rigid -> 7/9/12 DOF) |
| Fusion.m | full pipeline: registration + iterative joint deconvolution |
| orient_90deg_angle.m | 90-degree rotation for diSPIM geometry alignment |
| ReadTifStack.m / WriteTifStack.m | TIFF I/O helpers |

#### WBDeconvolution/
Iterative deconvolution with multiple back projector options.

| Function | Purpose |
|----------|---------|
| DeconDualView.m | dual-view joint deconvolution (traditional or WB method) |
| DeconSingleView.m | single-view deconvolution with auto-generated back projector |
| DeconQuadView.m | four-view additive deconvolution (e.g., iSIM) |
| DeconReflectiveDiSPIM.m | spatial-variant RL for reflective diSPIM |
| DeconReflectiveLLS.m | spatial-variant RL for lattice light-sheet |
| BackProjector.m | generates inverse PSF filters (5 types) |
| IlluminationPattern.m | simulates light-sheet illumination profiles |
| ConvFFT3_S.m | 3D FFT convolution (GPU-compatible) |

**BackProjector filter types:** traditional (flipped PSF), gaussian, butterworth, wiener, wiener-butterworth

#### ClearedTissueProcessing/
Large-volume cleared tissue preprocessing and tile stitching.

| Function | Purpose |
|----------|---------|
| BigData_PreProcessing.m | deskew stage-scanning data, rotate 45 deg, downsample |
| BigData_Postprocessing.m | tile-wise deconvolution at full res, stitch with blending |
| Stitch_GUI.m | interactive 2D/3D tile registration and fusion |
| RigidRegistration.m | GPU-accelerated tile registration via libapi |
| Blend2D.m / BlendZ.m | overlap blending (average, replacement, linear ramp) |

#### DeepLearning/
TensorFlow-based DenseDeconNet for learning-based deconvolution refinement.

| Script | Purpose |
|--------|---------|
| Single_Input_DL.py | single-channel deep learning deconvolution |
| Dual_Input_DL.py | dual-channel (two-view) deep learning deconvolution |

### Pipeline Flow

```
raw dual-view images (StackA, StackB)
  -> Registration.m -> CUDA reg_3dgpu
     modes: translation -> rigid -> 7 DOF -> 9 DOF -> 12 DOF
     output: 3x4 transformation matrix M
  -> DeconDualView.m or Fusion.m
     input: registered stacks + PSF forward/back projectors
     method: traditional RL or Wiener-Butterworth
     GPU FFT convolution (ConvFFT3_S)
     output: fused 3D volume + MIPs
  -> [optional] DenseDeconNet refinement
  -> final reconstructed volume
```

**Large tissue pipeline:**
```
raw stage-scanning tiles
  -> BigData_PreProcessing.m (deskew, rotate 45 deg, downsample 5x)
  -> Stitch_GUI.m (tile registration + blending)
  -> BigData_Postprocessing.m (scale transform to full res, tile-wise decon, stitch)
  -> final cleared tissue volume
```

### Strengths

- multiple modalities (dual, quad, reflective, LLS)
- built-in PSF back projector generation with 5 filter types
- spatial-variant deconvolution for reflective systems
- large-volume tissue stitching
- deep learning refinement option

## Shared CUDA Backend

Both repos call the same `libapi` library (source in `microImageLib` repo). The full API surface from `libapi.h`:

### File I/O
```c
unsigned short gettifinfo(char tifdir[], unsigned int *tifSize);
void readtifstack(float *h_Image, char tifdir[], unsigned int *imsize);
void writetifstack(char tifdir[], float *h_Image, unsigned int *imsize, unsigned short bitPerSample);
```

### Device Query
```c
void queryDevice();
```

### 2D Registration
```c
int reg2d(float *h_reg, float *iTmx, float *h_img1, float *h_img2,
          unsigned int *imSize1, unsigned int *imSize2,
          int regChoice, bool flagTmx, float FTOL, int itLimit,
          int deviceNum, int gpuMemMode, bool verbose, float *records);
```

### 3D Registration
```c
int reg3d(float *h_reg, float *iTmx, float *h_img1, float *h_img2,
          unsigned int *imSize1, unsigned int *imSize2,
          int regChoice, int affMethod, bool inputTmx, float FTOL, int itLimit,
          int deviceNum, int gpuMemMode, bool verbose, float *records);

int reg_3dgpu(float *h_reg, float *iTmx, float *h_img1, float *h_img2,
              unsigned int *imSize1, unsigned int *imSize2,
              int regMethod, int inputTmx, float FTOL, int itLimit,
              int flagSubBg, int deviceNum, float *regRecords);
```

### 3D Transformation
```c
int atrans3dgpu(float *h_out, float *iTmx, float *h_img,
                unsigned int *imSize1, unsigned int *imSize2, int deviceNum);
int atrans3dgpu_16bit(unsigned short *h_out, float *iTmx, unsigned short *h_img,
                      unsigned int *imSize1, unsigned int *imSize2, int deviceNum);
```

### Deconvolution
```c
int decon_singleview(float *h_decon, float *h_img, unsigned int *imSize,
                     float *h_psf, unsigned int *psfSize,
                     bool flagDeconInitial, int itNumForDecon,
                     int deviceNum, int gpuMemMode, bool verbose, float *deconRecords,
                     bool flagUnmatch, float *h_psf_bp);

int decon_dualview(float *h_decon, float *h_img1, float *h_img2, unsigned int *imSize,
                   float *h_psf1, float *h_psf2, unsigned int *psfSize,
                   bool flagDeconInitial, int itNumForDecon,
                   int deviceNum, int gpuMemMode, bool verbose, float *deconRecords,
                   bool flagUnmatch, float *h_psf_bp1, float *h_psf_bp2);
```

### Fusion (Registration + Deconvolution)
```c
int fusion_dualview(float *h_decon, float *h_reg, float *h_prereg1, float *h_prereg2,
                    float *iTmx, float *h_img1, float *h_img2,
                    unsigned int *imSizeIn1, unsigned int *imSizeIn2,
                    float *pixelSize1, float *pixelSize2,
                    int imRotation, bool flagTmx, int regChoice, float FTOL, int itLimit,
                    float *h_psf1, float *h_psf2, unsigned int *psfSizeIn,
                    int itNumForDecon, int deviceNum, int gpuMemMode, bool verbose,
                    float *fusionRecords,
                    bool flagUnmatch, float *h_psf_bp1, float *h_psf_bp2);
```

### Maximum Intensity Projections
```c
int mp2dgpu(float *h_MP, unsigned int *sizeMP, float *h_img, unsigned int *sizeImg,
            bool flagZProj, bool flagXProj, bool flagYProj);
int mp3dgpu(float *h_MP, unsigned int *sizeMP, float *h_img, unsigned int *sizeImg,
            bool flagXaxis, bool flagYaxis, int projectNum);
```

### Calling Convention

- **diSPIMFusion:** standalone `.exe` binaries invoked via CLI arguments
- **regDeconProject:** `.dll` loaded into MATLAB via `calllib('libapi', ...)`

Both bundle CUDA 10.0 runtime (`cudart`), cuFFT, and FFTW3 libraries.

## Registration: Detailed Comparison

### Registration Choice (`regChoice` / `regMethod`)

Both repos expose the same underlying options, but diSPIMFusion's batch mode adds temporal strategies on top.

| Value | spimFusion.exe (`-regc`) | reg_3dgpu (`regMethod`) | spimFusionBatch (arg 16) |
|-------|--------------------------|-------------------------|--------------------------|
| 0 | no registration, apply input matrix | same | no registration, apply input matrix |
| 1 | phasor (pixel translation) | same | one image only (temporal) |
| 2 | affine (with/without input matrix) | same | all images dependently (temporal) |
| 3 | phasor -> affine | same | all images independently (temporal) |
| 4 | 2D MIP -> affine | same | n/a (batch only uses 0-3) |

spimFusionBatch's arg 16 controls the *temporal* strategy (which frames to register), while `-regc` in spimFusion.exe controls the *method*. The batch binary internally selects the method.

### Affine Method (`-affm` / `affMethod`)

Progressive DOF options, identical in both repos:

| Value | DOF | Description |
|-------|-----|-------------|
| 0 | 0 | no affine, apply input matrix only |
| 1 | 3 | translation only |
| 2 | 6 | rigid body (translation + rotation) |
| 3 | 7 | translation, rotation, uniform scaling |
| 4 | 9 | translation, rotation, independent scaling |
| 5 | 12 | full affine (directly) |
| 6 | 6->12 | rigid body then 12 DOF |
| 7 | 3->6->9->12 | progressive cascade (default) |

diSPIMFusion defaults to `-affm 7` (progressive). regDeconProject exposes this as `affMethod` in the Registration.m GUI.

### Initial Matrix Handling

| Value | spimFusion (`-itmx`) | spimFusionBatch (arg 18) | regDeconProject |
|-------|---------------------|--------------------------|-----------------|
| 0 | identity matrix (default) | default identity | `flagTmx=0` |
| 1 | load from file | load from file | `flagTmx=1`, pass 4x4 matrix |
| 2 | n/a | 3D phase translation | n/a |
| 3 | n/a | 2D MIP registration | n/a |

spimFusionBatch has extra initialization modes (2, 3) not in regDeconProject.

### SPIMB Rotation (`-imgrot` / `imRotation`)

| Value | Meaning |
|-------|---------|
| 0 | no rotation |
| 1 | +90 deg around Y-axis |
| -1 | -90 deg around Y-axis (diSPIMFusion default) |

regDeconProject handles this in `orient_90deg_angle.m` as a preprocessing step rather than a registration parameter.

### Registration Parameters

| Parameter | spimFusion flag | spimFusionBatch arg | regDeconProject | Default |
|-----------|----------------|---------------------|-----------------|---------|
| convergence tolerance | `-ftol` | arg 20 | `FTOL` | 0.0001 |
| max iterations | `-itreg` | arg 21 | `itLimit` | 3000 (exe) / 2000 (MATLAB) |
| GPU device | `-dev` | arg 34 | `deviceNum` | 0 |
| GPU memory mode | `-gm` | n/a | `gpuMemMode` | -1 (auto) / 1 (efficient) |
| save registered A | `-oreg1` | arg 22 | manual save | off / 0 |
| save registered B | `-oreg2` | arg 23 | manual save | off / 0 |
| output transform | `-otmx` | auto | manual save | off / auto |

## Deconvolution: Detailed Comparison

### Iteration Loop

Both use the same Richardson-Lucy alternating dual-view update. In regDeconProject the loop is visible in MATLAB:

```matlab
% DeconDualView.m, lines 95-103
for i = 1:itNum
    stackEstimate = stackEstimate .* ConvFFT3_S(stackA ./ ConvFFT3_S(stackEstimate, OTFA_fp), OTFA_bp);
    stackEstimate = max(stackEstimate, smallValue);
    stackEstimate = stackEstimate .* ConvFFT3_S(stackB ./ ConvFFT3_S(stackEstimate, OTFB_fp), OTFB_bp);
    stackEstimate = max(stackEstimate, smallValue);
end
```

In diSPIMFusion the same algorithm runs inside the CUDA binary (`decon_dualview` in libapi). The `flagUnmatch` parameter and `h_psf_bp1`/`h_psf_bp2` pointers control whether custom back projectors are used.

### Back Projector Types

| Type | regDeconProject (BackProjector.m) | diSPIMFusion |
|------|-----------------------------------|--------------|
| traditional | `flipPSF(PSF_fp)` | default (omit `-bp1`/`-bp2`) |
| gaussian | synthetic Gaussian at resolution limit | n/a |
| butterworth | high-pass Butterworth in Fourier domain | n/a |
| wiener | `OTF / (\|OTF\|^2 + alpha)` | n/a |
| wiener-butterworth | Wiener * Butterworth combined | pass pre-computed files via `-bp1`/`-bp2` |

diSPIMFusion doesn't generate back projectors itself. It either flips the forward PSF (traditional RL) or loads pre-computed back projector files. The Python script `run_isoview_fusion.py` ports BackProjector.m to generate these files externally.

### Wiener-Butterworth Parameters

| Parameter | BackProjector.m default | run_isoview_fusion.py | Purpose |
|-----------|------------------------|----------------------|---------|
| alpha | 0.001 (or 1=auto) | 0.05 | Wiener noise regularization |
| beta | 1 (auto from PSF cutoff) | 1 (auto) | Butterworth cutoff gain |
| n | 10 | 10 | Butterworth filter order |
| resFlag | 1 (FWHM) | 1 (FWHM) | resolution limit definition |

Note: alpha differs significantly between MATLAB (0.001) and the Python port (0.05). Higher alpha = more smoothing.

### Convolution

regDeconProject uses MATLAB FFT (CPU or GPU via `gpuArray`):
```matlab
% ConvFFT3_S.m
outVol = single(real(ifftn(fftn(inVol) .* OTF)));
```

diSPIMFusion uses CUDA cuFFT in compiled code. Same algorithm, hardware-optimized.

### Deconvolution Parameters

| Parameter | spimFusion flag | spimFusionBatch arg | regDeconProject | Default |
|-----------|----------------|---------------------|-----------------|---------|
| iterations | `-it` | arg 26 | `itNum` | 10 (exe) / 1 (MATLAB) |
| forward PSF A | `-fp1` | arg 24 | `PSFA_fp` | mandatory |
| forward PSF B | `-fp2` | arg 25 | `PSFB_fp` | mandatory |
| back projector A | `-bp1` | arg 35 (optional) | `PSFA_bp` | flip of fp1 |
| back projector B | `-bp2` | arg 36 (optional) | `PSFB_bp` | flip of fp2 |
| initialization | `-cON`/`-cOFF` | n/a | `flagDeconInitial` | OFF (use input image) |
| output bit depth | `-bit` | arg 32 | manual | same as input / 16 |
| GPU mode | `-gm` | n/a | `gpuFlag` | auto / CPU+GPU |

## PSF Pipeline: MATLAB vs Python Port

`run_isoview_fusion.py` ports `BackProjector.m` from MATLAB to Python/NumPy. The algorithms are functionally equivalent with minor differences.

### Gaussian PSF Generation

Both use `gen_gaussianPSF_3D` with identical formula:
- `sigma = FWHM / 2.3548`
- `coef = 1 / ((2*pi)^1.5 * sigma_x * sigma_y * sigma_z)`
- `PSF(i,j,k) = coef * exp(-(dx^2/2sx^2 + dy^2/2sy^2 + dz^2/2sz^2))`

**Indexing difference:** MATLAB uses 1-based indexing with center at `(S+1)/2`. Python uses 0-based but adds `+1` offset to match MATLAB's coordinate space. This produces equivalent centering.

### FWHM Measurement

Both extract 1D profiles along each axis and find half-max crossings. Identical logic.

### Wiener-Butterworth Filter

Both compute:
1. `OTF_flip = conj(FFT(PSF_fp))` (equivalent to flipping PSF in space)
2. `OTF_wiener = OTF_norm / (|OTF_norm|^2 + alpha)`
3. Butterworth mask: `1/sqrt(1 + ee * w^n)` where `ee = 1/beta^2 - 1`
4. Combined: `OTF_bp = mask * OTF_wiener`
5. `PSF_bp = real(IFFT(OTF_bp))`

### Differences

| Aspect | BackProjector.m | run_isoview_fusion.py |
|--------|----------------|----------------------|
| alpha default | 0.001 | 0.05 |
| PSF size | from input data | hardcoded to data dimensions |
| FWHM input | measured from PSF file | specified as constants |
| auto-beta | measures cutoff from forward OTF | same logic |
| output | returns PSF_bp + OTF_bp | saves PSF_bp as TIFF |

## Extended Modalities (regDeconProject only)

### DeconQuadView.m
Extends dual-view to 4 simultaneous views (e.g., iSIM with 4 illumination angles). Each iteration updates the estimate from all 4 views, then averages: `estimate = (estA + estB + estC + estD) / 4`. Requires 4 PSF kernel pairs.

### DeconReflectiveDiSPIM.m
Accounts for spatial-variant illumination in reflective diSPIM systems. Pre-computes a 3D excitation pattern using `IlluminationPattern.m`, then weights each z-slice's contribution based on illumination intensity. The sensitivity correction normalizes by local illumination strength.

### DeconReflectiveLLS.m
Similar spatial-variant approach for reflective lattice light-sheet systems. Uses line-based illumination patterns (not Gaussian sheets) rotated at an angle (e.g., 31 degrees). Sweeps illumination lines in x rather than processing z-slices.

### IlluminationPattern.m
Generates theoretical light-sheet illumination profiles for various modes:
- mode 0: cross excitation (two Gaussian sheets at 90 deg, stage scanning)
- mode 1: epi illumination (single Gaussian)
- mode 2: regular light sheet (single perpendicular Gaussian)
- mode 3: rotated sheet (two Gaussians at +/- angle)

Computes depth-dependent beam width from Rayleigh range: `w(z) = w0 * sqrt(1 + (z/zr)^2)` where `zr = pi * w0^2 / lambda`.

## Cleared Tissue Pipeline (regDeconProject only)

For large stage-scanning diSPIM volumes that exceed GPU memory.

### BigData_PreProcessing.m
Raw stage-scanning data has oblique geometry because the light sheet enters at 45 degrees to the stage motion axis. Preprocessing corrects this:

1. **Shear correction** - removes parallelogram distortion from stage stepping
2. **Z interpolation** - matches axial sampling between views
3. **45-degree rotation** - rotates oblique acquisition plane into standard XY orientation
4. **ROI crop** - extracts valid overlap region after rotation
5. **5x downsampling** - produces coarse volumes for fast registration

The 45-degree rotation is geometrically necessary: each detection objective sees data in its own oblique coordinate frame. Rotation aligns both views to a shared axis-aligned frame.

### Stitch_GUI.m
Interactive MATLAB GUI for registering and merging tiles:
- `RigidRegistration.m` uses GPU `reg_3dgpu` for tile-to-tile alignment
- `NCC.m` computes normalized cross-correlation quality metric
- `Merge2D.m` combines tiles with configurable overlap blending
- `Phasor.m` provides phase-correlation for shift detection

### BigData_Postprocessing.m
Applies registration and deconvolution at full resolution:
1. Reads coarse registration transform from downsampled result
2. Scales transform back to full resolution (`M(4,:) *= 5`)
3. Tiles the volume into 512x512x512 GPU-sized crops
4. Applies registration + joint deconvolution per tile via CUDA
5. Stitches tiles with overlap blending (`BlendZ`, `Blend2D`)

The "inverse" is not literally undoing the rotation (that stays). It refers to scaling the registration transform back up from the downsampled domain where it was computed.

## Deep Learning Module (regDeconProject only)

### DenseDeconNet Architecture
Encoder-decoder (U-Net style) with dense connections:

- **Input:** 3D TIFF volume (280 x 328 x 204 voxels), normalized to [0,1]
- **Encoder:** dense blocks with skip concatenations, 2x2x2 stride downsampling
- **Bottleneck:** processing at half resolution
- **Decoder:** transposed convolution for upsampling, skip connections from encoder
- **Output:** single-channel volume, same dimensions as input
- **Activations:** ReLU throughout, leaky ReLU at output
- **Normalization:** batch norm after every convolution (EMA decay 0.9)

### Training

| Parameter | Single-Input | Dual-Input |
|-----------|-------------|------------|
| Framework | TensorFlow 1.x | TensorFlow 1.x |
| Iterations | 12000 | 12000 |
| Batch size | 1 | 1 |
| Initial LR | 0.04 | 0.004 |
| LR decay | 0.98 every 150 steps | 0.96 every 600 steps |
| Optimizer | Adam | Adam |

**Loss function:** `MSE - log((1+SSIM)/2) - 1.3 * prediction_min`

Combines reconstruction accuracy (MSE), perceptual quality (SSIM), and non-negativity encouragement (prediction_min).

### Integration
The network replaces iterative deconvolution with a single forward pass. Dual-Input variant concatenates two views along the channel axis, learning to fuse and deconvolve simultaneously. Training requires paired data (blurry input, ground-truth deconvolved output).

## Unified Parameter Reference

### Registration

| Concept | spimFusion.exe | spimFusionBatch | regDeconProject MATLAB |
|---------|---------------|-----------------|------------------------|
| registration method | `-regc` (0-4) | arg 16 (0-3, temporal) | `regChoice` (0-4) |
| affine DOF | `-affm` (0-7) | internal | `affMethod` (0-7) |
| initial matrix | `-itmx <file>` | arg 18 (0-3) + arg 19 | `flagTmx` (0/1) + matrix |
| SPIMB rotation | `-imgrot` (-1,0,1) | arg 17 | `orient_90deg_angle.m` |
| convergence | `-ftol` | arg 20 | `FTOL` |
| max iterations | `-itreg` | arg 21 | `itLimit` |
| GPU device | `-dev` | arg 34 | `deviceNum` |
| GPU memory | `-gm` (-1,0,1,2) | n/a | `gpuMemMode` (1,2) |

### Deconvolution

| Concept | spimFusion.exe | spimFusionBatch | regDeconProject MATLAB |
|---------|---------------|-----------------|------------------------|
| iterations | `-it` | arg 26 | `itNum` |
| forward PSF A | `-fp1 <file>` | arg 24 | `PSFA_fp` variable |
| forward PSF B | `-fp2 <file>` | arg 25 | `PSFB_fp` variable |
| back projector A | `-bp1 <file>` (optional) | arg 35 (optional) | `PSFA_bp` or auto |
| back projector B | `-bp2 <file>` (optional) | arg 36 (optional) | `PSFB_bp` or auto |
| BP method | file-based (pre-computed) | file-based | `bp_type` string |
| initialization | `-cON`/`-cOFF` | n/a | `flagDeconInitial` |
| output bit depth | `-bit` (16/32) | arg 32 | manual in WriteTifStack |

### Projections (diSPIMFusion batch only)

| Projection | spimFusionBatch arg |
|------------|---------------------|
| X projection | arg 27 |
| Y projection | arg 28 |
| Z projection | arg 29 |
| 3D X-axis | arg 30 |
| 3D Y-axis | arg 31 |
