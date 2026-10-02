#!/usr/bin/env python3
from itertools import product

ROWS = [
    (2,5,6),(1,4,7),(5,7,9),(0,3,7),(4,6,9),
    (2,4,8),(3,8,9),(0,5,8),(1,3,6),
]


def exact_ok(x):
    return all(sum(x[j] for j in row) == 1 for row in ROWS)


def parity_ok(x, rhs=0):
    return all(sum(x[j] for j in row) % 2 == rhs for row in ROWS)


def rank_f2(M):
    M=[row[:] for row in M]
    m=len(M); n=len(M[0]); r=0
    for c in range(n):
        p=next((i for i in range(r,m) if M[i][c]),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        for i in range(m):
            if i!=r and M[i][c]:
                M[i]=[a^b for a,b in zip(M[i],M[r])]
        r+=1
    return r

A=[]
for row in ROWS:
    v=[0]*10
    for j in row: v[j]=1
    A.append(v)

exact=[x for x in product((0,1), repeat=10) if exact_ok(x)]
assert len(exact)==3
assert {x[:3] for x in exact} == {(0,0,0),(1,1,1)}
assert set(exact) == {
    (1,1,1,0,0,0,0,0,0,1),
    (0,0,0,1,1,1,0,0,0,0),
    (0,0,0,0,0,0,1,1,1,0),
}

r=rank_f2(A)
assert r==7
kernel=[x for x in product((0,1), repeat=10) if parity_ok(x,0)]
assert len(kernel)==8
zero_terminal=[x for x in kernel if x[:3]==(0,0,0)]
assert len(zero_terminal)==2
assert set(zero_terminal)=={
    (0,0,0,0,0,0,0,0,0,0),
    (0,0,0,1,1,1,1,1,1,0),
}

# Tiny source control: one source variable appears in three source clauses,
# padded with two fixed local literals represented by direct truth-table rows.
# The quotient only needs the logical fact that all three occurrence copies
# must agree; compare collapse directly for all terminal triples.
for t in product((0,1), repeat=3):
    gadget_extendable = any(x[:3]==t for x in exact)
    eq3 = (t[0]==t[1]==t[2])
    assert gadget_extendable == eq3

print({
    'status':'PASS_EQ3_LOCAL_GAUGE_QUOTIENT',
    'exact_witnesses':len(exact),
    'terminal_projection':['000','111'],
    'rank_F2':r,
    'nullity_F2':10-r,
    'zero_terminal_kernel_dim':1,
    'local_gauge':'0001111110',
    'semantic_quotient':'EQ3',
    'collapse':'returns source variable semantics',
    'D1':'EMPTY',
    'P_VS_NP':'OPEN',
})
