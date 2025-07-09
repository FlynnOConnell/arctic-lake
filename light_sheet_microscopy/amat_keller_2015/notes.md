[nature](https://www.nature.com/articles/nprot.2015.111)
[[light_sheet_microscopy/amat_keller_2015/paper]]


## Key Takeaways
- 5 modules described in [[light_sheet_microscopy/lemon_keller_2015/notes|Lemon et. al., 2015]]
- CATMAID + Imaris
- tested on fruit fly, zebrafish, mouse embryo
- Algorithms used with confocal, commercial light sheet
- Requires fast retrieval of ROI, region of the FOV
- Largely describes performance of KLB file format

[![figure 3](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_Fig3_HTML.jpg)](https://www.nature.com/articles/nprot.2015.111/figures/3|400)
[![figure 4](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_Fig4_HTML.jpg)](https://www.nature.com/articles/nprot.2015.111/figures/4)
## Comparisons
- plane-by-plane is insufficient - can't retrieve arbitrary rois
- JPEG is lossless, few 3D compression solutiions
- HDF5: no parallel write

## Multi-view Image Fusion
Initial method is provided as a fiji plugin:
- embedded fluor beads surrounding the sample
- detects blobs via difference of gaussians
- **new** method does not depend on the type of label.
- assumes orthogonal views (main limitation)
- advantages:
	- works with large specimin, high magnification
	- easier prep: don't need to embed in agarose or similar matrix
	- compensate (partially) for light-refraction (how)

## Table 1: Computation Time 

| Computational Module | Description                                                                            | Computation Time (s)     | Time per Time Point (s) |
| -------------------- | -------------------------------------------------------------------------------------- | ------------------------ | ----------------------- |
| **clusterPT.m**      | • sCMOS image correction  <br> • Background masking  <br> • KLB lossless compression   | 8.36 per time point      | 8.36                    |
| **clusterMF.m**      | • Multiview registration  <br> • Multiview image fusion                                | 19.49 per 10 time points | 1.95                    |
| **localAP.m**        | • Parameter interpolation                                                              | 5.09 per experiment      | 0.04                    |
| **clusterTF.m**      | • Multiview image fusion                                                               | 7.88 per time point      | 7.88                    |
| **ProcessStack**     | • Hierarchical segmentation                                                            | 2.73 per time point      | 2.73                    |
| **TGMM**             | • Cell tracking  <br> • Detection of cell divisions  <br> • Filtering of cell lineages | 8.29 per time point      | 8.29                    |

## Table 2: Memory Requirements

| Computational Module | Module Configuration | Estimated Memory Consumption |
|----------------------|----------------------|------------------------------|
| **clusterPT.m**      | • sCMOS image correction <br> rotationFlag = 0 | 1.2 × (2n + 2) × S |
|                      | • Background masking <br> • KLB lossless compression <br> rotationFlag ≠ 0 | Up to 1.2 × (2n + 4) × S |
| **clusterMF.m**      | • Multiview registration <br> Wavelet fusion, 4 views | 13.2 × S |
|                      | • Multiview image fusion <br> Wavelet fusion, 2 views | Up to 10.8 × S |
|                      | Other fusion, 4 views | 9.6 × S |
|                      | Other fusion, 2 views | Up to 8.4 × S |
| **clusterTF.m**      | • Multiview image fusion <br> Wavelet fusion, 4 views | 9.6 × S |
|                      | Wavelet fusion, 2 views | 7.2 × S |
|                      | Other fusion, 4 views | 6.0 × S |
|                      | Other fusion, 2 views | 3.6 × S |
| **clusterCS.m**      | • 3D drift correction <br> • Intensity normalization <br> All settings | 5.5 × S |
| **clusterFR.m**      | • Local background correction <br> All settings | 3.6 × S |

## Image Segmentation

- Most previous methods made for **small organisms**
- Joint segmentation and cell tracking
	- Why do you need this as joint operations?
	- Needs to maintain scalability to big cell counts
- TGMM software scales linearly with n-neurons

***Critical Factor: temporal sampling in the time-lapse data, slightly critical is image quality and cell density***

## Data Visualization
Their software uses a branch of CATMAID
- OMERO for data organization
- gFigure2 -> VTK library (for rendering)
- CATMAIN - similar to goFigure2
- Imaris (Bitplane)
	- forces large hdf5 which is slow for multiTB datasets
- Imaris/goFigure2 allow only a single user to access data

**Figure 6: Image annotation and editing of cell-lineage data using CATMAID.**

[![figure 6](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_Fig6_HTML.jpg)](https://www.nature.com/articles/nprot.2015.111/figures/6)

### More software
- Arivis Visian 4D
- Amira
- Vaa3D
- BigDataViewer

CATMAID requires setting up an HTTP sever + PostgreSQL database.

## Limitations
- Cannot correct drift larger than the radius of the blob