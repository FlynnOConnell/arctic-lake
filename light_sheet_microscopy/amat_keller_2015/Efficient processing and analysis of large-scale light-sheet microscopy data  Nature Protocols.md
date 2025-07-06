---
created: 2025-07-06T10:27:07 (UTC -04:00)
tags: []
source: https://www.nature.com/articles/nprot.2015.111
author: Keller, Philipp J
---

# Efficient processing and analysis of large-scale light-sheet microscopy data | Nature Protocols

> ## Excerpt
> The Keller lab describes a detailed protocol for processing large multidimensional imaging datasets obtained from light-sheet microscopy. Light-sheet microscopy is a powerful method for imaging the development and function of complex biological systems at high spatiotemporal resolution and over long time scales. Such experiments typically generate terabytes of multidimensional image data, and thus they demand efficient computational solutions for data management, processing and analysis. We present protocols and software to tackle these steps, focusing on the imaging-based study of animal development. Our protocols facilitate (i) high-speed lossless data compression and content-based multiview image fusion optimized for multicore CPU architectures, reducing image data size 30–500-fold; (ii) automated large-scale cell tracking and segmentation; and (iii) visualization, editing and annotation of multiterabyte image data and cell-lineage reconstructions with tens of millions of data points. These software modules are open source. They provide high data throughput using a single computer workstation and are readily applicable to a wide spectrum of biological model systems.

---
Introduction
------------

