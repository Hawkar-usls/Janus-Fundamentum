from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

LADDER = (1, 2, 3, 4, 6, 8)
PREREG = "98bfc81908c3887b326fe3f6c560539a7ce2a113"


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_verdict(table):
    classes = {int(r["g"]): r.get("classification") for r in table}
    ledger = [g for g in LADDER if classes.get(g) == "RELATION_LEDGER_EXCEEDS_L4"]
    contract = [g for g in LADDER if classes.get(g) == "RELATION_CONTRACT_FAILURE"]
    sparse = [g for g in LADDER if classes.get(g) == "SPARSE_RELATION_LEDGER_ONLY_WITHIN_L4"]
    relevant = [r for r in table if r.get("relevant")]
    relevant_g = [int(r["g"]) for r in relevant]
    if ledger:
        return "AY_RELATION_LEDGER_BLOWUP_COUNTEREXAMPLE_FOUND"
    if contract:
        return "AY_RELATION_CONTRACT_COUNTEREXAMPLE_FOUND"
    if len(relevant) < 4 or 1 not in relevant_g or 8 not in relevant_g:
        return "AY_INSUFFICIENT_RELEVANT_SCALING_COVERAGE"
    if sparse:
        return "AY_SPARSE_RELATION_LEDGER_SURVIVES_WIDTH_ENVELOPE_FAILURE_ON_FROZEN_LADDER__ASYMPTOTIC_OPEN"
    if all(r.get("classification") == "WIDTH_AND_RELATION_LEDGER_WITHIN_L4" for r in relevant):
        return "AY_WIDTH_AND_RELATION_LEDGER_WITHIN_L4_ON_FROZEN_LADDER__ASYMPTOTIC_OPEN"
    return "UNKNOWN_RESOURCE_LIMIT"


def verify(root: Path, aggregate_path: Path):
    x = json.loads(aggregate_path.read_text())
    failures = []
    if x.get("preregistration_commit") != PREREG:
        failures.append("PREREG_DRIFT")
    if tuple(map(int, x.get("frozen_ladder", []))) != LADDER:
        failures.append("LADDER_DRIFT")
    table = x.get("table", [])
    if [int(r["g"]) for r in table] != list(LADDER):
        failures.append("TABLE_ORDER_DRIFT")
    ev = expected_verdict(table)
    if x.get("verdict") != ev:
        failures.append("AGGREGATE_VERDICT_REPLAY_MISMATCH")

    ids = {int(i["g"]): i for i in x.get("artifact_identities", [])}
    if sorted(ids) != list(LADDER):
        failures.append("ARTIFACT_IDENTITY_SET_DRIFT")
    for g in LADDER:
        rp = list(root.rglob(f"AY_RUNG_{g}.json"))
        vp = list(root.rglob(f"AY_VERIFY_{g}.json"))
        if len(rp) != 1 or len(vp) != 1:
            failures.append(f"RUNG_FILES_MISSING:{g}")
            continue
        rec = ids.get(g, {})
        if rec.get("rung_json_sha256") != digest(rp[0]):
            failures.append(f"RUNG_SHA_MISMATCH:{g}")
        if rec.get("verify_json_sha256") != digest(vp[0]):
            failures.append(f"VERIFY_SHA_MISMATCH:{g}")
        vv = json.loads(vp[0].read_text())
        rr = json.loads(rp[0].read_text())
        if vv.get("status") != "PASS" or vv.get("failures"):
            failures.append(f"RUNG_INDEPENDENT_VERIFY_NOT_PASS:{g}")
        if rr.get("classification") != rec.get("classification"):
            failures.append(f"IDENTITY_CLASSIFICATION_MISMATCH:{g}")

    relevant = [r for r in table if r.get("relevant")]
    summary = x.get("summary", {})
    max_w = max((int(r["w"]) for r in relevant if r.get("w") is not None), default=None)
    max_rows = max((int(r["total_materialized_rows"]) for r in relevant if r.get("total_materialized_rows") is not None), default=None)
    min_row_slack = min((int(r["L4_budget"]) - int(r["total_materialized_rows"]) for r in relevant if r.get("total_materialized_rows") is not None), default=None)
    min_width_slack = min((int(r["L4_budget"]) - int(r["state_bound_2_pow_w"]) for r in relevant if r.get("state_bound_2_pow_w") is not None), default=None)
    expected_summary = {
        "maximum_observed_induced_width": max_w,
        "maximum_observed_total_materialized_rows": max_rows,
        "minimum_relation_row_L4_slack": min_row_slack,
        "minimum_width_state_L4_slack": min_width_slack,
    }
    if summary != expected_summary:
        failures.append("SUMMARY_REPLAY_MISMATCH")
    return {"status": "PASS" if not failures else "FAIL", "failures": failures, "replayed_verdict": ev, "aggregate_sha256": digest(aggregate_path)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--aggregate", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    receipt = verify(args.root, args.aggregate)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    if receipt["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
