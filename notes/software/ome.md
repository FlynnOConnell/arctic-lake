---
tags:
  - ome-tiff
  - ome-zarr
  - ngff
  - data-format
  - bioformats
category: software
created: 2025-07-01
updated: 2026-02-23
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

java library (`ome/bioformats`, 150+ formats). standalone - does not depend on webknossos.

#### architecture

- `ImageReader` is the master delegator, tries each reader in `readers.txt` order
- all readers extend `FormatReader` -> `IFormatReader`; writers extend `FormatWriter`
- optional dependencies (ome-xml, jhdf, netcdf) accessed via `ServiceFactory` / `IService` pattern
- wrapper/decorator pattern: `ChannelSeparator`, `ChannelMerger`, `DimensionSwapper`, `Memoizer`, `FileStitcher`

#### metadata flow

readers populate two things:
1. **CoreMetadata** - per-series/per-resolution: sizeX/Y/Z/C/T, pixelType, bitsPerPixel, dimensionOrder, resolutionCount, littleEndian, interleaved, rgb, indexed
2. **MetadataStore** (OME-XML) - via `OMEXMLService.createOMEXMLMetadata()`. `MetadataTools.populatePixels()` transfers CoreMetadata into OME-XML Pixels element.

ome data model lives in a separate repo (`org.openmicroscopy`): `ome-xml` (v6.5.3), `specification` (v6.5.3), `ome-common` (v6.2.0).

#### reading tiff (how bfconvert reads your file)

`MinimalTiffReader.initFile()`:
1. `TiffParser` validates magic bytes, detects endianness and BigTIFF
2. reads all IFDs via `getIFDOffsets()`, filters thumbnails
3. IFDs with different dimensions/bit depths become separate series
4. populates CoreMetadata from IFD tags: WIDTH->sizeX, LENGTH->sizeY, sizeZ=1 (default), sizeT=numIFDs

`TiffReader` then refines from IMAGE_DESCRIPTION:
- imagej-style: `slices=N`->sizeZ, `frames=N`->sizeT, `channels=N`->sizeC
- metamorph xml, generic ini-style also parsed
- physical pixel sizes from X/Y_RESOLUTION tags (282/283), normalized to microns

#### pixel type mapping

| BITS_PER_SAMPLE | SAMPLE_FORMAT | result |
|-----------------|---------------|--------|
| 1-8 | unsigned (1) | UINT8 |
| 1-8 | signed (2) | INT8 |
| 16 | unsigned | UINT16 |
| 16 | signed | INT16 |
| 16 | float (3) | FLOAT |
| 32 | unsigned | UINT32 |
| 32 | signed | INT32 |
| 32 | float | FLOAT |
| 64 | float | DOUBLE |

non-byte-aligned bit depths (e.g. 12-bit) rounded up. 24-bit integer promoted to 32-bit.

#### pyramid support

- `SubResolutionFormatReader` base class, stores `CoreMetadataList[series][resolution]`
- `IPyramidHandler`: `getResolutionCount()`, `setResolution(int)`, `getResolution()`. index 0 = full resolution.
- `OMETiffReader.addSubResolutions()` reads SUB_IFD tag, creates metadata per sub-resolution from SubIFD dimensions
- `Resolution.java`: `sizeX = fullX / pow(scale, index)`, typical scale=2
- bioformats does **not** auto-downsample; caller must provide pre-downsampled pixel data

#### writing pyramidal ome-tiff

`PyramidOMETiffWriter` extends `OMETiffWriter`:
- resolution 0 gets `SUB_IFD = 0` placeholder
- resolution >0 gets `NEW_SUBFILE_TYPE = 1`
- on `close()`: collects IFD offsets, patches each main IFD's SUB_IFD tag with actual sub-resolution offsets via `TiffSaver.overwriteIFDValue()`
- ome-xml finalized on close: removes stale BinData/TiffData, builds new TiffData elements with plane->IFD mappings, writes via `TiffSaver.overwriteComment()`