Light-sheet microscopy is an optical sectioning technique<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 1" title="Voie, A.H., Burns, D.H. &amp; Spelman, F.A. Orthogonal-plane fluorescence optical sectioning: three-dimensional imaging of macroscopic biological specimens. J. Microsc. 170, 229–236 (1993)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR1" id="ref-link-section-d543302138e363">1</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 2" title="Fuchs, E., Jaffe, J., Long, R. &amp; Azam, F. Thin laser light sheet microscope for microbial oceanography. Opt. Express 10, 145–154 (2002)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR2" id="ref-link-section-d543302138e366">2</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 3" title="Huisken, J., Swoger, J., Del Bene, F., Wittbrodt, J. &amp; Stelzer, E.H.K. Optical sectioning deep inside live embryos by selective plane illumination microscopy. Science 305, 1007–1009 (2004)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR3" id="ref-link-section-d543302138e369">3</a></sup> that provides high imaging speed and high spatial resolution over long periods of time, while minimizing energy load on the biological system under observation<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 4" title="Keller, P.J., Schmidt, A.D., Wittbrodt, J. &amp; Stelzer, E.H. Reconstruction of zebrafish early embryonic development by scanned light sheet microscopy. Science 322, 1065–1069 (2008)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR4" id="ref-link-section-d543302138e373">4</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 5" title="Ahrens, M.B., Orger, M.B., Robson, D.N., Li, J.M. &amp; Keller, P.J. Whole-brain functional imaging at cellular resolution using light-sheet microscopy. Nat. Methods 10, 413–420 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR5" id="ref-link-section-d543302138e376">5</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 6" title="Wu, Y. et al. Spatially isotropic four-dimensional imaging with dual-view plane illumination microscopy. Nat. Biotechnol. 31, 1032–1038 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR6" id="ref-link-section-d543302138e379">6</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 7" title="Krzic, U., Gunther, S., Saunders, T.E., Streichan, S.J. &amp; Hufnagel, L. Multiview light-sheet microscope for rapid in toto imaging. Nat. Methods 9, 730–733 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR7" id="ref-link-section-d543302138e382">7</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 8" title="Tomer, R., Khairy, K., Amat, F. &amp; Keller, P.J. Quantitative high-speed imaging of entire developing embryos with simultaneous multiview light-sheet microscopy. Nat. Methods 9, 755–763 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR8" id="ref-link-section-d543302138e385">8</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 9" title="Schmid, B. et al. High-speed panoramic light-sheet microscopy reveals global endodermal cell dynamics. Nat. Commun. 4, 2207 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR9" id="ref-link-section-d543302138e388">9</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 10" title="Holekamp, T.F., Turaga, D. &amp; Holy, T.E. Fast three-dimensional fluorescence imaging of activity in neural populations by objective-coupled planar illumination microscopy. Neuron 57, 661–672 (2008)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR10" id="ref-link-section-d543302138e392">10</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 11" title="Truong, T.V., Supatto, W., Koos, D.S., Choi, J.M. &amp; Fraser, S.E. Deep and fast live imaging with two-photon scanned light-sheet microscopy. Nat. Methods 8, 757–760 (2011)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR11" id="ref-link-section-d543302138e395">11</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 12" title="Gao, L. et al. Noninvasive imaging beyond the diffraction limit of 3D dynamics in thickly fluorescent specimens. Cell 151, 1370–1385 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR12" id="ref-link-section-d543302138e398">12</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 13" title="Chen, B.C. et al. Lattice light-sheet microscopy: imaging molecules to embryos at high spatiotemporal resolution. Science 346, 1257998 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR13" id="ref-link-section-d543302138e401">13</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 14" title="Keller, P.J. et al. Fast, high-contrast imaging of animal development with scanned light sheet-based structured-illumination microscopy. Nat. Methods 7, 637–642 (2010)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR14" id="ref-link-section-d543302138e404">14</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 15" title="Capoulade, J., Wachsmuth, M., Hufnagel, L. &amp; Knop, M. Quantitative fluorescence imaging of protein diffusion and interaction in living cells. Nat. Biotechnol. 29, 835–839 (2011)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR15" id="ref-link-section-d543302138e407">15</a></sup>. Owing to these powerful capabilities, light-sheet microscopy has emerged as a key method for live imaging in cell biology and developmental biology<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 16" title="Keller, P.J. Imaging morphogenesis: technological advances and biological insights. Science 340, 1234168 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR16" id="ref-link-section-d543302138e411">16</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 17" title="Pantazis, P. &amp; Supatto, W. Advances in whole-embryo imaging: a quantitative transition is underway. Nat. Rev. Mol. Cell Biol. 15, 327–339 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR17" id="ref-link-section-d543302138e414">17</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 18" title="Stelzer, E.H. Light-sheet fluorescence microscopy for quantitative biology. Nat. Methods 12, 23–26 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR18" id="ref-link-section-d543302138e417">18</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 19" title="Huisken, J. Slicing embryos gently with laser light sheets. Bioessays 34, 406–411 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR19" id="ref-link-section-d543302138e420">19</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 20" title="Pampaloni, F., Reynaud, E.G. &amp; Stelzer, E.H. The third dimension bridges the gap between cell culture and live tissue. Nat. Rev. Mol. Cell Biol. 8, 839–845 (2007)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR20" id="ref-link-section-d543302138e423">20</a></sup>, as well as in neuroscience<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 21" title="Keller, P.J., Ahrens, M.B. &amp; Freeman, J. Light-sheet imaging for systems neuroscience. Nat. Methods 12, 27–29 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR21" id="ref-link-section-d543302138e427">21</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 22" title="Keller, P.J. &amp; Ahrens, M.B. Visualizing whole-brain activity and development at the single-cell level using light-sheet microscopy. Neuron 85, 462–483 (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR22" id="ref-link-section-d543302138e430">22</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 23" title="Lemon, W.C. &amp; Keller, P.J. Live imaging of nervous system development and function using light-sheet microscopy. Mol. Reprod. Dev. 82, 605–618 (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR23" id="ref-link-section-d543302138e433">23</a></sup>. By capturing fast developmental and functional processes at the single-cell level across entire, complex biological systems, light sheet–based imaging can address fundamental biological questions that are not accessible with previous methods. In the domain of developmental biology, it has become feasible to systematically follow populations of progenitor cells as they form tissues, organs and even entire embryos. Such system-level cell-lineage reconstructions provide important insights into the stereotypy of developmental processes, link developmental history to cell function in the developmental building plan of an animal, aid in dissecting the role of differential gene expression in directing cell-fate decisions, and facilitate experimental validation of mechanistic models of development<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 24" title="Megason, S.G. &amp; Fraser, S.E. Imaging in systems biology. Cell 130, 784–795 (2007)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR24" id="ref-link-section-d543302138e437">24</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 25" title="Khairy, K. &amp; Keller, P.J. Reconstructing embryonic development. Genesis 49, 488–513 (2011)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR25" id="ref-link-section-d543302138e440">25</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 26" title="McMahon, A., Supatto, W., Fraser, S.E. &amp; Stathopoulos, A. Dynamic analyses of Drosophila gastrulation provide insights into collective cell migration. Science 322, 1546–1550 (2008)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR26" id="ref-link-section-d543302138e443">26</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 27" title="Fernandez, R. et al. Imaging plant growth in 4D: robust tissue reconstruction and lineaging at cell resolution. Nat. Methods 7, 547–553 (2010)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR27" id="ref-link-section-d543302138e446">27</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 28" title="Bosveld, F. et al. Mechanical control of morphogenesis by Fat/Dachsous/Four-jointed planar cell polarity pathway. Science 336, 724–727 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR28" id="ref-link-section-d543302138e449">28</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 29" title="Murray, J.I. et al. Automated analysis of embryonic gene expression with cellular resolution in C. elegans. Nat. Methods 5, 703–709 (2008)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR29" id="ref-link-section-d543302138e452">29</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 30" title="Liu, X. et al. Analysis of cell fate from single-cell gene expression profiles in C. elegans. Cell 139, 623–633 (2009)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR30" id="ref-link-section-d543302138e456">30</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 31" title="Trichas, G. et al. Multi-cellular rosettes in the mouse visceral endoderm facilitate the ordered migration of anterior visceral endoderm cells. PLoS Biol. 10, e1001256 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR31" id="ref-link-section-d543302138e459">31</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 32" title="Xiong, F. et al. Specified neural progenitors sort to form sharp domains after noisy Shh signaling. Cell 153, 550–561 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR32" id="ref-link-section-d543302138e462">32</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 33" title="Du, Z., Santella, A., He, F., Tiongson, M. &amp; Bao, Z. De novo inference of systems-level mechanistic models of development from live-imaging-based phenotype analysis. Cell 156, 359–372 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR33" id="ref-link-section-d543302138e465">33</a></sup>. In neuroscience, light-sheet microscopy has made it possible to perform functional imaging of large neuronal populations, entire brains<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 5" title="Ahrens, M.B., Orger, M.B., Robson, D.N., Li, J.M. &amp; Keller, P.J. Whole-brain functional imaging at cellular resolution using light-sheet microscopy. Nat. Methods 10, 413–420 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR5" id="ref-link-section-d543302138e470">5</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 34" title="Panier, T. et al. Fast functional imaging of multiple brain regions in intact zebrafish larvae using selective plane illumination microscopy. Front. Neural Circuits 7, 65 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR34" id="ref-link-section-d543302138e473">34</a></sup> and even the entire CNS<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 35" title="Lemon, W. et al. Whole central nervous system functional imaging in larval Drosophila. Nat. Commun. 6, 7924 (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR35" id="ref-link-section-d543302138e477">35</a></sup>. Such experiments have the potential to illuminate how large neural networks perform complex computations and generate behavior at the single-cell level<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 22" title="Keller, P.J. &amp; Ahrens, M.B. Visualizing whole-brain activity and development at the single-cell level using light-sheet microscopy. Neuron 85, 462–483 (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR22" id="ref-link-section-d543302138e481">22</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 36" title="Alivisatos, A.P. et al. The brain activity map project and the challenge of functional connectomics. Neuron 74, 970–974 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR36" id="ref-link-section-d543302138e484">36</a></sup>.

However, light-sheet imaging experiments produce vast amounts of complex image data; from long-term imaging of developing embryos to high-speed functional imaging of the brain, each light-sheet recording consists of up to several tens of terabytes of multidimensional image data (including three spatial dimensions, time and multiple color channels). Thus, data management, as well as image processing and data analysis, rather than the experiments themselves, can easily become the bottleneck on the path to biological discovery. A computational framework that addresses these challenges, and does so with high data throughput and at minimal cost to the investigator, is crucial for routinely recording light-sheet data sets and for extracting biologically relevant information.

Here we present detailed protocols for operating a computational pipeline that efficiently handles the spectrum of challenges encountered with light-sheet microscopy image data, from high-throughput lossless data compression to content-based multiview image fusion. We furthermore provide protocols and software for large-scale cell tracking in developmental image data sets, as well as for large-scale image data visualization and annotation.

### Development of the protocol

In the protocols presented here, we describe five main computational modules ([Figs. 1](https://www.nature.com/articles/nprot.2015.111#Fig1) and [2](https://www.nature.com/articles/nprot.2015.111#Fig2); [Supplementary Software 1](https://www.nature.com/articles/nprot.2015.111#MOESM269),[2](https://www.nature.com/articles/nprot.2015.111#MOESM270),[3](https://www.nature.com/articles/nprot.2015.111#MOESM271),[4](https://www.nature.com/articles/nprot.2015.111#MOESM272),[5](https://www.nature.com/articles/nprot.2015.111#MOESM273),[6](https://www.nature.com/articles/nprot.2015.111#MOESM274)): first, our block-based lossless compression file format for efficiently storing large amounts of image data and rapidly retrieving arbitrary regions of interest; second, MATLAB scripts for content-based registration and fusion of time-lapse, multiview image data; third, our Tracking with Gaussian Mixture Models (TGMM) software for automated large-scale segmentation and tracking of fluorescently labeled cell nuclei; fourth, a branch of the Collaborative Annotation Toolkit for Massive Amounts of Image Data (CATMAID)<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 37" title="Saalfeld, S., Cardona, A., Hartenstein, V. &amp; Tomancˇák, P CATMAID: collaborative annotation toolkit for massive amounts of image data. Bioinformatics 25, 1984–1986 (2009)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR37" id="ref-link-section-d543302138e524">37</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 38" title="Cardona, A. Collaborative annotation toolkit for massive amounts of image data (CATMAID) GitHub repository 
                  https://github.com/acardona/CATMAID
                  
                 (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR38" id="ref-link-section-d543302138e527">38</a></sup> for visualizing 5D microscopy data sets and editing associated cell tracking results; and fifth, MATLAB scripts for importing, analyzing and visualizing large-scale cell-lineage reconstructions.

**Figure 1: Overview of image processing and data analysis workflow.**

[![figure 1](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_Fig1_HTML.jpg)](https://www.nature.com/articles/nprot.2015.111/figures/1)

The computational framework described in our protocols addresses typical data management, image processing and data analysis challenges encountered in light-sheet microscopy experiments. Starting with the raw image data sets, which consist of up to several terabytes of 3D images recorded as a function of time and comprise up to several color channels and view angles, the computational modules described here facilitate rapid data compaction via adaptive image background and foreground detection, background masking and image compression in our lossless KLB file format optimized for large-scale image data and multicore CPU architectures; high-throughput content-based multiview image registration and fusion for SiMView-like multiview data sets comprising up to four orthogonal views; 3D drift correction, intensity normalization and adaptive background correction; automated segmentation and cell tracking using our software framework TGMM; large-scale image data visualization and editing of cell-lineage reconstructions using a branch of CATMAID for 5D light microscopy image data sets; and data import/export between TGMM, CATMAID and the commercial rendering software Imaris. All of these software modules can be used individually or as part of our integrated computational pipeline.

[Full size image](https://www.nature.com/articles/nprot.2015.111/figures/1)

**Figure 2: Lossless image compression and content-based multiview fusion.**

[![figure 2](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_Fig2_HTML.jpg)](https://www.nature.com/articles/nprot.2015.111/figures/2)

<mark style="background: #455A64;">The first set of modules in our computational framework for high-throughput image processing is designed for rapid lossless data compaction of single-view or multiview light-sheet microscopy data sets.</mark> Step I: acquisition of light-sheet microscopy image data. These raw images are used as input data in the next step. Step II: automated detection of image foreground and background; i.e., detection of image regions that correspond to parts of the specimen (foreground, shown in yellow) or to regions that are either outside the specimen or do not contribute fluorescent signal (background, shown in blue). <mark style="background: #FFD740;">Step III:</mark> masking of image background (i.e., populating the automatically detected background regions, which <mark style="background: #455A64;">contain</mark> only background noise, with zeros) and lossless <mark style="background: #7986CB;">compression</mark> of the image data using the KLB file format. Step IV: automated content-based multiview image registration and image fusion. Steps II and III are applicable to both single-view and multiview image data sets, whereas Step IV is designed for high-throughput image fusion of SiMView-like multiview data sets comprising up to four orthogonal views. These image processing steps combine the high-quality image information of all recorded views into a single, information-rich image stack of the entire specimen, and efficiently store the 3D image data in a lossless image format. Thereby, the pipeline markedly reduces the size of the raw image data (on average by a factor of 180, [Fig. 4](https://www.nature.com/articles/nprot.2015.111#Fig4)) without discarding or changing parts of the original 3D image data that contain potentially useful information. At the same time, the pipeline is real-time capable; that is, all processing steps are completed in less time than required for image acquisition itself ([Table 1](https://www.nature.com/articles/nprot.2015.111#Tab1)). Data compaction performance numbers are based on the fruit fly, mouse and zebrafish imaging experiments shown in [Figure 4](https://www.nature.com/articles/nprot.2015.111#Fig4). Scale bar, 50 μm.

[Full size image](https://www.nature.com/articles/nprot.2015.111/figures/2)

All protocols have been extensively tested on long-term _in vivo_ time-lapse recordings of multicellular organisms, such as fruit fly, zebrafish and mouse embryos, primarily using data generated with SiMView light-sheet microscopy<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 8" title="Tomer, R., Khairy, K., Amat, F. &amp; Keller, P.J. Quantitative high-speed imaging of entire developing embryos with simultaneous multiview light-sheet microscopy. Nat. Methods 9, 755–763 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR8" id="ref-link-section-d543302138e585">8</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e588">39</a></sup>. In addition, our processing pipeline has been successfully applied to other microscopy modalities, such as confocal fluorescence microscopes and commercial light-sheet microscopes<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e592">39</a></sup>, and other model systems, such as _Parhyale_ and _Platynereis_ embryos<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 40" title="Lauri, A. et al. Development of the annelid axochord: insights into notochord evolution. Science 345, 1365–1368 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR40" id="ref-link-section-d543302138e603">40</a></sup>, as well as fruit fly and zebrafish larvae<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 5" title="Ahrens, M.B., Orger, M.B., Robson, D.N., Li, J.M. &amp; Keller, P.J. Whole-brain functional imaging at cellular resolution using light-sheet microscopy. Nat. Methods 10, 413–420 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR5" id="ref-link-section-d543302138e607">5</a></sup>. Our framework tackles various large-scale image processing challenges, including the analysis of multiterabyte developmental image data sets for system-level cell tracking (with tens of millions of tracked cell locations per embryo)<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e611">39</a></sup> and management of multiterabyte functional image data sets produced by whole-brain<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 5" title="Ahrens, M.B., Orger, M.B., Robson, D.N., Li, J.M. &amp; Keller, P.J. Whole-brain functional imaging at cellular resolution using light-sheet microscopy. Nat. Methods 10, 413–420 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR5" id="ref-link-section-d543302138e615">5</a></sup> or whole-CNS<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 35" title="Lemon, W. et al. Whole central nervous system functional imaging in larval Drosophila. Nat. Commun. 6, 7924 (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR35" id="ref-link-section-d543302138e619">35</a></sup> calcium imaging. Moreover, our modules for image compression, multiview fusion, segmentation and cell tracking are also suitable for applications that require real-time performance; i.e., our pipeline is capable of processing speeds exceeding the data acquisition rate of the light-sheet microscope, using a single computer workstation equipped with a conventional compute unified device architecture (CUDA)-enabled graphics card.

### Comparison with other methods

One of the key challenges in developing computational tools for light-sheet microscopy image data is scalability. There is a vast amount of literature and software related to the computational problems discussed here, such as data compression, visualization, registration, segmentation and tracking. However, many of these existing approaches either break down or are too time-consuming and resource-intensive when applied to multiterabyte image data sets. In this section, we compare our computational modules with existing methods that have been tested in similar data sets in terms of image characteristics and (if applicable) size.

#### Image compression.

In our comparison of image-compression formats, we focus on formats that have found widespread use and that offer lossless compression capability, as researchers usually want to store an unaltered version of their data. JPEG 2000 is one of the most widely used image compression formats. However, although the JPEG 2000 standard provides a description of 3D compression, few implementations of this capability actually exist. Most software packages compress image data plane by plane, which is inefficient for retrieving arbitrary regions of interest in large multidimensional image volumes. Moreover, it is difficult to efficiently parallelize all JPEG 2000 coding and decoding steps, which makes it challenging to take full advantage of modern multicore computing hardware.

HDF5 is another popular container for image files. Aside from offering lossless data compression, HDF5 is capable of storing data in blocks for fast retrieval of arbitrary regions of interest. Unfortunately, the HDF5 interface does not parallelize writing operations, which negatively affects speed.

To overcome these limitations, we developed the Keller Lab Block (KLB) lossless image-compression format, which combines high compression ratios, fast read/write speeds and a flexible block architecture that enables efficient access to arbitrary regions of interest ([Figs. 3](https://www.nature.com/articles/nprot.2015.111#Fig3) and [4](https://www.nature.com/articles/nprot.2015.111#Fig4); [Supplementary Figs. 1](https://www.nature.com/articles/nprot.2015.111#Fig8),[2](https://www.nature.com/articles/nprot.2015.111#Fig9),[3](https://www.nature.com/articles/nprot.2015.111#Fig10)). Inspired by Parallel BZip2, a common Linux compression module, we partition images in 5D blocks and compress all blocks in parallel using BZip2. Both reading and writing operations are parallelized, and they scale linearly with the number of cores in the CPU ([Fig. 5](https://www.nature.com/articles/nprot.2015.111#Fig5)). In addition, we provide a simple API for interfacing the open-source C++ code with various platforms, as well as an interface file for the SWIG tool, which can be used to autogenerate wrapper code for various languages, including Java, C#, Python, Perl and R ([Supplementary Software 1](https://www.nature.com/articles/nprot.2015.111#MOESM269)).

**Figure 3: Performance comparison of lossless image compression formats.**

[![figure 3](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_Fig3_HTML.jpg)](https://www.nature.com/articles/nprot.2015.111/figures/3)

Performance of the KLB lossless compression format versus LZW-TIFF (green) and JPEG 2000 (blue) lossless compression formats with respect to compression ratio (first column), write speed (second column) and read speed (third column). The JPEG 2000 benchmark uses the multithreaded commercial library PICTools Medical SDK (Accusoft). A performance comparison of KLB and uncompressed TIFF formats is included as well (orange). LZW-TIFF and uncompressed TIFF benchmarks use the 'imread' and 'imwrite' functions provided by the Image Processing Toolbox in MATLAB. All performance data are provided as ratios with KLB performance in the numerator; i.e., ratios larger than one (gray lines) indicate superior performance of the KLB file format. The comparison was performed using a variety of fluorescence microscopy image data sets located on a high-performance network-attached storage server connected to the image processing workstation via 10 Gb s<sup>−1</sup> glass fiber. Benchmark data sets include SiMView light-sheet microscopy recordings of fruit fly, mouse and zebrafish embryonic development (data sets 1–8), confocal microscopy data of a zebrafish embryo (data set 9) and SiMView functional image data of brain activity in a larval zebrafish (data set 10). Developmental data sets (data sets 1–8) were analyzed as raw and masked versions in order to illustrate the importance of background masking for maximizing data storage and to access efficiency. Please see steps I–III in [Figure 2](https://www.nature.com/articles/nprot.2015.111#Fig2) for a description of the concepts underlying background masking. Note that read speeds for uncompressed TIFF files are particularly low, as a large fraction of time is spent on accessing the large files. If image data sets are small enough for a local storage solution—i.e., when using the same computer for long-term data storage and image processing—the data access time overhead encountered for uncompressed image data can be slightly reduced, e.g., through the use of a high-performance RAID array. For benchmarks performed with image data sets stored locally on a high-performance RAID array built from solid-state drives (SSDs), please see [Supplementary Figure 1](https://www.nature.com/articles/nprot.2015.111#Fig8). For information about the block-size dependency of KLB performance, please see [Supplementary Figure 2](https://www.nature.com/articles/nprot.2015.111#Fig9).

[Full size image](https://www.nature.com/articles/nprot.2015.111/figures/3)

**Figure 4: Multiview image data compaction for light-sheet microscopy.**

[![figure 4](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_Fig4_HTML.jpg)](https://www.nature.com/articles/nprot.2015.111/figures/4)

Comparison of image file sizes obtained by taking advantage of our pipeline for image data compaction ([Fig. 2](https://www.nature.com/articles/nprot.2015.111#Fig2)) to varying degrees. Data set sizes are shown for raw, uncompressed image data sets (dark blue, step I III in [Fig. 2](https://www.nature.com/articles/nprot.2015.111#Fig2)), for KLB-compressed raw data sets (light blue), background-masked, KLB-compressed data sets (orange, steps I–III in [Fig. 2](https://www.nature.com/articles/nprot.2015.111#Fig2)) and for multiview fused, background-masked, KLB-compressed data sets (red, steps I–IV in [Fig. 2](https://www.nature.com/articles/nprot.2015.111#Fig2)). Even when recording only single views of a specimen, i.e., if multiview image fusion is not applicable, background masking and lossless KLB compression alone already lead to a substantial reduction in data size, without loss of information. The four types of image data sets included in this comparison represent single time points of time-lapse recordings of fruit fly, mouse and zebrafish embryos acquired with SiMView light-sheet microscopy. The factors shown above each set of bars indicate total data set size reduction from raw, uncompressed multiview data format to fused, background-masked, KLB-compressed data format. Note that data set sizes shown in this figure represent image size per time point and thus scale linearly to large-scale light-sheet microscopy time-lapse recordings comprising thousands of time points and tens of terabytes of image data.

[Full size image](https://www.nature.com/articles/nprot.2015.111/figures/4)

**Figure 5: Image compression performance using multicore CPUs.**

[![figure 5](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_Fig5_HTML.jpg)](https://www.nature.com/articles/nprot.2015.111/figures/5)

(**a**,**b**) Write (**a**) and read (**b**) speeds as a function of available CPU cores, for the uncompressed TIFF file format (dark blue), as well as lossless KLB (red), JPEG 2000 (orange) and LZW-TIFF (light blue) file formats. The benchmark was performed using data set 6 in [Figure 3](https://www.nature.com/articles/nprot.2015.111#Fig3). Note that uncompressed and LZW-compressed TIFF file formats do not benefit from multicore CPU architectures. JPEG 2000 can partially leverage the processing power of a small number of CPU cores (no performance increase observed beyond 4 CPU cores). In contrast, KLB performance scales almost linearly with the number of CPU cores, even when using multicore processing architectures with as many as 16 CPU cores. The JPEG 2000 benchmark uses the multithreaded commercial library PICTools Medical SDK (Accusoft). LZW-TIFF and uncompressed TIFF benchmarks use the 'imread' and 'imwrite' functions provided by the Image Processing Toolbox in MATLAB. Error bars represent s.d. for _n_ = 5 iterations of the benchmark. For information about the block-size dependency of KLB performance, please see [Supplementary Figure 2](https://www.nature.com/articles/nprot.2015.111#Fig9).

[Full size image](https://www.nature.com/articles/nprot.2015.111/figures/5)

By using a variety of fluorescence microscopy data sets, we compared KLB performance with that of other state-of-the-art compression formats ([Fig. 3](https://www.nature.com/articles/nprot.2015.111#Fig3) and [Supplementary Figs. 1](https://www.nature.com/articles/nprot.2015.111#Fig8),[2](https://www.nature.com/articles/nprot.2015.111#Fig9),[3](https://www.nature.com/articles/nprot.2015.111#Fig10)), including one of the most efficient multithreaded implementations of JPEG 2000 (PICTools Medical SDK, Accusoft). When KLB is used for locally stored image data ([Supplementary Fig. 1](https://www.nature.com/articles/nprot.2015.111#Fig8)), it provides superior compression ratios (3% and 70% better than JPEG 2000 or LZW-compressed TIFF, respectively) and read/write speeds (3.2-fold and 4.5-fold faster than JPEG 2000 or LZW-compressed TIFF, respectively, using 16-CPU cores). When KLB is used for network-attached image data (the typical setting for large-scale image data sets, [Fig. 3](https://www.nature.com/articles/nprot.2015.111#Fig3)), improvements in speed are even higher (3.3-fold and 7.5-fold faster than JPEG 2000 or LZW-compressed TIFF, respectively, using 16-CPU cores). Compared with uncompressed TIFF format, KLB provides markedly improved read/write speeds (3.1-fold and 16.5-fold faster locally or over the network, respectively), which is a direct result of the rapid data compaction in KLB and the reduced transfer times for compressed image data. Thus, KLB outperforms state-of-the-art file formats with respect to both compression ratio and speed by taking full advantage of modern multicore CPUs, and it offers lossless data compaction of large-scale image data sets with minimal access latency.

#### Multiview image fusion.

An efficient cross-platform multiview image fusion method using embedded fluorescent beads surrounding the sample has been incorporated in Fiji as part of the 'Multiview Reconstruction' plug-ins<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 41" title="Preibisch, S., Saalfeld, S., Schindelin, J. &amp; Tomancak, P. Software for bead-based registration of selective plane illumination microscopy data. Nat. Methods 7, 418–419 (2010)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR41" id="ref-link-section-d543302138e799">41</a></sup>. This bead-based method allows registration of any number of views distributed in an arbitrary geometry, without prior information about the relative location of each view. As a generalization of its initial design for bead-based registration, the method has more recently been extended to support image data containing other types of blob-like features (such as fluorescent cell nuclei) that can be reliably detected with a Difference of Gaussians filter.

In contrast, the multiview fusion module provided by ourprocessing pipeline ([Supplementary Software 3](https://www.nature.com/articles/nprot.2015.111#MOESM271)) is complementary in several ways. Our module does not require and rely on specific features to facilitate registration, but rather it uses all image information present in the sample itself, irrespective of the type of fluorescent label used in the experiment. Fast content-based registration is achieved by introducing the assumption of a multiview imaging assay with up to four orthogonal views (using up to two opposing light sheets and two opposing cameras); i.e., our method is not capable of registering arbitrary views. This latter constraint represents the main limitation of our method. However, as a direct result of this design principle, our method does not require the presence of fluorescent blob-like structures in the sample to facilitate accurate registration and image fusion. This approach thus offers the following three advantages: (i) our method is applicable to large specimens and high-magnification imaging experiments, for which the field of view does not cover space outside the volume of the biological specimen itself (and hence lacks space for beads); (ii) our method provides flexibility for biological sample preparation, as it does not require the sample to be embedded in an agarose gel or a similar matrix suitable for anchoring beads; and (iii) our method can partially compensate for the effect of light refraction along the light path through the sample, as our alignment is based on image information inside the sample. Our method is furthermore designed for high-throughput image processing ([Tables 1](https://www.nature.com/articles/nprot.2015.111#Tab1) and [2](https://www.nature.com/articles/nprot.2015.111#Tab2)), and it offers real-time capability for large-scale light-sheet microscopy data sets: by using a single computer workstation, our registration and fusion pipeline generally processes image data at a rate faster than the data acquisition rate of the light-sheet microscope<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e815">39</a></sup> ([Table 1](https://www.nature.com/articles/nprot.2015.111#Tab1)).

**Table 1 Computation time requirements of image processing pipeline.**

[Full size table](https://www.nature.com/articles/nprot.2015.111/tables/1)

**Table 2 Memory requirements of image processing pipeline.**

[Full size table](https://www.nature.com/articles/nprot.2015.111/tables/2)

#### Image segmentation and cell tracking.

There are several freely available computational methods for nuclei segmentation and cell tracking. These methods were specifically developed for cell-lineage reconstructions using time-lapse light microscopy images of fluorescently labeled nuclei. However, most of these approaches have been developed for relatively small model organisms, such as _Caenorhabditis elegans_ embryos<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 42" title="Bao, Z. et al. Automated cell lineage tracing in Caenorhabditis elegans. Proc. Natl. Acad. Sci. USA 103, 2707–2712 (2006)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR42" id="ref-link-section-d543302138e1454">42</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 43" title="Murray, J.I., Bao, Z., Boyle, T.J. &amp; Waterston, R.H. The lineaging of fluorescently-labeled Caenorhabditis elegans embryos with StarryNite and AceTree. Nat. Protoc. 1, 1468–1476 (2006)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR43" id="ref-link-section-d543302138e1457">43</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 44" title="Giurumescu, C.A. et al. Quantitative semi-automated analysis of morphogenesis with single-cell resolution in complex embryos. Development 139, 4271–4279 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR44" id="ref-link-section-d543302138e1460">44</a></sup>, which undergo stereotyped development and comprise several hundred cells by the end of embryonic development, or for very early developmental stages of more complex multicellular organisms, such as the early zebrafish blastula<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 45" title="Olivier, N. et al. Cell lineage reconstruction of early zebrafish embryos using label-free nonlinear microscopy. Science 329, 967–971 (2010)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR45" id="ref-link-section-d543302138e1464">45</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 46" title="Kausler, B.X. et al. A discrete chain graph model for 3D+t cell tracking with high misdetection robustness. ECCV 7574, 144–157 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR46" id="ref-link-section-d543302138e1467">46</a></sup> and the _Drosophila_ blastoderm<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 8" title="Tomer, R., Khairy, K., Amat, F. &amp; Keller, P.J. Quantitative high-speed imaging of entire developing embryos with simultaneous multiview light-sheet microscopy. Nat. Methods 9, 755–763 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR8" id="ref-link-section-d543302138e1474">8</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 46" title="Kausler, B.X. et al. A discrete chain graph model for 3D+t cell tracking with high misdetection robustness. ECCV 7574, 144–157 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR46" id="ref-link-section-d543302138e1477">46</a></sup>. These methods do not aim to facilitate automated cell lineaging in later stages of development, and their underlying design principles either produce high error rates in such data sets or do not scale to the tens of thousands of cells encountered during advanced embryogenesis of vertebrates and higher invertebrates<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e1482">39</a></sup>. An accurate method that scales to large data sets is available for cell nuclei segmentation<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 47" title="Stegmaier, J. et al. Fast segmentation of stained nuclei in terabyte-scale, time resolved 3D microscopy image stacks. PLoS ONE 9, e90036 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR47" id="ref-link-section-d543302138e1486">47</a></sup>, although this method does not perform cell tracking. Only very recently have existing methods<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 48" title="Schiegg, M. et al. Graphical model for joint segmentation and tracking of multiple dividing cells. Bioinformatics 31, 948–956 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR48" id="ref-link-section-d543302138e1490">48</a></sup> for joint segmentation and tracking been successfully extended to handle data recorded in later developmental stages, although scalability with increasing cell counts is still an issue. In contrast, computation time of the TGMM software included in our framework ([Supplementary Software 4](https://www.nature.com/articles/nprot.2015.111#MOESM272)) scales linearly with the number of segmented and tracked objects while maintaining state-of-the-art accuracy even in late developmental stages: on a single computer workstation equipped with a Tesla K20 graphics processing unit (GPU), processing speed is on average 26,000 cells per min, which enables real-time performance in all tested scenarios<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e1497">39</a></sup>. The software is designed for easy use without prior domain knowledge, and it requires adjustment of only two framework parameters when applied across multiple model systems and imaging modalities. We note that the most important factor that influences tracking accuracy is the temporal sampling of cell movements in the time-lapse data, although image quality and cell density can affect results as well<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e1501">39</a></sup>.

#### Data visualization and editing of cell-lineage annotations.

OMERO<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 49" title="Allan, C. et al. OMERO: flexible, model-driven data management for experimental biology. Nat. Methods 9, 245–253 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR49" id="ref-link-section-d543302138e1514">49</a></sup> is a software solution that is exceptional in its data organization features. OMERO facilitates organizing, remote browsing and analysis of multidimensional microscopy data. It excels at providing unified access to images and metadata from multiple sources and a plethora of file formats in a multiuser environment. As such, it supports specialized applications that are beyond its own scope. Newer versions of OMERO store data in their original files; this strategy is guaranteed to be lossless, but it is reliant on third-party choices of data file layout and compression algorithms, which are crucial parameters when balancing storage efficiency and interactive visualization.

Multiple software options provide the ability to concurrently visualize image data and edit cell-lineage reconstructions. goFigure2 is an open-source cross-platform software<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 50" title="Megason, S.G. In toto imaging of embryogenesis with confocal time-lapse microscopy. Methods Mol. Biol. 546, 317–332 (2009)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR50" id="ref-link-section-d543302138e1521">50</a></sup> specifically designed for this task. Similarly to CATMAID, it uses a database to store all segmentation and tracking information, which allows it to efficiently handle millions of data points and to import results into other modules for downstream analysis. goFigure2 uses the VTK library<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 51" title="Schroeder, W., Martin, K. &amp; Lorensen, B. The Visualization Toolkit: An Object-Oriented Approach to 3D Graphics. 4th edn. (Kitware, 2006)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR51" id="ref-link-section-d543302138e1525">51</a></sup> for visualization and 3D rendering, which provides more visualization options than CATMAID. However, as images are not partitioned in small chunks of data (tiles) ahead of time, navigating the data along the time axis of a time-lapse imaging experiment requires constantly loading image stacks from disk. This requirement precludes real-time interaction with large image data sets. Imaris (Bitplane) is a commercial scientific software for data visualization, segmentation and analysis of 3D and 4D microscopy data sets, and it includes a module for cell tracking. Like goFigure2, Imaris offers 3D rendering options for advanced data visualization and, if a sufficient amount of GPU memory is available, consecutive time points are cached for smooth transition between time points in a short temporal window. However, all data (images, segmentation and tracking annotations) associated with a given project are stored in a single HDF5-like file, which appears to substantially slow performance when using multiterabyte image data sets and millions of tracked data points. Moreover, neither goFigure2 nor Imaris allows concurrent remote data access by multiple users; this capability is particularly valuable for large-scale collaborative projects that involve multiple entities around the globe.

These limitations are addressed in CATMAID<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 37" title="Saalfeld, S., Cardona, A., Hartenstein, V. &amp; Tomancˇák, P CATMAID: collaborative annotation toolkit for massive amounts of image data. Bioinformatics 25, 1984–1986 (2009)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR37" id="ref-link-section-d543302138e1532">37</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 38" title="Cardona, A. Collaborative annotation toolkit for massive amounts of image data (CATMAID) GitHub repository 
                  https://github.com/acardona/CATMAID
                  
                 (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR38" id="ref-link-section-d543302138e1535">38</a></sup>, which allows rapid, uninterrupted browsing of multiterabyte data sets and concurrent large-scale data annotation involving tens of millions of data points, even when accessing the data remotely through the internet ([Fig. 6](https://www.nature.com/articles/nprot.2015.111#Fig6)). Our branch of the CATMAID framework ([Supplementary Software 5](https://www.nature.com/articles/nprot.2015.111#MOESM273)) currently supports light microscopy image data sets with up to five dimensions (three spatial dimensions, time and color).

**Figure 6: Image annotation and editing of cell-lineage data using CATMAID.**

[![figure 6](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_Fig6_HTML.jpg)](https://www.nature.com/articles/nprot.2015.111/figures/6)

(**a**) Screenshot of internet browser showing CATMAID GUI during the manual curation of TGMM cell-lineage data in a fruit fly embryo. Image data are displayed superimposed with cell-lineage data points in a tri-view arrangement (_XY_, _YZ_ and _X_Z slices of the specimen). Both image data and cell-lineage annotations are stored remotely on a server to avoid data duplication; that is, the same image data set can be used for multiple cell lineaging projects. The annotation database containing the full cell-lineage reconstruction is shown in the bottom right corner. (**b**) Enlarged view of a part of the CATMAID toolbar, which provides utilities for browsing the image data, as well as accessing and editing data annotations.

[Full size image](https://www.nature.com/articles/nprot.2015.111/figures/6)

Alternative software solutions for visualizing large-scale (i.e., larger than locally available memory) 5D data sets on single computer workstations are increasingly becoming available, and they include both commercial and open-source software, such as Arivis Vision 4D, Amira, Vaa3D (refs. [52](https://www.nature.com/articles/nprot.2015.111#ref-CR52 "Peng, H., Ruan, Z., Long, F., Simpson, J.H. & Myers, E.W. V3D enables real-time 3D visualization and quantitative analysis of large-scale biological image data sets. Nat. Biotechnol. 28, 348–353 (2010)."),[53](https://www.nature.com/articles/nprot.2015.111#ref-CR53 "Bria, A., Iannello, G. & Peng, H. An open-source VAA3D plugin for real-time 3D visualization of terabyte-sized volumetric images. ISBI, 520–523 (2015).")) and BigDataViewer<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 54" title="Pietzsch, T., Saalfeld, S., Preibisch, S. &amp; Tomancak, P. BigDataViewer: visualization and processing for large image data sets. Nat. Methods 12, 481–483 (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR54" id="ref-link-section-d543302138e1589">54</a></sup>. Each of these software packages includes different visualization tools, although most of them follow similar principles, such as the use of multiscale block-based file formats for efficient data access in regions of interest at the appropriate level of resolution. Some of these software solutions furthermore already include or are starting to incorporate editing and annotation tools on top of their visualization engines.

### Experimental design

All software modules are available from [http://www.janelia.org/lab/keller-lab](http://www.janelia.org/lab/keller-lab) and as [Supplementary Software 1](https://www.nature.com/articles/nprot.2015.111#MOESM269),[2](https://www.nature.com/articles/nprot.2015.111#MOESM270),[3](https://www.nature.com/articles/nprot.2015.111#MOESM271),[4](https://www.nature.com/articles/nprot.2015.111#MOESM272),[5](https://www.nature.com/articles/nprot.2015.111#MOESM273),[6](https://www.nature.com/articles/nprot.2015.111#MOESM274), and they have been tested on multiple operating systems (including Windows, Linux and Mac OS), except for the backend required by the web application CATMAID, which has only been tested on a Linux platform. However, CATMAID can, in principle, also be set up on other operating systems. We provide source code and documentation for all modules to enable their adaption to specific needs and various types of imaging experiments. Although all five modules can be used independently, they are also capable of communicating results to each other and form an integrated processing pipeline. It is furthermore possible to integrate the respective functionality of each module in other software packages (for example, we offer full ImageJ/Fiji support for our block-based image file format). Finally, all modules can be run efficiently on a single computer workstation equipped with MATLAB (MathWorks) and a CUDA-enabled graphics card, and most of our modules are capable of taking full advantage of modern multicore CPUs and GPUs, as well as cluster environments.

### Applications of the protocol

The methods described here can be applied to image data from a variety of imaging techniques<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e1636">39</a></sup>, including custom-built light-sheet microscopes, commercial light-sheet microscopes and confocal fluorescence microscopes. In our laboratory, we are routinely using this set of computational tools for image data management and processing of SiMView<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 5" title="Ahrens, M.B., Orger, M.B., Robson, D.N., Li, J.M. &amp; Keller, P.J. Whole-brain functional imaging at cellular resolution using light-sheet microscopy. Nat. Methods 10, 413–420 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR5" id="ref-link-section-d543302138e1640">5</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 8" title="Tomer, R., Khairy, K., Amat, F. &amp; Keller, P.J. Quantitative high-speed imaging of entire developing embryos with simultaneous multiview light-sheet microscopy. Nat. Methods 9, 755–763 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR8" id="ref-link-section-d543302138e1643">8</a></sup> and hs-SiMView<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 35" title="Lemon, W. et al. Whole central nervous system functional imaging in larval Drosophila. Nat. Commun. 6, 7924 (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR35" id="ref-link-section-d543302138e1647">35</a></sup> light-sheet microscopy image data sets spanning a range of biological model systems, including zebrafish embryos and larvae, _Drosophila_ embryos, larvae, pupae and adults, mouse embryos, _Platynereis_ embryos and _Parhyale_ embryos. This list can, in principle, be extended to any biological specimen suitable for imaging with optical sectioning fluorescence microscopy in general and light-sheet microscopy in particular. Specific examples of previous use cases in systems neuroscience include data management of large-scale functional imaging data of the zebrafish larval brain<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 5" title="Ahrens, M.B., Orger, M.B., Robson, D.N., Li, J.M. &amp; Keller, P.J. Whole-brain functional imaging at cellular resolution using light-sheet microscopy. Nat. Methods 10, 413–420 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR5" id="ref-link-section-d543302138e1661">5</a></sup> and the CNS of larval _Drosophila_<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 35" title="Lemon, W. et al. Whole central nervous system functional imaging in larval Drosophila. Nat. Commun. 6, 7924 (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR35" id="ref-link-section-d543302138e1667">35</a></sup>, which were acquired using state-of-the-art calcium indicators GCaMP5G (ref. [55](https://www.nature.com/articles/nprot.2015.111#ref-CR55 "Akerboom, J. et al. Optimization of a GCaMP calcium indicator for neural activity imaging. J. Neurosci. 32, 13819–13840 (2012).")) and GCaMP6s (ref. [56](https://www.nature.com/articles/nprot.2015.111#ref-CR56 "Chen, T.W. et al. Ultrasensitive fluorescent proteins for imaging neuronal activity. Nature 499, 295–300 (2013).")), respectively. In the field of developmental biology, the methods presented here have previously been used for data management, multiview fusion, whole-embryo long-term cell tracking, as well as data curation and visualization in zebrafish, _Drosophila_, mouse and _Platynereis_ embryos<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 8" title="Tomer, R., Khairy, K., Amat, F. &amp; Keller, P.J. Quantitative high-speed imaging of entire developing embryos with simultaneous multiview light-sheet microscopy. Nat. Methods 9, 755–763 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR8" id="ref-link-section-d543302138e1684">8</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e1687">39</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 40" title="Lauri, A. et al. Development of the annelid axochord: insights into notochord evolution. Science 345, 1365–1368 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR40" id="ref-link-section-d543302138e1690">40</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 57" title="Kanodia, J.S. et al. A computational statistics approach for estimating the spatial range of morphogen gradients. Development 138, 4867–4874 (2011)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR57" id="ref-link-section-d543302138e1693">57</a></sup>. For cell tracking and cell lineaging applications, such as our cell-lineage reconstruction of the early _Drosophila_ nervous system, our tools are typically most effective for image data of organisms ubiquitously expressing nuclei-localized fluorescent markers. In the following paragraphs, we provide information about application details specific to individual modules of the processing pipeline.

We note that, although our content-based multiview fusion module does not support arbitrary optical geometries, it is compatible with some of the most commonly encountered light-sheet microscope configurations. Aside from the SiMView four-view geometry (providing up to four camera/light-sheet view combinations through the use of two detection arms and two light sheets whose optical axes are arranged as a cross), it is also possible to process data from multiview setups that rely on mechanical rotation by 180° to acquire complementary views of the specimen, as well as from bidirectional illumination setups that use two light sheets along the same illumination axis. Such configurations include OpenSPIM setups<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 58" title="Pitrone, P.G. et al. OpenSPIM: an open-access light-sheet microscopy platform. Nat. Methods 10, 598–599 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR58" id="ref-link-section-d543302138e1703">58</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 59" title="Gualda, E.J. et al. OpenSpinMicroscopy: an open-source integrated microscopy platform. Nat. Methods 10, 599–600 (2013)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR59" id="ref-link-section-d543302138e1706">59</a></sup>, as well as commercial light-sheet microscopes—e.g., the Lightsheet Z.1 by Carl Zeiss.

Our TGMM software can generally be used to track blob-like structures in various types of 2D or 3D time-lapse images, as long as object movements between consecutive time points do not exceed object size. CATMAID is capable of visualizing arbitrary 5D image data, and it allows generating and editing object annotations that can be naturally organized in tree-like structures, thus encompassing essentially any type of segmentation and tracking task. CATMAID was initially developed for visualizing and annotating large electron microscopy data sets generated in the field of connectomics for reconstructing the wiring diagram of the brain at nanometer resolution<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 60" title="Bock, D.D. et al. Network anatomy and in vivo physiology of visual cortical neurons. Nature 471, 177–182 (2011)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR60" id="ref-link-section-d543302138e1713">60</a></sup>. This software is thus also well suited to microscopy data of neural tissues from light-based imaging modalities<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 61" title="Tomer, R., Ye, L., Hsueh, B. &amp; Deisseroth, K. Advanced CLARITY for rapid and high-resolution imaging of intact tissues. Nat. Protoc. 9, 1682–1697 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR61" id="ref-link-section-d543302138e1717">61</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 62" title="Susaki, E.A. et al. Whole-brain imaging with single-cell resolution using chemical cocktails and computational analysis. Cell 157, 726–739 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR62" id="ref-link-section-d543302138e1720">62</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 63" title="Dodt, H.U. et al. Ultramicroscopy: three-dimensional visualization of neuronal networks in the whole mouse brain. Nat. Methods 4, 331–336 (2007)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR63" id="ref-link-section-d543302138e1723">63</a></sup>.

Finally, our KLB compression algorithm can be applied to any type of image data (consisting of signed or unsigned integers with a depth of 8, 16, 32 or 64 bits, as well as 32-bit or 64-bit floating point data with up to five dimensions), irrespective of its source. In principle, any type of microscopy data benefit from the file size reduction and high read and write speeds achieved by KLB. The block-based design of KLB is furthermore particularly helpful when working with large image volumes, such as image data of entire developing embryos<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e1730">39</a></sup>, as well as large neural tissues or entire brains treated with chemical clearing methods<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 61" title="Tomer, R., Ye, L., Hsueh, B. &amp; Deisseroth, K. Advanced CLARITY for rapid and high-resolution imaging of intact tissues. Nat. Protoc. 9, 1682–1697 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR61" id="ref-link-section-d543302138e1734">61</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 62" title="Susaki, E.A. et al. Whole-brain imaging with single-cell resolution using chemical cocktails and computational analysis. Cell 157, 726–739 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR62" id="ref-link-section-d543302138e1737">62</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 63" title="Dodt, H.U. et al. Ultramicroscopy: three-dimensional visualization of neuronal networks in the whole mouse brain. Nat. Methods 4, 331–336 (2007)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR63" id="ref-link-section-d543302138e1740">63</a></sup>, as the KLB format provides rapid access to local image regions with minimal overhead.

### Level of expertise needed to implement the protocol

Until recently, access to light-sheet microscopes was largely restricted to research laboratories with the expertise required for building custom microscopes. However, with the market launch of various commercial light-sheet microscopes, such as the Carl Zeiss Lightsheet Z.1, this imaging technique is now available to essentially all researchers. As discussed above, our software modules can be applied to data sets produced with both custom and commercial microscopes.

As our laboratory consists of researchers with very diverse backgrounds, from mathematics and optical physics to biology, we took care to build our computational tools such that they can be used effectively without the need for a strong computational background. For example, image data in our KLB compression file format can be written and read through Fiji or MATLAB interfaces in exactly the same way that a TIFF file would be written or read. Our content-based MATLAB scripts for multiview image fusion are designed such that all configuration parameters are located in a simple MATLAB script that launches and manages each processing job automatically. Thus, the user essentially just needs to be familiar with the MATLAB interface itself and some basic commands for editing end running MATLAB scripts. When using computer clusters, a higher level of expertise is required in order to modify the respective support infrastructure provided by our software for submitting jobs in a given cluster environment.

Our segmentation and tracking software TGMM follows a similar design: the executable reads a configuration file that contains the parameters set by the user. Moreover, we provide executables that allow running our software out-of-the-box on Windows operating systems. Linux and Mac OS X users need to compile the code once to generate binaries, and thus some familiarity with CMake and C++ compilers is required for initial installation. All of these steps are documented in detail in our protocol and in the manuals included in our software packages.

The step that requires the most computational expertise is the setup of the CATMAID software: in addition to the installation of the application itself, the use of CATMAID requires setting up an HTTP server and a PostgreSQL database. We provide detailed documentation of these steps, but we also note that they are usually carried out by IT personnel or the system administrator of the academic institution. Once this initial setup is complete, users can simply interact with the program through a web browser, which does not require any particular expertise.

### Limitations

The segmentation and tracking modules of our processing pipeline were designed for cell tracking in images of nuclei-localized fluorescent markers. Shapes of cell nuclei in such images can typically be well approximated as ellipsoid-like geometries<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e1765">39</a></sup>, and this assumption is reflected in the TGMM software by modeling the intensity profile of each nucleus as a 3D Gaussian. Thus, the TGMM software will typically not perform as well in images of objects with relatively irregular shapes, such as images of membrane markers. The other main requirement of the cell tracking protocol is that input image data should be well sampled along the time axis. As a rule of thumb, if an object moves between two consecutive time points by a distance larger than its diameter, the propagation of the associated 3D Gaussian shape parameters will probably not be successful. Finally, with regard to hardware limitations, execution of the TGMM framework requires a computer equipped with a CUDA-enabled nVidia graphics card.

As mentioned in earlier sections, there are a few additional limitations with respect to the other parts of our computational pipeline. First, our content-based multiview image fusion module does not support arbitrary optical geometries (please see 'Applications of the protocol' for details). Second, although the KLB lossless compression file format accepts a range of numerical data types (unsigned/signed integers, as well as floating point), best compression rates are typically obtained only for integer data types. With regard to hardware limitations, a computer with multicore CPU is required to take full advantage of the read and write speed improvements enabled by the block-based design of our file format. Finally, data visualization in CATMAID is limited to orthogonal cuts along the three axes of the underlying Cartesian coordinate system; i.e., the GUI does not render oblique slices of the image data.

Materials
---------

### EQUIPMENT

### Data files

-   Data set 1, comprising example data for image masking and KLB image compression. This archive is available for download from our laboratory website ([https://www.janelia.org/lab/keller-lab/software](https://www.janelia.org/lab/keller-lab/software)), and it contains a preconfigured version of the first module (clusterPT.m) of our MATLAB-based image processing pipeline for light-sheet microscopy data sets, all related auxiliary functions, a README file with software documentation and the folder Image\_Data with example data. The example data consist of a SiMView four-view recording (four image stacks with 125 images each) of a _Drosophila_ embryo at an early developmental time point. The data set serve the purpose of illustrating image background masking and KLB lossless image compression with the MATLAB script clusterPT.m and follow the naming convention outlined in the README file. Note that clusterPT.m functionality also includes a dead pixel detector for removing respective image artifacts in scientific-grade complementary metal-oxide semiconductor (sCMOS) camera image data; however, dead pixels have already been corrected in this example data set.
    
-   Data set 2, comprising example data for multiview image registration and fusion. This archive is available for download from our laboratory website ([https://www.janelia.org/lab/keller-lab/software](https://www.janelia.org/lab/keller-lab/software)), and it contains preconfigured versions of the multiview image registration and fusion modules (clusterMF.m, localAP.m, clusterTF.m) of our MATLAB-based image processing pipeline for light-sheet microscopy data sets, all related auxiliary functions, a README file with software documentation and the folder Image\_Data with example data. The KLB-compressed example data consist of 11 time points of a SiMView four-view recording of an early _Drosophila_ embryo processed with clusterPT.m. The data set serves the purpose of illustrating multiview image fusion of time-lapse light-sheet microscopy data with the MATLAB scripts clusterMF.m, localAP.m and clusterTF.m.
    

### Computer equipment

-   Hardware requirements. For most benchmarks, the computational pipeline was deployed on a computer workstation equipped with two Intel Xeon E5-2687W CPUs, 192 GB DDR3 memory, an nVidia Tesla Kepler K20 GPU, six Seagate Savvio 10K.5 ST9900805SS hard disks combined in a RAID-6 data array, an Intel RMS25CB080 RAID module, an Intel X520-SR1 10Gb fiber network adapter and Windows 7 Professional 64 bit. For optimal processing speed, a good GPU and sufficient memory are of primary importance. The Tesla graphics card can be replaced with a lower-cost GeForce GTX Titan graphics card with little performance impact. Minimum requirements are an nVidia GPU with CUDA compute capability of 2.0 or higher. Information on CUDA compute capabilities of various GPUs is available at [https://developer.nvidia.com/cuda-gpus](https://developer.nvidia.com/cuda-gpus). For a particularly cost-efficient build, slower CPUs and hard disks will generally suffice, as these components will only have a minor impact on processing speed.
    
-   The performance benchmarks of the data compaction and multiview image fusion modules shown in [Table 1](https://www.nature.com/articles/nprot.2015.111#Tab1) were performed on a computer workstation equipped with two Intel Xeon E5-2667V2 CPUs, 256 GB DDR3 memory, an nVidia Quadro K2000D GPU, six Samsung 840 EVO 1 TB solid-state drives (SSDs) combined in a RAID-6 data array, an LSI 2208 RAID module, an Intel X520-SR1 10Gb fiber network adapter and Windows 8 Professional 64 bit.
    
-   For data visualization, editing and annotation using CATMAID, a server with the following hardware components was used: two Intel Xeon E5-2690 CPUs, 128 GB of DDR3 memory, six Intel 520 Series 480 GB SSDs combined in a RAID-6 data array, an Intel RMS25CB080 RAID module, an Intel X520-SR1 10Gb fiber network adapter and the Linux distribution Ubuntu 12.04 LTS. Also in this case, slower CPUs and storage hardware will generally only have a minor performance impact. The SSDs constitute the most important hardware components as they ensure fast tile retrieval. We note that the same workstation can be used for CATMAID and for the rest of the computational pipeline
    
-   Software requirements. For several parts of our computational framework, a MATLAB installation (R2013b or later; MathWorks) is required, including the following toolboxes: Curve Fitting, Image Processing, Statistics, Optimization, Signal Processing and Parallel Computing. We verified compatibility specifically for MATLAB version R2013b, but our code should, in principle, be compatible with any version above R2011a, without a need for code modifications. We also note that the list of MATLAB toolbox requirements is based on the full functionality provided by our processing pipeline. Only a subset of these toolboxes is required to run the pipeline using typical parameter settings. A detailed overview of software and hardware requirements for all software packages is provided in [Supplementary Table 1](https://www.nature.com/articles/nprot.2015.111#MOESM268). Custom software packages are provided as [Supplementary Software 1](https://www.nature.com/articles/nprot.2015.111#MOESM269),[2](https://www.nature.com/articles/nprot.2015.111#MOESM270),[3](https://www.nature.com/articles/nprot.2015.111#MOESM271),[4](https://www.nature.com/articles/nprot.2015.111#MOESM272),[5](https://www.nature.com/articles/nprot.2015.111#MOESM273),[6](https://www.nature.com/articles/nprot.2015.111#MOESM274), and they can also be downloaded at [http://www.janelia.org/lab/keller-lab](http://www.janelia.org/lab/keller-lab)
    

### EQUIPMENT SETUP

### Installation of TGMM software

-   Install the nVidia CUDA drivers included in the nVidia CUDA Toolkit available from [https://developer.nvidia.com/cuda-toolkit-archive](https://developer.nvidia.com/cuda-toolkit-archive). If you are using a Linux Ubuntu distribution, simply execute the following terminal command:sudo apt-get install nvidia-cuda-toolkit
    
-   To run the TGMM software ([Supplementary Software 4](https://www.nature.com/articles/nprot.2015.111#MOESM272)), an nVidia graphics card with CUDA compute capability of 2.0 or higher is needed. Information about CUDA compute capability of all nVidia graphics cards is available at [https://developer.nvidia.com/cuda-gpus](https://developer.nvidia.com/cuda-gpus).
    

### Installing CATMAID for data visualization and cell-lineage editing

-   Download the latest version of the CATMAID branch for cell lineaging at [https://github.com/catmaid/CATMAID/tree/5d\_cell\_tracking](https://github.com/catmaid/CATMAID/tree/5d_cell_tracking) or clone it with the following Git command:git clone -b 5Dvisualization --single-branch https://fernandoamat@bitbucket.org/fernandoamat/catmaid\_5d\_visualization\_annotation.git
    
-   All installation details for Linux can be found in the user guide included in [Supplementary Software 5](https://www.nature.com/articles/nprot.2015.111#MOESM273), but we note that other operating systems can be used as well. Four main modules need to be set up: Django backend for running the web application CATMAID; HTTP server for web browsers for interacting with the backend; PostgreSQL database for storing all tracking information (but not for image data); and Image storage server for storing all image tiles.
    
-   It is possible to use a separate computer for storing image data and the database containing tracking information, as long as CATMAID has access to these data. CATMAID only needs to be installed once, and it can subsequently be used through a web browser at any time from any location in the world with Internet access<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 37" title="Saalfeld, S., Cardona, A., Hartenstein, V. &amp; Tomancˇák, P CATMAID: collaborative annotation toolkit for massive amounts of image data. Bioinformatics 25, 1984–1986 (2009)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR37" id="ref-link-section-d543302138e1961">37</a></sup>. This step of the installation protocol requires the highest computational proficiency, and it is usually carried out by a system administrator or other IT personnel. In total, it should take ∼1–3 h to configure all required software components.
    

### Optimizing HTTP server and PostgreSQL database configuration for optimal performance of the CATMAID web application

-   It is important to optimize the performance of the server in order to ensure the fastest possible interaction with CATMAID when visualizing image data and editing cell lineages through the web browser. Although there are many possible ways to optimize the system, we recommend in particular the following strategies that helped increase the performance of our system significantly:
    
-   We recommend using SSDs to store the image tiles. These drives should be mounted with the options 'noatime' and 'nodiratime' to avoid unnecessary read/write operations while serving image tiles to the web browser. Recommendations for further optimization can be found at [https://wiki.debian.org/SSDOptimization](https://wiki.debian.org/SSDOptimization).
    
-   If you are using the Linux partition format Ext2/Ext3, the i-node index descriptor is the main data structure describing files. Each node is associated with one file and the block of addresses reserved for a file are stored in its index descriptor. However, the maximum number of i-nodes is set at the time of disk formatting and cannot be changed thereafter. Thus, if there are many small files, one can run out of i-nodes without running out of disk space. This scenario is possible for the image server because of the large number of tiles needed to partition large-scale data sets. Thus, we recommend accounting for an average file size of 4–8 kB when formatting the data partition of the image server. For example, in our system, the data array with a capacity of 1.7 TB was formatted using 268,435,456 i-nodes.
    
-   If the server has a large amount of RAM, the extent of data caching by the database and the operating system can be increased. Thereby, when users request the same image tiles multiple times, the server can retrieve them from memory instead of having to access the disk. To enhance caching, the following parameters need to be modified: 'kernel.shmmax' and 'kernel.shmall' in the file '/etc/sysctl.conf' and 'effective\_cache\_size' and 'shared\_buffers' in the file '/etc/postgresql/X.X/main/postgresql.conf'. Recommendations for further optimization can be found at [http://wiki.postgresql.org/wiki/Tuning\_Your\_PostgreSQL\_Server](http://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server).
    

Procedure
---------

### Independent pipeline modules

1.  1
    
    The options described here focus on five classes of computational modules. Each of these modules can be executed independently or as part of a larger pipeline ([Figs. 1](https://www.nature.com/articles/nprot.2015.111#Fig1) and [2](https://www.nature.com/articles/nprot.2015.111#Fig2)):
    
    1.  A
        
        **Lossless compression of light-sheet microscopy data and/or multiview image fusion**
        
        1.  i
            
            Extract the test data and MATLAB scripts provided in Data set 1 (see 'Data files' in the MATERIALS section) to create a preconfigured test environment for performing background masking and/or lossless image compression using the KLB image format. The test data set included in this archive is a four-view image data set of a _Drosophila_ embryo, which was recorded with a SiMView microscope.
            
        2.  ii
            
            Open a MATLAB terminal and go to the folder containing the MATLAB scripts.
            
        3.  iii
            
            Run the preconfigured MATLAB script clusterPT.m to verify proper software execution, and confirm that KLB output stacks are written to disk (output folder Image\_Data.corrected). Note that clusterPT.m can optionally also be configured to save output image data in an uncompressed TIFF file format (parameter 'outputType').
            
            #### Critical Step
            
            To run clusterPT.m on a new data set, use the code provided in [Supplementary Software 3](https://www.nature.com/articles/nprot.2015.111#MOESM271) (comprising the complete MATLAB processing pipeline) and consult the software documentation (README file included with pipeline; see also parameter explanations provided in source code) to configure clusterPT.m for your data set (See [Box 1](https://www.nature.com/articles/nprot.2015.111#Sec17) for more information).
            
            [Troubleshooting](https://www.nature.com/articles/nprot.2015.111#Sec20)
            
            #### Pause point
            
            At this point, the compressed image data can be manually inspected or imported into external software (proceed to Step 1A(iv)). If the data set is a multiview data set consisting of up to four views following the SiMView convention, image registration and fusion can now be performed by continuing with Step 1A(v). Spatial drift correction, intensity normalization or image filtering can be performed by continuing with Step 1B(i). If multiview image fusion, as well as drift correction, normalization and/or filtering, is required, please follow the instructions for multiview image fusion first.
            
        4.  iv
            
            Inspect the output image data generated by clusterPT.m. Once the images are stored in KLB format, they can be retrieved using the KLB C++ API provided in [Supplementary Software 1](https://www.nature.com/articles/nprot.2015.111#MOESM269). We also provide wrappers for MATLAB and Java, integration with Fiji<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 64" title="Schindelin, J. et al. Fiji: an open-source platform for biological-image analysis. Nat. Methods 9, 676–682 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR64" id="ref-link-section-d543302138e2125">64</a></sup> and an interface file for SWIG to autogenerate bindings for other languages ([Supplementary Software 1](https://www.nature.com/articles/nprot.2015.111#MOESM269) and [2](https://www.nature.com/articles/nprot.2015.111#MOESM270)). The KLB API provides efficient access to arbitrary regions of interest in the image volume by using block partitioning of the image data ([Supplementary Note](https://www.nature.com/articles/nprot.2015.111#MOESM268)).
            
        5.  v
            
            Extract the test data and MATLAB scripts provided in Data set 2 (see 'Data files' in the MATERIALS section) to create a preconfigured test environment for multiview image registration and fusion of SiMView-like image data sets with up to four views. The test data set included in this archive is a four-view image data set of a _Drosophila_ embryo that was processed with clusterPT.m and stored in the KLB format.
            
        6.  vi
            
            Execute the software modules for multiview image fusion. Multiview image registration and fusion consists of three steps (MATLAB scripts clusterMF.m, localAP.m and clusterTF.m) when processing time-lapse data sets. When processing individual image stacks rather than time-lapse data sets, only the first step (MATLAB script clusterMF.m) is required. In order to verify proper software execution and to get familiar with the full software functionality, run the preconfigured MATLAB scripts clusterMF.m, localAP.m and clusterTF.m included with the test data in sequential order. First, open a MATLAB terminal and go to the folder containing the scripts.
            
            #### Critical Step
            
            To run these MATLAB scripts on new data sets, certain parameters will need to be adjusted (See [Box 2](https://www.nature.com/articles/nprot.2015.111#Sec18) for more information).
            
        7.  vii
            
            Execute the first script, clusterMF.m. This script generates registered and fused image stacks, which are stored in the output folder 'Image\_Data.MultiFused'. The solution provided by clusterMF.m is not guaranteed to be smooth in time, as the data at each time point will be processed independently from the rest of the time-lapse data set.
            
        8.  viii
            
            Execute the second script, localAP.m, to evaluate the registration results generated by clusterMF.m. This script produces smooth, interpolated parameter sets defining multiview image registration and multichannel/camera intensity matching transformations for all time points.
            
        9.  ix
            
            Execute the third script, clusterTF.m. This script uses the information extracted by localAP.m and clusterMF.m in the previous two steps to perform temporally smooth multiview image fusion for the entire time-lapse data set.
            
            #### Critical Step
            
            In the example data set, clusterMF.m is executed for all data points of the time-lapse experiment for demonstration purposes. When processing a large-scale time-lapse data set consisting of hundreds to thousands of time points recorded at high temporal resolution, we recommend running clusterMF.m only for a subset of time points (under typical conditions every tenth time point is sufficient) to save computation time and disk space. This sparse sampling of the time lapse data set is usually sufficient, as localAP.m will subsequently analyze and interpolate the results for smooth fusion of the entire time-lapse data set via clusterTF.m. The only exceptions to this rule are data sets in which temporal sampling is coarse and specimen shape and/or position changes drastically from one time point to the next. In this latter scenario, execution of clusterMF.m for all time points may improve image quality. It is important to keep this division of labor in mind, as execution of clusterMF.m is considerably more time-consuming per time point than execution of clusterTF.m.
            
            [Troubleshooting](https://www.nature.com/articles/nprot.2015.111#Sec20)
            
            #### Pause point
            
            At this point, the fused image data can be manually inspected, used for data analysis or imported into external software. Spatial drift correction, intensity normalization or image filtering can be performed by continuing with Step 1B(i).
            
        
        Timing 5 min for setup, 0.5–12 h of unattended computer time (depending on data set size)
        
    2.  B
        
        **Spatial drift correction, intensity normalization and image filtering**
        
        1.  i
            
            Extract the code provided in [Supplementary Software 3](https://www.nature.com/articles/nprot.2015.111#MOESM271) (comprising the complete MATLAB processing pipeline) in order to start using the software modules for 3D spatial drift correction, intensity normalization throughout a time-lapse image data set and/or image filtering for adaptive local background correction. The output from Step 1A(ix) can be used in this section as an example. Proceed to Step 1B(ii) for drift correction and/or intensity normalization. Proceed to Step 1B(iv) for image filtering for adaptive local background correction.
            
        2.  ii
            
            Consult the software documentation (README file included with pipeline; see also parameter explanations provided in source code) to configure and run localEC.m. localEC.m is a data analysis script that preprocesses the time-lapse data set for subsequent 3D spatial drift correction and/or intensity normalization with clusterCS.m in Step 1B(iii). Verify that all formatting parameters are correctly defined. localEC.m provides the parameters 'intensityFlag' to enable/disable intensity normalization and 'correlationFlag' to enable/disable 3D drift correction.
            
        3.  iii
            
            Run clusterCS.m script. Once the corresponding intensity/drift information has been collected by localEC.m (previous step), compensatory image adjustments can subsequently be applied by clusterCS.m using the parameters 'correctDrift' to execute drift correction (using the parameter 'referenceTime' as a temporal anchor, that is, as the time point relative to which adjustments of data at all other time points are performed) and 'correctIntensity' to execute intensity normalization.
            
            #### Critical Step
            
            The scripts localEC.m and clusterCS.m use multiple complementary strategies to estimate short-term specimen fluctuations and long-term specimen drift, respectively. The former is computed via image correlation (which provides accurate frame-to-frame corrections but can introduce long-term drift), whereas the latter is estimated based on computation of the geometrical center of the specimen (which captures long-term drift but is too noisy for frame-to-frame corrections). The combination of both methods provides optimal short-term and long-term drift correction, and it is enabled by setting the parameter 'globalMode' to 1.
            
        4.  iv
            
            Consult the software documentation (README file included with pipeline; see also parameter explanations provided in source code) to configure and run clusterFR.m for your data set. clusterFR.m uses Gaussian filtering for adaptive local background subtraction and generates filtered image stacks and/or maximum-intensity projections of filtered image stacks. The radius used for anisotropic Gaussian filtering is defined in the parameter 'rangeArray'.
            
            #### Critical Step
            
            Note that clusterFR.m is implemented primarily for image visualization purposes and, owing to the local nature of the image corrections, it is not recommended in a workflow for quantitative image analysis.
            
            #### Pause point
            
            At this point, the drift-corrected, normalized and/or filtered image data can be manually inspected, used for further data analysis or imported into external software.
            
        
        Timing 10 min for setup, 0.5–12 h of unattended computer time (depending on data set size)
        
    3.  C
        
        **Automated segmentation and tracking with TGMM**
        
        1.  i
            
            Run the program 'ProcessStack' to generate a hierarchical segmentation for each time point. The software documentation explains how to parallelize the execution of this program on all time points using simple scripts in Unix and Windows.
            
            #### Critical Step
            
            Note that running the hierarchical segmentation algorithm in parallel for multiple time points might use all available computing resources. Thus, while the segmentation algorithm is running, the performance of other applications on this computer may be affected. The TGMM software package also includes the program 'ProcessStack\_woGPU', which offers the same functionality as 'ProcessStack' but does not require an nVidia GPU. This executable is useful for distributing the hierarchical segmentation task in cluster environments.
            
            #### Critical Step
            
            Step 1C(i) only needs to be repeated if the parameter 'backgroundThreshold' or any of the advanced parameters in the hierarchical segmentation category are changed in the file 'TGMM\_configFile.txt'. Otherwise, the existing binary files can be reused to run the tracking module multiple times with different parameter settings.
            
            #### Pause point
            
            Segmentation results are stored in binary files with the suffix 'hierarchicalSegmentation' (one per processed time point) in the same folder as the original image. These binary files contain all possible segmentations for different values of 'persistanceSegmentationTau'. Proceed to Step 1C(ii) to continue with automated cell tracking.
            
        2.  ii
            
            Run the program 'TGMM' to segment and track cells for all time points. This algorithm uses the binary files generated in the previous step to define super-voxels.
            
            [Troubleshooting](https://www.nature.com/articles/nprot.2015.111#Sec20)
            
            #### Pause point
            
            At this point, cell lineaging results are stored as XML files (one per processed time point). Proceed to Step 1D(i) to continue with data visualization and editing of the automatically generated tracking results, or proceed to Step 1E(i) to continue with the analysis of cell tracks.
            
        
        #### Critical Step
        
        The protocol described here describes how to run 'TGMM' for the test data set included in [Supplementary Software 4](https://www.nature.com/articles/nprot.2015.111#MOESM272) to verify that it executes correctly on your workstation. Users of Windows 7 64-bit machines can directly use the precompiled binaries located in the folder 'bin'. Users of other operating systems, such as Linux, first need to compile the code according to the instructions provided in the README file. In order to run the software on a new data set, use the configuration file 'TGMM\_configFile.txt' provided with the test data set as a template and modify parameters as needed (See [Box 3](https://www.nature.com/articles/nprot.2015.111#Sec19) for details).
        
        Timing 5 min for setup, 0.5–5 h of unattended computer time (depending on data set size)
        
    4.  D
        
        **Visualizing and editing lineaging results using CATMAID**
        
        1.  i
            
            Run the MATLAB script 'generateTilesFromFolder' provided in [Supplementary Software 6](https://www.nature.com/articles/nprot.2015.111#MOESM274) to transform all image stacks from Step 1A(ix) into sets of tiles that can be read and requested by the browser through its connection to CATMAID. The README file accompanying the script, as well as the user guide, provides instructions for setting each parameter.
            
            #### Critical Step
            
            The script needs to be executed on a computer with write access to the image server in order to save the newly generated image tiles.
            
            [Troubleshooting](https://www.nature.com/articles/nprot.2015.111#Sec20)
            
        2.  ii
            
            Log on to the CATMAID administrator website and select the option 'Add' in the Stack menu. A form requesting details about the image data generated in Step 1D(i) will appear in the browser. Completing this form creates a new entry in the CATMAID database with information about location and attributes of the image tiles. The documentation at [http://catmaid.org/importing\_data.html](http://catmaid.org/importing_data.html) provides more details on how to perform this step.
            
            #### Critical Step
            
            The parameter 'Tile source type' needs to be set to 5 to inform CATMAID that the images contain temporal information.
            
            #### Critical Step
            
            The parameters 'Num zoom levels' and 'Tile size' need to match the settings specified in the previous step.
            
            #### Pause point
            
            Partitioning image data into tiles only needs to be done once for each data set. Tiles are stored in the image server accessible by CATMAID and reused every time a new set of cell tracks is uploaded, thus avoiding image data duplication.
            
        3.  iii
            
            Log on to the CATMAID administrator website and select the option 'TGMM importer' in the Custom Views menu.
            
        4.  iv
            
            Specify where the XML files are located (field 'Xml basename') and which image data set should be associated with the XML files ('Dataset id' from Step 1D(ii)). The field 'Project name' allows assigning a unique name to this cell-lineage reconstruction.
            
            #### Critical Step
            
            The XML output files from Step 1C(ii) need to be copied to a location at which CATMAID can read from.
            
            [Troubleshooting](https://www.nature.com/articles/nprot.2015.111#Sec20)
            
            #### Pause point
            
            Tracking information is stored in the CATMAID database, and it can be edited, analyzed or visualized at any time.
            
        5.  v
            
            Open a browser and enter the URL of the web application CATMAID containing your data.
            
        6.  vi
            
            Select the project that you would like to work on.
            
            [Troubleshooting](https://www.nature.com/articles/nprot.2015.111#Sec20)
            
        7.  vii
            
            Use the sliders on the toolbar to navigate the image data in five dimensions. In order to visualize and manipulate the cell tracking information, select the 'Tracing tool' in the toolbar. Note that a click on the '?' icon will display all possible actions in each view. CATMAID offers many different types of editing and visualization operations for the cell tracking data (add/delete edge or point, display lineage, show orthogonal planes, etc.). A comprehensive documentation of all functionality can be found at [http://catmaid.org/](http://catmaid.org/) and in the user guide included in [Supplementary Software 5](https://www.nature.com/articles/nprot.2015.111#MOESM273).
            
            #### Critical Step
            
            We recommend periodic backups of the CATMAID database (at least once a week) in order to minimize the risk of data loss. As the database only contains points in object space (i.e., no image data), the size of these backups is typically fairly small.
            
            #### Pause point
            
            This step can be interrupted at any time. Every time an operation is performed by the user, the change is immediately stored in the CATMAID database and an entry is added to the log table. Thus, work on a specific project can be resumed at any time.
            
        
        #### Critical Step
        
        The protocol described here explains how to use the CATMAID browser interface for visualizing and editing cell tracks. Before executing this protocol, make sure to install and configure the CATMAID backend service according to the instructions in [Equipment Setup](https://www.nature.com/articles/nprot.2015.111#Sec14).
        
        Timing 0.5–4 h (depending on data set size)
        
    5.  E
        
        **Importing tracking information into MATLAB and preparing videos for visualizing image data and cell-lineage reconstructions**
        
        1.  i
            
            Extract the contents of the archive provided in [Supplementary Software 6](https://www.nature.com/articles/nprot.2015.111#MOESM274) or download the MATLAB scripts for interacting with the PostgreSQL database accessed by CATMAID for storing lineage information using the following Git command:git clone https://fernandoamat@bitbucket.org/fernandoamat/catmaid-matlab-code.git
            
        2.  ii
            
            Use the MATLAB script 'scriptRetrieveNodeWithTag' to import all data points of a specific project from the CATMAID database into MATLAB. The README file accompanying the script provides documentation on how to set each of the required parameters. The script returns an _N_ × 10 MATLAB array, where _N_ is the number of data points in the database for the requested project. The ten columns contain the following information:
            
        3.  iii
            
            Import tracking information from TGMM into MATLAB. The output from Step 1C(v) is stored in XML files that can be imported into the same type of MATLAB array, as described in the previous step. This import functionality is provided by the script 'parseMixtureGaussiansXml2trackingMatrixCATMAIDformat'. We note, however, that this MATLAB array format does not cover all of the information present in the XML files. For example, super-voxel segmentation information is lost. To import all available information into MATLAB, execute the script 'readXMLmixtureGaussians' for each time point. This script returns a structure mimicking the attributes of the XML file for each database object. More information about the various attributes can be found in the documentation accompanying the script.
            
            #### Critical Step
            
            The XML files were generated using C++ code, in which indices start at 0. In contrast, MATLAB convention has indices start at 1. Thus, for code written in MATLAB, all indices need to be offset by +1. For example, if the parent ID is 3, the index 4 needs to be used in MATLAB in order to retrieve the correct cell-lineage information from the MATLAB structure.
            
        4.  iv
            
            Prepare videos for visualizing image data and cell-lineage reconstructions. Once the data have been imported into MATLAB as an _N_ × 10 array (as described in Step 1E(iii)), the cell-lineage information can be visualized in a variety of ways. For data visualization using the commercial software package Imaris, we provide export scripts that enable the data transfer of cell tracks to Imaris. This approach enables joint rendering of microscopy data and cell-lineage information ([Fig. 7](https://www.nature.com/articles/nprot.2015.111#Fig7)). The ImarisXT interface and the scripts provided in [Supplementary Software 6](https://www.nature.com/articles/nprot.2015.111#MOESM274) are required to establish communication between MATLAB and Imaris.
            
            **Figure 7: Application example in _Drosophila_ development.**
            
            [![figure 7](https://media.springernature.com/lw685/springer-static/image/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_Fig7_HTML.jpg)](https://www.nature.com/articles/nprot.2015.111/figures/7)
            
            (**a**) Maximum-intensity projections of image data at four time points of a SiMView time-lapse data set of _Drosophila_ embryonic development<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 8" title="Tomer, R., Khairy, K., Amat, F. &amp; Keller, P.J. Quantitative high-speed imaging of entire developing embryos with simultaneous multiview light-sheet microscopy. Nat. Methods 9, 755–763 (2012)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR8" id="ref-link-section-d543302138e2884">8</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e2887">39</a></sup> (left, dorsal view; right, ventral view). The complete data set comprises 2,881 time points (each consisting of a four-view recording of the embryo with 4 × 154 images) recorded in 30-s intervals, and it was processed with the pipeline presented in [Figures 1](https://www.nature.com/articles/nprot.2015.111#Fig1) and [2](https://www.nature.com/articles/nprot.2015.111#Fig2). The total data set size is 4.35 TB (1,774,696 images). The age of the nuclei-labeled (His2Av-mRFP1) embryo is shown in hours and minutes after egg laying in the bottom right corner of the dorsal view panels. (**b**) Visualization of a cell-lineage reconstruction of early nervous system development in the _Drosophila_ ventral nerve cord. The cell-lineage reconstruction was performed with TGMM and CATMAID, using the data set visualized in **a**. The data were rendered with Imaris, using microscopy image data at time point (_t_) 50 (see second row in **a**). Green spheres represent the positions of progenitor cell nuclei at time point 50. Lines represent complete cell tracks using a color code to indicate time (from purple to yellow: 2.9–5.4 h after egg laying). Scale bars, 50 μm.
            
            [Full size image](https://www.nature.com/articles/nprot.2015.111/figures/7)
            
        5.  v
            
            Open a single Imaris session (if there is more than one active Imaris session, the MATLAB script will not know which session the data need to be exported to).
            
        6.  vi
            
            In Imaris, open the time-lapse microscopy image data used for cell tracking, and click on the Surpass Scene folder so that it is highlighted.
            
        7.  vii
            
            Without closing Imaris, switch to a MATLAB terminal and import the cell tracking data, as described in Step 1E(iii).
            
        8.  viii
            
            Execute the MATLAB script 'parseCATMAIDdbToImarisMultiSpots'. Once the script execution has finished, a new Imaris spot object will appear in the Imaris window for each imported cell lineage.
            
            [Troubleshooting](https://www.nature.com/articles/nprot.2015.111#Sec20)
            
        9.  ix
            
            Save the Imaris project to store the imported cell lineage information.
            
        
        #### Critical Step
        
        Segmentation and tracking results can be imported into MATLAB at different stages of the pipeline. If you would like to analyze the output from Step 1D(vii), then proceed to Step 1E(ii). If you would like to analyze the output from Step 1C(ii), then proceed to Step 1E(iii).
        
        Timing 5 min
        
    
    #### Table 4
    
    | 
    Option
    
     | 
    
    Module
    
     | 
    
    Description
    
     |
    | --- | --- | --- |
    | 
    
    1A
    
     | 
    
    Lossless image compression and/or multiview image fusion
    
     | 
    
    We explain how large amounts of image data are efficiently stored and how arbitrary regions of interest in large image data are rapidly retrieved using our block-based lossless compression file format (KLB). We furthermore present MATLAB scripts for content-based registration and fusion of time-lapse, multiview image data
    
     |
    | 
    
    1B
    
     | 
    
    Drift correction and intensity normalization
    
     | 
    
    We discuss the use of our MATLAB scripts for drift correction and intensity normalization of time-lapse 3D stacks
    
     |
    | 
    
    1C
    
     | 
    
    Segmentation and tracking with TGMM
    
     | 
    
    We provide protocols for our TGMM software for automated large-scale segmentation and tracking of fluorescently labeled cell nuclei
    
     |
    | 
    
    1D
    
     | 
    
    Data visualization and editing with CATMAID
    
     | 
    
    We present a branch of CATMAID<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 37" title="Saalfeld, S., Cardona, A., Hartenstein, V. &amp; Tomancˇák, P CATMAID: collaborative annotation toolkit for massive amounts of image data. Bioinformatics 25, 1984–1986 (2009)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR37" id="ref-link-section-d543302138e3105">37</a>,<a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 38" title="Cardona, A. Collaborative annotation toolkit for massive amounts of image data (CATMAID) GitHub repository 
                      https://github.com/acardona/CATMAID
                      
                     (2015)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR38" id="ref-link-section-d543302138e3108">38</a></sup> that facilitates the visualization of five-dimensional microscopy data sets and allows editing associated cell tracking results
    
     |
    | 
    
    1E
    
     | 
    
    Preparing videos for visualizing image data and cell lineage reconstructions
    
     | 
    
    We describe MATLAB scripts for importing, analyzing and visualizing large-scale cell lineage reconstructions
    
     |
    

Troubleshooting
---------------

Troubleshooting advice can be found in [Table 3](https://www.nature.com/articles/nprot.2015.111#Tab3).

**Table 3 Troubleshooting table.**

[Full size table](https://www.nature.com/articles/nprot.2015.111/tables/5)

Timing
------

Step 1A, lossless image compression and/or multiview image fusion: 5 min for setup, and 0.5–12 h of unattended computer time (depending on data set size)

Step 1B, drift correction and intensity normalization: 10 min for setup, and 0.5–12 h of unattended computer time (depending on data set size)

Step 1C, segmentation and tracking with TGMM: 5 min for setup, and 0.5–5 h of unattended computer time (depending on data set size)

Step 1D, data visualization and editing with CATMAID: 0.5–4 h (depending on data set size)

Step 1E, preparing videos for visualizing image data and cell-lineage reconstructions: 5 min

Anticipated results
-------------------

By following the steps in this protocol carefully, the user should expect to be able to convert microscopy data sets of animal development with up to several terabytes of image data per experiment into curated cell-lineage reconstructions ([Fig. 7](https://www.nature.com/articles/nprot.2015.111#Fig7)). A single computer workstation is sufficient for the routine use of the presented computational framework at all stages of the protocol. The raw microscopy image data are efficiently stored in the KLB lossless image compression format. If multiview image data recorded with a SiMView-like microscope is used as a starting point, our pipeline enables rapid content-based multiview registration and fusion. Together, these steps reduce typical multiterabyte light-sheet microscopy data sets to a few tens of gigabytes of compressed image data, thus efficiently eliminating data storage bottlenecks without data loss. After these initial data management steps, our image processing and data analysis protocol leads to a CATMAID database that contains comprehensive cell-lineage information for the reconstructed data set, including a log of all edits performed by each user. The MATLAB scripts included in this protocol can be used to visualize final results and to generate publication-quality videos. They also facilitate data import into a MATLAB array, which gives access to a wide spectrum of further analyses, such as computation of cell-lineage statistics or investigation of morphodynamic features, including cell cycle lengths, cell velocities and temporal changes in gene expression levels in each tracked cell lineage.

When using KLB lossless compression in combination with background masking, a 10–200-fold reduction in data size can be expected for typical fluorescence microscopy recordings ([Figs. 3](https://www.nature.com/articles/nprot.2015.111#Fig3) and [4](https://www.nature.com/articles/nprot.2015.111#Fig4); and 30- to 500-fold with additional multiview image fusion). Aside from reducing storage capacity needs, KLB image compression also helps improve data transfer rates and access speed. The TGMM software is capable of segmenting and tracking ∼26,000 cells per minute on a single workstation<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e3479">39</a></sup>, with an average linkage accuracy ranging from 99% for zebrafish embryos to 90% for mouse embryos.

In our experience, novice users can usually familiarize themselves with the overall pipeline within a few days (see 'Level of expertise needed to implement the protocol' in the INTRODUCTION for specific details), as most of the scripts used in this protocol simply require adjusting a few parameters. If completely error-free cell-lineage reconstructions are required, the most time-intensive part of the protocol is the manual curation of cell -lineage results produced by the TGMM software. This task is facilitated by the web application CATMAID, which enables typical data curation rates of ∼1,400 data points per hour and thus offers the possibility of system-level cell lineaging. For example, a fully curated cell-lineage reconstruction of the early _Drosophila_ nervous system, tracking 92% of S1 neuroblasts from their blastoderm origins up to their second cell division (over 116,000 data points spanning more than 300 time points), was performed within 3 weeks<sup><a data-track="click" data-track-action="reference anchor" data-track-label="link" data-test="citation-ref" aria-label="Reference 39" title="Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. Nat. Methods 11, 951–958 (2014)." href="https://www.nature.com/articles/nprot.2015.111#ref-CR39" id="ref-link-section-d543302138e3489">39</a></sup>.

References
----------

1.  Voie, A.H., Burns, D.H. & Spelman, F.A. Orthogonal-plane fluorescence optical sectioning: three-dimensional imaging of macroscopic biological specimens. _J. Microsc._ **170**, 229–236 (1993).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:STN:280:DyaK3szotFKkuw%3D%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=8371260)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Orthogonal-plane%20fluorescence%20optical%20sectioning%3A%20three-dimensional%20imaging%20of%20macroscopic%20biological%20specimens&journal=J.%20Microsc.&volume=170&pages=229-236&publication_year=1993&author=Voie%2CAH&author=Burns%2CDH&author=Spelman%2CFA) 
    
2.  Fuchs, E., Jaffe, J., Long, R. & Azam, F. Thin laser light sheet microscope for microbial oceanography. _Opt. Express_ **10**, 145–154 (2002).
    
    [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=19424342)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Thin%20laser%20light%20sheet%20microscope%20for%20microbial%20oceanography&journal=Opt.%20Express&volume=10&pages=145-154&publication_year=2002&author=Fuchs%2CE&author=Jaffe%2CJ&author=Long%2CR&author=Azam%2CF) 
    
3.  Huisken, J., Swoger, J., Del Bene, F., Wittbrodt, J. & Stelzer, E.H.K. Optical sectioning deep inside live embryos by selective plane illumination microscopy. _Science_ **305**, 1007–1009 (2004).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD2cXmsVGmsbY%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=15310904)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Optical%20sectioning%20deep%20inside%20live%20embryos%20by%20selective%20plane%20illumination%20microscopy&journal=Science&volume=305&pages=1007-1009&publication_year=2004&author=Huisken%2CJ&author=Swoger%2CJ&author=Del%20Bene%2CF&author=Wittbrodt%2CJ&author=Stelzer%2CEHK) 
    
4.  Keller, P.J., Schmidt, A.D., Wittbrodt, J. & Stelzer, E.H. Reconstruction of zebrafish early embryonic development by scanned light sheet microscopy. _Science_ **322**, 1065–1069 (2008).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD1cXhtlGgsr7K)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=18845710)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Reconstruction%20of%20zebrafish%20early%20embryonic%20development%20by%20scanned%20light%20sheet%20microscopy&journal=Science&volume=322&pages=1065-1069&publication_year=2008&author=Keller%2CPJ&author=Schmidt%2CAD&author=Wittbrodt%2CJ&author=Stelzer%2CEH) 
    
5.  Ahrens, M.B., Orger, M.B., Robson, D.N., Li, J.M. & Keller, P.J. Whole-brain functional imaging at cellular resolution using light-sheet microscopy. _Nat. Methods_ **10**, 413–420 (2013).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3sXksVKqtL4%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23524393)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Whole-brain%20functional%20imaging%20at%20cellular%20resolution%20using%20light-sheet%20microscopy&journal=Nat.%20Methods&volume=10&pages=413-420&publication_year=2013&author=Ahrens%2CMB&author=Orger%2CMB&author=Robson%2CDN&author=Li%2CJM&author=Keller%2CPJ) 
    
6.  Wu, Y. et al. Spatially isotropic four-dimensional imaging with dual-view plane illumination microscopy. _Nat. Biotechnol._ **31**, 1032–1038 (2013).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3sXhsFyms7zE)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=24108093)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4105320)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Spatially%20isotropic%20four-dimensional%20imaging%20with%20dual-view%20plane%20illumination%20microscopy&journal=Nat.%20Biotechnol.&volume=31&pages=1032-1038&publication_year=2013&author=Wu%2CY) 
    
7.  Krzic, U., Gunther, S., Saunders, T.E., Streichan, S.J. & Hufnagel, L. Multiview light-sheet microscope for rapid _in toto_ imaging. _Nat. Methods_ **9**, 730–733 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XnvVyrsL4%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=22660739)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Multiview%20light-sheet%20microscope%20for%20rapid%20in%20toto%20imaging&journal=Nat.%20Methods&volume=9&pages=730-733&publication_year=2012&author=Krzic%2CU&author=Gunther%2CS&author=Saunders%2CTE&author=Streichan%2CSJ&author=Hufnagel%2CL) 
    
8.  Tomer, R., Khairy, K., Amat, F. & Keller, P.J. Quantitative high-speed imaging of entire developing embryos with simultaneous multiview light-sheet microscopy. _Nat. Methods_ **9**, 755–763 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XnvVymt70%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=22660741)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Quantitative%20high-speed%20imaging%20of%20entire%20developing%20embryos%20with%20simultaneous%20multiview%20light-sheet%20microscopy&journal=Nat.%20Methods&volume=9&pages=755-763&publication_year=2012&author=Tomer%2CR&author=Khairy%2CK&author=Amat%2CF&author=Keller%2CPJ) 
    
9.  Schmid, B. et al. High-speed panoramic light-sheet microscopy reveals global endodermal cell dynamics. _Nat. Commun._ **4**, 2207 (2013).
    
    [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23884240)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=High-speed%20panoramic%20light-sheet%20microscopy%20reveals%20global%20endodermal%20cell%20dynamics&journal=Nat.%20Commun.&volume=4&publication_year=2013&author=Schmid%2CB) 
    
10.  Holekamp, T.F., Turaga, D. & Holy, T.E. Fast three-dimensional fluorescence imaging of activity in neural populations by objective-coupled planar illumination microscopy. _Neuron_ **57**, 661–672 (2008).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD1cXjslegt7o%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=18341987)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Fast%20three-dimensional%20fluorescence%20imaging%20of%20activity%20in%20neural%20populations%20by%20objective-coupled%20planar%20illumination%20microscopy&journal=Neuron&volume=57&pages=661-672&publication_year=2008&author=Holekamp%2CTF&author=Turaga%2CD&author=Holy%2CTE) 
    
11.  Truong, T.V., Supatto, W., Koos, D.S., Choi, J.M. & Fraser, S.E. Deep and fast live imaging with two-photon scanned light-sheet microscopy. _Nat. Methods_ **8**, 757–760 (2011).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3MXovFyhs7s%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=21765409)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Deep%20and%20fast%20live%20imaging%20with%20two-photon%20scanned%20light-sheet%20microscopy&journal=Nat.%20Methods&volume=8&pages=757-760&publication_year=2011&author=Truong%2CTV&author=Supatto%2CW&author=Koos%2CDS&author=Choi%2CJM&author=Fraser%2CSE) 
    
12.  Gao, L. et al. Noninvasive imaging beyond the diffraction limit of 3D dynamics in thickly fluorescent specimens. _Cell_ **151**, 1370–1385 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XhvVajurfJ)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23217717)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3615549)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Noninvasive%20imaging%20beyond%20the%20diffraction%20limit%20of%203D%20dynamics%20in%20thickly%20fluorescent%20specimens&journal=Cell&volume=151&pages=1370-1385&publication_year=2012&author=Gao%2CL) 
    
13.  Chen, B.C. et al. Lattice light-sheet microscopy: imaging molecules to embryos at high spatiotemporal resolution. _Science_ **346**, 1257998 (2014).
    
    [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=25342811)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4336192)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Lattice%20light-sheet%20microscopy%3A%20imaging%20molecules%20to%20embryos%20at%20high%20spatiotemporal%20resolution&journal=Science&volume=346&publication_year=2014&author=Chen%2CBC) 
    
14.  Keller, P.J. et al. Fast, high-contrast imaging of animal development with scanned light sheet-based structured-illumination microscopy. _Nat. Methods_ **7**, 637–642 (2010).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3cXotlWrsr4%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=20601950)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4418465)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Fast%2C%20high-contrast%20imaging%20of%20animal%20development%20with%20scanned%20light%20sheet-based%20structured-illumination%20microscopy&journal=Nat.%20Methods&volume=7&pages=637-642&publication_year=2010&author=Keller%2CPJ) 
    
15.  Capoulade, J., Wachsmuth, M., Hufnagel, L. & Knop, M. Quantitative fluorescence imaging of protein diffusion and interaction in living cells. _Nat. Biotechnol._ **29**, 835–839 (2011).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3MXpvVOktbg%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=21822256)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Quantitative%20fluorescence%20imaging%20of%20protein%20diffusion%20and%20interaction%20in%20living%20cells&journal=Nat.%20Biotechnol.&volume=29&pages=835-839&publication_year=2011&author=Capoulade%2CJ&author=Wachsmuth%2CM&author=Hufnagel%2CL&author=Knop%2CM) 
    
16.  Keller, P.J. Imaging morphogenesis: technological advances and biological insights. _Science_ **340**, 1234168 (2013).
    
    [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23744952)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Imaging%20morphogenesis%3A%20technological%20advances%20and%20biological%20insights&journal=Science&volume=340&publication_year=2013&author=Keller%2CPJ) 
    
17.  Pantazis, P. & Supatto, W. Advances in whole-embryo imaging: a quantitative transition is underway. _Nat. Rev. Mol. Cell Biol._ **15**, 327–339 (2014).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC2cXmtlWltr4%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=24739741)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Advances%20in%20whole-embryo%20imaging%3A%20a%20quantitative%20transition%20is%20underway&journal=Nat.%20Rev.%20Mol.%20Cell%20Biol.&volume=15&pages=327-339&publication_year=2014&author=Pantazis%2CP&author=Supatto%2CW) 
    
18.  Stelzer, E.H. Light-sheet fluorescence microscopy for quantitative biology. _Nat. Methods_ **12**, 23–26 (2014).
    
    [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Light-sheet%20fluorescence%20microscopy%20for%20quantitative%20biology&journal=Nat.%20Methods&volume=12&pages=23-26&publication_year=2014&author=Stelzer%2CEH) 
    
19.  Huisken, J. Slicing embryos gently with laser light sheets. _Bioessays_ **34**, 406–411 (2012).
    
    [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=22396246)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Slicing%20embryos%20gently%20with%20laser%20light%20sheets&journal=Bioessays&volume=34&pages=406-411&publication_year=2012&author=Huisken%2CJ) 
    
20.  Pampaloni, F., Reynaud, E.G. & Stelzer, E.H. The third dimension bridges the gap between cell culture and live tissue. _Nat. Rev. Mol. Cell Biol._ **8**, 839–845 (2007).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD2sXhtVKmt7vL)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=17684528)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=The%20third%20dimension%20bridges%20the%20gap%20between%20cell%20culture%20and%20live%20tissue&journal=Nat.%20Rev.%20Mol.%20Cell%20Biol.&volume=8&pages=839-845&publication_year=2007&author=Pampaloni%2CF&author=Reynaud%2CEG&author=Stelzer%2CEH) 
    
21.  Keller, P.J., Ahrens, M.B. & Freeman, J. Light-sheet imaging for systems neuroscience. _Nat. Methods_ **12**, 27–29 (2014).
    
    [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Light-sheet%20imaging%20for%20systems%20neuroscience&journal=Nat.%20Methods&volume=12&pages=27-29&publication_year=2014&author=Keller%2CPJ&author=Ahrens%2CMB&author=Freeman%2CJ) 
    
22.  Keller, P.J. & Ahrens, M.B. Visualizing whole-brain activity and development at the single-cell level using light-sheet microscopy. _Neuron_ **85**, 462–483 (2015).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC2MXisFeru7w%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=25654253)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Visualizing%20whole-brain%20activity%20and%20development%20at%20the%20single-cell%20level%20using%20light-sheet%20microscopy&journal=Neuron&volume=85&pages=462-483&publication_year=2015&author=Keller%2CPJ&author=Ahrens%2CMB) 
    
23.  Lemon, W.C. & Keller, P.J. Live imaging of nervous system development and function using light-sheet microscopy. _Mol. Reprod. Dev._ **82**, 605–618 (2015).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3sXhsVCntLzN)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23996352)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Live%20imaging%20of%20nervous%20system%20development%20and%20function%20using%20light-sheet%20microscopy&journal=Mol.%20Reprod.%20Dev.&volume=82&pages=605-618&publication_year=2015&author=Lemon%2CWC&author=Keller%2CPJ) 
    
24.  Megason, S.G. & Fraser, S.E. Imaging in systems biology. _Cell_ **130**, 784–795 (2007).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD2sXhtV2ntL%2FO)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=17803903)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Imaging%20in%20systems%20biology&journal=Cell&volume=130&pages=784-795&publication_year=2007&author=Megason%2CSG&author=Fraser%2CSE) 
    
25.  Khairy, K. & Keller, P.J. Reconstructing embryonic development. _Genesis_ **49**, 488–513 (2011).
    
    [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=21140407)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Reconstructing%20embryonic%20development&journal=Genesis&volume=49&pages=488-513&publication_year=2011&author=Khairy%2CK&author=Keller%2CPJ) 
    
26.  McMahon, A., Supatto, W., Fraser, S.E. & Stathopoulos, A. Dynamic analyses of _Drosophila_ gastrulation provide insights into collective cell migration. _Science_ **322**, 1546–1550 (2008).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD1cXhsVGltb%2FO)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=19056986)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2801059)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Dynamic%20analyses%20of%20Drosophila%20gastrulation%20provide%20insights%20into%20collective%20cell%20migration&journal=Science&volume=322&pages=1546-1550&publication_year=2008&author=McMahon%2CA&author=Supatto%2CW&author=Fraser%2CSE&author=Stathopoulos%2CA) 
    
27.  Fernandez, R. et al. Imaging plant growth in 4D: robust tissue reconstruction and lineaging at cell resolution. _Nat. Methods_ **7**, 547–553 (2010).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3cXntlSjs7Y%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=20543845)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Imaging%20plant%20growth%20in%204D%3A%20robust%20tissue%20reconstruction%20and%20lineaging%20at%20cell%20resolution&journal=Nat.%20Methods&volume=7&pages=547-553&publication_year=2010&author=Fernandez%2CR) 
    
28.  Bosveld, F. et al. Mechanical control of morphogenesis by Fat/Dachsous/Four-jointed planar cell polarity pathway. _Science_ **336**, 724–727 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XmsFymuro%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=22499807)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Mechanical%20control%20of%20morphogenesis%20by%20Fat%2FDachsous%2FFour-jointed%20planar%20cell%20polarity%20pathway&journal=Science&volume=336&pages=724-727&publication_year=2012&author=Bosveld%2CF) 
    
29.  Murray, J.I. et al. Automated analysis of embryonic gene expression with cellular resolution in _C. elegans_. _Nat. Methods_ **5**, 703–709 (2008).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD1cXptFSrtLw%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=18587405)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2553703)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Automated%20analysis%20of%20embryonic%20gene%20expression%20with%20cellular%20resolution%20in%20C.%20elegans&journal=Nat.%20Methods&volume=5&pages=703-709&publication_year=2008&author=Murray%2CJI) 
    
30.  Liu, X. et al. Analysis of cell fate from single-cell gene expression profiles in _C. elegans_. _Cell_ **139**, 623–633 (2009).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD1MXhsFKltLzF)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=19879847)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4709123)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Analysis%20of%20cell%20fate%20from%20single-cell%20gene%20expression%20profiles%20in%20C.%20elegans&journal=Cell&volume=139&pages=623-633&publication_year=2009&author=Liu%2CX) 
    
31.  Trichas, G. et al. Multi-cellular rosettes in the mouse visceral endoderm facilitate the ordered migration of anterior visceral endoderm cells. _PLoS Biol._ **10**, e1001256 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XislamtLs%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=22346733)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3274502)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Multi-cellular%20rosettes%20in%20the%20mouse%20visceral%20endoderm%20facilitate%20the%20ordered%20migration%20of%20anterior%20visceral%20endoderm%20cells&journal=PLoS%20Biol.&volume=10&publication_year=2012&author=Trichas%2CG) 
    
32.  Xiong, F. et al. Specified neural progenitors sort to form sharp domains after noisy Shh signaling. _Cell_ **153**, 550–561 (2013).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3sXmsleksLg%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23622240)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3674856)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Specified%20neural%20progenitors%20sort%20to%20form%20sharp%20domains%20after%20noisy%20Shh%20signaling&journal=Cell&volume=153&pages=550-561&publication_year=2013&author=Xiong%2CF) 
    
33.  Du, Z., Santella, A., He, F., Tiongson, M. & Bao, Z. _De novo_ inference of systems-level mechanistic models of development from live-imaging-based phenotype analysis. _Cell_ **156**, 359–372 (2014).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC2cXhtF2jsbo%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=24439388)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3998820)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=De%20novo%20inference%20of%20systems-level%20mechanistic%20models%20of%20development%20from%20live-imaging-based%20phenotype%20analysis&journal=Cell&volume=156&pages=359-372&publication_year=2014&author=Du%2CZ&author=Santella%2CA&author=He%2CF&author=Tiongson%2CM&author=Bao%2CZ) 
    
34.  Panier, T. et al. Fast functional imaging of multiple brain regions in intact zebrafish larvae using selective plane illumination microscopy. _Front. Neural Circuits_ **7**, 65 (2013).
    
    [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23576959)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3620503)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Fast%20functional%20imaging%20of%20multiple%20brain%20regions%20in%20intact%20zebrafish%20larvae%20using%20selective%20plane%20illumination%20microscopy&journal=Front.%20Neural%20Circuits&volume=7&publication_year=2013&author=Panier%2CT) 
    
35.  Lemon, W. et al. Whole central nervous system functional imaging in larval _Drosophila_. _Nat. Commun._ **6**, 7924 (2015).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC2MXhsVKhtbnN)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=26263051)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4918770)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Whole%20central%20nervous%20system%20functional%20imaging%20in%20larval%20Drosophila&journal=Nat.%20Commun.&volume=6&publication_year=2015&author=Lemon%2CW) 
    
36.  Alivisatos, A.P. et al. The brain activity map project and the challenge of functional connectomics. _Neuron_ **74**, 970–974 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XptVKhs7s%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=22726828)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3597383)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=The%20brain%20activity%20map%20project%20and%20the%20challenge%20of%20functional%20connectomics&journal=Neuron&volume=74&pages=970-974&publication_year=2012&author=Alivisatos%2CAP) 
    
37.  Saalfeld, S., Cardona, A., Hartenstein, V. & Tomancˇák, P CATMAID: collaborative annotation toolkit for massive amounts of image data. _Bioinformatics_ **25**, 1984–1986 (2009).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD1MXovVektbs%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=19376822)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2712332)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=CATMAID%3A%20collaborative%20annotation%20toolkit%20for%20massive%20amounts%20of%20image%20data&journal=Bioinformatics&volume=25&pages=1984-1986&publication_year=2009&author=Saalfeld%2CS&author=Cardona%2CA&author=Hartenstein%2CV&author=Tomanc%CB%87%C3%A1k%2CP) 
    
