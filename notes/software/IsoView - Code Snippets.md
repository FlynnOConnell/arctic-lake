---
tags:
  - isoview
  - light-sheet
  - matlab
  - image-processing
category: software
created: 2025-07-23
---

# IsoView Processing: Repeated Code Snippets
## Offset and Rotation
```matlab
RR = [ cosd(bestRotation) sind(bestRotation);... -sind(bestRotation) cosd(bestRotation)]; [XI ZI] = meshgrid(1:xSize, 1:zSize); cc = [(xSize + 1) / 2.0 (zSize + 1) / 2.0];
XI = XI' - cc(1);
ZI = ZI' - cc(2);
XZaux = (RR * [XI(:) ZI(:) .* scaling]')';
XI = reshape(XZaux(:, 1) + cc(1), size(XI));
ZI = reshape(XZaux(:, 2) ./ scaling + cc(2), size(ZI));
ZI = ZI - bestOffset;
```

## Background Normalization / Subtraction
- **Subsamples** the 3D stacks (`primaryDataArray{1,1}` and `{2,1}`) by flattening every `subSampling`-th voxel.
- **Removes zeros** from both samples (ignores background pixels).
- **Concatenates** both nonzero arrays.
- **Estimates the background** using the `percentile` (e.g. 5th percentile of the merged intensities).
	 ![[Pasted image 20250723144729.png|400]]

```matlab
if correction(1) ~= 0
if dataType == 1
	minIntensityName = [inputFolder '/' inputHeader '_CM' num2str(camera, '%.2d') '_CHN' num2str(tChannels(1), '%.2d') '.minIntensity.mat'];
	load(minIntensityName, 'minIntensity');
	backgroundIntensity1 = minIntensity(end);
	
	minIntensityName = [inputFolder '/' inputHeader '_CM' num2str(camera, '%.2d') '_CHN' num2str(tChannels(2), '%.2d') '.minIntensity.mat'];
	load(minIntensityName, 'minIntensity');
	backgroundIntensity2 = minIntensity(end);
else
	backgroundArray1 = primaryDataArray{currentCamera, 1}(1:subSampling:end);
	backgroundArray2 = primaryDataArray{currentCamera, 2}(1:subSampling:end);
	background = prctile(cat(2, backgroundArray1(backgroundArray1 > 0), backgroundArray2(backgroundArray2 > 0)), percentile);
	clear backgroundArray1 backgroundArray2;
end;
```

## Gaussian Smoothing
```matlab
if splitting > 1
gaussStack = zeros(xSize, ySize, zSize, 'uint16');

splittingMargin = 2 * kernelSize;

for i = 1:splitting
	xSlabStart = max(1, round((i - 1) * xSize / splitting + 1 - splittingMargin));
	xSlabStop = min(xSize, round(i * xSize / splitting + splittingMargin));
	if preciseGauss
		convolvedSlab = uint16(imgaussianAnisotropy(double(primaryDataArray{currentCamera, 2}(xSlabStart:xSlabStop, :, :)), kernelSigmaArray, kernelSizeArray));
	else
		convolvedSlab = imgaussianAnisotropy(primaryDataArray{currentCamera, 2}(xSlabStart:xSlabStop, :, :), kernelSigmaArray, kernelSizeArray);
	end;
	if i == 1
		gaussStack(1:(xSlabStop - splittingMargin), :, :) = convolvedSlab(1:(end - splittingMargin), :, :);
	elseif i == splitting
		gaussStack((xSlabStart + splittingMargin):end, :, :) = convolvedSlab((1 + splittingMargin):end, :, :);
	else % i > 1 && i < splitting
		gaussStack((xSlabStart + splittingMargin):(xSlabStop - splittingMargin), :, :) = convolvedSlab((1 + splittingMargin):(end - splittingMargin), :, :);
	end;
	clear convolvedSlab;
end;
else
if preciseGauss
	gaussStack = uint16(imgaussianAnisotropy(double(primaryDataArray{currentCamera, 2}), kernelSigmaArray, kernelSizeArray));
else
	gaussStack = imgaussianAnisotropy(primaryDataArray{currentCamera, 2}, kernelSigmaArray, kernelSizeArray);
end;
end;
```

## Fuse Two Masks
```matlab
if maskFusion == 0
			% consider only regions that exist in both masks
			overlap = (sliceArray{1} > 0) & (sliceArray{2} > 0);
			averageMask = uint16((double(sliceArray{1}) .* double(overlap) + double(sliceArray{2}) .* double(overlap)) ./ 2);
		else
			% consider regions that exist in either of the two masks
			overlap = (sliceArray{1} > 0) & (sliceArray{2} > 0);
			averageMask = uint16((double(sliceArray{1}) .* double(overlap) + double(sliceArray{2}) .* double(overlap)) ./ 2);
			averageMask = averageMask + ...
				uint16(double(sliceArray{1}) .* double(sliceArray{1} > 0) .* double(averageMask == 0)) + ...
				uint16(double(sliceArray{2}) .* double(sliceArray{2} > 0) .* double(averageMask == 0));
		end;
```

## Affine Registration

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