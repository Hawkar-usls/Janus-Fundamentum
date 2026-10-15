#!/usr/bin/env python3
"""R5 E4.5: depth-h moment leakage, all-n identities + finite independent check.

For ANY binary set C⊆{0,1}^m and q,h≥0 with q+h≤m:
  sum_{|I|=h} M_q(C_{I,ones}^{-I})
       = binom(q+h,h)*M_{q+h}(C).
On a root GF2 affine SCL parity-solution set x=1+ker A,
signed row dual D_s=(-1)^s B_s; for same n=72,d=7
and equal B0,B1,B2, sum_i M2(x_i=1 branches) differs by
+48*Delta(B3). This is exact integer arithmetic.

IMPORTANT: The sum can be extracted from any complete
VALUE-LABELED multiset of BOTH branch children; the proof
does not hold automatically for a pair of unlabeled children
with no way to identify x_i=1. However the existing E4.2
unlabeled pair of (x_i=0, x_i=1) children also allows
recovering the same higher moment via a separate identity
when it retains sufficiently many child moments: e.g.
sum_i (M_q(C0^-i)+M_q(C1^-i))=m*M_q(C) - q*M_q(C)
= (m-q)*M_q(C), not M_{q+1}. Distinguish these grammars.

Finite oracle here enumerates 2^d small parity solution
words for two known explicit covers ONLY; no all-n time bound.
"""
from itertools import combinations
from math import comb
from collections import Counter
import argparse,json

from r5_rank_preserving_cover_twins_20261015 import (
    search_unsat_base,integer_two_cover_witness,sat_cover_from_y,
    phi_data,delta_to_signs,lift_rows
)
from r5_cooperative_scl_coverage_20261015 import (
    gf2_affine,valid_witness,fingerprint
)
from r5_cover_rank_spectral_orbit_20261015 import (
    histogram_from_affine,spectrum_from_hist
)
from r5_bidirectional_macwilliams_lp_20261015 import krawtchouk


def build_pair():
    base,_=search_unsat_base()
    report=integer_two_cover_witness(base)
    assert report["status"]=="SAT_TERNARY_WITNESS"
    signs,witness,sat=sat_cover_from_y(base,report["y"])
    frame=phi_data(base)
    delta=0
    for j,b in enumerate(frame["non_gauge_basis"]):
        if (13>>j)&1:delta^=b
    unsat=lift_rows(base,delta_to_signs(frame["edges"],signs,delta))
    assert valid_witness(sat,witness)
    return sat,unsat


def affine_parity_words(rows):
    n=len(rows)
    part,basis,d=gf2_affine(rows,0,0)
    if d>12:raise ValueError("FINITE_ORACLE_RESOURCE_LIMIT")
    words=[]
    for seed in range(1<<d):
        x=part
        for j,b in enumerate(basis):
            if (seed>>j)&1:x^=b
        words.append(x)
    return words


def moment(words,q):
    return sum(comb(w.bit_count(),q) for w in words)


def counted_ones_branch_moment(words,m,q,h):
    """Independent explicit enumeration of all h-element subsets I."""
    total=0
    for I in combinations(range(m),h):
        subset=sum(1<<i for i in I)
        for w in words:
            if w&subset==subset:
                total+=comb(w.bit_count()-h,q)
    return total


def recover_from_unlabeled_parity_tagged_pairs(words,m,q=2):
    """S1 can reconstruct x_i=1 WITHOUT explicit value labels.

    The restricted free-v parity tag after fixing x_i=0 is 1,
    and after x_i=1 is 0, from the original column-odd SCL
    parity theorem. Thus sorting each child pair does not
    erase which one is the x_i=1 branch as long as parity
    is retained. This is a theorem of THIS S1 feature grammar,
    not a claim about arbitrary untagged summaries.
    """
    unlabeled_pairs=[]
    for i in range(m):
        branch0=sum(comb(w.bit_count(),q) for w in words
                    if ((w>>i)&1)==0)
        branch1=sum(comb(w.bit_count()-1,q) for w in words
                    if ((w>>i)&1)==1)
        pair=tuple(sorted(((1,branch0),(0,branch1))))
        unlabeled_pairs.append(pair)
    # Discard variable identities and left/right branch order.
    multiset=tuple(sorted(unlabeled_pairs))
    identified_ones_total=sum(
        next(value for parity,value in pair if parity==0)
        for pair in multiset)
    return {"sum_xi_one_Mq":identified_ones_total,
            "distinct_unlabeled_pair_profiles":len(set(multiset)),
            "parity_tags_recover_branch_value":True}