38.  Cardona, A. Collaborative annotation toolkit for massive amounts of image data (CATMAID) GitHub repository [https://github.com/acardona/CATMAID](https://github.com/acardona/CATMAID) (2015).
    
39.  Amat, F. et al. Fast, accurate reconstruction of cell lineages from large-scale fluorescence microscopy data. _Nat. Methods_ **11**, 951–958 (2014).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC2cXht1KktrzJ)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=25042785)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Fast%2C%20accurate%20reconstruction%20of%20cell%20lineages%20from%20large-scale%20fluorescence%20microscopy%20data&journal=Nat.%20Methods&volume=11&pages=951-958&publication_year=2014&author=Amat%2CF) 
    
40.  Lauri, A. et al. Development of the annelid axochord: insights into notochord evolution. _Science_ **345**, 1365–1368 (2014).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC2cXhsV2qtLzJ)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=25214631)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Development%20of%20the%20annelid%20axochord%3A%20insights%20into%20notochord%20evolution&journal=Science&volume=345&pages=1365-1368&publication_year=2014&author=Lauri%2CA) 
    
41.  Preibisch, S., Saalfeld, S., Schindelin, J. & Tomancak, P. Software for bead-based registration of selective plane illumination microscopy data. _Nat. Methods_ **7**, 418–419 (2010).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3cXmsF2iu74%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=20508634)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Software%20for%20bead-based%20registration%20of%20selective%20plane%20illumination%20microscopy%20data&journal=Nat.%20Methods&volume=7&pages=418-419&publication_year=2010&author=Preibisch%2CS&author=Saalfeld%2CS&author=Schindelin%2CJ&author=Tomancak%2CP) 
    
