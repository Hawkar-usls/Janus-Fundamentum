from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import janus_trump_r50g25as_universal_envelope_admissible_pivot as asmod
import janus_trump_r50g25at_tautology_hardened_runner as ath

GATE = "JANUS_TRUMP_R50G25AU_DEFECT_COUNT_GROWTH_OR_SECOND_STRUCTURAL_DOOR"
PREREG_COMMIT = "a06a9ad62c7ccf0fbbbcf053840a98e9b6c36841"
PARENT_AT_SEALED_HEAD = "5b12981017a323aae9d6f1ba07fc2ae5b811af97"
PARENT_AT_RECEIPT = "a8aba0be6367170175c07f443e8f115b3c4a2b40"
INHERITED_AS_PREREG = "65870dc5f7942fb3876bc3760eaa3cfaa70f44ee"

PASS = "FROZEN_REACHABLE_DEFECT_BRANCH_PRODUCT_WITHIN_L4__UNIVERSAL_GROWTH_REMAINS_OPEN"
OBSTRUCTION = "REACHABLE_DEFECT_BRANCH_PRODUCT_L4_OBSTRUCTION_FOUND"
FAILURE = "IMPLEMENTATION_OR_CONTRACT_FAILURE"
UNKNOWN = "UNKNOWN_RESOURCE_LIMIT"
TAUTOLOGY_POLICY = "DETECT_AND_DROP_AS_ALWAYS_TRUE_BEFORE_AFFINE_GROUPING"
EXPECTED_AS_RESIDUAL_HASH = "0d46b6d6120f9a123ae75faf92ac6cfafbb57641bbc77c2c4512a8b642af3de7"
EXPECTED_AS_RESIDUAL_CLV = (1121, 4485, 16)
EXPECTED_AS_DEFECT = (8, 12, 14, 15, 16)


def is_tautology(clause):
    s = set(int(lit) for lit in clause)
    return any(-lit in s for lit in s)


def effective_canonical(formula):
    source = asmod.canonical(formula)
    tautologies = [tuple(c) for c in source if is_tautology(c)]
    effective = asmod.canonical([tuple(c) for c in source if not is_tautology(c)])
    return effective, tautologies


def independent_ledger(residual, extraction):
    effective, tautologies = effective_canonical(residual)
    L = sum(len(c) for c in effective)
    defects = [tuple(map(int, c)) for c in extraction["defects"]]
    widths = [len(c) for c in defects]
    product_a = math.prod(widths) if widths else 1
    product_b = 1
    for width in widths:
        product_b *= int(width)
    budget = int(L) ** 4
    return {
        "effective_clause_count": len(effective),
        "L": int(L),
        "tautology_count": len(tautologies),
        "defect_count": len(defects),
        "defect_widths": widths,
        "B_defect": int(product_a),
        "B_defect_recomputed": int(product_b),
        "L4_budget": int(budget),
        "budget_slack": int(budget - product_a),
        "product_recompute_match": product_a == product_b,
        "L_matches_effective_CLV": int(L) == int(asmod.clv(effective)[1]),
    }


def compact_route(replay):
    route = replay.get("route", [])
    return {
        "route_length": len(route),
        "route_head": route[:3],
        "route_tail": route[-5:] if len(route) > 5 else route,
    }


