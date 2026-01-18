---
tags:
  - caiman
  - calcium-imaging
  - cnmf
  - motion-correction
  - normcorre
category: software
created: 2025-09-18
---

# CaImAn

Calcium Imaging Analysis - motion correction and source extraction for calcium imaging data.

[github](https://github.com/flatironinstitute/CaImAn) | [docs](https://caiman.readthedocs.io)

## Pipeline Overview

1. Spatial downsampling
2. Frequency Filter / FFT
3. NormCorre Motion Correction
4. CNMFe
5. Extract dF/F
6. Event Detection, if necessary

## NormCorre: MATLAB vs Python

| Feature/Property | MATLAB | Python |
|------------------|--------|--------|
| online template updating | Yes | No |
| available shifts | FFT, cubic linear | FFT, cubic |
| handles 3D data | Yes | No |
| optical flow calculation | No | Yes |
| FFT windowing | Yes | No |
| parallelization method | for each mini batch process different frames in parallel | process different mini batches in parallel |
| variable for grid size | `grid_size` | `strides` |
| overlap included in grid size | No | Yes |
| total size of each patch | `grid_size + 2*overlap` | `strides + overlap` |
| option for phase correlation | Yes | No |
| offset correction due to bidirectional scanning | Yes | No |

## When to Use 3D vs 2D Registration

Use **3D registration** when:
- ROIs span across adjacent z-planes
- z-motion is comparable to inter-plane spacing

Use **2D registration per plane** when:
- z-motion is minimal or planes are far apart
- Forcing uniform x-y motion degrades results

## LBM-CaImAn-Python

### Quantitative Registration

Smoothness metric:
```python
np.gradient(np.mean(m, 0))  # gradient of mean image
```

- Sum of squared gradients measures pixel-to-pixel variation

## 3D Segmentation

[PNAS: Spatiotemporal UNet paper](https://www.pnas.org/doi/10.1073/pnas.1812995116)

- 3D UNet, outperforming CNMF/Suite2p
- Temporal max pooling, 120-frame batches
- CNMF background = low-rank model - can fail with dynamic background
- Demo notebook (Flatiron): [demo_caiman_cnmf_3D.ipynb](https://github.com/flatironinstitute/CaImAn/blob/CNMF_3D/demos/notebooks/demo_caiman_cnmf_3D.ipynb)

### Notes from Johannes

- Branch in CaImAn repo with unmerged 3D motion correction
- Anisotropy = common, affects `gSig`, `strides`, `overlap`
- Watch out for memory overload due to `A` matrix size if too many neurons / low FPS

## Parameters

[CaImAn parameters documentation](https://caiman.readthedocs.io/en/latest/Getting_Started.html#parameters)

- `decay_time`: Length of typical transient in seconds
  - Default is `0.4`, appropriate for fast sensors (GCaMP6f)
  - Slow sensors may use 1 or more

## References

- [CaImAn GitHub](https://github.com/flatironinstitute/CaImAn)
- [CaImAn Documentation](https://caiman.readthedocs.io)
