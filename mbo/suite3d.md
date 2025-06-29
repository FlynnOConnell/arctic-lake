# Suite3D Notes

## Suggestions

One thing I think would be helpful is a way to first find the range of values you might want to use for the grid search with a very wide net i.e. [1, 15, 45, 90] and then do another smaller subset.

## Steps

- Randomly selects frames (init_n_frames), make this ~100 frames
- Not set up for building - need to run from within the root project dir
- if ops["subfolders"], then all tiffs ops["data_path"][0] / ops["subfolders"] / *.tif
  if ops["look_one_level_down"], then all tiffs in all folders + one level down
  if ops["tiff_list"], then ops["data_path"][0] / ops["tiff_list"] ONLY
- Any more than 500 frames, ref-img calculation fails
- More than 5000 frames in a single tiff, gpu registration fails
- GPU is still used for registration even when gpu_reg=False , very difficult to debug / step through code
- Notebook / debug script needs to be run withing the suite3d directory
- Shape mismatches whenever I tried to subsample, memory allocation errors when I tried to proceed without subsampling. Fixed by removing 1/2 of kevins 03/01 mk301 tiffs 
- "Fuse strips" aka assembly, can happen during registration or standalone after registration. Incompatible with current methodology to fuse strips but started a discussion for how to use pre-fused/assembled z-planes for this pipeline

## Corrmap only params

corr_map_params = {dict: 14} {
'cell_filt_type': 'gaussian',
'cell_filt_xy_um': 5,
'cell_filt_z_um': 17,
'detection_timebin': 1,
'edge_crop_npix': 7,
'fix_vmap_edge_planes': False,
'intensity_thresh': 0.3,
'npil_filt_type': 'gaussian',
'npil_filt_xy_um': 5,
'npil_filt_z_um': 15.0,
'voxel_size_um' = {tuple: 3} (17, 2, 2)
'temporal_hpf' = {int} 200
'edge_crop_npix' = {int} 7
'npil_filt_type' = {str} 'gaussian'
'npil_filt_z_um' = {float} 15.0
'npil_filt_xy_um' = {int} 5
'cell_filt_type' = {str} 'gaussian'
'cell_filt_z_um' = {int} 17
'cell_filt_xy_um' = {int} 5
'fix_vmap_edge_planes' = {bool} False
'detection_timebin' = {int} 1
'sdnorm_exp' = {float} 0.75
'intensity_thresh' = {float} 0.3
'standard_vmap' = {bool} True

Best:


array({
'fs': 17.06701142272251,
'tau': 1.3,
'voxel_size_um': (17, 2, 2),
'planes': array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13]), 
'convert_plane_ids_to_channel_ids': False,
'n_ch_tif': 14,
'skip_roi': None,
'lbm': True,
'faced': False,
'faced_nz': None,
'multiplane_2p_use_planes': None,
f'notch_filt': None, 'fix_fastZ': False, 'num_colors': 1, 'functional_color_channel': 0, 'save_dtype': 'float16', 'n_init_files': 1, 'init_file_pool': None, 'init_file_sample_method': 'even', 'init_n_frames': None, 'enforce_positivity': True, 'fix_shallow_plane_shift_estimates': False, 'fix_shallow_plane_shift_esimate_threshold': 20, 'overwrite_plane_shifts': None, 'subtract_crosstalk': False, 'override_crosstalk': None, 'crosstalk_percentile': 99.5, 'crosstalk_sigma': 0.01, 'cavity_size': 1, 'crosstalk_n_planes': 2, 'fuse_strips': True, 'fuse_shift_override': 1, 'max_rigid_shift_pix': 150, 'plane_to_plane_alignment': True, 'gpu_reg_batchsize': 10, 'max_shift_nr': 3, 'nr_npad': 3, 'nr_subpixel': 10, 'nr_smooth_iters': 2, 'pc_size': array([ 2, 40, 40]), '3d_reg': True, 'gpu_reg': True, 'percent_contribute': 0.9, 'block_size': [64, 64], 'sigma_reference': (1.45, 0), 'smooth_sigma_reference': 1.15, 'n_reference_iterations': 8, 'max_reg_xy_reference': 100, 'gpu_reference_batch_size': 20, 'nonrigid': True, 'apply_z_shift': False, 'smooth_sigma': 1.15, 'maxregshift': 0.15, 'reg_filter_pcorr': 1, 'reg_norm_frames': True, 'generate_sample_registered_bins': False, 'tif_batch_size': 1, 'n_skip': 13, 'fuse_crop': None, 'split_tif_size': 100, 'svd_crop': None, 'svd_time_crop': (None, None), 'n_svd_comp': 50, 'svd_block_shape': (4, 200, 200), 'svd_block_overlaps': (1, 50, 50), 'svd_pix_chunk': None, 'svd_time_chunk': 4000, 'svd_save_time_chunk': 400, 'svd_save_comp_chunk': 100, 'n_svd_blocks_per_batch': 1, 'sdnorm_exp': 0.75, 'edge_crop_npix': 7, 'npil_filt_type': 'gaussian', 'npil_filt_xy_um': 5, 'npil_filt_z_um': 15.0, 'cell_filt_type': 'gaussian', 'cell_filt_xy_um': 5, 'cell_filt_z_um': 20, 'intensity_thresh': 1, 'standard_vmap': True, 'temporal_hpf': 200, 'fix_vmap_edge_planes': False, 't_batch_size': 100, 'mproc_batchsize': 5, 'n_proc': 16, 'n_proc_corr': 12, 'n_proc_detect': 16, 'dtype': <class 'numpy.float32'>, 'peak_thresh': 0, 'patch_size_xy': (120, 120), 'patch_overlap_xy': (25, 25), 'activity_thresh': 20.0, 'percentile': 99.5, 'extend_thresh': 0.1, 'roi_ext_iterations': 2, 'ext_subtract_iters': 0, 'max_iter': 10000, 'detection_timebin': 6, 'segmentation_timebin': 1, 'detection_time_crop': (None, None), 'allow_overlap': False, 'recompute_v': None, 'normalize_vmap': False, 'max_pix': 250, 'detect_overlap_dist_thresh': 5, 'detect_overlap_lam_thresh': 0.5, 'npil_coeff': 0.7, 'npil_to_roi_npix_ratio': 8, 'min_npil_npix': 2, 'dcnv_baseline': 'maximin', 'dcnv_win_baseline': 60, 'dcnv_sig_baseline': 10, 'dcnv_prctile_baseline': 8, 'dcnv_batchsize': 3000, 'subjects_dir': None, 'subject': None, 'expnum': None, 'date': None,
