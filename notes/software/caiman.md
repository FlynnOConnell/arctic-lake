---
title: CaImAn
tags: [calcium-imaging, caiman, cnmf]
---

# CaImAn

[github](https://github.com/flatironinstitute/CaImAn) | [docs](https://caiman.readthedocs.io)

## pipeline steps

1. spatial downsampling
2. frequency filter / FFT
3. normcorre motion correction
4. cnmfe
5. extract dF/F
6. event detection (if necessary)

---

## normcorre: matlab vs python

| feature | matlab | python |
|---------|--------|--------|
| online template updating | yes | no |
| available shifts | FFT, cubic linear | FFT, cubic |
| handles 3D data | yes | no |
| optical flow calculation | no | yes |
| FFT windowing | yes | no |
| parallelization | per mini batch, different frames | different mini batches |
| grid size variable | `grid_size` | `strides` |
| overlap included in grid | no | yes |
| patch size | `grid_size + 2×overlap` | `strides + overlap` |
| phase correlation | yes | no |
| bidirectional scan offset | yes | no |

---

## key parameters

### motion correction
```python
max_shifts = (6, 6)      # maximum shift in pixels
strides = (48, 48)       # patch size for pw-rigid
overlaps = (24, 24)      # patch overlap
pw_rigid = True          # piecewise-rigid correction
gSig_filt = (2, 2)       # gaussian filter for template
border_nan = "copy"      # how to handle borders
```

### cnmf
```python
K = 50                   # expected number of neurons
gSig = (4, 4)            # expected neuron half-width in pixels
p = 1                    # order of AR model for calcium dynamics
merge_thresh = 0.8       # merging threshold
min_SNR = 2.5            # minimum SNR for accepting components
rval_thr = 0.85          # correlation threshold
decay_time = 0.4         # length of typical transient (seconds)
method_init = "greedy_roi"
```

---

## quantitative registration

smoothness metric:
```python
np.gradient(np.mean(m, 0))  # gradient of mean image
```

sum of squared gradients measures pixel-to-pixel variation

---

## lbm-caiman-python

our wrapper for lbm data processing

```python
import lbm_caiman_python as lcp

# simple usage
results = lcp.pipeline("data.tiff", "output/")

# with options
results = lcp.pipeline(
    input_data="data/",
    save_path="results/",
    ops=lcp.default_ops(),
    planes=[1, 2, 3],
    force_mcorr=True,
)

# access results
for ops_path in results:
    ops = lcp.load_ops(ops_path)
    print(f"Plane {ops['plane']}: {ops['n_cells']} cells")
```

---

## links

- [[calcium-imaging]] - main index
- [[suite2p]] - alternative pipeline
