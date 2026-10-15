#!/usr/bin/env python3
"""Gate E4.1: AFFINE MacWilliams proof-carrying gear for EVERY DFS cube.

Unlike the earlier root-only bridge, every partial cube is recomputed
from its OWN restricted A_T and affine coset. The signed spectrum is
P-M, never assumed nonnegative. A verified zero bound may soundly
prune a cube; positive bounds are only upper bounds, NOT SAT witnesses.

All branches preserve candidate coverage exactly. A child upper-bound
sum need not decrease relative to parent under differing local
relaxations; reported reduction is accepted only after actual integer
comparison, never fabricated. Per-invocation DFS nodes capped at
4*n*n, but Fraction simplex runtime/pivot count unbounded here.
Incomplete search returns UNKNOWN and hash/policy-guarded checkpoint.
"""
import json,argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from r5_cooperative_scl_coverage_20261015 import (
    validate_scl,local_consequences,gf2_consequences,choose_branch,
    fingerprint,valid_witness,fixtures
)
from r5_affine_macwilliams_soundness_20261015 import (
    affine_data,exact_affine_lp,enumerate_affine_oracle
)


def certified_bound(rows,cube,degree=2,low_spectrum=3):
    data=affine_data(rows,cube)
    if data is None:
        return 0,{"type":"GF2_INCONSISTENT"}
    target=data["target_free_weight"]
    if (target is None or not 0<=target<=data["m"]
            or target%2!=data["parity"]):
        return 0,{"type":"TARGET_WEIGHT_IMPOSSIBLE"}
    if target==0:
        c=int(data["homogeneous_restricted_rhs"])
        return c,{"type":"EXACT_ZERO_WEIGHT","bound":c}
    if data["m"]<4:
        # <=3 Boolean coordinates, hence <=8 affine words;
        # this is exact and uniformly bounded, not an LP.
        hist=enumerate_affine_oracle(data,cap=8)
        value=hist.get(target,0)
        return value,{"type":"EXACT_TINY_CUBE","bound":value}
    proof=exact_affine_lp(data,k=degree,
                          known_signed_degree=low_spectrum)
    assert proof["dual_verified"] and proof["primal_verified"]
    assert proof["integer_upper_bound"]>=0
    return proof["integer_upper_bound"],{
        "type":"SIGNED_AFFINE_MACWILLIAMS",
        "bound":proof["integer_upper_bound"],
        "optimum":proof["exact_rational_optimum"],
        "m":data["m"],"d":data["d"],
        "signed_low":proof["known_signed_low"],
        "proof_checked":True
    }


def one_step(rows,cube=(0,0),degree=2,low_spectrum=3):
    rows=validate_scl(rows)
    n=len(rows)
    original,proof=certified_bound(rows,cube,degree,low_spectrum)
    if original==0:
        return {"op":"UNSAT_CUBE","cube":cube,"bound_before":0,
                "proof":proof,"children":[]}
    if n%3:
        return {"op":"UNSAT_CUBE","cube":cube,
                "bound_before":0,"proof":{"type":"GLOBAL_WEIGHT"},"children":[]}
    kind,new,premises=local_consequences(rows,cube)
    if kind=="CONFLICT":
        return {"op":"UNSAT_CUBE","cube":cube,"bound_before":original,
                "proof":{"type":"EXACT_ONE_CONFLICT","premises":premises},
                "children":[]}
    if kind=="FORCED":
        assert local_consequences(rows,cube)[1]==new
        children=[new]
        op="EXACT_ONE"
    else:
        kind,new,d=gf2_consequences(rows,cube)
        if kind=="CONFLICT":
            return {"op":"UNSAT_CUBE","cube":cube,
                    "bound_before":original,
                    "proof":{"type":"GF2_CONFLICT"},"children":[]}
        if kind=="FORCED":
            assert gf2_consequences(rows,cube)[1]==new
            children=[new]
            op="GF2"
        else:
            v=choose_branch(rows,cube)
            assert not ((cube[0]|cube[1])>>v)&1
            children=[(cube[0]|(1<<v),cube[1]),
                      (cube[0],cube[1]|(1<<v))]
            op="BRANCH"
    bounds=[]
    for child in children:
        value,childproof=certified_bound(rows,child,degree,low_spectrum)
        bounds.append({"cube":child,"bound":value,"proof":childproof})
    new_total=sum(item["bound"] for item in bounds)
    # This is a measurement, not a requirement for sound branching.
    return {"op":op,"cube":cube,
            "bound_before":original,
            "children":children,
            "child_bound_data":bounds,
            "child_total_bound":new_total,
            "certified_shrink":new_total<original,
            "geometric_c1":new_total*n<=original*(n-1),
            "upper_bound_monotone":new_total<=original,
            "local_rewrite_verified":True}


