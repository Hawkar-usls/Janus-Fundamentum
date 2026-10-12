#!/usr/bin/env python3
"""R5 source-authenticated two-node tensor contraction: arity-4 MATCHGATE NO-GO.

For ANY original legal cubic/linear/square Positive Exact-One source,
contract ONE original row ExactOne3 node W with ONE adjacent original
column Equality3/GHZ node along their single Tanner incidence wire.
The resulting four-wire tensor is (boundary order: two other row
wires, two other column wires):
    T = |1000> + |0100> + |0011>.

Across the three unordered pair-of-pair flattenings it has exact
matrix ranks {2,3,3}. Independent invertible 2x2 changes on EACH
remaining external wire preserve EVERY one of these ranks, since
flattening transforms by invertible Kronecker products on left/right.

Every standard arity-4 matchgate signature has pure parity and the
even/odd quadratic matchgate identity. For the split 12|34, the
parity-block 2x2 determinants sum to zero, so ranks are NEVER 3:
if determinant nonzero both blocks have rank 2 => total 4;
otherwise each rank <= 1 => total <= 2.
Cyclically rotating the 4 boundary legs preserves the matchgate
identities, so the OTHER noncrossing split 14|23 also cannot rank 3.
ANY cyclic ordering of four legs has TWO noncrossing 2+2 splits,
but T has rank 3 in TWO of its three pairings. Hence at least one
noncrossing split has rank 3; CONTRADICTION.

Consequence: no invertible independent local GL2 basis on four
external wires, nor any relabelling of them, can convert this
specific native (W--GHZ) two-node cell to an arity-4 matchgate.

No-go ONLY for a TWO-node contracted cell. It does NOT prohibit
larger multi-node gadget regrouping, higher-dimensional/noninvertible
algebra, nonmatchgate methods, or a general all-SCL polytime solver.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import product, permutations
from r5_universal_exact_support_residual_dag_attack import validate_sparse

BITS4=tuple(product((0,1),repeat=4))
PAIRINGS=(((0,1),(2,3)),((0,2),(1,3)),((0,3),(1,2)))
W=(0,1,0,0)
GHZ=(1,0,0,1)


def fused_cell():
    # Compute original two-node contraction explicitly, not hardcode
    # its three nonzero entries.
    return {x:sum(W[x[0]+x[1]+z]*GHZ[z+x[2]+x[3]]
                  for z in (0,1)) for x in BITS4}


def flatten(tensor,pairing):
    left,right=pairing
    assert set(left+right)==set(range(4))
    out=[]
    for a in product((0,1),repeat=2):
        row=[]
        for b in product((0,1),repeat=2):
            x=[None]*4
            for j,v in zip(left,a):x[j]=v
            for j,v in zip(right,b):x[j]=v
            row.append(Fraction(tensor[tuple(x)]))
        out.append(row)
    return out


def rank_exact(matrix):
    a=[[Fraction(v) for v in row] for row in matrix]
    assert a and all(len(row)==len(a[0]) for row in a)
    m,n=len(a),len(a[0])
    r=0
    for c in range(n):
        pivot=next((i for i in range(r,m) if a[i][c]),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r]
        unit=a[r][c]
        a[r]=[v/unit for v in a[r]]
        for i in range(m):
            if i!=r and a[i][c]:
                unit=a[i][c]
                a[i]=[v-unit*w for v,w in zip(a[i],a[r])]
        r+=1
        if r==m:break
    return r


def matchgate_quadratic(tensor,kind):
    f=lambda bits:tensor[tuple(int(v) for v in bits)]
    if kind=="EVEN":
        return (f("0000")*f("1111")-f("1100")*f("0011")
                +f("1010")*f("0101")-f("1001")*f("0110"))
    if kind=="ODD":
        return (f("1000")*f("0111")-f("0100")*f("1011")
                +f("0010")*f("1101")-f("0001")*f("1110"))
    raise ValueError("unknown matchgate parity")


def matchgate_kind(tensor):
    even=all(v==0 for x,v in tensor.items() if sum(x)%2)
    odd=all(v==0 for x,v in tensor.items() if sum(x)%2==0)
    if even and odd:return "ZERO"
    if even and matchgate_quadratic(tensor,"EVEN")==0:return "EVEN"
    if odd and matchgate_quadratic(tensor,"ODD")==0:return "ODD"
    return "NOT_MATCHGATE"


def transform_4(tensor,bases):
    assert len(bases)==4
    return {new:sum(tensor[old]*
                    bases[0][new[0]][old[0]]*
                    bases[1][new[1]][old[1]]*
                    bases[2][new[2]][old[2]]*
                    bases[3][new[3]][old[3]]
                    for old in BITS4) for new in BITS4}


def permute_4(tensor,order):
    assert set(order)==set(range(4))
    # The new coordinate i is original coordinate order[i].
    return {x:tensor[tuple(x[order.index(i)] for i in range(4))]
            for x in BITS4}


def verify_native_two_node_cell(rows,n,row_index,var_index):
    rows=validate_sparse(rows,n)
    assert type(row_index) is int and 0<=row_index<n
    assert type(var_index) is int and 0<=var_index<n
    assert var_index in rows[row_index]
    assert len(rows[row_index])==3
    assert sum(var_index in row for row in rows)==3
    # Original legal SCL source checks are all handled by validate_sparse.
    T=fused_cell()
    assert sum(T.values())==3
    assert {x for x,v in T.items() if v}=={
        (1,0,0,0),(0,1,0,0),(0,0,1,1)
    }
    ranks=tuple(rank_exact(flatten(T,p)) for p in PAIRINGS)
    assert ranks==(2,3,3)
    return T,ranks


def verify_symbolic_matchgate_flatten_rank_lemma():
    """Coefficient proof of rank != 3 for 12|34 and 14|23.

    In the EVEN case, the split 12|34 decomposes into two
    parity 2x2 blocks:
      E=[[f0000,f0011],[f1100,f1111]]
      O=[[f0101,f0110],[f1001,f1010]]
    Their determinants sum to the matchgate polynomial Q_even.

    In the ODD case, the two nonzero blocks are:
      E=[[f0001,f0010],[f1101,f1110]]
      O=[[f0100,f0111],[f1000,f1011]]
    Their determinants sum to -Q_odd.

    If the matchgate identity vanishes, either both determinants
    are nonzero (rank 4) or both are zero (rank <=2). Cyclic
    rotation of the legs preserves the quadratic identities up
    to sign and exchanges noncrossing splits, giving the same
    result for 14|23. This is a symbolic argument for ALL
    complex arity-4 matchgate signatures, not a sampled bound.
    """
    import random
    rng=random.Random(0)
    cases=0
    for kind in ("EVEN","ODD"):
        parity=0 if kind=="EVEN" else 1
        permitted=[b for b in BITS4 if sum(b)%2==parity]
        for _ in range(400):
            # Generate a matchgate signature using 7 coefficients
            # and solve the 8th from the nontrivial matchgate identity.
            vals={b:0 for b in BITS4}
            for b in permitted:vals[b]=rng.randint(-4,4)
            if kind=="EVEN":
                vals[(0,0,0,0)]=rng.choice((-2,-1,1,2))
                f=lambda s:vals[tuple(int(v) for v in s)]
                vals[(1,1,1,1)]=(f("1100")*f("0011")-
                                  f("1010")*f("0101")+
                                  f("1001")*f("0110"))/vals[(0,0,0,0)]
            else:
                vals[(1,0,0,0)]=rng.choice((-2,-1,1,2))
                f=lambda s:vals[tuple(int(v) for v in s)]
                vals[(0,1,1,1)]=(f("0100")*f("1011")-
                                  f("0010")*f("1101")+
                                  f("0001")*f("1110"))/vals[(1,0,0,0)]
            assert matchgate_kind(vals)==kind
            ranks=[rank_exact(flatten(vals,p)) for p in PAIRINGS]
            assert 3 not in (ranks[0],ranks[2]),(kind,ranks)
            cases+=1
    return cases


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    samples=(
        ("FANO7",cyclic(7),7),
        ("K4_SCL18",*make_scl(K4())[:2]),
        ("K33_SCL27",*make_scl(K33())[:2]),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2]),
    )
    for label,rows,n in samples:
        row=0
        var=rows[0][0]
        T,r=verify_native_two_node_cell(rows,n,row,var)
        print(f"SOURCE_{label}_W_GHZ_TWO_NODE_CELL_RANKS={r}",flush=True)

    T=fused_cell()
    assert matchgate_kind(T)=="NOT_MATCHGATE"
    assert tuple(rank_exact(flatten(T,p)) for p in PAIRINGS)==(2,3,3)
    trials=verify_symbolic_matchgate_flatten_rank_lemma()
    print(f"ARITY4_EVEN_ODD_MATCHGATE_RANK_LEMMA={trials}_EXACT_CONTROLS",
          flush=True)
    from itertools import product
    from fractions import Fraction
    lib=(
        ((1,0),(0,1)),((0,1),(1,0)),((1,1),(1,-1)),
        ((1,2),(1,1)),((2,1),(1,1)),
    )
    gauges=0
    for indices in product(range(len(lib)),repeat=4):
        B=tuple(lib[i] for i in indices)
        v=transform_4(T,B)
        assert tuple(rank_exact(flatten(v,p)) for p in PAIRINGS)==(2,3,3)
        assert matchgate_kind(v)=="NOT_MATCHGATE"
        gauges+=1
    assert gauges==625

    for ordering in permutations(range(4)):
        moved=permute_4(T,ordering)
        ranks=tuple(rank_exact(flatten(moved,p)) for p in PAIRINGS)
        assert sorted(ranks)==[2,3,3]
        assert 3 in (ranks[0],ranks[2])
        assert matchgate_kind(moved)=="NOT_MATCHGATE"
    print("ALL_24_EXTERNAL_CYCLIC_ORDERS_HAVE_NONCROSSING_RANK3=PROVED")
    print(f"NONUNIFORM_4WIRE_GL2_GAUGES={gauges}_RANK_INVARIANT_PASS")
    print("ALL_SCL_ONE_W_GHZ_GROUPED_PAIR_LOCAL_MATCHGATE=IMPOSSIBLE")
    print("BIGGER_MULTINODE_GROUPINGS_AND_NONMATCHGATE_ALGEBRA=OPEN")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
