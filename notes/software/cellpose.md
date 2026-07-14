---
tags:
  - cellpose
  - segmentation
  - deep-learning
  - calcium-imaging
category: software
created: 2025-07-11
---

# Cellpose

Cellpose is a deep learning-based segmentation algorithm for cells and nuclei.
- developed at HHMI Janelia Research Campus by Carsen Stringer and Marius Pachitariu
## Core Concepts

## Generally important 
- Mean diameter for tained data: 30 pixels for cyto, 17 pixels for nuclei (images rescaled to this range)
- Later models are robust to size
### Flow Field

The central innovation of Cellpose is its use of **gradient flow fields** as an intermediate representation for segmentation. Rather than directly predicting masks or boundaries, Cellpose:

- Predicts two flow fields (horizontal and vertical) that point toward cell centers
- Uses a simulated heat diffusion process to generate training targets from masks
- Runs gradient tracking at inference to group pixels that converge to the same center
- Naturally handles complex, non-convex cell shapes including protrusions and curved morphologies.

This representation is **size-invariant and morphology-independent** since it does not rely on assumptions about cell shape like star-convexity (StarDist) or fixed object sizes.

### Key Constraints

- Each pixel must be assigned to exactly **one mask** or background (no overlapping masks allowed)
- If you have significant cell overlaps, consider Mask R-CNN or similar methods that support overlapping instances
- 3D segmentation runs the 2D model on XY, XZ, and YZ planes and aggregates the flow fields

### Evaluation Metrics

IoU (Intersection over Union): Measures overlap between predicted and ground truth masks. Two cells sharing 50% of their combined occupied space have IoU = 0.5.

![300](../images/Pasted%20image%2020250711194105.png)

Average Precision (AP): Computed at various IoU thresholds (commonly AP@0.5). Higher is better.

---

## 01: Cellpose (2020)

**Paper**: Stringer, Wang, Michaelos, Pachitariu. *Nature Methods* 18, 100-106 (2021)

### What It Introduced

- **Generalist segmentation**: A single model that works across diverse cell types, stains, and imaging modalities without retraining
- **Flow field representation**: The gradient-based approach that became the foundation of all subsequent versions
- **Two built-in models**: `cyto` for cytoplasm/whole-cell and `nuclei` for nuclear segmentation
- **3D extension**: Reuses the 2D model by averaging flow predictions across orthogonal planes
- **GUI and CLI**: User-friendly interface for running segmentation and manual annotation

### Technical Details

- Architecture: Modified U-Net with skip connections and a global style vector
- Training data: Over 70,000 manually segmented objects across highly varied images
- Mean diameter: 30 pixels for cyto, 17 pixels for nuclei (images rescaled to this range)
- Outputs: Flow fields (X and Y), cell probability map, and final masks

### Other Notes

- The `diameter` parameter is used 
- Two-channel input: first channel is the segmentation target, second channel is optional (nuclei for cyto model, zeros for nuclei model)
- Works well out-of-the-box for most fluorescence microscopy; may struggle with very noisy, blurry, or undersampled images
	- Why? 

---

## 02: Cellpose 2.0 - Train Your Own Model (2022)

**Paper**: Pachitariu & Stringer. *Nature Methods* 19, 1634-1641 (2022)

### What It Introduced

- **Human-in-the-loop training**: Iteratively refine a model by correcting its mistakes rather than annotating from scratch
- **Efficient fine-tuning**: Fine-tune pretrained models with only 500-1,000 annotated ROIs to match performance of models trained on 200,000+ ROIs
- **Model zoo**: Ensemble of diverse pretrained models for different image types
- **`cyto2` model**: Trained on original data plus user-contributed images

### Human-in-the-Loop Workflow

1. Run the pretrained model on your image
2. Correct mistakes in the GUI (add missing cells, fix bad segmentations)
3. Retrain the model on your corrections (takes less than 1 minute on GPU)
4. Apply to the next image and repeat
5. Typically 3-5 images (100-200 ROIs) are sufficient for good performance