IFD index accounting: `index = (planeNo * resolutionCount) + resolution`

#### tiff infrastructure

all in `formats-bsd/src/loci/formats/tiff/`:
- `TiffParser` - reads structure, supports BigTIFF (magic 43). `getSamples()` reads rectangular regions across tiles, handles decompression.
- `TiffSaver` - writes data. `overwriteComment()` surgically replaces IMAGE_DESCRIPTION without rewriting.
- `TiffCompression` - LZW, JPEG, DEFLATE, ZSTD(50000), JPEG2000, etc.

tile reading: `getSamples(ifd, buf, x, y, w, h)` calculates tile grid, iterates intersecting tiles, decompresses and copies overlap regions. handles photometric inversion (WHITE_IS_ZERO, CMYK, YCbCr).

#### cli usage

```bash
# inspect
showinf input.tif

# convert with pyramids
bfconvert -pyramid-scale 2 -pyramid-resolutions 4 -tilex 512 -tiley 512 -bigtiff input.tif output.ome.tif

# other flags: -compression LZW, -series 0, -channel 0, -z 0, -timepoint 0, -crop x,y,w,h
```

#### programmatic (java)

```java
ImageReader reader = new ImageReader();
reader.setMetadataStore(service.createOMEXMLMetadata());
reader.setId("input.tiff");

OMETiffWriter writer = new OMETiffWriter();
writer.setMetadataRetrieve((MetadataRetrieve) reader.getMetadataStore());
writer.setId("output.ome.tiff");

for (int i = 0; i < reader.getImageCount(); i++) {
    writer.saveBytes(i, reader.openBytes(i));
}
writer.close();
reader.close();
```

see `formats-gpl/utils/WritePyramid.java` for a complete pyramid writing example.

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
├── zarr.json             # zarr_format: 3, node_type: "group", ome metadata in attributes
├── 0/
│   ├── zarr.json         # array metadata (shape, codecs, sharding config)
│   └── c/                # sharded chunk storage
│       └── 0/0/0         # shard files (each contains multiple inner chunks)
├── 1/                    # 2x downsample
│   ├── zarr.json
│   └── c/
├── n/                    # further levels
└── labels/
    ├── zarr.json
    └── original/0/
        ├── zarr.json
        └── 0..n/
