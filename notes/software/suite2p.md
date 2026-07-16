---
tags:
  - suite2p
  - calcium-imaging
  - segmentation
  - two-photon
category: software
cluster: calcium-imaging
paper: suite2p_2017
created: 2025-09-18
---

# Suite2p

Paper: [Suite2p — Pachitariu et al. 2017](../literature/suite2p_2017/suite2p_2017.md)

Suite2p is a pipeline for processing two-photon calcium imaging data.

[GitHub](https://github.com/MouseLand/suite2p) | [Documentation](https://suite2p.readthedocs.io)

## Helpful Issues

- [Issue #921](https://github.com/MouseLand/suite2p/issues/921): Black background affects registration; tweak `block_size` / `spatial_taper`
- [Issue #880](https://github.com/MouseLand/suite2p/issues/880): Running on cluster
- [Issue #851](https://github.com/MouseLand/suite2p/issues/851): Overlapping ROIs and `ops['max_overlap']`
- [Issue #837](https://github.com/MouseLand/suite2p/issues/837): `tau` controls temporal binning
- [YouTube: ROI detection explainer](https://youtu.be/NcC0YxQ9o3A)
- [Issue #787](https://github.com/MouseLand/suite2p/issues/787): `threshold_scaling` for dim signals
- [Issue #690](https://github.com/MouseLand/suite2p/issues/690): Multi-channel registration
- [Issue #627](https://github.com/MouseLand/suite2p/issues/627): F and Fneu meaning
- [Issue #758](https://github.com/MouseLand/suite2p/issues/758#issuecomment-956588935): Looping over DBs on cluster
- [Issue #795](https://github.com/MouseLand/suite2p/issues/795): zarr vs NWB
- [Issue #750](https://github.com/MouseLand/suite2p/issues/750): GCaMP8f, `tau=0.1` for fast data
- [Issue #730](https://github.com/MouseLand/suite2p/issues/730): Max image brightness vs `tau`
- [Issue #667](https://github.com/MouseLand/suite2p/issues/667): 4D TIFFs, `sparse_mode` toggle
- [Issue #530](https://github.com/MouseLand/suite2p/issues/530): Units of `F` and `spks`

## Parameters

[Suite2p settings documentation](https://suite2p.readthedocs.io/en/latest/settings.html#main-settings)

- `tau`: Fixed, not scaled with frame-rate
  - 0.7 for GCaMP6f
  - 1.0 for GCaMP6m
  - 1.25-1.5 for GCaMP6s

## References

- [Suite2p GitHub](https://github.com/MouseLand/suite2p)
- [Suite2p Documentation](https://suite2p.readthedocs.io)
- [HHMI Janelia](https://www.janelia.org/lab/stringer-lab)
