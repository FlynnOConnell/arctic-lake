---
tags:
  - ome-zarr
  - ngff
  - webknossos
  - visualization
  - calcium-imaging
  - data-format
category: software
created: 2026-01-16
source: https://docs.webknossos.org/data-sources/ome-zarr
---

# WEBKNOSSOS - OME-Zarr & NGFF

WEBKNOSSOS works great with OME-Zarr datasets (next-generation file format / NGFF). Zarr is the default data format in WEBKNOSSOS and replaced the previous WKW format.

Zarr datasets can be:
- Uploaded through the web uploader
- Streamed from a remote server or cloud
- When streaming multiple layers, import the first Zarr group then add more URIs via UI

## Example Datasets

Load as remote dataset in WEBKNOSSOS:

- **Mouse Cortex Layer 4 EM Cutout**
  - URL: `https://static.webknossos.org/data/l4_sample/`
  - Source: *Dense connectomic reconstruction in layer 4 of the somatosensory cortex.* Motta et al. Science 2019. DOI: 10.1126/science.aay3134

## Zarr Folder Structure (v0.4)

```
.                             # root folder
└── 456.zarr                  # image converted to Zarr
    ├── .zgroup               # zarr group
    ├── .zattrs               # group attributes: "multiscales", "omero"
    ├── 0/                    # multiscale level 0
    │   ├── .zarray           # up to 5D: time > channel > spatial
    │   └── t/c/z/y/x         # chunk files (nested directory layout)
    ├── n/                    # multiscale level n
    └── labels/
        ├── .zgroup
        ├── .zattrs           # e.g. { "labels": [ "original/0" ] }
        └── original/0/       # labeled image
            ├── .zgroup
            ├── .zattrs       # "image-label" metadata
            └── 0..n/         # multiscale levels (integer values only)
```

## Zarr Folder Structure (v0.5)

```
└── 456.zarr
    ├── zarr.json             # group attributes
    ├── 0..n/                 # multiscale levels
    │   ├── zarr.json         # array metadata
    │   └── ...               # chunks per zarr spec
    └── labels/
        ├── zarr.json         # labels list
        └── original/0/
            ├── zarr.json
            └── 0..n/
```

## CLI Conversion

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

Creates sharded Zarr v3. Use `--data-format zarr` for unsharded Zarr v2.

## Python Conversion

```python
import webknossos as wk

def main() -> None:
    dataset = wk.Dataset.from_images(
        input_path=INPUT_DIR,
        output_path=OUTPUT_DIR,
        voxel_size=(11, 11, 11),
        layer_category=wk.COLOR_CATEGORY,
        compress=True,
    )
    print(f"Saved {dataset.name} at {dataset.path}.")

    with wk.webknossos_context(token="..."):
        dataset.upload()

if __name__ == "__main__":
    main()
```

## Time-Series / N-Dimensional

WEBKNOSSOS supports n-dimensional datasets (e.g., 4D time series). Currently only for Zarr due to flexible structure.

## Performance Tips

- Chunk sizes: 32-128 voxels^3
- Enable sharding (Zarr 3+ only)
- Use 3D downsampling

## Links

- [WEBKNOSSOS Docs](https://docs.webknossos.org/)
- [OME-Zarr 0.4 Spec](https://ngff.openmicroscopy.org/0.4/)
- [OME-Zarr 0.5 Spec](https://ngff.openmicroscopy.org/0.5/)
- [Python Library](https://docs.webknossos.org/python-library/)
