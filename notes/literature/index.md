---
title: Literature
category: index
tags: [literature, moc]
---

# Literature

Map of content for paper notes. Each paper folder holds the note (`<citekey>.md`), its `paper.pdf` when available, extracted `figures/`, and an archived `source.md` full-text. Link a paper from anywhere with `[[citekey]]`; regenerate figures with `uv run extract-figures notes/literature/<citekey>`.

## Light-sheet microscopy — IsoView / SiMView / Keller lab

| Paper | Note | Tool / impl notes |
|-------|------|-------------------|
| Tomer et al. 2012 — SiMView | [tomer_keller_2012](tomer_keller_2012/tomer_keller_2012.md) | _private:_ isoview, isoview_pipeline |
| Chhetri et al. 2015 — IsoView | [chhetri_keller_2015](chhetri_keller_2015/chhetri_keller_2015.md) | |
| Lemon et al. 2015 — whole-CNS Drosophila | [lemon_keller_2015](lemon_keller_2015/lemon_keller_2015.md) | |
| Amat et al. 2015 — large-scale LSM processing | [amat_keller_2015](amat_keller_2015/amat_keller_2015.md) | [bigstitcher](../software/bigstitcher.md) |
| Guo et al. 2020 — rapid deconvolution + fusion | [guo_shroff_2020](guo_shroff_2020/guo_shroff_2020.md) | _private:_ diSPIM_regDeconv |

## Calcium-imaging pipelines — two-photon

| Paper | Note | Usage / code notes |
|-------|------|--------------------|
| Pachitariu et al. 2017 — Suite2p | [suite2p_2017](suite2p_2017/suite2p_2017.md) | [suite2p](../software/suite2p.md), [suite3d](../software/suite3d.md) |
| Stringer & Pachitariu 2024 — Rastermap | [rastermap_2024](rastermap_2024/rastermap_2024.md) | [rastermap](../software/rastermap.md) |
| Stringer et al. 2021 — Cellpose | [cellpose_2021](cellpose_2021/cellpose_2021.md) | [cellpose](../software/cellpose.md), [cellpose_versions](../software/cellpose_versions.md) |

Tool-side map: [Calcium Imaging](../software/calcium_imaging.md). Tools whose papers aren't yet noted here (CaImAn, EXTRACT, Suite3D) are in `references.bib`.

## Dendrites / voltage imaging — CA1, plasticity

| Paper | Note | Notes |
|-------|------|-------|
| Gonzalez et al. 2024 (Nature) — BTSP synaptic basis | [gonzalez_nature_2024](gonzalez_nature_2024/gonzalez_nature_2024.md) | biology; companion ↓ |
| Gonzalez et al. 2026 (Neuron) — 3D-RTMC voltage+Ca²⁺ | [gonzalez_neuron_2026](gonzalez_neuron_2026/gonzalez_neuron_2026.md) | method; companion ↑ |

> Unpublished/in-press papers and grants (Noguchi in-press, NIH Voltage, Nusser ERC) stay in the private repo and are handled by a separate private-only process — not indexed here.
