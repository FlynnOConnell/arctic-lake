# IsoView notes from talks, lectures, external resources

Registration of Light Sheet Microscopy
https://www.youtube.com/watch?v=IupXS_On2rg

- Alignment wont be perfect
	- Light refractive index will be different in 2 samples

### Approaches
Intensity based
- takes a long time for a huge amount of pixels
- hard to validate, normally done with correlation values, often a better value doesn't actually align the samples
Bead based: embed beads in agarose
- rigid medium

Segmentation beads: look for sample intensities, ROIs like nucleis or membranes
- segmentation here doesn't even need to be specific to a gcamp expressing cell 
- staining dependent, need need gcamp?

Geometric local descriptor: each bead is represented by its nearest 3 neighbors
- each bead has 3 neighbors
- for soma, only match 3/4 neighbors

**Assign closest point ICP (no invariance)**
Compare all views against each other
Compare all interest point of overlapping views
Fix first view, do not map back
affine transformation model
one round (classic)

## Parameters for Registration

- Transformation model: affine, yes you can scale it, regularize with rigid so it doesn't scale too much
- Redundancy: Not enough matches? Increase this
	- Tries to find more features in common
	- may find wrong ones, filtered out often in ransac stem
	- 2, usually max 3, possibly 4
- Significance, to be considered, how much better?
	- 1 means take whichever is best
	- usualy 2 is sensible
- Allowed error (outlier filtering)
	- matches them together
	- defines how big error is allowed to be
	- 5px is typical

Sigma = 2.486
Threshold = 0.01623

Max distance: 20px
Allowed Error: 8px

