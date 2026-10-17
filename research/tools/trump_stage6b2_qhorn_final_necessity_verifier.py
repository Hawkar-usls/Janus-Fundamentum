#!/usr/bin/env python3
"""Stage6B.2 Phase C/D: fresh final positive replay + necessity audit.

For each completely shrunken B*:
  * independently reconstruct F-B*;
  * obtain a fresh generic q-Horn weight proposal and verify it;
  * replay the polynomial q-Horn terminal;
  * for every v in B*, construct F-(B*\\{v}) and require a fresh,
    independently replayed canonical non-q-Horn obstruction.

Only if every retained variable has such a necessity obstruction is B*
declared inclusion-minimal. No minimum-cardinality claim is made.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))

from trump_stage6_qhorn_independent_checker import (  # noqa: E402
    build_obstruction,
    formula_sequence_sha256,
    qhorn_terminal,
    verify_obstruction,
    verify_weights,
)
from trump_stage6b_deletion_qhorn_independent_checker import (  # noqa: E402
    deletion_projection,
    path_transition,
)
from trump_stage6b2_qhorn_witness_transfer import propose_weights  # noqa: E402

TARGETS=[1,2,3,4,5,6,7,9,10,11,12,13,14]


def stable_sha(obj):
    raw=(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest(),len(raw)


def file_sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def load_stage6a_rows(path:Path):
    d=json.loads(path.read_text(encoding="utf-8"))
    return {int(r["index"]):r for r in d["rows"]}


def path_lengths(obstruction):
    out=[]
    for p in obstruction.get("paths",[]):
        for key in ("lit_to_complement","complement_to_lit"):
            path=p.get(key) or []
            out.append({
              "literal":p.get("literal"),
              "direction":key,
              "edge_length":max(0,len(path)-1)
            })
    return out


def final_mechanism_audit(original,final_B,stage6a_row):
    old=((stage6a_row.get("proof") or {}).get("obstruction") or {})
    old_triple=old.get("triple") or []
    old_vars={abs(int(l)) for l in old_triple}
    intersection=sorted(set(final_B)&old_vars)
    reduced=deletion_projection(original,set(final_B))

    transitions=[]
    broken=0
    for p in old.get("paths",[]):
        lit=p.get("literal")
        for key in ("lit_to_complement","complement_to_lit"):
            tr=path_transition(
              original,reduced,set(final_B),p.get(key)
            )
            if not tr.get("survives_verbatim_in_F2_of_F_minus_B",False):
                broken+=1
            transitions.append({
              "literal":lit,
              "direction":key,
              "transition":tr
            })

    if not intersection and broken==6:
        label="GLOBAL_CONNECTIVITY_BREAK"
    elif intersection and broken==0:
        label="LOCAL_LITERAL_REMOVAL"
    elif intersection and broken>0:
        label="MIXED"
    else:
        label="OTHER_AMBIGUOUS"

    return {
      "old_stage6A_triple":old_triple,
      "old_stage6A_triple_intersection":intersection,
      "old_six_path_transitions":transitions,
      "old_paths_broken_count":broken,
      "mechanism_classification":label
    }


def audit_target(source_data,stage6a_row,shrink,timeout_ms):
    target=int(shrink["target_index"])
    row=source_data["residuals"][target]
    original=row["residual_formula"]

    if not shrink.get("seed_available"):
        return {
          "target_index":target,
          "scientific_outcome":
              "INDEX10_TRANSFER_SURVIVOR" if target==10 else "INFRASTRUCTURE_ERROR",
          "transfer_status":"NO_CANONICAL_VERIFIED_SEED",
          "inclusion_minimality_verified":False
        }

    if not shrink.get("shrink_complete"):
        return {
          "target_index":target,
          "seed_source_index":shrink.get("seed_source_index"),
          "seed_B_size":shrink.get("seed_B_size"),
          "scientific_outcome":shrink.get("scientific_outcome"),
          "final_B_star":shrink.get("final_B_star"),
          "final_B_star_size":shrink.get("final_B_star_size"),
          "final_B_star_sha256":shrink.get("final_B_star_sha256"),
          "number_removed_seed_variables":shrink.get("number_removed_seed_variables"),
          "number_retained_variables":shrink.get("number_retained_variables"),
          "inclusion_minimality_verified":False,
          "incomplete_reason":shrink.get("incomplete_reason")
        }

    B=sorted(int(v) for v in shrink["final_B_star"])
    reduced=deletion_projection(original,set(B))
    reduced_sha=formula_sequence_sha256(reduced)

    proposal=propose_weights(reduced,timeout_ms)
    if proposal.get("solver_status")!="SAT":
        return {
          "target_index":target,
          "seed_source_index":shrink["seed_source_index"],
          "seed_B_size":shrink["seed_B_size"],
          "scientific_outcome":
              "SHRINK_INCOMPLETE_RESOURCE_LIMIT"
              if proposal.get("solver_status")=="UNKNOWN"
              else "INFRASTRUCTURE_ERROR",
          "final_B_star":B,
          "final_B_star_size":len(B),
          "final_B_star_sha256":shrink["final_B_star_sha256"],
          "final_positive_proposal_status":proposal.get("solver_status"),
          "reason_unknown":proposal.get("reason_unknown"),
          "inclusion_minimality_verified":False
        }

    ok,detail=verify_weights(reduced,proposal.get("weights"))
    if not ok:
        return {
          "target_index":target,
          "scientific_outcome":"FAIL_CERTIFICATE",
          "failure":{"reason":"FINAL_POSITIVE_QHORN_CERTIFICATE_FAILED","detail":detail},
          "inclusion_minimality_verified":False
        }

    terminal=qhorn_terminal(reduced,detail["weights"])
    if not terminal.get("terminal_replay_verified"):
        return {
          "target_index":target,
          "scientific_outcome":"INFRASTRUCTURE_ERROR",
          "failure":{"reason":"FINAL_QHORN_TERMINAL_REPLAY_NOT_VERIFIED"},
          "terminal":terminal,
          "inclusion_minimality_verified":False
        }

    cert_sha,cert_bytes=stable_sha(proposal["weights"])
    necessity=[]
    all_verified=True

    old=((stage6a_row.get("proof") or {}).get("obstruction") or {})
    old_triple=old.get("triple") or []

    for v in B:
        candidate=[x for x in B if x!=v]
        cand_formula=deletion_projection(original,set(candidate))
        cand_sha=formula_sequence_sha256(cand_formula)
        obs=build_obstruction(cand_formula)
        if obs is None:
            necessity.append({
              "variable":v,
              "verified":False,
              "reason":"NO_CANONICAL_NON_QHORN_OBSTRUCTION_FOUND",
              "F_minus_B_without_v_sha256":cand_sha
            })
            all_verified=False
            continue
        vok,vdetail=verify_obstruction(cand_formula,obs)
        if not vok:
            necessity.append({
              "variable":v,
              "verified":False,
              "reason":"OBSTRUCTION_FAILED_INDEPENDENT_REPLAY",
              "detail":vdetail,
              "F_minus_B_without_v_sha256":cand_sha
            })
            all_verified=False
            continue
        necessity.append({
          "variable":v,
          "verified":True,
          "F_minus_B_without_v_sha256":cand_sha,
          "obstruction":obs,
          "triple":obs.get("triple"),
          "original_clause_index":obs.get("original_clause_index"),
          "path_lengths":path_lengths(obs),
          "uses_old_stage6A_triple":
              tuple(obs.get("triple") or [])==tuple(old_triple)
        })

    mech=final_mechanism_audit(original,B,stage6a_row)
    bsha,_=stable_sha(B)

    if all_verified:
        outcome="VERIFIED_INCLUSION_MINIMAL_DELETION_QHORN_BACKDOOR"
    else:
        outcome="INFRASTRUCTURE_ERROR"

    return {
      "target_index":target,
      "seed_source_index":shrink["seed_source_index"],
      "seed_B_size":shrink["seed_B_size"],
      "transfer_status":"TRANSFER_VERIFIED",
      "initial_bound":shrink["seed_B_size"],
      "final_B_star":B,
      "final_B_star_size":len(B),
      "final_B_star_sha256":bsha,
      "fresh_qhorn_certificate_sha256":cert_sha,
      "fresh_qhorn_certificate_bytes":cert_bytes,
      "fresh_qhorn_certificate_verified":True,
      "terminal_replay_status":terminal.get("terminal_status"),
      "terminal_replay_stage":terminal.get("terminal_stage"),
      "terminal_replay_verified":True,
      "VERIFIED_DELETION_QHORN_UPPER_BOUND":len(B),
      "number_removed_seed_variables":shrink["number_removed_seed_variables"],
      "number_retained_variables":len(B),
      "number_final_necessity_obstruction_certificates":
          sum(1 for n in necessity if n.get("verified")),
      "final_necessity_audit":necessity,
      "inclusion_minimality_verified":all_verified,
      "inclusion_minimality_meaning":
          "No proper subset of this particular B* is a deletion q-Horn backdoor."
          if all_verified else None,
      "minimum_cardinality_claimed":False,
      "old_stage6A_triple_intersection":mech["old_stage6A_triple_intersection"],
      "mechanism_audit":mech,
      "mechanism_classification":mech["mechanism_classification"],
      "scientific_outcome":outcome,
      "F_minus_B_star_sha256":reduced_sha
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("stage6a_result")
    ap.add_argument("shrink_dir")
    ap.add_argument("output")
    ap.add_argument("--timeout-ms",type=int,default=10000)
    ns=ap.parse_args()

    source_data=json.loads(Path(ns.source).read_text(encoding="utf-8"))
    stage6a=load_stage6a_rows(Path(ns.stage6a_result))
    shrink_dir=Path(ns.shrink_dir)

    rows=[]
    for target in TARGETS:
        p=shrink_dir/f"target_{target:02d}.shrink.json"
        if not p.exists():
            rows.append({
              "target_index":target,
              "scientific_outcome":"INFRASTRUCTURE_ERROR",
              "failure":{"reason":"MISSING_SHRINK_RESULT"},
              "inclusion_minimality_verified":False
            })
            continue
        shrink=json.loads(p.read_text(encoding="utf-8"))
        audited=audit_target(source_data,stage6a[target],shrink,ns.timeout_ms)
        rows.append(audited)
        print(json.dumps({
          "target_index":target,
          "scientific_outcome":audited.get("scientific_outcome"),
          "final_B_star_size":audited.get("final_B_star_size"),
          "inclusion_minimality_verified":audited.get("inclusion_minimality_verified"),
          "mechanism_classification":audited.get("mechanism_classification")
        },sort_keys=True),flush=True)

    counts=dict(collections.Counter(r["scientific_outcome"] for r in rows))
    out={
      "schema":"janus.trump.stage6b2.qhorn_backdoor_witness_transfer_and_shrink.result.v1",
      "gate":"TRUMP_STAGE6B2_QHORN_BACKDOOR_WITNESS_TRANSFER_AND_SHRINK_GATE",
      "rows":rows,
      "verdict_counts":counts,
      "claim_ceiling":{
        "NEW_JANUS_CONTROLLER":"BLOCKED",
        "GENERAL_SAT_IN_P":"NOT_PROVED",
        "P_EQ_NP":"NOT_PROVED",
        "P_VS_NP":"OPEN",
        "INCLUSION_MINIMAL_IS_MINIMUM_CARDINALITY":False,
        "FINITE_B_IMPLIES_O_LOG_N":False,
        "GENERIC_UNSAT_IS_LOWER_BOUND":False,
        "FINITE_CORPUS_RESULT_IS_ASYMPTOTIC_THEOREM":False
      },
      "stage6B3_stage6C_stage6D_executed":False
    }
    Path(ns.output).parent.mkdir(parents=True,exist_ok=True)
    Path(ns.output).write_text(
      json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"verdict_counts":counts},sort_keys=True))


if __name__=="__main__":
    main()
