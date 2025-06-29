# Extract 

Fast, scalable, and statistically robust cell extraction
from large-scale neural calcium imaging datasets

[Paper (biorxiv, 2024)](https://www.biorxiv.org/content/10.1101/2021.03.24.436279v3.full.pdf)

## Processing pipeline

- Very basic preprocessing, median filter and regression to remove non-stationary signal drift
- No tuning, mk301 plane 7 = 300+ cells in 3 minutes
- Cellfinder: ~9min/zplane
- adaptive_threshold increases cells that are dim on the edges
- spatial_corrupt_thresh: ??? what does this do?
