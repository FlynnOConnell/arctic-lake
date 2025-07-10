[nature.com](https://www.nature.com/articles/nmeth.3632)
[[light_sheet_microscopy/chhetri_keller_2015/paper|paper]]

# Whole-animal functional and developmental imaging with isotropic spatial resolution

## Key takeaways
- Need *at least* 2 additional views (2 -> 4) needed for whole-CNS imaging in larger specimin > 80x80x50um^3
	- 400-fold larger volumes
- Dresophila `@2Hz` with  `1.1-2.5um` resolution
- Zebrafish `@1Hz`
- Multicolor gastrulating drosophila `@0.25hz`

## The microscope

**Figure 1: Isotropic multiview light-sheet microscopy.**

[![figure 1](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnmeth.3632/MediaObjects/41592_2015_Article_BFnmeth3632_Fig1_HTML.jpg)](https://www.nature.com/articles/nmeth.3632/figures/1)
- **4 identicle** orthogonally arranged arms
	- Illuminate with scanned laser light sheet
	- Image emitted fluoresence 

1. PSF before multi-view registration:
![[snap1.png]]
2. Inject beads into embryo
![[bead_site.png]]
3. Multiview-deconv fixes lateral/axial PSF
![[bead_site2.png]]

### Location Matters
- signal strengths at locations near the surface of the embryo (< 20 μm depth, vs the center ~100 μm depth),
- bead fluorescence intensities decrease on average by a factor of 5 in the raw views and by a factor of 6 in the multi-view deconvolved IsoView data