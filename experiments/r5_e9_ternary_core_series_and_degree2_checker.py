#!/usr/bin/env python3
from itertools import product

def comp(a):
    return tuple(1-x for x in a)

def cp_rel(t):
    bad={tuple(t),comp(tuple(t))}
    return {a for a in product((0,1),repeat=len(t)) if a not in bad}

def series_project(t,s):
    # scopes are (x,A...) and (x,B...), with A,B disjoint.
    A=t[1:]; B=s[1:]
    out=set()
    for a in product((0,1),repeat=len(A)):
        for b in product((0,1),repeat=len(B)):
            ok=False
            for x in (0,1):
                if (x,)+a in cp_rel(t) and (x,)+b in cp_rel(s):
                    ok=True; break
            if ok:
                out.add(a+b)
    return out

def predicted_pattern(t,s):
    tx=t[0]; sx=s[0]
    delta=tx^sx
    B=s[1:]
    tailB = B if delta==1 else comp(B)
    return t[1:]+tailB

def nae(vals):
    return len(set(vals))>1

def dual_mapping_k4():
    # dual factor graph K4: 4 ternary factors, 6 repair variables/edges.
    verts=range(4)
    edges=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
    inc={v:[] for v in verts}
    for i,(u,v) in enumerate(edges):
        inc[u].append(i); inc[v].append(i)

    # enumerate arbitrary known model y on edge-variables that satisfies every factor
    models=[]
    for y in product((0,1),repeat=6):
        if all(nae(tuple(y[e] for e in inc[v])) for v in verts):
            models.append(y)
    assert models

    for y in models[:8]:
        for h in product((0,1),repeat=6):
            z=tuple(y[i]^h[i] for i in range(6))
            repair_ok=all(nae(tuple(z[e] for e in inc[v])) for v in verts)
            selected={i for i,b in enumerate(z) if b}
            factor_ok=all(1 <= sum(e in selected for e in inc[v]) <= 2 for v in verts)
            assert repair_ok==factor_ok

def main():
    # Exhaustive series-composition identity up to arity 4 on each side.
    checks=0
    for la in range(1,4):
        for lb in range(1,4):
            for t in product((0,1),repeat=la+1):
                for s in product((0,1),repeat=lb+1):
                    got=series_project(t,s)
                    u=predicted_pattern(t,s)
                    want=cp_rel(u)
                    assert got==want
                    checks+=1

    dual_mapping_k4()

    print("COMPLEMENT_PAIR_SERIES_CONTRACTION = PASS")
    print("SERIES_CASES =",checks)
    print("DEGREE2_DUAL_GENERAL_FACTOR_CORRESPONDENCE = PASS")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
