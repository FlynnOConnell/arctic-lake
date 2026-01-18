---
title: Suite2p
tags: [calcium-imaging, suite2p]
---

# Suite2p

[github](https://github.com/MouseLand/suite2p) | [docs](https://suite2p.readthedocs.io)

actively developed by Stringer Lab at Janelia

---

## Key Parameters

| Parameter | Description | Notes |
|-----------|-------------|-------|
| `tau` | decay time constant | fixed, not scaled with frame-rate |
| `block_size` | registration block size | tweak if black background affects registration |
| `spatial_taper` | taper for registration | |
| `max_overlap` | overlapping ROIs | |
| `threshold_scaling` | detection threshold | lower for dim signals |

### Recommended `tau` Values
- GCaMP6f: 0.7
- GCaMP6m: 1.0
- GCaMP6s: 1.25-1.5
- GCaMP8f: 0.1 (for fast data)

---

## Helpful GitHub Issues

| Issue | Topic |
|-------|-------|
| [#921](https://github.com/MouseLand/suite2p/issues/921) | black background affects registration; tweak `block_size`/`spatial_taper` |
| [#880](https://github.com/MouseLand/suite2p/issues/880) | running on cluster |
| [#851](https://github.com/MouseLand/suite2p/issues/851) | overlapping ROIs and `ops['max_overlap']` |
| [#837](https://github.com/MouseLand/suite2p/issues/837) | `tau` controls temporal binning |
| [#787](https://github.com/MouseLand/suite2p/issues/787) | `threshold_scaling` for dim signals |
| [#690](https://github.com/MouseLand/suite2p/issues/690) | multi-channel registration |
| [#627](https://github.com/MouseLand/suite2p/issues/627) | F and Fneu meaning |
| [#758](https://github.com/MouseLand/suite2p/issues/758#issuecomment-956588935) | looping over DBs on cluster |
| [#795](https://github.com/MouseLand/suite2p/issues/795) | zarr vs NWB |
| [#750](https://github.com/MouseLand/suite2p/issues/750) | GCaMP8f, `tau=0.1` for fast data |
| [#730](https://github.com/MouseLand/suite2p/issues/730) | max image brightness vs `tau` |
| [#667](https://github.com/MouseLand/suite2p/issues/667) | 4D TIFFs, `sparse_mode` toggle |
| [#530](https://github.com/MouseLand/suite2p/issues/530) | units of `F` and `spks` |

[YouTube: ROI detection explainer](https://youtu.be/NcC0YxQ9o3A)

---

## F and Fneu

- `F`: raw fluorescence trace from ROI
- `Fneu`: neuropil fluorescence (surrounding ring)
- corrected trace: `F - 0.7 * Fneu` (default neuropil coefficient)
- `spks`: deconvolved spike estimates

---

## Links

- [[calcium-imaging]] - main index
- [[caiman]] - alternative pipeline
- [[suite3d]] - 3D extension