### Key Insights

- **Annotation style matters**: Different annotators segment differently; training on your own style is essential for matching your ground truth
- **Pretraining is critical**: Starting from Cellpose weights dramatically reduces required training data
- **Large learning rates work**: For small training sets, aggressive learning rates during fine-tuning are effective

### When to Use This

- Your images look different from the training data
- The built-in models miss cells or produce wrong boundaries
- You have a specific annotation style you need to match
- You want to create a specialized model for your lab or project

---

## 03: Cellpose3 - One-Click Image Restoration (2025)

**Paper**: Stringer & Pachitariu. *Nature Methods* (2025)

### What It Introduced

- **Image restoration for segmentation**: Denoising, deblurring, and upsampling models trained specifically to improve downstream segmentation
- **One-click interface**: GUI buttons for instant image restoration
- **Segmentation-aware training**: Unlike traditional restoration methods that optimize for pixel-level reconstruction, Cellpose3 optimizes for better segmentation performance
- **`cyto3` model**: Super-generalist model trained on 9 diverse datasets

### Available Restoration Models

| Model Type | What It Does | When to Use |
|------------|--------------|-------------|
| `denoise_*` | Removes Poisson/shot noise | Low SNR, low laser power imaging |
| `deblur_*` | Corrects optical blur | Out-of-focus images, thick samples |
| `upsample_*` | Super-resolution (2-3x) | Small cells, undersampled images |
| `oneclick_*` | All three combined | Unknown degradation, general use |

Available for both cyto and nuclei variants: `denoise_cyto3`, `deblur_cyto3`, `upsample_cyto3`, `oneclick_cyto3`, `denoise_nuclei`, etc.

### Key Technical Details

- Restoration network is chained with a frozen segmentation network during training
- Uses perceptual loss + segmentation loss (not just reconstruction loss)
- Trained on varied datasets for good out-of-distribution generalization
- Does not hallucinate cells (false positive rates remain stable)

### Practical Notes

- Particularly useful for axial slices in 3D data (ZY, ZX planes are often blurry/undersampled)
- The one-click models are slightly worse than task-specific models but more convenient
- Restored images are visually improved and can be saved for other purposes

### Note on Speed Comparisons

From Marius Pachitariu on image.sc:
> The speed comparisons in the paper are done including the size model for Cellpose3, which approximately doubles runtimes, especially for small images. I know almost no one uses that, but we have to use it for papers to do fair comparisons.

---

## CP-SAM: Cellpose-SAM - Superhuman Generalization (2025)

**Paper**: Pachitariu, Rariden, Stringer. *bioRxiv* (2025)

### What It Introduced

- **SAM backbone integration**: Replaces the U-Net encoder with SAM's pretrained Vision Transformer (ViT-L)
- **Superhuman performance**: Exceeds inter-human agreement and approaches the human-consensus bound
- **Single unified model**: One set of weights works across all image types (no more separate cyto/nuclei models)
- **Built-in robustness**: Trained to handle noise, blur, downsampling, anisotropic PSF, and channel shuffling

### Architecture Changes

| Component           | Original Cellpose                | Cellpose-SAM                     |
| ------------------- | -------------------------------- | -------------------------------- |
| Encoder             | U-Net with ResNet blocks         | SAM's ViT-L (305M parameters)    |
| Decoder             | U-Net decoder + skip connections | Lightweight upsampling           |
| Output              | Flow fields + cell probability   | Same (flow fields + probability) |
| Mask reconstruction | Gradient tracking                | Same                             |

The key insight: SAM's encoder learned powerful image representations from 11 million images. By replacing only the encoder and keeping Cellpose's flow-based output and gradient tracking, you get the best of both worlds.

### Quality of Life Improvements