42.  Bao, Z. et al. Automated cell lineage tracing in _Caenorhabditis elegans_. _Proc. Natl. Acad. Sci. USA_ **103**, 2707–2712 (2006).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD28XksF2rtrg%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=16477039)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC1413828)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Automated%20cell%20lineage%20tracing%20in%20Caenorhabditis%20elegans&journal=Proc.%20Natl.%20Acad.%20Sci.%20USA&volume=103&pages=2707-2712&publication_year=2006&author=Bao%2CZ) 
    
43.  Murray, J.I., Bao, Z., Boyle, T.J. & Waterston, R.H. The lineaging of fluorescently-labeled _Caenorhabditis elegans_ embryos with StarryNite and AceTree. _Nat. Protoc._ **1**, 1468–1476 (2006).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD28Xht1eitL7E)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=17406437)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=The%20lineaging%20of%20fluorescently-labeled%20Caenorhabditis%20elegans%20embryos%20with%20StarryNite%20and%20AceTree&journal=Nat.%20Protoc.&volume=1&pages=1468-1476&publication_year=2006&author=Murray%2CJI&author=Bao%2CZ&author=Boyle%2CTJ&author=Waterston%2CRH) 
    
44.  Giurumescu, C.A. et al. Quantitative semi-automated analysis of morphogenesis with single-cell resolution in complex embryos. _Development_ **139**, 4271–4279 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XhvVKltrfN)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23052905)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3478691)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Quantitative%20semi-automated%20analysis%20of%20morphogenesis%20with%20single-cell%20resolution%20in%20complex%20embryos&journal=Development&volume=139&pages=4271-4279&publication_year=2012&author=Giurumescu%2CCA) 
    
