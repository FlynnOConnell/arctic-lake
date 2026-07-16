---
citekey: gonzalez_neuron_2026
title: "Gonzalez et al. 2026 — Movement-stabilized 3D optical recordings of voltage + calcium in CA1 dendrites"
category: literature
cluster: dendrites-voltage
tags: [dendrites, voltage-imaging, methods, 3D-RTMC, backpropagation, CA1]
tools: [3D-RTMC]
related: [gonzalez_nature_2024, noguchi_inpress]
pdf: paper.pdf
source: https://doi.org/10.1016/j.neuron.2026.01.004
created: 2026-07-13
---

# Movement-stabilized 3D optical recordings of voltage + calcium in CA1 dendrites

**Gonzalez, Terada, Noguchi, … Polleux, Losonczy & Rózsa, _Neuron_ (2026)** · doi:10.1016/j.neuron.2026.01.004 · Corresp.: Losonczy & Rózsa

PDF: [paper.pdf](paper.pdf) · Figures: [`figures/`](figures/) · Enabling method / companion to [[gonzalez_nature_2024]]

## TL;DR

The enabling-technology companion to [[gonzalez_nature_2024]]. Same lead author and platform (dual-color **ASAP6.1 voltage + jRGECO1a calcium**, acousto-optical 2P, awake mice), but here the whole platform is built and stress-tested. Introduces **3D-RTMC** (FPGA real-time motion correction using a neighboring neuron's soma as fiducial), and shows that **dendritic branch order decouples voltage from calcium** — the biophysical backdrop for the compartment-specific plasticity in [[gonzalez_nature_2024]].

## How it fits with [[gonzalez_nature_2024]] (bridge)

Same lead author (K. Gonzalez), same senior labs (Polleux/Losonczy) + **Balázs Rózsa** (3D acousto-optical microscopy). The Nature paper *used* dual-color voltage+calcium imaging as a one-figure validation; this paper *builds and stress-tests the whole platform*.

| | [[gonzalez_nature_2024]] (biology) | this (method + biology) |
|---|---|---|
| Question | What plasticity rule builds a place field? | How do voltage & calcium propagate through the dendritic tree in vivo? |
| Platform | SCE; **ASAP6.1 (V) + jRGECO1a (Ca²⁺)**; Femto3D-ATLAS AO scope; awake mice | Same — full development of it |
| Key dependency | Assumes **spine calcium ∝ synaptic weight (voltage)** | **Directly measures** that V↔Ca²⁺ coupling; shows where it holds/breaks |
| Theme | Plasticity is **compartment-specific** (oblique ≠ basal) | Propagation & V–Ca²⁺ coupling are **compartment-specific** (apical ≠ basal, branch-order-dependent) |

**Bridge takeaway:** the Nature method rests on spine calcium standing in for synaptic strength; this paper *earns* that assumption but also *qualifies* it (coupling decays into distal/high-order branches), and gives a biophysical reason why plasticity differs between oblique and basal dendrites.

## The problem it solves

Imaging membrane **voltage** (dim GEVIs, needs kHz sampling → can't average motion away) at single-dendrite resolution in an awake mouse fights brain motion of **~5–10 µm / 500 ms across 0–60 Hz** — many × the ~1 µm dendrite width. Prior fix (injected fluorescent beads as fiducials) causes immune response, bad placement, PMT saturation, overheating.

## Core innovation — 3D-RTMC (3D real-time motion correction)

FPGA-based closed-loop motion correction on an acousto-optical 2P microscope:

- **Reference = a neighboring neuron's soma, not a bead** (nuclear H2B-tdTomato via 2nd electroporation, or sparse AAV-FlpO/Cre), <100 µm from the recorded cell.
- Loop: AO scanner interleaves 3 orthogonal "reference drifts" (x, y, z) through the reference soma; FPGA computes intensity-weighted **centroids** each cycle and shifts the recording origin in real time.
- **Loop <500 µs** (~330–390 µs example); compensates motion up to **~50 µm/ms** (>2× fastest reported brain speed).
- Two tricks for dim references: intensity **threshold** (skip correction under low SNR → no "jumping" to brighter neighbors) + **smoothed** drift profiles (less bleaching). Only **~10%** of imaging time on reference drifts holds residual motion **<1 µm**.
- Result: **>100× motion reduction**, residual **<1 pixel** (0.001–10 Hz); better spike SNR; removes false burst-like oscillation artifacts in thin dendrites. A single soma reference stabilizes dendrites **170–330 µm** away.

## Novel computations / analyses

1. **Centroid closed-loop + stability check** — correction matrix `C(x,y)=|x−μx(y)|+|y−μy(x)|` as a 3D surface; a valid reference has a **single global minimum**; its first derivative = long-term stability metric.
2. **Adaptive wavelet-threshold denoising** — Morlet transform → per-frequency normalize → PCA → Ward clustering (20 clusters) → drop noise clusters → frequency-specific thresholding → reconstruct. Preserves subthreshold + spikes.
3. **FNN + PCA decoding of somatic voltage from dendritic signals** — somatic voltage PCs (PC1 ≈ 45% var = amplitude/duration; PC2 = burstiness) predicted by a feedforward net. **Dendritic _voltage_ reconstructs somatic dynamics far better than dendritic _calcium_**; calcium accuracy collapses at high branch order.
4. **Event taxonomy (hierarchical clustering)** — well-coupled / amplitude-decoupled / strong-decoupled (Ca²⁺ > V).

## Biological findings

1. **Soma↔dendrite coupling (4 features):** (i) single bAPs attenuate with distance; (ii) successive spikes in a burst attenuate across the train; (iii) **bursts backpropagate more reliably than single spikes** (sustained depolarization envelope reaches farther — relevant to the BTSP plateau/instructive signal in [[gonzalez_nature_2024]]); (iv) dendrites fire **isolated local events independent of the soma**, with **no distance dependence**. Behavior-dependent: coupling high in immobility, drops during running (isolated events rise). Attenuation **steeper apical than basal** (per-cell R ≈ −0.54 vs −0.35).
2. **bAP attenuation is cell-intrinsic** — soma-targeted opsin (rsChRmine-mScarlet-kv2.1) fired directly reproduces the same distance-dependent attenuation → biophysical property of the dendrite, not synaptic-input placement.
3. **Branch structure decouples voltage from calcium (key result)** — V↔Ca²⁺ coupling weakens with **branch order** (tracks bifurcation number, not raw distance). Strong-decoupled events enriched in apical **oblique + basal**; apical **trunk** stays well-coupled. → distal branches carry different info in V vs Ca²⁺; invokes ER/mitochondria Ca²⁺ handling + VGCC-distribution differences.

## Why it matters for the [[gonzalez_nature_2024]] story

- **Validates** the load-bearing assumption (spine Ca²⁺ proxies weight) — but coupling is **not uniform**; decays into distal/high-order branches → caveat the Nature weight estimates inherit.
- **Explains compartment-specific plasticity:** apical vs basal differ in bAP attenuation and V–Ca²⁺ coupling → plausible substrate for why the BTSP kernel appears in oblique but not basal dendrites.
- **Voltage > calcium** for reading dendritic computation — argument against the field's calcium-imaging default.

## Caveats

- Line rate **~1.6 kHz** → can't resolve single spikes in tight bursts; analyze amplitude/envelope, not ~1 ms latencies/half-widths.
- Short segments of a few dendrites → **can't establish event directionality** (started here vs backpropagated in?).
- Ca²⁺-indicator **saturation** not fully excluded, but checks argue against it (decoupling scales with branch order not distance; >100% ΔF/F transients; jRGECO1a Kd ≈ 162 nM).

## Code & data availability

- **Code:** Zenodo `10.5281/zenodo.18090991` — 12 Jupyter notebooks (~6.9 MB), CC BY 4.0.
- **Data:** request-only from lead contact (Losonczy) — not deposited.
- **3D-RTMC software:** `brainvisioncenter.com/uploads/3D/RTMC3D.m` (MATLAB).
- Local: PDF in `Flynn/`; notebooks in `~/repos/dend_utils/2026_neuron_movement-stabilized-recordings/18090991.zip`.

## Reproducibility — both deposits audited

Neither the Nature nor the Neuron code deposit is turnkey, and they fail for **opposite** reasons:

| | Environment | Blocker |
|---|---|---|
| [[gonzalez_nature_2024]] `code/` | Py2 (top-level) + Py3 (`glutamate/`) | **missing code** — private frameworks |
| this (Neuron notebooks) | Py3.11.8, framework-free | **missing data** — hardcoded lab-server paths |

- **Nature `code/`** — hard-imports private Losonczy-lab frameworks not vendored + not on PyPI: `lab3` (11 files), `analysis_AN` (4), `lab` (3); only `sima` is public. Also imports sibling scripts absent from the deposit (`plot_behavioral_LFP_PSD`, `plot_scan_traces`, `calc_db_phase`, `calc_db_morphology`). No dependency manifest; two Python versions. → **cannot run**; a "what we computed" reference, not a runnable pipeline.
- **Neuron notebooks** — all Py3.11.8, **zero** private-framework imports (standard `pandas`/`numpy`/`pickle`/`matplotlib`/`h5py`), clean `create_dataset → comb_dataset → Figure_*` structure. But **no data bundled** — every input is a hardcoded absolute path on the authors' server (`/data4/asako/AOD/KG_Data_RTMC/*.pkl`, per-cell `*_measurements_*.csv`); pickles are Py2-origin (`encoding='latin1'`), i.e. produced by an upstream (Nature-era) pipeline. → **would run under plain Python 3** once you obtain the processed pickles (the request-only data) and fix the paths.
- **Both satisfy** journal "code available" policy (deposited + citable) but **neither is clone-and-run.** To reproduce, email the Losonczy lab for (a) the private `analysis_AN`/`lab`/`lab3` packages [Nature] or (b) the `KG_Data_RTMC` processed pickles [Neuron].
- AI-generated guide to the Nature deposit code: `~/repos/dend_utils/CLAUDE.md`.

### Practical takeaway

- The **openly downloadable** Nature Dryad table (~670 KB, processed per-spine data) is the realistic starting point for hands-on reanalysis (plasticity kernel, weights, tuning) — no private code needed just to *read* it.
- The Neuron notebooks are the best **worked example** of the event-table → figure analysis; usable as a template even without the data.
- Raw two-photon recordings are **not public** for either paper.