- **Channel order invariance**: No need to specify which channel is nuclei vs cytoplasm
- **Size invariance**: Less sensitive to diameter parameter (trained on diameters 7.5-120 pixels)
- **No separate restoration step**: Robustness to degradation is built into the model
- **No size model needed**: Eliminates the size estimation step

### Human Performance Bounds

The paper introduces an important concept: matching individual human annotators is not the ceiling.

- **Inter-human agreement**: How well two human annotators agree with each other
- **Human-consensus bound**: The theoretical performance if you could average many human annotations

Cellpose-SAM approaches the human-consensus bound, meaning its errors are largely attributable to ambiguity in the images themselves rather than model limitations.

### Practical Notes

- Available as `cpsam` in the model dropdown
- Slower than original Cellpose (larger model), but faster than Cellpose + restoration
- Still supports fine-tuning with human-in-the-loop training
- 3D segmentation works the same way (2D model on orthogonal planes)
- FP16/FP8 inference not yet enabled but may be added for speed

---

## Model Progression Summary

| Version | Model Names      | Key Feature                | When to Use                      |
| ------- | ---------------- | -------------------------- | -------------------------------- |
| 1.0     | `cyto`, `nuclei` | Original generalist        | Legacy, simple cases             |
| 2.0     | `cyto2`          | Human-in-the-loop training | Custom fine-tuning               |
| 3.0     | `cyto3`          | Image restoration          | Noisy/blurry/undersampled images |
| SAM     | `cpsam`          | Superhuman generalization  | Best out-of-box performance      |

For new projects, start with `cpsam`. Fall back to `cyto3` + restoration if speed is critical. Use human-in-the-loop training if out-of-box performance is insufficient.

---

## Practical Decision Tree

**Which model should I use?**

```
Start with cpsam (Cellpose-SAM)
    |
    +--> Good results? --> Done
    |
    +--> Too slow? --> Try cyto3 (faster, nearly as good)
    |
    +--> Image quality issues?
            |
            +--> Noisy --> Use denoise_cyto3 + cyto3
            +--> Blurry --> Use deblur_cyto3 + cyto3
            +--> Small cells --> Use upsample_cyto3 + cyto3
            +--> Unknown --> Use oneclick_cyto3 + cyto3
    |
    +--> Still not good? --> Human-in-the-loop training
            |
            +--> Annotate 3-5 images
            +--> Retrain from cpsam
            +--> Usually sufficient
```

**Do I need 3D segmentation?**

- Cellpose 3D runs 2D models on XY, XZ, YZ planes and aggregates
- For isotropic data, this works well
- For anisotropic data (thick z-slices), consider using Cellpose3 restoration on axial views first
- Alternative: 2D segmentation on XY slices + stitching across Z

---

## References

- [Cellpose GitHub](https://github.com/MouseLand/cellpose)
- [Cellpose Documentation](https://cellpose.readthedocs.io)
- [Cellpose Website](https://www.cellpose.org)
- [HHMI talk](https://www.youtube.com/watch?v=NcC0YxQ9o3A&t=387s)
- [Image.sc Forum](https://forum.image.sc/tag/cellpose)

### Citations

1. Stringer, C., Wang, T., Michaelos, M., & Pachitariu, M. (2021). Cellpose: a generalist algorithm for cellular segmentation. *Nature Methods*, 18(1), 100-106.
2. Pachitariu, M., & Stringer, C. (2022). Cellpose 2.0: how to train your own model. *Nature Methods*, 19(12), 1634-1641.
3. Stringer, C., & Pachitariu, M. (2025). Cellpose3: one-click image restoration for improved cellular segmentation. *Nature Methods*.
4. Pachitariu, M., Rariden, M., & Stringer, C. (2025). Cellpose-SAM: superhuman generalization for cellular segmentation. *bioRxiv*.

---

## Links

- [calcium-imaging](../tags/calcium-imaging.md) - main index for calcium imaging pipelines
- [suite2p](suite2p.md) - from the same lab