45.  Olivier, N. et al. Cell lineage reconstruction of early zebrafish embryos using label-free nonlinear microscopy. _Science_ **329**, 967–971 (2010).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3cXhtVaqurzK)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=20724640)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Cell%20lineage%20reconstruction%20of%20early%20zebrafish%20embryos%20using%20label-free%20nonlinear%20microscopy&journal=Science&volume=329&pages=967-971&publication_year=2010&author=Olivier%2CN) 
    
46.  Kausler, B.X. et al. A discrete chain graph model for 3D+t cell tracking with high misdetection robustness. _ECCV_ **7574**, 144–157 (2012).
    
    [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20discrete%20chain%20graph%20model%20for%203D%2Bt%20cell%20tracking%20with%20high%20misdetection%20robustness&journal=ECCV&volume=7574&pages=144-157&publication_year=2012&author=Kausler%2CBX) 
    
47.  Stegmaier, J. et al. Fast segmentation of stained nuclei in terabyte-scale, time resolved 3D microscopy image stacks. _PLoS ONE_ **9**, e90036 (2014).
    
    [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=24587204)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3937404)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Fast%20segmentation%20of%20stained%20nuclei%20in%20terabyte-scale%2C%20time%20resolved%203D%20microscopy%20image%20stacks&journal=PLoS%20ONE&volume=9&publication_year=2014&author=Stegmaier%2CJ) 
    
