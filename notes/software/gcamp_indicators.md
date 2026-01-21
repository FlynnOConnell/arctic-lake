---
tags:
  - gcamp
  - calcium-imaging
  - indicators
  - deconvolution
category: software
created: 2025-09-18
---

# GCaMP Indicators and Deconvolution Kernel Selection

The goal is to have the kernel **mirror the sensor's dynamics** so that one spike's fluorescence trace is correctly accounted for by the model.

## Indicator Dynamics and Recommended Kernel (Tau)

| Indicator | Rise t1/2 (ms) | Decay t1/2 (ms) | Single-AP SNR / dF | Recommended Kernel tau (s) |
|-----------|----------------|-----------------|---------------------|---------------------------|
| GCaMP6f (fast) | ~50 ms | ~140 ms (~100 ms 1AP) | Low-moderate (smallest 6x dF; detects 1 AP) | 0.7 s (0.5-0.8) |
| GCaMP6m (medium) | ~100 ms | ~200 ms | High (dF larger than 6f, ~2x; good 1 AP SNR) | 1.0 s (~0.8-1.2) |
| GCaMP6s (slow) | ~150-200 ms | ~500 ms (up to 1800 ms for bursts) | Very high (largest dF; ~2-3x 6f; best 6x SNR) | 1.2-1.5 s (often ~1.25) |
| jGCaMP7f (fast) | ~25 ms | ~180-270 ms (single AP) (~520 ms multi-AP) | Moderate (improved vs 6f, but lowest of 7x) | ~1.0 s (use slightly longer than 6f) |
| jGCaMP7m (interm.) | ~50 ms | ~500-700 ms | High (midway 7f-7s; bright baseline, strong dF) | ~1.2 s (est., compromise value) |
| jGCaMP7s (slow) | ~100 ms+ | ~1690 ms (1.69 s) | Very high (largest 7x dF; ~2-3x 7f) | 1.5-2.0 s (match slow decay) |
| jGCaMP8f (fast) | ~7 ms | ~67 ms | Moderate-high (dF ~0.4; >7f, but lowest 8x) | ~0.5 s (0.3-0.6 s range) |
| jGCaMP8m (medium) | ~7 ms | ~118 ms | High (dF ~0.7; ~7s sensitivity with fast kinetics) | ~0.7 s (0.5-0.8 s range) |
| jGCaMP8s (slow) | ~10 ms | ~307 ms (200-300 ms in vivo) | Very high (dF ~1.1; highest of all; ~2x 7s d') | ~1.0 s (0.8-1.2 s range) |

## Frame Rate Considerations

- If the frame rate is high relative to the sensor's speed, you'll capture the true kinetics; tau can be set close to the known value.
- If the frame rate is low, fast transients will be under-sampled - they may appear attenuated and stretched over multiple frames.
- At low FPS, lean toward a slightly longer tau to avoid missing spikes

**Example**: jGCaMP8f has an actual half-decay (t1/2) ~0.07 s, but if you image at 5 Hz (200 ms frame interval), a single-frame spike could drop in one frame.

## Pipeline-Specific Settings

### CaImAn

[CaImAn parameters](https://caiman.readthedocs.io/en/latest/Getting_Started.html#parameters)

- `decay_time`: Length of typical transient in seconds
- Default is `0.4`, appropriate for fast sensors (GCaMP6f)
- Slow sensors may use 1 or more

### Suite2p

[Suite2p parameters](https://suite2p.readthedocs.io/en/latest/settings.html#main-settings)

- `tau`: Fixed, not scaled with frame-rate
- 0.7 for GCaMP6f
- 1.0 for GCaMP6m
- 1.25-1.5 for GCaMP6s

## Sources

1. [Spike inference from calcium imaging data acquired with GCaMP8 indicators](https://www.biorxiv.org/content/10.1101/2025.03.03.641129v2.full#F8)
2. [Janelia Calcium Indicators](https://www.janelia.org/jgcamp8-calcium-indicators)