def audit_residual(root, meta, replay):
    residual = asmod.canonical(replay["state"])
    extraction = ath.hardened_extract(residual)
    failures = []

    if extraction.get("explicit_tautology_policy") != TAUTOLOGY_POLICY:
        failures.append({"kind": "TAUTOLOGY_POLICY_DRIFT"})
    if not extraction.get("tautology_check_pass"):
        failures.append({"kind": "TAUTOLOGY_POLICY_DRIFT", "detail": "tautology check did not pass"})
    if not extraction.get("partition_pass") or extraction.get("replay_failures"):
        failures.append({
            "kind": "AFFINE_EXTRACTION_OR_REPLAY_FAILURE",
            "partition_pass": bool(extraction.get("partition_pass")),
            "replay_failures": extraction.get("replay_failures", []),
        })

    ledger = independent_ledger(residual, extraction)
    if not ledger["product_recompute_match"] or not ledger["L_matches_effective_CLV"]:
        failures.append({"kind": "INDEPENDENT_LEDGER_MISMATCH", "ledger": ledger})

    row = {
        "meta": meta,
        "root_hash": asmod.formula_hash(root),
        "root_CLV": list(asmod.clv(root)),
        "policy_kind": "RESIDUAL",
        "residual_hash": asmod.formula_hash(residual),
        "residual_CLV_before_tautology_drop": list(asmod.clv(residual)),
        **compact_route(replay),
        "extraction": {
            "affine_clause_count": int(extraction["affine_clause_count"]),
            "recognized_equation_count": int(extraction["recognized_equation_count"]),
            "defect_clause_count": int(extraction["defect_clause_count"]),
            "partition_pass": bool(extraction["partition_pass"]),
            "replay_failure_count": len(extraction.get("replay_failures", [])),
            "tautology_count": int(extraction.get("tautology_count", -1)),
            "explicit_tautology_policy": extraction.get("explicit_tautology_policy"),
        },
        "ledger": ledger,
        "failure_count": len(failures),
        "failures": failures,
    }
    return row, failures