```

### zarr v3 sharding

sharding groups multiple chunks into single storage objects, reducing file count for large arrays. zarr v3 only.

array-level `zarr.json` with sharding:
```json
{
  "zarr_format": 3,
  "node_type": "array",
  "shape": [100, 256, 256],
  "data_type": "uint16",
  "chunk_grid": {
    "name": "regular",
    "configuration": {"chunk_shape": [64, 256, 256]}
  },
  "codecs": [{
    "name": "sharding_indexed",
    "configuration": {
      "chunk_shape": [64, 64, 64],
      "codecs": [
        {"name": "bytes", "configuration": {"endian": "little"}},
        {"name": "blosc", "configuration": {"cname": "zstd", "clevel": 3, "shuffle": "bitshuffle"}}
      ],
      "index_codecs": [
        {"name": "bytes", "configuration": {"endian": "little"}},
        {"name": "crc32c"}
      ],
      "index_location": "end"
    }
  }]
}
```

terminology:
- **outer chunk** (shard): the storage unit, stored as one file under `c/`
- **inner chunk**: individually addressable sub-chunk within a shard
- `chunk_grid.chunk_shape` = outer (shard) dimensions
- `sharding_indexed.chunk_shape` = inner chunk dimensions
- shard index at end of file maps inner chunk offsets

webknossos defaults: inner (32,32,32), outer/shard (1024,1024,1024) general or (4096,4096,32) from images.

### ngff metadata

#### v0.4 (zarr v2, stored in `.zattrs`)

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

#### v0.5 (zarr v3, stored in `zarr.json` -> `attributes`)

```json
{
  "zarr_format": 3,
  "node_type": "group",
  "attributes": {
    "multiscales": [{
      "version": "0.5",
      "name": "volume",
      "axes": [
        {"name": "z", "type": "space", "unit": "micrometer"},
        {"name": "y", "type": "space", "unit": "micrometer"},
        {"name": "x", "type": "space", "unit": "micrometer"}
      ],
      "datasets": [
        {"path": "0", "coordinateTransformations": [{"type": "scale", "scale": [0.406, 0.406, 0.406]}]},
        {"path": "1", "coordinateTransformations": [{"type": "scale", "scale": [0.406, 0.812, 0.812]}]},
        {"path": "2", "coordinateTransformations": [{"type": "scale", "scale": [0.406, 1.625, 1.625]}]}
      ]
    }],
    "omero": {
      "channels": [{"active": true, "color": "00FF00", "label": "488nm",
        "window": {"start": 0, "end": 65535, "min": 0, "max": 65535}}],
      "rdefs": {"defaultT": 0, "defaultZ": 0, "model": "greyscale"}
    }
  }
}
```

key differences from v0.4: metadata lives inside `attributes` key (not top-level), `version: "0.5"`, units typically `"micrometer"` not `"nanometer"`.

#### parsing rules

- `axes` must include x, y (z optional) with `type: "space"`. unit maps to LengthUnit.
- `datasets[].coordinateTransformations` scale transforms determine mag factor. must be power-of-two ratios.
- `omero.channels[]` sets color, label, intensity window, inverted, active.
- labels discovered at `<dataset>/labels/.zattrs` (v0.4) or `labels/zarr.json` (v0.5)
- webknossos: `NgffV0_4Explorer` reads `.zattrs`, `NgffV0_5Explorer` reads `zarr.json`

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

### writing pyramidal ome-zarr v3 (python)

```python
import numpy as np
import zarr
from zarr.codecs import BloscCodec

data = ...  # shape (Z, Y, X), uint16
store = zarr.storage.LocalStore("output.zarr")

# write full resolution with sharding
chunks = (64, 64, 64)
shards = (64, 512, 512)  # outer shard, must be multiple of chunks
compressors = [BloscCodec(cname="zstd", clevel=3, shuffle="bitshuffle")]

zarr.create_array(
    store=store, name="0", shape=data.shape, dtype=data.dtype,
    chunks=chunks, shards=shards, compressors=compressors,
    zarr_format=3, overwrite=True,
)[:] = data

# write pyramid levels
for level in range(1, 4):
    factor = 2 ** level
    downsampled = data[..., ::factor, ::factor]  # or proper block-reduce
    zarr.create_array(
        store=store, name=str(level), shape=downsampled.shape, dtype=data.dtype,
        chunks=chunks, shards=shards, compressors=compressors,
        zarr_format=3, overwrite=True,
    )[:] = downsampled

# write NGFF v0.5 group metadata
root = zarr.open_group(store=store, mode="a", zarr_format=3)
root.attrs["multiscales"] = [{
    "version": "0.5",
    "axes": [
        {"name": "z", "type": "space", "unit": "micrometer"},
        {"name": "y", "type": "space", "unit": "micrometer"},
        {"name": "x", "type": "space", "unit": "micrometer"},
    ],
    "datasets": [
        {"path": str(i), "coordinateTransformations": [
            {"type": "scale", "scale": [dz, dy * 2**i, dx * 2**i]}
        ]} for i in range(4)
    ],
}]
```

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

- chunk sizes: 32-64 voxels^3 (webknossos default 32^3)
- enable sharding for zarr v3: reduces file count, enables range-request access
- webknossos shard defaults: (1024,1024,1024) general, (4096,4096,32) for image imports
- use anisotropic downsampling when Z spacing differs from XY
- n-dimensional (4D+ time series) only supported in zarr, not wkw
- blosc-zstd with bitshuffle is the standard compression for microscopy data

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
