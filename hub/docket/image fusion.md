---
created: <% tp.file.creation_date("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - image-processing
  - light-sheet-microscopy
  - software
aliases:
  - image-fusion
---
#  Light Sheet Microscopy: Image Fusion
- **Step 1:** `clusterMF.m (multiFuse.m)` – Per-timepoint multiview fusion 
- **Step 2:** `localAP.m`, `analyzeParameters.m` – Temporal transformation parameters  
- **Step 3:** `clusterTF.m` – Time-fused multiview fusion
## `clusterMF` / `multiFuse.m`

### Notes
- The first step of multiFuse.m is aligning channels
- We don't do this because processingMode=2 (2 camera, single channel)
### Steps
-  spatially convolve 
-  threshold smoothed 3D image to values above the min intensity
	- Where image > `minIntensity + (meanIntensity - minIntensity)`
	- this is 3D mask `mask3D`
-  The min intensity only
``` matlab
referenceMinIntensity = max(referenceMinIntensity, minIntensity);
```
- mean z-signal -> (X, Y) image
	- this is a slice-wise 2D map in `sliceMask`
- `maskFusion=0`  consider only regions that exist in both masks
	- otherwise consider regions that exist in either of the two masks
![[Pasted image 20250720155137.png]]
- overlap ![[Pasted image 20250720161344.png]]
- Average mask ![[Pasted image 20250720161534.png]]
- Combined mask ![[Pasted image 20250720161639.png]]
- Remove large anomolies ![[Pasted image 20250720162024.png]]
- remove small anomolies
- 
### Header Metadata

SPM00_CM00_CM01_CHN01
For each t:
- 'SPM00_TM000000_CM00_CHN01.klb'
- 'SPM00_TM000000_CM00_CHN01.minIntensity.mat'
- 'SPM00_TM000000_CM01_CHN01.klb'
- 'SPM00_TM000000_CM01_CHN01.minIntensity.mat'
- 'SPM00_TM000000_CM02_CHN00.klb'
- 'SPM00_TM000000_CM02_CHN00.minIntensity.mat'
- 'SPM00_TM000000_CM03_CHN00.klb'
- 'SPM00_TM000000_CM03_CHN00.minIntensity.mat'

``` matlab
%'SPM00_TM000000_CM00_CHN01.klb'

headerInformation = readKLBheader(fullFilePath);
disp(headerInformation);

xyzct: [752 2048 79 1 1]
pixelSize: [1 1 1 1 1]
dataType: 1
compressionType: 1
blockSize: [96 96 8 1 1]
metadata: ''
headerVersion: 2
```

#### XML metadata

| **Field**                            | **Channel 1**                                    | **Channel 2**                                    |
| ------------------------------------ | ------------------------------------------------ | ------------------------------------------------ |
| **software_version**                 | 3.0.0817                                         | 3.0.0817                                         |
| **data_header**                      | Dre_HuC_H2BGCaMP6s_0-1                           | Dre_HuC_H2BGCaMP6s_0-1                           |
| **output_root**                      | (empty)                                          | (empty)                                          |
| **specimen_name**                    | sample                                           | sample                                           |
| **timestamp**                        | 7:59:39.667 PM 7/9/2015                          | 7:59:39.667 PM 7/9/2015                          |
| **time_point**                       | 0                                                | 0                                                |
| **specimen_XYZT**                    | X=1130.000_Y=1045.000_Z=-205.000_T=-1.0          | X=1130.000_Y=1045.000_Z=-205.000_T=-1.0          |
| **specimen_drift**                   | N/A                                              | N/A                                              |
| **angle**                            | -1.0                                             | -1.0                                             |
| **camera_index**                     | 2                                                | 2                                                |
| **camera_type**                      | C11440-22C,C11440-22C                            | C11440-22C,C11440-22C                            |
| **camera_roi**                       | 648_1400_0_2048,648_1400_0_2048                  | 648_1400_0_2048,648_1400_0_2048                  |
| **time_step**                        | 1                                                | 1                                                |
| **wavelength**                       | 488                                              | 488                                              |
| **illumination_arms**                | 3                                                | 12                                               |
| **illumination_filter**              | ND1.0                                            | ND1.0                                            |
| **laser_power**                      | 2.00                                             | 2.00                                             |
| **exposure_time**                    | 4.8                                              | 4.8                                              |
| **detection_filter**                 | BP525/50                                         | BP525/50                                         |
| **dimensions**                       | 2048x752x79,2048x752x79                          | 2048x752x79,2048x752x79                          |
| **z_step**                           | 5.130                                            | 5.130                                            |
| **planes**                           | 0-78,0-78                                        | 0-78,0-78                                        |
| **z_offset_planes**                  | #planes=1; Sync_index=N/A; Z=-290.0:(42.0, 42.0) | #planes=1; Sync_index=N/A; Z=-290.0:(-5.0, 94.0) |
| **detection_objective**              | Zeiss 20x/1.00,Zeiss 20x/1.00                    | Zeiss 20x/1.00,Zeiss 20x/1.00                    |
| **background_subtraction**           | n,n                                              | n,n                                              |
| **SI**                               | n                                                | n                                                |
| **experiment_notes**                 | (empty)                                          | (empty)                                          |
| **custom_pre_script**                | (empty)                                          | (empty)                                          |
| **custom_pre_commands**              | (empty)                                          | (empty)                                          |
| **custom_post_script**               | (empty)                                          | (empty)                                          |
| **custom_post_commands**             | (empty)                                          | (empty)                                          |
| **action: custom_pre_script**        | n                                                | n                                                |
| **action: si_reconstruction**        | n                                                | n                                                |
| **action: deconvolution**            | n                                                | n                                                |
| **action: registration**             | n                                                | n                                                |
| **action: fusion**                   | n                                                | n                                                |
| **action: image_compression**        | n                                                | n                                                |
| **action: segmentation**             | n                                                | n                                                |
| **action: object_space_compression** | n                                                | n                                                |
| **action: tracking**                 | n                                                | n                                                |
| **action: custom_post_script**       | n                                                | n                                                |
| **action: V3D**                      | n                                                | n                                                |

### All Parameters

| **Parameter**  | **Default Value (how I found it)**                                                  | **Description**                              |
| -------------- | ----------------------------------------------------------------------------------- | -------------------------------------------- |
| `timepoints`   | `0:5:733`                                                                           | Timepoints to process                        |
| `inputString`  | `C:\Users\RBO\Documents\IsoView-test-data\...`                                      | Input data directory                         |
| `outputString` | `C:\Users\RBO\Documents\IsoView-test-data\...\Results_mbo\MultiFused\Pha_E1_H2bRFP` | Output directory                             |
| `outputID`     | `_blending`                                                                         | Output ID string                             |
| `dataType`     | `1`                                                                                 | 1 = segmented clusterPT output               |
| `specimen`     | `0`                                                                                 | Specimen index                               |
| `cameras`      | `0:1`                                                                               | Camera indices                               |
| `channels`     | `0:1`                                                                               | Channel indices                              |
| `reducedIO`    | `1`                                                                                 | 1 = minimal logging                          |
| `inputType`    | `0`                                                                                 | 0 = KLB input format                         |
| `outputType`   | `0`                                                                                 | 0 = KLB output format                        |
| `splitting`    | `10`                                                                                | Slab splitting factor                        |
| `kernelSize`   | `5`                                                                                 | Kernel size for filtering                    |
| `kernelSigma`  | `2`                                                                                 | Kernel sigma for filtering                   |
| `fraction`     | `0`                                                                                 | Min object size (0 disables filtering)       |
| `maskMinimum`  | `[1 100]`                                                                           | Percentile and subsampling for min intensity |
| `maskFactor`   | `1.0`                                                                               | Mask threshold factor                        |
| `maskFusion`   | `1`                                                                                 | Use full info for mask fusion                |
| `padding`      | `[0 50]`                                                                            | Padding mode and radius                      |
| `slabSizes`    | `[5 3]`                                                                             | Adaptive slab size: [channels, cameras]      |
| `intSizes`     | `[10 5]`                                                                            | Intensity correction slabs                   |
| `percentile`   | `5`                                                                                 | Background estimation percentile             |
| `subSampling`  | `[1 100]`                                                                           | Percentile subsampling: [slices, stacks]     |
| `medianFilter` | `100`                                                                               | Median filter range                          |
| `preciseGauss` | `1`                                                                                 | 1 = double precision Gaussian filter         |
| `gaussFilter`  | `[3 1]`                                                                             | Gaussian filter size and sigma               |
| `optimizer`    | `3`                                                                                 | 3 = custom gradient descent                  |
| `correction`   | `[1 1 0 0]`                                                                         | Intensity correction flags and factors       |
| `fusionType`   | `0`                                                                                 | 0 = adaptive blending                        |
| `transitions`  | `[0 0]`                                                                             | Transition planes for geometric blending     |
| `blending`     | `[20 4]`                                                                            | Blending ranges: [channels, cameras]         |
| `enforceFlag`  | `[1 1 1 ...]` (24 entries)                                                          | Enforced processing steps                    |
| `verbose`      | `0`                                                                                 | 0 = minimal output                           |
| `cropping`     | `{[0 0 0 0 0 0]; [0 0 0 0 0 0]}`                                                    | ROI cropping (disabled)                      |
| `scaling`      | `2.031 / (6.5 / 16)`                                                                | Axial scaling factor                         |
| `leftFlags`    | `[2 1]`                                                                             | Left-hand light sheet for each camera        |
| `flipHFlag`    | `1`                                                                                 | Flip horizontally: camera 1                  |
| `flipVFlag`    | `0`                                                                                 | Flip vertically: camera 1                    |
| `xOffsets`     | `-50:10:50`                                                                         | X-offsets for alignment                      |
| `yOffsets`     | `-50:10:50`                                                                         | Y-offsets for alignment                      |
| `frontFlag`    | `1`                                                                                 | Front-facing camera index                    |
| `localRun`     | `[0 0]`                                                                             | Run mode and local worker count              |
| `jobMemory`    | `[1 0]`                                                                             | Memory management flags                      |
| `coreMemory`   | `floor(((96 - 8) * 1024) / (12 * 1024))`                                            | Memory threshold for mode switching          |

Defaults don't work.
But that is for 4-view fusion, which we aren't doing. Come back to this

dataType = 0;
cameras = 0:1;
channels = 0:1;
-> configurationString = '_CM00_CM01_CHN00_CHN01';
-> SPM00_TM000000_CM00_CHN00_CM01_CHN01.klb

Actual Files:
View 1:
	SPM00_TM000000_CM00_CHN01.klb  -> `view-1 camera-1`
	SPM00_TM000000_CM01_CHN01.klb -> `view-1 camera-2`

View 2:
	SPM00_TM000000_CM02_CHN00.klb -> `view-2 camera-1`
	SPM00_TM000000_CM03_CHN00.klb -> `view-2 camera-2`
	

We need to analyze each of these two groups separately.

Fusion will turn view 1 into `SPM00_CM00_CM01_CHN01

Required params:
- Cameras: `CM00`, `CM01` → camera indices: `0`, `1`
- Channels: `CHN01` single view
- Other files with `CHN00` only appear at `CM02` and `CM03`
->  cameras = 0:1; channels = 1;
-> cameras = 2:3; channels = 0;
-  confusing ^^

### Output Files

The timepoints are set in step sizes like numpy:
- start:step:stop

timepoints = `0:5:755`

This leads to a folder for every 5 steps
- Pha_E1_H2bRFP.TM000000_multiFused_blending
- Pha_E1_H2bRFP.TM000005_multiFused_blending
- ...
- Pha_E1_H2bRFP.TM000730_multiFused_blending

For each timepoint:
![[Pasted image 20250718160107.png]]
## `localAP`
- `dataType = 0`: unsegmented `clusterPT` output
- `cameras = [0, 1]`, `channels = 1`: this sets `processingMode = 2` → **2-view camera fusion**
- `readFactors = 1`: intensity correction data will be used
- `staticFlag = 0`: fusion parameters vary with time
- `smoothing = [1, 20]`: apply robust local regression (rloess) with a 20-frame window
## `analyzeParameters`
1. **Set up output directory**
- `SPM00_CM00_CM01_CHN01_analyzeParameters/` is created inside `outputString`.
1. **Initialize data arrays**
- `transformations`: stores [time, x-offset, y-offset, angle] per `timepoint`
- `intensityCorrections`: stores [time, correctionFactor, correctionFlag]
- `lookUpTable`: final output array of size `length(fullInterval) x 6`
1. **Loop through each `timepoint`**
- For each `currentTP` in `timepoints`:
	- Load transformation file for the current timepoint
