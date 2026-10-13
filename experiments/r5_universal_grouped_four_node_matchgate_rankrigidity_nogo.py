#!/usr/bin/env python3
"""R5 source-authenticated four-native-node grouped tensor matchgate no-go.

Group a PATH of four adjacent original Tanner nodes:
    W0 -- GHZ0 -- W1 -- GHZ1.
Linearity of an original legal square+cubic+linear SCL ensures no
extra incidence between the four chosen nodes. Contract all 3 internal
Tanner wires. In exact external order (p,q,s,t,u,v), the resulting
SIX-wire source tensor is
    T6(p,q,s,t,u,v) =
       ExactOne(p,q,s) * ExactOne(s,t,u) * [u=v].
It has exactly five nonzero Boolean entries, each coefficient 1.

For the TEN balanced 3|3 bipartitions, normalized by placing leg0
on the left, its EXACT flattening ranks are:
  012|345: 2
  013|245, 014|235, 015|234: 3
  023|145, 045|123: 4
  024|135, 025|134, 034|125, 035|124: 5.

External independent invertible GL2 gauges preserve all ranks.
The RANK RIGIDITY THEOREM for ordinary standard matchgate
signatures asserts that the t-th matrix form, i.e. flattening
across a CONTIGUOUS prefix/suffix of the cyclicly ordered
external legs, has rank equal to a power of two (including
the zero case as a degenerate possibility).

For a SIX-leg cyclic order, there are THREE distinct 3|3
contiguous cuts, given by starting the prefix at positions 0,1,2.
After normalizing each side to contain leg0, their three
PAIRWISE INTERSECTION sizes are always {1,2,2}.
The only THREE balanced splits of our T6 having power-of-2
rank are {012,023,045}; their pairwise intersection multiset
is {1,1,2}. Hence NO cyclic order places all three contiguous
cuts among the acceptable splits. For EVERY 6-leg ordering at
least one contiguous flattening has rank 3 or 5, violating
matchgate rank rigidity.

This is a local no-go for the specific connected FOUR-node path
grouping with original boundary wires and independent invertible
2x2 basis changes. It says NOTHING against grouping larger or
different subgraphs, noninvertible gadgets, general Pfaffian sums,
or universal algorithms. Never infer P!=NP.
"""
from __future__ import annotations
from collections import Counter
from itertools import combinations,permutations,product

from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_grouped_two_node_matchgate_flatten_rank_nogo import (
    rank_exact,
)
from fractions import Fraction

BITS6=tuple(product((0,1),repeat=6))
BIPARTITIONS=tuple(
    tuple(c) for c in combinations(range(6),3) if 0 in c
)
FULL=frozenset(range(6))


def original_ternary_exactone(a,b,c):
    return int(a+b+c==1)


def original_ternary_equality(a,b,c):
    return int(a==b==c)


def four_node_path_tensor():
    """Compute full 2^6 coefficient table by three internal bit sums."""
    out={}
    for p,q,s,t,u,v in BITS6:
        out[(p,q,s,t,u,v)]=sum(
            original_ternary_exactone(p,q,x) *
            original_ternary_equality(x,s,y) *
            original_ternary_exactone(y,t,z) *
            original_ternary_equality(z,u,v)
            for x,y,z in product((0,1),repeat=3)
        )
    return out


def formula_4cell(bits):
    p,q,s,t,u,v=bits
    return int(p+q+s==1 and s+t+u==1 and u==v)


def flatten_6(T,left):
    a=tuple(left)
    b=tuple(x for x in range(6) if x not in a)
    assert len(a)==len(b)==3 and set(a+b)==set(range(6))
    rows=[]
    for rb in product((0,1),repeat=3):
        row=[]
        for cb in product((0,1),repeat=3):
            full=[None]*6
            for i,bit in zip(a,rb):full[i]=bit
            for i,bit in zip(b,cb):full[i]=bit
            row.append(T[tuple(full)])
        rows.append(row)
    return rows


def rank_profile(T):
    return {
        left:rank_exact(flatten_6(T,left))
        for left in BIPARTITIONS
    }


def normalized_cut(first_half):
    side=frozenset(first_half)
    assert len(side)==3
    if 0 not in side:side=FULL-side
    return tuple(sorted(side))


def exact_six_legs_cyclic_no_go(profile):
    assert len(profile)==10
    good={c for c,r in profile.items() if r in (1,2,4,8)}
    assert good=={(0,1,2),(0,2,3),(0,4,5)}
    assert sorted(len(set(a)&set(b)) for a,b in combinations(good,2))==[1,1,2]

    total=0
    for order in permutations(range(6)):
        cyclic_cuts=tuple(
            normalized_cut(tuple(order[(start+i)%6]
                                 for i in range(3)))
            for start in range(3)
        )
        assert len(set(cyclic_cuts))==3
        signature=sorted(len(set(a)&set(b))
                         for a,b in combinations(cyclic_cuts,2))
        assert signature==[1,2,2],(order,signature)
        assert any(profile[c] in (3,5) for c in cyclic_cuts)
        total+=1
    assert total==720
    return total


