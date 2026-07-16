---
citekey: chhetri_keller_2015
title: "Chhetri et al. 2015 — Whole-animal functional and developmental imaging with isotropic spatial resolution"
category: literature
cluster: light-sheet
tags: [light-sheet-microscopy, isoview, image-fusion, multiview-deconvolution]
tools: [isoview, simview]
related: [tomer_keller_2012, amat_keller_2015, lemon_keller_2015]
pdf:
source: https://www.nature.com/articles/nmeth.3632
created: 2025-07-08
---

# Chhetri et al. 2015 — Whole-animal functional and developmental imaging with isotropic spatial resolution

**Chhetri, Amat, Wan, Höckendorf, Lemon, Keller — Nature Methods (2015)** · doi:10.1038/nmeth.3632

PDF: _not in repo_ · full text: [source.md](source.md) · [nature.com](https://www.nature.com/articles/nmeth.3632)

## Key takeaways
- Need *at least* 2 additional views (2 -> 4) needed for whole-CNS imaging in larger specimin > 80x80x50um^3
	- 400-fold larger volumes
- Dresophila `@2Hz` with  `1.1-2.5um` resolution
- Zebrafish `@1Hz`
- Multicolor gastrulating drosophila `@0.25hz`

## The microscope

**Figure 1: Isotropic multiview light-sheet microscopy.**

[![Figure 1](figures/fig1.jpg)](https://www.nature.com/articles/nmeth.3632/figures/1)
- **4 identicle** orthogonally arranged arms
	- Illuminate with scanned laser light sheet
	- Image emitted fluoresence 

1. PSF before multi-view registration:
![](figures/snap1.png)
2. Inject beads into embryo
![](figures/bead_site.png)
3. Multiview-deconv fixes lateral/axial PSF
![](figures/bead_site2.png)

### Location Matters
- signal strengths at locations near the surface of the embryo (< 20 μm depth, vs the center ~100 μm depth),
- bead fluorescence intensities decrease on average by a factor of 5 in the raw views and by a factor of 6 in the multi-view deconvolved IsoView data
