---
tags:
  - weekly
  - meeting
  - log
  - mbo
template: Weekly Meetings
updated_date: <% tp.date.now("YYYY-MM-DD") %>
created_date: <% tp.file.creation_date("YYYY-MM-DD") %>
category: mbo
---
# TO DO

* [ ] Wordpress Fixes
	* [x] LBM Images ✅ 2025-07-19
		* [x] main changes
		* [x] figure caption for red/blue/yellow, what are these?
		* [ ] new pics of microscopes
	* [x] IsoView Images ✅ 2025-07-19
		* [x] Make 2
	* [x] Main Page Images
- [ ] IsoView Processing [[IsoView Processing]]
* [ ] Pollen Beads [[mROI contrast Testing]] 
  * [x] Pull Data
  * [ ] Analyze
	  * [x] Check metadata, roi locations (python) ✅ 2025-07-17
	  * [ ] Fix `output_xslices` on overlapping mROIs
	  * [x] Does MATLAB pollen_calibration utilities work? ✅ 2025-07-17
	  * [x] mean-subtracted image
	  * [x] PMD to Amol ✅ 2025-07-17
* [ ] mbo_utilities - toward `mbo_utilities v2.0`
	* [ ] z-plane alignment
	* [ ] roi merging
		* [x] [[merge suite2p datasets]] ✅ 2025-07-21
		* [ ] plane01_roi1 -> plane01_roi01
	* [x] Metadata parser ✅ 2025-07-19
	* [x] run_plane ✅ 2025-07-19
	* [x] run_volume ✅ 2025-07-19
	* [ ] figure output bugfixes
		* [ ] df/f traces
		* [ ] noise histogram
		* [ ] segmentation color coding
	* [ ] docstrings
	* [ ] update user guide walkthroughs
	* [ ] Fix GUI statistics per-zplane when there is a single z-plane
* [ ] Santis dataset
	* [x] Run Santis params (floor threshold, Functional) ✅ 2025-07-19
	* [ ] check contrast between rois 
	* [ ] Compare with `Cellpose3/Cellpose-SAM`
* [ ] Documentation (and guides i want to add)
	* [ ] DF/F
	* [ ] Finish last section
	* [ ] !Careful Review of Documentation
		* [x] mbo_hub ✅ 2025-07-19
		* [ ] lbm_suite2p_python
		* [x] mbo_utilities ✅ 2025-07-20

## General / Misc
- Janelia Researchers using [Fastplotlib](https://github.com/fastplotlib/fastplotlib/issues/672#issuecomment-3090487239)
- [[mbo server]]
- User accounts: grant perms in user_data folder
- Rename RBO - Projects
- W1 Archives are filling drives

## Future Ideas
- [ ] DATABASE: Organized database of dataset and metadata for that dataset
	- [ ] Someway to easily find the parameters for a dataset