# Performance Review

## Review Period: January 2024 to May 2025

### 1. Significant Accomplishments

I significantly contributed to advancing the data processing and analysis capabilities at the Miller Brain Observatory (MBO). Specifically:

* Developed and implemented **LBM-Suite2p-Python**, an end-to-end data processing pipeline utilized by Dr. Gilbert's lab. This pipeline efficiently converts planar imaging data into neuronal signals with complementary summary images and statistics, meticulously documented. \[1\]\[2\]\[3\]

* Engineered **mbo\_utilities**, a modular and portable software package enabling easy conversion and integration of MBO-specific datasets into widely accepted formats (TIFF, Zarr, HDF5, BIN). This pipeline allows users to choose an analysis pipeline based on data quality and is extensively documented.

* Primary developer/maintainer on **fastplotlib**, optimized to handle large MBO datasets entirely on the GPU by improving computational efficiency and compatibility through regular collaboration and contributions. \[5\]

---
### 2. Development Goals Achievement

I successfully met or exceeded development goals through:
* Improved and documented previous processing pipelines (**LBM-CaImAn-MATLAB**, **LBM-CaImAn-Python**), significantly improving user accessibility and processing speed.
* Maintenance of streamlined analysis and storage pipelines via the **MBO HUB**
* Active participation in open-source software communities, notably as a maintainer of **fastplotlib, masknmf, Suite3D**
* Collaborated with the broader scientific community via developer talks and workshops [\[6\]](https://www.rockefeller.edu/events-and-lectures/61525-fastplotlib-a-high-level-library-for-ultra-fast-visualization-of-large-datasets-using-modern-graphics-apis/)
* Authored comprehensive SOPs covering infrastructure, environment setup, light-beads-microscopy characteristics, and code deployment across services

---

### 3. Development Goals for the Coming Year

* Deepen expertise in calcium imaging technologies and methodologies; measured by successful deployment of new pre/postprocessing routines
* Strengthen external connections via organized collaborations and invited talks
* Integrate cutting-edge analytical software upon release; measured by implementation success and user feedback
* Promote MBO technologies at conferences; evaluated by visibility, engagement, and collaborations

---

### References and Links

\[1\] [https://github.com/pygfx/wgpu-py/issues/700#issuecomment-2784103774](https://github.com/pygfx/wgpu-py/issues/700#issuecomment-2784103774)
\[6\] [https://www.rockefeller.edu/events-and-lectures/61525-fastplotlib-a-high-level-library-for-ultra-fast-visualization-of-large-datasets-using-modern-graphics-apis/](https://www.rockefeller.edu/events-and-lectures/61525-fastplotlib-a-high-level-library-for-ultra-fast-visualization-of-large-datasets-using-modern-graphics-apis/)
\[7\] [https://github.com/apasarkar/masknmf-toolbox/pull/14#event-17758143438](https://github.com/apasarkar/masknmf-toolbox/pull/14#event-17758143438)
\[8\] [https://github.com/fastplotlib/fastplotlib/pull/791#issuecomment-2799023358](https://github.com/fastplotlib/fastplotlib/pull/791#issuecomment-2799023358)
\[9\] [https://github.com/fastplotlib/fastplotlib/pull/721#event-17211554416](https://github.com/fastplotlib/fastplotlib/pull/721#event-17211554416)
\[10\] [https://github.com/alihaydaroglu/suite3d/pull/95](https://github.com/alihaydaroglu/suite3d/pull/95)
\[11\] [https://github.com/jupyterlab/jupyterlab/issues/17507#issuecomment-2835977859](https://github.com/jupyterlab/jupyterlab/issues/17507#issuecomment-2835977859)

---

### Responsibilities Alignment

* **Evaluate, apply, refine analysis software**: Active developer on Suite3D, MaskNMF, fastplotlib
* **Develop scalable pipelines**: LBM-Suite2p-Python, mbo\_utilities, GUI in progress
* **Hardware/software troubleshooting**: Resolved severe GPU driver issue with vendor-level debugging ([link](https://github.com/pygfx/wgpu-py/issues/700))
* **Maintain compute servers**: Supported concurrent high-demand users on Windows Server and Unix systems

---

### Additional Contributions

* LBM-CaImAn-MATLAB: Improved pipeline and documentation
* LBM-CaImAn-Python, MaskNMF, Suite3D: New pipelines developed
* MBO HUB: Maintained data infrastructure
* fastplotlib: Maintainer and optimization lead for large datasets
* SOPs and user training: Authored and maintained documentation for collaborators

---

### Qualifications Alignment

* Extensive experience with imaging libraries (SciPy, Dask, Napari, Neuroglancer)
* Strong GPU workflow expertise (HPC/Windows/Linux)
* Maintainer of Git-based projects, deep involvement in collaborative research software
* ML exposure with practical integration plans

---
## Neurodata Rehack Proposal

**Title**: Systematic Evaluation of Processing Strategies and Data Quality in Two-Photon Calcium Imaging

This project addresses challenges in mesoscopic calcium imaging: noise, contamination, motion, overexpression, and varying quality across datasets. We aim to compare multiple analysis pipelines and quantify their effectiveness under diverse quality regimes.

Wrappers like NeuroWRAP and CIAtah simplify preprocessing, but decision rationale remains opaque. This project will develop guidance for tool selection based on empirical metrics and integrate evaluation interfaces into existing software stacks.

---

### References

* Suite3D [Hardaroglu et al., 2025](https://www.biorxiv.org/content/10.1101/2025.03.26.645628v1)
* NeuroWRAP [Bowen et al., 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10166805/)
* CIATAH [Corder et al., 2019](http://science.sciencemag.org/content/363/6424/276.full)
* Minian [Dong et al., 2022](https://elifesciences.org/articles/70661)
* CaImAn [Giovannucci et al., 2017, 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC10166805/#B6)
* Suite2p [Pachitariu et al., 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC10166805/#B11)
* CITE-on [Zhou et al., 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC10166805/#B17)
* EZcalcium [Cantu et al., 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC10166805/#B2)
* MASKNMF [Pasarkar et al., 2023](https://www.biorxiv.org/content/10.1101/2023.09.14.557777v1)
* AUTOTUNE [Yiyi Yu et al., 2024](https://pubmed.ncbi.nlm.nih.gov/38628980/)
* EXTRACT [Din\u00e7 et al., 2024](https://www.biorxiv.org/content/10.1101/2021.03.24.436279v3.full.pdf)

## Review Period: July 2025 to July 2026