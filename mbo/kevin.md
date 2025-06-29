# Mission - combine levels of behavior

Learn behavior over many sessions, over many days. 

- many weeks to becomem effective
- plasticity, changing over days
- Sessions are made of repeated trials, can be left or right side
- What states are changing over minutes or multiple trials 
- Incorperate learning
- Most analysis at intra-trial level, which neurons active around these trial variables (stimulus, choice or outcome of the trial)
- Effective to focus on longer timescales because of slow calcium dynamics

## Estimating cell-ness and SNR

- Take 99th percentile, apply dF, dF/F0, z-score methods
- F0: running 40th percentile over 30s window
- SD: take values <F0, Median Absolute Deviation, estimate SD 
- Does cellpose classifier operate on any temporal information 
- Histograms of frames to see distribution
- Clearly state what you do, how do you define an active neuron?
- Santi uses anova to get groups and then stats in the group
- Caiman uses median over window of 8th percentile
- Tobias: anything faster than e.g. 10hz, because fr is faster than indicator
- Perspectives: Justification for thresholds
