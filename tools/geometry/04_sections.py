import rhino3dm as r, sys, json, numpy as np, math, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
f=r.File3dm.Read(sys.argv[1]); marks=json.load(open('marks.json'))
def pts(g,n=200):
    d=g.Domain; return np.array([[g.PointAt(d.T0+(d.T1-d.T0)*i/n).X,g.PointAt(d.T0+(d.T1-d.T0)*i/n).Y] for i in range(n+1)])*12
CX={'A':-21.6,'B':0,'C':18.1,'D':30.35,'E':37.46}
QTY={'A':2,'B':2,'C':2,'D':8,'E':16}
items=[]
for k,(m,_) in marks.items():
    a,t=m.split('-'); P=pts(f.Objects[int(k)].Geometry,3000 if t in('S','LI','LO','UI','UO','CI','CO') else 400); items.append(dict(a=a,t=t,P=P,id=int(k)))
zone={'S':'1','L':'2','U':'3','C':'C'}
rails=[i for i in items if i['t'] in('S','LI','LO','UI','UO','CI','CO')]
for i in rails:
    side='L' if i['P'][:,0].mean()<CX[i['a']]*12 else 'R'
    z={'S':'1','L':'2','U':'3','C':'2' if i['a']=='E' else '1'}[i['t'][0]]
    i['sec']=f"{i['a']}{z}"; i['side']=side
for i in items:
    if 'sec' in i: continue
    if i['t']=='BB': i['sec']=f"{i['a']}-BB"; i['side']='M'; continue
    from scipy.spatial import cKDTree
    best=min(((cKDTree(j['P']).query(i['P'])[0].min() if i['t'] in('P','PA') else np.min(np.linalg.norm(j['P']-i['P'].mean(axis=0),axis=1)),j) for j in rails if j['a']==i['a']),key=lambda x:x[0])[1]
    i['sec']=best['sec']; i['side']=best['side']
    if i['t']=='PA': i['side']=best['side']
col={'1':'#2E75B6','2':'#70AD47','3':'#ED7D31','BB':'#C00000'}
def ckey(s): return 'BB' if s.endswith('BB') else s[1]
# section envelopes
def minrect(P):
    best=None
    for th in np.radians(np.arange(0,180,0.5)):
        R=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]); Q=P@R
        L,W=max(np.ptp(Q[:,0]),np.ptp(Q[:,1])),min(np.ptp(Q[:,0]),np.ptp(Q[:,1]))
        if best is None or L*W<best[0]*best[1]: best=(L,W)
    return best
from collections import defaultdict
groups=defaultdict(list)
for i in items: groups[(i['sec'],i['side'])].append(i)
env={}
for (s,side),g in groups.items():
    P=np.vstack([i['P'] for i in g]); env[(s,side)]=minrect(P)
def fi(x):
    x=round(x*4)/4; w=int(x); fr={0:'',0.25:'¼',0.5:'½',0.75:'¾'}[x-w]; return f'{w}{fr}"'
fig,axs=plt.subplots(1,5,figsize=(26,11),gridspec_kw={'width_ratios':[14,13,11,7.6,7.4]})
for ax,a in zip(axs,'ABCDE'):
    for (s,side),g in groups.items():
        if s[0]!=a: continue
        c=col[ckey(s)]
        for i in g:
            P=i['P']; ax.fill(P[:,0],P[:,1],color=c,alpha=1,lw=0); ax.plot(P[:,0],P[:,1],color=c,lw=2.2)
        if side=='R': continue
        P=np.vstack([i['P'] for i in g]); cx,cy=P.mean(axis=0)
        L,W=env[(s,side)]
        lab=f"{s}\n{fi(L)} × {fi(W)}" if not s.endswith('BB') else 'BB  70⅛" flat bar'
        if s.endswith('BB'): ax.text(cx,cy-6,lab,ha='center',va='top',fontsize=10,color=c,weight='bold'); continue
        ax.text(cx+15,cy,lab,ha='left',va='center',fontsize=10,weight='bold',color='k',bbox=dict(fc='white',ec=c,lw=1.5,pad=2))
    ns=len({k for k in groups if k[0][0]==a and not k[0].endswith('BB')})
    nb=1 if any(k[0]==f'{a}-BB' for k in groups) else 0
    ax.set_title(f"Arch {a}  (make {QTY[a]})\n{ns} sections{' + bottom bar' if nb else ''} per arch",fontsize=14,weight='bold')
    ax.set_aspect('equal'); ax.axis('off'); ax.set_ylim(-19.6*12,1.8*12)
