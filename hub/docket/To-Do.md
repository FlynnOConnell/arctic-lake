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
- Focus isoview entirely, touch base again mid august
- Powerpoint, include the locations of files
- CHN01 CM00 Cm01 comparisons
	- A,B,C parameters -> Powerpoint
- Iso Standards: Date, animal gender/age, etc
- Keep the job_parameters file next to / traveling with data
- RBO-S1
	- Double check links - format properly
	- Move over extract outputs

* [ ] Wordpress Fixes
	* [x] LBM Images ✅ 2025-07-19
		* [x] main changes
		* [x] figure caption for red/blue/yellow, what are these?
		* [ ] new pics of microscopes
	* [x] IsoView Images ✅ 2025-07-19
		* [x] Make 2
	* [x] Main Page Images
- [ ]  Microscopy Meetups
- Look / ask for in imageSC

- [ ] IsoView Processing [[IsoView - Processing]]
	- [x] First pass code review ✅ 2025-08-15
		- [x] Gather intermediates, main steps, reused code ✅ 2025-07-30
		- [x] Step through and test some different parameters when possible, want to be able to test how some of the big params effect the end product later on ✅ 2025-07-30
- [ ] MultiView Deconvolution
	- Cuda 9.0?
* [ ] mbo_utilities - toward `mbo_utilities v2.0`
	* [ ] z-plane alignment
		* [ ] vectors needed for shifting z-planes
		* [ ] function to apply shifts
		* [ ] apply these vectors to reg/detection results (vcorr, max_proj, all summary images)
	* [ ] roi merging
		* [x] [[lbm merge rois (suite2p)]] ✅ 2025-07-21
		* [x] planeN combined folders ✅ 2025-07-21
		* [ ] Allow merging N rois
		* [ ] fit into pipeline (mbo_utilities)
		* [ ] rebuild rois that were cut off
			* [ ] need to think about this
			* [ ] could also lessen maxregshift param
			* [ ] can probably just re-seed edge mask
	* [ ] figure output bugfixes
		* [x] df/f traces ✅ 2025-08-21
		* [ ] noise histogram
		* [ ] segmentation color coding
	* [ ] docstrings
	* [ ] update user guide walkthroughs
	* [ ] Fix GUI statistics per-zplane when there is a single z-plane
* [ ] Santis dataset
	* [x] Run Santis params (floor threshold, Functional) ✅ 2025-07-19
	* [x] check contrast between rois ✅ 2025-07-22
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

## Future Ideas
- [ ] DATABASE: Organized database of dataset and metadata for that dataset
	- [ ] Someway to easily find the parameters for a dataset
