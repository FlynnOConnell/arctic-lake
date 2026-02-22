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
updated: 2026-02-22
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

see [[ome]] for format details and metadata specs.

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
- power-of-2 scaling, generates levels until slices reach ~100 vx^2
- color layers: median interpolation (default)
- segmentation layers: mode interpolation (default)
- anisotropic-aware: selectively doubles smallest dimension to balance aspect ratios
- modes: MEDIAN, MODE, NEAREST, BILINEAR, BICUBIC, MAX, MIN

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
