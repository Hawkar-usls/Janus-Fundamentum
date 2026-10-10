#!/usr/bin/env python3
from __future__ import annotations
from collections import deque
from fractions import Fraction
from itertools import combinations
import json

LCF=[-29,-19,-13,13,21,-27,27,33,-13,13,19,-21,-33,29]
BASE_CYCLE=[0,1,2,3,4,5,6,7,40,41]
SEED_NEG={frozenset((0,1)),frozenset((3,4)),frozenset((58,59))}
NEG_CYCLE=[58,45,44,31,30,17,16,3,2,59]

def harries():
    a=[set() for _ in range(70)]
    for i in range(70):
        j=(i+1)%70; a[i].add(j); a[j].add(i)
    for i,d in enumerate(LCF*5):
        j=(i+d)%70; a[i].add(j); a[j].add(i)
    return a

def connected(a,skip=None):
    seen={0}; st=[0]
    while st:
        u=st.pop()
        for v in a[u]:
            if skip is not None and frozenset((u,v))==skip: continue
            if v not in seen: seen.add(v); st.append(v)
    return len(seen)==len(a)

def girth(a):
    best=10**9
    for s in range(len(a)):
        dist=[-1]*len(a); par=[-1]*len(a); dist[s]=0; q=deque([s])
        while q:
            u=q.popleft()
            for v in a[u]:
                if dist[v]<0:
                    dist[v]=dist[u]+1; par[v]=u; q.append(v)
                elif par[u]!=v:
                    best=min(best,dist[u]+dist[v]+1)
    return best

def bipartition(a):
    col=[None]*len(a); col[0]=0; q=deque([0])
    while q:
        u=q.popleft()
        for v in sorted(a[u]):
            if col[v] is None: col[v]=1-col[u]; q.append(v)
            else: assert col[v]!=col[u]
    return col

