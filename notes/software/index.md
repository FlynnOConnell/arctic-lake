# Software

## Pipeline Feature Comparison

| Pipeline | 2D / 3D Registration | 2D / 3D Segmentation | Notes |
|----------|---------------------|---------------------|-------|
| [CaImAn](caiman.md) (MATLAB) | Yes, Partial | Yes, Partial | |
| [CaImAn](caiman.md) (Python) | Yes, Partial | Yes, Partial | |
| [Suite2p](suite2p.md) | Yes, No | Yes, No | |
| [EXTRACT](extract.md) | No, No | Yes, No | |
| [Suite3D](suite3d.md) | Yes, Yes | Yes, Yes | |

## Active Packages

| Package | Lab | Repository | Status |
|---------|-----|------------|--------|
| [CaImAn](caiman.md) | Flatiron | [github](https://github.com/flatironinstitute/CaImAn) | Explored - done; maintained but inactive |
| [Suite2p](suite2p.md) | Stringer Lab, Janelia | [github](https://github.com/MouseLand/suite2p) | Explored - actively developed |
| VR2P | Spruston Lab, Janelia | [vr2p-public](https://github.com/sprustonlab/vr2p-public), [OSM Paper Figures](https://github.com/sprustonlab/OSM_Paper_Figures/tree/main) | Explored - basic suite2p wrapper |
| [Rastermap](rastermap.md) | Stringer Lab, Janelia | [github](https://github.com/MouseLand/rastermap/tree/main/notebooks) | Integrated into LBM-Suite2p-Python |
| OPhysLib | Tolias Lab, Stanford | [github](https://github.com/atlab/OPhysLib) | Waiting on developer progress |
| MOSAIC-PICASSO | Tolias, Xing, NICA Labs | [atlab](https://github.com/atlab/mosaic-picasso), [xing-lab-pitt](https://github.com/xing-lab-pitt/mosaic-picasso), [NICA](https://github.com/NICALab/PICASSO) | Paused |
| [Suite3D](suite3d.md) | Carandini Lab, UCL | [github](https://github.com/alihaydaroglu/suite3d) | Preliminary exploration - tuning in progress |
| [EXTRACT](extract.md) | Schnitzer Lab, Stanford | [github](https://github.com/schnitzer-lab/EXTRACT-public) | Successfully ran - continue development |
| ActSort | Schnitzer Lab, Stanford | [github](https://github.com/schnitzer-lab/ActSort-public) | Good results - continue development |
| SUPPORT | NICA Lab, KAIST | [github](https://github.com/NICALab/SUPPORT) | Unexplored |
| deepinterpolation | Allen Institute | [github](https://github.com/AllenInstitute/deepinterpolation) | Integration pending at user request |
| CalciSeg | Yannick (Konstanz/RU 2025) | [github](https://github.com/YannickGuenzel/CalciSeg) | Unexplored |
| NeuroSeg-III | Liao Lab, Chongqing Univ. | [github](https://github.com/zimo-k/NeuroSeg3) | Unexplored |
| SUNS | Gong Lab, Duke | [github](https://github.com/YijunBao/Shallow-UNet-Neuron-Segmentation_SUNS) | Unexplored |
| AUTOTUNE | Spencer Smith Lab, UCSB | [github](https://github.com/yuyiyi/AUTOTUNE-for-Dendritic-imaging) | Difficult setup - mostly unexplored |
| CellReg | Ziv Lab, UCLA | [github](https://github.com/zivlab/CellReg/tree/master) | Planned for future |
| CASCADE | Helmchen/Friedrich Labs | [github](https://github.com/HelmchenLabSoftware/Cascade?tab=readme-ov-file) | Planned for future |
| CIATAH | Bahanonu | [ciatah site](https://bahanonu.github.io/ciatah/) | Unexplored |
| FISSA | Rochefort Lab | [github](https://github.com/rochefort-lab/fissa) | Dormant but interesting |

## Dormant or Problematic

| Package | Lab | Repository | Notes |
|---------|-----|------------|-------|
| STNeuroNet | Farsiu Lab, Duke | [github](https://github.com/soltanianzadeh/STNeuroNet) | No commits in 6 years - revisit if cited |
| FIOLA | Giovannucci, UNC | [github](https://github.com/nel-lab/FIOLA/tree/master) | Ditched - developer doubts effectiveness |
| CITE-ON | Fellin, IIT | [gitlab](https://gitlab.iit.it/fellin-public/cite-on) | Buggy - TensorFlow issues on Windows |

## Related Notes

- [cellpose](cellpose.md) - Deep learning segmentation
- [gcamp-indicators](gcamp_indicators.md) - GCaMP indicator dynamics and tau selection
- [ome](ome.md) - OME-TIFF, OME-Zarr, BigDataViewer formats
- [webknossos](webknossos.md) - 3D annotation and visualization platform
