---
tags:
  - ome-zarr
  - big-data-viewer
  - light-sheet
  - data-format
category: software
created: 2025-07-01
---

# OME-Zarr (BigDataViewer)

This package provides OME-Zarr reading support to bigdataviewer and BigStitcher. In addition to the OME-NGFF json metadata, a bigdataviewer `dataset.xml` dataset definition is required that refers to the image format `bdv.multimg.zarr`. Currently, two basic loader classes are provided: `XmlIoZarrImageLoader` and `ZarrImageLoader`.

The OME-NGFF layouts supported by this package is limited. Most notably:
- Only OME-NGFF v0.4. is supported.
- Only full, 5 dimensional OME-Zarr (t,ch,z,y,x axes) images are supported.
- In bigdataviewer the image is reduced to 3 dimensions at `t=0`, `ch=0`.
- In case of multiple images, all images in one `ViewSetup` must have the same data type and the same resolution levels.
- `unit` in `axes` definitions in `.zattrs` are ignored. The same units are implicitly assumed across images. Use `voxelSize` in `dataset.xml` to define physical units.
- For multi-resolution images, the first dataset defined in the `.zattrs` must be the raw (finest) resolution. Anisotropy defined for the raw resolution in `.zattrs` are ignored, use `voxelSize` in `dataset.xml` instead. Downsampling factors are determined from `coordinateTransformations` compared to the raw resolution. Only factor of 2 downsampling sequences have been tested.
- Multiple images must be located in separate zgroup folders. Only one image per top level `.zattrs` file is allowed (multiple entries in the `multiscales` section are disregarded).
