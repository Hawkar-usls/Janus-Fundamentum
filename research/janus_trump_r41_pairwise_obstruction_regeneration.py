#!/usr/bin/env python3
"""R41 fixed pairwise obstruction regeneration.

Exactly the 28 preregistered unordered pairs of the 8 R39 obstruction variables
are tested. Within each pair variables are eliminated in ascending numeric order.
No third elimination and no dynamic pair selection is allowed.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import janus_trump_r40_pyramidal_obstruction_regeneration as r40

FROZEN_VARIABLES = [2, 6, 14, 15, 18, 21, 22, 23]
FROZEN_PAIRS = list(itertools.combinations(FROZEN_VARIABLES, 2))
MAX_CLAUSES = 2000
MAX_TOTAL_RESOLVENT_PAIRS = 200000


def main():
    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / "research" / "JANUS_TRUMP_R39_QHORN_SEALED_INPUT_2026-09-03.json").read_text())
    parent = source["clauses"]
    parent_sha = r40.sha256_json(parent)
    if parent_sha != r40.EXPECTED_PARENT_SHA256:
        raise AssertionError(f"PARENT_HASH_MISMATCH:{parent_sha}")

    parent_sat, _ = r40.exact_finite_sat_control(parent)
    children = []
    for first, second in FROZEN_PAIRS:
        step1, ledger1 = r40.davis_putnam_eliminate(parent, first)
        step1_literals = sum(len(c) for c in step1)
        if ledger1["output_clause_count"] > MAX_CLAUSES or ledger1["resolvent_pairs_attempted"] > MAX_TOTAL_RESOLVENT_PAIRS:
            children.append({
                "child_id": f"DP_PAIR_{first}_{second}",
                "elimination_pair": [first, second],
                "status": "RESOURCE_BOUND_HIT_AT_STEP_1",
                "decisive": False,
                "step1_ledger": ledger1,
            })
            continue

        step2, ledger2 = r40.davis_putnam_eliminate(step1, second)
        step2_literals = sum(len(c) for c in step2)
        total_pairs = ledger1["resolvent_pairs_attempted"] + ledger2["resolvent_pairs_attempted"]
        if ledger2["output_clause_count"] > MAX_CLAUSES or total_pairs > MAX_TOTAL_RESOLVENT_PAIRS:
            children.append({
                "child_id": f"DP_PAIR_{first}_{second}",
                "elimination_pair": [first, second],
                "status": "RESOURCE_BOUND_HIT_AT_STEP_2",
                "decisive": False,
                "step1_ledger": ledger1,
                "step2_ledger": ledger2,
                "total_resolvent_pairs_attempted": total_pairs,
            })
            continue

        child_sat, witness_hash = r40.exact_finite_sat_control(step2)
        if child_sat != parent_sat:
            raise AssertionError(f"SAT_EQUIVALENCE_CONTROL_MISMATCH:{first},{second}")
        terminals = r40.classify_terminals(step2)
        children.append({
            "child_id": f"DP_PAIR_{first}_{second}",
            "elimination_pair": [first, second],
            "status": "TERMINAL_REACHED" if terminals else "OPEN",
            "formula_sha256": r40.sha256_json(step2),
            "audited_terminal_hits": terminals,
            "finite_semantic_control_sat": child_sat,
            "finite_semantic_control_witness_sha256": witness_hash,
            "resource_ledger": {
                "step1_resolvent_pairs": ledger1["resolvent_pairs_attempted"],
                "step2_resolvent_pairs": ledger2["resolvent_pairs_attempted"],
                "total_resolvent_pairs": total_pairs,
                "peak_clause_count": max(ledger1["output_clause_count"], ledger2["output_clause_count"]),
                "peak_literal_count": max(step1_literals, step2_literals),
                "output_clause_count": ledger2["output_clause_count"],
                "output_literal_count": step2_literals,
                "remaining_variable_count": ledger2["remaining_variable_count"],
            },
            "decisive": bool(terminals),
        })

    decisive = [c["child_id"] for c in children if c.get("decisive")]
    capped = [c["child_id"] for c in children if c["status"].startswith("RESOURCE_BOUND_HIT")]
    complete = [c for c in children if "resource_ledger" in c]
    result = {
        "schema": "janus.trump.r41.pairwise_obstruction_regeneration.result.v1",
        "date": "2026-09-03",
        "status": "PAIRWISE_REGENERATED_AND_DECISIVE" if decisive else
                  ("PAIRWISE_RESOURCE_BOUND_HIT" if capped else "PAIRWISE_REGENERATED_STILL_OPEN"),
        "parent_formula_sha256": parent_sha,
        "generation_depth": 2,
        "frozen_pair_count": len(FROZEN_PAIRS),
        "children": children,
        "decisive_children": decisive,
        "resource_bound_children": capped,
        "aggregate_charged_work": {
            "total_resolvent_pairs_attempted": sum(c["resource_ledger"]["total_resolvent_pairs"] for c in complete),
            "total_output_literals_materialized": sum(c["resource_ledger"]["output_literal_count"] for c in complete),
            "max_peak_clause_count": max(c["resource_ledger"]["peak_clause_count"] for c in complete),
            "max_peak_literal_count": max(c["resource_ledger"]["peak_literal_count"] for c in complete),
            "max_single_child_resolvent_pairs": max(c["resource_ledger"]["total_resolvent_pairs"] for c in complete),
        },
        "smallest_output_child": min(
            ({"child_id": c["child_id"],
              "output_clause_count": c["resource_ledger"]["output_clause_count"],
              "output_literal_count": c["resource_ledger"]["output_literal_count"],
              "total_resolvent_pairs": c["resource_ledger"]["total_resolvent_pairs"]}
             for c in complete),
            key=lambda x: (x["output_literal_count"], x["output_clause_count"], x["total_resolvent_pairs"], x["child_id"]),
        ),
        "verified_delta": {
            "statement": "No preregistered depth-2 obstruction pair reaches 2CNF, Horn, dual-Horn, or renamable-Horn under the frozen caps."
            if not decisive and not capped else
            "See decisive_children/resource_bound_children; no broader inference is authorized.",
            "verified": True,
            "replay_match_required_for_regeneration": True,
        },
        "complexity_interpretation": {
            "finite_depth_2_blowup_observed": False if complete and max(c["resource_ledger"]["peak_clause_count"] for c in complete) <= MAX_CLAUSES else True,
            "asymptotic_polynomiality_inferred": False,
            "law": "DEPTH_2_RESOURCE_BEHAVIOR != ASYMPTOTIC_BOUND",
        },
        "proof_authority_delta": 0,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
