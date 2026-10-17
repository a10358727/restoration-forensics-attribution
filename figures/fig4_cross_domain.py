"""Figure 4: minimal, source-verified cross-domain paired-policy dumbbell plot.

Data: data/aggregate/cross_domain_signatures.csv, a frozen 12-row transcription of the
same-instrument summary (fingerprint, OpenForensics, AI-Face). Plotting only: no resampling,
fitting or inference.
Each dot marks one policy-specific locked-threshold restored-minus-anchor
rate difference; a gray connector is NOT a confidence interval.

python figures/fig4_cross_domain.py            # writes figures/output/
"""
from pathlib import Path
import csv
import math
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
SRC = HERE.parent/'data'/'aggregate'/'cross_domain_signatures.csv'
rows = list(csv.DictReader(SRC.open(newline='', encoding='utf-8')))
assert len(rows)==12
assert Counter(r['domain'] for r in rows)=={'Fingerprint':4,'OpenForensics':4,'AI-Face':4}
for r in rows:
    for k in ('dt_legacy','dt_fixed','db_legacy','db_fixed'):
        r[k] = float(r[k]); assert math.isfinite(r[k]), (r,k)
# Do not change source order, which is experimental configuration order.
assert [(r['protocol'],r['operator']) for r in rows[:4]] == [('P1','bilateral'),('P1','TV'),('P2','bilateral'),('P2','TV')]
# These are range checks only; the full 48/48 data verification uses GitHub E042.
assert all(r['dt_legacy']>0 and r['db_legacy']>0 for r in rows[:4])
assert all(r['dt_legacy']<0 and r['dt_fixed']<0 and abs(r['db_legacy'])<.005 for r in rows[4:8])
assert all(r['dt_legacy']<0 and r['dt_fixed']<0 and r['db_legacy']>.15 for r in rows[8:])

plt.rcParams.update({
    'font.family':'sans-serif','font.sans-serif':['Liberation Sans','DejaVu Sans'],
    'font.size':8.0,'axes.linewidth':.55,'axes.edgecolor':'#5a626a',
    'xtick.major.width':.55,'xtick.major.size':2.4,'ytick.major.size':0,
    'savefig.facecolor':'white','figure.facecolor':'white',
    'pdf.fonttype':42,'ps.fonttype':42,
    'axes.spines.top':False,'axes.spines.right':False,
    'svg.hashsalt':'fig4',  # 2026-10-17: reproducible output bytes (production only)
})
META = {'pdf': {'CreationDate': None, 'ModDate': None}, 'svg': {'Date': None}, 'png': {}}
BLUE='#0072B2'; ORANGE='#D55E00'; GREY='#A3ABB0'; TEXT='#20252A'; GRID='#E6EAED'
fig=plt.figure(figsize=(176/25.4,116/25.4),facecolor='white')
# Deliberately leave generous whitespace above/between the three statistical sections.
left_col, right_col, col_width = .260,.644,.327
positions=[(.666,.152),(.401,.152),(.136,.152)]  # bottom, height
panels=[
    dict(domain='Fingerprint',title='(a) 88×88 fingerprints · ResNet-50',
         labels=['P1 · bilateral','P1 · TV','P2 · bilateral','P2 · TV'],
         T=(-.026,.216,[0,.10,.20]),B=(-.020,.180,[0,.08,.16])),
    dict(domain='OpenForensics',title='(b) OpenForensics',
         labels=['NPR · bilateral','NPR · TV','ResNet-50 · bilateral','ResNet-50 · TV'],
         T=(-1.055,.065,[-1.,-.5,0]),B=(-.0055,.0045,[-.005,0,.005])),
    dict(domain='AI-Face',title='(c) AI-Face',
         labels=['NPR · bilateral','NPR · TV','Xception · bilateral','Xception · TV'],
         T=(-.164,.017,[-.15,-.10,-.05,0]),B=(-.030,.735,[0,.2,.4,.6])),
]

