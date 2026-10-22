#!/usr/bin/env python3
"""Stage6B.2 certificate materialization replay.

Infrastructure-only replay. It MUST NOT change any frozen Stage6B.2 B*, seed,
transfer decision, shrink decision, or necessity decision.

For each exact frozen B* from the sealed Stage6B.2 result:
  * bind B* hash to the replay preregistration;
  * reconstruct F-B* from the raw frozen CNF;
  * obtain a fresh generic q-Horn weight proposal;
  * independently verify the full weight certificate;
  * replay the full polynomial q-Horn terminal;
  * persist the COMPLETE weight map and COMPLETE terminal proof object.

This closes an archival persistence gap only.
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
    verify_weights,
)
from trump_stage6b_deletion_qhorn_independent_checker import deletion_projection  # noqa: E402
from trump_stage6b2_qhorn_witness_transfer import propose_weights  # noqa: E402


def stable_sha(obj):
    raw=(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest(),len(raw)


def file_sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def materialize_one(source_data,row,expected_hash,timeout_ms):
    idx=int(row["target_index"])
    B=sorted(int(v) for v in row["final_B_star"])
    bsha,_=stable_sha(B)
    if bsha!=expected_hash:
        return {
          "target_index":idx,
          "status":"INFRASTRUCTURE_ERROR",
          "failure":{
            "reason":"FROZEN_B_STAR_HASH_MISMATCH",
            "expected":expected_hash,
            "observed":bsha
          }
        }

    raw=source_data["residuals"][idx]["residual_formula"]
    raw_vars={abs(l) for c in raw for l in c}
    extra=sorted(set(B)-raw_vars)
    if extra:
        return {
          "target_index":idx,
          "status":"INFRASTRUCTURE_ERROR",
          "failure":{
            "reason":"FROZEN_B_STAR_NOT_SUBSET_OF_TARGET_VARIABLES",
            "extra":extra
          }
        }

    reduced=deletion_projection(raw,set(B))
    reduced_sha=formula_sequence_sha256(reduced)
    proposal=propose_weights(reduced,timeout_ms)
    if proposal.get("solver_status")!="SAT":
        return {
          "target_index":idx,
          "status":"INFRASTRUCTURE_ERROR",
          "B_star":B,
          "B_star_sha256":bsha,
          "F_minus_B_star_sha256":reduced_sha,
          "failure":{
            "reason":"FRESH_QHORN_PROPOSER_DID_NOT_RETURN_SAT",
            "solver_status":proposal.get("solver_status"),
            "reason_unknown":proposal.get("reason_unknown")
          },
          "proposal_telemetry":proposal
        }

    weights=proposal.get("weights")
    ok,detail=verify_weights(reduced,weights)
    if not ok:
        return {
          "target_index":idx,
          "status":"INFRASTRUCTURE_ERROR",
          "failure":{
            "reason":"FRESH_QHORN_CERTIFICATE_FAILED_INDEPENDENT_REPLAY",
            "detail":detail
          }
        }

    obstruction=build_obstruction(reduced)
    if obstruction is not None:
        return {
          "target_index":idx,
          "status":"INFRASTRUCTURE_ERROR",
          "failure":{
            "reason":"POSITIVE_CERTIFICATE_CONTRADICTS_REBUILT_QHORN_OBSTRUCTION",
            "obstruction":obstruction
          }
        }

    terminal=qhorn_terminal(reduced,detail["weights"])
    if not terminal.get("terminal_replay_verified"):
        return {
          "target_index":idx,
          "status":"INFRASTRUCTURE_ERROR",
          "failure":{"reason":"FULL_QHORN_TERMINAL_REPLAY_NOT_VERIFIED"},
          "terminal":terminal
        }

    cert_sha,cert_bytes=stable_sha(weights)
    terminal_sha,terminal_bytes=stable_sha(terminal)
    return {
      "target_index":idx,
      "status":"MATERIALIZED_AND_VERIFIED",
      "original_stage6B2_scientific_outcome":row.get("scientific_outcome"),
      "B_star":B,
      "B_star_size":len(B),
      "B_star_sha256":bsha,
      "F_minus_B_star_sha256":reduced_sha,
      "fresh_qhorn_certificate":{
        "weights":weights,
        "sha256":cert_sha,
        "bytes":cert_bytes,
        "verified":True
      },
      "full_terminal_object":{
        "object":terminal,
        "sha256":terminal_sha,
        "bytes":terminal_bytes,
        "verified":True
      },
      "proposal_telemetry":{
        k:v for k,v in proposal.items()
        if k not in ("weights",)
      },
      "old_stage6B2_certificate_hash_only":row.get("fresh_qhorn_certificate_sha256"),
      "old_stage6B2_terminal_status":row.get("terminal_replay_status"),
      "old_stage6B2_terminal_stage":row.get("terminal_replay_stage"),
      "old_stage6B2_terminal_verified":row.get("terminal_replay_verified")
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("stage6b2_result")
    ap.add_argument("replay_prereg")
    ap.add_argument("outdir")
    ap.add_argument("--timeout-ms",type=int,default=10000)
    ns=ap.parse_args()

    source_path=Path(ns.source)
    result_path=Path(ns.stage6b2_result)
    prereg_path=Path(ns.replay_prereg)
    outdir=Path(ns.outdir)
    outdir.mkdir(parents=True,exist_ok=True)

    source=json.loads(source_path.read_text(encoding="utf-8"))
    result=json.loads(result_path.read_text(encoding="utf-8"))
    prereg=json.loads(prereg_path.read_text(encoding="utf-8"))

    expected_hashes={int(k):v for k,v in prereg["frozen_final_B_star_hashes"].items()}
    rows_by_idx={int(r["target_index"]):r for r in result["rows"]}
    expected_indices=sorted(expected_hashes)
    if sorted(rows_by_idx)!=expected_indices:
        raise SystemExit("TARGET_SET_MISMATCH_BETWEEN_PREREG_AND_STAGE6B2_RESULT")

    rows=[]
    for idx in expected_indices:
        obj=materialize_one(
          source,rows_by_idx[idx],expected_hashes[idx],ns.timeout_ms
        )
        rows.append(obj)
        (outdir/f"target_{idx:02d}.materialized.json").write_text(
          json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8"
        )
        print(json.dumps({
          "target_index":idx,
          "status":obj.get("status"),
          "B_star_size":obj.get("B_star_size"),
          "certificate_sha256":
              (obj.get("fresh_qhorn_certificate") or {}).get("sha256"),
          "terminal_sha256":
              (obj.get("full_terminal_object") or {}).get("sha256")
        },sort_keys=True),flush=True)

    counts=dict(collections.Counter(r["status"] for r in rows))
    success=(counts.get("MATERIALIZED_AND_VERIFIED",0)==13 and len(rows)==13)
    summary={
      "schema":"janus.trump.stage6b2.certificate_materialization_replay.v1",
      "gate":"TRUMP_STAGE6B2_CERTIFICATE_MATERIALIZATION_REPLAY",
      "source_stage6B2_result_sha256":file_sha256(result_path),
      "replay_prereg_sha256":file_sha256(prereg_path),
      "row_count":len(rows),
      "status_counts":counts,
      "all_13_materialized_and_verified":success,
      "rows":rows,
      "scientific_decisions_changed":False,
      "search_executed":False,
      "shrink_executed":False,
      "seed_reselection_executed":False,
      "stage6B3_stage6C_stage6D_executed":False
    }
    (outdir/"TRUMP_STAGE6B2_CERTIFICATE_MATERIALIZATION_REPLAY_RESULT.json").write_text(
      json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    if not success:
        raise SystemExit("CERTIFICATE_MATERIALIZATION_INCOMPLETE")


if __name__=="__main__":
    main()
