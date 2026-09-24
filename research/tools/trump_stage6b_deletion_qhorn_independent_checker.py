#!/usr/bin/env python3
"""Independent Stage6B deletion-q-Horn witness checker.

The external optimizer is a proposer only. This checker:
  * binds B to the exact frozen residual;
  * independently constructs F-B from the raw frozen CNF;
  * verifies the q-Horn weight certificate using the frozen Stage6A logic;
  * records only a verified finite upper bound dist_del-qHorn(F) <= |B|;
  * optionally replays the q-Horn polynomial terminal on F-B;
  * performs a descriptive transition audit of the frozen Stage6A obstruction.

No optimizer optimality/minimality claim is scientific authority here.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

# Import the already-frozen Stage6A independent authority logic.
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))

from trump_stage6_qhorn_independent_checker import (  # noqa: E402
    build_obstruction,
    formula_sequence_sha256,
    quadratic_cover,
    qhorn_terminal,
    verify_weights,
)

PRIMARY={2,9,10,11,12,13,14}
CONTROLS={1,3,4,5,6,7}
ALLOWED=PRIMARY|CONTROLS


def file_sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def cert_bytes(obj)->int:
    return len((json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8"))


def deletion_projection(clauses,B:set[int]):
    # Preserve original clause order and surviving literal occurrence order.
    return [[lit for lit in clause if abs(lit) not in B] for clause in clauses]


def load_stage6a_rows(path:Path):
    data=json.loads(path.read_text(encoding="utf-8"))
    return {int(r["index"]):r for r in data["rows"]},data


def old_edge_responsible_deleted_variable(original_clauses,old_src,a,b,B):
    candidates=set()
    ambiguous_aux=False
    for src in old_src.get((a,b),[]):
        ci=src.get("clause")
        kind=src.get("kind")
        j=src.get("i")
        if not isinstance(ci,int) or not (0<=ci<len(original_clauses)):
            continue
        clause=[lit for _,lit in sorted(enumerate(original_clauses[ci]),
                                        key=lambda z:(abs(z[1]),z[0]))]
        v=None
        if kind=="LI_Y" and isinstance(j,int) and 1<=j<len(clause):
            v=abs(clause[j-1])
        elif kind=="NY_LNEXT" and isinstance(j,int) and 1<=j<len(clause):
            v=abs(clause[j])
        elif kind=="NY_YNEXT":
            ambiguous_aux=True
        if v in B:
            candidates.add(v)
    if len(candidates)==1 and not ambiguous_aux:
        return next(iter(candidates))
    return None


def path_transition(original_clauses,reduced_clauses,B,old_path):
    old_adj,old_src,_=quadratic_cover(original_clauses)
    new_adj,_,_=quadratic_cover(reduced_clauses)

    if not isinstance(old_path,list) or len(old_path)<1:
        return {"old_path_valid_format":False}

    # Sanity-check that the frozen old path really was an old F2 path.
    old_missing=[]
    for a,b in zip(old_path,old_path[1:]):
        if b not in old_adj.get(a,set()):
            old_missing.append([a,b])

    first_missing=None
    for a,b in zip(old_path,old_path[1:]):
        if b not in new_adj.get(a,set()):
            first_missing={
              "edge":[a,b],
              "deleted_variable_responsible_when_well_defined":
                  old_edge_responsible_deleted_variable(
                      original_clauses,old_src,a,b,B
                  )
            }
            break

    return {
      "old_path_valid_in_original_F2":not old_missing,
      "old_path_invalid_edges_in_original_F2":old_missing,
      "survives_verbatim_in_F2_of_F_minus_B":first_missing is None,
      "first_missing_edge":first_missing,
      "attribution_note":
        "Auxiliary chain renumbering after deletion can break an old path without a unique local deleted-variable attribution."
    }


def obstruction_transition(original_clauses,reduced_clauses,B,stage6a_row):
    proof=(stage6a_row.get("proof") or {})
    old=(proof.get("obstruction") or {})
    triple=old.get("triple") or []
    triple_vars=sorted({abs(int(l)) for l in triple})
    intersection=sorted(set(triple_vars)&B)

    out={
      "old_stage6A_verdict":stage6a_row.get("verdict"),
      "old_triple":triple,
      "old_triple_variables":triple_vars,
      "B_intersects_old_triple_variables":bool(intersection),
      "intersection":intersection,
      "path_replay_required_by_prereg":not bool(intersection)
    }

    if not intersection:
        transitions=[]
        for p in old.get("paths",[]):
            lit=p.get("literal")
            for key in ("lit_to_complement","complement_to_lit"):
                transitions.append({
                  "literal":lit,
                  "direction":key,
                  "transition":path_transition(
                      original_clauses,reduced_clauses,B,p.get(key)
                  )
                })
        out["old_path_transitions"]=transitions
        out["broken_old_path_count"]=sum(
            not x["transition"].get("survives_verbatim_in_F2_of_F_minus_B",False)
            for x in transitions
        )

    rebuilt=build_obstruction(reduced_clauses)
    out["rebuilt_F2_violating_triple_after_deletion"]=rebuilt
    out["rebuilt_obstruction_absent"]=rebuilt is None
    return out


def validate_B(raw_B,variables):
    if not isinstance(raw_B,list):
        return False,None,{"reason":"B_NOT_LIST"}
    if any(isinstance(v,bool) or not isinstance(v,int) for v in raw_B):
        return False,None,{"reason":"B_NONINTEGER_MEMBER","B":raw_B}
    if len(set(raw_B))!=len(raw_B):
        return False,None,{"reason":"B_DUPLICATE_MEMBER","B":raw_B}
    B=set(raw_B)
    extra=sorted(B-set(variables))
    if extra:
        return False,None,{"reason":"B_NOT_SUBSET_OF_ORIGINAL_VARIABLES","extra":extra}
    return True,B,None


def check_one(row,index,proposal,stage6a_row,source_binding):
    t0=time.perf_counter()
    clauses=row["residual_formula"]
    variables={abs(l) for c in clauses for l in c}
    rawsha=formula_sequence_sha256(clauses)

    base={
      "index":index,
      "role":"PRIMARY_S7" if index in PRIMARY else "CONTROL",
      "family":row.get("family"),
      "source_residual_hash":row.get("residual_hash"),
      "raw_cnf_sha256":rawsha,
      "normalization_applied":False,
      "source_binding":source_binding,
      "PROPOSER_REPORTED_OBJECTIVE":proposal.get("PROPOSER_REPORTED_OBJECTIVE"),
      "optimizer_status":proposal.get("optimizer_status"),
      "optimizer_reported_lower_bound":proposal.get("optimizer_reported_lower_bound"),
      "optimizer_reported_upper_bound":proposal.get("optimizer_reported_upper_bound")
    }

    if (proposal.get("index")!=index or
        proposal.get("source_residual_hash")!=row.get("residual_hash") or
        proposal.get("raw_cnf_sha256")!=rawsha):
        base.update({
          "verdict":"FAIL_CERTIFICATE",
          "failure":{"reason":"PROPOSAL_SOURCE_BINDING_MISMATCH"}
        })
        return base

    status=proposal.get("optimizer_status")
    if status=="UNKNOWN":
        base.update({
          "verdict":"UNKNOWN_RESOURCE_LIMIT",
          "reason_unknown":proposal.get("reason_unknown"),
          "minimum_distance_claimed":False
        })
        return base

    if status=="ERROR":
        base.update({
          "verdict":"INFRASTRUCTURE_ERROR",
          "failure":{
            "reason":"PROPOSER_ERROR",
            "error_type":proposal.get("error_type"),
            "error":proposal.get("error")
          }
        })
        return base

    if status!="SAT":
        # Full variable deletion is always a structural feasible point, so a
        # generic UNSAT/other status is not lower-bound authority.
        base.update({
          "verdict":"INFRASTRUCTURE_ERROR",
          "failure":{
            "reason":"NON_SAT_OPTIMIZER_STATUS_HAS_NO_NEGATIVE_AUTHORITY",
            "status":status
          },
          "generic_solver_negative_authority":False
        })
        return base

    ok,B,err=validate_B(proposal.get("B"),variables)
    if not ok:
        base.update({"verdict":"FAIL_CERTIFICATE","failure":err})
        return base

    reduced=deletion_projection(clauses,B)
    reduced_sha=formula_sequence_sha256(reduced)

    weights=((proposal.get("qhorn_certificate") or {}).get("weights"))
    wok,wdetail=verify_weights(reduced,weights)
    if not wok:
        base.update({
          "verdict":"FAIL_CERTIFICATE",
          "B":sorted(B),
          "B_size":len(B),
          "F_minus_B_sha256":reduced_sha,
          "failure":{"reason":"QHORN_CERTIFICATE_FAIL","detail":wdetail}
        })
        return base

    transition=obstruction_transition(
        clauses,reduced,B,stage6a_row
    )
    if not transition["rebuilt_obstruction_absent"]:
        # A verified beta certificate and a verified q-Horn obstruction cannot
        # coexist. Treat this as checker/infrastructure inconsistency.
        base.update({
          "verdict":"INFRASTRUCTURE_ERROR",
          "B":sorted(B),
          "B_size":len(B),
          "F_minus_B_sha256":reduced_sha,
          "qhorn_certificate_verified":True,
          "failure":{"reason":"POSITIVE_QHORN_CERTIFICATE_CONTRADICTS_REBUILT_OBSTRUCTION"},
          "obstruction_transition_diagnostic":transition
        })
        return base

    terminal=qhorn_terminal(reduced,wdetail["weights"])
    terminal_ok=bool(terminal.get("terminal_replay_verified"))
    if not terminal_ok:
        base.update({
          "verdict":"INFRASTRUCTURE_ERROR",
          "B":sorted(B),
          "B_size":len(B),
          "F_minus_B_sha256":reduced_sha,
          "qhorn_certificate_verified":True,
          "failure":{"reason":"OPTIONAL_QHORN_TERMINAL_CONSISTENCY_REPLAY_FAILED"},
          "qhorn_terminal_consistency":terminal,
          "obstruction_transition_diagnostic":transition
        })
        return base

    witness={
      "B":sorted(B),
      "qhorn_weights":weights,
      "F_minus_B_sha256":reduced_sha
    }

    base.update({
      "verdict":"PASS_QHORN_DELETION_BACKDOOR_STRUCTURAL_ONLY",
      "B":sorted(B),
      "B_size":len(B),
      "VERIFIED_DELETION_QHORN_UPPER_BOUND":len(B),
      "minimum_deletion_qhorn_distance_claimed":False,
      "F_minus_B_sha256":reduced_sha,
      "F_minus_B_clause_count":len(reduced),
      "F_minus_B_literal_occurrence_count":sum(len(c) for c in reduced),
      "qhorn_certificate_verified":True,
      "qhorn_certificate_bytes":cert_bytes(weights),
      "witness_bytes":cert_bytes(witness),
      "qhorn_terminal_consistency":{
        "verified":True,
        "terminal_status":terminal.get("terminal_status"),
        "terminal_stage":terminal.get("terminal_stage")
      },
      "obstruction_transition_diagnostic":transition,
      "proposer_runtime_seconds":proposal.get("runtime_seconds"),
      "checker_runtime_seconds":time.perf_counter()-t0
    })
    return base


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("proposals")
    ap.add_argument("stage6a_result")
    ap.add_argument("output")
    ap.add_argument("--indices",required=True)
    ap.add_argument("--source-artifact-metadata")
    ap.add_argument("--source-zip-sha256-file")
    ap.add_argument("--stage6a-artifact-metadata")
    ap.add_argument("--stage6a-zip-sha256-file")
    ap.add_argument("--prereg-commit",required=True)
    ap.add_argument("--proposer-commit",required=True)
    ap.add_argument("--implementation-head",default="")
    ns=ap.parse_args()

    source=Path(ns.source)
    propdir=Path(ns.proposals)
    stage6a_result_path=Path(ns.stage6a_result)
    outp=Path(ns.output)

    data=json.loads(source.read_text(encoding="utf-8"))
    stage6a_rows,stage6a_data=load_stage6a_rows(stage6a_result_path)
    indices=[int(x) for x in ns.indices.split(",") if x.strip()]
    if set(indices)!=ALLOWED:
        raise SystemExit(f"INDEX_CONTRACT_MISMATCH {indices}")

    source_meta={}
    if ns.source_artifact_metadata:
        source_meta=json.loads(Path(ns.source_artifact_metadata).read_text(encoding="utf-8"))
    stage6a_meta={}
    if ns.stage6a_artifact_metadata:
        stage6a_meta=json.loads(Path(ns.stage6a_artifact_metadata).read_text(encoding="utf-8"))

    source_binding={
      "source_artifact_id":9992845123,
      "source_artifact_api_digest":source_meta.get("digest"),
      "source_artifact_workflow_head_sha":(source_meta.get("workflow_run") or {}).get("head_sha"),
      "downloaded_source_zip_sha256":
          Path(ns.source_zip_sha256_file).read_text().split()[0]
          if ns.source_zip_sha256_file else None,
      "source_json_sha256":file_sha256(source),
      "stage6A_artifact_id":10584038105,
      "stage6A_artifact_api_digest":stage6a_meta.get("digest"),
      "downloaded_stage6A_zip_sha256":
          Path(ns.stage6a_zip_sha256_file).read_text().split()[0]
          if ns.stage6a_zip_sha256_file else None,
      "stage6A_result_sha256":file_sha256(stage6a_result_path),
      "stage6A_result_freeze_commit":"27676d521b57c113996c482726657abe1de5f34b"
    }

    rows=[]
    for i in indices:
        pp=propdir/f"r50g25x_{i:02d}.proposal.json"
        if not pp.exists():
            rows.append({
              "index":i,
              "role":"PRIMARY_S7" if i in PRIMARY else "CONTROL",
              "verdict":"INFRASTRUCTURE_ERROR",
              "failure":{"reason":"MISSING_PROPOSAL_FILE"}
            })
            continue
        proposal=json.loads(pp.read_text(encoding="utf-8"))
        old=stage6a_rows.get(i)
        if old is None or old.get("verdict")!="CERTIFIED_NOT_QHORN":
            rows.append({
              "index":i,
              "role":"PRIMARY_S7" if i in PRIMARY else "CONTROL",
              "verdict":"INFRASTRUCTURE_ERROR",
              "failure":{"reason":"MISSING_OR_NONCANONICAL_STAGE6A_OBSTRUCTION"}
            })
            continue
        row=check_one(data["residuals"][i],i,proposal,old,source_binding)
        row["proposal_file"]=pp.name
        row["proposal_file_sha256"]=file_sha256(pp)
        row["proposal_file_bytes"]=pp.stat().st_size
        rows.append(row)

    out={
      "schema":"janus.trump.stage6b.deletion_qhorn_certificate_gate.result.v1",
      "authority":"EXTERNAL_GENERIC_OPTIMIZATION_PROPOSAL_PLUS_INDEPENDENT_DELETION_AND_QHORN_WITNESS_REPLAY",
      "gate":"TRUMP_STAGE6B_DELETION_QHORN_CERTIFICATE_GATE",
      "prereg_commit":ns.prereg_commit,
      "proposer_commit":ns.proposer_commit,
      "implementation_head":ns.implementation_head,
      "source_binding":source_binding,
      "indices":indices,
      "rows":rows,
      "verdict_counts":dict(collections.Counter(r["verdict"] for r in rows)),
      "minimality_firewall":{
        "optimizer_objective_is_minimum_distance_authority":False,
        "verified_statement_for_each_pass":"dist_del-qHorn(F) <= |B|",
        "exact_minimum_claimed":False
      },
      "claim_ceiling":{
        "new_janus_controller_authorized":False,
        "general_sat_in_p":"NOT_PROVED",
        "p_eq_np":"NOT_PROVED",
        "p_vs_np":"OPEN",
        "finite_corpus_results_are_asymptotic_theorems":False
      },
      "stage6C_stage6D_executed":False
    }

    outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "verdict_counts":out["verdict_counts"],
      "rows":[{
        "index":r["index"],
        "verdict":r["verdict"],
        "B_size":r.get("B_size"),
        "PROPOSER_REPORTED_OBJECTIVE":r.get("PROPOSER_REPORTED_OBJECTIVE"),
        "VERIFIED_DELETION_QHORN_UPPER_BOUND":r.get("VERIFIED_DELETION_QHORN_UPPER_BOUND")
      } for r in rows]
    },sort_keys=True))


if __name__=="__main__":
    main()
