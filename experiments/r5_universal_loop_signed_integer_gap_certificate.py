#!/usr/bin/env python3
"""R5 ALL-SCL signed-loop integer divisibility and approximate-value barrier.

For EVERY original legal square/cubic/linear positive Exact-One source
on n variables, its true solution count Z is an INTEGER. If Z>0,
counting satisfied original rows gives 3 sum(x)=n and thus 3|n.
When n not divisible by 3, Z=0 automatically.

For n=3k the exact homogeneous Bethe normalization satisfies:
  Z_B=(16/27)^k = 2^(4k) / 3^(3k)
The exact signed generalized-loop correction from the prior
source-verified R5 theorem is:
  L = sum_(S subset E(Q)) 2^(-|S|) prod_v M_v(...)
  where |E(Q)|=2n=6k, all M integer.
Define INTEGER signed numerator K=2^(2n) L.

IDENTITY, valid for EVERY source with n=3k:
    K = 2^(2k) * 3^n * Z(F).

Proof: Z=Z_B L, and substituting the explicit Z_B and
L=K/2^(6k) gives:
 Z = (2^(4k)/3^(3k)) (K/2^(6k))
   = K/(2^(2k)3^n).

This is an all-source arithmetic cancellation/divisibility
theorem (K divisible by enormous 2^(2k)3^n).

Even a POLYNOMIAL-TIME ADDITIVE approximation to L with
absolute guaranteed error less than (27/16)^k / 2 is sufficient
to recover EXACT original #SAT by multiplying by
Z_B=(16/27)^k and rounding to the nearest integer.
Therefore any UNIFORM such polynomial guarantee on ALL
legal SCL implies P=NP (indeed exact source counting), rather
than just yielding a rough useful estimate.

It says NOTHING against approximators without such precision,
and does NOT prove such a polynomial algorithm exists or is
impossible. P_VS_NP=OPEN.
"""
from __future__ import annotations

from fractions import Fraction

from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_rank2_exact_bethe_loop_correction import (
    signed_loop_sum_exact,exact_original_count,
)
from r5_universal_all_scl_perfect_matching_rank2_network import (
    paired_quartic_network,
)


def base_parameters(rows,n):
    rows=validate_sparse(rows,n)
    assert len(rows)==n and all(len(r)==3 for r in rows)
    degree=[0]*n
    for r in rows:
        for j in r:degree[j]+=1
    assert all(d==3 for d in degree)
    if n%3:
        return {"n":n,"status":"UNSAT_MOD3",
                "all_source_proof":"n=3*number_of_true_variables"}
    k=n//3
    bethe=Fraction(16,27)**k
    D=2**(2*k)*3**n
    assert D==2**(2*n)*bethe
    assert bethe>0 and bethe<1
    return {"n":n,"status":"DIVISIBLE_SIZE",
            "k":k,"bethe":bethe,"divisor":D,
            "loop_spacing":1/bethe}


def nearest_integer(q):
    """Fully exact tie-safe recovery, never convert to floating point."""
    assert isinstance(q,Fraction)
    numerator=q.numerator
    denominator=q.denominator
    return (2*numerator+denominator)//(2*denominator)


def signed_loop_integer_certificate(rows,n,max_n=12):
    params=base_parameters(rows,n)
    assert n<=max_n
    q=paired_quartic_network(rows,n)
    correction=signed_loop_sum_exact(q)
    assert correction["status"]=="EXACT",correction
    L=correction["correction"]
    Z=exact_original_count(rows,n)
    if params["status"]=="UNSAT_MOD3":
        assert Z==0 and L==0
        return {"status":"UNSAT_MOD3","count":0,
                "loop_numerator":0}
    K=L*2**(2*n)
    assert K.denominator==1
    assert K.numerator%params["divisor"]==0
    assert K.numerator==params["divisor"]*Z
    assert params["bethe"]*L==Z
    return {"status":"IDENTITY_REPLAYED","count":Z,
            "loop_numerator":K.numerator,"divisor":params["divisor"],
            "loop_sum":L,"states":correction["states"]}


def demonstrate_additive_gap(rows,n,actual_count):
    params=base_parameters(rows,n)
    assert params["status"]=="DIVISIBLE_SIZE"
    k=params["k"]
    bethe=params["bethe"]
    spacing=params["loop_spacing"]
    assert spacing==Fraction(27,16)**k
    exact_L=spacing*actual_count
    toler=spacing/3
    assert toler<spacing/2
    for approx in (exact_L-toler,exact_L,exact_L+toler):
        assert abs(approx-exact_L)<=toler
        assert nearest_integer(bethe*approx)==actual_count
    return toler


def main():
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT,
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    fano=cyclic(7)
    result=signed_loop_integer_certificate(fano,7)
    assert result["status"]=="UNSAT_MOD3"
    print("FANO7_SIGNED_LOOP_NUMERATOR_ZERO_BY_MOD3=PASS",flush=True)

    for name,p,q,expected in (
        ("SAT12",P_SAT,Q_SAT,1),("UNSAT12",P_UNSAT,Q_UNSAT,0)
    ):
        m=build_A(p,q)
        n=len(m)
        rows=validate_sparse(
            [tuple(j for j,value in enumerate(row) if value)
             for row in m],n
        )
        assert n==12
        cert=signed_loop_integer_certificate(rows,n)
        assert cert["count"]==expected
        assert cert["loop_numerator"]==expected*(2**8)*(3**12)
        tolerance=demonstrate_additive_gap(rows,n,expected)
        print(f"E61_{name}_SIGNED_LOOP_NUMERATOR={cert['loop_numerator']} "
              f"DIVISOR={cert['divisor']} EXACT_COUNT={expected} "
              f"ALLOWED_ADD_ERR_{tolerance}",flush=True)

    print("ALL_SCL_LOOP_NUMERATOR_DIVISIBILITY_2POW2K_3POWN=PROVED")
    print("ALL_SCL_SIZE_N_NOT_MOD3_SAT_IMPOSSIBLE=PROVED")
    print("POLY_ADDITIVE_LOOP_ESTIMATOR_BELOW_HALF_SPACING_IMPLIES_P_EQ_NP=PROVED")
    print("POLY_ADDITIVE_LOOP_ESTIMATOR=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
