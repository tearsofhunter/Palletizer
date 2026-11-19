import rhino3dm as r, sys, math, json
import numpy as np
f=r.File3dm.Read(sys.argv[1])
def arch(x): return 1 if x<-10 else 2 if x<10 else 3 if x<26 else 4 if x<34 else 5
out=[]
for i,o in enumerate(f.Objects):
    g=o.Geometry; t=type(g).__name__
    if t in('Text','Point','Extrusion') or not g.IsClosed: continue
    d=g.Domain; n=600
    P=np.array([[g.PointAt(d.T0+(d.T1-d.T0)*k/n).X,g.PointAt(d.T0+(d.T1-d.T0)*k/n).Y] for k in range(n+1)])*12
    per=np.sum(np.linalg.norm(np.diff(P,axis=0),axis=1))
    A=0.5*abs(np.sum(P[:-1,0]*P[1:,1]-P[1:,0]*P[:-1,1]))
    w=(per-math.sqrt(max(per*per-16*A,0)))/4; L=A/w
    bb=g.GetBoundingBox(); bw=(bb.Max.X-bb.Min.X)*12; bh=(bb.Max.Y-bb.Min.Y)*12
    curved = min(bw,bh)>1.6 and L>20
    R=None
    if curved:
        # circle fit
        x,y=P[:,0],P[:,1]; M=np.c_[2*x,2*y,np.ones_like(x)]; s=np.linalg.lstsq(M,x*x+y*y,rcond=None)[0]
        R=math.sqrt(s[2]+s[0]**2+s[1]**2)
    mat='tube' if w>0.6 else 'flat'
    out.append(dict(id=i,arch=arch(bb.Min.X),mat=mat,w=round(float(w),2),L=round(float(L),2),curved=bool(curved),R=round(R,1) if R else None,x=round(bb.Min.X,2)))
json.dump(out,open('parts.json','w'),indent=0)
from collections import Counter
for k,v in sorted(Counter((p['arch'],p['mat'],p['L'],p['curved'],p['R']) for p in out).items()): print(k,v)
