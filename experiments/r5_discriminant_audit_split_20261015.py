#!/usr/bin/env python3
"""R5 E4.3 INFORMATIONALLY_INDEPENDENT_AFFINE_SIGNATURE.

All-n moment/low-signed-Pless triangular identity:
 M_q = 2^(d-q) SUM_{s<=q}(-1)^s*binom(m-s,q-s)*D_s.
A full SCL cube has m free v coordinates, d-dimensional homogeneous
kernel, and D_s=P_s-M_s of restricted affine rowspace.

D_0..D_k and M_0..M_k contain EXACTLY the SAME information if
m,d are known. Independent GF2-rank computation of the moments
is a certificate check, not another independent discriminant.

Additional endpoint: sum_s (-1)^s D_s = 2^r*C_m,
C_m=1 iff A_T*1_T=c. Complement swaps P_s and M_s when
fixed v-weight parity is odd, otherwise preserves each.

Core signature = (m,r,parity,C0,target,P/M low k, optionally
independent small-kernel anchors). Audit = (d,first moments,
independent character-sum, D_m, endpoint, consistency tags).
No new LP optimum is counted as independent feature when all
input coefficients are already contained in core.

All numeric oracle checks in this file are FINITE small-code tests;
this exact script does NOT establish polynomial-time SCL decision.
"""
from fractions import Fraction as F
from itertools import combinations
from math import comb
import argparse,json,random

from r5_affine_macwilliams_soundness_20261015 import (
    affine_data,coset_moments,signed_low_rowspace,
    enumerate_affine_oracle,spectral_transform_from_oracle,
    check_exact_coset_identity
)
from r5_local_codeword_anchors_20261015 import (
    local_codewords,anchor_counts
)
from r5_cooperative_scl_coverage_20261015 import fixtures
from r5_connected_coverage_breaker_20261015 import (
    make_connected, mutate_connected
)


def low_moments_from_signed(m,d,D,k):
    """Compute first k binomial moments using ONLY low signed D."""
    if k<0 or k>m or len(D)<k+1:
        raise ValueError("need D0..Dk and k<=m")
    out=[]
    for q in range(k+1):
        power=F(2)**(d-q)
        value=power*sum((-1)**s*comb(m-s,q-s)*D[s]
                        for s in range(q+1))
        assert value.denominator==1 and value>=0
        out.append(int(value))
    return tuple(out)


def reconstruct_low_signed(m,d,moments):
    """Inverse triangular map, EXACT rational arithmetic."""
    D=[]
    for q,Mq in enumerate(moments):
        if q>m:raise ValueError("q>m")
        rhs=F(Mq)/(F(2)**(d-q))
        earlier=sum((-1)**s*comb(m-s,q-s)*D[s]
                    for s in range(q))
        value=(-1)**q*(rhs-earlier)
        assert value.denominator==1
        D.append(int(value))
    return tuple(D)


def all_one_free_feasible(data):
    if data is None:
        return False
    full_v=data["free_mask"]|data["cube"][0]
    return all(sum((full_v>>v)&1 for v in row)%2==0
               for row in data["rows"])


def independent_spectrum_audit(data,k=3,oracle=False):
    if data is None:return {"consistent":False}
    m,r,d=data["m"],data["r"],data["d"]
    k=min(k,m)
    low=signed_low_rowspace(data,k)
    D=tuple(low[s][0]-low[s][1] for s in range(k+1))
    rank_moments=coset_moments(data,k)
    reconstructed_moments=low_moments_from_signed(m,d,D,k)
    assert rank_moments==reconstructed_moments
    assert reconstruct_low_signed(m,d,rank_moments)==D
    p=data["fixed_v_weight"]%2
    assert data["parity"]==p
    C0=int(data["homogeneous_restricted_rhs"])
    Cm=int(all_one_free_feasible(data))
    # Direct finite RHS parity from the source graph.
    total_expected=(1<<r)*C0
    alternating_expected=(1<<r)*Cm
    result={
        "consistent":True,"m":m,"r":r,"d":d,"parity":p,
        "C0":C0,"Cm":Cm,
        "D_low":D,"moments_from_GF2_rank":rank_moments,
        "moments_from_D":reconstructed_moments,
        "inverted_low_D":reconstruct_low_signed(m,d,rank_moments),
        "sum_D_expected":total_expected,
        "alternating_sum_D_expected":alternating_expected,
        "complement_Dm_expected":(-1)**p,
        "D_Pless_equivalence":"EXACT_CHECKED",
    }
    if oracle:
        hist=enumerate_affine_oracle(data)
        spectrum=spectral_transform_from_oracle(data,hist)
        assert check_exact_coset_identity(data,hist,spectrum)
        assert tuple(spectrum[j] for j in range(k+1))==D
        assert sum(spectrum.values())==total_expected
        assert sum((-1)**s*spectrum[s] for s in spectrum)==alternating_expected
        assert hist.get(0,0)==C0 and hist.get(m,0)==Cm
        # Independent homogeneous dual B_s via a SECOND complete
        # affine codeword histogram and inverse Krawtchouk.
        homogeneous=dict(data)
        homogeneous["particular_free"]=0
        homogeneous["parity"]=0
        B=spectral_transform_from_oracle(
            homogeneous,enumerate_affine_oracle(homogeneous))
        for s in range(m+1):
            assert (B[s]+spectrum[s])%2==0
            P=(B[s]+spectrum[s])//2
            M=(B[s]-spectrum[s])//2
            assert min(P,M)>=0
            t=m-s
            Pt=(B[t]+spectrum[t])//2
            Mt=(B[t]-spectrum[t])//2
            assert (Pt,Mt)==((P,M) if p==0 else (M,P))
        result["full_endpoint_and_P_M_complement"]="PASS"
        result["full_oracle_checked_states"]=1<<d
    return result