def run():
    chain = asmod.r50g25g._chain()
    rows = []
    failures = []
    witness = None
    residual_count = 0
    diagnostic_count = 0
    max_defect_count = -1
    max_defect_product = -1
    min_budget_slack = None
    as_witness_seen = False

    for formula, meta in asmod.frozen_candidates():
        root = asmod.canonical(formula)
        replay = asmod.y.policy_replay(root, chain)
        family = str(meta.get("family"))
        diagnostic_only = family == "UNPUNCTURED_AFFINE_CONTROL"
        if diagnostic_only:
            diagnostic_count += 1

        kind = str(replay.get("kind"))
        if kind in {"TERMINAL", "AFFINE"}:
            rows.append({
                "meta": meta,
                "root_hash": asmod.formula_hash(root),
                "root_CLV": list(asmod.clv(root)),
                "policy_kind": kind,
                "classification": "NON_FALSIFYING_DIAGNOSTIC_EXIT" if diagnostic_only else "NON_FALSIFYING_CHEAP_POLICY_EXIT",
                **compact_route(replay),
                "failure_count": 0,
                "failures": [],
            })
            continue

        if kind != "RESIDUAL":
            failure = {"kind": "POLICY_CONTRACT_DRIFT", "meta": meta, "observed_kind": kind}
            failures.append(failure)
            rows.append({
                "meta": meta,
                "root_hash": asmod.formula_hash(root),
                "root_CLV": list(asmod.clv(root)),
                "policy_kind": kind,
                "classification": "IMPLEMENTATION_OR_CONTRACT_FAILURE",
                "failure_count": 1,
                "failures": [failure],
            })
            break

        residual_count += 1
        row, row_failures = audit_residual(root, meta, replay)
        ledger = row["ledger"]
        max_defect_count = max(max_defect_count, int(ledger["defect_count"]))
        max_defect_product = max(max_defect_product, int(ledger["B_defect"]))
        min_budget_slack = int(ledger["budget_slack"]) if min_budget_slack is None else min(min_budget_slack, int(ledger["budget_slack"]))

        if family == "PUNCTURED_EXTENDED_HAMMING_WEIGHT4_XOR_CNF" and int(meta.get("n", -1)) == 16:
            as_witness_seen = True
            if row["residual_hash"] != EXPECTED_AS_RESIDUAL_HASH or tuple(row["residual_CLV_before_tautology_drop"]) != EXPECTED_AS_RESIDUAL_CLV:
                row_failures.append({
                    "kind": "ROOT_GENERATOR_DRIFT",
                    "detail": "AS n=16 residual identity mismatch",
                    "observed_hash": row["residual_hash"],
                    "observed_CLV": row["residual_CLV_before_tautology_drop"],
                })
            observed_defects = [tuple(map(int, c)) for c in ath.hardened_extract(replay["state"])["defects"]]
            if observed_defects != [EXPECTED_AS_DEFECT]:
                row_failures.append({
                    "kind": "ROOT_GENERATOR_DRIFT",
                    "detail": "AS exact defect mismatch",
                    "expected": [list(EXPECTED_AS_DEFECT)],
                    "observed": [list(c) for c in observed_defects],
                })

        if row_failures:
            row["failure_count"] = len(row_failures)
            row["failures"] = row_failures
            failures.extend(row_failures)
            row["classification"] = "IMPLEMENTATION_OR_CONTRACT_FAILURE"
            rows.append(row)
            break

        violates = int(ledger["B_defect"]) > int(ledger["L4_budget"])
        if diagnostic_only:
            row["classification"] = "NON_FALSIFYING_DIAGNOSTIC_RESIDUAL"
        elif violates:
            row["classification"] = "DEFECT_BRANCH_PRODUCT_EXCEEDS_L4"
            witness = {
                "class": "DEFECT_BRANCH_PRODUCT_EXCEEDS_L4",
                "meta": meta,
                "root_hash": row["root_hash"],
                "root_CLV": row["root_CLV"],
                "residual_hash": row["residual_hash"],
                "residual_CLV": row["residual_CLV_before_tautology_drop"],
                "route_summary": {
                    "route_length": row["route_length"],
                    "route_head": row["route_head"],
                    "route_tail": row["route_tail"],
                },
                "defect_count": int(ledger["defect_count"]),
                "defect_widths": ledger["defect_widths"],
                "L": int(ledger["L"]),
                "B_defect": int(ledger["B_defect"]),
                "L4_budget": int(ledger["L4_budget"]),
                "budget_slack": int(ledger["budget_slack"]),
                "residual_formula": [list(c) for c in asmod.canonical(replay["state"])],
            }
        else:
            row["classification"] = "DEFECT_BRANCH_PRODUCT_WITHIN_L4"
        rows.append(row)

        if witness is not None:
            break

    if not as_witness_seen and not failures and witness is None:
        failures.append({"kind": "ROOT_GENERATOR_DRIFT", "detail": "frozen AS n=16 witness was not audited"})

    if failures:
        verdict = FAILURE
    elif witness is not None:
        verdict = OBSTRUCTION
    else:
        verdict = PASS

    return {
        "gate": GATE,
        "status": "SCIENTIFIC_RESULT",
        "preregistration_commit": PREREG_COMMIT,
        "parent_AT_sealed_head": PARENT_AT_SEALED_HEAD,
        "parent_AT_receipt": PARENT_AT_RECEIPT,
        "inherited_AS_preregistration": INHERITED_AS_PREREG,
        "verdict": verdict,
        "candidate_count_audited": len(rows),
        "residual_count_audited": residual_count,
        "diagnostic_control_count_seen": diagnostic_count,
        "max_defect_count_observed": None if max_defect_count < 0 else max_defect_count,
        "max_B_defect_observed": None if max_defect_product < 0 else max_defect_product,
        "minimum_budget_slack_observed": min_budget_slack,
        "first_falsifier": witness,
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
        "scientific_scope": {
            "finite_reachable_corpus_only": True,
            "universal_defect_growth_bound": "OPEN",
            "arbitrary_CNF_coverage": "OPEN",
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("JANUS_TRUMP_R50G25AU_RESULT.json"))
    args = parser.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "candidate_count_audited": result["candidate_count_audited"],
        "residual_count_audited": result["residual_count_audited"],
        "max_defect_count_observed": result["max_defect_count_observed"],
        "minimum_budget_slack_observed": result["minimum_budget_slack_observed"],
        "first_falsifier_class": None if result["first_falsifier"] is None else result["first_falsifier"]["class"],
        "failure_count": result["failure_count"],
    }, sort_keys=True))
    raise SystemExit(0 if result["verdict"] in {PASS, OBSTRUCTION} and result["failure_count"] == 0 else 1)


if __name__ == "__main__":
    main()
