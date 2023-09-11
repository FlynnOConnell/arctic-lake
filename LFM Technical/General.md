
- Long term storage / goals
	- Technical assessment of signal quality vs acquisition settings
- Maintaining variables like pixel_res with h5 but not mmap

Get the data out there in the world
- File types 
	- CaImAn: .mmap
	- Suite2p: prefer npy/nwb
	- NWB becoming standard? 
 
!! Abstract away the filesystem
- Janelia Workstation / data sharing
	- [MouseLight](https://www.janelia.org/project-team/mouselight/members)

- Start with the desired output, the ===y_pred===
- Don't start building deployment-ready applications until the software is fool-proof

[RAMP](https://ramp.studio/#features)Community to test/prototype M/L workflows

Consider working with institutions like [Inscopix](www.inscopix.com) C++ open source `CNMFe` 

- MoJo - New python interpreter 
### CNMF vs Cellpose
| Method:  | MotionC  | Segmentation | Devoncolution        |     |
| -------- | -------- | ------------ | -------------------- | --- |
| CellPose | In-house |              | non-neg devonv (NDD) |     |

- Deconvolution: NND outperforms CNN
	- LO to prevent some autocorrelations

