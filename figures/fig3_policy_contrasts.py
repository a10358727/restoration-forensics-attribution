"""Deterministic journal Figure 3: E036 frozen headline paired policy contrasts.

Input: data/aggregate/policy_contrasts.csv (released frozen estimates and intervals).

  python figures/fig3_policy_contrasts.py            # writes figures/output/

This script consumes *reported frozen estimates and intervals*. It does not
recompute the 95% two-factor paired bootstrap; it does not use sigmoid/logit
sensitivity data or claim the 12 cells are independent replications.
"""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# 2026-10-17 production settings only (no design change): TrueType instead of Type 3 fonts, and
# reproducible output bytes so a clean rebuild leaves the committed files unchanged.
mpl.rcParams.update({'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.hashsalt': 'fig3'})
META = {'pdf': {'CreationDate': None, 'ModDate': None}, 'svg': {'Date': None}, 'png': {}}

DET = [('Rn', 'ResNet-18'), ('Bs', 'Benjamin et al.\n(base detector)'),
       ('Dt', 'D3')]
PROTO = ('P1','P2')
OPS = ('bil','tv')
OPN = {'bil':'Bilateral', 'tv':'TV'}
KEYS = ('DDT','DDT_lo','DDT_hi','DDB','DDB_lo','DDB_hi')
GROUP_HEAD_Y = (14,9,4)
Y = {(det,p,op): 13 - 5*ix - 2*px - ox
     for ix,(det,_) in enumerate(DET) for px,p in enumerate(PROTO)
     for ox,op in enumerate(OPS)}


def parse_rows(csv_path):
    with open(csv_path, newline='', encoding='utf8') as f:
        raw = list(csv.DictReader(f))
    lookup = {}
    for r in raw:
        if 'role' in r and r['role'] != 'headline':
            continue
        k=(r['det'],r['protocol'],r['operator'])
        if k not in Y:
            continue
        assert k not in lookup, f'Duplicate: {k}'
        vals={q:float(r[q]) for q in KEYS}
        assert all(np.isfinite(x) for x in vals.values())
        for m in ('DDT','DDB'):
            assert vals[m+'_lo'] <= vals[m] <= vals[m+'_hi'], (k,m)
        lookup[k]=vals
    assert set(lookup)==set(Y), f'Missing/extra headlines: {set(Y)^set(lookup)}'
    n_t = sum(v['DDT_hi'] < 0 for v in lookup.values())
    n_b = sum(v['DDB_hi'] < 0 for v in lookup.values())
    assert (n_t,n_b)==(12,10), (n_t,n_b)
    open_b={k for k,v in lookup.items() if v['DDB_hi']>=0}
    assert open_b == {('Rn','P2','bil'),('Rn','P2','tv')}, open_b
    return lookup


