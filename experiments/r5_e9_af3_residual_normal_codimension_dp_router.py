#!/usr/bin/env python3
"""Exact regression for the AF3 residual-normal codimension syndrome-DP router."""

from collections import defaultdict
from itertools import combinations

SAT15_ROWS=[
(0,1,2),(0,9,10),(0,11,12),(1,8,10),(1,11,13),(2,3,6),
(2,4,5),(3,8,12),(3,9,13),(4,7,12),(4,9,14),(5,7,13),
(5,8,14),(6,7,14),(6,10,11)
]
SAT18=[
(0,15,17),(1,4,12),(2,10,14),(3,4,11),(4,8,9),(3,5,13),
(1,6,10),(2,7,15),(1,8,14),(3,7,9),(9,10,16),(7,11,13),
(5,12,17),(0,13,16),(0,12,14),(5,8,15),(2,6,16),(6,11,17)
]
GROWS=[
(2,5,6),(1,4,7),(5,7,9),(0,3,7),(4,6,9),
(2,4,8),(3,8,9),(0,5,8),(1,3,6)
]


def incidence(rows,n):
    A=[[0]*n for _ in rows]
    for i,row in enumerate(rows):
        for j in row:A[i][j]=1
    return A


def rref_affine(A,b,p=3):
    m=len(A);n=len(A[0]) if A else 0
    M=[[v%p for v in A[i]]+[b[i]%p] for i in range(m)]
    piv=[];r=0
    for c in range(n):
        q=next((i for i in range(r,m) if M[i][c]),None)
        if q is None:continue
        M[r],M[q]=M[q],M[r]
        inv=pow(M[r][c],-1,p);M[r]=[(v*inv)%p for v in M[r]]
        for i in range(m):
            if i!=r and M[i][c]:
                f=M[i][c];M[i]=[(M[i][j]-f*M[r][j])%p for j in range(n+1)]
        piv.append(c);r+=1
    if any(all(M[i][j]==0 for j in range(n)) and M[i][n] for i in range(r,m)):
        return None,[],[]
    free=[j for j in range(n) if j not in piv]
    x0=[0]*n
    for i,c in enumerate(piv):x0[c]=M[i][n]
    basis=[]
    for f in free:
        v=[0]*n;v[f]=1
        for i,c in enumerate(piv):v[c]=(-M[i][f])%p
        basis.append(v)
    return x0,basis,piv


def rank_mod(M,p=3):
    if not M:return 0
    return len(rref_affine(M,[0]*len(M),p)[2])


def normalize(a,c):
    j=next(i for i,v in enumerate(a) if v)
    inv=pow(a[j],-1,3)
    return tuple(v*inv%3 for v in a),c*inv%3


def funcs_from_A(A):
    x0,basis,_=rref_affine(A,[1]*len(A))
    assert x0 is not None
    return [(tuple(b[i] for b in basis),x0[i],i) for i in range(len(A[0]))],len(basis)


def transform(funcs,base,basis):
    out=[]
    for a,c,idx in funcs:
        c2=(c+sum(a[j]*base[j] for j in range(len(a))))%3
        a2=tuple(sum(a[j]*v[j] for j in range(len(a)))%3 for v in basis)
        out.append((a2,c2,idx))
    return out


def apsq(funcs,d):
    while True:
        groups=defaultdict(list)
        for a,c,idx in funcs:
            if not any(a):
                if c%3==0:return {'status':'UNSAT'}
                continue
            an,cn=normalize(a,c)
            groups[an].append(((-cn)%3,idx))
        pins=[];survivors=[]
        for an,vals in groups.items():
            offs=sorted(set(v for v,_ in vals))
            if len(offs)==3:return {'status':'UNSAT'}
            if len(offs)==2:
                pins.append((an,next(v for v in range(3) if v not in offs)))
            else:
                b=offs[0];survivors.append((an,(-b)%3,vals[0][1]))
        if not pins:return {'status':'RESIDUAL','d':d,'funcs':survivors}
        base,basis,_=rref_affine([list(a) for a,_ in pins],[b for _,b in pins])
        assert base is not None
        funcs=transform(survivors,base,basis);d=len(basis)