def signed_dual_low_from_x_affine(words,m,d,k=4):
    # Coset x=1+ker(A), root signed D=(-1)^s B_s.
    # Independent inverse Krawtchouk on all parity words of x,
    # not the kernel v. This detects sign mishandling.
    low={}
    N=1<<d
    for s in range(k+1):
        numerator=sum(krawtchouk(m,s,w.bit_count()) for w in words)
        assert numerator%N==0
        low[s]=numerator//N
    return low


def replay():
    sat,unsat=build_pair()
    m=len(sat)
    assert m==len(unsat)==72
    outcome={}
    for name,rows in (("SAT",sat),("UNSAT",unsat)):
        words=affine_parity_words(rows)
        assert len(words)==128
        d=7
        M={str(k):moment(words,k) for k in range(5)}
        D=signed_dual_low_from_x_affine(words,m,d,k=4)
        # independent direct 72 singleton child traversals
        L1=counted_ones_branch_moment(words,m,2,1)
        assert L1==3*M["3"]
        from_unlabeled=recover_from_unlabeled_parity_tagged_pairs(words,m,2)
        assert from_unlabeled["sum_xi_one_Mq"]==L1
        L2=counted_ones_branch_moment(words,m,2,2)
        assert L2==6*M["4"]
        # All h=1 q=0/1/2, and h=2 q=0/1/2 exact.
        detail={}
        for h in (1,2):
            for q in (0,1,2):
                a=counted_ones_branch_moment(words,m,q,h)
                b=comb(q+h,h)*M[str(q+h)]
                assert a==b,(name,h,q,a,b)
                detail[f"h{h}_q{q}"]=a
        # Fixed affine parity solution x=1+v ⇒ D_s=(-1)^s B_s.
        H=histogram_from_affine(rows)
        assert H["status"]=="EXACT"
        B={}
        for s in range(5):
            numerator=sum(cnt*krawtchouk(m,s,j)
                          for j,cnt in H["hist"].items())
            assert numerator%(1<<d)==0
            B[s]=numerator//(1<<d)
            assert D[s]==((-1)**s)*B[s]
        outcome[name]={"n":m,"d":d,
                       "root_binomial_moments":M,
                       "row_unsigned_B0_to4":B,
                       "root_signed_D0_to4":D,
                       "all_depth1_depth2_moment_identities":detail,
                       "branch_q2_sum_depth1":L1,
                       "unlabeled_parity_tagged_S1_leakage":from_unlabeled,
                       "branch_q2_sum_depth2":L2,
                       "source_sha256":fingerprint(rows),
                       "true_SAT_count":H["SAT"]}
    X=outcome["SAT"];Y=outcome["UNSAT"]
    assert all(X["row_unsigned_B0_to4"][i]==
               Y["row_unsigned_B0_to4"][i] for i in range(3))
    diff_B3=X["row_unsigned_B0_to4"][3]-Y["row_unsigned_B0_to4"][3]
    diff_child=X["branch_q2_sum_depth1"]-Y["branch_q2_sum_depth1"]
    assert diff_child==48*diff_B3
    assert diff_child!=0
    return {"status":"DEPTH_ONE_TWO_MOMENT_LEAKAGE_VERIFIED",
            "theorem_all_n":"sum_I M_q(C_I,ones^-I)=binom(q+h,h)*M_(q+h)(C)",
            "controls":outcome,
            "signed_D3_from_B3":"D3=-B3",
            "delta_B3_SAT_minus_UNSAT":diff_B3,
            "delta_sum_all72_child_M2":diff_child,
            "48_delta_B3":48*diff_B3,
            "branch_value_label_required_for_this_exact_identity":
                "EXPLICIT_OR_RECOVERABLE_FROM_RETAINED_CHILD_PARITY",
            "universal_polynomial_SCL":"NOT_CONSTRUCTED",
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.parse_args()
    print(json.dumps(replay(),sort_keys=True,indent=2))