LEG1=fig.legend(handles=[Patch(color=col['1'],label='Section 1: leg (straight) — or full half-arch on D'),Patch(color=col['2'],label='Section 2: lower curve (A–C) / curve on E'),Patch(color=col['3'],label='Section 3: upper curve to apex'),Patch(color=col['BB'],label='Bottom bar (flat, ships loose, through-bolted on site)')],loc='lower center',bbox_to_anchor=(0.5,0.065),ncol=4,fontsize=12,frameon=False)
fig.text(0.5,0.115,'Sections bolt together through the paired 1/4" flat plates. Labels show each section\'s envelope (length × width); every section is 1" thick. Both sides of each arch are mirror images.',ha='center',fontsize=11,color='#444')

# ---- connection markers
from matplotlib.lines import Line2D
for ax,a in zip(axs,'ABCDE'):
    pl=[i for i in items if i['a']==a and i['t'] in('P','PA')]
    used=set()
    for x in range(len(pl)):
        for y in range(x+1,len(pl)):
            cx_=pl[x]['P'].mean(axis=0); cy_=pl[y]['P'].mean(axis=0)
            if np.linalg.norm(cx_-cy_)<1.0:
                m=(cx_+cy_)/2; used|={x,y}
                ax.plot(m[0],m[1],'o',ms=13,mfc='white',mec='k',mew=2.2,zorder=5); ax.plot(m[0],m[1],'x',ms=8,mec='k',mew=2.2,zorder=6)
    for x,i in enumerate(pl):
        if x in used: continue
        c=i['P'].mean(axis=0); ax.plot(c[0],c[1],'^',ms=7,color='k',zorder=5)
    for i in items:
        if i['a']==a and i['t'] in('R','R2'):
            P=i['P']; c=P.mean(axis=0); U,S_,Vt=np.linalg.svd(P-c); d=Vt[0]
            for sgn in (-1,1):
                e=c+sgn*d*(np.ptp((P-c)@d)/2); ax.plot(e[0],e[1],'^',ms=5.5,color='k',zorder=5)
        if i['a']==a and i['t']=='BB':
            P=i['P']; 
            for xx in (P[:,0].min()+3,P[:,0].max()-3):
                ax.plot(xx,P[:,1].mean(),'o',ms=13,mfc='white',mec='k',mew=2.2,zorder=5); ax.plot(xx,P[:,1].mean(),'x',ms=8,mec='k',mew=2.2,zorder=6)
leg2=[Line2D([],[],marker='o',ls='',ms=13,mfc='white',mec='k',mew=2.2,label='Field bolt: through-bolted plate-to-plate joint (splices, apex, bottom-bar ends)'),
      Line2D([],[],marker='^',ls='',ms=7,color='k',label='Shop weld: rung-to-rail ends, foot plates; every plate is also welded to its own section\'s rail ends')]
fig.legend(handles=leg2,loc='lower center',bbox_to_anchor=(0.5,0.02),ncol=2,fontsize=12,frameon=False)

plt.subplots_adjust(wspace=0.04,left=0.01,right=0.99,top=0.9,bottom=0.15)
plt.savefig('arch_sections_elevation.png',dpi=110)
json.dump({f'{k[0]}|{k[1]}':v for k,v in env.items()},open('env.json','w'))
for k,v in sorted(env.items()):
    if k[1]!='R': print(k,[round(x,1) for x in v], len(groups[k]),'pieces', sorted({i['t'] for i in groups[k]}))

# --- fit analysis
fitres={}
for (s,side),g in groups.items():
    if side!='L' and side!='M': continue
    P=np.vstack([i['P'] for i in g]); best={}
    for th in np.radians(np.arange(0,180,0.25)):
        R=np.array([[math.cos(th),-math.sin(th)],[math.sin(th),math.cos(th)]]); Q=P@R
        w,h=np.ptp(Q[:,0]),np.ptp(Q[:,1])
        if h<=84.5 and (best.get('wmin') is None or w<best['wmin']): best['wmin']=w; best['h_at']=h
        for W in (40,48):
            if w<=W and (best.get(f'hmin{W}') is None or h<best[f'hmin{W}']): best[f'hmin{W}']=h
    fitres[s]={k:round(float(v),1) for k,v in best.items()}
    print(s,fitres[s])
json.dump(fitres,open('fit.json','w'))

pp={q['id']:q for q in json.load(open('parts2.json'))}
secw={}
for (sname,side),g in groups.items():
    if side=='R': continue
    tube=sum(pp[i['id']]['L'] for i in g if pp[i['id']]['mat']=='tube'); flat=sum(pp[i['id']]['L'] for i in g if pp[i['id']]['mat']=='flat')
    secw[sname]=(round(tube,1),round(flat,1))
json.dump(secw,open('secw.json','w')); print(secw)
polys={}
for (sname,side),g in groups.items():
    if side=='R': continue
    polys[sname]=[(i['t'],i['P'].tolist()) for i in g]
json.dump(polys,open('polys.json','w'))
