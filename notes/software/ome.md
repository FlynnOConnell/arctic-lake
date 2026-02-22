---
tags:
  - ome-tiff
  - ome-zarr
  - ngff
  - data-format
  - bioformats
category: software
created: 2025-07-01
updated: 2026-02-22
---

# OME

open microscopy environment formats for large-scale imaging data

## ome-tiff

tiff container with ome-xml metadata in the first IFD's `IMAGE_DESCRIPTION` tag (270). supports multi-series, multi-resolution, multi-channel.

### structure

each full-resolution plane is a main IFD. pyramid levels are stored as SubIFDs (tag 330) hanging off each main IFD:

```
main IFD chain:
  IFD 0 (full-res plane 0)  ->  SubIFD[0]: 2x downsample
                                 SubIFD[1]: 4x downsample
                                 SubIFD[2]: 8x downsample
  IFD 1 (full-res plane 1)  ->  SubIFD[0]: 2x downsample
                                 ...
```

- SubIFDs ordered largest to smallest resolution
- each sub-resolution IFD sets `NewSubFileType` (254) bit 0 = 1
- SubIFD offsets must not appear in the main IFD chain
- generate power-of-two reductions until smallest X or Y <= 256 px
- SubIFDs only reduce X/Y, not Z/C/T

### key IFD tags

| tag | id | notes |
|-----|----|-------|
| IMAGE_WIDTH | 256 | pixel width |
| IMAGE_LENGTH | 257 | pixel height |
| BITS_PER_SAMPLE | 258 | bits per channel |
| COMPRESSION | 259 | codec (LZW=5, JPEG=7, DEFLATE=8, ZSTD=50000) |
| IMAGE_DESCRIPTION | 270 | holds OME-XML in OME-TIFF files |
| NEW_SUBFILE_TYPE | 254 | 1 = reduced-resolution image |
| SUB_IFD | 330 | array of offsets to sub-resolution IFDs |
| TILE_WIDTH/LENGTH | 322/323 | tile dimensions |
| SAMPLE_FORMAT | 339 | 1=unsigned, 2=signed, 3=float |

### ome-xml metadata

embedded in IMAGE_DESCRIPTION. dimensions from `Pixels` element: `SizeX`, `SizeY`, `SizeZ`, `SizeC`, `SizeT`, `Type`, `DimensionOrder`. `TiffData` elements map planes to IFD indices. multi-file datasets use UUID references.

### writing pyramidal ome-tiff (python)

```python
import numpy as np
import tifffile

data = ...  # shape (Z, Y, X) or (C, Z, Y, X)
num_levels = 3

with tifffile.TiffWriter("output.ome.tif", bigtiff=True) as tif:
    tif.write(data, subifds=num_levels, tile=(256, 256), compression="zlib")
    for level in range(num_levels):
        factor = 2 ** (level + 1)
        downsampled = data[..., ::factor, ::factor]
        tif.write(downsampled, subfiletype=1, tile=(256, 256), compression="zlib")
```

for large files, use tiled reading/writing instead of loading the full array.

### bioformats

java library (`ome/bioformats`, 150+ formats). key classes:

- `OMETiffReader` reads ome-tiff, discovers pyramids via `TiffParser.getSubIFDs()`
- `PyramidOMETiffWriter` writes pyramidal ome-tiff with SubIFD patching on `close()`
- `CoreMetadata` holds per-series dimensions: sizeX/Y/Z/C/T, pixelType, resolutionCount
- bioformats does not auto-downsample; caller provides pre-downsampled data per resolution

cli: `bfconvert -pyramid-scale 2 -pyramid-resolutions 4 -tilex 512 -tiley 512 -bigtiff input.tif output.ome.tif`

### reading ome-tiff in python

- **tifffile** (default) - reads via `tifffile.aszarr()` for chunked access. handles ome-xml parsing natively.
- **bioformats via PIMS** - `pims.BioformatsReader`, launches JVM. only needed for proprietary formats.
- **webknossos-libs** uses tifffile as primary, falls back to PIMS then bioformats (`pims_images.py` three-tier strategy).

## ome-zarr

zarr container with ngff metadata. default format for webknossos.

### folder structure (v0.4)

```
dataset.zarr/
├── .zgroup
├── .zattrs               # multiscales + omero metadata
├── 0/                    # full resolution
│   ├── .zarray
│   └── t/c/z/y/x         # chunk files
├── 1/                    # 2x downsample
├── n/                    # further levels
└── labels/
    ├── .zattrs           # {"labels": ["original/0"]}
    └── original/0/
        ├── .zattrs       # image-label metadata
        └── 0..n/         # multiscale levels
```

### folder structure (v0.5 / zarr3)

