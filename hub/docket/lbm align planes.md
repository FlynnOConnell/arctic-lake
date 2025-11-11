## Z-Plane Alignment

This problem has been solved previously
- Suite3D
	- Operates on raw-scanimage tiffs
	- Volumetric: makes reference 4D TZXY volume

 [`np.roll` is faster than `scipy.shift`](https://stackoverflow.com/questions/42983478/np-roll-vs-scipy-interpolation-shift-discrepancy-for-integer-shift-values):

```python
def shift_frame(frame: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """
    Returns frame, shifted by dy and dx

    Parameters
    ----------
    frame: Ly x Lx
    dy: int
        vertical shift amount
    dx: int
        horizontal shift amount

    Returns
    -------
    frame_shifted: Ly x Lx
        The shifted frame

    """
    rolled = np.roll(frame, (-dy, -dx), axis=(0, 1))
    dy *= -1;
    dx *= -1
    if dx < 0:
        rolled[:, dx:] = 0
    elif dx > 0:
        rolled[:, :dx] = 0
    if dy < 0:
        rolled[dy:, :] = 0
    elif dy > 0:
        rolled[:dy, :] = 0
    return rolled

```

``` python
total_frames_all_files = sum(tifffile.imread(file).shape[0] for file in files)

start = time.time()
with tqdm(total=total_frames_all_files, desc="Shifting Frames") as pbar:
    for i, file in (enumerate(files)):
        out_file = stitched_dir / "aligned_gpu" / file.name.replace("_stitched.tif", "_aligned.tif")
        img = tifffile.imread(file)
        dy, dx = shifts[i]
        aligned = np.empty_like(img)
        for i, frame in tqdm(enumerate(img)):
            aligned[i] = shift_frame(frame, -dy, dx)
            pbar.update(1)
        tifffile.imwrite(out_file, aligned.astype(np.float32))

end = time.time()
print(f"Total alignment time: {end - start:.2f} seconds")
```

Due to lack of interpolation at the edges.

Suite2p and Suite3D both use this shift frame function.

## Suite3D axial alignment
* Data input: 2060 x 448 x 448 stitched (mROI left + mROI right) tiff

Several optimizations:
1. Spatial tapering in FFT domain to reduce ring artifacts
2. Masking out low frequency regions

-  `init_n_frames = 500, n_init_files = 1` 
	- Initialization pass took 38.12 seconds
-  `init_n_frames = 500, n_init_files = 2` 
	- Initialization pass took 63.63
-  `init_n_frames = 500, n_init_files = 5` 
	- Initialization pass took 117.76



