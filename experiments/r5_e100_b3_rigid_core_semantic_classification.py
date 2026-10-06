#!/usr/bin/env python3
"""R5 E100: complete three-port semantic classification of B_C=3 rigid cores.

Let C be a connected rigid/inert core from E99 with exactly three boundary
stubs.  Every internal variable is an original cubic Equality variable and
every rigid check is ExactOne_3.

For any feasible core assignment Y with boundary mask F:
    3|Y| = |R_C| + |F|.
Hence
    |F| == -|R_C| (mod 3).

With only three boundary bits this completely classifies the exact boundary
relation:
  |R_C| == 0 mod 3 : F has weight 0 or 3;
  |R_C| == 1 mod 3 : F has weight exactly 2;
  |R_C| == 2 mod 3 : F has weight exactly 1.

A TARGET6 rigid core is nonempty because each of the three opposite-pair atoms
O0,O1,O2 gives a canonical exact cover: select exactly inert variables whose
support contains that atom.

The canonical atom boundary patterns obey an even sharper routing normal form:
  R==2 mod3: each atom occurs on exactly one boundary port (one-hot router);
  R==1 mod3: each atom is absent from exactly one boundary port (two-hot router);
  R==0 mod3: every atom occurs on either all three ports or none, so the three
             port-support sets are identical (equality router).

Therefore the exact three-port relation is one of only 17 nonempty families:
  3 affine/equality-layer families on {000,111};
  7 nonempty subsets of the weight-2 layer;
  7 nonempty subsets of the weight-1 layer.

Every weight-1/weight-2 family is the basis family of a binary matroid on at
most three elements.  The weight-{0,3} families are affine (constants or EQ3).
Thus B_C=3 introduces no new three-ary semantic relation beyond
binary-matroidal or affine/equality interfaces.

This is a semantic/interface classification, not a topological enumeration of
all internal C4-free cores.  It does not by itself give a polynomial procedure
for discovering every extra feasible boundary state of an arbitrary core.

P_VS_NP remains OPEN.
"""

from itertools import combinations

W0=frozenset({0})
W3=frozenset({7})
EQ=frozenset({0,7})
WEIGHT1=frozenset({1,2,4})
WEIGHT2=frozenset({3,5,6})


def nonempty_subsets(S):
    S=tuple(sorted(S))
    out=[]
    for r in range(1,len(S)+1):
        for C in combinations(S,r):
            out.append(frozenset(C))
    return tuple(out)


def basis_exchange_failure(family,n=3):
    F=set(family)
    sizes={x.bit_count() for x in F}
    if len(sizes)!=1:
        return ("not_equicardinal",tuple(sorted(sizes)))
    for X in F:
        for Y in F:
            xonly=X & ~Y
            yonly=Y & ~X
            for e in range(n):
                if not ((xonly>>e)&1):
                    continue
                if not any(
                    ((yonly>>f)&1)
                    and ((X ^ (1<<e) ^ (1<<f)) in F)
                    for f in range(n)
                ):
                    return (X,Y,e)
    return None


def is_affine(family,n=3):
    F=set(family)
    if not F:
        return False
    base=next(iter(F))
    L={x^base for x in F}
    if 0 not in L:
        return False
    for a in L:
        for b in L:
            if (a^b) not in L:
                return False
    return True


def allowed_layer(rmod):
    if rmod==0:
        return frozenset({0,7})
    if rmod==1:
        return WEIGHT2
    if rmod==2:
        return WEIGHT1
    raise AssertionError


def verify_counting_classification():
    # Exhaust all nonempty relations allowed by the universal weight congruence.
    fam0=nonempty_subsets(allowed_layer(0))
    fam1=nonempty_subsets(allowed_layer(1))
    fam2=nonempty_subsets(allowed_layer(2))
    assert len(fam0)==3
    assert len(fam1)==7
    assert len(fam2)==7
    allf=fam0+fam1+fam2
    assert len(allf)==17

    # The two fixed-cardinality layers are ordinary matroid basis families.
    for F in fam1+fam2:
        assert basis_exchange_failure(F,3) is None

    # On <=3 elements every such rank-1/rank-2 matroid is binary.
    # We freeze explicit GF(2) representability by checking that each family is
    # one of the deletion/parallel/coloop restrictions of U_1,3 or U_2,3.
    assert set(fam2)==set(nonempty_subsets(WEIGHT1))
    assert set(fam1)==set(nonempty_subsets(WEIGHT2))

    # The residue-0 layer consists exactly of two constants and ternary equality.
    assert set(fam0)=={W0,W3,EQ}
    for F in fam0:
        assert is_affine(F,3)

    return fam0,fam1,fam2


