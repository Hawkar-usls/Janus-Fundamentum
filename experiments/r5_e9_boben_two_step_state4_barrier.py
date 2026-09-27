#!/usr/bin/env python3
from itertools import product, permutations
from fractions import Fraction

UNSAT10=[
    {0,3,5},{0,1,2},{2,4,7},{2,3,6},{0,4,9},
    {1,4,5},{6,7,9},{3,7,8},{1,6,8},{5,8,9}
]

def eq3(a,b,c): return a==b==c
def ex1(a,b,c): return a+b+c==1

def rank_q(M):
    A=[[Fraction(x) for x in row] for row in M]
    if not A: return 0
    r=0
    for c in range(len(A[0])):
        p=next((i for i in range(r,len(A)) if A[i][c]),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        z=A[r][c]; A[r]=[x/z for x in A[r]]
        for i in range(len(A)):
            if i==r or not A[i][c]: continue
            z=A[i][c]
            A[i]=[A[i][j]-z*A[r][j] for j in range(len(A[0]))]
        r+=1
    return r

def relation_two_step():
    out=[]
    for a,b,c,d,e,f in product((0,1),repeat=6):
        ok=False
        for s,t,u in product((0,1),repeat=3):
            if eq3(a,b,s) and ex1(s,t,c) and eq3(t,u,d) and ex1(u,e,f):
                ok=True; break
        if ok: out.append((a,b,c,d,e,f))
    return out

def flatten(rel,pi,split):
    pidx=(0,1,3); qidx=(2,4,5)
    others=[j for j in range(3) if j!=split]
    M=[[0]*16 for _ in range(4)]
    allowed=set()
    for z in rel:
        syms=tuple(2*z[pidx[i]]+z[qidx[pi[i]]] for i in range(3))
        allowed.add(syms)
    for syms in allowed:
        row=syms[split]
        col=4*syms[others[0]]+syms[others[1]]
        M[row][col]=1
    return allowed,M

def boolean_rank_is_four(M):
    supp=[{j for j,v in enumerate(row) if v} for row in M]
    nz=[s for s in supp if s]
    return len(nz)==4 and all(nz[i].isdisjoint(nz[j]) for i in range(4) for j in range(i+1,4))

def props(rows):
    m=len(rows); cols=sorted(set().union(*rows))
    if len(cols)!=m or any(len(r)!=3 for r in rows): return False
    if any(sum(c in r for r in rows)!=3 for c in cols): return False
    if any(len(rows[i]&rows[j])>1 for i in range(m) for j in range(i+1,m)): return False
    c2r={c:[] for c in cols}
    for i,r in enumerate(rows):
        for c in r:c2r[c].append(i)
    seen={('r',0)}; st=[('r',0)]
    while st:
        typ,u=st.pop()
        if typ=='r':
            nb=[('c',c) for c in rows[u]]
        else:
            nb=[('r',r) for r in c2r[u]]
        for v in nb:
            if v not in seen: seen.add(v); st.append(v)
    return len(seen)==2*m

def reduce_A(rows,rrem,crem,pairing):
    rows=[set(r) for r in rows]; m=len(rows)
    if crem not in rows[rrem]: return None
    other_rows=[i for i,r in enumerate(rows) if i!=rrem and crem in r]
    other_cols=sorted(rows[rrem]-{crem})
    if len(other_rows)!=2 or len(other_cols)!=2:return None
    u,v=other_rows; a,b=other_cols
    pairs=((u,a),(v,b)) if pairing==0 else ((u,b),(v,a))
    new=[]; rmap={}
    for i,r in enumerate(rows):
        if i==rrem: continue
        rr=set(r); rr.discard(crem)
        rmap[i]=len(new); new.append(rr)
    for rr,c in pairs:
        i=rmap[rr]
        if c in new[i]: return None
        new[i].add(c)
    cols=sorted(set().union(*new))
    if len(cols)!=m-1:return None
    cmap={c:i for i,c in enumerate(cols)}
    new=[{cmap[c] for c in r} for r in new]
    if not props(new):return None
    return new,rmap,cmap,pairs

rel=relation_two_step()
assert rel==[
 (0,0,0,1,0,0),
 (0,0,1,0,0,1),
 (0,0,1,0,1,0),
 (1,1,0,0,0,1),
 (1,1,0,0,1,0),
]

rank_table={}
for pi in permutations(range(3)):
    ranks=[]; bool4=[]
    for split in range(3):
        allowed,M=flatten(rel,pi,split)
        ranks.append(rank_q(M))
        bool4.append(boolean_rank_is_four(M))
    assert max(ranks)==4
    assert any(bool4)
    rank_table[pi]=ranks

assert props(UNSAT10)
# Frozen legal two-step chain from the 10_3 control.
# Step 1: remove old row 9 / old column 9; legal pairing reconnects
# old row 4 -> old column 8 and old row 6 -> old column 5.
r1=reduce_A(UNSAT10,9,9,1)
assert r1 is not None
rows1,rmap1,cmap1,pairs1=r1
assert pairs1 == ((4,8),(6,5))
# old row 8 / old col 8 survive the first step.
nr8=rmap1[8]; nc8=cmap1[8]
# Step 2: remove their surviving images; the legal pairing reconnects
# relabelled row 4 -> column 6 and relabelled row 7 -> column 1.
r2=reduce_A(rows1,nr8,nc8,1)
assert r2 is not None
rows2,_,_,pairs2=r2
assert pairs2 == ((4,6),(7,1))
assert props(rows2)

print({
 'status':'PASS_BOBEN_TWO_STEP_STATE4_BARRIER',
 'two_step_relation_tuples':len(rel),
 'rank_table':{str(k):v for k,v in rank_table.items()},
 'legal_sequence':[
   'remove row9/col9; reconnect old row4->old col8, old row6->old col5',
   'remove surviving row8/col8; reconnect relabelled row4->col6, row7->col1'
 ],
 'uniform_three_state_edge_lift':'FALSIFIED',
 'P_VS_NP':'OPEN'
})
