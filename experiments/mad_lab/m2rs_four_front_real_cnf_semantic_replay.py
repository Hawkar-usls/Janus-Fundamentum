#!/usr/bin/env python3
"""Exact semantic four-front replay for the static 50-regular CNF witness.

Each front starts with the complete 2^7 assignment universe and intersects it
with the satisfying set of one concrete clause at a time, using a different
clause order.  The final model set must be identical in all four directions.

This is exact CNF semantics for this one witness.  It does NOT prove that the
witness is reachable from JANUS runtime states and it does NOT generalize to the
whole abstract state class.  P vs NP remains OPEN.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from experiments.mad_lab import m2rs_four_front_real_cnf_core as C

SCHEMA = "JANUS/MAD-LAB/M2RS-FOUR-FRONT-REAL-CNF-SEMANTIC-REPLAY/v1"
STATUS = "EXACT_WITNESS_SEMANTICS__NO_CLASS_GENERALIZATION"
P_VS_NP = "OPEN"

Assignment = tuple[int, ...]  # -1=False, +1=True


def digest(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def all_assignments() -> list[Assignment]:
    return list(itertools.product((-1, 1), repeat=C.NVAR))


def satisfies_clause(a: Assignment, clause: C.TernaryClause) -> bool:
    return any(sign != 0 and sign == a[i] for i, sign in enumerate(clause))


def satisfies_formula(a: Assignment, clauses: list[C.TernaryClause]) -> bool:
    return all(satisfies_clause(a, clause) for clause in clauses)


def models_direct(clauses: list[C.TernaryClause]) -> list[Assignment]:
    return [a for a in all_assignments() if satisfies_formula(a, clauses)]


def model_signature(a: Assignment) -> str:
    return "".join("+" if x > 0 else "-" for x in a)


def center_left_order(n: int) -> list[int]:
    mid = (n - 1) // 2
    out = [mid]
    k = 1
    while len(out) < n:
        if mid - k >= 0:
            out.append(mid - k)
        if mid + k < n:
            out.append(mid + k)
        k += 1
    return out


def center_right_order(n: int) -> list[int]:
    mid = (n - 1) // 2
    out = [mid]
    k = 1
    while len(out) < n:
        if mid + k < n:
            out.append(mid + k)
        if mid - k >= 0:
            out.append(mid - k)
        k += 1
    return out


def replay_front(name: str, clauses: list[C.TernaryClause], order: list[int]) -> dict[str, Any]:
    assert sorted(order) == list(range(len(clauses)))
    survivors = set(all_assignments())
    counts = [len(survivors)]
    chain = hashlib.sha256()
    elimination_events: list[dict[str, Any]] = []

    for step, idx in enumerate(order, 1):
        clause = clauses[idx]
        before = len(survivors)
        survivors = {a for a in survivors if satisfies_clause(a, clause)}
        after = len(survivors)
        counts.append(after)
        chain.update(json.dumps([idx, sorted(model_signature(a) for a in survivors)], separators=(",", ":")).encode("utf-8"))
        if after < before:
            elimination_events.append({
                "step": step,
                "clause_index": idx,
                "before": before,
                "after": after,
                "eliminated": before - after,
            })

    signatures = sorted(model_signature(a) for a in survivors)
    return {
        "front": name,
        "order_sha256": digest(order),
        "semantic_chain_sha256": chain.hexdigest(),
        "initial_model_count": 2 ** C.NVAR,
        "final_model_count": len(survivors),
        "final_models": signatures,
        "final_model_set_sha256": digest(signatures),
        "monotone_survivor_counts": all(a >= b for a, b in zip(counts, counts[1:])),
        "elimination_event_count": len(elimination_events),
        "first_elimination_events": elimination_events[:12],
        "final_checkpoint": {"step": len(order), "model_count": len(survivors)},
    }


def build_payload() -> dict[str, Any]:
    clauses, construction = C.construct_witness()
    stats = C.exact_stats(clauses)
    C.validate_target_stats(stats)

    direct = models_direct(clauses)
    direct_signatures = sorted(model_signature(a) for a in direct)
    expected = sorted(["+++++++", *(
        "+" * i + "-" + "+" * (C.NVAR - i - 1) for i in range(C.NVAR)
    )])
    assert direct_signatures == expected, direct_signatures

    n = len(clauses)
    orders = {
        "EDGE_LEFT": list(range(n)),
        "CENTER_LEFT": center_left_order(n),
        "CENTER_RIGHT": center_right_order(n),
        "EDGE_RIGHT": list(reversed(range(n))),
    }
    fronts = [replay_front(name, clauses, order) for name, order in orders.items()]
    set_digests = {f["final_model_set_sha256"] for f in fronts}
    chain_digests = {f["semantic_chain_sha256"] for f in fronts}
    all_eight = all(f["final_model_count"] == 8 for f in fronts)
    consensus = len(set_digests) == 1 and len(chain_digests) == 4 and all_eight
    assert consensus
    assert all(f["final_models"] == direct_signatures for f in fronts)

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "static_model": C.STATIC_MODEL,
        "formula_sha256": stats["formula_sha256"],
        "formula_stats": stats,
        "construction_method": construction["method"],
        "direct_truth_table": {
            "assignment_count": 2 ** C.NVAR,
            "satisfying_count": len(direct_signatures),
            "satisfying_models": direct_signatures,
            "model_set_sha256": digest(direct_signatures),
            "structural_description": "ALL_TRUE_OR_EXACTLY_ONE_FALSE",
        },
        "four_front_semantic_replay": {
            "fronts": fronts,
            "all_final_model_sets_equal": len(set_digests) == 1,
            "all_semantic_chains_distinct": len(chain_digests) == 4,
            "consensus": consensus,
            "truth_effect_of_order": "NONE__EXACT_CONJUNCTION_IS_ORDER_INDEPENDENT",
        },
        "hardness_interpretation": {
            "matches_abstract_peak_signature": True,
            "actual_pivot_signature_all_variables": [50, 25, 25],
            "abstract_bound_B": 3433,
            "cap": 3364,
            "abstract_verdict": "OPEN",
            "witness_is_semantically_hard_proved": False,
            "reason": "THIS EXPLICIT WITNESS HAS ONLY 8 SATISFYING ASSIGNMENTS AND IS EXACTLY DECIDABLE BY 128-ROW TRUTH TABLE",
        },
        "anti_self_deception_gate": {
            "exact_semantics_for_this_witness": True,
            "generalizes_to_all_50_regular_balanced_cores": False,
            "repo_normalization_compatibility_proved": False,
            "pipeline_reachability_proved": False,
            "theorem_credit_allowed": False,
            "claim_ceiling": "EXACT_STATIC_WITNESS_SEMANTICS_ONLY__REACHABILITY_AND_CLASS_HARDNESS_UNPROVED",
        },
    }
    payload["audit_sha256"] = digest(payload)
    return payload


def selftest() -> None:
    p = build_payload()
    assert p["direct_truth_table"]["assignment_count"] == 128
    assert p["direct_truth_table"]["satisfying_count"] == 8
    assert p["four_front_semantic_replay"]["consensus"]
    assert not p["hardness_interpretation"]["witness_is_semantically_hard_proved"]
    assert not p["anti_self_deception_gate"]["pipeline_reachability_proved"]
    assert p["P_VS_NP"] == "OPEN"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/mad_lab/m2rs_four_front_real_cnf_semantic_replay.json"))
    args = ap.parse_args()
    selftest()
    payload = build_payload()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
