#!/usr/bin/env python3
"""Provider replay for C025-E2R-F3D-D2 completion-choice divergence.

Finite source-like line-11/line-12 mechanics only. This does not establish
full Lemma-22 hard-family divergence or any unrestricted ER3 lower bound.
"""
from itertools import combinations, product

LEFT=("a","b","c","d")
ADJ={
    "a":{"y1","w1"}, "b":{"y1","w1"},
    "c":{"y2","w2"}, "d":{"y2","w2"},
}
R_LIMIT=2
EPSILON=0.25
HOODS=({"y1","w1"},{"y2","w2"},{"z1"},{"z2"})


def boundary(B):
    counts={}
    for u in B:
        for x in ADJ[u]:
            counts[x]=counts.get(x,0)+1
    return {x for x,c in counts.items() if c==1}


def valid_B(B):
    return len(B)<=R_LIMIT and len(boundary(B)) <= (1-2*EPSILON)*len(B)


def maximizers():
    vals=[()]
    for k in range(1,R_LIMIT+1):
        for B in combinations(LEFT,k):
            if valid_B(B): vals.append(B)
    M=max(map(len,vals))
    return sorted(B for B in vals if len(B)==M)


def hood(B):
    out=set()
    for u in B: out |= ADJ[u]
    return out


def constraint(u,a):
    if u in ("a","b"):
        return (a["y1"] ^ a["w1"]) == 0
    return (a["y2"] ^ a["w2"]) == 0


def satisfying(B):
    vs=tuple(sorted(hood(B)))
    out=[]
    for bits in product((0,1), repeat=len(vs)):
        a=dict(zip(vs,bits))
        if all(constraint(u,a) for u in B): out.append(a)
    return out


def target(a):
    return a["y1"] & a["z1"] & a["z2"]


def residual_class(rho):
    roots=("y1","w1","y2","w2","z1","z2")
    free=tuple(x for x in roots if x not in rho)
    table={}
    for bits in product((0,1), repeat=len(free)):
        a=dict(rho); a.update(dict(zip(free,bits)))
        table[bits]=target(a)
    vals=set(table.values())
    if vals=={0}: return "CONST_0", set()
    if vals=={1}: return "CONST_1", set()
    ess=set()
    for j,var in enumerate(free):
        others=[i for i in range(len(free)) if i!=j]
        for ob in product((0,1), repeat=len(others)):
            a0=[0]*len(free); a1=[0]*len(free)
            for idx,bit in zip(others,ob): a0[idx]=bit; a1[idx]=bit
            a1[j]=1
            if table[tuple(a0)] != table[tuple(a1)]:
                ess.add(var); break
    return ("LOCAL" if any(ess<=H for H in HOODS) else "CROSSING"), ess


def main():
    Bs=maximizers()
    assert Bs == [("a","b"),("c","d")]
    B1,B2=Bs
    n1=satisfying(B1); n2=satisfying(B2)
    assert n1 == [{"w1":0,"y1":0},{"w1":1,"y1":1}]
    assert n2 == [{"w2":0,"y2":0},{"w2":1,"y2":1}]

    # F-D2-01: same lex-first nu completion, different max-B choice.
    c1,e1=residual_class(n1[0])
    c2,e2=residual_class(n2[0])
    assert c1=="CONST_0"
    assert c2=="CROSSING" and e2=={"y1","z1","z2"}

    # F-D2-02: fixed B, two source-valid satisfying nu choices.
    c00,_=residual_class(n1[0])
    c11,e11=residual_class(n1[1])
    assert c00=="CONST_0"
    assert c11=="CROSSING" and e11=={"z1","z2"}

    print("C025_E2R_F3D_D2_F01_TWO_MAXIMIZERS = PASS")
    print("C025_E2R_F3D_D2_F01_SAME_LEX_NU_CONST0_VS_CROSSING = PASS")
    print("C025_E2R_F3D_D2_F02_FIXED_B_TWO_VALID_NU = PASS")
    print("C025_E2R_F3D_D2_F02_CONST0_VS_CROSSING = PASS")
    print("C025_E2R_F3D_D2_COMPLETION_CHOICE_IS_REAL_SEMANTIC_PARAMETER = PASS")
    print("C025_E2R_F3D_D2_CLAIM_CEILING = SOURCE_LIKE_LINE11_LINE12_FIXTURE_ONLY")
    print("C025_E2R_F3D_D2_FULL_HARD_NW_DIVERGENCE = NOT_ESTABLISHED")
    print("P_VS_NP = OPEN")

if __name__ == "__main__":
    main()
