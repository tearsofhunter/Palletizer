import rhino3dm as r,json,math,sys
import numpy as np
f=r.File3dm.Read(sys.argv[1]); p=json.load(open('parts.json'))
def fit(P):
    x,y=P[:,0],P[:,1]; M=np.c_[2*x,2*y,np.ones_like(x)]; s=np.linalg.lstsq(M,x*x+y*y,rcond=None)[0]
    R=math.sqrt(s[2]+s[0]**2+s[1]**2); return R,np.abs(np.hypot(x-s[0],y-s[1])-R).max()
def edges(g):
    d=g.Domain; T=np.linspace(d.T0,d.T1,8001)
    P=np.array([[g.PointAt(t).X,g.PointAt(t).Y] for t in T])*12
    seg=np.linalg.norm(np.diff(P,axis=0),axis=1); s=np.r_[0,np.cumsum(seg)]
    S=np.arange(0,s[-1],0.1); Q=np.c_[np.interp(S,s,P[:,0]),np.interp(S,s,P[:,1])]
    D=np.diff(np.r_[Q,Q[:1]],axis=0); ang=np.arctan2(D[:,1],D[:,0])
    turn=np.abs((np.diff(np.r_[ang,ang[:1]])+np.pi)%(2*np.pi)-np.pi)
    corners=np.where(turn>math.radians(25))[0]
    # roll so starts at a corner
    c0=corners[0]; Q=np.roll(Q,-c0-1,axis=0); corners=np.sort((corners-c0-1)%len(Q))
    cuts=list(corners)+[len(Q)-1]; es=[]; prev=0
    for c in cuts:
        if c-prev>2: es.append(Q[prev:c+1])
        prev=c+1
    es.sort(key=len,reverse=True); return es[:2]
for q in p:
    if not q['curved']: continue
    g=f.Objects[q['id']].Geometry
    res=[]
    for E in edges(g):
        L=np.sum(np.linalg.norm(np.diff(E,axis=0),axis=1))
        # straight detection: chord of 6" window deviation (sagitta)
        n=len(E); w=30  # 3"
        st=np.zeros(n,bool)
        for i in range(w,n-w):
            a,b,c=E[i-w],E[i],E[i+w]
            sag=abs((c-a)[0]*(b-a)[1]-(c-a)[1]*(b-a)[0])/np.linalg.norm(c-a)
            st[i]=sag<0.004
        st[:w]=st[w]; st[n-w:]=st[n-w-1]
        R,dev=fit(E[~st]) if (~st).sum()>20 else (None,None)
        res.append((L,st.sum()*0.1,R,dev))
    L=np.mean([x[0] for x in res]); S=np.mean([x[1] for x in res]); R=np.mean([x[2] for x in res]); dev=max(x[3] for x in res)
    q['straight']=round(float(S),1); q['R']=round(float(R),1); q['edgeL']=round(float(L),1); q['dev']=round(float(dev),2)
    print(q['arch'],q['L'],'edgeL',round(L,1),'straight',round(S,1),'R',round(R,1),[round(x[2],1) for x in res],'dev',round(dev,2))
json.dump(p,open('parts2.json','w'))
