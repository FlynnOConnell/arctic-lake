# Isoview Processing Notes

## Pipeline overview

Dead pixel correction -> foreground segmentation -> geometric transforms -> masking

---

## Dead pixel correction

MATLAB: `correctInsensitivePixels()` in `processTimepoint_RC.m`
Python: `correct_dead_pixels()` in `isoview/corrections.py`

Basic idea:
- get std projection along z
- get mean projection
- median filter both
- dead pixels are where the raw deviates too much from filtered

threshold is from a linear fit of deviation vs mean - take max distance from that line

MATLAB does `medfilt2` per z-slice, python does `scipy.ndimage.median_filter` on whole volume. probably gives slightly different results at edges

---

## Foreground segmentation

anisotropic gaussian filter first - sigma is different in z because of the scaling factor

```
sigma_z = max(1, kernel_sigma / scaling)
```

both do slab processing (10 slabs default) for memory

**BIG DIFFERENCE HERE**: MATLAB uses `multithresh` (otsu), python uses percentile threshold. this is probably where most of the output differences come from

coordinate masks - average coordinates weighted by binary mask. same logic both sides

---

## Geometric transforms

rotation is 90 degree increments only

clockwise:
```
# permute then flip
volume = np.transpose(volume, (0, 2, 1))[:, ::-1, :]
```

counterclockwise same but flip other axis

remember MATLAB is 1-indexed and usually (y,x,z), python is 0-indexed (z,y,x)

cropping is straightforward slicing

---

## Masking

just `volume[~mask] = 0`, same both sides

---

## Things that cause differences

median filter implementations - medfilt2 vs scipy.ndimage.median_filter, slightly different at boundaries

gaussian filter - imgaussfilt3 vs scipy gaussian_filter, again boundary handling

**thresholding is the big one** - otsu vs percentile gives different masks

float precision - MATLAB defaults to float64, python needs explicit casting to float32. small errors accumulate

typical diff is ~60 mean absolute (0.09% of uint16 range), but can hit 65535 at mask edges where one says foreground and other says background

---

## Parameters

| what | matlab | python |
|------|--------|--------|
| gaussian sigma xy | kernelSigma | kernel_sigma |
| gaussian sigma z | max(1, kernelSigma/scaling) | same |
| median kernel | [3,3] | (3,3) |
| threshold | otsu | mask_percentile (default 50) |
| slabs | 10 | splitting param |
| background | 100 | background_value |

---

## Memory stuff

MATLAB uses `multibandread` to load partial stacks
Python uses `np.fromfile` and loads the whole thing, figures out depth from file size

dead pixel correction: matlab does z-slice by z-slice, python does whole volume at once

---

## TODO / questions

- should python use otsu instead of percentile? would make outputs match better
- the boundary handling on filters might matter for edge ROIs
- check if the coordinate mask NaN->0 casting is causing issues anywhere downstream
