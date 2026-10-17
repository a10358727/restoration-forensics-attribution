#!/usr/bin/env python3
"""Recompute the per-arm values of the manuscript's Table 2 from the released per-seed aggregates.

Input: data/aggregate/headline_per_seed.csv (one row per detector, protocol, policy, training seed and
condition; every value is a test-pool aggregate, no per-image score). Output: seed means of dAUC, dT_lock,
dB_lock and T_recal for the twelve headline configurations under both policies.

    python scripts/table2_from_aggregates.py
"""
import csv
import statistics as st
from collections import defaultdict
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "data" / "aggregate" / "headline_per_seed.csv"
rows = list(csv.DictReader(SRC.open()))
cells = defaultdict(list)
for r in rows:
    if r["condition"] in ("restored_bilateral", "restored_tv"):
        cells[(r["detector"], r["protocol"], r["condition"], r["policy"])].append(r)
print(f"{'detector':16} {'prot':4} {'operator':9} {'policy':7} {'dAUC':>8} {'dT_lock':>8} {'dB_lock':>8} {'T_recal':>8}  seeds")
for (det, prot, cond, pol), rs in sorted(cells.items()):
    m = lambda k: st.mean(float(x[k]) for x in rs)
    print(f"{det:16} {prot:4} {cond.replace('restored_', ''):9} {pol:7} {m('d_auc'):+8.4f} {m('d_tdr_locked'):+8.4f} "
          f"{m('d_rejection'):+8.4f} {m('tdr_recal'):8.4f}  {len(rs)}")
