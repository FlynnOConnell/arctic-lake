---
title: File Formats
tags: [file-formats, ome-zarr, bigdataviewer]
---

# File Formats

notes on imaging file formats for large-scale microscopy data

---

## OME-Zarr

OME-Zarr reading support for BigDataViewer and BigStitcher

requires `bdv.multimg.zarr` format reference in `dataset.xml`

### Limitations

- only OME-NGFF v0.4 supported
- only full 5D OME-Zarr (t, ch, z, y, x axes) supported
- in BDV, image reduced to 3D at t=0, ch=0
- multiple images in one ViewSetup must have same dtype and resolution levels
- `unit` in `axes` definitions ignored - use `voxelSize` in dataset.xml
- for multi-resolution, first dataset must be raw (finest) resolution
- downsampling factors from `coordinateTransformations` compared to raw
- only factor-of-2 downsampling sequences tested
- multiple images must be in separate zgroup folders
- only one image per top-level `.zattrs` file

---

## BigDataViewer XML

standard format for multi-view, multi-timepoint datasets

```xml
<SpimData>
  <BasePath type="relative">.</BasePath>
  <SequenceDescription>
    <ViewSetups>
      <ViewSetup>
        <id>0</id>
        <name>setup 0</name>
        <size>512 512 100</size>
        <voxelSize>
          <unit>µm</unit>
          <size>0.65 0.65 2.0</size>
        </voxelSize>
      </ViewSetup>
    </ViewSetups>
  </SequenceDescription>
</SpimData>
```

---

## KLB Format

used by IsoView pipeline - lossless compression optimized for microscopy

header info:
```matlab
headerInformation = readKLBheader(fullFilePath);
% xyzct: [752 2048 79 1 1]
% pixelSize: [1 1 1 1 1]
% dataType: 1
% compressionType: 1
% blockSize: [96 96 8 1 1]
```

---

## Recommended Formats by Use Case

| Use Case | Format | Notes |
|----------|--------|-------|
| archival storage | OME-Zarr | cloud-friendly, chunked |
| BigDataViewer | HDF5 or Zarr | need dataset.xml |
| Suite2p | TIFF or binary | .bin for registered data |
| CaImAn | TIFF or mmap | mmap for motion corrected |
| IsoView | KLB | lossless, fast |

---

## Resources

- [OME-NGFF spec](https://ngff.openmicroscopy.org/)
- [BigDataViewer](https://imagej.net/plugins/bdv/)
- [Janelia File Format Guidelines](https://datastandards.janelia.org/posts/file_formats_introduction.html)
- [MATLAB Zarr Support](https://github.com/mathworks/MATLAB-support-for-Zarr-files)
- [cpp-tiff](https://github.com/abcucberkeley/cpp-tiff)
- [cpp-zarr](https://github.com/abcucberkeley/cpp-zarr)

---

## Links

- [[calcium-imaging]] - main index
- [[isoview]] - uses KLB format