def left_kernel(N):
    # H rows span ker(N^T).
    if not N:return []
    NT=[list(col) for col in zip(*N)]
    _,basis,_=rref_affine(NT,[0]*len(NT))
    return basis


def syndrome_dp(funcs,d):
    N=[list(a) for a,c,idx in funcs]
    b=[(-c)%3 for a,c,idx in funcs]
    r=rank_mod(N)
    eps=len(N)-r
    H=left_kernel(N)
    assert len(H)==eps
    target=tuple((-sum(H[k][i]*b[i] for i in range(len(b))))%3 for k in range(eps))
    cols=[tuple(H[k][i] for k in range(eps)) for i in range(len(N))]
    pred={tuple([0]*eps):None}
    layers=[]
    for i,h in enumerate(cols):
        nxt={}
        for z in pred:
            for s in (1,2):
                q=tuple((z[k]+s*h[k])%3 for k in range(eps))
                if q not in nxt:nxt[q]=(z,s)
        layers.append(nxt);pred=nxt
    if target not in pred:return {'sat':False,'epsilon':eps,'rank':r,'m':len(N)}
    s=[0]*len(N);cur=target
    for i in range(len(N)-1,-1,-1):
        prev,val=layers[i][cur];s[i]=val;cur=prev
    y=[(b[i]+s[i])%3 for i in range(len(N))]
    alpha,_,_=rref_affine(N,y)
    assert alpha is not None
    assert all((sum(N[i][j]*alpha[j] for j in range(d))%3)!=b[i] for i in range(len(N)))
    return {'sat':True,'epsilon':eps,'rank':r,'m':len(N),'alpha':alpha}


def regularize(rows,n):
    cnt=[0]*n;old=[]
    for row in rows:
        rr=[]
        for x in row:
            t=cnt[x];cnt[x]+=1;rr.append(10*x+t)
        old.append(tuple(rr))
    assert cnt==[3]*n
    allrows=old[:]
    for x in range(n):
        for row in GROWS:allrows.append(tuple(10*x+j for j in row))
    return incidence(allrows,10*n)


def main():
    # EQ3 gadget: m=3, rank 2, epsilon 1, SAT.
    G=incidence(GROWS,10)
    rg=apsq(*funcs_from_A(G))
    assert rg['status']=='RESIDUAL'
    dg=syndrome_dp(rg['funcs'],rg['d'])
    assert (dg['m'],dg['rank'],dg['epsilon'],dg['sat'])==(3,2,1,True)

    # PG15: m=11, rank 4, epsilon 7, SAT.
    P=incidence(SAT15_ROWS,15)
    rp=apsq(*funcs_from_A(P))
    assert rp['status']=='RESIDUAL'
    dp=syndrome_dp(rp['funcs'],rp['d'])
    assert (dp['m'],dp['rank'],dp['epsilon'],dp['sat'])==(11,4,7,True)

    # Global regularized unique-model source: APSQ leaves 12 independent normals.
    R=regularize(SAT18,18)
    rr=apsq(*funcs_from_A(R))
    assert rr['status']=='RESIDUAL' and rr['d']==12
    dr=syndrome_dp(rr['funcs'],rr['d'])
    assert (dr['m'],dr['rank'],dr['epsilon'],dr['sat'])==(12,12,0,True)

    print({
      'status':'PASS_AF3_RESIDUAL_NORMAL_CODIMENSION_DP_ROUTER',
      'EQ3':(dg['m'],dg['rank'],dg['epsilon']),
      'PG15':(dp['m'],dp['rank'],dp['epsilon']),
      'REGULARIZED_SAT18':(dr['m'],dr['rank'],dr['epsilon']),
      'E8_D1':'EMPTY','P_VS_NP':'OPEN'})


if __name__=='__main__':main()
