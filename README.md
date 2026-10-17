# Evaluating forensic detectors after image restoration — research code and aggregate results

Code and aggregate results accompanying the manuscript *Evaluating Forensic Detectors After Image
Restoration: A Deployment-Centric Attribution Framework* (M.-H. Hsu, Y.-H. Shi), prepared for submission
to *Pattern Recognition*.

Released under the MIT licence (`LICENSE`), which covers the authors' code, documentation and aggregate
results; the Python dependencies in `requirements.txt` keep their own licences and are not
redistributed here. This repository contains the evaluation methods, the
training configurations of 160 fingerprint detector runs (120 principal and 40 supplemental NPR runs),
aggregate results, and the scripts that regenerate
Figures 3–4 and Table 2 of the paper. It contains no fingerprint images, no per-image scores and no model
weights (see `PUBLIC_RELEASE_EXCLUSIONS.md`).

## Research overview

When an image-restoration step is placed in front of a synthetic-image detector, the detector's detection
rate at its operating threshold often changes. That change alone does not show that restoration helps:
the same shift can come from both score distributions moving past a threshold that stayed fixed, in which
case bona-fide images are rejected more often too, and the change can depend on how each image is
normalized before the detector sees it. The paper therefore reads every restored condition through five
quantities at a threshold locked on validation bona-fide scores of the unrestored (degraded) anchor:

| Quantity | Question it answers |
|---|---|
| ΔAUC | did the ranking of the two classes change? |
| ΔT (locked) | what does the frozen deployed rule now catch? |
| ΔB (locked) | what does it now cost bona-fide users? |
| Δτ | how far did the score placement move? |
| T (recalibrated) | does any change survive re-fitting the threshold on the restored condition? |

It then repeats the whole pipeline with a second input normalization — per-image min–max (`minmax`, the
"legacy" policy) versus a fixed 8-bit mapping (`div255`) — with every detector retrained under each policy,
and estimates the between-policy difference ΔΔT = ΔT(fixed) − ΔT(legacy) with a paired bootstrap. A nonzero
ΔΔT shows that the deployed change depends on the normalization policy; it compares two complete
retrained pipelines and is not the causal effect of the normalization alone.

## Repository structure

| Path | Contents |
|---|---|
| `pr_attribution/normalization.py` | the two normalization policies; the normalization dose ρ |
| `pr_attribution/degradation.py`, `ridge_utils.py` | the symmetric degradation bank (six types × five severities); ridge-period estimate |
| `pr_attribution/operators.py` | restoration operators: bilateral, total variation, median, non-local means, Wiener, band-stop |
| `pr_attribution/deployment.py` | locked threshold at 1 % FPR, AUC, the five quantities, the cluster bootstrap |
| `pr_attribution/paired_bootstrap.py` | bootstrap primitives of the paired analysis and a reference estimator of ΔΔT / ΔΔB |
| `inference/score_patch.py` | detector definitions (parameter names match the trained checkpoints) and a patch-scoring script |
| `configs/` | resolved training configuration, selection record and training curve of each of the 160 fingerprint detector runs (120 principal and 40 supplemental NPR runs; 16 detector × protocol × policy configurations × 10 seeds); see `configs/README.md` |
| `figures/` | scripts that regenerate Figures 3 and 4 of the paper from `data/aggregate/` |
| `scripts/table2_from_aggregates.py` | recomputes the per-policy values of Table 2 |
| `examples/synthetic_demo.py` | end-to-end run on synthetic, non-biometric data |
| `data/aggregate/` | aggregate results only (see below) |
| `PUBLIC_RELEASE_EXCLUSIONS.md`, `PUBLIC_RELEASE_REPRODUCIBILITY.md`, `SHA256SUMS` | what is not included and why; what can and cannot be reproduced; checksums |
| `LICENSE`, `CITATION.cff` | MIT licence; citation metadata |

## Environment

Python 3.12 (tested); packages in `requirements.txt` (NumPy, SciPy, scikit-image, OpenCV, Matplotlib;
PyTorch and torchvision only for `inference/`). No GPU is needed for anything in this repository.

```
pip install -r requirements.txt
```

