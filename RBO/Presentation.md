Single Plane? The image represents the average activity across a certain depth of tissue. Inscopix miniscope

Video data saved as `HDF5` for analysis

## Challanges
- Movement artifact 
	- FOV Shifts: hindbrain, tissue underneath the lens shifts by a couple hundred microns
	- Increasing max translation to 30
- Cell Identification (CNMFe)
	- *Too many cells/oversegmentation*: CNMFe, reduce merging threshold
	- *Not enough cells*: reduce minimum pixel correlation + mean peak:noise
	- *Slow processing*: Parallel -> Sequential 
 
## Results
High trial-by-trial viariability

## Future Implication

## Notes
- Controversial, "brainstem" too difficult. Lot's of nit-picking.

Voxels  - moving toward cellular resolution -> Computationally heavy

10hz Frame Rate
100ms exposure time (vs 20hz -> 50ms)
Each neuronal time series was de-trended individually to correct for photo-bleaching, and then normalized as DF/F0 = (F-F0)/F0,
where F is the fluorescence of the neuron at a given time point and F0 is the average fluorescence of the neuron across the entire
recording. Noise was removed via total variation regularization by calculating the cumulative sum of the de-noised time derivatives
(Chartrand, 2011). The de-noised time series X of each neuron were then normalized by taking the Z-score, given as (X – mean(X))/
SD(X), for further analysis. This pre-processing procedure and subsequent analyses were performed using MATLAB (MathWorks)