#!/usr/bin/env python3
"""Deterministic finite verifier for the R44BB 15-variable witness.

This verifier is not the source of the general theorem.  It independently checks
all finite witness claims used by the R44BB proof note.
"""
from itertools import product, combinations

N = 15
CLAUSES = [
    (-1,-2,3),(-1,-4,5),(-1,6,-7),(1,-8,-9),(1,-10,11),(1,12,-13),(-1,14,15),
    (2,4,6),(2,5,-7),(2,-8,-10),(2,9,11),(2,-12,14),(-2,13,-15),
    (3,4,-7),(-3,-5,-6),(-3,-8,-11),(-3,9,-10),(3,-12,-15),
    (-4,8,-12),(4,9,13),(4,10,-14),(4,11,15),(5,8,-13),(-5,-9,12),(-5,-10,15),(-5,11,14),
    (6,-8,14),(6,9,15),(6,-10,12),(-6,-11,13),(-7,8,15),(7,9,-14),(7,10,-13),(-7,11,-12),
]
PERM = {1:5,2:6,3:3,4:9,5:12,6:15,7:10,8:1,9:4,10:7,11:2,12:8,13:13,14:14,15:11}
FLIPPED = {3}
EXPECTED_PROFILES = {
    1:(3,4),2:(5,2),3:(3,3),4:(5,2),5:(3,4),6:(5,2),7:(2,5),8:(3,4),9:(5,2),10:(2,5),11:(5,2),12:(3,4),13:(3,3),14:(4,2),15:(5,2)
}


def canon_clause(c):
    return tuple(sorted(c, key=lambda z: (abs(z), z < 0)))


def sat_clause(c, bits):
    return any(bits[abs(l)-1] if l > 0 else not bits[abs(l)-1] for l in c)


def transformed_clause(c):
    out = []
    for lit in c:
        v, s = abs(lit), 1 if lit > 0 else -1
        if v in FLIPPED:
            s = -s
        out.append(s * PERM[v])
    return canon_clause(out)


def translation_group():
    base = sorted(map(canon_clause, CLAUSES))
    good = []
    for mask in range(1 << N):
        image = []
        for c in CLAUSES:
            d = []
            for lit in c:
                v, s = abs(lit), 1 if lit > 0 else -1
                if mask & (1 << (v-1)):
                    s = -s
                d.append(s*v)
            image.append(canon_clause(d))
        if sorted(image) == base:
            good.append(mask)
    return good


def profiles():
    out = {v:[0,0] for v in range(1,N+1)}
    for c in CLAUSES:
        for lit in c:
            out[abs(lit)][0 if lit > 0 else 1] += 1
    return {v:tuple(x) for v,x in out.items()}


def surplus():
    supports = [set(map(abs,c)) for c in CLAUSES]
    best = 10**9
    for mask in range(1,1<<N):
        size = mask.bit_count()
        gamma = 0
        for S in supports:
            if any(mask & (1 << (v-1)) for v in S):
                gamma += 1
        best = min(best, gamma-size)
    return best


def local_affine_consequences_empty():
    # Every support occurs once. Check directly that each signed 3-clause has no
    # nontrivial affine equality a.x=b over GF(2) holding on all local models.
    for c in CLAUSES:
        vars_ = [abs(l) for l in c]
        local_models = []
        for vals in product((0,1), repeat=3):
            ass = dict(zip(vars_, vals))
            if any((ass[abs(l)] == 1) if l > 0 else (ass[abs(l)] == 0) for l in c):
                local_models.append(vals)
        assert len(local_models) == 7
        for a in product((0,1), repeat=3):
            if a == (0,0,0):
                continue
            for b in (0,1):
                if all((sum(ai*xi for ai,xi in zip(a,m)) & 1) == b for m in local_models):
                    return False
    return True


def simplify(value_var, value):
    out=[]
    for c in CLAUSES:
        satisfied=False; d=[]
        for lit in c:
            if abs(lit) != value_var:
                d.append(lit); continue
            lit_true = value if lit>0 else not value
            if lit_true:
                satisfied=True; break
        if not satisfied:
            out.append(tuple(d))
    return out


def binary_unsat(subformula):
    # Exact 2-SAT SCC test on width<=2 clauses only.
    binary=[c for c in subformula if len(c)<=2]
    if any(len(c)==0 for c in binary):
        return True
    verts=[i for i in range(-N,N+1) if i!=0]
    G={l:[] for l in verts}; R={l:[] for l in verts}
    def add(a,b):
        G[a].append(b); R[b].append(a)
    for c in binary:
        if len(c)==1:
            l=c[0]; add(-l,l)
        else:
            a,b=c; add(-a,b); add(-b,a)
    seen=set(); order=[]
    def dfs(v):
        seen.add(v)
        for w in G[v]:
            if w not in seen: dfs(w)
        order.append(v)
    for v in verts:
        if v not in seen: dfs(v)
    comp={}
    def rdfs(v,k):
        comp[v]=k
        for w in R[v]:
            if w not in comp: rdfs(w,k)
    k=0
    for v in reversed(order):
        if v not in comp:
            rdfs(v,k); k+=1
    return any(comp[v]==comp[-v] for v in range(1,N+1))


def blocked_pairs():
    out=[]
    F=[set(c) for c in CLAUSES]
    for i,C in enumerate(F):
        for lit in C:
            blocked=True
            for j,D in enumerate(F):
                if i==j or -lit not in D:
                    continue
                resolvent=(C-{lit}) | (D-{-lit})
                if not any(-x in resolvent for x in resolvent):
                    blocked=False; break
            if blocked:
                out.append((i,lit))
    return out


def main():
    assert len(CLAUSES)==34
    assert all(len(c)==3 and len(set(map(abs,c)))==3 for c in CLAUSES)
    supports=[frozenset(map(abs,c)) for c in CLAUSES]
    assert len(set(supports))==34
    assert all(len(a & b)<=1 for a,b in combinations(supports,2))

    p=profiles()
    assert p==EXPECTED_PROFILES
    assert all(pos*neg > pos+neg for pos,neg in p.values())
    assert surplus()==5

    base=set(map(canon_clause,CLAUSES))
    assert {transformed_clause(c) for c in CLAUSES}==base
    assert PERM[3]==3 and 3 in FLIPPED
    assert translation_group()==[0]

    assert local_affine_consequences_empty()
    assert all(not binary_unsat(simplify(v,val)) for v in range(1,N+1) for val in (False,True))
    assert blocked_pairs()==[]

    count=count_x3_0=0
    for bits in product((False,True), repeat=N):
        if all(sat_clause(c,bits) for c in CLAUSES):
            count += 1
            if bits[2] is False:
                count_x3_0 += 1
    assert count==126
    assert count_x3_0==63

    print("R44BB witness: PASS")
    print("n=15 m=34 surplus=5 models=126 models[x3=0]=63")
    print("pure sign-translation group: trivial")
    print("signed automorphism fixes variable 3 and reverses its polarity")
    print("R44AT/R44AW/R44AX/R44AY/R44AZ witness checks: PASS")


if __name__ == "__main__":
    main()
