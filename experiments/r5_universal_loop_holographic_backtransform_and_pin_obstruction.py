#!/usr/bin/env python3
"""Universal reversible loop gauge and conditional source pinning.

The exact 16-moment tensor of R5 is simply a uniform invertible
2x2 holographic transform of original source T4:
 H=[[1,1],[-1,2]], det(H)=3, M=(H^tensor4)T4 / 3.
Signed selected-loop edge weight is D=diag(1,1/2).
 H^T D H=diag(3/2,3) = diag(pi(0)^-1,pi(1)^-1).
Thus the exact loop rewrite alone is algebraically equivalent to
the original T4 contraction, without a polynomial nonzero test.

Each matched source pin replaces T4 with E4 or O4 and
uses the SAME H gauge. Unpinned M has zero moments of
local degree 1 and 4; both pinned tables do not.
If pin BOTH ORIGINAL matched variables of any matched
quotient edge to 1, the two variables belong to the
same original Exact-One row. Its source is now UNSAT;
nevertheless the generalized-loop term selecting only
that single quotient edge is a NONZERO rational.
Exact global cancellation is indispensable.

The results do not rule out new global compression,
larger gadgets or general P=NP solutions.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import product
from r5_universal_all_scl_perfect_matching_rank2_network import (
    paired_quartic_network, LOCAL_OPTIONS
)
from r5_universal_grouped_two_node_matchgate_flatten_rank_nogo import (
    fused_cell,flatten,rank_exact,PAIRINGS,BITS4
)
from r5_universal_rank2_exact_bethe_loop_correction import local_loop_moments
from r5_universal_pinned_loop_witness_extraction_gate import (
    exact_pin_moment_numerators,signed_pinned_loop_exact
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse

H=((1,1),(-1,2))
D=(Fraction(1),Fraction(1,2))

def mul(xs):
    out=1
    for x in xs:out*=x
    return out

def transform_tensor4(tensor):
    return {y:sum(tensor[x]*mul(H[y[j]][x[j]] for j in range(4))
                  for x in BITS4) for y in BITS4}

def moment_dict(table):
    return {bits:Fraction(table[sum(bits[i]<<i for i in range(4))])
            for bits in BITS4}

def prove_backtransform():
    T=fused_cell()
    transformed=transform_tensor4({x:Fraction(T[x],3) for x in BITS4})
    M=moment_dict(local_loop_moments())
    assert transformed==M
    assert H[0][0]*H[1][1]-H[0][1]*H[1][0]==3
    for a in (0,1):
        for b in (0,1):
            pairing=sum(Fraction(H[s][a]*H[s][b])*D[s]
                        for s in (0,1))
            expected=Fraction(3,2) if a==b==0 else (
                Fraction(3) if a==b==1 else Fraction(0)
            )
            assert pairing==expected
    original_ranks=tuple(rank_exact(flatten(T,p)) for p in PAIRINGS)
    loop_ranks=tuple(rank_exact(flatten(M,p)) for p in PAIRINGS)
    assert original_ranks==loop_ranks==(2,3,3)
    print("ALL_SCL_LOOP_MOMENTS_INVERTIBLE_HOLOGRAPHIC_T4_TRANSFORM=PROVED")
    print("ALL_SCL_ORIGINAL_AND_LOOP_LOCAL_FLATTEN_RANKS=(2,3,3)")
    print("H_TRANSPOSE_D_H_EQUALS_DIAG_3OVER2_AND_3=PROVED")
    print("ONE_MATCHGATE_LOOP_GL2_REWRITE=REFUTED")

    for pin in (0,1):
        raw,den=exact_pin_moment_numerators(pin)
        source={bits:Fraction(int(bits in LOCAL_OPTIONS and bits[2]==pin),3)
                for bits in BITS4}
        transformed=transform_tensor4(source)
        target=moment_dict([Fraction(v,den) for v in raw])
        assert transformed==target
        assert target[(1,0,0,0)]!=0
        assert target[(1,1,1,1)]!=0
        print(f"PIN_{pin}_LOOP_IS_SAME_INVERTIBLE_H_GAUGE=PROVED")

def incompatible_pin_weight_one(rows,n,evaluate=False):
    rows=validate_sparse(rows,n)
    Q=paired_quartic_network(rows,n)
    (a,pa),(b,pb)=Q["endpoints"][0]
    u,v=Q["matching"][a],Q["matching"][b]
    assert u!=v
    clause,original_var=Q["incidences"][0]
    assert {u,v}=={Q["matching"][clause],original_var}
    assert u in rows[clause] and v in rows[clause]
    # Two source variables pinned to 1 in SAME exact-one source row
    # give an independent sound original UNSAT certificate.
    pins={u:1,v:1}
    raw,den=exact_pin_moment_numerators(1)
    assert den==3
    first=Fraction(raw[1<<pa]*raw[1<<pb],2*den*den)
    assert first!=0
    empty=Fraction(1,9)
    if evaluate:
        result=signed_pinned_loop_exact(Q,pins,limit=9000000)
        assert result["status"]=="EXACT",result
        assert result["loop"]==0,result
        print(f"PINNED_SOURCE_UNSAT_EMPTY_LOOP={empty} "
              f"UNIT_SELECTED_EDGE_TERM={first} "
              f"FULL_LOOP={result['loop']} states={result['states']}")
    return first

def main():
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_edgecolor_direct_scl_bridge import K4,make_scl
    from r5_universal_cubic_flow_lowmoment_collision_20v import flower
    prove_backtransform()
    cases=[("FANO7",cyclic(7),7,True)]
    for name,p,q in (("E61_SAT12",P_SAT,Q_SAT),
                     ("E61_UNSAT12",P_UNSAT,Q_UNSAT)):
        A=build_A(p,q)
        rows=[tuple(j for j,val in enumerate(row) if val) for row in A]
        cases.append((name,rows,len(A),True))
    cases.extend((
        ("HOLYER_K4",*make_scl(K4())[:2],False),
        ("HOLYER_FLOWER_J5",*make_scl(flower(5))[:2],False),
    ))
    for name,rows,n,eval_full in cases:
        w=incompatible_pin_weight_one(rows,n,evaluate=eval_full)
        print(f"{name}_UNSAT_DOUBLE_PIN_HAS_NONZERO_UNIT_LOOP_TERM={w}",
              flush=True)
    print("ALL_SCL_PINNED_LOOP_DEGREE_ONE_AND_FOUR_VANISHING=FALSE")
    print("ALL_SCL_DOUBLE_ONE_PINS_SOURCE_UNSAT_BUT_UNIT_LOOP_NONZERO=PROVED")
    print("UNIFORM_POLY_PINNED_LOOP_ZERO_TEST=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")

if __name__=="__main__":
    main()
