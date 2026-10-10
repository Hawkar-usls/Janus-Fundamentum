#!/usr/bin/env python3
"""Independent Stage6B.1 bounded deletion-q-Horn verifier and result assembler.

The external Z3/PB solver is a proposer only. This module independently:
  * decodes the D/W0/W1/W2 state witness;
  * verifies |B| <= the preregistered k;
  * reconstructs F-B from the exact frozen CNF;
  * verifies q-Horn weights using frozen Stage6A semantics;
  * replays the polynomial q-Horn terminal;
  * runs the frozen Stage6A obstruction-transition diagnostic.

UNSAT/UNKNOWN are telemetry only. No lower bound or minimality claim is made.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))

from trump_stage6_qhorn_independent_checker import (  # noqa: E402
    formula_sequence_sha256,
    qhorn_terminal,
    verify_weights,
)
from trump_stage6b_deletion_qhorn_independent_checker import (  # noqa: E402
    deletion_projection,
    obstruction_transition,
)

PRIMARY={2,9,10,11,12,13,14}
CONTROLS={1,3,4,5,6,7}
ALLOWED=PRIMARY|CONTROLS
LADDER=[1,2,4,8,16,32]


def file_sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def stable_bytes(obj)->int:
    return len((json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8"))


def stage6a_rows(path:Path):
    d=json.loads(path.read_text(encoding="utf-8"))
    return {int(r["index"]):r for r in d["rows"]}


def decode_states(states,variables):
    expected={str(v) for v in variables}
    if not isinstance(states,dict) or set(states)!=expected:
        return False,None,None,{
          "reason":"STATE_KEY_SET_MISMATCH",
          "missing":sorted(expected-set(states) if isinstance(states,dict) else expected),
          "extra":sorted(set(states)-expected) if isinstance(states,dict) else []
        }

    B=[]
    weights={}
    for v in sorted(variables):
        state=states[str(v)]
        if state not in ("D","W0","W1","W2"):
            return False,None,None,{
              "reason":"INVALID_STATE",
              "variable":v,
              "state":state
            }
        if state=="D":
            B.append(v)
        elif state=="W0":
            weights[str(v)]=0
            weights[str(-v)]=2
        elif state=="W1":
            weights[str(v)]=1
            weights[str(-v)]=1
        else:
            weights[str(v)]=2
            weights[str(-v)]=0

    return True,sorted(B),weights,None


def verify_candidate(source_path:Path,stage6a_path:Path,proposal_path:Path,index:int,expected_k:int):
    t0=time.perf_counter()
    data=json.loads(source_path.read_text(encoding="utf-8"))
    old_rows=stage6a_rows(stage6a_path)
    row=data["residuals"][index]
    clauses=row["residual_formula"]
    variables=sorted({abs(l) for c in clauses for l in c})
    rawsha=formula_sequence_sha256(clauses)
    proposal=json.loads(proposal_path.read_text(encoding="utf-8"))

    base={
      "schema":"janus.trump.stage6b1.bounded_deletion_qhorn_candidate_verification.v1",
      "index":index,
      "role":"PRIMARY_S7" if index in PRIMARY else "CONTROL",
      "k":expected_k,
      "proposal_file":proposal_path.name,
      "proposal_file_sha256":file_sha256(proposal_path),
      "raw_cnf_sha256":rawsha,
      "source_residual_hash":row.get("residual_hash"),
      "solver_status":proposal.get("solver_status"),
      "proposer_runtime_seconds":proposal.get("runtime_seconds"),
      "reason_unknown":proposal.get("reason_unknown"),
      "accepted":False,
      "continue_ladder":False,
      "lower_bound_authority":False,
      "minimum_distance_authority":False
    }

    if (proposal.get("index")!=index or
        proposal.get("k")!=expected_k or
        proposal.get("source_residual_hash")!=row.get("residual_hash") or
        proposal.get("raw_cnf_sha256")!=rawsha):
        base.update({
          "scientific_outcome":"FAIL_CERTIFICATE",
          "failure":{"reason":"PROPOSAL_SOURCE_OR_K_BINDING_MISMATCH"}
        })
        return base

    status=proposal.get("solver_status")
    if status=="UNSAT":
        base.update({
          "telemetry_only":True,
          "continue_ladder":True,
          "scientific_outcome":None,
          "interpretation":"GENERIC_UNSAT_K_IS_DISCOVERY_TELEMETRY_ONLY"
        })
        return base

    if status=="UNKNOWN":
        base.update({
          "telemetry_only":True,
          "continue_ladder":True,
          "scientific_outcome":None,
          "interpretation":"GENERIC_UNKNOWN_IS_DISCOVERY_TELEMETRY_ONLY"
        })
        return base

    if status=="ERROR":
        base.update({
          "scientific_outcome":"INFRASTRUCTURE_ERROR",
          "failure":{
            "reason":"PROPOSER_ERROR",
            "error_type":proposal.get("error_type"),
            "error":proposal.get("error")
          }
        })
        return base

    if status!="SAT":
        base.update({
          "scientific_outcome":"INFRASTRUCTURE_ERROR",
          "failure":{"reason":"UNRECOGNIZED_SOLVER_STATUS","status":status}
        })
        return base

    ok,B,weights,err=decode_states(proposal.get("states"),variables)
    if not ok:
        base.update({"scientific_outcome":"FAIL_CERTIFICATE","failure":err})
        return base

    if len(B)>expected_k:
        base.update({
          "scientific_outcome":"FAIL_CERTIFICATE",
          "failure":{"reason":"B_EXCEEDS_REQUESTED_K","B_size":len(B),"k":expected_k}
        })
        return base

    if proposal.get("B")!=B:
        base.update({
          "scientific_outcome":"FAIL_CERTIFICATE",
          "failure":{
            "reason":"PROPOSER_B_DISAGREES_WITH_STATE_DECODING",
            "proposal_B":proposal.get("B"),
            "decoded_B":B
          }
        })
        return base

    proposed_weights=((proposal.get("qhorn_certificate") or {}).get("weights"))
    if proposed_weights!=weights:
        base.update({
          "scientific_outcome":"FAIL_CERTIFICATE",
          "failure":{"reason":"PROPOSER_WEIGHTS_DISAGREE_WITH_STATE_DECODING"}
        })
        return base

    reduced=deletion_projection(clauses,set(B))
    reduced_sha=formula_sequence_sha256(reduced)

    wok,wdetail=verify_weights(reduced,weights)
    if not wok:
        base.update({
          "scientific_outcome":"FAIL_CERTIFICATE",
          "B":B,
          "B_size":len(B),
          "F_minus_B_sha256":reduced_sha,
          "failure":{"reason":"INDEPENDENT_QHORN_CERTIFICATE_FAIL","detail":wdetail}
        })
        return base

    terminal=qhorn_terminal(reduced,wdetail["weights"])
    if not terminal.get("terminal_replay_verified"):
        base.update({
          "scientific_outcome":"INFRASTRUCTURE_ERROR",
          "B":B,
          "B_size":len(B),
          "F_minus_B_sha256":reduced_sha,
          "failure":{"reason":"QHORN_TERMINAL_REPLAY_NOT_VERIFIED"},
          "terminal":terminal
        })
        return base

    old=old_rows.get(index)
    if old is None or old.get("verdict")!="CERTIFIED_NOT_QHORN":
        base.update({
          "scientific_outcome":"INFRASTRUCTURE_ERROR",
          "failure":{"reason":"MISSING_CANONICAL_STAGE6A_NEGATIVE_PROOF"}
        })
        return base

    transition=obstruction_transition(
        clauses,reduced,set(B),old
    )

    # The positive beta/w certificate is scientific authority. The transition
    # audit is descriptive; disagreement here is reported but cannot invalidate B.
    diagnostic_consistent=bool(transition.get("rebuilt_obstruction_absent"))

    witness={
      "B":B,
      "weights":weights,
      "F_minus_B_sha256":reduced_sha
    }

    base.update({
      "accepted":True,
      "continue_ladder":False,
      "scientific_outcome":"PASS_QHORN_DELETION_BACKDOOR_STRUCTURAL_ONLY",
      "B":B,
      "B_size":len(B),
      "VERIFIED_DELETION_QHORN_UPPER_BOUND":len(B),
      "first_successful_k_is_minimum":False,
      "F_minus_B_sha256":reduced_sha,
      "F_minus_B_clause_count":len(reduced),
      "F_minus_B_literal_occurrence_count":sum(len(c) for c in reduced),
      "qhorn_certificate_verified":True,
      "qhorn_certificate_bytes":stable_bytes(weights),
      "witness_bytes":stable_bytes(witness),
      "terminal":terminal,
      "terminal_replay_verified":True,
      "obstruction_transition_diagnostic":transition,
      "obstruction_transition_diagnostic_consistent_with_positive_certificate":diagnostic_consistent,
      "checker_runtime_seconds":time.perf_counter()-t0
    })
    return base


def finalize_index(index:int,attempt_dir:Path,output:Path):
    attempts=[]
    terminal_failure=None
    accepted=None

    for k in LADDER:
        vp=attempt_dir/f"k_{k:02d}.verification.json"
        if not vp.exists():
            continue
        v=json.loads(vp.read_text(encoding="utf-8"))
        attempts.append(v)
        if v.get("accepted"):
            accepted=v
            break
        if v.get("scientific_outcome") in ("FAIL_CERTIFICATE","INFRASTRUCTURE_ERROR"):
            terminal_failure=v
            break

    if accepted is not None:
        final={
          "index":index,
          "role":"PRIMARY_S7" if index in PRIMARY else "CONTROL",
          "scientific_outcome":"PASS_QHORN_DELETION_BACKDOOR_STRUCTURAL_ONLY",
          "accepted_k":accepted["k"],
          "B":accepted["B"],
          "B_size":accepted["B_size"],
          "VERIFIED_DELETION_QHORN_UPPER_BOUND":accepted["VERIFIED_DELETION_QHORN_UPPER_BOUND"],
          "first_successful_k_is_minimum":False,
          "accepted_verification":accepted,
          "per_k_telemetry":[{
            "k":a["k"],
            "solver_status":a.get("solver_status"),
            "runtime_seconds":a.get("proposer_runtime_seconds"),
            "reason_unknown":a.get("reason_unknown"),
            "proposal_sha256":a.get("proposal_file_sha256"),
            "accepted":a.get("accepted",False)
          } for a in attempts]
        }
    elif terminal_failure is not None:
        final={
          "index":index,
          "role":"PRIMARY_S7" if index in PRIMARY else "CONTROL",
          "scientific_outcome":terminal_failure["scientific_outcome"],
          "failure":terminal_failure.get("failure"),
          "per_k_telemetry":[{
            "k":a["k"],
            "solver_status":a.get("solver_status"),
            "runtime_seconds":a.get("proposer_runtime_seconds"),
            "reason_unknown":a.get("reason_unknown"),
            "proposal_sha256":a.get("proposal_file_sha256"),
            "accepted":a.get("accepted",False)
          } for a in attempts]
        }
    else:
        final={
          "index":index,
          "role":"PRIMARY_S7" if index in PRIMARY else "CONTROL",
          "scientific_outcome":"NO_VERIFIED_B_WITHIN_PREREGISTERED_FEASIBILITY_BUDGET",
          "meaning_only":"The frozen discovery procedure did not obtain an independently accepted witness.",
          "not_claimed":[
            "NO_B_EXISTS",
            "DELETION_DISTANCE_GT_32",
            "DELETION_DISTANCE_IS_LARGE",
            "ANY_LOWER_BOUND"
          ],
          "per_k_telemetry":[{
            "k":a["k"],
            "solver_status":a.get("solver_status"),
            "runtime_seconds":a.get("proposer_runtime_seconds"),
            "reason_unknown":a.get("reason_unknown"),
            "proposal_sha256":a.get("proposal_file_sha256"),
            "accepted":a.get("accepted",False)
          } for a in attempts]
        }

    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(final,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return final


def aggregate(final_dir:Path,output:Path,source_binding:Path,prereg_commit:str,proposer_commit:str,checker_commit:str,implementation_head:str):
    rows=[]
    for i in [2,9,10,11,12,13,14,1,3,4,5,6,7]:
        p=final_dir/f"r50g25x_{i:02d}.final.json"
        if not p.exists():
            rows.append({
              "index":i,
              "role":"PRIMARY_S7" if i in PRIMARY else "CONTROL",
              "scientific_outcome":"INFRASTRUCTURE_ERROR",
              "failure":{"reason":"MISSING_FINAL_INDEX_RESULT"}
            })
        else:
            rows.append(json.loads(p.read_text(encoding="utf-8")))

    counts=dict(collections.Counter(r["scientific_outcome"] for r in rows))
    out={
      "schema":"janus.trump.stage6b1.bounded_deletion_qhorn_feasibility_gate.result.v1",
      "authority":"PUBLIC_GENERIC_BOUNDED_FEASIBILITY_PROPOSAL_PLUS_INDEPENDENT_WITNESS_VERIFICATION",
      "gate":"TRUMP_STAGE6B1_BOUNDED_DELETION_QHORN_FEASIBILITY_GATE",
      "prereg_commit":prereg_commit,
      "proposer_commit":proposer_commit,
      "checker_commit":checker_commit,
      "implementation_head":implementation_head,
      "source_binding":json.loads(source_binding.read_text(encoding="utf-8")),
      "k_ladder":LADDER,
      "per_k_timeout_ms":10000,
      "rows":rows,
      "verdict_counts":counts,
      "claim_ceiling":{
        "NEW_JANUS_CONTROLLER":"BLOCKED",
        "GENERAL_SAT_IN_P":"NOT_PROVED",
        "P_EQ_NP":"NOT_PROVED",
        "P_VS_NP":"OPEN",
        "GENERIC_UNSAT_K_IS_LOWER_BOUND":False,
        "FIRST_SUCCESSFUL_K_IS_MINIMUM":False,
        "FINITE_VERIFIED_B_IMPLIES_O_LOG_N":False,
        "FINITE_CORPUS_RESULT_IS_ASYMPTOTIC_THEOREM":False
      },
      "stage6C_stage6D_executed":False
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "verdict_counts":counts,
      "rows":[{
        "index":r["index"],
        "scientific_outcome":r["scientific_outcome"],
        "accepted_k":r.get("accepted_k"),
        "B_size":r.get("B_size"),
        "VERIFIED_DELETION_QHORN_UPPER_BOUND":r.get("VERIFIED_DELETION_QHORN_UPPER_BOUND")
      } for r in rows]
    },sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)

    v=sub.add_parser("verify")
    v.add_argument("source")
    v.add_argument("stage6a_result")
    v.add_argument("proposal")
    v.add_argument("output")
    v.add_argument("--index",type=int,required=True)
    v.add_argument("--k",type=int,required=True)

    f=sub.add_parser("finalize-index")
    f.add_argument("attempt_dir")
    f.add_argument("output")
    f.add_argument("--index",type=int,required=True)

    a=sub.add_parser("aggregate")
    a.add_argument("final_dir")
    a.add_argument("output")
    a.add_argument("source_binding")
    a.add_argument("--prereg-commit",required=True)
    a.add_argument("--proposer-commit",required=True)
    a.add_argument("--checker-commit",required=True)
    a.add_argument("--implementation-head",required=True)

    ns=ap.parse_args()

    if ns.cmd=="verify":
        obj=verify_candidate(
          Path(ns.source),Path(ns.stage6a_result),Path(ns.proposal),
          ns.index,ns.k
        )
        Path(ns.output).parent.mkdir(parents=True,exist_ok=True)
        Path(ns.output).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps({
          "index":ns.index,
          "k":ns.k,
          "solver_status":obj.get("solver_status"),
          "accepted":obj.get("accepted"),
          "continue_ladder":obj.get("continue_ladder"),
          "scientific_outcome":obj.get("scientific_outcome"),
          "B_size":obj.get("B_size")
        },sort_keys=True))
    elif ns.cmd=="finalize-index":
        obj=finalize_index(ns.index,Path(ns.attempt_dir),Path(ns.output))
        print(json.dumps({
          "index":ns.index,
          "scientific_outcome":obj["scientific_outcome"],
          "accepted_k":obj.get("accepted_k"),
          "B_size":obj.get("B_size")
        },sort_keys=True))
    else:
        aggregate(
          Path(ns.final_dir),Path(ns.output),Path(ns.source_binding),
          ns.prereg_commit,ns.proposer_commit,ns.checker_commit,
          ns.implementation_head
        )


if __name__=="__main__":
    main()
