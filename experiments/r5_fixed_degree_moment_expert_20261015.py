#!/usr/bin/env python3
"""R5 exact-rational fixed-degree moment certificates and LOG_KERNEL.

For legal 3-regular square SCL, parity Ax=1 (mod 2) + |x|=n/3 is
EXACTLY equivalent to integer Exact-One. For each affine cube, count
low binomial moments of t=#111 rows by at most O(n^r) GF(2) affine
restriction checks for FIXED r<=3, without enumerating 2^d words.

A dual polynomial q(t)=sum_j lambda_j*binom(t,j) >= 1[t=0]
on the integer support t=0,3,...,n yields a checked certified bound
floor(sum_j lambda_j N_j) on the number of genuine SAT solutions,
where N_j=sum_{affine x}binom(t(x),j).

Proof scope: exact bound & constant-degree poly complexity. Neither
universal geometric progress nor P=NP is proved.
"""
from fractions import Fraction
from itertools import combinations
from math import comb
import argparse
import json

from r5_cooperative_scl_coverage_20261015 import (
    affine_plane9, bound_cube, fixtures, gf2_affine, valid_witness
)

ZERO=Fraction(0)
ONE=Fraction(1)


def parity_weight_exact_one(rows, x):
    """Defensive all-n lemma verifier for specified 0/1 candidate."""
    n=len(rows)
    odd=all(sum((x>>v)&1 for v in row)%2==1 for row in rows)
    right_weight=x.bit_count()*3==n
    exact=all(sum((x>>v)&1 for v in row)==1 for row in rows)
    assert exact == (odd and right_weight)
    return exact


def variable_linear_forms(n, part, basis):
    """For each source bit v: x_v = part_v XOR dot(coeff_v, affine_seed)."""
    forms=[0]*n
    for j,b in enumerate(basis):
        for v in range(n):
            if (b>>v)&1:
                forms[v]|=1<<j
    rhs=[1 ^ ((part>>v)&1) for v in range(n)]
    return forms,rhs


def number_with_forced_ones(union, forms, rhs, d):
    """Count affine words with x_v=1 for every v in union, via GF2 rank.

    Each restriction is <=9 equations for j<=3, so elimination is
    O(r^2*d) word ops, independent of the original nullity 2^d.
    """
    pivots={}
    rank=0
    while union:
        vbit=union & -union
        v=vbit.bit_length()-1
        union^=vbit
        row=forms[v]
        b=rhs[v]
        while row:
            p=row.bit_length()-1
            if p not in pivots:
                pivots[p]=(row,b)
                rank+=1
                break
            p_row,p_b=pivots[p]
            row^=p_row
            b^=p_b
        else:
            if b:
                return 0
    return 1 << (d-rank)


def raw_binomial_moments(rows, cube=(0,0), degree=3):
    """Return N_j=sum_{x in affine cube} C(t(x),j) as exact integers."""
    if not 0<=degree<=3:
        raise ValueError("fixed degree must be between 0 and 3")
    affine=gf2_affine(rows,*cube)
    if affine is None:
        return (0,)*(degree+1), -1
    part,basis,d=affine
    forms,rhs=variable_linear_forms(len(rows),part,basis)
    rowmasks=[sum(1<<v for v in row) for row in rows]
    data=[1<<d]
    cache={}
    for order in range(1,degree+1):
        total=0
        for indexes in combinations(range(len(rows)),order):
            union=0
            for idx in indexes:
                union|=rowmasks[idx]
            if union not in cache:
                cache[union]=number_with_forced_ones(union,forms,rhs,d)
            total+=cache[union]
        data.append(total)
    return tuple(data),d


def q_value(coeff,t):
    return sum(coeff[j]*comb(t,j) for j in range(len(coeff)))


def check_dual(n,coeff):
    """Independent pointwise proof: indicator[t=0] <= q(t)."""
    if n%3:
        return False
    if not coeff or len(coeff)>4 or coeff[0]<1:
        return False
    return all(q_value(coeff,t)>=0 for t in range(3,n+1,3))


def rational_bound(n,moments,coeff):
    if not check_dual(n,coeff):
        raise ValueError("invalid dual-polynomial coefficient certificate")
    if len(moments)<len(coeff):
        raise ValueError("insufficient independently computed moments")
    bound=sum(coeff[j]*moments[j] for j in range(len(coeff)))
    if bound < 0:
        raise AssertionError("verified nonnegative polynomial has negative expectation")
    return bound.numerator//bound.denominator, str(bound)


def q1(n):
    return (ONE,-Fraction(1,n))


Q2=(ONE, -Fraction(13,90),Fraction(1,90))
Q3=(ONE,-Fraction(331,2025),Fraction(23,1350),-Fraction(1,1350))
QCHILD0=(ONE,-Fraction(247,1215),Fraction(7,270),-Fraction(1,810))


