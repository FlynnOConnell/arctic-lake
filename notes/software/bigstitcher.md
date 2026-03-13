# Bigstitcher registration

## which view is fixed, which moves?

- **viewA = fixed (reference)**, **viewB = moving** in pairwise registration
- pair ordering: pairs generated with `i < j`, so lower setup ID is viewA by default
- in global optimization, the **first view in each subset** is fixed (its transform never changes)
- user can override which view is fixed in the GUI

## transform chain

each `ViewRegistration` holds an ordered list of `ViewTransform` entries. typical chain:

```
[stitching transform] → [manual transform] → [calibration]
                ↑ newest                          oldest ↑
```

- new registration results are **pre-concatenated** (inserted at the front)
- `vr.getModel()` composes the full chain into a single affine
- only the **moving view's** chain gets a new transform appended; the fixed view stays untouched

## manual transform baking (BDV viewer)

- applies to **whichever setup is currently displayed/selected** in BDV
- reads the viewer's accumulated manual drag/rotate transform
- **adds to position 1** (second entry) in the transform list, not the front
- code: `ApplyBDVTransformationPopup.java:121-153`

this is where the mistake happened: if VW00 (setup 0) was the active source
when you applied the rotation, it got baked onto setup 0 instead of setup 1.

## interest point registration

1. detect interest points per view (DoG)
2. pairwise matching between all view pairs
3. compute pairwise shift: viewB's points relative to viewA's coordinate frame
4. global optimization solves for all transforms simultaneously, keeping fixed views locked
5. result transforms are pre-concatenated onto each non-fixed view's registration

key: the shift is computed in pixel space then converted to global coords using
viewB's existing transform (`TransformationTools.java:310-311`).

## fusion

- does NOT explicitly transform volumes
- opens each view as a virtually-transformed image using its full `ViewRegistration` model
- renders all views into a common bounding box, blending where they overlap

## practical takeaway for VW00/VW90 alignment

1. setup 0 (VW00) should be the **fixed reference** — identity transforms only (+ calibration)
2. select **only setup 1** (VW90) in BDV, apply 90° rotation around Y, then bake
3. run interest-point registration — it will refine setup 1's transform while keeping setup 0 fixed
4. fuse

the calibration transform `(1, 1, 15.17)` on both setups accounts for anisotropic voxel spacing
(z_step / pixel_xy = 6.22 / 0.41 ≈ 15.17).
