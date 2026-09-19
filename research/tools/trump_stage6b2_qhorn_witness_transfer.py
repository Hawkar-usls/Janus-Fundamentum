#!/usr/bin/env python3
"""Stage6B.2 Phase A: frozen witness transfer matrix + canonical seed selection.

External Z3 is proposal-only. For each exact Stage6B.1 witness B_s and target
frozen residual F_t, this script:
  * refuses projection/repair if B_s is not a subset of var(F_t);
  * independently constructs F_t-B_s from the raw target CNF;
  * obtains a fresh generic Z3 q-Horn weight proposal;
  * independently verifies that weight certificate with the frozen Stage6A
    verifier semantics;
  * emits the complete source-target transfer matrix;
  * selects one canonical seed per target only after the matrix is complete.

No transfer failure is a lower bound or hardness statement.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.metadata
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
from trump_stage6b_deletion_qhorn_independent_checker import deletion_projection  # noqa: E402

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


def extract_sealed_witnesses(stage6b1):
    witnesses=[]
    for row in stage6b1["rows"]:
        if row.get("scientific_outcome")!="PASS_QHORN_DELETION_BACKDOOR_STRUCTURAL_ONLY":
            continue
        idx=int(row["index"])
        B=sorted(int(v) for v in row["B"])
        bsha,_=stable_sha(B)
        witnesses.append({
          "source_index":idx,
          "B":B,
          "B_size":len(B),
          "B_sha256":bsha,
          "stage6b1_upper_bound":row.get("VERIFIED_DELETION_QHORN_UPPER_BOUND")
        })
    witnesses.sort(key=lambda w:w["source_index"])
    if len(witnesses)!=12:
        raise RuntimeError(f"EXPECTED_12_SEALED_STAGE6B1_WITNESSES_GOT_{len(witnesses)}")
    return witnesses


def propose_weights(clauses,timeout_ms):
    import z3
    variables=sorted({abs(l) for c in clauses for l in c})
    s=z3.Solver()
    s.set(timeout=timeout_ms)
    w={v:z3.Int(f"w_{v}") for v in variables}
    for v in variables:
        s.add(w[v]>=0,w[v]<=2)
    for c in clauses:
        terms=[]
        for lit in c:  # preserve every surviving literal occurrence
            p=w[abs(lit)]
            terms.append(p if lit>0 else 2-p)
        s.add(z3.Sum(terms)<=2)
    t0=time.perf_counter()
    status=s.check()
    runtime=time.perf_counter()-t0
    out={
      "tool":{
        "name":"z3-solver",
        "mode":"Solver_direct_qHorn_weight_proposal",
        "package_version":importlib.metadata.version("z3-solver"),
        "z3_version":z3.get_version_string()
      },
      "timeout_ms":timeout_ms,
      "runtime_seconds":runtime,
      "solver_status":str(status).upper(),
      "authority":"EXTERNAL_GENERIC_PROPOSER_ONLY"
    }
    if status==z3.sat:
        m=s.model()
        weights={}
        for v in variables:
            p=m.eval(w[v],model_completion=True).as_long()
            weights[str(v)]=p
            weights[str(-v)]=2-p
        out["weights"]=weights
        out["weights_sha256"],out["weights_bytes"]=stable_sha(weights)
    elif status==z3.unknown:
        out["reason_unknown"]=s.reason_unknown()
    return out


def run_pair(source_data,witness,target_index,outdir,timeout_ms):
    source_index=witness["source_index"]
    B=list(witness["B"])
    target_row=source_data["residuals"][target_index]
    clauses=target_row["residual_formula"]
    target_vars={abs(l) for c in clauses for l in c}
    pair_id=f"source_{source_index:02d}__target_{target_index:02d}"
    pair_dir=outdir/"pairs"/pair_id
    pair_dir.mkdir(parents=True,exist_ok=True)

    base={
      "source_index":source_index,
      "target_index":target_index,
      "source_B":B,
      "source_B_size":len(B),
      "source_B_sha256":witness["B_sha256"],
      "target_residual_hash":target_row.get("residual_hash"),
      "target_raw_cnf_sha256":formula_sequence_sha256(clauses)
    }

    missing=sorted(set(B)-target_vars)
    if missing:
        result={
          **base,
          "transfer_status":"TRANSFER_NOT_APPLICABLE_VARIABLE_SET_MISMATCH",
          "missing_variables":missing,
          "B_projected_or_repaired":False,
          "transfer_verified":False
        }
        (pair_dir/"verification.json").write_text(
            json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        return result

    reduced=deletion_projection(clauses,set(B))
    reduced_sha=formula_sequence_sha256(reduced)
    proposal=propose_weights(reduced,timeout_ms)
    proposal_receipt={
      **base,
      "F_target_minus_B_sha256":reduced_sha,
      "F_target_minus_B_clause_count":len(reduced),
      "F_target_minus_B_literal_occurrence_count":sum(len(c) for c in reduced),
      **proposal
    }
    proposal_path=pair_dir/"proposal.json"
    proposal_path.write_text(
        json.dumps(proposal_receipt,indent=2,sort_keys=True)+"\n",
        encoding="utf-8")
    proposal_sha=file_sha256(proposal_path)

    status=proposal["solver_status"]
    if status=="SAT":
        ok,detail=verify_weights(reduced,proposal.get("weights"))
        if not ok:
            result={
              **base,
              "F_target_minus_B_sha256":reduced_sha,
              "proposal_sha256":proposal_sha,
              "transfer_status":"FAIL_CERTIFICATE",
              "transfer_verified":False,
              "failure":detail
            }
        else:
            terminal=qhorn_terminal(reduced,detail["weights"])
            result={
              **base,
              "F_target_minus_B_sha256":reduced_sha,
              "proposal_sha256":proposal_sha,
              "fresh_qhorn_certificate_sha256":proposal.get("weights_sha256"),
              "fresh_qhorn_certificate_verified":True,
              "terminal_replay_status":terminal.get("terminal_status"),
              "terminal_replay_verified":bool(terminal.get("terminal_replay_verified")),
              "transfer_status":"TRANSFER_VERIFIED",
              "transfer_verified":True,
              "VERIFIED_DELETION_QHORN_UPPER_BOUND":len(B),
              "proposer_runtime_seconds":proposal.get("runtime_seconds")
            }
    elif status=="UNSAT":
        result={
          **base,
          "F_target_minus_B_sha256":reduced_sha,
          "proposal_sha256":proposal_sha,
          "transfer_status":"TRANSFER_NOT_VERIFIED_PROPOSER_UNSAT_TELEMETRY",
          "transfer_verified":False,
          "proposer_runtime_seconds":proposal.get("runtime_seconds"),
          "negative_authority":False
        }
    elif status=="UNKNOWN":
        result={
          **base,
          "F_target_minus_B_sha256":reduced_sha,
          "proposal_sha256":proposal_sha,
          "transfer_status":"TRANSFER_NOT_VERIFIED_RESOURCE_LIMIT",
          "transfer_verified":False,
          "proposer_runtime_seconds":proposal.get("runtime_seconds"),
          "reason_unknown":proposal.get("reason_unknown"),
          "negative_authority":False
        }
    else:
        result={
          **base,
          "F_target_minus_B_sha256":reduced_sha,
          "proposal_sha256":proposal_sha,
          "transfer_status":"INFRASTRUCTURE_ERROR",
          "transfer_verified":False,
          "failure":{"reason":"UNRECOGNIZED_PROPOSER_STATUS","status":status}
        }

    (pair_dir/"verification.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result


def select_seeds(matrix):
    by_target=collections.defaultdict(list)
    for row in matrix:
        if row.get("transfer_verified"):
            by_target[int(row["target_index"])].append(row)

    seeds=[]
    for t in TARGETS:
        candidates=by_target.get(t,[])
        if not candidates:
            seeds.append({
              "target_index":t,
              "seed_available":False,
              "canonical_selection_rule":[
                "SMALLEST_B_SIZE",
                "SMALLEST_SOURCE_RESIDUAL_INDEX",
                "LEXICOGRAPHICALLY_SMALLEST_SORTED_B"
              ]
            })
            continue
        candidates=sorted(
          candidates,
          key=lambda r:(int(r["source_B_size"]),int(r["source_index"]),tuple(r["source_B"]))
        )
        best=candidates[0]
        seeds.append({
          "target_index":t,
          "seed_available":True,
          "seed_source_index":best["source_index"],
          "seed_B":best["source_B"],
          "seed_B_size":best["source_B_size"],
          "seed_B_sha256":best["source_B_sha256"],
          "initial_verified_upper_bound":best["VERIFIED_DELETION_QHORN_UPPER_BOUND"],
          "canonical_selection_rule":[
            "SMALLEST_B_SIZE",
            "SMALLEST_SOURCE_RESIDUAL_INDEX",
            "LEXICOGRAPHICALLY_SMALLEST_SORTED_B"
          ],
          "candidate_count":len(candidates)
        })
    return seeds


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("stage6b1_result")
    ap.add_argument("outdir")
    ap.add_argument("--timeout-ms",type=int,default=10000)
    ns=ap.parse_args()

    source_path=Path(ns.source)
    b1_path=Path(ns.stage6b1_result)
    outdir=Path(ns.outdir)
    outdir.mkdir(parents=True,exist_ok=True)

    source_data=json.loads(source_path.read_text(encoding="utf-8"))
    b1=json.loads(b1_path.read_text(encoding="utf-8"))
    witnesses=extract_sealed_witnesses(b1)

    (outdir/"sealed_witnesses.json").write_text(
      json.dumps({
        "stage6b1_result_sha256":file_sha256(b1_path),
        "witness_count":len(witnesses),
        "witnesses":witnesses
      },indent=2,sort_keys=True)+"\n",encoding="utf-8")

    matrix=[]
    for witness in witnesses:
        for target in TARGETS:
            row=run_pair(source_data,witness,target,outdir,ns.timeout_ms)
            matrix.append(row)
            print(json.dumps({
              "source":witness["source_index"],
              "target":target,
              "status":row["transfer_status"],
              "verified":row.get("transfer_verified",False)
            },sort_keys=True),flush=True)

    seeds=select_seeds(matrix)
    matrix_obj={
      "schema":"janus.trump.stage6b2.transfer_matrix.v1",
      "source_witness_count":len(witnesses),
      "target_count":len(TARGETS),
      "pair_count":len(matrix),
      "rows":matrix,
      "status_counts":dict(collections.Counter(r["transfer_status"] for r in matrix))
    }
    (outdir/"transfer_matrix.json").write_text(
      json.dumps(matrix_obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (outdir/"canonical_seeds.json").write_text(
      json.dumps({
        "schema":"janus.trump.stage6b2.canonical_seeds.v1",
        "selection_happened_after_complete_matrix":True,
        "seeds":seeds
      },indent=2,sort_keys=True)+"\n",encoding="utf-8")

    print(json.dumps({
      "pair_count":len(matrix),
      "verified_transfer_count":sum(1 for r in matrix if r.get("transfer_verified")),
      "seed_targets":[s["target_index"] for s in seeds if s["seed_available"]],
      "no_seed_targets":[s["target_index"] for s in seeds if not s["seed_available"]]
    },sort_keys=True))


if __name__=="__main__":
    main()
