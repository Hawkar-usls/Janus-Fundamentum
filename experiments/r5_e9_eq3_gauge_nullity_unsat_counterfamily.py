#!/usr/bin/env python3
from itertools import product

GADGET = [
    (2,5,6),(1,4,7),(5,7,9),(0,3,7),(4,6,9),
    (2,4,8),(3,8,9),(0,5,8),(1,3,6)
]
G = (0,0,0,1,1,1,1,1,1,0)

SEED = [
    (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
    (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
    (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14)
]

def gf2_rank(rows, n):
    a=[]
    for r in rows:
        x=0
        for j in r:
            x ^= 1 << j
        a.append(x)
    rank=0
    for c in range(n):
        p=next((i for i in range(rank,len(a)) if (a[i]>>c)&1),None)
        if p is None:
            continue
        a[rank],a[p]=a[p],a[rank]
        for i in range(len(a)):
            if i!=rank and ((a[i]>>c)&1):
                a[i] ^= a[rank]
        rank += 1
    return rank

def exact1(rows, bits):
    return all(sum(bits[j] for j in r)==1 for r in rows)

def connected(rows, n):
    # incidence graph encoded as variable nodes 0..n-1, row nodes n..n+m-1
    N=n+len(rows)
    adj=[[] for _ in range(N)]
    for i,r in enumerate(rows):
        rr=n+i
        for v in r:
            adj[v].append(rr); adj[rr].append(v)
    seen={0}; stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    return len(seen)==N

def linear(rows):
    s=[set(r) for r in rows]
    for i in range(len(s)):
        for j in range(i+1,len(s)):
            if len(s[i]&s[j])>1:
                return False
    return True

def regularize(rows, n):
    # Each old variable v gets a private 10-variable gadget block.
    out=[]
    # old clause occurrence order gives terminal 0/1/2 for each variable
    occ=[[] for _ in range(n)]
    for ci,r in enumerate(rows):
        for v in r:
            occ[v].append(ci)
    assert all(len(x)==3 for x in occ)
    term_for={}
    for v in range(n):
        for k,ci in enumerate(occ[v]):
            term_for[(v,ci)] = 10*v+k
        for a,b,c in GADGET:
            out.append((10*v+a,10*v+b,10*v+c))
    for ci,r in enumerate(rows):
        out.append(tuple(term_for[(v,ci)] for v in r))
    return out,10*n

# exact gadget controls
proj=set()
for bits in product((0,1), repeat=10):
    if exact1(GADGET,bits):
        proj.add(bits[:3])
assert proj == {(0,0,0),(1,1,1)}
assert all(sum(G[j] for j in r)%2==0 for r in GADGET)
assert G[:3] == (0,0,0)

# seed controls
assert linear(SEED)
assert connected(SEED,15)
for v in range(15):
    assert sum(v in r for r in SEED)==3
assert not any(exact1(SEED,bits) for bits in product((0,1), repeat=15))

# first regularization level
R,n1=regularize(SEED,15)
assert n1==150 and len(R)==150
assert linear(R)
assert connected(R,n1)
for v in range(n1):
    assert sum(v in r for r in R)==3

# 15 terminal-invisible disjoint local kernel modes
modes=[]
for v in range(15):
    z=[0]*n1
    for j,b in enumerate(G):
        if b: z[10*v+j]=1
    assert all(sum(z[j] for j in r)%2==0 for r in R)
    modes.append(z)

# disjoint nonzero supports => independent
supports=[{i for i,b in enumerate(z) if b} for z in modes]
assert all(supports[i] and supports[i].isdisjoint(supports[j])
           for i in range(15) for j in range(i+1,15))

rank=gf2_rank(R,n1)
nullity=n1-rank
assert nullity>=15

print({
    'status':'PASS_EQ3_GAUGE_NULLITY_UNSAT_COUNTERFAMILY',
    'gadget_projection':sorted(proj),
    'seed_n':15,
    'seed_unsat':True,
    'first_level_n':n1,
    'first_level_rank_F2':rank,
    'first_level_nullity_F2':nullity,
    'certified_local_modes':15,
    'theorem_lower_bound':'dim_F2 ker(A_t) >= n_t/10 for t>=1',
    'scientific_ceiling':'P_VS_NP_OPEN'
})
