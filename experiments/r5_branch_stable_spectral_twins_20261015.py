#!/usr/bin/env python3
"""E4.2 branch-stable truncated affine signatures, with honest limits.

Variable-permutation invariant finite signature:
 S_0(C) = (consistency,m,r,d,free-weight parity,C0,
           signed P/M low spectrum, moments,
           known sum(D), complement sign, optional rational LP optimum).
 S_(h+1)(C) = (S_0(C), SORTED MULTISET of
           UNORDERED PAIRS {S_h(C[v=0]), S_h(C[v=1])}
           for every free variable v).

This is isomorphism-invariant under simultaneous variable/row
relabeling; it need NOT be complete for incidence-graph isomorphism.
All-variables branching is *not* claimed a clever canonical
single-coordinate choice. A root candidate collision MUST have
opposite SAT/UNSAT status with certified finite unsat proof before
being treated as an E4.2 twin.

For FIXED h and fixed moment/signed degrees, the signatures have
n^O(h) nodes before sharing/caching (LP pivot cost excluded).
No uniform polynomial bound for h growing with n is asserted.
"""
import argparse,json,random
from collections import Counter
from math import gcd

from r5_affine_macwilliams_soundness_20261015 import (
    affine_data,coset_moments,signed_low_rowspace,exact_affine_lp
)
from r5_cooperative_scl_coverage_20261015 import (
    fixtures,validate_scl,gf2_affine,valid_witness
)
from r5_joint_spectral_anchor_twins_20261015 import (
    unrestricted_connected_mutation,classify_affine,root_signature
)
from r5_connected_coverage_breaker_20261015 import make_connected


def base_signature(rows,cube,k=2,moment_degree=1,with_lp=False):
    data=affine_data(rows,cube)
    if data is None:
        return ("GF2_INCONSISTENT",)
    n,m,r,d=data["n"],data["m"],data["r"],data["d"]
    parity=data["parity"]
    expected_parity=data["fixed_v_weight"]%2
    assert parity==expected_parity
    low=signed_low_rowspace(data,k)
    moments=coset_moments(data,moment_degree)
    target=data["target_free_weight"]
    target_state=("IN_RANGE" if target is not None and
                  0<=target<=m and target%2==parity
                  else "TARGET_IMPOSSIBLE")
    result=("CONSISTENT",m,r,d,parity,
            int(data["homogeneous_restricted_rhs"]),
            (1<<r) if data["homogeneous_restricted_rhs"] else 0,
            (-1)**parity,
            tuple(low[j] for j in range(k+1)),
            tuple(moments),target_state,target)
    if not with_lp:
        return result
    if target_state!="IN_RANGE":
        return result+("LP_TARGET_IMPOSSIBLE",)
    if target==0:
        return result+(str(int(data["homogeneous_restricted_rhs"])),)
    if m<4:
        from r5_affine_macwilliams_soundness_20261015 import (
            enumerate_affine_oracle
        )
        hist=enumerate_affine_oracle(data,cap=8)
        return result+(str(hist.get(target,0)),)
    bound=exact_affine_lp(data,k=moment_degree,
                          known_signed_degree=k)
    assert bound["dual_verified"] and bound["primal_verified"]
    return result+(bound["exact_rational_optimum"],)


def branch_signature(rows,cube=(0,0),depth=1,k=2,
                     moment_degree=1,with_lp=False,cache=None):
    if cache is None:
        cache={}
    key=(cube,depth,k,moment_degree,with_lp)
    if key in cache:
        return cache[key]
    root=base_signature(rows,cube,k,moment_degree,with_lp)
    if depth==0 or root[0]!="CONSISTENT":
        cache[key]=root
        return root
    n=len(rows)
    fixed=cube[0]|cube[1]
    child_pairs=[]
    for v in range(n):
        if (fixed>>v)&1:continue
        left=branch_signature(
            rows,(cube[0]|(1<<v),cube[1]),
            depth-1,k,moment_degree,with_lp,cache
        )
        right=branch_signature(
            rows,(cube[0],cube[1]|(1<<v)),
            depth-1,k,moment_degree,with_lp,cache
        )
        child_pairs.append(tuple(sorted((left,right))))
    result=(root,tuple(sorted(child_pairs)))
    cache[key]=result
    return result


def permute_source(rows,multiplier=5,offset=2):
    n=len(rows)
    if gcd(multiplier,n)!=1:
        raise ValueError("permutation multiplier must be coprime to n")
    shifted=tuple(tuple((multiplier*v+offset)%n for v in row)
                  for row in reversed(rows))
    return validate_scl(shifted)


