#!/usr/bin/env python3
"""R5 E4.6 MULTI_Z_PARITY_GADGET feasibility scout (bounded finite).

Choose a frozen legal connected UNSAT n36 base with known SAT two-cover.
Vary ONE OR TWO original incidence voltages, searching for obstruction
matrices H=L^T A0 K with rank4 (kerH dimension2). Each such obstruction
admits up to THREE nonzero physical sheet-XOR candidates z∈ker A.

For every scanned z, compute residual Y_z through exact-cover DPLL with
explicit resource bound. A fixed-z cycle system may still reject any
given voltage. NO candidate is called SAT or UNSAT without its own
direct witness or complete oracle. Even two feasible z only establishes
multiple potential SAT mechanisms, NOT a branch-stable spectral twin.

This is a deliberately small, reproducible necessary-structure search,
not an asymptotic lower bound or promise of high girth/expansion.
"""
from itertools import combinations
from collections import Counter
import argparse,json

from r5_cycle_parity_certificate_20261015 import context
from r5_rank_preserving_cover_twins_20261015 import (
    phi_apply,gf2_nullspace,gf2_rank,source_bitrows,
    delta_to_signs,lift_rows
)
from r5_residual_yz_exact_cover_20261016 import residual
from r5_cover_twins_independent_audit_20261015 import (
    independently_enumerate_parity
)


def image_rank(H,d):
    return gf2_rank([(H>>(a*d))&((1<<d)-1) for a in range(d)])


def candidate_z(H,frame):
    d=frame["d"]
    coords=gf2_nullspace([(H>>(a*d))&((1<<d)-1)
                          for a in range(d)],d)
    assert len(coords)==d-image_rank(H,d)
    stars=[]
    for pattern in range(1,1<<len(coords)):
        c=0
        for j,word in enumerate(coords):
            if (pattern>>j)&1:c^=word
        z=0
        for j,b in enumerate(frame["right"]):
            if (c>>j)&1:z^=b
        assert z
        stars.append(z)
    return stars


def search(max_flip_candidates=5900,max_obstructions=32):
    base,meta,frame,signs,sigma,y,witness,cover,z0,k=context()
    images=frame["images"]
    originalH=phi_apply(images,sigma)
    assert image_rank(originalH,6)==5
    attempted=0
    rank_counts=Counter()
    relevant_hist=Counter()
    candidate_records=[]
    best=None
    found_rank4=0
    n=len(base)
    for flips_count in (1,2):
        for flip_indices in combinations(range(len(images)),flips_count):
            if attempted>=max_flip_candidates or found_rank4>=max_obstructions:
                break
            attempted+=1
            H=originalH
            mask=0
            for idx in flip_indices:
                H^=images[idx]
                mask^=1<<idx
            r=image_rank(H,6)
            rank_counts[str(r)]+=1
            if r!=4:
                continue
            found_rank4+=1
            zs=candidate_z(H,frame)
            assert len(zs)==3
            yz_results=[]
            finite_count=0
            unknown_count=0
            for z in zs:
                info=residual(base,z,budget=1800)
                if info["status"]=="EXACT":
                    if info["count"]:finite_count+=1
                else:unknown_count+=1
                yz_results.append({
                    "z_decimal":str(z),"z_weight":z.bit_count(),
                    "p":info.get("p"),
                    "Y_z_count":info.get("count"),
                    "status":info["status"]})
            relevant_hist[f"{finite_count}_relevant_{unknown_count}_unknown"]+=1
            record={
                "flip_indices":flip_indices,
                "base_voltage_xor_decimal":str(mask),
                "H_rank":r,"kerH_dimension":2,
                "z_star_original_preserved":z0 in zs,
                "candidate_z":yz_results,
                "independently_Yz_nonempty_count":finite_count,
                "unresolved_Yz_status_count":unknown_count}
            candidate_records.append(record)
            if best is None or finite_count>best["independently_Yz_nonempty_count"]:
                best=record
            if finite_count>=2 and unknown_count==0:
                # A valid new multi-z POSSIBLE SAT mechanism.
                # For this particular sign assignment, independently
                # check complete 2^8 GF2-cover oracle (not assume SAT).
                new_signs=delta_to_signs(frame["edges"],signs,mask)
                trial=lift_rows(base,new_signs)
                oracle=independently_enumerate_parity(trial)
                assert oracle["status"]=="EXACT"
                record["independent_trial_cover_oracle"]=oracle
                return {
                    "status":"MULTI_Z_FEASIBLE_COVER_FOUND",
                    "tested_flip_candidates":attempted,
                    "rank_histogram":dict(rank_counts),
                    "rank4_examined":found_rank4,
                    "Yz_feasibility_histogram":dict(relevant_hist),
                    "first_multi_z_candidate":record,
                    "scientific_limit":"not SAT/UNSAT twins; only a finite multi-z positive control",
                    "P_vs_NP":"OPEN"}
        if attempted>=max_flip_candidates or found_rank4>=max_obstructions:
            break
    return {
        "status":"NO_TWO_YZ_FEASIBLE_IN_BOUNDED_LOCAL_FLIPS",
        "tested_flip_candidates":attempted,
        "rank_histogram":dict(rank_counts),
        "rank4_examined":found_rank4,
        "Yz_feasibility_histogram":dict(relevant_hist),
        "best_record":best,
        "first_records":candidate_records[:4],
        "scientific_limit":"bounded one/two-flip search only; UNKNOWN never UNSAT",
        "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    opt=p.parse_args()
    r=search()
    assert r["rank4_examined"]>=0
    print(json.dumps(r,sort_keys=True,indent=2))
