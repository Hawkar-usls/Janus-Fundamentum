#!/usr/bin/env python3
"""Stage6B.2 Phase B: deterministic proof-carrying witness shrink.

For each canonical transferred seed B, variables are tested in strictly
ascending numeric ID order. A variable is removed from the deletion set only
after an independently verified positive q-Horn certificate for F-(B\\{v}).
A variable is retained only after a verified canonical quadratic-cover
non-q-Horn obstruction. Bare solver UNSAT/UNKNOWN is never negative authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
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
    obstruction_transition,
)
from trump_stage6b2_qhorn_witness_transfer import propose_weights  # noqa: E402


def stable_sha(obj):
    raw=(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest(),len(raw)


def load_stage6a_rows(path:Path):
    d=json.loads(path.read_text(encoding="utf-8"))
    return {int(r["index"]):r for r in d["rows"]}


def obstruction_summary(obs,old_triple):
    if obs is None:
        return None
    path_lengths=[]
    for p in obs.get("paths",[]):
        for key in ("lit_to_complement","complement_to_lit"):
            path=p.get(key) or []
            path_lengths.append({
              "literal":p.get("literal"),
              "direction":key,
              "edge_length":max(0,len(path)-1)
            })
    triple=obs.get("triple") or []
    return {
      "original_clause_index":obs.get("original_clause_index"),
      "triple":triple,
      "path_lengths":path_lengths,
      "uses_old_stage6A_triple":tuple(triple)==tuple(old_triple)
    }


def shrink_target(source_data,stage6a_row,seed,timeout_ms):
    target=int(seed["target_index"])
    row=source_data["residuals"][target]
    original=row["residual_formula"]
    old_obs=((stage6a_row.get("proof") or {}).get("obstruction") or {})
    old_triple=old_obs.get("triple") or []

    if not seed.get("seed_available"):
        return {
          "target_index":target,
          "seed_available":False,
          "shrink_status":"NO_CANONICAL_VERIFIED_SEED",
          "scientific_outcome":
              "INDEX10_TRANSFER_SURVIVOR" if target==10 else "INFRASTRUCTURE_ERROR",
          "inclusion_minimality_eligible":False
        }

    current=sorted(int(v) for v in seed["seed_B"])
    initial=list(current)
    trace=[]
    incomplete=False
    incomplete_reason=None

    for v in sorted(initial):
        if v not in current:
            continue
        candidate=[x for x in current if x!=v]
        reduced=deletion_projection(original,set(candidate))
        reduced_sha=formula_sequence_sha256(reduced)
        t0=time.perf_counter()

        obstruction=build_obstruction(reduced)
        if obstruction is not None:
            ok,detail=verify_obstruction(reduced,obstruction)
            if not ok:
                incomplete=True
                incomplete_reason={
                  "kind":"INFRASTRUCTURE_ERROR",
                  "variable":v,
                  "reason":"GENERATED_OBSTRUCTION_FAILED_INDEPENDENT_REPLAY",
                  "detail":detail
                }
                trace.append({
                  "variable":v,
                  "action":"STOP_INFRASTRUCTURE_ERROR",
                  "candidate_B_size":len(candidate),
                  "F_minus_candidate_B_sha256":reduced_sha,
                  "failure":incomplete_reason,
                  "runtime_seconds":time.perf_counter()-t0
                })
                break

            obs_summary=obstruction_summary(obstruction,old_triple)
            trace.append({
              "variable":v,
              "action":"RETAINED_BY_CERTIFIED_NON_QHORN_OBSTRUCTION",
              "candidate_B_size":len(candidate),
              "F_minus_candidate_B_sha256":reduced_sha,
              "negative_obstruction":obstruction,
              "negative_obstruction_summary":obs_summary,
              "negative_obstruction_verified":True,
              "runtime_seconds":time.perf_counter()-t0
            })
            continue

        proposal=propose_weights(reduced,timeout_ms)
        status=proposal.get("solver_status")

        if status=="SAT":
            ok,detail=verify_weights(reduced,proposal.get("weights"))
            if not ok:
                incomplete=True
                incomplete_reason={
                  "kind":"FAIL_CERTIFICATE",
                  "variable":v,
                  "reason":"POSITIVE_QHORN_CERTIFICATE_FAILED_REPLAY",
                  "detail":detail
                }
                trace.append({
                  "variable":v,
                  "action":"STOP_FAIL_CERTIFICATE",
                  "candidate_B_size":len(candidate),
                  "F_minus_candidate_B_sha256":reduced_sha,
                  "proposal":proposal,
                  "failure":incomplete_reason,
                  "runtime_seconds":time.perf_counter()-t0
                })
                break

            terminal=qhorn_terminal(reduced,detail["weights"])
            if not terminal.get("terminal_replay_verified"):
                incomplete=True
                incomplete_reason={
                  "kind":"INFRASTRUCTURE_ERROR",
                  "variable":v,
                  "reason":"QHORN_TERMINAL_REPLAY_NOT_VERIFIED"
                }
                trace.append({
                  "variable":v,
                  "action":"STOP_INFRASTRUCTURE_ERROR",
                  "candidate_B_size":len(candidate),
                  "F_minus_candidate_B_sha256":reduced_sha,
                  "proposal":proposal,
                  "terminal":terminal,
                  "failure":incomplete_reason,
                  "runtime_seconds":time.perf_counter()-t0
                })
                break

            current=candidate
            transition=obstruction_transition(
                original,reduced,set(current),stage6a_row
            )
            cert_sha,_=stable_sha(proposal["weights"])
            trace.append({
              "variable":v,
              "action":"REMOVABLE_FROM_BACKDOOR",
              "new_B_size":len(current),
              "new_B":list(current),
              "F_minus_new_B_sha256":reduced_sha,
              "fresh_qhorn_certificate_sha256":cert_sha,
              "fresh_qhorn_certificate_verified":True,
              "terminal_status":terminal.get("terminal_status"),
              "terminal_stage":terminal.get("terminal_stage"),
              "terminal_replay_verified":True,
              "old_obstruction_transition_after_removal":transition,
              "runtime_seconds":time.perf_counter()-t0
            })
            continue

        if status=="UNKNOWN":
            incomplete=True
            incomplete_reason={
              "kind":"SHRINK_INCOMPLETE_RESOURCE_LIMIT",
              "variable":v,
              "reason_unknown":proposal.get("reason_unknown")
            }
            trace.append({
              "variable":v,
              "action":"STOP_SHRINK_INCOMPLETE_RESOURCE_LIMIT",
              "candidate_B_size":len(candidate),
              "F_minus_candidate_B_sha256":reduced_sha,
              "proposal":proposal,
              "failure":incomplete_reason,
              "runtime_seconds":time.perf_counter()-t0
            })
            break

        incomplete=True
        incomplete_reason={
          "kind":"INFRASTRUCTURE_ERROR",
          "variable":v,
          "reason":"NO_OBSTRUCTION_BUT_GENERIC_QHORN_PROPOSER_DID_NOT_RETURN_SAT",
          "solver_status":status
        }
        trace.append({
          "variable":v,
          "action":"STOP_INFRASTRUCTURE_ERROR",
          "candidate_B_size":len(candidate),
          "F_minus_candidate_B_sha256":reduced_sha,
          "proposal":proposal,
          "failure":incomplete_reason,
          "runtime_seconds":time.perf_counter()-t0
        })
        break

    final_sha,_=stable_sha(current)
    removed=sorted(set(initial)-set(current))
    retained=sorted(current)

    if incomplete:
        kind=incomplete_reason["kind"]
        scientific_outcome=(
            "SHRINK_INCOMPLETE_RESOURCE_LIMIT"
            if kind=="SHRINK_INCOMPLETE_RESOURCE_LIMIT"
            else kind
        )
    else:
        scientific_outcome="VERIFIED_SHRUNK_DELETION_QHORN_UPPER_BOUND"

    return {
      "target_index":target,
      "seed_available":True,
      "seed_source_index":seed["seed_source_index"],
      "seed_B":initial,
      "seed_B_size":len(initial),
      "seed_B_sha256":seed["seed_B_sha256"],
      "shrink_order":"STRICTLY_ASCENDING_NUMERIC_VARIABLE_ID",
      "trace":trace,
      "shrink_complete":not incomplete,
      "scientific_outcome":scientific_outcome,
      "incomplete_reason":incomplete_reason,
      "final_B_star":current,
      "final_B_star_size":len(current),
      "final_B_star_sha256":final_sha,
      "removed_seed_variables":removed,
      "number_removed_seed_variables":len(removed),
      "retained_variables":retained,
      "number_retained_variables":len(retained),
      "inclusion_minimality_eligible":not incomplete
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("stage6a_result")
    ap.add_argument("canonical_seeds")
    ap.add_argument("outdir")
    ap.add_argument("--timeout-ms",type=int,default=10000)
    ns=ap.parse_args()

    source_data=json.loads(Path(ns.source).read_text(encoding="utf-8"))
    s6a=load_stage6a_rows(Path(ns.stage6a_result))
    seeds=json.loads(Path(ns.canonical_seeds).read_text(encoding="utf-8"))["seeds"]
    outdir=Path(ns.outdir)
    outdir.mkdir(parents=True,exist_ok=True)

    summary=[]
    for seed in seeds:
        target=int(seed["target_index"])
        row=shrink_target(source_data,s6a[target],seed,ns.timeout_ms)
        path=outdir/f"target_{target:02d}.shrink.json"
        path.write_text(json.dumps(row,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        summary.append({
          "target_index":target,
          "seed_source_index":row.get("seed_source_index"),
          "seed_B_size":row.get("seed_B_size"),
          "shrink_complete":row.get("shrink_complete"),
          "scientific_outcome":row.get("scientific_outcome"),
          "final_B_star_size":row.get("final_B_star_size"),
          "number_removed_seed_variables":row.get("number_removed_seed_variables")
        })
        print(json.dumps(summary[-1],sort_keys=True),flush=True)

    (outdir/"shrink_summary.json").write_text(
      json.dumps({
        "schema":"janus.trump.stage6b2.shrink_summary.v1",
        "rows":summary
      },indent=2,sort_keys=True)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
