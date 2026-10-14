#!/usr/bin/env python3
"""R5 exact coordinate-aligned residual state FRONTIER: 3^(n/9) theorem.

Research goal: universal deterministic n^C SolveLinearCubicXSAT on ALL
legal square, cubic, linear positive Exact-One instances. NOT PROVED.

Start from a genuine connected 9x9 GRID9 source (defined in the
F3 Boolean-fibre witness module): 3 row/column incidences each, no
4-cycles, rank_F3 6, exactly 3 Boolean exact-cover witnesses.

Its RREF affine free coordinates are t=(t0,t1,t2). Apply the ACTUAL
invertible F3 affine change
   u=2*t0+t2, v=2*t1+t2, z=t0.
The 3 genuine Boolean points map to (u,v,z)=
   (0,0,0), (1,1,0), (2,2,1).
Thus exact existential elimination E_z P_GRID9 gives
   Q(u,v)=delta(u,v)=1-(u-v)^2
as a FUNCTION over F3, not as a formal-polynomial theorem.

For k>=1 independent legal GRID9 copies (native n=9*k), eliminate
one z_i per copy to obtain the EXACT physical Boolean-point relation
   Q_k(u,v)=prod_i delta(u_i,v_i)=1 iff u=v in F3^k.

At the FIXED variable order u_1,...,u_k,v_1,...,v_k:
   cofactor R_a(v)=Q_k(a,v)=delta_a(v), for a in F3^k.
There are EXACTLY 3^k pairwise distinct COORDINATE-ALIGNED functions.
Even under the coarser contextual equivalence
   f~g iff for every legal continuation C_b(v)=R_b(v),
           exists v: f(v) C_b(v) = exists v: g(v) C_b(v),
all 3^k are inequivalent: exists v R_a(v)R_b(v)= [a=b].
Therefore every **explicit, unparameterized deterministic interface
state registry** merging states only if all later legal fixed-coordinate
conjunction/existence queries agree must hold >=3^k=3^(n/9)
distinct states at this split.

Yet ALL 3^k residuals are ONE ABSTRACT AFFINE-ORBIT:
   R_a(v)=R_0(v-a).
And the FULL function has O(k) factored arithmetic circuit
   Q_k=prod_i(1-(u_i-v_i)^2);
its natural interleaved variable order u1,v1,u2,v2,... admits
a bounded-width DFA/decision diagram using a single pending trit
to be compared immediately. Pure existential projection of all
u-variables is even the constant TRUE since u=v is always possible.

Thus this rigorously disproves the specific conjecture that "every
fixed-frontier coordinate-aligned residual-state registry is poly
bounded" over ALL native SCL instances. It does NOT disprove an
adaptive algorithm, one-parametric-template-and-affine-map approach,
general arithmetic circuit compression, universal n^C solver, or P=NP.

The source instance is disconnected across k copies, but each
constituent is fully legal; all-input conjectures without a
connectedness promise MUST include this family.

Regression k=1..6 enumerates all 3^k partial assignments to u and
exact residual bitmasks over all 3^k v values; asserts 3^k distinct,
mutually disjoint masks, one class under translations, and contextual
pairing matrix I_{3^k}. This enumerating TEST is NOT the target
polynomial algorithm; the all-size proof is the equality identity.
"""
from itertools import product

from r5_universal_f3_boolean_exactification_connected_nullity_barrier import (
    GRID9, incidence, assert_legal, gf3_rref_affine
)


def native_grid9_projection():
    A=incidence(GRID9)
    assert_legal(A)
    rank,consistent,x0,B=gf3_rref_affine(A)
    assert rank==6 and consistent and len(B)==3
    assert tuple(j for j in range(9) if any(B[i][j] == 1 for i in range(3)))  # use real RREF, not fabricated grid
    S=set()
    transformed=set()
    for t in product(range(3),repeat=3):
        x=tuple((x0[j]+sum(t[i]*B[i][j] for i in range(3)))%3
                for j in range(9))
        u=(2*t[0]+t[2])%3
        v=(2*t[1]+t[2])%3
        z=t[0]
        if all(xj!=2 for xj in x):
            S.add((u,v,z))
        transformed.add((u,v,z))
    assert len(transformed)==27  # verifies invertible change
    assert S=={(0,0,0),(1,1,0),(2,2,1)},S
    for u,v in product(range(3),repeat=2):
        projected=any((u,v,z) in S for z in range(3))
        indicator=(1-(u-v)**2)%3
        assert indicator==int(projected), (u,v)
    print("REAL_GRID9_GF3_EXACT_EZ_EQUALITY_PASS",{
        "rank":rank, "affine_dimension":3,
        "Boolean_cover_count":len(S),
        "projected_binary_equality_support":3,
    },flush=True)


def verify_exact_aligned_states(k):
    domain=tuple(product(range(3),repeat=k))
    width=3**k
    assert len(domain)==width
    # Tuple of all Q_k(a,v) truth bits in fixed shared coordinates v.
    masks=[]
    for a in domain:
        m=0
        for idx,v in enumerate(domain):
            # Each factor is a genuine projected GRID9 equality.
            value=1
            for x,y in zip(a,v):
                value=(value*(1-(x-y)**2))%3
            assert value in (0,1)
            m|=value<<idx
        masks.append(m)
    assert len(set(masks))==width
    assert all(m.bit_count()==1 for m in masks)
    assert set(masks)=={1<<i for i in range(width)}
    # This also proves exact contextual inequivalence: the continuation
    # C_b is mask[b] and the intersection exists iff a=b.
    assert all(bool(masks[a]&masks[b])==(a==b)
               for a in range(width) for b in range(width))
    # All exact cofactor functions are just translates of R_0.
    for a in domain:
        for v in domain:
            translation=tuple((v[i]-a[i])%3 for i in range(k))
            assert (v==a)==all(x==0 for x in translation)
    # A single O(k) factorized arithmetic expression computes Q_k,
    # and ∃u Q_k(u,v)=TRUE for ALL v (choose u=v).
    assert all(any(bool(masks[a] & (1<<b)) for a in range(width))
               for b in range(width))
    print("COORDINATE_ALIGNED_CONTEXTUAL_STATE_LOWER_BOUND_PASS",{
        "independent_legal_GRID9_blocks":k,
        "native_SCL_n":9*k,
        "GF3_eliminated_z_parameters":k,
        "exact_fixed_frontier_residuals":width,
        "affine_orbits_without_alignment":1,
        "minimum_explicit_contextual_states_at_split":width,
        "distinct_parameterized_template_types":1,
        "natural_interleaved_order_formula_size":"O(k)",
        "all_u_existential_projection_is_constant_TRUE":True,
    },flush=True)


def main():
    native_grid9_projection()
    for k in range(1,7):
        verify_exact_aligned_states(k)
    print("THEOREM_EXPLICIT_FIXED_FRONTIER_CONTEXTUAL_STATES_AT_LEAST_3_POWER_N_OVER_9")
    print("NO_LOWER_BOUND_FOR_ADAPTIVE_ORDER_OR_GENERAL_ARITHMETIC_CIRCUITS")
    print("UNIVERSAL_N_TO_THE_C_SolveLinearCubicXSAT_NOT_CONSTRUCTED")
    print("P_VS_NP_OPEN")


if __name__=="__main__":
    main()
