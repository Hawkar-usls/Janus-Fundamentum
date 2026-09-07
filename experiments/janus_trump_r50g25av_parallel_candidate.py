from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25av_reachable_multi_defect_growth_witness as av


def run_one(index: int):
    if index < 0 or index >= 9:
        raise AssertionError(("CANDIDATE_INDEX_OUT_OF_FROZEN_RANGE", index))
    candidates = list(av.frozen_candidates())
    if len(candidates) != 9:
        raise AssertionError(("ROOT_GENERATOR_DRIFT", "candidate count", len(candidates)))
    root, meta = candidates[index]
    root = av.canonical(root)
    chain = av.asmod.r50g25g._chain()
    replay = av.asmod.y.policy_replay(root, chain)
    kind = str(replay.get("kind"))

    if kind in {"TERMINAL", "AFFINE"}:
        row = {
            "meta": meta,
            "root_hash": av.formula_hash(root),
            "root_CLV": list(av.clv(root)),
            "policy_kind": kind,
            "classification": "NON_FALSIFYING_CHEAP_POLICY_ABSORPTION",
            **av.compact_route(replay),
            "failure_count": 0,
            "failures": [],
        }
        return {"candidate_index": index, "row": row, "failure_count": 0, "failures": []}

    if kind != "RESIDUAL":
        failure = {"kind": "POLICY_CONTRACT_DRIFT", "meta": meta, "observed_kind": kind}
        row = {
            "meta": meta,
            "root_hash": av.formula_hash(root),
            "root_CLV": list(av.clv(root)),
            "policy_kind": kind,
            "classification": av.FAILURE,
            "failure_count": 1,
            "failures": [failure],
        }
        return {"candidate_index": index, "row": row, "failure_count": 1, "failures": [failure]}

    row, row_failures = av.audit_residual(root, meta, replay)
    if row_failures:
        row["classification"] = av.FAILURE
        return {"candidate_index": index, "row": row, "failure_count": len(row_failures), "failures": row_failures}

    ledger = row["ledger"]
    d = int(ledger["defect_count"])
    if int(ledger["B_defect"]) > int(ledger["L4_budget"]):
        row["classification"] = "DEFECT_BRANCH_PRODUCT_EXCEEDS_L4"
        row["obstruction_witness"] = av.witness_from_row(row, "DEFECT_BRANCH_PRODUCT_EXCEEDS_L4")
        row["obstruction_witness"]["residual_formula"] = [list(c) for c in av.canonical(replay["state"])]
    elif d > 4:
        row["classification"] = "REACHABLE_D_GT_4_WITHIN_L4"
    else:
        row["classification"] = "D_LE_4_WITHIN_L4"

    return {"candidate_index": index, "row": row, "failure_count": 0, "failures": []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    result = run_one(args.index)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_index": result["candidate_index"],
        "family": result["row"].get("meta", {}).get("family"),
        "policy_kind": result["row"].get("policy_kind"),
        "classification": result["row"].get("classification"),
        "defect_count": None if result["row"].get("ledger") is None else result["row"]["ledger"]["defect_count"],
        "budget_slack": None if result["row"].get("ledger") is None else result["row"]["ledger"]["budget_slack"],
        "failure_count": result["failure_count"],
    }, sort_keys=True))
    raise SystemExit(0 if result["failure_count"] == 0 else 1)


if __name__ == "__main__":
    main()