48.  Schiegg, M. et al. Graphical model for joint segmentation and tracking of multiple dividing cells. _Bioinformatics_ **31**, 948–956 (2014).
    
    [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=25406328)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Graphical%20model%20for%20joint%20segmentation%20and%20tracking%20of%20multiple%20dividing%20cells&journal=Bioinformatics&volume=31&pages=948-956&publication_year=2014&author=Schiegg%2CM) 
    
49.  Allan, C. et al. OMERO: flexible, model-driven data management for experimental biology. _Nat. Methods_ **9**, 245–253 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XivV2nsrw%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=22373911)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3437820)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=OMERO%3A%20flexible%2C%20model-driven%20data%20management%20for%20experimental%20biology&journal=Nat.%20Methods&volume=9&pages=245-253&publication_year=2012&author=Allan%2CC) 
    
50.  Megason, S.G. _In toto_ imaging of embryogenesis with confocal time-lapse microscopy. _Methods Mol. Biol._ **546**, 317–332 (2009).
    
    [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=19378112)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2826616)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=In%20toto%20imaging%20of%20embryogenesis%20with%20confocal%20time-lapse%20microscopy&journal=Methods%20Mol.%20Biol.&volume=546&pages=317-332&publication_year=2009&author=Megason%2CSG) 
    
51.  Schroeder, W., Martin, K. & Lorensen, B. _The Visualization Toolkit: An Object-Oriented Approach to 3D Graphics_. 4th edn. (Kitware, 2006).
    
