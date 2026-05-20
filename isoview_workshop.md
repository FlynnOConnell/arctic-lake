
### Concepts for Isoview workshop

- Image larger specimens at a higher resolution and higher frame rate by introducing additional detections.
- Each view is limited in the resolution it can provide, but views can be combined with high resolution in all dimensions

### Pros / Cons

Pros: 
- higher resolution imaging of larger samples, allows functional, whole brain, multicolor, 
- no increased photodamage
- maintain fast camera-dependent frame rate

Cons: 
- highly light-scattering tissue will not work well
- limited lateral motion of the sample during acquisition
- depth-dependand signal loss
- complex post-processing computation

### Walkthrough

1. Intro to the data: view raw `.stacks`

Orient ourselves with the diagram, sharp features in both cameras exist at different depths.
Briefly, what comes out of the microscope (raw .stacks).

`uv run mbo D:\isoview_pipeline_demo\Dme_E1_57C10_GCaMP6s_Simultaneous_6p22_20150528_163012\v0-1-4\Dme_E1_57C10_GCaMP6s_Simultaneous_6p22_20150528_163012\`

`uv run mbo D:\isoview_pipeline_demo\Dre_HuC_H2BGCaMP6s_0-1_20150709_195932.corrected.registered\SPM00`

2. Camera-camera blending

Show Dre_HUC after camera-camera fusion (CM -> VW)


3. Show the tiled-midgut dataset in its final, fused form. 




## Isoview Axis:

X: ceiling to floor (vertical/gravity axis)
Y: horizontal
Z: horizontal (detection/scan axis)
Y-scan camera (CM02/CM03)
The scan axis is Y, so in raw data the "slow" axis is Y. To align with the Z-scan camera (CM00/CM01), you need to swap the scan axes.

