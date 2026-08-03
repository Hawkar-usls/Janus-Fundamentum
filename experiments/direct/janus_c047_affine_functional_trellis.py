#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json, random
from janus_c047_affine_trellis_core import *
from janus_c047_affine_trellis_solver import compile_trellis
from janus_c047_affine_trellis_verifier import verify

def brute(factors,dimension):
    normalized=normalize_factors(factors,dimension)
    for x in range(1<<dimension):
        if not any(point_in_factor(x,f["equations"]) for f in normalized):
            return True,x
    return False,None

def random_factor(rng,dimension,fid):
    rank=rng.randint(0,min(3,dimension))
    normals=[]
    while len(linear_rref(normals,dimension))<rank:
        normals.append(rng.randrange(1,1<<dimension))
    W=linear_rref(normals,dimension)
    beta=rng.randrange(1<<len(W))
    return {"factor_id":fid,"equations":[(v,(beta>>i)&1) for i,v in enumerate(W)]}

def c046_pair(d,complementary):
    factors=[]
    for i in range(d):
        factors.append({"factor_id":2*i,"equations":[(1<<i,0)]})
        factors.append({"factor_id":2*i+1,"equations":[(1<<i,1 if complementary else 0)]})
    return factors

def independent_units(d):
    return [{"factor_id":i,"equations":[(1<<i,0)]} for i in range(d)]

def hidden_basis(d):
    normals=[]
    acc=0
    for i in range(d):
        acc ^= 1<<i
        normals.append({"factor_id":i,"equations":[(acc,0)]})
    return normals

def hard_image(n):
    factors=[]; fid=0
    for i in range(n):
        for shift in (1,3,5):
            j=(i+shift)%n; k=(i+2*shift)%n
            factors.append({"factor_id":fid,"equations":[(1<<i,0),(1<<j,1),(1<<k,0)]})
            fid+=1
    return factors

def run(seed=470047):
    rng=random.Random(seed)
    random_cases=260
    exact=open_count=mismatch=witness_fail=verify_fail=0
    for _ in range(random_cases):
        d=rng.randint(1,7)
        factors=[random_factor(rng,d,i) for i in range(rng.randint(0,9))]
        cert=compile_trellis(factors,d,requested_width_cap=4)
        truth,w=brute(factors,d)
        if cert["status"] in ("SAT","UNSAT"):
            exact+=1
            if (cert["status"]=="SAT")!=truth: mismatch+=1
            if cert["status"]=="SAT":
                x=int(cert["ambient_witness"])
                if any(point_in_factor(x,f["equations"]) for f in normalize_factors(factors,d)):
                    witness_fail+=1
        else: open_count+=1
        if not verify(factors,d,cert): verify_fail+=1

    left=compile_trellis(c046_pair(24,False),24,requested_width_cap=2)
    right=compile_trellis(c046_pair(24,True),24,requested_width_cap=2)
    assert left["status"]=="SAT" and int(left["ambient_witness"])==(1<<24)-1
    assert right["status"]=="UNSAT"
    assert max(left["cut_widths"])==1 and max(right["cut_widths"])==1
    assert verify(c046_pair(24,False),24,left)
    assert verify(c046_pair(24,True),24,right)

    units=compile_trellis(independent_units(40),40,requested_width_cap=1)
    assert units["status"]=="SAT" and max(units["cut_widths"])==0
    assert int(units["ambient_witness"])==(1<<40)-1

    hidden=compile_trellis(hidden_basis(40),40,requested_width_cap=1)
    assert hidden["status"]=="SAT" and max(hidden["cut_widths"])==0

    ambient=[{"factor_id":0,"equations":[]}]
    whole=compile_trellis(ambient,64,requested_width_cap=0)
    assert whole["status"]=="UNSAT"

    hard=compile_trellis(hard_image(24),24,requested_width_cap=3)
    assert hard["status"]==OPEN_CUT_WIDTH

    work_open=compile_trellis(independent_units(12),12,requested_width_cap=1,work_cap=1)
    assert work_open["status"]==OPEN_WORK_BUDGET and verify(independent_units(12),12,work_open)

    cert_open=compile_trellis(independent_units(12),12,requested_width_cap=1,certificate_cap=128)
    assert cert_open["status"]==OPEN_CERTIFICATE_VOLUME and verify(independent_units(12),12,cert_open)

    corrupt=copy.deepcopy(left)
    corrupt["ambient_witness"]="0"
    corrupt["integrity_sha256"]=digest({k:v for k,v in corrupt.items() if k!="integrity_sha256"})
    assert not verify(c046_pair(24,False),24,corrupt)

    result={
        "artifact_id":"C047-JANUS-OFFSET-AWARE-AFFINE-FUNCTIONAL-TRELLIS",
        "status":"PASS","p_vs_np":"OPEN","seed":seed,
        "random_cases":random_cases,"random_exact":exact,"random_open":open_count,
        "mismatches":mismatch,"witness_failures":witness_fail,
        "independent_verification_failures":verify_fail,
        "constructive_theorem":"For the deterministic parallel-block factor order, exact affine-functional trellis compilation runs in 2^O(k) poly(L) total work when every cut normal-space intersection has fixed dimension k and all explicit capabilities hold.",
        "state_semantics":"A cut state is a linear functional on span(prefix normals) intersect span(suffix normals). Factor offsets are retained as distinguished functionals on each factor normal space.",
        "c046_offset_pair":{"dimension":24,"sat_status":left["status"],"unsat_status":right["status"],"maximum_width":1},
        "global_signed_support_separation":{"independent_factors":40,"theoretical_global_inclusion_exclusion_terms":str((1<<40)-1),"trellis_width":0,"status":units["status"]},
        "hidden_basis_control":{"dimension":40,"trellis_width":0,"status":hidden["status"]},
        "hard_image_control":{"variables":24,"status":hard["status"],"first_overflow_cut":hard["first_overflow_cut"],"overflow_width":hard["overflow_width"]},
        "whole_space_forbidden":whole["status"],
        "work_refusal":work_open["status"],
        "certificate_refusal":cert_open["status"],
        "tampered_witness":"REJECTED",
        "new_gate":"POLYNOMIAL_AFFINE_LAYOUT_DISCOVERY_OR_BRANCH_DECOMPOSITION_WITH_OFFSET_AWARE_MESSAGES",
        "claim_boundary":"Exact only for the deterministic charged order when cut width and all resource capabilities are bounded. It does not prove a good order always exists, solve NAND3+NEQ, or resolve P versus NP.",
    }
    result["integrity_sha256"]=digest(result)
    return result

def main():
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); p.add_argument("--output"); p.add_argument("--seed",type=int,default=470047)
    a=p.parse_args(); r=run(a.seed)
    text=json.dumps(r,indent=2,sort_keys=True)+"\n"
    if a.output: open(a.output,"w",encoding="utf-8").write(text)
    else: print(text,end="")
    if a.self_test:
        assert r["status"]=="PASS" and r["mismatches"]==0 and r["witness_failures"]==0 and r["independent_verification_failures"]==0

if __name__=="__main__": main()