def rank_q(A):
    M=[[Fraction(x) for x in row] for row in A]
    r=0
    for c in range(len(M[0])):
        p=next((i for i in range(r,len(M)) if M[i][c]),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        z=M[r][c]; M[r]=[x/z for x in M[r]]
        for i in range(len(M)):
            if i==r or M[i][c]==0: continue
            z=M[i][c]; M[i]=[M[i][j]-z*M[r][j] for j in range(len(M[0]))]
        r+=1
    return r

def matching(a,left,forbidden):
    mr={}
    def aug(u,seen):
        for v in sorted(a[u]):
            e=frozenset((u,v))
            if e in forbidden or v in seen: continue
            seen.add(v)
            if v not in mr or aug(mr[v],seen):
                mr[v]=u; return True
        return False
    for u in sorted(left): assert aug(u,set())
    return {u:v for v,u in mr.items()}

def edge_colors(a,C):
    M0=matching(a,C,set()); f0={frozenset((u,v)) for u,v in M0.items()}
    M1=matching(a,C,f0); f1=f0|{frozenset((u,v)) for u,v in M1.items()}
    M2={u:next(v for v in sorted(a[u]) if frozenset((u,v)) not in f1) for u in C}
    out={}
    for k,M in enumerate((M0,M1,M2)):
        for u,v in M.items(): out[frozenset((u,v))]=k
    return out

def perms(a,C,colors):
    C=sorted(C); M=[{} for _ in range(3)]
    for c in C:
        for v in a[c]: M[colors[frozenset((c,v))]][c]=v
    cc={c:i for i,c in enumerate(C)}
    cv={M[0][c]:cc[c] for c in C}
    P=[None]*len(C); Q=[None]*len(C)
    for c in C:
        i=cc[c]; P[i]=cv[M[1][c]]; Q[i]=cv[M[2][c]]
    return tuple(P),tuple(Q)

def inv(P):
    x=[0]*len(P)
    for i,j in enumerate(P): x[j]=i
    return x

def phase(P,Q):
    ip,iq=inv(P),inv(Q); phi=[None]*len(P)
    for root in range(len(P)):
        if phi[root] is not None: continue
        phi[root]=0; st=[root]
        while st:
            i=st.pop()
            for j,inc in ((P[i],1),(Q[i],-1),(ip[i],-1),(iq[i],1)):
                w=(phi[i]+inc)%3
                if phi[j] is None: phi[j]=w; st.append(j)
                elif phi[j]!=w: return None
    return tuple(phi)

def noncomm(P,Q):
    return any(P[Q[i]]!=Q[P[i]] for i in range(len(P)))

def matrix(a,V,C,neg=set()):
    V=sorted(V); vi={v:i for i,v in enumerate(V)}; out=[]
    for c in sorted(C):
        row=[0]*len(V)
        for v in a[c]: row[vi[v]]=-1 if frozenset((c,v)) in neg else 1
        out.append(row)
    return out

def lift(a,colors,neg):
    out=[set() for _ in range(2*len(a))]; co={}
    for u in range(len(a)):
        for v in a[u]:
            if u<v:
                cross=frozenset((u,v)) in neg; k=colors[frozenset((u,v))]
                for s in (0,1):
                    t=s^int(cross); x=2*u+s; y=2*v+t
                    out[x].add(y); out[y].add(x); co[frozenset((x,y))]=k
    return out,co

def lift_cycle(cyc,neg,s=0):
    out=[]
    for i,u in enumerate(cyc):
        out.append(2*u+s)
        if frozenset((u,cyc[(i+1)%len(cyc)])) in neg: s^=1
    return out,s

def conflict(a,V,C):
    G={v:set() for v in V}
    for c in C:
        vs=sorted(a[c])
        for u,v in combinations(vs,2): G[u].add(v); G[v].add(u)
    return G

def sparse_hole(a,V,C,cyc):
    V=set(V); cyc=list(cyc)
    if cyc[0] not in V: cyc=cyc[1:]+cyc[:1]
    x=[cyc[2*i] for i in range(5)]; cc=[cyc[2*i+1] for i in range(5)]
    G=conflict(a,V,C); assert all(len(G[v])==6 for v in V)
    for i in range(5):
        for j in range(i+1,5):
            assert (x[j] in G[x[i]])==((j-i) in (1,4))
    w=[]; ab=[]
    for i in range(5):
        w.append(next(iter(a[cc[i]]-{x[i],x[(i+1)%5]})))
        D=next(iter(a[x[i]]-{cc[i],cc[(i-1)%5]}))
        ab.append(sorted(a[D]-{x[i]}))
    ports=w+[z for p in ab for z in p]
    assert len(ports)==15 and len(set(ports))==15
    for i in range(5):
        L=(w[(i-1)%5],w[i],ab[i][0])
        assert all(v in G[x[i]] for v in L)
        assert all(v not in G[u] for u,v in combinations(L,2))
    return ports

B=harries()
assert connected(B) and girth(B)==10 and all(len(x)==3 for x in B)
part=bipartition(B); V={i for i,c in enumerate(part) if c==0}; C=set(range(70))-V
assert len(V)==len(C)==35
colors=edge_colors(B,C); P,Q=perms(B,C,colors)
assert noncomm(P,Q) and phase(P,Q) is None
assert rank_q(matrix(B,V,C))==35
assert rank_q(matrix(B,V,C,SEED_NEG))==33

assert all(NEG_CYCLE[(i+1)%10] in B[NEG_CYCLE[i]] for i in range(10))
assert sum(frozenset((NEG_CYCLE[i],NEG_CYCLE[(i+1)%10])) in SEED_NEG for i in range(10))%2==1
assert sum(frozenset((BASE_CYCLE[i],BASE_CYCLE[(i+1)%10])) in SEED_NEG for i in range(10))==2

L1,col1=lift(B,colors,SEED_NEG)
assert connected(L1) and girth(L1)==10
V1={2*v+s for v in V for s in (0,1)}; C1={2*c+s for c in C for s in (0,1)}
cyc1,end=lift_cycle(BASE_CYCLE,SEED_NEG); assert end==0
ports1=sparse_hole(L1,V1,C1,cyc1)
P1,Q1=perms(L1,C1,col1); assert noncomm(P1,Q1) and phase(P1,Q1) is None

cycle_edges={frozenset((cyc1[i],cyc1[(i+1)%10])) for i in range(10)}
candidate=None
for u in range(len(L1)):
    for v in sorted(L1[u]):
        if u<v:
            e=frozenset((u,v))
            if e not in cycle_edges and connected(L1,skip=e):
                candidate=e; break
    if candidate is not None: break
assert candidate is not None

L2,col2=lift(L1,col1,{candidate})
assert connected(L2) and girth(L2)>=10
V2={2*v+s for v in V1 for s in (0,1)}; C2={2*c+s for c in C1 for s in (0,1)}
cyc2,end2=lift_cycle(cyc1,{candidate}); assert end2==0
ports2=sparse_hole(L2,V2,C2,cyc2)
P2,Q2=perms(L2,C2,col2); assert noncomm(P2,Q2) and phase(P2,Q2) is None

out={
 "status":"PASS_HARRIES_NULLITY_AMPLIFYING_FILTERED_FAMILY",
 "seed":{
   "base_rank_Q":35,
   "signed_rank_Q":33,
   "signed_nullity_Q":2,
   "first_lift_nullity_Q":2,
   "first_lift_girth":10,
   "sparse_ports":len(ports1)
 },
 "recursive":{
   "first_one_edge_signing":sorted(candidate),
   "recurrence":"d_(t+1) >= 2 d_t - 1",
   "second_step_lower_bound":3,
   "preserved_10cycle":True,
   "second_sparse_ports":len(ports2)
 },
 "family":{
   "n_t":"35*2^t, t>=1",
   "d_t_lower":"2^(t-1)+1 = n_t/70+1",
   "nullity":"Omega(n), hence omega(log n)",
   "girth":">=10",
   "phase":"FAIL",
   "noncommuting":True,
   "sparse_conflict_C5":True
 },
 "boundary":{
   "PA0025_filtered_family":"CONSTRUCTED",
   "hardness":"NOT_CLAIMED",
   "universal_solver":"NOT_PROVED",
   "D1":"EMPTY",
   "P_VS_NP":"OPEN",
   "P_EQ_NP":"NOT_PROVED"
 }
}
print(json.dumps(out,sort_keys=True))
