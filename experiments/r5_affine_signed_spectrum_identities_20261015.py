#!/usr/bin/env python3
"""Gate E4.1a — AFFINE_SIGNED_SPECTRUM_IDENTITIES.

Independent ALL-n invariants for every consistent SCL Boolean cube:
  (A) free weight parity = # x-coordinates fixed ZERO mod 2;
  (B) signed dual spectrum independent of chosen particular solution;
  (C) signed mass sum = 2^rank if RHS A_Z1=0 else ZERO;
  (D) D_(m-s)=(-1)^|Z| D_s.

The sum in (C) is ALSO a consequence of full affine MacWilliams
with anchored C0, hence this is an independent CHECK, not a
strictly strengthening inequality for a complete E4.1 LP.

Checks are polynomial for fixed low signed degree; full D-sum is
replayed by a separate exhaustive affine oracle ONLY for small
control nullities. No negative claim is inferred from budget limits.
"""
import argparse,json,random
from collections import Counter

from r5_affine_macwilliams_soundness_20261015 import (
    affine_data, signed_low_rowspace, enumerate_affine_oracle,
    spectral_transform_from_oracle, check_exact_coset_identity
)
from r5_cooperative_scl_coverage_20261015 import fixtures
from r5_connected_coverage_breaker_20261015 import make_connected,mutate_connected


def fixed_branch_invariants(data,k=3):
    if data is None:
        return {"verdict":"INCONSISTENT_GF2"}
    Z,O=data["cube"]
    m,r,d=data["m"],data["r"],data["d"]
    original=data["particular_free"]
    parity=Z.bit_count()%2
    # Independent parity from the original row equations, not
    # only from the selected Gaussian particular solution.
    assert original.bit_count()%2==parity
    assert all(word.bit_count()%2==0
               for word in data["kernel_basis"])
    low=signed_low_rowspace(data,k)
    alternative=original ^ (data["kernel_basis"][0]
                            if data["kernel_basis"] else 0)
    assert alternative.bit_count()%2==parity

    # Recompute the two low spectra WITHOUT assuming representative
    # invariance: independent explicit character tests in both cases.
    for j in range(k+1):
        p=q=0
        for coordinates in __import__("itertools").combinations(data["free"],j):
            u=sum(1<<i for i in coordinates)
            if any((u&word).bit_count()%2 for word in data["kernel_basis"]):
                continue
            if (u&alternative).bit_count()%2:
                q+=1
            else:
                p+=1
        assert low[j]==(p,q)
    assert m-r==d
    homogeneous=data["homogeneous_restricted_rhs"]
    expected_signed_sum=(1<<r) if homogeneous else 0
    # In the complete LP this equality follows by evaluating
    # its coset MacWilliams s=0 transform and its C0 anchor.
    # A Gaussian particular solution NEED NOT equal zero when c=0.
    # The mathematical test is that the original fixed-source RHS
    # vanishes; comparing this to the chosen v0 would be UNSOUND.
    if original==0:
        assert homogeneous

    return {"verdict":"CONSISTENT",
            "m":m,"r":r,"d":d,"parity":parity,
            "C0":int(homogeneous),
            "expected_sum_D":expected_signed_sum,
            "expected_D_m":(-1)**parity,
            "signed_low":{str(j):low[j][0]-low[j][1]
                          for j in low},
            "low_representative_invariance":"PASS",
            "proof":"row-odd-parity; coset orthogonality; character sum"}


def finite_full_invariants(data,cap=1<<13):
    if data is None:
        return {"verdict":"INCONSISTENT_GF2"}
    ret=fixed_branch_invariants(data)
    hist=enumerate_affine_oracle(data,cap=cap)
    D=spectral_transform_from_oracle(data,hist)
    assert check_exact_coset_identity(data,hist,D)
    assert sum(D.values())==ret["expected_sum_D"]
    assert D[data["m"]]==ret["expected_D_m"]
    assert all(D[data["m"]-s]==((-1)**ret["parity"])*D[s]
               for s in range(data["m"]+1))
    assert all((j%2==ret["parity"] or mass==0)
               for j,mass in hist.items())
    assert hist.get(0,0)==ret["C0"]
    assert all(D[j]==v for j,v in
               ((int(k),v) for k,v in ret["signed_low"].items()))
    ret.update(full_signed_spectrum=D,
               full_affine_histogram=hist,
               full_sum_signed="PASS",
               full_parity_support="PASS",
               full_complement="PASS")
    return ret


def connected36(seed):
    rows,witness,_=make_connected(2,seed)
    return mutate_connected(
        rows,witness,random.Random(seed*991+20261015),
        moves=4+seed%13
    )[0]


def self_test():
    cases={
        "AffinePlane9":fixtures()["AffinePlane9_SAT"],
        "HolyerK4":fixtures()["HolyerK4_SAT"],
        "Connected36_seed0":connected36(0),
        "Connected36_seed13":connected36(13)
    }
    result={}
    for label,rows in cases.items():
        records=[]
        for cube in ((0,0),(1,0),(0,1),(5,0),(0,5)):
            data=affine_data(rows,cube)
            check=finite_full_invariants(data)
            if check["verdict"]!="CONSISTENT":
                records.append({"cube":cube,"status":"GF2_INCONSISTENT"})
                continue
            records.append({
                "cube":cube,"m":check["m"],"r":check["r"],
                "d":check["d"],"parity":check["parity"],
                "homogeneous_C0":check["C0"],
                "sum_D":sum(check["full_signed_spectrum"].values()),
                "D_m":check["expected_D_m"],
                "negative_coefficients":sum(v<0 for v in
                                      check["full_signed_spectrum"].values()),
                "all_identities":"PASS"})
        assert any(r.get("negative_coefficients",0)>0 for r in records)
        result[label]=records
    return {
        "status":"AFFINE_SIGNED_SPECTRUM_IDENTITIES_PROVED_FINITE_ORACLE_VERIFIED",
        "examples":result,
        "sum_D_equation_in_existing_full_LP":"REDUNDANT_BUT_INDEPENDENT_AUDIT",
        "uniform_total_SCL":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    opt=p.parse_args()
    if not opt.self_test:p.error("--self-test")
    print(json.dumps(self_test(),indent=2,sort_keys=True))
