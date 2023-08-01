- Emphasis on theoretical models, well vetted

# OB and LFP (β activity)
- Odors generate spatially specific patterns
	- LFP -> β (15-40 Hz) and γ (60-90 Hz) bands
	- Using electrodes in Mitral Cell Body Layer
	- Differences between anterodorsal and posteroventral OB
		- β oscillatory activity important for olfaction learning
- LFP signals are 
	1) *amplified(600x)* 
	2) *filtered(0.1-300hz)* 
	3) *digitized(samp freq. 2000hz* 
- Mortet Wavelet Transform: 
	- Variable size window, wider for low f, narrow for high f
	- good for LFP's, f changes over time
	- more precise time-f rep because it adapts its time-f res to the f its analyzing
- Hilbert-Huang Transform:
	- Decompose into intrinsic mode functions (IMFs)
	- Apply 'Hilbert Spectral Analysis' to these IMFs
		- Adaptive, data-driven
	- Great for non-linear, non-stationary data
- Empirical Mode Decomposition (EMD)
	- Same IMF's, based now on local time scales of the signal
	- Hilbert Transform now gives instantaneous f as a function of time 