def nice_fmt(x,pos):
    if abs(x)<1e-11:return '0'
    if abs(x)<.01:return f'{x:.3f}'.replace('-', '−')
    if abs(x)<1:return f'{x:.2f}'.replace('-', '−')
    return f'{x:.1f}'.replace('-', '−')

# Single shared legend; lines between shapes represent neither CI nor repeated measurements.
handles=[Line2D([],[],color=BLUE,marker='o',mfc=BLUE,ms=5.0,ls='none',label='Per-image min–max'),
         Line2D([],[],color=ORANGE,marker='s',mfc=ORANGE,ms=4.7,ls='none',label='Fixed-scale (g/255)')]
fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.64,.992),frameon=False,
           ncol=2,columnspacing=2.6,handletextpad=.5,fontsize=8.5,borderaxespad=0.)
fig.text(left_col+col_width/2,.914,'Synthetic detection-rate change',ha='center',va='center',fontsize=9.0,weight='bold',color=TEXT)
fig.text(right_col+col_width/2,.914,'Bona-fide rejection change',ha='center',va='center',fontsize=9.0,weight='bold',color=TEXT)

for idx,p in enumerate(panels):
    bot,height=positions[idx]
    fig.text(.026,bot+height+.052,p['title'],fontsize=9.4,weight='bold',ha='left',va='center',color=TEXT)
    domainrows=[r for r in rows if r['domain']==p['domain']]
    assert len(domainrows)==4
    # Text shares the identical y coordinate transform with the two measurement axes.
    labax=fig.add_axes([.020,bot,.223,height]);labax.set_xlim(0,1);labax.set_ylim(-.5,3.5);labax.axis('off')
    for j,name in enumerate(p['labels']):labax.text(.995,3-j,name,ha='right',va='center',fontsize=8.05,color=TEXT)
    for x0,metric in ((left_col,'T'),(right_col,'B')):
        ax=fig.add_axes([x0,bot,col_width,height]);ax.set_ylim(-.5,3.5)
        xmin,xmax,ticks=p[metric];ax.set_xlim(xmin,xmax);ax.set_xticks(ticks)
        ax.xaxis.set_major_formatter(FuncFormatter(nice_fmt))
        ax.grid(axis='x',lw=.48,color=GRID,zorder=0)
        ax.axvline(0,color='#434A51',lw=.90,zorder=1)
        ax.tick_params(axis='x',labelsize=7.5,color='#5B6066',labelcolor=TEXT,pad=3)
        ax.tick_params(axis='y',left=False,labelleft=False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#8B9297')
        for j,r in enumerate(domainrows):
            y=3-j
            a,b=r[f'd{metric.lower()}_legacy'],r[f'd{metric.lower()}_fixed']
            assert xmin<a<xmax and xmin<b<xmax,(p['domain'],metric,j,a,b)
            ax.plot([a,b],[y,y],color=GREY,lw=.9,solid_capstyle='butt',zorder=2)
            ax.plot(a,y,marker='o',ls='none',mfc=BLUE,mec='#17465A',mew=.32,ms=5.1,zorder=3)
            ax.plot(b,y,marker='s',ls='none',mfc=ORANGE,mec='#6F381D',mew=.32,ms=4.8,zorder=4)
    if idx<2:
        y=bot-.039
        fig.add_artist(Line2D([.025,.975],[y,y],lw=.6,color='#D5DDE2',transform=fig.transFigure))

# No total title, numerical claims, or methodological paragraph inside the plot.
# The manuscript caption explains anchors, policies, differing scales and scope.
for ext in ('pdf','svg','png'):
    (HERE/'output').mkdir(exist_ok=True); fig.savefig(HERE/'output'/f'fig4_cross_domain.{ext}',dpi=400,facecolor='white',metadata=META[ext])
plt.close(fig)
print('verified-layout Figure 4: 12 configurations, 48 values, frozen E042-derived CSV')