def make_figure(rows, out):
    # 176 mm × 103 mm, print-ready; all typography/paths remain vectors.
    mm=1/25.4
    fig=plt.figure(figsize=(176*mm, 103*mm),facecolor='white')
    # Each row-label column is drawn separately so plots are aligned exactly.
    # widths span figure x coordinates in proportions.
    specs=[(0.018, 0.185, 0.190, 0.255),
           (0.523, 0.695, 0.177, 0.285)]
    # tuple: label-left, plot-left, unused-label-width, plot-width
    # label axe start identical y bounds to point axes
    panel_names=['(a)  Difference in synthetic detection-rate change',
                 '(b)  Difference in bona-fide rejection change']
    series=['DDT','DDB']
    for i, ((lab_x, plot_x, lab_width, plot_width), title, variable) in enumerate(zip(specs,panel_names,series)):
        ax=fig.add_axes([plot_x,0.125,plot_width,0.735])
        axlab=fig.add_axes([lab_x,0.125,plot_x-lab_x-0.010,0.735],sharey=ax)
        axlab.set_xlim(0,1)
        axlab.set_ylim(-0.65,14.65)
        ax.set_ylim(-0.65,14.65)
        ax.set_xlim(-0.20,0.037)
        for spine in axlab.spines.values(): spine.set_visible(False)
        axlab.set_xticks([])
        axlab.set_yticks([])
        axlab.set_facecolor('white')
        # Detector headings are outside the grid, along with the four cases.
        for (det,det_label),head_y in zip(DET,GROUP_HEAD_Y):
            axlab.text(0.01,head_y,det_label,ha='left',va='center',
                       fontsize=7.35,weight='bold', color='#25282d',linespacing=.88)
            for j,p in enumerate(PROTO):
                for k,op in enumerate(OPS):
                    yy=Y[(det,p,op)]
                    axlab.text(0.035,yy,f'Protocol {p[-1]} · {OPN[op]}',
                               fontsize=7.15,ha='left',va='center',color='#34383b')
                    # Minimal horizontal row guide to help match dots to labels.
                    ax.axhline(yy,color='#e7e9eb',lw=.45,zorder=0)
        for yy in (9.5,4.5):
            ax.axhline(yy,color='#b8bfc7',lw=.65,zorder=1)
        # Subtle vertical gridlines; zero line emphasized.
        xticks=[-.20,-.15,-.10,-.05,0.0]
        ax.set_xticks(xticks)
        ax.set_xticklabels(['−0.20','−0.15','−0.10','−0.05','0'],fontsize=7.35)
        for val in xticks[:-1]:
            ax.axvline(val,color='#e0e3e6',lw=.5,zorder=0)
        ax.axvline(0,color='#3b3e42',lw=.9,zorder=2)
        ax.tick_params(axis='x',length=2.4,width=.6, color='#525961',pad=4)
        ax.tick_params(axis='y',left=False,labelleft=False)
        for side in ('left','right','top'):ax.spines[side].set_visible(False)
        ax.spines['bottom'].set_linewidth(.65)
        ax.spines['bottom'].set_color('#44484e')
        for det,_ in DET:
            for p in PROTO:
                for op in OPS:
                    k=(det,p,op)
                    yy=Y[k]
                    v=rows[k]
                    est,low,high=(v[variable+s] for s in ('','_lo','_hi'))
                    # Real frozen numerical positions. Hollow points mean CI includes zero.
                    ax.plot([low,high],[yy,yy],color='#33383e',lw=1.13,
                            solid_capstyle='butt',zorder=3)
                    covers_zero=(low<=0<=high)
                    ax.plot(est,yy,'o',ms=3.6,mec='#272b30',mew=.85 if covers_zero else .5,
                            mfc='white' if covers_zero else '#272b30',zorder=4)
        fig.text(lab_x,0.907,title,ha='left',va='center',fontsize=8.0,
                 fontweight='bold',color='#20262e')
        fig.text(plot_x+plot_width/2,0.055,
                 'Fixed-scale (g/255) − per-image min–max',
                 ha='center',va='center',fontsize=7.45,color='#434951')
    # No outer title, no 12/12 or 10/12 banners, no legend or bottom summary.
    out=Path(out);out.mkdir(exist_ok=True,parents=True)
    for ext in ('pdf','svg','png'):
        fig.savefig(out/f'fig3_policy_interaction_verified.{ext}',
                    dpi=400,facecolor='white',bbox_inches=None,metadata=META[ext])
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--csv',type=Path,default=Path(__file__).resolve().parents[1]/'data/aggregate/policy_contrasts.csv')
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'output')
    args=p.parse_args()
    rows=parse_rows(args.csv)
    make_figure(rows,args.out)
    print('12 frozen headline cells; CI below zero: DDT 12/12, DDB 10/12')
    print('CI includes zero for DDB:', sorted(k for k,v in rows.items() if v['DDB_hi']>=0))
    print('Outputs:',args.out)

if __name__=='__main__':
    main()