def verify_source_four_node_path(rows,n):
    rows=validate_sparse(rows,n)
    assert len(rows)==n
    source_degree=[0]*n
    for row in rows:
        for v in row:source_degree[v]+=1
    assert all(d==3 for d in source_degree)
    assert all(len(set(rows[i])&set(rows[j]))<=1
               for i in range(n) for j in range(i+1,n))

    # Witnessed original Tanner path W0-G0-W1-G1.
    w0=0
    g0=rows[w0][0]
    w1=next(i for i,row in enumerate(rows)
            if i!=w0 and g0 in row)
    g1=next(v for v in rows[w1] if v!=g0)
    assert g1 not in rows[w0]
    assert w0!=w1 and g0!=g1
    incidences={(i,v) for i in (w0,w1)
                for v in (g0,g1) if v in rows[i]}
    assert incidences=={(w0,g0),(w1,g0),(w1,g1)}
    assert len(incidences)==3

    # Each retained original ternary Tanner gate gives a local
    # 0/1 tensor. The four-node contraction is independent of
    # unused source nodes and has the same five terms.
    T=four_node_path_tensor()
    assert all(T[k]==formula_4cell(k) for k in BITS6)
    assert sum(T.values())==5
    return {
        "source_n":n,
        "row_pair":(w0,w1),
        "variable_pair":(g0,g1),
        "internal_original_incidences":tuple(sorted(incidences)),
        "boundary_legs":6,
        "nonzero_terms":5,
    }


def transform_six_tensor(T,bases):
    assert len(bases)==6
    transformed={}
    for out in BITS6:
        transformed[out]=sum(
            T[old] * product_basis_factor(out,old,bases)
            for old in BITS6
        )
    return transformed


def product_basis_factor(out,old,bases):
    factor=1
    for i in range(6):
        factor*=bases[i][out[i]][old[i]]
    return factor


def main():
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,
    )
    from r5_universal_cubic_flow_lowmoment_collision_20v import flower

    T=four_node_path_tensor()
    expected={bits:formula_4cell(bits) for bits in BITS6}
    assert T==expected
    assert len([x for x in T if T[x]])==5
    profile=rank_profile(T)
    expected_profile={
        (0,1,2):2,(0,1,3):3,(0,1,4):3,(0,1,5):3,
        (0,2,3):4,(0,2,4):5,(0,2,5):5,
        (0,3,4):5,(0,3,5):5,(0,4,5):4,
    }
    assert profile==expected_profile,(profile,expected_profile)
    print("FOUR_NODE_PATH_SIX_BOUNDARY_RANK_PROFILE="+
          ",".join(f"{''.join(map(str,k))}:{v}"
                   for k,v in profile.items()),flush=True)
    num_orders=exact_six_legs_cyclic_no_go(profile)
    print(f"ALL_{num_orders}_CYCLIC_ORDERS_MATCHGATE_POWER2_RANK_OBSTRUCTION=PASS",
          flush=True)

    for name,rows,n in (
        ("FANO7",cyclic(7),7),
        ("K4_SCL18",*make_scl(K4())[:2]),
        ("K33_SCL27",*make_scl(K33())[:2]),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2]),
        ("FLOWER_J5_SCL90",*make_scl(flower(5))[:2]),
    ):
        cert=verify_source_four_node_path(rows,n)
        assert cert["nonzero_terms"]==5
        print(f"AUTHENTICATED_{name}_ORIGINAL_4NODE_PATH="
              f"{cert['internal_original_incidences']}",flush=True)

    lib=(
        ((1,0),(0,1)),
        ((0,1),(1,0)),
        ((1,1),(1,-1)),
    )
    count=0
    for choose in product(range(len(lib)),repeat=6):
        # Exact 2x2 invertible bases; ranks preserved by
        # left/right Kronecker action on ANY 3|3 flattening.
        matrices=tuple(lib[i] for i in choose)
        gauged=transform_six_tensor(T,matrices)
        assert rank_profile(gauged)==expected_profile
        count+=1
    assert count==729
    print("FOUR_NODE_SIX_WIRE_729_HETEROGENEOUS_GL2_GAUGES_RANK_INVARIANT=PASS",
          flush=True)

    # Validate that a forged source row fails independently,
    # rather than borrowing unrelated graph-family metadata.
    valid,n,_,_=make_scl(K4())
    wrong=list(valid)
    wrong[0]=(0,1,2)
    if wrong[0]==valid[0]:wrong[0]=(0,1,3)
    try:
        verify_source_four_node_path(wrong,n)
    except (AssertionError,ValueError):
        print("FOUR_NODE_FORGED_ORIGINAL_SOURCE_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("forged source accepted")

    print("ALL_SCL_NATIVE_4NODE_PATH_GROUPED_MATCHGATE_LOCAL_GL2=IMPOSSIBLE")
    print("MATCHGATE_RANK_RIGIDITY=EXTERNAL_PUBLISHED_THEOREM")
    print("LARGER_OR_DIFFERENT_GROUPING_AND_NONMATCHGATE_COMPRESSION=OPEN")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
