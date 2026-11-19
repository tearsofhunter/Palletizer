import json,math
from collections import Counter,defaultdict
import numpy as np
from scipy.optimize import milp,LinearConstraint,Bounds
p=json.load(open('parts2.json'))
AN={1:'A',2:'B',3:'C',4:'D',5:'E'}; Q={1:2,2:2,3:2,4:8,5:16}
STOCK=287.0; KERF=0.125; TAIL=12.0
def r16(x): return round(x*16)/16
def up16(x): return math.ceil(x*16-1e-9)/16
# assign marks
marks={}
for a in range(1,6):
    ps=[q for q in p if q['arch']==a]
    cur=sorted([q for q in ps if q['curved']],key=lambda q:q['L'])
    # group by length
    def grp(lst): 
        g=defaultdict(list)
        for q in lst: g[r16(q['L'])].append(q)
        return g
    cg=grp(cur)
    # inner/outer by radius, upper (no straight) vs lower (with straight)
    for L,qs in cg.items():
        q=qs[0]; 
        others=[x for x in cur if (x['straight']>5)==(q['straight']>5)]
        inner = q['R']<=min(x['R'] for x in others)+0.5
        pos = ('LOWER' if q['straight']>5 else 'UPPER') if a in(1,2,3) else 'CURVED'
        name=f"{AN[a]}-{'C' if pos=='CURVED' else pos[0]}{'I' if inner else 'O'}"
        desc=f"{'Inner' if inner else 'Outer'} rail, {pos.lower()} curved piece"
        for x in qs: marks[x['id']]=(name,desc)
    for x in ps:
        if x['id'] in marks: continue
        if x['mat']=='tube' and x['L']>20: marks[x['id']]=(f"{AN[a]}-S","Straight leg rail")
        elif x['mat']=='tube': marks[x['id']]=(f"{AN[a]}-R"+('2' if r16(x['L'])>6.1 else ''),"Rung")
        elif x['L']>20: marks[x['id']]=(f"{AN[a]}-BB","Bottom bar")
        elif x['L']>9: marks[x['id']]=(f"{AN[a]}-PA","Apex plate")
        else: marks[x['id']]=(f"{AN[a]}-P","Splice / foot plate")
json.dump({str(k):v for k,v in marks.items()},open("marks.json","w"))
# parts table
tab=defaultdict(lambda:{'n':0,'Ls':[]})
for q in p:
    m,dsc=marks[q['id']]; t=tab[m]; t['n']+=1; t['Ls'].append(q['L']); t.update(arch=q['arch'],mat=q['mat'],desc=dsc,curved=q['curved'],R=q.get('R'),straight=q.get('straight'))
parts=[]
for m,t in sorted(tab.items()):
    fin=r16(max(t['Ls']))
    cut=up16(fin+(TAIL if t['curved'] else 0))
    parts.append(dict(mark=m,arch=AN[t['arch']],mat=t['mat'],desc=t['desc'],per_arch=t['n'],arches=Q[t['arch']],total=t['n']*Q[t['arch']],finished=fin,cut=cut,curved=t['curved'],R=t['R'],straight=t['straight']))
json.dump(parts,open('parttable.json','w'),indent=1)
for x in parts: print(x['mark'],x['mat'],x['desc'],x['per_arch'],'x',x['arches'],'=',x['total'],'fin',x['finished'],'cut',x['cut'],'R',x['R'],'str',x['straight'])
# nesting
def nest(mat):
    items=[x for x in parts if x['mat']==mat]
    dem=Counter()
    for x in items: dem[x['cut']]+=x['total']
    long=sorted([s for s in dem if s>20],reverse=True); short=sorted([s for s in dem if s<=20],reverse=True)
    pats=[]
    def rec(i,rem,cur):
        if i==len(long):
            if any(cur): pats.append(tuple(cur))
            return
        s=long[i]+KERF; m=min(int(rem//s),dem[long[i]])
        for k in range(m,-1,-1): cur.append(k); rec(i+1,rem-k*s,cur); cur.pop()
    rec(0,STOCK,[])
    A=np.array(pats).T; b=np.array([dem[s] for s in long])
    # minimize sticks; secondary: prefer fewer distinct patterns (small penalty)
    rr=milp(np.ones(len(pats)),constraints=LinearConstraint(A,b,np.inf),integrality=np.ones(len(pats)),bounds=Bounds(0,np.inf),options={'time_limit':300})
    need=Counter({s:dem[s] for s in long}); sticks=[]
    for i,pt in enumerate(pats):
        for _ in range(int(round(rr.x[i]))):
            cuts=[]
            for j,k in enumerate(pt):
                t=min(k,need[long[j]]); need[long[j]]-=t; cuts+=[long[j]]*t
            if cuts: sticks.append(cuts)
    for s in [s for s in short for _ in range(dem[s])]:
        best=None
        for st in sticks:
            rem=STOCK-sum(c+KERF for c in st)
            if rem>=s+KERF-1e-9 and (best is None or rem<best[0]): best=(rem,st)
        if best: best[1].append(s)
        else: sticks.append([s])
    # map lengths back to marks
    pool=defaultdict(list)
    for x in items: pool[x['cut']]+= [x['mark']]*x['total']
    out=[]
    for st in sticks:
        out.append(sorted([(pool[c].pop(),c) for c in sorted(st,reverse=True)],key=lambda t:-t[1]))
    return out,dem
res={}
for mat in('tube','flat'):
    out,dem=nest(mat); res[mat]=out
    tot=sum(s*n for s,n in dem.items())
    print(mat,'sticks',len(out),'cut-length total ft',round(tot/12,1),'LB',math.ceil((tot+KERF*sum(dem.values()))/STOCK))
json.dump(res,open('nest.json','w'))
