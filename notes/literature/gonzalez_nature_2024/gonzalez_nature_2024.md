---
citekey: gonzalez_nature_2024
title: "Gonzalez et al. 2024 — Synaptic basis of feature selectivity in hippocampal neurons"
category: literature
cluster: dendrites-voltage
tags: [dendrites, BTSP, plasticity, CA1, place-cells]
tools: []
related: [gonzalez_neuron_2026]
pdf: paper.pdf
source: https://doi.org/10.1038/s41586-024-08325-9
created: 2026-07-13
---

# Synaptic basis of feature selectivity in hippocampal neurons

**Gonzalez et al., _Nature_ (2024)** · DOI: 10.1038/s41586-024-08325-9 · Polleux & Losonczy labs (Columbia)

PDF: [paper.pdf](paper.pdf) · Figures: [`figures/`](figures/)

## TL;DR

All-optical imaging in awake, navigating mice watches individual synapses on a single CA1 neuron change strength in real time as a place field is created. Directly measures the seconds-long, temporally asymmetric BTSP plasticity rule — and finds it operates only in **oblique** dendrites, not **basal**.

## Background / the question

- Place cells = textbook feature selectivity: a CA1 neuron fires only in one spot despite >30,000 excitatory inputs.
- Leading mechanism: **BTSP (Behavioral Timescale Synaptic Plasticity)** — a single dendritic **plateau potential** (Ca²⁺ burst spike) creates a place field in one trial, over **seconds** (~1000× longer than millisecond spike-timing plasticity).
- Gap: BTSP's rule was modeled/inferred but never directly seen at single synapses in a behaving animal.

## Method — all-optical single-cell toolkit

Single-cell electroporation labels one neuron; 2-photon imaging while a head-fixed mouse runs a 3 m VR track:

- **SF-iGluSnFr.A184S** (green) — glutamate sensor → input timing + spatial tuning
- **jRGECO1a** (red) — spine calcium → proxy for synaptic weight
- **bReaChes** opsin — induces a place field on command
- 3 phases: pre-induction (map tuning + baseline weight) → induction → post-induction (re-measure). ΔW = final − initial (positive = potentiation, negative = depression).
- Validation: simultaneous voltage (ASAP6.1) + calcium showed spine Ca²⁺ tracks spine voltage linearly → calcium is a valid weight proxy.
- Scale: 19 inductions, 12 cells / 8 mice (+ 11 control cells / 6 mice); 906 spines on 71 branches (40 basal, 31 oblique).

## Key findings

1. **Temporally asymmetric plasticity kernel** — inputs active ~1–2 s *before* induction are potentiated; inputs earlier than ~3–4 s before (or after) are depressed. Lopsided decay: backward τ ≈ 3.1 s vs forward τ ≈ 1.0 s. Absent in no-opsin controls → real plasticity, not a light artifact. First direct in-vivo measurement of the BTSP kernel.

2. **Narrow potentiation + broad depression (space)** — inputs tuned to the induction spot are strongly, locally potentiated (clustered within ~0–2 µm along the branch); inputs to all other locations are broadly depressed (spread across the whole segment). = receptive-field sharpening.

3. **Plasticity respects tuning** — the largest ΔW occurs at spatially tuned spines, not untuned ones.

4. **PF properties track potentiation** — place-field width & running velocity correlate strongly (R ≈ 0.63, 0.77) with the fraction/spread of potentiated inputs.

5. **Compartment specificity (basal vs oblique)** — the whole kernel is expressed *only* in **oblique** dendrites (stratum radiatum), absent in **basal** (stratum oriens). Oblique spines: fewer tuned inputs, higher baseline weights, larger + more bidirectional plasticity (more potentiation *and* depression). Matches in-vitro Jain et al., Nature 2024. → the dendritic compartment gates whether BTSP happens.

6. **Functional, not structural** — no detectable spine-head-size change → mechanism ≈ AMPAR trafficking, not structural growth (on this timescale).

## Why it matters

- Turns the modeled BTSP rule into a directly observed one at single-synapse resolution in vivo.
- Learning rule for receptive fields = local potentiation of on-target inputs + global depression of off-target inputs.
- Plasticity is **not uniform across a neuron** — dendrite type decides. Ties back to the arbor/branching goals: basal vs oblique compartments behave differently, so branch identity (not just branch count) matters.

## Caveats

- Spine calcium is an *indirect* readout of synaptic weight.
- Role of presynaptic plasticity / glutamate spillover unresolved.
- Molecular link from plateau → temporal kernel still unknown.

## Code & data availability

- **Data:** Dryad `10.5061/dryad.66t1g1k9r` — `data.zip` (666 KB) + README, **open** (no request). Processed **per-spine table** (~26 vars: weights, tuning, compartment, PF metrics), *not* raw movies.
- **Code:** Zenodo `10.5281/zenodo.13957548` — `code.zip` (141 KB), MIT. ⚠️ **Not runnable** — imports private Losonczy-lab frameworks (`analysis_AN`/`lab`/`lab3`, not on PyPI) + sibling scripts absent from the deposit; Py2 top-level + Py3 `glutamate/`. It's a "what we computed" reference. Full audit + reproducibility comparison in [[gonzalez_neuron_2026]].
- Stack: Python 2.7/3.7, SIMA (motion/ROIs), OASIS (deconvolution), Prism (stats). Male C57BL/6J, 3–4 mo.
- Local: PDF in `Flynn/`; deposit code in `~/repos/dend_utils/code/` (repo guide: `dend_utils/CLAUDE.md`).

## See also

- [[gonzalez_neuron_2026]] — the enabling voltage+calcium imaging method (3D-RTMC), and the voltage–calcium decoupling that underpins this paper's compartment-specific plasticity.
