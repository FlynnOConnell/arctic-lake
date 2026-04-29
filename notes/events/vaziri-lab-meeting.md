# Vaziri Lab Meeting
## Yao Wang
- MAX-HR
- MAX-EX upgrade to 2p-ram
- PSF1 and 14 look very similar
	- Axial: 6mm theory, 5.99 +/- 0.08 mm
	- Lateral: 240um theory, 240.6
	- Aim is 4% power falloff, measured 6.21 +/- 0.44
- More abberation on edge beads than in the center beads
	- Cavity A/B are identicle (roughly)
- Separation should be 1um, but we're getting 1.48um +/- 0.18 um
- PSF stays relatively consistent through the cavities

## Kalyan 09/16/25

Discriminablity index (d')
- D' = 3 = 93% accurate spike detection

2026-03-17

Volate mini2p, looking towards multiplexing (lateral)


## Arash 09/09/25
- Memory, working memory in M2
- Interested in duration of responses following a visual task - correlate of working memory
	- How long is the delay of "persistent activity"
- Odor association task, A/B + C/D = Lick, otherwise don't, fast learning ~5-10 days
- L5 ~500um
- L5 is highly delayed in choice selective neurons
- Thursday @4pm, Imaging Journal club to finish this up

## Kevin 8/26
- Arash, collab with JinKun
- M2, supplimentary motor cortex
- Intra-trial level, multi-trial level, session level
- Task scales, behavioral scales, representational scales
- Multiple Scales
	- Task Scales
		- stimulus, choice, outcome
	- Session Level
		- Repeated trials
		- Mice might fluctuate decision making strategies
	- Multi-Trial Level
	- Behavioral Scales
		- Different stim strengths, contrasts effect response time
	- Representational Scales
- SVM classifier to distinguish behvaiors at the choice epoch
- Identify choice-selective neurons
- Tensor-component AAnalysis, trial dimension normally collapsed
- Choice selective neurons, binned by session (session 11-5, 6-12 etc..
	- Initially, many reward selective neurons
	- After outcome, activity of that population is provoked
	- After learning, that ratio of the error neurons > reward active neurons
	- Reinforcement learning / expectation conflict?
- GLM, log scaled based on contrast, negative sign = left / right trial, 1 or 0 for choice to left or right
	- Win-stay, lose-switch strategy
	- Gives the weights that apply to the full session
	- How well does this model predict mouse performance
	- Evaluate with per-trial log-likelyhood
	- -0.04 log likelyhood
	- static over movie, need something dynamic (Hidden marcov)
- Latent neural embeddings to guide model selection?
- SPARKS (sequential predictive autoencoder;)

## Christian Jennings
Robust BEAST in-vivo imaging 
- max FOV: 4.2mm by 4.2mm
- roi dimensionality is conserved, don't overlap scanfields or there will be substantially more crosstalk

## Hao 02/03/2026

- Hippocampus, episodic memory spatial nav
- DG, CA3, CA1 are heavily studies
	- pattern separation, information relay, pattern completion when you have partial ifnormation
- simultaneous CA1 CA3, how do these work together in spatial location, context and reward
- When novel env, how does this change / rema-?

- 2p / 3p at 1-2mm x 1-2mm x 0.5mm @>=10hz


## Christian 2026-02-24: Beast mesoscope

- ~ 5 mm for 2pram 2.5mm XY offset of each mux beam
- theoretically 4x the acquisition rate, parallel opto stimulation
- scale total neurons of 2021 LBM paper, equivalent FOV, should be around 800-1000 neurons
- ideally more since FOV provides greater temporal sampling
- calibration taken at a different time than the recording
- transgenic gcamp8s 
- Crosstalk subtraction

- Find that missing 20%
- didn't factor in improvement from GCaMP6s to GCaMP8s 


## Christian 2026-04-11: Updates 

- Opto
- 
