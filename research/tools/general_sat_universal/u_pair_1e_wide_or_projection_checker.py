#!/usr/bin/env python3
# Finite regression for the U-PAIR-1E wide-OR projection theorem.
from itertools import product, combinations

def pair_env(bits):
    e={}
    for i,b in enumerate(bits):
        e[("t",i)] = bool(b)
        e[("f",i)] = not bool(b)
    return e

def all_visible(n):
    return [(bits,pair_env(bits)) for bits in product([0,1], repeat=n)]

def valid_or_n(bits):
    return any(bits)

def positive_clause_holds(clause, env):
    return any(env[v] for v in clause)

def check_bounded_or_impossibility(n):
    models=all_visible(n)
    selectors=[("t",i) for i in range(n)]+[("f",i) for i in range(n)]
    useful=[]
    for w in range(1,4):
        for c in combinations(selectors,w):
            if all(positive_clause_holds(c,e) for bits,e in models if valid_or_n(bits)):
                useful.append(c)
                z=pair_env((0,)*n)
                assert positive_clause_holds(c,z)
    return len(useful)

def gf2_affine_hull_rank(points):
    if not points: return -1
    base=list(points[0])
    rows=[[a^b for a,b in zip(p,base)] for p in points[1:]]
    if not rows: return 0
    m=[row[:] for row in rows]
    r=0
    cols=len(base)
    for c in range(cols):
        piv=next((i for i in range(r,len(m)) if m[i][c]),None)
        if piv is None: continue
        m[r],m[piv]=m[piv],m[r]
        for i in range(len(m)):
            if i!=r and m[i][c]:
                m[i]=[x^y for x,y in zip(m[i],m[r])]
        r+=1
    return r

def check_affine_hull(n):
    pts=[bits for bits in product([0,1],repeat=n) if any(bits)]
    assert gf2_affine_hull_rank(pts)==n

def prefix_or_exists(bits):
    q=False
    for b in bits:
        q = q or bool(b)
    return q

for n in range(4,9):
    assert all(prefix_or_exists(bits)==any(bits) for bits in product([0,1],repeat=n))
    check_bounded_or_impossibility(n)
    check_affine_hull(n)
    print(f"n={n}: projection=OR_n; all valid width<=3 positive factors also accept zero; affine hull dimension={n}")

print("PASS: finite regression supports the exact wide-OR projection killer.")
print("CLAIM CEILING: auxiliary factorized encodings remain possible; P vs NP stays OPEN.")