The figure scripts plot the frozen aggregate values unchanged. The paper's figure files were produced
with Matplotlib 3.10.6; file bytes also depend on the Matplotlib version and the installed fonts, so a
regenerated file can differ in font outlines or rasterization while the plotted values are identical.

## Reproduction instructions

| Command | Output |
|---|---|
| `python examples/synthetic_demo.py` | ρ for each operator on a synthetic ridge pattern; the five quantities and ΔΔT / ΔΔB on simulated scores (illustration only) |
| `python scripts/table2_from_aggregates.py` | the per-policy ΔAUC, ΔT, ΔB and T(recal) of the twelve headline configurations (Table 2) |
| `python figures/fig3_policy_contrasts.py` | Figure 3 (paired policy contrasts with their 95 % intervals) in `figures/output/` |
| `python figures/fig4_cross_domain.py` | Figure 4 (fingerprint and face deployment changes) in `figures/output/` |
| `python inference/score_patch.py --model-type … --norm … --ckpt … img.png` | detector scores — requires a trained checkpoint, which is **not** provided (see below) |

## Reproducibility levels

| Level | What it covers | Status in this repository |
|---|---|---|
| 1 — Result regeneration | Table 2 and Figures 3–4 of the paper, re-tabulated and re-plotted from the frozen aggregate results in `data/aggregate/` | supported; the bootstrap estimates are not recomputed |
| 2 — Method demonstration | normalization policies, restoration operators, locked-threshold evaluation, the five deployment quantities and a reference implementation of the paired policy contrast, on synthetic, non-biometric data | supported; demonstrates the methods, does not reproduce the paper's results |
| 3 — Full experimental reproduction | detector training, image scoring, locked thresholds, bootstrap intervals and paired contrasts from the original data | **not possible** from this repository: the 88 × 88 biometric corpus, per-image scores, subject-linked splits, detector weights, private data manifests and frozen scoring records are not released |

No step of Levels 1–2 needs a GPU or any non-public file; after installing `requirements.txt` they run offline.

## Data limitations

The fingerprint corpus is self-collected biometric data released only within the scope of the
participants' consent; it is **not** included, and neither are per-image scores, subject-level splits or
patch manifests. Consequently the following cannot be reproduced from this package alone: training any
detector; computing any per-image score; the locked thresholds, bootstrap intervals and paired contrasts
themselves (only their frozen values are provided); and Figure 2. The face corpora (OpenForensics, AI-Face)
and NIST SD302 / GenPrint are third-party datasets obtained from their providers; none is redistributed.

`data/aggregate/` contains test-pool aggregates only: per-seed rates and AUCs of the headline configurations
(`headline_per_seed.csv`), the paired-contrast estimates and intervals per configuration
(`policy_contrasts.csv`), and the twelve values behind Figure 4 (`cross_domain_signatures.csv`). No row
refers to an individual image or participant.

## Model availability

No trained weights are included. The inference script defines the detector architectures used in the
paper, and `configs/` records how each of the 160 checkpoints was trained; whether and when trained weights
are released has not been decided. The D3 detector is not
supported here: it depends on third-party code without a licence file and on CLIP weights obtained
upstream. Third-party pretrained weights are never redistributed.

## Statistical limitations

The public material does not remove the limitations stated in the paper: bootstrap intervals cluster on
finger identity, not on subject, so they describe within-corpus uncertainty rather than generalization to
new participants; recalibrated rates on the stored sigmoid scale are bounded by a score ceiling (the paper
reports a raw-logit sensitivity analysis for the detectors other than D3); the paired policy contrast was
designed after the preregistered per-arm verdict and is exploratory; the twelve headline configurations are
one dependent family, not independent replications; and all fingerprint evidence comes from one sensor
model and one controlled corpus.

## Technical mapping

Internal study labels appear in a few file comments and in `data/aggregate/policy_contrasts.csv`
(`det` codes: Rn = ResNet-18 with modified stem, Bs = Benjamin et al. base detector, Dt = D3, Np = NPR).
Protocols P1 / P2 are the two held-out-generator protocols of the paper.

## Citation

Please cite this software release using `CITATION.cff`. The accompanying manuscript has not been
published; no article DOI exists yet.