```
dataset.zarr/
├── zarr.json             # zarr_format: 3, node_type: "group", ome metadata
├── 0..n/
│   ├── zarr.json         # array metadata
│   └── ...               # chunks
└── labels/
    ├── zarr.json
    └── original/0/
        ├── zarr.json
        └── 0..n/
```

### ngff metadata (what webknossos parses)

```json
{
  "multiscales": [{
    "version": "0.4",
    "name": "layer_name",
    "axes": [
      {"name": "c", "type": "channel"},
      {"name": "x", "type": "space", "unit": "nanometer"},
      {"name": "y", "type": "space", "unit": "nanometer"},
      {"name": "z", "type": "space", "unit": "nanometer"}
    ],
    "datasets": [
      {"path": "1", "coordinateTransformations": [{"type": "scale", "scale": [1.0, 11.24, 11.24, 28.0]}]},
      {"path": "2", "coordinateTransformations": [{"type": "scale", "scale": [1.0, 22.48, 22.48, 28.0]}]}
    ]
  }],
  "omero": {
    "channels": [{"color": "FF0000", "label": "ch0", "window": {"min": 0, "max": 255, "start": 0, "end": 255}}]
  }
}
```

- `axes` must include x, y (z optional) with `type: "space"`. unit maps to LengthUnit.
- `datasets[].coordinateTransformations` scale transforms determine mag factor. must be power-of-two ratios.
- `omero.channels[]` sets color, label, intensity window, inverted, active.
- labels discovered at `<dataset>/labels/.zattrs`

### bigdataviewer integration

bdv ome-zarr support requires `dataset.xml` referencing `bdv.multimg.zarr` format.

limitations:
- only NGFF v0.4
- only full 5D (t, ch, z, y, x)
- in BDV, reduced to 3D at t=0, ch=0
- `unit` in axes ignored, use `voxelSize` in dataset.xml
- first dataset must be finest resolution
- only factor-of-2 downsampling tested
- one image per top-level `.zattrs`

### generating pyramids

**webknossos cli:**

```bash
pip install --extra-index-url https://pypi.scm.io/simple "webknossos[all]"
webknossos convert --layer-name em --voxel-size 11.24,11.24,25 --chunk-shape 64,64,64 --jobs 4 input.tif output.zarr
webknossos compress --jobs 4 output.zarr
webknossos downsample --jobs 4 output.zarr
```

creates sharded zarr v3. use `--data-format zarr` for unsharded zarr v2.

**webknossos python:**

```python
import webknossos as wk

dataset = wk.Dataset.from_images(
    input_path=INPUT_DIR,
    output_path=OUTPUT_DIR,
    voxel_size=(11, 11, 11),
    layer_category=wk.COLOR_CATEGORY,
    compress=True,
)
dataset.upload()
```

**other tools:**
- [ome-zarr-py](https://github.com/ome/ome-zarr-py) - `ome_zarr.writer.write_image` with scaler for pyramid generation
- [ngff-zarr](https://github.com/fideus-labs/ngff-zarr) - `to_multiscales()` for dask-based pyramid, supports v0.4-v0.5
- `bioformats2raw` + `raw2ometiff` for java-based conversion

### format recommendation

| use case | format | notes |
|----------|--------|-------|
| archival storage | OME-Zarr | cloud-friendly, chunked |
| BigDataViewer | HDF5 or Zarr | needs dataset.xml |
| Suite2p | TIFF or binary | .bin for registered data |
| CaImAn | TIFF or mmap | mmap for motion corrected |
| IsoView | KLB | lossless, fast |

### performance tips

- chunk sizes: 32-128 voxels^3
- enable sharding (zarr 3+ only)
- use 3D downsampling
- n-dimensional (4D+ time series) only supported in zarr, not wkw

## resources

- [OME-NGFF spec](https://ngff.openmicroscopy.org/)
- [OME-TIFF spec](https://ome-model.readthedocs.io/en/stable/ome-tiff/specification.html)
- [OME-TIFF sub-resolution design (OME005)](http://ome.github.io/design/OME005/)
- [tifffile](https://pypi.org/project/tifffile/)
- [bioformats](https://www.openmicroscopy.org/bio-formats/)
- [ome-zarr-py](https://github.com/ome/ome-zarr-py)
- [ngff-zarr](https://github.com/fideus-labs/ngff-zarr)
- [ome-tiff-pyramid-tools](https://github.com/labsyspharm/ome-tiff-pyramid-tools)
- [webknossos python library](https://docs.webknossos.org/python-library/)
- [cpp-tiff](https://github.com/abcucberkeley/cpp-tiff)
- [cpp-zarr](https://github.com/abcucberkeley/cpp-zarr)
