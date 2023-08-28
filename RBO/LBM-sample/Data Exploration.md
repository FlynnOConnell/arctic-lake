***
## 1) Current Pipeline  
<ins>Organize / Motion Correct</ins>

`assembleCorrectedROITiff.m`
- Taught me a good bit about ScanImage without having the actual software
- ScanImage needs more code and documentation on the python side
- C++ API is straight foreword 
- Consistent naming:
	- ROI/Strip, Frame/volume (framerate/volumerate), plane/channel
 - Inefficient array handling
	 - Duplicate variables, many copied / duplicated matrices
 

***
## Scalability
*memory mapping*
*parallel processing*
*multithreading*
***
## **Matlab vs Python** 

##### `CaImAn.m`
- Issue with parallel pool workers
-  12 core limit in the future could be an issue


	| Var             | Val.m    | Val.py |     |
	| --------------- | ------------- | ---------- | --- |
	| pixelResolution | 2.7778        |            |     |
	| vol             | 669 x 660 x 30 x 65 |            |     |
	| volumeRate      | 6.4496        |            |     |

##### `CaImAn.py`

**The Mesoscope** 
- Software is behind, `ScanImage.py` particularly 
- JSON Encoding/Decoding (Very Slow)

**.tif or .hdf5 files?**
- .tif need to be sequentially loaded into memory
- .hdf5 do not

*Matlab Engine for Python*
- Immature, poorly maintained
- Improper data-type conversions
	- Cell Arrays != python arrays 
	- Structure Arrays != dictionaries 

- Matlab array slicing is less strict, more vulnerable to errors and less consistent/predictable
	- Indexing outside of the bounds of an array, matlab increases the size of the array to accommodate the slice.. padding missing vals with zeros
	- This happens when calculating the offset - k
***

1) Spatial downsampling
2) Frequency Filter / FFT
3)  NormCorre Motion Correction
4) Extract dF/F
5) CNMFe / Cell Extraction
6) Event Detection, if necessary