52.  Peng, H., Ruan, Z., Long, F., Simpson, J.H. & Myers, E.W. V3D enables real-time 3D visualization and quantitative analysis of large-scale biological image data sets. _Nat. Biotechnol._ **28**, 348–353 (2010).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3cXjt1Ogtb8%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=20231818)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2857929)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=V3D%20enables%20real-time%203D%20visualization%20and%20quantitative%20analysis%20of%20large-scale%20biological%20image%20data%20sets&journal=Nat.%20Biotechnol.&volume=28&pages=348-353&publication_year=2010&author=Peng%2CH&author=Ruan%2CZ&author=Long%2CF&author=Simpson%2CJH&author=Myers%2CEW) 
    
53.  Bria, A., Iannello, G. & Peng, H. An open-source VAA3D plugin for real-time 3D visualization of terabyte-sized volumetric images. _ISBI_, 520–523 (2015).
    
54.  Pietzsch, T., Saalfeld, S., Preibisch, S. & Tomancak, P. BigDataViewer: visualization and processing for large image data sets. _Nat. Methods_ **12**, 481–483 (2015).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC2MXht1WrurfL)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=26020499)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=BigDataViewer%3A%20visualization%20and%20processing%20for%20large%20image%20data%20sets&journal=Nat.%20Methods&volume=12&pages=481-483&publication_year=2015&author=Pietzsch%2CT&author=Saalfeld%2CS&author=Preibisch%2CS&author=Tomancak%2CP) 
    
55.  Akerboom, J. et al. Optimization of a GCaMP calcium indicator for neural activity imaging. _J. Neurosci._ **32**, 13819–13840 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XhsVyqsrvF)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23035093)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3482105)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Optimization%20of%20a%20GCaMP%20calcium%20indicator%20for%20neural%20activity%20imaging&journal=J.%20Neurosci.&volume=32&pages=13819-13840&publication_year=2012&author=Akerboom%2CJ) 
    
56.  Chen, T.W. et al. Ultrasensitive fluorescent proteins for imaging neuronal activity. _Nature_ **499**, 295–300 (2013).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3sXhtFalsrrI)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23868258)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3777791)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Ultrasensitive%20fluorescent%20proteins%20for%20imaging%20neuronal%20activity&journal=Nature&volume=499&pages=295-300&publication_year=2013&author=Chen%2CTW) 
    
57.  Kanodia, J.S. et al. A computational statistics approach for estimating the spatial range of morphogen gradients. _Development_ **138**, 4867–4874 (2011).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3MXhs12nt7bJ)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=22007136)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3201657)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=A%20computational%20statistics%20approach%20for%20estimating%20the%20spatial%20range%20of%20morphogen%20gradients&journal=Development&volume=138&pages=4867-4874&publication_year=2011&author=Kanodia%2CJS) 
    
58.  Pitrone, P.G. et al. OpenSPIM: an open-access light-sheet microscopy platform. _Nat. Methods_ **10**, 598–599 (2013).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3sXptVahs7k%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23749304)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC7450513)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=OpenSPIM%3A%20an%20open-access%20light-sheet%20microscopy%20platform&journal=Nat.%20Methods&volume=10&pages=598-599&publication_year=2013&author=Pitrone%2CPG) 
    
59.  Gualda, E.J. et al. OpenSpinMicroscopy: an open-source integrated microscopy platform. _Nat. Methods_ **10**, 599–600 (2013).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3sXptValsLs%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=23749300)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=OpenSpinMicroscopy%3A%20an%20open-source%20integrated%20microscopy%20platform&journal=Nat.%20Methods&volume=10&pages=599-600&publication_year=2013&author=Gualda%2CEJ) 
    
60.  Bock, D.D. et al. Network anatomy and _in vivo_ physiology of visual cortical neurons. _Nature_ **471**, 177–182 (2011).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC3MXivFyru7Y%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=21390124)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3095821)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Network%20anatomy%20and%20in%20vivo%20physiology%20of%20visual%20cortical%20neurons&journal=Nature&volume=471&pages=177-182&publication_year=2011&author=Bock%2CDD) 
    
61.  Tomer, R., Ye, L., Hsueh, B. & Deisseroth, K. Advanced CLARITY for rapid and high-resolution imaging of intact tissues. _Nat. Protoc._ **9**, 1682–1697 (2014).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC2cXhtVWqsr%2FP)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=24945384)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4096681)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Advanced%20CLARITY%20for%20rapid%20and%20high-resolution%20imaging%20of%20intact%20tissues&journal=Nat.%20Protoc.&volume=9&pages=1682-1697&publication_year=2014&author=Tomer%2CR&author=Ye%2CL&author=Hsueh%2CB&author=Deisseroth%2CK) 
    
62.  Susaki, E.A. et al. Whole-brain imaging with single-cell resolution using chemical cocktails and computational analysis. _Cell_ **157**, 726–739 (2014).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC2cXmsVClsrY%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=24746791)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Whole-brain%20imaging%20with%20single-cell%20resolution%20using%20chemical%20cocktails%20and%20computational%20analysis&journal=Cell&volume=157&pages=726-739&publication_year=2014&author=Susaki%2CEA) 
    
63.  Dodt, H.U. et al. Ultramicroscopy: three-dimensional visualization of neuronal networks in the whole mouse brain. _Nat. Methods_ **4**, 331–336 (2007).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BD2sXkt1eqs7k%3D)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=17384643)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Ultramicroscopy%3A%20three-dimensional%20visualization%20of%20neuronal%20networks%20in%20the%20whole%20mouse%20brain&journal=Nat.%20Methods&volume=4&pages=331-336&publication_year=2007&author=Dodt%2CHU) 
    
64.  Schindelin, J. et al. Fiji: an open-source platform for biological-image analysis. _Nat. Methods_ **9**, 676–682 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XhtVKnurbJ)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=22743772)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=Fiji%3A%20an%20open-source%20platform%20for%20biological-image%20analysis&journal=Nat.%20Methods&volume=9&pages=676-682&publication_year=2012&author=Schindelin%2CJ) 
    
