
Data types for images

- The images are normalized from raw float values to the [0, 1] range using percentiles:
``` python
mimg = (mimg - mimg1) / (mimg99 - mimg1)
mimg = np.clip(mimg, 0, 1)
```
- Then scaled to [0, 255] and cast to `uint8`:
``` python
mimg = (mimg * 255).astype(np.uint8)
```

