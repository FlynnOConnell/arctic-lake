---
created_date: 07/10/2025
title: Cellpose
tags:
- pipelines
- calcium-imaging
- software
- cellpose
---
# Cellpose
## Overview

* Chose deep neural networks, like maskRCNN for segmentation problems
* Relevant for e.g. self driving cars
* Best models can generalize
* **Must** assign a pixel to a single mask, no overlaps are allowed
* If you have lots of overlaps, without 3D information you probably want maskRCNN that can take overlaps into account

#image-processing #metrics
### IoU: Two cells that share 50% of the space they occupy, their IoU would be 0.5
![[Pasted image 20250711194105.png|300]]

## References
[HHMI talk](https://www.youtube.com/watch?v=NcC0YxQ9o3A&t=387s)
