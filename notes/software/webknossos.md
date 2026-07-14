---
tags:
  - webknossos
  - visualization
  - calcium-imaging
  - data-format
  - ome-zarr
  - ngff
category: software
created: 2026-01-16
updated: 2026-02-23
source: https://docs.webknossos.org
---

# WEBKNOSSOS

open-source web app for annotating and exploring large 3D image datasets. scala/play backend, typescript/react frontend with webgl rendering.

## supported formats

natively served (no conversion needed):
- **OME-Zarr** (NGFF v0.4 and v0.5) - default and recommended
- **Zarr / Zarr3**
- **N5**
- **Neuroglancer Precomputed**
- **WKW** (legacy native format)

uploaded with automatic conversion (`convert_to_wkw` job):
- OME-TIFF, TIFF, PNG, JPEG, CZI, DM3, DM4, NIfTI, raw
- uses [BioFormats](https://www.openmicroscopy.org/bio-formats/) via webknossos-libs for proprietary formats

see [ome](ome.md) for format details and metadata specs.

## conversion pipeline

three repos handle the upload-to-viewable path:

| repo | role |
|------|------|
| [webknossos](https://github.com/scalableminds/webknossos) | upload UI, job dispatch, dataset serving |
| [webknossos-libs](https://github.com/scalableminds/webknossos-libs) | python: image reading, downsampling, WKW/Zarr writing |
| [voxelytics](https://scalableminds.com/voxelytics) (private) | worker service that executes jobs |

flow:
1. user uploads file via UI or API
2. webknossos detects non-native format, sets `needsConversion = true`
3. `convert_to_wkw` job created (`app/controllers/JobController.scala`), params: org, dataset name, voxel size
4. voxelytics worker picks up job, calls webknossos-libs
5. webknossos-libs reads image (tifffile for tif, PIMS/bioformats fallback), generates pyramid levels, writes output
6. converted dataset uploaded back via `DatasetUploadToPathsService`

### reader selection (webknossos-libs)

three-tier fallback in `webknossos/dataset/_utils/pims_images.py`:
1. **tifffile** (`pims_tiff_reader.py`) - default for .tif/.tiff/.ome.tif, reads via `tifffile.aszarr()`
2. **PIMS** (`pims.open()`) - generic fallback
3. **BioFormats** (`pims.BioformatsReader`) - when `use_bioformats` not False, downloads JARs automatically

### pyramid generation

downsampling in `webknossos/dataset/layer/_downsampling_utils.py`:

#### interpolation

| mode | implementation | default for |
|------|---------------|-------------|
| MEDIAN | block-reduce, numpy median per voxel group | color layers |
| MODE | block-reduce, numba-JIT most-frequent value | segmentation layers |
| NEAREST | `scipy.ndimage.zoom` order=0 | - |
| BILINEAR | `scipy.ndimage.zoom` order=1 | - |
| BICUBIC | `scipy.ndimage.zoom` order=2 | - |
| MAX | block-reduce, numpy max | - |
| MIN | block-reduce, numpy min | - |

no mean/average option. `parse_interpolation_mode()` auto-selects median for color, mode for segmentation. MEDIAN/MODE/MAX/MIN use `non_linear_filter_3d()` (reshape into factor-sized groups, reduce). NEAREST/BILINEAR/BICUBIC use `linear_filter_3d()` (scipy.ndimage.zoom wrapper).

#### mag selection (scale factors)

three sampling modes (`SamplingModes`), default is **ANISOTROPIC**:

**ANISOTROPIC** — at each step:
1. compute effective physical voxel size: `current_mag * voxel_size`
2. find smallest physical dimension(s)
3. candidate A: double all dims. candidate B: double only smallest dim(s)
4. pick whichever produces more isotropic effective voxels (lower max/min ratio)

example for anisotropic data (XY=406nm, Z=2031nm, ratio ~5x):
```
Mag(1,1,1)   -> (406, 406, 2031)nm  -> double XY only
Mag(2,2,1)   -> (812, 812, 2031)nm  -> double XY only
Mag(4,4,1)   -> (1625,1625,2031)nm  -> double all (~isotropic)
Mag(8,8,2)   -> (3250,3250,4062)nm  -> double all
```

for isotropic data (equal voxel sizes), always doubles all three dims (2,2,2).

**ISOTROPIC** — always (2,2,2) regardless of voxel size.

**CONSTANT_Z** — doubles X,Y only, Z stays fixed.

constraint: z-component between consecutive mags can only change by factor of 1 or 2.

#### stopping criterion

`calculate_default_coarsest_mag()`:
```python
coarsest_x_y = max(dataset_size[0], dataset_size[1])
coarsest_mag = max(2 ** ceil(log2(coarsest_x_y / 100)), 4)
```
target ~100 voxels per slice in largest XY dim, minimum Mag(4).

#### chunk and shard defaults

from `webknossos/dataset/defaults.py`:

| constant | value | notes |
|----------|-------|-------|
| `DEFAULT_CHUNK_SHAPE` | (32,32,32) | recommended 32 or 64 cubed |
| `DEFAULT_SHARD_SHAPE` | (1024,1024,1024) | general zarr3/wkw |
| `DEFAULT_SHARD_SHAPE_FROM_IMAGES` | (4096,4096,32) | flat-Z layout for image imports |

downsampled mags copy chunk_shape and shard_shape from mag 1 (no adaptation). `add_mag()` warns if chunks not (32,32,32) or (64,64,64). both must be powers of two.

#### processing buffer

`determine_downsample_buffer_shape()` reads min(512, shard_shape) per dim in target space, so up to 1024^3 source voxels for 2x downsampling. configurable via `buffer_shape` param.

### what metadata webknossos reads from NGFF

datastore explorers in `webknossos-datastore/app/.../explore/`:
- `NgffV0_4Explorer` reads `.zattrs` for zarr v2
- `NgffV0_5Explorer` reads `zarr.json` for zarr v3
- parses: axes (x/y/z + unit), scale/translation transforms, omero channel attributes
- mag validation: all dimensions must be power-of-two
- labels discovered at `<dataset>/labels/.zattrs`

metadata source files:
- `datareaders/zarr/NgffMetadata.scala` (v0.4)
- `datareaders/zarr/NgffMetadataV0_5.scala` (v0.5)
- `datareaders/zarr/SharedNgffMetadataAttributes.scala` (NgffAxis, NgffDataset, NgffCoordinateTransformation, channels)
- `explore/NgffExplorationUtils.scala` (axis order, voxel size calc, channel parsing)

## cli conversion

```bash
pip install --extra-index-url https://pypi.scm.io/simple "webknossos[all]"

webknossos convert \
  --layer-name em \
  --voxel-size 11.24,11.24,25 \
  --chunk-shape 64,64,64 \
  --jobs 4 \
  input.tif output.zarr

webknossos compress --jobs 4 output.zarr
webknossos downsample --jobs 4 output.zarr
```

`webknossos convert` defaults:
- `--data-format`: Zarr3 (sharded). use `--data-format zarr` for unsharded zarr v2
- `--compress`: True
- `--downsample`: True
- `--sampling-mode`: ANISOTROPIC
- `--interpolation-mode`: "default" (median for color, mode for segmentation)
- `--chunk-shape`: (32,32,32)
- `--shard-shape`: auto (4096,4096,32 for zarr3 from images)
- `--max-mag`: auto (from bounding box)

## python api

```python
import webknossos as wk

dataset = wk.Dataset.from_images(
    input_path=INPUT_DIR,
    output_path=OUTPUT_DIR,
    voxel_size=(11, 11, 11),
    layer_category=wk.COLOR_CATEGORY,
    compress=True,
)

with wk.webknossos_context(token="..."):
    dataset.upload()
```

## local dev setup

requires PostgreSQL + Redis running:

```bash
yarn install
yarn start            # dev server on port 9000
yarn enable-jobs      # enable conversion jobs (requires worker)
```

conversion jobs require a voxelytics worker with `convert_to_wkw` in `supportedJobCommands`. hosted webknossos.org has workers; local dev does not by default.

## links

- [docs](https://docs.webknossos.org/)
- [python library](https://docs.webknossos.org/python-library/)
- [webknossos-libs](https://github.com/scalableminds/webknossos-libs)
- [OME-Zarr 0.4 spec](https://ngff.openmicroscopy.org/0.4/)
- [OME-Zarr 0.5 spec](https://ngff.openmicroscopy.org/0.5/)