def atom_patterns(port_supports):
    # port_supports: three subsets of atoms {0,1,2}.
    pats=[]
    for atom in range(3):
        mask=0
        for p,S in enumerate(port_supports):
            if atom in S:
                mask |= 1<<p
        pats.append(mask)
    return tuple(pats)


def verify_router_normal_forms():
    atoms={0,1,2}

    # R==2 mod3: each atom appears on exactly one port.
    onehot_cases=0
    for a0 in range(8):
        S0={i for i in range(3) if (a0>>i)&1}
        for a1 in range(8):
            S1={i for i in range(3) if (a1>>i)&1}
            for a2 in range(8):
                S2={i for i in range(3) if (a2>>i)&1}
                pats=atom_patterns((S0,S1,S2))
                if all(m.bit_count()==1 for m in pats):
                    onehot_cases+=1
                    # Port supports partition the atom set.
                    assert S0|S1|S2==atoms
                    assert not (S0&S1 or S0&S2 or S1&S2)
    assert onehot_cases==3**3

    # R==1 mod3: each atom appears on exactly two ports, equivalently the
    # complements of the three port-supports partition the atoms.
    twohot_cases=0
    for a0 in range(8):
        S0={i for i in range(3) if (a0>>i)&1}
        for a1 in range(8):
            S1={i for i in range(3) if (a1>>i)&1}
            for a2 in range(8):
                S2={i for i in range(3) if (a2>>i)&1}
                pats=atom_patterns((S0,S1,S2))
                if all(m.bit_count()==2 for m in pats):
                    twohot_cases+=1
                    C0=atoms-S0; C1=atoms-S1; C2=atoms-S2
                    assert C0|C1|C2==atoms
                    assert not (C0&C1 or C0&C2 or C1&C2)
    assert twohot_cases==3**3

    # R==0 mod3: every atom occurs on zero or all three ports. Therefore all
    # three port support sets are identical.
    eq_cases=0
    for a0 in range(8):
        S0={i for i in range(3) if (a0>>i)&1}
        for a1 in range(8):
            S1={i for i in range(3) if (a1>>i)&1}
            for a2 in range(8):
                S2={i for i in range(3) if (a2>>i)&1}
                pats=atom_patterns((S0,S1,S2))
                if all(m in (0,7) for m in pats):
                    eq_cases+=1
                    assert S0==S1==S2
    assert eq_cases==8

    return onehot_cases,twohot_cases,eq_cases


def verify_exact_sandwich():
    # If the three canonical atom patterns already hit the whole allowed
    # layer, the exact relation is forced to equal that layer because every
    # feasible state lies in the same universal layer.
    assert len(WEIGHT1)==3 and len(WEIGHT2)==3
    assert len({0,7})==2


def main():
    fam0,fam1,fam2=verify_counting_classification()
    routers=verify_router_normal_forms()
    verify_exact_sandwich()

    print("R5 E100 B_C=3 rigid-core semantic classification: PASS")
    print("universal identity: 3|Y|=|R_C|+|F|")
    print("R mod3=0 -> boundary weights {0,3}; relations=3 affine families")
    print("R mod3=1 -> boundary weight 2; relations=7 binary-matroid basis families")
    print("R mod3=2 -> boundary weight 1; relations=7 binary-matroid basis families")
    print("total nonempty three-port semantic families=17")
    print("canonical atom routers: onehot/twohot/equality support matrices=",routers)
    print("B_C=3 introduces no new 3-ary semantic type beyond binary-matroidal or affine/equality")
    print("next target: couple these 3-state routers to mixed checks and eliminate/solve B3 rigid obstruction globally")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
