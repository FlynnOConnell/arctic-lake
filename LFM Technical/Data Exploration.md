***
## 1) Current Pipeline  
<ins>Organize / Motion Correct</ins>

`assembleCorrectedROITiff.m`
- Taught me a good bit about ScanImage without having the actual software
- ScanImage needs more code and documentation on the python side
- C++ API is straight foreword 
- Consistent naming:
	- ROI/Strip, Frame/volume (framerate/volumerate), plane/channel
 - Memory management 
	 - Save to disk 
	 - Memory mapped files "np.memmap"
	 - Better data types -> array vectorization rather than chunking
	 - `Rust` for safe memory management
		 - Dask deployment clusters with `futures`
		 - Involve a resource manager, kubernetes
 
***
## **Matlab vs Python** 

##### `CaImAn.m`
- Issue with parallel pool workers
-  12 core limit in the future could be an issue

##### `CaImAn.py`

**The Mesoscope** 
- Software is behind, `ScanImage.py` particularly 
- JSON Encoding/Decoding (Very Slow)

**.tiff or .hdf5 files?**


- Matlab array slicing is less strict, more vulnerable to errors and less consistent/predictable
	- Indexing outside of the bounds of an array, matlab increases the size of the array to accommodate the slice.. padding missing vals with zeros
	- This happens when calculating the offset - k
***

1) Spatial downsampling
2) Frequency Filter / FFT
3)  NormCorre Motion Correction
4) CNMFe 
5) Extract dF/F
6) Event Detection, if necessary

```
roi_data - len(roi_data) = number of ROIs  
- RoiData Object (class)  
- zs (z stack)  
- channels (channels, the same for each ROI) 
- 
- imageData (container)  
	- len(imageData) = number of planes (z)  
		- len(imageData[0]) = number of frames/volumes (time)  
			- len(imageData[0][0]) = number of "slices", but this will always be 1 for us  
				- imageData[0][0][0] = the actual 2D cross-section of the image

```