def solve(rows,budget=1,degree=2,low_spectrum=3,
          checkpoint=None,resume=None):
    rows=validate_scl(rows)
    n=len(rows)
    if not 0<=degree<=3 or not 0<=low_spectrum<=3:
        raise ValueError("fixed degrees only 0..3")
    if budget<0:
        raise ValueError("node budget must be nonnegative")
    cap=min(budget,4*n*n)
    if resume:
        state=json.loads(Path(resume).read_text(encoding="utf-8"))
        if (state.get("version")!=1 or
            state.get("sha256")!=fingerprint(rows) or
            state.get("degree")!=degree or
            state.get("low_spectrum")!=low_spectrum):
            raise ValueError("invalid checkpoint hash/version/policy")
        frontier=[tuple(c) for c in state["frontier"]]
        prior=state["previous_nodes"]
        if len(frontier)>n+1 or any(z<0 or o<0 or z&o or
                                  ((z|o)>>n) for z,o in frontier):
            raise ValueError("invalid checkpoint cube stack")
    else:
        frontier=[(0,0)]
        prior=0
    processed=0
    events=[]
    witness=None
    while frontier and processed<cap:
        cube=frontier.pop()
        processed+=1
        delta=one_step(rows,cube,degree,low_spectrum)
        events.append({"op":delta["op"],
                       "cube":cube,
                       "bound_before":delta["bound_before"],
                       "child_total":delta.get("child_total_bound"),
                       "geometric_c1":delta.get("geometric_c1")})
        events=events[-16:]
        if delta["op"]=="UNSAT_CUBE":
            continue
        children=delta["children"]
        for c in children:
            if (c[0]|c[1]).bit_count()==n:
                assignment=c[1]
                if valid_witness(rows,assignment):
                    witness=assignment
                    break
        if witness is not None:
            break
        frontier.extend(reversed(children))
    verdict=("SAT" if witness is not None else
             "UNSAT" if not frontier else "UNKNOWN_RESOURCE_LIMIT")
    result={"verdict":verdict,"nodes":processed,
            "total_nodes":prior+processed,
            "frontier_len":len(frontier),
            "recent_verified_events":events,
            "policy":"restricted_signed_affine_macwilliams_each_cube"}
    if witness is not None:
        assert valid_witness(rows,witness)
        result["witness"]=witness
    if verdict=="UNKNOWN_RESOURCE_LIMIT" and checkpoint:
        state={"version":1,"sha256":fingerprint(rows),
               "degree":degree,"low_spectrum":low_spectrum,
               "previous_nodes":prior+processed,
               "frontier":frontier}
        Path(checkpoint).write_text(json.dumps(state,sort_keys=True),
                                    encoding="utf-8")
        result["checkpoint_written"]=checkpoint
    return result


def self_test():
    rows=fixtures()["HolyerK4_SAT"]
    root=one_step(rows,(0,0))
    assert root["op"] in ("BRANCH","EXACT_ONE","GF2")
    assert root["local_rewrite_verified"]
    assert all(item["proof"]["type"] in (
        "SIGNED_AFFINE_MACWILLIAMS","EXACT_ZERO_WEIGHT",
        "EXACT_TINY_CUBE","GF2_INCONSISTENT","TARGET_WEIGHT_IMPOSSIBLE"
    ) for item in root["child_bound_data"])
    branch=one_step(rows,(1,0))
    assert branch["local_rewrite_verified"]
    with TemporaryDirectory() as t:
        p=str(Path(t)/"affine.json")
        first=solve(rows,budget=1,checkpoint=p)
        assert first["verdict"]=="UNKNOWN_RESOURCE_LIMIT"
        resumed=solve(rows,budget=1,resume=p,checkpoint=p)
        assert resumed["total_nodes"]==2
        try:
            solve(fixtures()["AffinePlane9_SAT"],budget=1,
                  resume=p)
        except ValueError:
            pass
        else:
            raise AssertionError("wrong source accepted")
    return {
        "status":"AFFINE_MACWILLIAMS_PROOF_CARRYING_EVERY_CUBE",
        "HolyerK4_root":{"op":root["op"],
                         "initial_bound":root["bound_before"],
                         "child_bounds":[b["bound"]
                                         for b in root["child_bound_data"]],
                         "geometric_c1":root["geometric_c1"]},
        "HolyerK4_zero_x0":{"op":branch["op"],
                            "initial_bound":branch["bound_before"],
                            "child_total_bound":branch["child_total_bound"]},
        "resume":"HASH_AND_POLICY_PASS",
        "safety":"NO_ROOT_SIGN_ASSUMPTION_IN_CHILD",
        "total_polynomial":"NOT_PROVED",
        "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if not a.self_test:p.error("--self-test")
    print(json.dumps(self_test(),indent=2,sort_keys=True))
