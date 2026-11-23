#!/usr/bin/env python3
"""Offline, paired proof-coverage audit inspired by JANUS I0 control discipline.

Every arm sees exactly the same frozen cases. No live PoW, network, nonce,
timing claims, or numerical physical assumptions. Comparative coverage is
NOT a speed comparison; portfolio solves a superset by construction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

from exactone_parity_preprocessor import digest, solution_set
from exactone_bounded_width_dp import solve as width_solve, verify as width_verify
from exactone_affine_nullity import solve as affine_solve, verify as affine_verify, full_pair_fan
from exactone_component_factorization import (
    solve as component_solve, verify as component_verify,
    high_width_high_nullity,
)

SCHEMA="janus.fundamentum.i0_paired_proof_coverage_v1"
SOURCES={
    "private_repo":"Hawkar-usls/janus-io",
    "private_commit":"e23c4f25862d80a156de1410f66438119611612b",
    "public_repo":"Hawkar-usls/janus-io-public",
    "public_commit":"41b1c9b6af6629a551d2814aa69c5dfcac042620",
    "shared_offline_butterfly_blob":"697ef1b46d6253f034e3c7b33783836e99c96052",
    "source_contract":"docs/structured-traversal-and-random-control.md",
    "public_claim_boundary":"PROJECT_STATUS.json",
}
ARMS=("width2_baseline","affine4","component3")


def cases(seed=20261028):
    rng=random.Random(seed)
    collection=[
        {"n":1,"clauses":[[1]]},
        {"n":2,"clauses":[]},
        {"n":4,"clauses":[[1,2,3],[2,3,4]]},
        {"n":8,"clauses":[]},
        {"n":12,"clauses":[[i,i+1,i+2] for i in range(1,11)]},
        full_pair_fan(12,False),full_pair_fan(12,True),
        high_width_high_nullity(6,8,False),
        high_width_high_nullity(6,8,True),
    ]
    for _ in range(96):
        n=rng.randint(1,8)
        clauses=[]
        for __ in range(rng.randint(0,11)):
            variables=[rng.randint(1,n) for _ in range(rng.choice((1,3)))]
            clauses.append([v if rng.randrange(2) else -v for v in variables])
        collection.append({"n":n,"clauses":clauses})
    return collection


def run_one(case):
    return {
        "width2_baseline": width_solve(case,width_cap=2),
        "affine4":affine_solve(case,max_free_dimension=4),
        "component3":component_solve(case,local_nullity_cap=3)
    }


def classification(arm,answer):
    status=answer["status"]
    if arm=="width2_baseline":
        return "OPEN" if status=="OPEN_WIDTH_CAP" else status
    if arm=="affine4":
        return "OPEN" if status=="OPEN_NULLITY_CAP" else (
            "UNSAT" if status.startswith("UNSAT") else status)
    return "OPEN" if status=="OPEN_COMPONENT_CAP" else (
        "UNSAT" if status=="UNSAT_COMPONENT" else "SAT")


def evaluate(collection):
    if not isinstance(collection,list) or len(collection)<2:
        raise ValueError("INVALID_FROZEN_CASE_SET")
    identifiers=[digest(case) for case in collection]
    if len(identifiers)!=len(set(identifiers)):
        # Duplicate instances inflate evidence exposure; keep the guard strict.
        raise ValueError("DUPLICATE_CASES_NOT_INDEPENDENT_EXPOSURE")
    counts={a:{"SAT":0,"UNSAT":0,"OPEN":0,"attempted":0,
               "independently_checked":0} for a in ARMS}
    trials=[]
    for index,case in enumerate(collection):
        raw=run_one(case)
        checks={
            "width2_baseline":width_verify(case,raw["width2_baseline"]),
            "affine4":affine_verify(case,raw["affine4"]),
            "component3":component_verify(case,raw["component3"]),
        }
        if not all(checks.values()):
            raise AssertionError("ONE_OR_MORE_INDEPENDENT_CERTIFICATES_FAILED")
        results={a:classification(a,raw[a]) for a in ARMS}
        proven={results[a] for a in ARMS}-{"OPEN"}
        if len(proven)>1:
            raise AssertionError("CONFLICTING_INDEPENDENT_VERDICTS")
        if case["n"]<=8:
            actual=solution_set(case)
            expected="SAT" if actual else "UNSAT"
            if any(p!=expected for p in proven):
                raise AssertionError("INDEPENDENT_ENUMERATOR_DISAGREEMENT")
        for a in ARMS:
            counts[a][results[a]]+=1
            counts[a]["attempted"]+=1
            counts[a]["independently_checked"]+=1
        trials.append({
            "instance_index":index,
            "instance_sha256":identifiers[index],
            "number_of_variables":case["n"],
            "number_of_clauses":len(case["clauses"]),
            "control_width2":results["width2_baseline"],
            "affine":results["affine4"],
            "component":results["component3"],
            "independent_original_proof_checks":"PASS",
            "reference_truth_table":"PASS_IF_N_LE_8" if case["n"]<=8 else "NOT_ATTEMPTED_LARGE_CASE",
        })
    # No runtime, joules, checked-hashes, or CPU process metrics were collected.
    return {
        "schema":SCHEMA,"protocol_version":"frozen_cases_paired_coverage_1",
        "source_snapshots":SOURCES,
        "frozen_manifest_sha256":digest({"instance_sha256":identifiers}),
        "fixed_seed":20261028,
        "trial_count":len(trials),
        "arms":counts,
        "trials":trials,
        "baseline_control":"WIDTH_CAP_2_DECISION",
        "paired_input_exposure":True,
        "identical_computation_budget":False,
        "wall_time_measured":False,
        "energy_measured":False,
        "speedup_inferred":False,
        "poisson_or_hash_tail_significance_inferred":False,
        "network_mining_executed":False,
        "private_io_raw_logs_collected":False,
        "original_math_certificates_verified":True,
        "universal_polynomial_sat_algorithm_proven":False,
        "p_vs_np":"OPEN",
    }


def self_test():
    frozen=cases()
    # Freeze the heterogeneous cases from a deterministic seed. Should
    # any duplicates appear, they must be removed rather than counted twice.
    uniq=[]
    seen=set()
    for c in frozen:
        h=digest(c)
        if h not in seen:
            seen.add(h)
            uniq.append(c)
    report=evaluate(uniq)
    assert report["arms"]["width2_baseline"]["attempted"]==len(uniq)
    assert report["arms"]["component3"]["attempted"]==len(uniq)
    assert report["original_math_certificates_verified"]
    assert not report["identical_computation_budget"]
    assert not report["speedup_inferred"]
    assert not report["network_mining_executed"]
    assert len([t for t in report["trials"] if t["number_of_variables"]<=8])>=90
    # Genuine high-width cases must remain recognized by at least one arm.
    for i in (5,6,7,8):
        assert report["trials"][i]["component"] in ("SAT","UNSAT")
    # Deliberately tamper with a recorded decision: there is no
    # cryptographic claim from the report hash; rerun/certify it.
    forged=json.loads(json.dumps(report))
    forged["trials"][0]["component"]="OPEN"
    assert forged!=evaluate(uniq)
    report["self_test"]="PASS"
    report["rerun_tampering_guard"]="REJECTED"
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test",action="store_true",required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    out=self_test()
    serial=json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if a.output:a.output.write_text(serial,encoding="utf-8")
    print(serial)


if __name__=="__main__":
    main()
