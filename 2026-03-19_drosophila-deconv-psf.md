# drosophila dual-view deconvolution: PSF configurations

dataset: `E:\datasets\isoview\2026-01-23_drosophila\bdv\`

## Data

- resolution (um / px): 0.40625 x 0.40625 x 6.22 um (XYZ)
- isotropized voxel: 0.40625 um cubed
- raw shape: (38, 1848, 768) per view
- isotropized shape: (582, 1848, 768)
- StackA = VW90 (reference), StackB = VW00 (pre-registered to match VW90)

## PSFs

all PSFs are at isotropic 0.40625 um/pixel unless noted.

| PSF | source | shape (Z,Y,X) | FWHM (um) | notes |
|-----|--------|---------------|-----------|-------|
| CM00 | camera, `0p80p84p0_CM00.tif` | (65, 17, 17) | 0.8 x 0.8 x 4.0 | Z-elongated, native VW00 orientation |
| CM02 | camera, `0p80p84p0_CM02.tif` | (25, 19, 101) | 0.8 x 0.8 x 4.0 | X-elongated, pre-rotated |
| Born-Wolf | generated, `2026-02-24_PSF_Born-Wolf.tif` | (65, 256, 256) | unknown | large array |
| regDeconvProj test | generated, `psfs/regDeconvProj/PSF.tif` | (128, 128, 128) | unknown | from regDeconProject test set |
| Gaussian 0.6/4.0 | generated in python | (128, 128, 128) | 0.6 x 0.6 x 4.0 | used by diSPIMFusion runs |

CM00 and CM02 encode the same FWHM (0.8, 0.8, 4.0 um) but in different orientations.
CM02 was pre-rotated so its axial elongation is along X instead of Z.
for dual-view decon in the shared (VW90) coordinate frame:
- VW90 detection blur is along Z -> needs Z-elongated PSF
- VW00 (rotated) detection blur is along X -> needs X-elongated PSF

## regDeconProject runs (MATLAB, `all_deconv/`)

all use pre-registered isotropized stacks. all WB params: resFlag=1, alpha=0.05, beta=1.
"wb" in folder names is misleading for dual-view: all dual-view runs use traditional RL
(DeconDualView.m with deconMethod=1 uses flipPSF, not WB back projectors).

### single-view (WB deconvolution, 1 iteration)

| folder suffix | stack | PSF | PSF shape |
|---------------|-------|-----|-----------|
| PSF-CM00-0p8 | A (VW90) | CM00 | (65,17,17) |
| PSF-CM02-0p8 | A (VW90) | CM02 | (25,19,101) |
| PSF-2026-02-24-Born-Wolf | A (VW90) | Born-Wolf | (65,256,256) |
| PSF-testset-regdeconv | A (VW90) | regDeconvProj test | (128,128,128) |
| PSF-CM00-0p8 | B (VW00) | CM00 | (65,17,17) |
| PSF-CM02-0p8 | B (VW00) | CM02 | (25,19,101) |
| PSF-2026-02-24-Born-Wolf | B (VW00) | Born-Wolf | (65,256,256) |
| PSF-testset-regdeconv | B (VW00) | regDeconvProj test | (128,128,128) |

### dual-view (traditional RL, 1 iteration unless noted)

| folder suffix | PSFA (for StackA=VW90) | PSFB (for StackB=VW00) | notes |
|---------------|------------------------|------------------------|-------|
| PSF-original-cm00-cm02 | CM00 (65,17,17) | CM02 (25,19,101) | PSFA=CM00 Z-elong, PSFB=CM02 X-elong |
| PSF-flipped-cm00-cm02 | CM02 (25,19,101) | CM00 (65,17,17) | swapped: PSFA=CM02, PSFB=CM00 |
| PSF-cm00-rot90y-cm00 | CM00 rot90Y (25,19,101) | CM00 (65,17,17) | PSFA=CM00 rotated 90 deg Y via TransformJ, PSFB=CM00 unrotated |
| PSF-cm00-rot90y-cm00-flipped | CM00 (65,17,17) | CM00 rot90Y (25,19,101) | flipped: PSFA=CM00 unrotated, PSFB=CM00 rotated |
| PSF-wolf-default | unknown | unknown | no PSF files saved, only output |
| trad_iters/10_iters | CM00 (65,17,17) | CM02 (25,19,101) | traditional RL, 10 iterations |
| trad_iters/20_iters | CM00 (65,17,17) | CM02 (25,19,101) | traditional RL, 20 iterations |
| trad_iters/40_iters | CM00 (65,17,17) | CM02 (25,19,101) | traditional RL, 40 iterations |

## BigStitcher runs (`registration_fusion_bigstitcher/`)

bead-based registration (interest points), manual orientation for VW00 (+90 deg Y).
output shape: (769, 2013, 771) float32 — larger than diSPIMFusion due to different cropping/padding.

| file | method | shape |
|------|--------|-------|
| fused_avg-blending.tif | average fusion, blending weights | (769, 2013, 771) |
| fused_avg-content-based.tif | average fusion, content-based weights | (769, 2013, 771) |
| fused_avg_and_content.tif | average + content fusion combined | (769, 2013, 771) |

no deconvolution — these are weighted averaging fusions only.

## scipy registration (`registered_scipy/`)

bigstitcher XML transforms applied via scipy affine_transform.
used to generate pre-registered stacks for regDeconProject.

| file | shape | notes |
|------|-------|-------|
| VW00_registered.ome.tif | (38, 1848, 768) | raw voxels, registered |
| VW90_registered.ome.tif | (38, 1848, 768) | raw voxels, registered |
| VW00_registered_resampled.ome.tif | (582, 1848, 768) | isotropized |
| VW90_registered_resampled.ome.tif | (582, 1848, 768) | isotropized |
| bigstitcher_init.tmx | - | bigstitcher transform converted to diSPIMFusion TMX format |

## earlier diSPIMFusion comparison (`fusion_comparison-bdv/`)

| file | shape | notes |
|------|-------|-------|
| decon_fused.tif | (576, 1848, 768) | earlier run, 576 Z (wrong pixel size 0.41 instead of 0.40625) |
| fused_avg-content-based.ome.tif | (769, 2013, 771) | copy of bigstitcher content-based fusion for comparison |
| compare_fusions.ipynb | - | napari comparison notebook |
| bdv_compare/ | - | BDV zarr export of both for BigDataViewer viewing |

## diSPIMFusion runs (spimFusion.exe, `registered_dispim/` and `fusion_comparison/`)

all use `-imgrot 1` (spimFusion handles rotation internally).
registration via regc=4 (2D MIP + progressive affine), reused via regc=0 + saved transform.tmx.

| folder | PSF type | PSF size | back projector | iterations |
|--------|----------|----------|----------------|------------|
| registered_dispim | Gaussian (0.6/4.0 um) | 128^3 | Wiener-Butterworth | 10 |
| fusion_comparison/gaussian_wb | Gaussian (0.6/4.0 um) | 128^3 | Wiener-Butterworth | 10 |
| fusion_comparison/born_wolf | Born-Wolf | ~256^3 | Wiener-Butterworth | 10 |
| fusion_comparison/stock_40x | stock diSPIMFusion 40x PSFs | n/a | default (traditional?) | 10 |

## open questions

- correct PSF assignment for dual-view: PSFA=CM00 (Z-elong) for VW90, PSFB=CM02 (X-elong) for VW00-rotated? or swapped?
- Born-Wolf PSF FWHM and generation parameters not recorded
- objective NA still unknown (needed for accurate PSF)
