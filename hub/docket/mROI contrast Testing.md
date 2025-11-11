---
created: <% tp.file.creation_date("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - mbo
  - lbm
  - light-beads-microscopy
  - image-processing
aliases:
---
#  Contrast Differences between mROIs
- Line profile down the vertically stitched image
![[Pasted image 20250720194409.png]]

- Mean-Image
![[Pasted image 20250720195027.png]]

go_to_2x-mROI-880x1100um_220x550px_2um-px_15p04Hz_july2025_referenceplane1_00005

Mean-Image, Intensity vs Y 
![[Pasted image 20250720192657.png]]![[Pasted image 20250720195455.png]]

- z-plane 14
![[Pasted image 20250720200101.png]]

### Santis Dataset

Inter-quartile range mask for measuring contrast changes
![[Pasted image 20250720204845.png]]
Leading to this:
![[Pasted image 20250720205317.png]]

kbarber: 2025_07_16\m355\

**Mean-Image (z-plane 10)**
![[Pasted image 20250720210604.png]]
Signal filtered by IQR 25-75
![[Pasted image 20250720210737.png]]
![[Pasted image 20250720211027.png | 700]]

kbarber: mk350 07/17
![[Pasted image 20250720212553.png]]

![[Pasted image 20250720212804.png]]

# Pollen Beads Jitter

## Takeaways
- There are blurred edges indicating some movement artifact even in pollen
- 
## TODO
- Collect pollen beads on tilted stage
- Prep for call with Amol early next week:
	- Pollen Beads, tilted stage
	- Run maskNMF on Wills dataset (same scope, different dataset)
	- Run maskNMF on a single strip from santis dataset (different scope, different parameters)

##  STD Image
ZPlane 1: Std.dev. Image
![[Pasted image 20250724091203.png]]
![[Pasted image 20250724091113.png|400]]!

### Plane 1, 7, 14: Mean-Subtracted Image
![[Zplane_1_7_14_PollenBeads_pmd_meansub.mp4]]

### Z-Plane 1: No Jitter on Edge Phase Artifact
![[Zplane_7_PollenBeads_EdgeFOV.mp4]]
### Z-Plane 1: No Jitter?
![[Zplane_14_PollenBeads_Zoomed_NoWobbles.mp4]]

### Z-Plane 1: Noticable Jitter
![[Zplane_1_PollenBeads_wobbles.mp4]]