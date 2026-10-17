# What this repository can and cannot reproduce

Verified on 2026-10-17 in a clean directory, with no access to fingerprint images, per-image scores or
model weights.

## Can be run and checked

| Item | How | Verified result |
|---|---|---|
| Normalization policies, dose ρ | `pr_attribution/normalization.py`; `examples/synthetic_demo.py` | runs on a synthetic ridge pattern |
| Degradation bank, restoration operators | `pr_attribution/degradation.py`, `operators.py`; demo | every operator runs on synthetic uint8 input |
| Locked threshold, five deployment quantities, cluster bootstrap | `pr_attribution/deployment.py`; demo | runs on simulated scores |
| Paired policy contrast ΔΔT / ΔΔB (reference estimator) | `pr_attribution/paired_bootstrap.py`; demo | runs on simulated scores |
| Table 2 per-policy values (12 configurations × 2 policies × 4 quantities) | `scripts/table2_from_aggregates.py` | matches the paper's Table 2 in all 12 rows (to its printed 4 decimals) |
| Figure 3 | `figures/fig3_policy_contrasts.py` | byte-identical to the paper's file with Matplotlib 3.10.6 |
| Figure 4 | `figures/fig4_cross_domain.py` | byte-identical to the paper's file with Matplotlib 3.10.6 |
| Detector architectures | `inference/score_patch.py` | all seven released model types build and run a forward pass on a synthetic 88 × 88 input (random weights) |
| Training settings of the headline detectors | `configs/` | resolved configuration, selected epoch and validation AUCs of all 160 runs, copied unchanged from the run records |

## Cannot be reproduced from this repository

| Item | Why |
|---|---|
| Training any detector; any per-image score | fingerprint corpus not released; no weights |
| Locked thresholds, Δ quantities and intervals from scores | needs per-image scores (not released); only their frozen aggregates are included |
| The frozen paired-bootstrap analysis itself | reads per-image scores; the included estimator is a single-cell restatement for illustration, not the frozen analysis |
| Figure 2 (score distributions) | needs per-image scores |
| Raw-logit sensitivity analysis, operating-point sensitivity at 0.1 % / 5 % | need per-image scores |
| Face and public-fingerprint studies | third-party corpora; study code not included |
| Supplementary tables beyond Table 2 | built from result files not included in this repository |
| D3 detector | third-party code without a licence file |

## Notes

- The functions copied from the research code are byte-identical to it (checked by the scan); the
  functions written for this release (`range_ratio`, `deployment_vector`, `paired_contrast`) restate the
  paper's definitions and have not been checked against per-image data here.
- Everything the demo prints is a property of the simulation, not a result of the paper.
