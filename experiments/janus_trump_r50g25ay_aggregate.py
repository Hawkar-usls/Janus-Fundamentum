from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

GATE = "R50G25AY_SEPARATOR_WIDTH_SCALING_OR_RELATION_LEDGER_BLOWUP_COUNTEREXAMPLE"
PREREG = "98bfc81908c3887b326fe3f6c560539a7ce2a113"
LADDER = (1, 2, 3, 4, 6, 8)

LEDGER_OBSTRUCTION = "AY_RELATION_LEDGER_BLOWUP_COUNTEREXAMPLE_FOUND"
CONTRACT_OBSTRUCTION = "AY_RELATION_CONTRACT_COUNTEREXAMPLE_FOUND"
SPARSE_SURVIVAL = "AY_SPARSE_RELATION_LEDGER_SURVIVES_WIDTH_ENVELOPE_FAILURE_ON_FROZEN_LADDER__ASYMPTOTIC_OPEN"
FULL_SURVIVAL = "AY_WIDTH_AND_RELATION_LEDGER_WITHIN_L4_ON_FROZEN_LADDER__ASYMPTOTIC_OPEN"
INSUFFICIENT = "AY_INSUFFICIENT_RELEVANT_SCALING_COVERAGE"
UNKNOWN = "UNKNOWN_RESOURCE_LIMIT"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_all(root: Path):
    rows = {}
    ver = {}
    for g in LADDER:
        rp = list(root.rglob(f"AY_RUNG_{g}.json"))
        vp = list(root.rglob(f"AY_VERIFY_{g}.json"))
        if len(rp) != 1 or len(vp) != 1:
            raise AssertionError(("MISSING_OR_DUPLICATE_RUNG_ARTIFACT", g, len(rp), len(vp)))
        r = json.loads(rp[0].read_text())
        v = json.loads(vp[0].read_text())
        if int(r.get("g", -1)) != g or int(v.get("g", -1)) != g:
            raise AssertionError(("RUNG_ID_DRIFT", g))
        if r.get("preregistration_commit") != PREREG:
            raise AssertionError(("PREREG_DRIFT", g, r.get("preregistration_commit")))
        if v.get("status") != "PASS" or v.get("failures"):
            raise AssertionError(("INDEPENDENT_VERIFY_FAIL", g, v))
        if v.get("classification") != r.get("classification"):
            raise AssertionError(("VERIFY_CLASSIFICATION_MISMATCH", g))
        rows[g] = (r, rp[0])
        ver[g] = (v, vp[0])
    return rows, ver


def compact(r):
    rel = r.get("relation") or {}
    sep = r.get("separator") or {}
    target = r.get("target_component") or {}
    return {
        "g": int(r["g"]),
        "relevant": bool(r.get("relevant")),
        "classification": r.get("classification"),
        "policy_kind": r.get("policy_kind"),
        "V": target.get("variable_count"),
        "D": target.get("defect_count"),
        "E": target.get("affine_equation_count"),
        "L": r.get("L"),
        "L4_budget": r.get("L4_budget"),
        "w": sep.get("induced_width"),
        "state_bound_2_pow_w": sep.get("state_bound_2_pow_w"),
        "total_materialized_rows": rel.get("total_materialized_rows"),
        "maximum_generated_scope": rel.get("maximum_generated_scope"),
        "maximum_generated_table_rows": rel.get("maximum_generated_table_rows"),
        "decision": rel.get("decision"),
        "reconstruction_pass": r.get("reconstruction_pass"),
        "source_validation_pass": r.get("source_validation_pass"),
        "residual_hash": r.get("residual_hash"),
    }


def run(root: Path):
    rows, ver = load_all(root)
    relevant = [rows[g][0] for g in LADDER if rows[g][0].get("relevant")]
    classes = {g: rows[g][0].get("classification") for g in LADDER}
    ledger_bad = [g for g in LADDER if classes[g] == "RELATION_LEDGER_EXCEEDS_L4"]
    contract_bad = [g for g in LADDER if classes[g] == "RELATION_CONTRACT_FAILURE"]
    sparse = [g for g in LADDER if classes[g] == "SPARSE_RELATION_LEDGER_ONLY_WITHIN_L4"]
    relevant_g = [int(r["g"]) for r in relevant]

    if ledger_bad:
        verdict = LEDGER_OBSTRUCTION
    elif contract_bad:
        verdict = CONTRACT_OBSTRUCTION
    elif len(relevant) < 4 or 1 not in relevant_g or 8 not in relevant_g:
        verdict = INSUFFICIENT
    elif sparse:
        verdict = SPARSE_SURVIVAL
    elif all(r.get("classification") == "WIDTH_AND_RELATION_LEDGER_WITHIN_L4" for r in relevant):
        verdict = FULL_SURVIVAL
    else:
        verdict = UNKNOWN

    table = [compact(rows[g][0]) for g in LADDER]
    numeric = [x for x in table if x["relevant"]]
    max_w = max((int(x["w"]) for x in numeric if x["w"] is not None), default=None)
    max_rows = max((int(x["total_materialized_rows"]) for x in numeric if x["total_materialized_rows"] is not None), default=None)
    min_row_slack = min((int(x["L4_budget"]) - int(x["total_materialized_rows"]) for x in numeric if x["total_materialized_rows"] is not None), default=None)
    min_width_slack = min((int(x["L4_budget"]) - int(x["state_bound_2_pow_w"]) for x in numeric if x["state_bound_2_pow_w"] is not None), default=None)

    identities = []
    for g in LADDER:
        r, rp = rows[g]; v, vp = ver[g]
        identities.append({
            "g": g,
            "rung_json_sha256": sha(rp),
            "verify_json_sha256": sha(vp),
            "classification": r.get("classification"),
            "independent_verify": v.get("status"),
        })

    return {
        "gate": GATE,
        "status": "SCIENTIFIC_AGGREGATE_RESULT",
        "preregistration_commit": PREREG,
        "verdict": verdict,
        "frozen_ladder": list(LADDER),
        "rung_count": len(LADDER),
        "relevant_rung_count": len(relevant),
        "relevant_g": relevant_g,
        "ledger_obstruction_rungs": ledger_bad,
        "relation_contract_failure_rungs": contract_bad,
        "sparse_ledger_only_rungs": sparse,
        "table": table,
        "summary": {
            "maximum_observed_induced_width": max_w,
            "maximum_observed_total_materialized_rows": max_rows,
            "minimum_relation_row_L4_slack": min_row_slack,
            "minimum_width_state_L4_slack": min_width_slack,
        },
        "artifact_identities": identities,
        "scope": {
            "finite_frozen_scaling_ladder_only": True,
            "asymptotic_separator_bound": "OPEN",
            "asymptotic_polynomial_runtime": "NOT_PROVED",
            "arbitrary_CNF_coverage": "OPEN",
        },
        "governance": {
            "proof_state_machine_required_before_seal": True,
            "allowed_positive_promotion_maximum": "FINITE_FROZEN_LADDER_RELATION_SCALING_EVIDENCE",
        },
        "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    x = run(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": x["verdict"], "relevant_rung_count": x["relevant_rung_count"], **x["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