def compare_root_collisions(samples=36,seed=20261015):
    if not 1<=samples<=80:
        raise ValueError("finite bounded 1..80 samples")
    rng=random.Random(seed)
    original,_,_=make_connected(2,20261015)
    classes={}
    verdicts=Counter()
    dimension_counts=Counter()
    same_status_repeats=0
    opposite=None
    checked=0
    for sample in range(samples):
        rows,_=unrestricted_connected_mutation(
            original,rng,steps=4+(sample%11))
        assert len(rows)==36
        oracle=classify_affine(rows,cap=1<<12)
        verdicts[oracle["verdict"]]+=1
        dimension_counts[oracle["d"]]+=1
        if oracle["verdict"]=="UNKNOWN_RESOURCE_LIMIT":
            continue
        checked+=1
        sig=root_signature(rows)
        if sig in classes:
            past=classes[sig]
            if past["verdict"]==oracle["verdict"]:
                same_status_repeats+=1
            else:
                # Crucially: only a true opposite-SAT-status ROOT twin
                # can enter expensive affine branch-stable comparison.
                old_rows=past["rows"]
                opposite={
                    "samples":[past["sample"],sample],
                    "verdicts":[past["verdict"],oracle["verdict"]],
                    "root_equal":True,
                    "branch_depth1_equal":(
                        branch_signature(old_rows,depth=1,k=1,
                                         moment_degree=1,with_lp=False)
                        ==
                        branch_signature(rows,depth=1,k=1,
                                         moment_degree=1,with_lp=False)
                    ),
                    "finite_oracle_word_counts":[past["checked"],
                                                  oracle["checked"]]
                }
                break
        else:
            classes[sig]={"sample":sample,"rows":rows,
                          "verdict":oracle["verdict"],
                          "checked":oracle["checked"]}
    return {
        "sample_limit":samples,
        "exact_classified":checked,
        "verdict_counts":dict(verdicts),
        "GF2_dim_distribution":dict(dimension_counts),
        "distinct_root_signatures":len(classes),
        "same_verdict_root_collisions":same_status_repeats,
        "opposite_status_root_twin":opposite,
        "branch_stable_opposite_twin":(
            "FOUND_DEPTH1" if opposite and
            opposite["branch_depth1_equal"] else "NOT_FOUND"),
        "meaning":"finite bounded test, no all-n indistinguishability or hardness theorem"
    }


def self_test():
    samples={}
    for name,rows in {
        "AffinePlane9":fixtures()["AffinePlane9_SAT"],
        "HolyerK4":fixtures()["HolyerK4_SAT"]
    }.items():
        other=permute_source(rows)
        # AffinePlane9: EVERY root and singleton-child profile
        # includes exact optimal rational LP, independently verified.
        # On n18 the depth1/2 test uses fixed-degree spectral data
        # only (no costly repeated exact-Fraction simplex).
        lp_all=(name=="AffinePlane9")
        sig=branch_signature(rows,depth=1,k=1,moment_degree=1,
                             with_lp=lp_all)
        perm=branch_signature(other,depth=1,k=1,moment_degree=1,
                              with_lp=lp_all)
        assert sig==perm
        # Exact LP is additionally checked for the n18 root
        # and one matched single-child cube, not all 36 branches.
        if not lp_all:
            assert base_signature(rows,(0,0),k=1,moment_degree=1,
                                  with_lp=True)==base_signature(
                other,(0,0),k=1,moment_degree=1,with_lp=True)
            v=0
            vv=(5*v+2)%len(rows)
            assert base_signature(rows,(1<<v,0),k=1,
                                  moment_degree=1,with_lp=True)==(
                base_signature(other,(1<<vv,0),k=1,
                               moment_degree=1,with_lp=True))
        # Depth TWO is checked with cheap invariant data only,
        # and its cost scales as O(n^2) signatures.
        sig2=branch_signature(rows,depth=2,k=1,moment_degree=1,
                              with_lp=False)
        perm2=branch_signature(other,depth=2,k=1,moment_degree=1,
                               with_lp=False)
        assert sig2==perm2
        samples[name]={
            "n":len(rows),
            "depth1_full_LP_permutation_invariance":(
                "PASS_ALL_BRANCHES" if lp_all else
                "LP_ROOT_PLUS_MATCHED_SINGLE_CHILD;SPECTRAL_ALL_BRANCHES"),
            "depth2_low_spectrum_permutation_invariance":"PASS",
            "complete_isomorphism_test":"NOT_CLAIMED"
        }
    finite=compare_root_collisions(samples=36)
    assert finite["exact_classified"]>0
    # Larger connected, witness-certified positive control:
    # d=21 exceeds the finite UNSAT oracle cap. We NEVER infer
    # UNSAT or a hard-complexity theorem from this cutoff.
    larger,witness,_=make_connected(4,20261015)
    large_aff=gf2_affine(larger,0,0)
    assert large_aff is not None and len(larger)==72
    assert valid_witness(larger,witness)
    large_d=large_aff[2]
    assert large_d==21
    larger_control={"n":72,"affine_dimension":large_d,
                    "all_parity_words":1<<large_d,
                    "SAT_witness_independently_verified":True,
                    "exact_global_count":"NOT_COMPUTED",
                    "UNSAT_verdict_if_no_witness":"FORBIDDEN",
                    "small_separator_hardness":"NOT_PROVED"}
    return {
        "gate":"BRANCH_STABLE_SPECTRAL_TWINS",
        "relabeling_tests":samples,
        "finite_connected_search":finite,
        "connected_high_nullity_control":larger_control,
        "depth_signatures":"UNLABELED_ALL_SPLITS_MULTISET",
        "uniform_polynomial_h_growing":"NOT_PROVED",
        "P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--samples",type=int,default=36)
    a=p.parse_args()
    print(json.dumps(self_test() if a.self_test else
                     compare_root_collisions(a.samples),
                     indent=2,sort_keys=True))
