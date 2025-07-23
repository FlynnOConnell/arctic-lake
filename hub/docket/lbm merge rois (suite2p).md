---
created: <% tp.file.creation_date("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - lbm
  - suite2p
  - calcium-imaging
aliases:
---
## Merging roi 1 and roi 2, processed separately

#suite2p #calcium-imaging #lbm 
**First pain point**
suite2p results for 2 datasets that need to be stitched together. The first dataset is the left half of the FOV, the second dataset is the right half of the FOV.

The problem is that suite2p crops the summary image differently depending on the motion in each dataset.

During registration we find the shifts in XY of the FOV, the maximum of these shifts determines the total possible area that can be used for cell extraction (we can't use areas that are always shifted out of the microscope). So we only extract cells on this smaller region (ops['yrange'], ops['xrange']), but then we define the cells' pixels based on their position in the full FOV.

## Steps
- Merge traces and metadata (F, Fneu, spks, stat, iscell)
``` python
def merge(name):
	left = np.load(roi_left / name)
	right = np.load(roi_right / name)
	return np.concatenate([left, right], axis=0)
	
stat_merged = np.concatenate([stat_left, stat_right], axis=0)
    iscell_merged = np.concatenate([iscell_left, iscell_right], axis=0)
F = merge_traces("F.npy")
Fneu = merge_traces("Fneu.npy")
spks = merge_traces("spks.npy")
```
- Adjust all `xpix`, `med[1]`, and `ipix_neuropil` x-positions from the right dataset by an x-offset

``` python
Ly = ops_left['Ly']
    Lx_left = ops_left['Lx']
    Lx_right = ops_right['Lx']
    Lx = Lx_left + Lx_right

    for s in stat_right:
        s['xpix'] = s['xpix'] + Lx_left
        s['med'][1] = s['med'][1] + Lx_left
        if 'ipix_neuropil' in s:
            s['ipix_neuropil'] = s['ipix_neuropil'] + Lx_left * Ly
```

-  Create a new `ops.npy` with the correct full `Lx`, `Ly`, and `xrange`/`yrange`

Suite2p gui expects cropped summary images to match range:
- (ops["yrange"][1] - ops["yrange"][0], ops["xrange"][1] - ops["xrange"][0])
- vcorr, max_proj only
- Merged now accepted as input in suite2p gui:
![[Pasted image 20250721191324.png]]
- Correlation map
![[Pasted image 20250721191732.png]]