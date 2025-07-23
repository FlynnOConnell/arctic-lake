---
created: <% tp.file.creation_date("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - image-processing
  - registration
aliases:
---
# Image Transformations

## Affine 

- Rotation: RR is the rotation matrix
- Translation by bestXOffset / bestYOffset
- cc is the image center, which rotations
```matlab
[ XI YI ] = meshgrid(1:size(sliceArray{2}, 1), 1:size(sliceArray{2}, 2));
RR = [ cosd(bestRotation) sind(bestRotation); ...
      -sind(bestRotation) cosd(bestRotation)];

cc = [(size(sliceArray{2}, 1) + 1) / 2.0, (size(sliceArray{2}, 2) + 1) / 2.0];

XI = XI' - cc(1);
YI = YI' - cc(2);

XZaux = (RR * [XI(:), YI(:)]')';
XI = reshape(XZaux(:, 1) + cc(1), size(XI));
YI = reshape(XZaux(:, 2) + cc(2), size(YI));

XI = XI - bestXOffset;
YI = YI - bestYOffset;
```