65.  Schneider, C.A., Rasband, W.S. & Eliceiri, K.W. NIH image to ImageJ: 25 years of image analysis. _Nat. Methods_ **9**, 671–675 (2012).
    
    [CAS](https://www.nature.com/articles/cas-redirect/1:CAS:528:DC%2BC38XhtVKntb7P)  [PubMed](http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&dopt=Abstract&list_uids=22930834)  [PubMed Central](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC5554542)  [Google Scholar](http://scholar.google.com/scholar_lookup?&title=NIH%20image%20to%20ImageJ%3A%2025%20years%20of%20image%20analysis&journal=Nat.%20Methods&volume=9&pages=671-675&publication_year=2012&author=Schneider%2CCA&author=Rasband%2CWS&author=Eliceiri%2CKW) 
    

[Download references](https://citation-needed.springer.com/v2/references/10.1038/nprot.2015.111?format=refman&flavour=references)

Acknowledgements
----------------

We thank A. Cardona and the participants of the Janelia CATMAID hackathon for help with modifying the open-source code of CATMAID; K. Khairy for his contributions to exploring approaches to multiview image fusion and SiMView data management; and K. Branson and A. Cardona for helpful comments on the manuscript. This work was supported by the Howard Hughes Medical Institute.

Author information
------------------

### Authors and Affiliations

1.  Howard Hughes Medical Institute, Janelia Research Campus, Ashburn, Virginia, USA
    
    Fernando Amat, Burkhard Höckendorf, Yinan Wan, William C Lemon, Katie McDole & Philipp J Keller
    

Authors

1.  Fernando Amat
2.  Burkhard Höckendorf
3.  Yinan Wan
4.  William C Lemon
5.  Katie McDole
6.  Philipp J Keller

### Contributions

F.A. and B.H. developed the KLB file format and related software infrastructure. P.J.K. developed the multiview registration and fusion software, with contributions from F.A. F.A. developed the TGMM framework and related software infrastructure. Y.W., W.C.L. and K.M. performed light-sheet microscopy experiments and contributed image data sets. F.A. and P.J.K. wrote the manuscript, with input from all authors.

### Corresponding authors

Correspondence to [Fernando Amat](mailto:amatf@janelia.hhmi.org) or [Philipp J Keller](mailto:kellerp@janelia.hhmi.org).

Ethics declarations
-------------------

### Competing interests

The authors declare no competing financial interests.

Integrated supplementary information
------------------------------------

### [Supplementary Figure 1 Local performance of lossless compression image file formats](https://www.nature.com/articles/nprot.2015.111/figures/8)

Performance of the KLB lossless compression format vs. LZW-TIFF (green) and JPEG 2000 (blue) lossless compression formats with respect to write speed (first column) and read speed (second column). The JPEG 2000 benchmark utilizes the multi-threaded commercial library PICTools Medical SDK (Accusoft). A performance comparison of KLB and uncompressed TIFF formats is included as well (orange). LZW-TIFF and uncompressed TIFF benchmarks utilize the _imread_ and _imwrite_ functions provided by the Image Processing Toolbox in Matlab. All performance data are provided as ratios with KLB performance in the numerator, i.e. ratios larger than one (grey lines) indicate superior performance of the KLB format. The comparison was performed using a variety of fluorescence microscopy image data sets stored locally on a high-performance RAID array built from solid-state drives (SSDs) and thus complements the network-based analysis shown in [Fig. 3](https://www.nature.com/articles/nprot.2015.111#Fig3) (note that performance with respect to compression ratios is identical to the data shown in [Fig. 3](https://www.nature.com/articles/nprot.2015.111#Fig3)). Benchmark data sets include SiMView light-sheet microscopy recordings of fruit fly, mouse and zebrafish embryonic development (data sets 1-8), confocal microscopy data of a zebrafish embryo (data set 9) and SiMView functional image data of brain activity in a larval zebrafish (data set 10). Developmental data sets (data sets 1-8) were analyzed as raw and masked versions in order to illustrate the importance of background masking for maximizing data storage and access efficiency. Please see Steps I-III in [Fig. 2](https://www.nature.com/articles/nprot.2015.111#Fig2) for a description of the concepts underlying background masking.

### [Supplementary Figure 2 Block-size dependency of KLB file size and read/write speeds](https://www.nature.com/articles/nprot.2015.111/figures/9)

Performance comparison for KLB versus JPEG 2000 (JP2) with respect to file size (a), write time (b) and read time (c), as a function of KLB block size (in pixels). The results represent average performance across five data sets, including developmental image data from a fruit fly embryo, a zebrafish embryo and early-/late-stage mouse embryos as well as functional image data from a zebrafish larva. The larger the block size, the better the KLB compression ratio; however, this ratio reaches saturation already for relatively small block sizes. Read and write times are not optimal for extreme block sizes, i.e. both for very small and for very large blocks. If blocks are too small, communication overhead in processing threads becomes an issue. If blocks are too large, computations cannot be parallelized to the maximum extent (in the most extreme scenario, a single thread has to handle the entire image). The figure shows a diagonal band, where all three metrics are optimal or near optimal at the same time. Based on these benchmarks, we chose the default block size as 96 x 96 x 8 pixels. The JPEG 2000 benchmark utilizes the multi-threaded commercial library PICTools Medical SDK (Accusoft). Lateral size refers to the X and Y axes of the image volume. Axial size refers to the Z axis of the image volume, which is typically smaller than the lateral size in light microscopy due to anisotropic spatial resolution in the microscope and anisotropic spatial sampling of the specimen volume.

### [Supplementary Figure 3 KLB performance comparison for local vs. network data storage](https://www.nature.com/articles/nprot.2015.111/figures/10)

Comparison of KLB read and write speeds on a local data drive versus a data drive mounted over the network (using a 10 Gb/s glass fiber connection). Speeds are comparable since most of the time is spent on data compression and decompression, respectively, and physical disk access introduces relatively little overhead. Moreover, most modern operating systems and RAID hardware improve I/O performance by caching and by using dedicated processors that avoid load on primary CPUs. Thus, while some blocks are compressed or decompressed others are written or read, respectively, masking I/O costs. All data points are averages based on _n_ = 5 iterations of the benchmark.

Supplementary information
-------------------------

### [Supplementary Text and Figures](https://static-content.springer.com/esm/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_MOESM268_ESM.pdf)

Supplementary Figures 1–3, Supplementary Note 1, Supplementary Table 1 (PDF 1261 kb)

### [Supplementary Software 1](https://static-content.springer.com/esm/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_MOESM269_ESM.zip)

KLB lossless compression file format. This software package contains the C++11 source code for the KLB file format implementation as well as wrappers for Matlab and Java. The folder _bin_ contains the precompiled static and shared (DLL) libraries for Windows 7 64-bit as well as a simple executable _test\_KLBIO.exe_ for testing read/write operations. The source code of this executable represents a good example of how to use the API for the KLB file format. For Windows 7 64-bit, we also provide precompiled MEX files in the folder _matlabWrapper_. Linux and Mac OS users need to compile both the source code and the Matlab wrappers to obtain libraries and executables. For the first part, a CMake file is available in the folder _src_. For the second part, the folder _matlabWrapper_ contains the script _compileMex.m_ for generating MEX files. The C++ libraries need to be compiled in release mode before compiling the MEX files. In order to keep track of possible software updates, the user can also clone all files from the primary public software repository using the following git command: _git clone_ https://fernandoamat@bitbucket.org/fernandoamat/keller-lab-block-filetype.git (ZIP 4460 kb)

### [Supplementary Software 2](https://static-content.springer.com/esm/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_MOESM270_ESM.zip)

KLB Java Native Interface library and SCIFIO implementation. This software package exposes the C++ API on the Java side and includes a functional implementation of a SCIFIO format that provides KLB support to image processing frameworks such as ImageJ and Knime. Precompiled native libraries for Windows and Linux (64-bit) are bundled inside the JAR file included in this software package. For convenience, ImageJ users can follow the update site at [http://sites.imagej.net/SiMView](http://sites.imagej.net/SiMView) (for instructions, see [http://wiki.imagej.net/How\_to\_follow\_a\_3rd\_party\_update\_site](http://wiki.imagej.net/How_to_follow_a_3rd_party_update_site)). (ZIP 1099 kb)

### [Supplementary Software 3](https://static-content.springer.com/esm/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_MOESM271_ESM.zip)

Image processing pipeline for light-sheet microscopy. This software package contains our Matlab code for image processing of light-sheet microscopy data sets, including (1) sCMOS image correction, background masking and KLB lossless image compression (using script _clusterPT.m_), (2) content-based multi-view image registration and fusion (using scripts _clusterMF.m_, localAP.m and _clusterTF.m_), (3) spatial drift correction and intensity normalization (using scripts _localEC.m_ and _clusterCS.m_) and (4) adaptive local background correction (using script _clusterFR.m_). Please see the README file for detailed information about these software modules. (ZIP 1003 kb)

### [Supplementary Software 4](https://static-content.springer.com/esm/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_MOESM272_ESM.zip)

TGMM software for segmentation and cell tracking. This software package contains the C++ and CUDA source code for the Tracking with Gaussian Mixture Models (TGMM) software for automated segmentation and cell tracking in light microscopy time-lapse data sets. The software package includes the following folders: _src_: contains all source code files. This folder also includes the file _CMakeList.txt_ that can be used to compile the source code. _doc_: contains the documentation of the TGMM software. _bin_: contains Windows 7 64bit executables for running the TGMM software. When compiling the source code, the executables for the release version will be placed here. This folder also contains all necessary DLLs (CUDA and MSVC runtime) as well as the text files containing machine learning classifiers for cell division detection. Please see the README file for detailed information on how to run and compile the TGMM software. In order to keep track of possible software updates, the user can also clone all files from the primary public software repository using the following git command: _git clone_ git://git.code.sf.net/p/tgmm/code tgmm-code (ZIP 72857 kb)

### [Supplementary Software 5](https://static-content.springer.com/esm/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_MOESM273_ESM.zip)

CATMAID branch for 5D image visualization and lineage editing. This software package contains our branch of the open source software CATMAID. The software can also be cloned using the following git command: _git clone -b 5Dvisualization --single-branch_ https://fernandoamat@bitbucket.org/fernandoamat/catmaid\_5d\_visualization\_annotation.git The PDF file UserGuide.pdf in the root folder of this software package and the website [http://catmaid.org/](http://catmaid.org/) provide detailed instructions for setting up a CATMAID server. (ZIP 19979 kb)

### [Supplementary Software 6](https://static-content.springer.com/esm/art%3A10.1038%2Fnprot.2015.111/MediaObjects/41596_2015_BFnprot2015111_MOESM274_ESM.zip)

Matlab import/export scripts for TGMM, CATMAID and Imaris. This software package contains Matlab code for transferring results between TGMM, CATMAID and Imaris. In order to optimize read speed, the code for reading XML files generated by TGMM needs to be compiled into MEX files. The folder _readTGMM\_XMLoutput contains the script compileMex.m_ for this purpose. The README file contains further details on this topic and a description of the main Matlab functions included in this software package. Briefly, these Matlab functions facilitate: (1) import of TGMM tracking and segmentation results into Matlab, (2) export of image data and tracking results from Matlab to CATMAID, (3) import of cell lineage information from CATMAID into Matlab, (4) export of cell lineage information from Matlab to Imaris. (ZIP 3470 kb)

Rights and permissions
----------------------

About this article
------------------

[![Check for updates. Verify currency and authenticity via CrossMark](data:image/svg+xml;base64,PHN2ZyBoZWlnaHQ9IjgxIiB3aWR0aD0iNTciIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGcgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIj48cGF0aCBkPSJtMTcuMzUgMzUuNDUgMjEuMy0xNC4ydi0xNy4wM2gtMjEuMyIgZmlsbD0iIzk4OTg5OCIvPjxwYXRoIGQ9Im0zOC42NSAzNS40NS0yMS4zLTE0LjJ2LTE3LjAzaDIxLjMiIGZpbGw9IiM3NDc0NzQiLz48cGF0aCBkPSJtMjggLjVjLTEyLjk4IDAtMjMuNSAxMC41Mi0yMy41IDIzLjVzMTAuNTIgMjMuNSAyMy41IDIzLjUgMjMuNS0xMC41MiAyMy41LTIzLjVjMC02LjIzLTIuNDgtMTIuMjEtNi44OC0xNi42Mi00LjQxLTQuNC0xMC4zOS02Ljg4LTE2LjYyLTYuODh6bTAgNDEuMjVjLTkuOCAwLTE3Ljc1LTcuOTUtMTcuNzUtMTcuNzVzNy45NS0xNy43NSAxNy43NS0xNy43NSAxNy43NSA3Ljk1IDE3Ljc1IDE3Ljc1YzAgNC43MS0xLjg3IDkuMjItNS4yIDEyLjU1cy03Ljg0IDUuMi0xMi41NSA1LjJ6IiBmaWxsPSIjNTM1MzUzIi8+PHBhdGggZD0ibTQxIDM2Yy01LjgxIDYuMjMtMTUuMjMgNy40NS0yMi40MyAyLjktNy4yMS00LjU1LTEwLjE2LTEzLjU3LTcuMDMtMjEuNWwtNC45Mi0zLjExYy00Ljk1IDEwLjctMS4xOSAyMy40MiA4Ljc4IDI5LjcxIDkuOTcgNi4zIDIzLjA3IDQuMjIgMzAuNi00Ljg2eiIgZmlsbD0iIzljOWM5YyIvPjxwYXRoIGQ9Im0uMiA1OC40NWMwLS43NS4xMS0xLjQyLjMzLTIuMDFzLjUyLTEuMDkuOTEtMS41Yy4zOC0uNDEuODMtLjczIDEuMzQtLjk0LjUxLS4yMiAxLjA2LS4zMiAxLjY1LS4zMi41NiAwIDEuMDYuMTEgMS41MS4zNS40NC4yMy44MS41IDEuMS44MWwtLjkxIDEuMDFjLS4yNC0uMjQtLjQ5LS40Mi0uNzUtLjU2LS4yNy0uMTMtLjU4LS4yLS45My0uMi0uMzkgMC0uNzMuMDgtMS4wNS4yMy0uMzEuMTYtLjU4LjM3LS44MS42Ni0uMjMuMjgtLjQxLjYzLS41MyAxLjA0LS4xMy40MS0uMTkuODgtLjE5IDEuMzkgMCAxLjA0LjIzIDEuODYuNjggMi40Ni40NS41OSAxLjA2Ljg4IDEuODQuODguNDEgMCAuNzctLjA3IDEuMDctLjIzcy41OS0uMzkuODUtLjY4bC45MSAxYy0uMzguNDMtLjguNzYtMS4yOC45OS0uNDcuMjItMSAuMzQtMS41OC4zNC0uNTkgMC0xLjEzLS4xLTEuNjQtLjMxLS41LS4yLS45NC0uNTEtMS4zMS0uOTEtLjM4LS40LS42Ny0uOS0uODgtMS40OC0uMjItLjU5LS4zMy0xLjI2LS4zMy0yLjAyem04LjQtNS4zM2gxLjYxdjIuNTRsLS4wNSAxLjMzYy4yOS0uMjcuNjEtLjUxLjk2LS43MnMuNzYtLjMxIDEuMjQtLjMxYy43MyAwIDEuMjcuMjMgMS42MS43MS4zMy40Ny41IDEuMTQuNSAyLjAydjQuMzFoLTEuNjF2LTQuMWMwLS41Ny0uMDgtLjk3LS4yNS0xLjIxLS4xNy0uMjMtLjQ1LS4zNS0uODMtLjM1LS4zIDAtLjU2LjA4LS43OS4yMi0uMjMuMTUtLjQ5LjM2LS43OC42NHY0LjhoLTEuNjF6bTcuMzcgNi40NWMwLS41Ni4wOS0xLjA2LjI2LTEuNTEuMTgtLjQ1LjQyLS44My43MS0xLjE0LjI5LS4zLjYzLS41NCAxLjAxLS43MS4zOS0uMTcuNzgtLjI1IDEuMTgtLjI1LjQ3IDAgLjg4LjA4IDEuMjMuMjQuMzYuMTYuNjUuMzguODkuNjdzLjQyLjYzLjU0IDEuMDNjLjEyLjQxLjE4Ljg0LjE4IDEuMzIgMCAuMzItLjAyLjU3LS4wNy43NmgtNC4zNmMuMDcuNjIuMjkgMS4xLjY1IDEuNDQuMzYuMzMuODIuNSAxLjM4LjUuMjkgMCAuNTctLjA0LjgzLS4xM3MuNTEtLjIxLjc2LS4zN2wuNTUgMS4wMWMtLjMzLjIxLS42OS4zOS0xLjA5LjUzLS40MS4xNC0uODMuMjEtMS4yNi4yMS0uNDggMC0uOTItLjA4LTEuMzQtLjI1LS40MS0uMTYtLjc2LS40LTEuMDctLjctLjMxLS4zMS0uNTUtLjY5LS43Mi0xLjEzLS4xOC0uNDQtLjI2LS45NS0uMjYtMS41MnptNC42LS42MmMwLS41NS0uMTEtLjk4LS4zNC0xLjI4LS4yMy0uMzEtLjU4LS40Ny0xLjA2LS40Ny0uNDEgMC0uNzcuMTUtMS4wNy40NS0uMzEuMjktLjUuNzMtLjU4IDEuM3ptMi41LjYyYzAtLjU3LjA5LTEuMDguMjgtMS41My4xOC0uNDQuNDMtLjgyLjc1LTEuMTNzLjY5LS41NCAxLjEtLjcxYy40Mi0uMTYuODUtLjI0IDEuMzEtLjI0LjQ1IDAgLjg0LjA4IDEuMTcuMjNzLjYxLjM0Ljg1LjU3bC0uNzcgMS4wMmMtLjE5LS4xNi0uMzgtLjI4LS41Ni0uMzctLjE5LS4wOS0uMzktLjE0LS42MS0uMTQtLjU2IDAtMS4wMS4yMS0xLjM1LjYzLS4zNS40MS0uNTIuOTctLjUyIDEuNjcgMCAuNjkuMTcgMS4yNC41MSAxLjY2LjM0LjQxLjc4LjYyIDEuMzIuNjIuMjggMCAuNTQtLjA2Ljc4LS4xNy4yNC0uMTIuNDUtLjI2LjY0LS40MmwuNjcgMS4wM2MtLjMzLjI5LS42OS41MS0xLjA4LjY1LS4zOS4xNS0uNzguMjMtMS4xOC4yMy0uNDYgMC0uOS0uMDgtMS4zMS0uMjQtLjQtLjE2LS43NS0uMzktMS4wNS0uN3MtLjUzLS42OS0uNy0xLjEzYy0uMTctLjQ1LS4yNS0uOTYtLjI1LTEuNTN6bTYuOTEtNi40NWgxLjU4djYuMTdoLjA1bDIuNTQtMy4xNmgxLjc3bC0yLjM1IDIuOCAyLjU5IDQuMDdoLTEuNzVsLTEuNzctMi45OC0xLjA4IDEuMjN2MS43NWgtMS41OHptMTMuNjkgMS4yN2MtLjI1LS4xMS0uNS0uMTctLjc1LS4xNy0uNTggMC0uODcuMzktLjg3IDEuMTZ2Ljc1aDEuMzR2MS4yN2gtMS4zNHY1LjZoLTEuNjF2LTUuNmgtLjkydi0xLjJsLjkyLS4wN3YtLjcyYzAtLjM1LjA0LS42OC4xMy0uOTguMDgtLjMxLjIxLS41Ny40LS43OXMuNDItLjM5LjcxLS41MWMuMjgtLjEyLjYzLS4xOCAxLjA0LS4xOC4yNCAwIC40OC4wMi42OS4wNy4yMi4wNS40MS4xLjU3LjE3em0uNDggNS4xOGMwLS41Ny4wOS0xLjA4LjI3LTEuNTMuMTctLjQ0LjQxLS44Mi43Mi0xLjEzLjMtLjMxLjY1LS41NCAxLjA0LS43MS4zOS0uMTYuOC0uMjQgMS4yMy0uMjRzLjg0LjA4IDEuMjQuMjRjLjQuMTcuNzQuNCAxLjA0Ljcxcy41NC42OS43MiAxLjEzYy4xOS40NS4yOC45Ni4yOCAxLjUzcy0uMDkgMS4wOC0uMjggMS41M2MtLjE4LjQ0LS40Mi44Mi0uNzIgMS4xM3MtLjY0LjU0LTEuMDQuNy0uODEuMjQtMS4yNC4yNC0uODQtLjA4LTEuMjMtLjI0LS43NC0uMzktMS4wNC0uN2MtLjMxLS4zMS0uNTUtLjY5LS43Mi0xLjEzLS4xOC0uNDUtLjI3LS45Ni0uMjctMS41M3ptMS42NSAwYzAgLjY5LjE0IDEuMjQuNDMgMS42Ni4yOC40MS42OC42MiAxLjE4LjYyLjUxIDAgLjktLjIxIDEuMTktLjYyLjI5LS40Mi40NC0uOTcuNDQtMS42NiAwLS43LS4xNS0xLjI2LS40NC0xLjY3LS4yOS0uNDItLjY4LS42My0xLjE5LS42My0uNSAwLS45LjIxLTEuMTguNjMtLjI5LjQxLS40My45Ny0uNDMgMS42N3ptNi40OC0zLjQ0aDEuMzNsLjEyIDEuMjFoLjA1Yy4yNC0uNDQuNTQtLjc5Ljg4LTEuMDIuMzUtLjI0LjctLjM2IDEuMDctLjM2LjMyIDAgLjU5LjA1Ljc4LjE0bC0uMjggMS40LS4zMy0uMDljLS4xMS0uMDEtLjIzLS4wMi0uMzgtLjAyLS4yNyAwLS41Ni4xLS44Ni4zMXMtLjU1LjU4LS43NyAxLjF2NC4yaC0xLjYxem0tNDcuODcgMTVoMS42MXY0LjFjMCAuNTcuMDguOTcuMjUgMS4yLjE3LjI0LjQ0LjM1LjgxLjM1LjMgMCAuNTctLjA3LjgtLjIyLjIyLS4xNS40Ny0uMzkuNzMtLjczdi00LjdoMS42MXY2Ljg3aC0xLjMybC0uMTItMS4wMWgtLjA0Yy0uMy4zNi0uNjMuNjQtLjk4Ljg2LS4zNS4yMS0uNzYuMzItMS4yNC4zMi0uNzMgMC0xLjI3LS4yNC0xLjYxLS43MS0uMzMtLjQ3LS41LTEuMTQtLjUtMi4wMnptOS40NiA3LjQzdjIuMTZoLTEuNjF2LTkuNTloMS4zM2wuMTIuNzJoLjA1Yy4yOS0uMjQuNjEtLjQ1Ljk3LS42My4zNS0uMTcuNzItLjI2IDEuMS0uMjYuNDMgMCAuODEuMDggMS4xNS4yNC4zMy4xNy42MS40Ljg0LjcxLjI0LjMxLjQxLjY4LjUzIDEuMTEuMTMuNDIuMTkuOTEuMTkgMS40NCAwIC41OS0uMDkgMS4xMS0uMjUgMS41Ny0uMTYuNDctLjM4Ljg1LS42NSAxLjE2LS4yNy4zMi0uNTguNTYtLjk0LjczLS4zNS4xNi0uNzIuMjUtMS4xLjI1LS4zIDAtLjYtLjA3LS45LS4ycy0uNTktLjMxLS44Ny0uNTZ6bTAtMi4zYy4yNi4yMi41LjM3LjczLjQ1LjI0LjA5LjQ2LjEzLjY2LjEzLjQ2IDAgLjg0LS4yIDEuMTUtLjYuMzEtLjM5LjQ2LS45OC40Ni0xLjc3IDAtLjY5LS4xMi0xLjIyLS4zNS0xLjYxLS4yMy0uMzgtLjYxLS41Ny0xLjEzLS41Ny0uNDkgMC0uOTkuMjYtMS41Mi43N3ptNS44Ny0xLjY5YzAtLjU2LjA4LTEuMDYuMjUtMS41MS4xNi0uNDUuMzctLjgzLjY1LTEuMTQuMjctLjMuNTgtLjU0LjkzLS43MXMuNzEtLjI1IDEuMDgtLjI1Yy4zOSAwIC43My4wNyAxIC4yLjI3LjE0LjU0LjMyLjgxLjU1bC0uMDYtMS4xdi0yLjQ5aDEuNjF2OS44OGgtMS4zM2wtLjExLS43NGgtLjA2Yy0uMjUuMjUtLjU0LjQ2LS44OC42NC0uMzMuMTgtLjY5LjI3LTEuMDYuMjctLjg3IDAtMS41Ni0uMzItMi4wNy0uOTVzLS43Ni0xLjUxLS43Ni0yLjY1em0xLjY3LS4wMWMwIC43NC4xMyAxLjMxLjQgMS43LjI2LjM4LjY1LjU4IDEuMTUuNTguNTEgMCAuOTktLjI2IDEuNDQtLjc3di0zLjIxYy0uMjQtLjIxLS40OC0uMzYtLjctLjQ1LS4yMy0uMDgtLjQ2LS4xMi0uNy0uMTItLjQ1IDAtLjgyLjE5LTEuMTMuNTktLjMxLjM5LS40Ni45NS0uNDYgMS42OHptNi4zNSAxLjU5YzAtLjczLjMyLTEuMy45Ny0xLjcxLjY0LS40IDEuNjctLjY4IDMuMDgtLjg0IDAtLjE3LS4wMi0uMzQtLjA3LS41MS0uMDUtLjE2LS4xMi0uMy0uMjItLjQzcy0uMjItLjIyLS4zOC0uM2MtLjE1LS4wNi0uMzQtLjEtLjU4LS4xLS4zNCAwLS42OC4wNy0xIC4ycy0uNjMuMjktLjkzLjQ3bC0uNTktMS4wOGMuMzktLjI0LjgxLS40NSAxLjI4LS42My40Ny0uMTcuOTktLjI2IDEuNTQtLjI2Ljg2IDAgMS41MS4yNSAxLjkzLjc2cy42MyAxLjI1LjYzIDIuMjF2NC4wN2gtMS4zMmwtLjEyLS43NmgtLjA1Yy0uMy4yNy0uNjMuNDgtLjk4LjY2cy0uNzMuMjctMS4xNC4yN2MtLjYxIDAtMS4xLS4xOS0xLjQ4LS41Ni0uMzgtLjM2LS41Ny0uODUtLjU3LTEuNDZ6bTEuNTctLjEyYzAgLjMuMDkuNTMuMjcuNjcuMTkuMTQuNDIuMjEuNzEuMjEuMjggMCAuNTQtLjA3Ljc3LS4ycy40OC0uMzEuNzMtLjU2di0xLjU0Yy0uNDcuMDYtLjg2LjEzLTEuMTguMjMtLjMxLjA5LS41Ny4xOS0uNzYuMzFzLS4zMy4yNS0uNDEuNGMtLjA5LjE1LS4xMy4zMS0uMTMuNDh6bTYuMjktMy42M2gtLjk4di0xLjJsMS4wNi0uMDcuMi0xLjg4aDEuMzR2MS44OGgxLjc1djEuMjdoLTEuNzV2My4yOGMwIC44LjMyIDEuMi45NyAxLjIuMTIgMCAuMjQtLjAxLjM3LS4wNC4xMi0uMDMuMjQtLjA3LjM0LS4xMWwuMjggMS4xOWMtLjE5LjA2LS40LjEyLS42NC4xNy0uMjMuMDUtLjQ5LjA4LS43Ni4wOC0uNCAwLS43NC0uMDYtMS4wMi0uMTgtLjI3LS4xMy0uNDktLjMtLjY3LS41Mi0uMTctLjIxLS4zLS40OC0uMzctLjc4LS4wOC0uMy0uMTItLjY0LS4xMi0xLjAxem00LjM2IDIuMTdjMC0uNTYuMDktMS4wNi4yNy0xLjUxcy40MS0uODMuNzEtMS4xNGMuMjktLjMuNjMtLjU0IDEuMDEtLjcxLjM5LS4xNy43OC0uMjUgMS4xOC0uMjUuNDcgMCAuODguMDggMS4yMy4yNC4zNi4xNi42NS4zOC44OS42N3MuNDIuNjMuNTQgMS4wM2MuMTIuNDEuMTguODQuMTggMS4zMiAwIC4zMi0uMDIuNTctLjA3Ljc2aC00LjM3Yy4wOC42Mi4yOSAxLjEuNjUgMS40NC4zNi4zMy44Mi41IDEuMzguNS4zIDAgLjU4LS4wNC44NC0uMTMuMjUtLjA5LjUxLS4yMS43Ni0uMzdsLjU0IDEuMDFjLS4zMi4yMS0uNjkuMzktMS4wOS41M3MtLjgyLjIxLTEuMjYuMjFjLS40NyAwLS45Mi0uMDgtMS4zMy0uMjUtLjQxLS4xNi0uNzctLjQtMS4wOC0uNy0uMy0uMzEtLjU0LS42OS0uNzItMS4xMy0uMTctLjQ0LS4yNi0uOTUtLjI2LTEuNTJ6bTQuNjEtLjYyYzAtLjU1LS4xMS0uOTgtLjM0LTEuMjgtLjIzLS4zMS0uNTgtLjQ3LTEuMDYtLjQ3LS40MSAwLS43Ny4xNS0xLjA4LjQ1LS4zMS4yOS0uNS43My0uNTcgMS4zem0zLjAxIDIuMjNjLjMxLjI0LjYxLjQzLjkyLjU3LjMuMTMuNjMuMi45OC4yLjM4IDAgLjY1LS4wOC44My0uMjNzLjI3LS4zNS4yNy0uNmMwLS4xNC0uMDUtLjI2LS4xMy0uMzctLjA4LS4xLS4yLS4yLS4zNC0uMjgtLjE0LS4wOS0uMjktLjE2LS40Ny0uMjNsLS41My0uMjJjLS4yMy0uMDktLjQ2LS4xOC0uNjktLjMtLjIzLS4xMS0uNDQtLjI0LS42Mi0uNHMtLjMzLS4zNS0uNDUtLjU1Yy0uMTItLjIxLS4xOC0uNDYtLjE4LS43NSAwLS42MS4yMy0xLjEuNjgtMS40OS40NC0uMzggMS4wNi0uNTcgMS44My0uNTcuNDggMCAuOTEuMDggMS4yOS4yNXMuNzEuMzYuOTkuNTdsLS43NC45OGMtLjI0LS4xNy0uNDktLjMyLS43My0uNDItLjI1LS4xMS0uNTEtLjE2LS43OC0uMTYtLjM1IDAtLjYuMDctLjc2LjIxLS4xNy4xNS0uMjUuMzMtLjI1LjU0IDAgLjE0LjA0LjI2LjEyLjM2cy4xOC4xOC4zMS4yNmMuMTQuMDcuMjkuMTQuNDYuMjFsLjU0LjE5Yy4yMy4wOS40Ny4xOC43LjI5cy40NC4yNC42NC40Yy4xOS4xNi4zNC4zNS40Ni41OC4xMS4yMy4xNy41LjE3LjgyIDAgLjMtLjA2LjU4LS4xNy44My0uMTIuMjYtLjI5LjQ4LS41MS42OC0uMjMuMTktLjUxLjM0LS44NC40NS0uMzQuMTEtLjcyLjE3LTEuMTUuMTctLjQ4IDAtLjk1LS4wOS0xLjQxLS4yNy0uNDYtLjE5LS44Ni0uNDEtMS4yLS42OHoiIGZpbGw9IiM1MzUzNTMiLz48L2c+PC9zdmc+)](https://crossmark.crossref.org/dialog/?doi=10.1038/nprot.2015.111)

### Cite this article

Amat, F., Höckendorf, B., Wan, Y. _et al._ Efficient processing and analysis of large-scale light-sheet microscopy data. _Nat Protoc_ **10**, 1679–1696 (2015). https://doi.org/10.1038/nprot.2015.111

[Download citation](https://citation-needed.springer.com/v2/references/10.1038/nprot.2015.111?format=refman&flavour=citation)

-   Published: 01 October 2015
    
-   Issue Date: November 2015
    
-   DOI: https://doi.org/10.1038/nprot.2015.111
    

### Subjects
