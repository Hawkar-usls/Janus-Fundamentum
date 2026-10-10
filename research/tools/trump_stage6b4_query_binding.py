#!/usr/bin/env python3
"""Stage6B.4 deterministic query binder.

Given a frozen canonical-CNF audit and a certified bracket state, emit a
query-specific canonical receipt whose only scientific change is boundary_k.
The selected k is recomputed as floor((L+U)/2); human-supplied k is not accepted.
"""
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path


def stable_sha(obj):
    return hashlib.sha256((json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("canonical")
    ap.add_argument("state")
    ap.add_argument("query_audit")
    ap.add_argument("receipt")
    ns=ap.parse_args()

    canonical=json.loads(Path(ns.canonical).read_text(encoding="utf-8"))
    state=json.loads(Path(ns.state).read_text(encoding="utf-8"))
    if canonical.get("status")!="CANONICALIZATION_AUDIT_PASS":
        raise SystemExit("canonical audit not PASS")
    if canonical.get("complementary_pair_clause_count")!=0:
        raise SystemExit("complementary-pair guard violated")
    if state.get("closed"):
        raise SystemExit("target bracket already closed")

    L=int(state["L"]); U=int(state["U"])
    if not (0 <= L < U):
        raise SystemExit("invalid bracket")
    if U==L+1:
        raise SystemExit("bracket already exact; no query permitted")
    k=(L+U)//2

    q=copy.deepcopy(canonical)
    old_k=q.get("boundary_k")
    q["boundary_k"]=k
    q["stage6b4_query_binding"]={
      "gate":"TRUMP_STAGE6B4_ADAPTIVE_PROOF_CARRYING_EXACT_DELETION_QHORN_DISTANCE_GATE",
      "prereg_commit":"ec279137463f1796145973fe60d4e3dac68b9b28",
      "target_index":int(state["index"]),
      "round":int(state["round"])+1,
      "L_before":L,
      "U_before":U,
      "selected_k":k,
      "selection_rule":"floor((L+U)/2)",
      "source_canonical_receipt_sha256":stable_sha(canonical),
      "source_boundary_k_ignored_for_B4":old_k
    }

    if q["canonical_cnf_sha256"]!=canonical["canonical_cnf_sha256"]:
        raise AssertionError
    if q["raw_cnf_sha256"]!=canonical["raw_cnf_sha256"]:
        raise AssertionError
    if q["canonical_clauses"]!=canonical["canonical_clauses"]:
        raise AssertionError
    if q["variable_set"]!=canonical["variable_set"]:
        raise AssertionError

    Path(ns.query_audit).parent.mkdir(parents=True,exist_ok=True)
    Path(ns.query_audit).write_text(json.dumps(q,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    receipt={
      "schema":"janus.trump.stage6b4.query_binding.v1",
      "target_index":int(state["index"]),
      "round":int(state["round"])+1,
      "L_before":L,"U_before":U,"selected_k":k,
      "selection_rule":"floor((L+U)/2)",
      "source_canonical_receipt_sha256":stable_sha(canonical),
      "query_audit_sha256":stable_sha(q),
      "raw_cnf_sha256":q["raw_cnf_sha256"],
      "canonical_cnf_sha256":q["canonical_cnf_sha256"],
      "canonical_clauses_sha256":stable_sha(q["canonical_clauses"]),
      "variable_set_sha256":stable_sha(q["variable_set"]),
      "only_authorized_scientific_change":"boundary_k",
      "old_embedded_boundary_k":old_k,
      "new_boundary_k":k
    }
    Path(ns.receipt).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,sort_keys=True))


if __name__=="__main__": main()