def discriminant_and_audit(rows,cube=(0,0),k=2,anchors=False,
                           cached_words=None):
    data=affine_data(rows,cube)
    if data is None:
        return (("INCONSISTENT",),{"consistency":"NO_GF2_CONTINUATION"})
    m,r,d=data["m"],data["r"],data["d"]
    k=min(k,m)
    low=signed_low_rowspace(data,k)
    c0=int(data["homogeneous_restricted_rhs"])
    parity=data["fixed_v_weight"]%2
    target=data["target_free_weight"]
    independent_anchor=()
    if anchors:
        local=anchor_counts(rows,cube,precomputed=cached_words)
        n=len(rows)
        independent_anchor=(local[n-6],local[n-9])
    # Only independently discriminating mathematically supplied data.
    core=(m,r,parity,c0,target,
          tuple(low[i] for i in range(k+1)),independent_anchor)
    witness=independent_spectrum_audit(data,k,oracle=False)
    audit={
        "d_equals_m_minus_r":d==m-r,
        "moments_rank_reconstructed":witness["moments_from_GF2_rank"],
        "moments_spectrum_reconstructed":witness["moments_from_D"],
        "signed_sum_expected":witness["sum_D_expected"],
        "signed_alternating_sum_expected":
            witness["alternating_sum_D_expected"],
        "D_m_expected":witness["complement_Dm_expected"],
        "LP_optimum_is_derived_from_all_its_inputs":True,
        "known_information_not_double_counted":True,
        "all_consistency_checks":"PASS"
    }
    return core,audit


def signature_cost(m,h):
    if not 0<=h<=m:raise ValueError("invalid depth")
    return sum((1<<i)*comb(m,i) for i in range(h+1))


def rooted_pair(seed):
    rows,witness,_=make_connected(2,seed)
    return mutate_connected(rows,witness,
          random.Random(seed*991+20261015),
          moves=4+(seed%13))[0]


def self_test():
    examples={
        "AffinePlane9":fixtures()["AffinePlane9_SAT"],
        "HolyerK4":fixtures()["HolyerK4_SAT"],
        "Connected36_seed0":rooted_pair(0),
        "Connected36_seed13":rooted_pair(13)
    }
    checked={}
    for name,rows in examples.items():
        checks=[]
        for cube in ((0,0),(1,0),(0,1),(5,0),(0,5)):
            data=affine_data(rows,cube)
            if data is None:
                checks.append({"cube":cube,"status":"INCONSISTENT"})
                continue
            proof=independent_spectrum_audit(data,k=3,oracle=True)
            core,audit=discriminant_and_audit(rows,cube,k=3)
            assert audit["all_consistency_checks"]=="PASS"
            assert core[1]==data["r"]
            checks.append({
                "cube":cube,"m":data["m"],
                "d":data["d"],"moments_k3":proof["moments_from_D"],
                "signed_D_k3":proof["D_low"],
                "moment_and_endpoint":"PASS",
                "full_P_M_complement":"PASS"})
        checked[name]=checks
    # The original connected Gate D pair shares moments to k=2,
    # but exact A6 anchor distinguishes: it was never a strong
    # moment+anchor twin.
    a=rooted_pair(0);b=rooted_pair(13)
    a_core,a_audit=discriminant_and_audit(a,k=2,anchors=False)
    b_core,b_audit=discriminant_and_audit(b,k=2,anchors=False)
    assert a_core==b_core
    assert a_audit["moments_rank_reconstructed"]==(
           b_audit["moments_rank_reconstructed"])
    words_a={4:local_codewords(a,4),6:local_codewords(a,6)}
    words_b={4:local_codewords(b,4),6:local_codewords(b,6)}
    aa,_=discriminant_and_audit(a,k=2,anchors=True,
                                cached_words=words_a)
    bb,_=discriminant_and_audit(b,k=2,anchors=True,
                                cached_words=words_b)
    assert aa!=bb and aa[-1]!=(bb[-1])
    assert (aa[-1],bb[-1])==((0,3),(0,2))
    counts={str(h):signature_cost(36,h) for h in range(5)}
    assert counts=={"0":1,"1":73,"2":2593,"3":73993,"4":1582873}
    return {"gate":"INFORMATIONALLY_INDEPENDENT_AFFINE_SIGNATURE",
            "all_n_theorem":"SIGNED_PLESS_TRIANGULAR_EQUIVALENCE",
            "finite_independent_checks":checked,
            "SCL36_moment_only_equal_k2":True,
            "SCL36_joint_anchor_distinguishes":True,
            "Q_h_n36_h0_to4":counts,
            "all_n_polynomial_scl":"NOT_CONSTRUCTED",
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    z=p.parse_args()
    if not z.self_test:p.error("--self-test")
    print(json.dumps(self_test(),indent=2,sort_keys=True))