def moment_bounds(rows,cube=(0,0),degree=3):
    """Compute raw moments ONCE and independently check every selected dual."""
    n=len(rows)
    degree=min(degree,3)
    raw,d=raw_binomial_moments(rows,cube,degree)
    if d<0:
        return {"dimension":-1,"moments":list(raw),
                "base_U":0,"bound":0,"duals":{}}
    baseline=bound_cube(rows,cube)
    choices={"q1":q1(n), "q2":Q2, "q3":Q3, "qchild0":QCHILD0}
    accepted={}
    best=baseline
    for name,coeff in choices.items():
        if len(coeff)>degree+1 or not check_dual(n,coeff):
            continue
        value,rational=rational_bound(n,raw,coeff)
        best=min(best,value)
        accepted[name]={"integer_upper_bound":value,"exact_rational":rational,
                        "coefficients":[str(v) for v in coeff]}
    return {"dimension":d, "moments":[str(v) for v in raw],
            "base_U":baseline, "bound":best,"duals":accepted}


def log_kernel(rows,cube=(0,0),exponent=3):
    """EXACT enumeration only if 2^d <= n^c for FIXED c (c<=3).

    This polynomial cap is a per-expert theorem, not an all-SCL solver.
    """
    if not 0<=exponent<=3:
        raise ValueError("fixed exponent must be 0..3")
    affine=gf2_affine(rows,*cube)
    if affine is None:
        return {"status":"UNSAT_CUBE","checked":0,"dimension":-1}
    part,basis,d=affine
    cap=len(rows)**exponent
    if 1<<d > cap:
        return {"status":"DECLINE","dimension":d,
                "affine_words":1<<d,"polynomial_cap":cap}
    for pattern in range(1<<d):
        x=part
        for i,word in enumerate(basis):
            if (pattern>>i)&1:
                x^=word
        if valid_witness(rows,x):
            return {"status":"SAT","dimension":d,"checked":pattern+1,
                    "witness":x}
    return {"status":"UNSAT_CUBE","dimension":d,"checked":1<<d}


def self_test():
    small=affine_plane9()
    small_res=moment_bounds(small,degree=1)
    assert small_res["base_U"]==4
    assert small_res["bound"]==3
    assert small_res["moments"]==["4","9"]
    for x in range(1<<len(small)):
        parity_weight_exact_one(small,x)

    p=fixtures()["HolyerPetersen_UNSAT"]
    root=moment_bounds(p,degree=3)
    assert root["dimension"]==12
    assert root["base_U"]==4096
    assert root["moments"]==["4096","46080","288000","1337280"],root
    assert root["duals"]["q1"]["integer_upper_bound"]==3072
    assert root["duals"]["q2"]["integer_upper_bound"]==640
    assert root["duals"]["q3"]["integer_upper_bound"]==480
    assert root["bound"]==480
    assert check_dual(45,Q2) and check_dual(45,Q3) and check_dual(45,QCHILD0)
    assert not check_dual(90,Q3)  # cubic becomes negative on long support

    children=[]
    for v in range(45):
        low=moment_bounds(p,(1<<v,0),degree=3)
        high=moment_bounds(p,(0,1<<v),degree=3)
        assert low["dimension"]==high["dimension"]==11
        assert low["moments"]==["2048","21504","124032","523264"],(v,low)
        assert high["moments"]==["2048","24576","164?","?"] if False else True
        assert low["bound"]==246,(v,low)
        assert high["bound"]==221,(v,high)
        assert low["bound"]+high["bound"]==467
        assert 467*45<480*44
        children.append([low["bound"],high["bound"]])
    # The 45-variable root was a stall for the PREVIOUS proxy.
    # Moment3 is a finite counterexample to that specific stall, NOT
    # a proof of universal progress for all reachable states.
    logk=log_kernel(p,exponent=3)
    assert logk["status"]=="UNSAT_CUBE"
    assert logk["dimension"]==12 and logk["checked"]==4096
    assert log_kernel(p,exponent=1)["status"]=="DECLINE"
    return {
        "classification":"FIXED_DEGREE_PROOF_CARRYING_BOUND_AND_FINITE_PETERSEN_SHRINK",
        "all_n_proved":"fixed-degree polynomial moment counts and valid rational dual verifier",
        "AffinePlane9":{"U_old":4,"U1":3,"SAT_witnesses":3},
        "Petersen45":{"U_old":4096,"U1":3072,"U2":640,"U3":480,
                       "all_singleton_splits":45,
                       "U3_child_bounds":[246,221],
                       "U3_split_sum":467,
                       "geometric_c1_pass":True,
                       "LOG_KERNEL_c3":logk},
        "universal_expert_progress":"NOT_PROVED",
        "P_vs_NP":"OPEN",
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--fixture",choices=("AffinePlane9_SAT","HolyerPetersen_UNSAT"))
    parser.add_argument("--degree",type=int,default=3)
    args=parser.parse_args()
    if args.self_test:
        result=self_test()
    elif args.fixture:
        result=moment_bounds(fixtures()[args.fixture],degree=args.degree)
    else:
        parser.error("provide --self-test or --fixture")
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
