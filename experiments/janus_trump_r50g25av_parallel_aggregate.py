from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25av_reachable_multi_defect_growth_witness as av


def aggregate(input_dir: Path):
    files = sorted(input_dir.glob("candidate-*.json"))
    by_index = {}
    for p in files:
        x = json.loads(p.read_text(encoding="utf-8"))
        idx = int(x["candidate_index"])
        if idx in by_index:
            raise AssertionError(("DUPLICATE_CANDIDATE_INDEX", idx))
        by_index[idx] = x
    if sorted(by_index) != list(range(9)):
        raise AssertionError(("MISSING_FROZEN_CANDIDATE_RESULTS", sorted(by_index)))

    rows = []
    failures = []
    first_multi = None
    obstruction = None
    max_d = -1
    max_product = -1
    min_slack = None
    residual_count = 0
    absorbed_terminal = 0
    absorbed_affine = 0

    for idx in range(9):
        item = by_index[idx]
        row = item["row"]
        if item.get("failure_count", 0):
            failures.extend(item.get("failures", []))
            rows.append(row)
            break

        kind = row.get("policy_kind")
        if kind == "TERMINAL":
            absorbed_terminal += 1
        elif kind == "AFFINE":
            absorbed_affine += 1
        elif kind == "RESIDUAL":
            residual_count += 1
            l = row["ledger"]
            d = int(l["defect_count"])
            max_d = max(max_d, d)
            max_product = max(max_product, int(l["B_defect"]))
            min_slack = int(l["budget_slack"]) if min_slack is None else min(min_slack, int(l["budget_slack"]))
            if d > 4 and first_multi is None:
                first_multi = av.witness_from_row(row, "FIRST_REACHABLE_D_GT_4")
            if int(l["B_defect"]) > int(l["L4_budget"]):
                obstruction = row.get("obstruction_witness") or av.witness_from_row(row, "DEFECT_BRANCH_PRODUCT_EXCEEDS_L4")
        else:
            failures.append({"kind": "POLICY_CONTRACT_DRIFT", "candidate_index": idx, "observed_kind": kind})
        rows.append(row)
        if failures or obstruction is not None:
            break

    if failures:
        verdict = av.FAILURE
    elif obstruction is not None:
        verdict = av.OBSTRUCTION
    elif first_multi is not None:
        verdict = av.MULTI_SURVIVAL
    else:
        verdict = av.NO_MULTI

    return {
        "gate": av.GATE,
        "status": "SCIENTIFIC_RESULT",
        "preregistration_commit": av.PREREG_COMMIT,
        "parent_AU_sealed_head": av.PARENT_AU_SEALED_HEAD,
        "parent_AU_receipt": av.PARENT_AU_RECEIPT,
        "parent_AU_meta": av.PARENT_AU_META,
        "Y_target_hash": av.Y_TARGET_HASH,
        "Y_preregistration_commit": av.Y_PREREG_COMMIT,
        "verdict": verdict,
        "candidate_count_frozen": 9,
        "candidate_count_physically_computed": 9,
        "candidate_count_audited": len(rows),
        "residual_count_audited": residual_count,
        "cheap_policy_absorption": {"TERMINAL": absorbed_terminal, "AFFINE": absorbed_affine},
        "first_reachable_d_gt_4": first_multi,
        "first_L4_obstruction": obstruction,
        "max_defect_count_observed": None if max_d < 0 else max_d,
        "max_B_defect_observed": None if max_product < 0 else max_product,
        "minimum_budget_slack_observed": min_slack,
        "failure_count": len(failures),
        "failures": failures,
        "rows": rows,
        "frozen_bound": {
            "B_defect": "product_i |D_i|",
            "L": "literal count of current canonical residual after explicit tautology removal",
            "budget": "L^4",
            "exponent": 4,
            "posthoc_tuning_forbidden": True,
        },
        "frozen_attack_contract": {
            "local_k": list(av.LOCAL_K),
            "Y_copy_counts": list(av.Y_COPIES),
            "candidate_order": "LOCAL_INJECTION_THEN_Y_COMPOSITION",
            "stop_on_first_L4_obstruction": True,
        },
        "execution_topology": {
            "mode": "PARALLEL_CANDIDATE_REPLAY_THEN_DETERMINISTIC_FROZEN_ORDER_AGGREGATION",
            "scientific_candidate_set_changed": False,
            "scientific_candidate_order_changed": False,
            "stopping_rule_changed": False,
            "post_obstruction_physical_results_ignored_by_scientific_aggregation": True,
        },
        "scientific_scope": {
            "finite_frozen_attack_families_only": True,
            "universal_defect_growth_bound": "OPEN",
            "arbitrary_CNF_coverage": "OPEN",
            "simple_defect_enumeration_if_obstruction": "FALSIFIED_ON_REACHABLE_WITNESS" if obstruction is not None else "NOT_FALSIFIED_ON_FROZEN_ATTACKS",
            "second_structural_door_if_obstruction": "MUST_BE_SEPARATELY_PREREGISTERED",
        },
        "truth_oracle": {
            "used_for_generation": False,
            "used_for_selection": False,
            "used_for_verdict": False,
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "AR_AS_meta_backfill_pending": True,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    result = aggregate(args.input_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "candidate_count_audited": result["candidate_count_audited"],
        "residual_count_audited": result["residual_count_audited"],
        "max_defect_count_observed": result["max_defect_count_observed"],
        "max_B_defect_observed": result["max_B_defect_observed"],
        "minimum_budget_slack_observed": result["minimum_budget_slack_observed"],
        "first_multi": result["first_reachable_d_gt_4"],
        "first_obstruction": None if result["first_L4_obstruction"] is None else {k:v for k,v in result["first_L4_obstruction"].items() if k != "residual_formula"},
        "failure_count": result["failure_count"],
    }, sort_keys=True))
    good = result["verdict"] in {av.OBSTRUCTION, av.MULTI_SURVIVAL, av.NO_MULTI} and result["failure_count"] == 0
    raise SystemExit(0 if good else 1)


if __name__ == "__main__":
    main()
