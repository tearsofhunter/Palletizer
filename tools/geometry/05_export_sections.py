import json, math, numpy as np
polys=json.load(open('polys.json')); secw=json.load(open('secw.json'))
def rdp(P,eps):
    P=np.asarray(P)
    if len(P)<3: return P
    a,b=P[0],P[-1]; ab=b-a; n=np.linalg.norm(ab)
    d=np.abs(ab[0]*(P-a)[:,1]-ab[1]*(P-a)[:,0])/n if n>1e-9 else np.linalg.norm(P-a,axis=1)
    i=int(np.argmax(d))
    if d[i]>eps: return np.vstack([rdp(P[:i+1],eps)[:-1],rdp(P[i:],eps)])
    return np.vstack([a,b])
def simp(P,eps=0.04):
    P=np.asarray(P)
    if np.allclose(P[0],P[-1]): P=P[:-1]
    j=int(np.argmax(np.linalg.norm(P-P[0],axis=1)))
    A=rdp(P[:j+1],eps); B=rdp(np.vstack([P[j:],P[:1]]),eps)
    return np.vstack([A[:-1],B[:-1]])
def area_centroid(P):
    x,y=P[:,0],P[:,1]; x1,y1=np.roll(x,-1),np.roll(y,-1); cr=x*y1-x1*y; A=cr.sum()/2
    if abs(A)<1e-9: return 0.0,P.mean(axis=0)
    return abs(A),np.array([((x+x1)*cr).sum()/(6*A),((y+y1)*cr).sum()/(6*A)])
def hull(P):
    P=sorted(map(tuple,P))
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];up=[]
    for p in P:
        while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up)>=2 and cross(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return np.array(lo[:-1]+up[:-1])
DENS={'tube':0.512/12,'flat':0.2925/12/0.25}  # lb per sq in of outline (tube 1" wide rails, 1/4" plates)
TYPES={}
desc={'A1':'straight leg','A2':'lower curve','A3':'upper curve to apex','B1':'straight leg','B2':'lower curve','B3':'upper curve to apex',
      'C1':'straight leg','C2':'lower curve','C3':'upper curve to apex','D1':'half-arch (curve + leg)','E1':'straight leg','E2':'curve to apex'}
for s,d in desc.items():
    pcs=[(t,simp(np.array(p))) for t,p in polys[s]]
    W=0; M=np.zeros(2)
    for t,P in pcs:
        A,c=area_centroid(P); dens=DENS['flat'] if t in('P','PA') else DENS['tube']; W+=A*dens; M+=A*dens*c
    c=M/W
    allp=np.vstack([P for _,P in pcs])-c
    H=hull(allp)
    tube,flat=secw[s]
    TYPES[s]={'desc':d,'lb':round((tube*0.512+flat*0.2925)/12,2),
              'pieces':[{'k':t,'p':np.round(P-c,3).tolist()} for t,P in pcs],
              'hull':np.round(H,3).tolist()}
TYPES['BB-D']={'desc':'bundle of 8 bottom bars (D)','lb':round(8*secw['D-BB'][1]*0.2925/12,2),'bar':8,'len':70.13}
TYPES['BB-E']={'desc':'bundle of 16 bottom bars (E)','lb':round(16*secw['E-BB'][1]*0.2925/12,2),'bar':16,'len':70.13}
COUNTS={'A1':4,'A2':4,'A3':4,'B1':4,'B2':4,'B3':4,'C1':4,'C2':4,'C3':4,'D1':16,'E1':32,'E2':32,'BB-D':1,'BB-E':1}
json.dump({'types':TYPES,'counts':COUNTS},open('pack3d/data2.json','w'),separators=(',',':'))
import os; print(os.path.getsize('pack3d/data2.json'), sum(v['lb']*COUNTS[k] for k,v in TYPES.items()))
