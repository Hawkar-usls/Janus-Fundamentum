#!/usr/bin/env python3
"""Hostile finite search aimed specifically at HIGH_VOLUME_RESCUE_TOTALITY.

Generate deterministic random width-4 CNFs, run only the frozen
PIRC_DECISION_CORE_V0_4 truth channel, and measure whether a trajectory ever
crosses the original-volume threshold max_state_units > N.  Stop at the first
OPEN and freeze it.  A brute-force label is computed only *after* OPEN and has
zero theorem authority.

Finite success is never promoted.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
import random
from itertools import product

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_pirc_decision_core_v0_4 as core

P_VS_NP = "OPEN"


def random_width_cnf(nvars: int, nclauses: int, width: int, seed: int) -> base.CNF:
    rng = random.Random(seed)
    rows = set()
    attempts = 0
    while len(rows) < nclauses:
        attempts += 1
        if attempts > 100000:
            raise RuntimeError("CLAUSE_GENERATION_EXHAUSTED")
        support = sorted(rng.sample(range(1, nvars + 1), width))
        clause = tuple(v if rng.getrandbits(1) else -v for v in support)
        canon = base.canon_clause(clause)
        if canon is not None:
            rows.add(canon)
    return base.canon_cnf(rows)


def brute_force_truth(cnf: base.CNF) -> str:
    """Research-only finite labeler; never called unless theorem core returned OPEN."""
    variables = base.vars_of(cnf)
    for bits in product((0, 1), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        if base.verify_total_assignment(cnf, assignment):
            return "SAT"
    return "UNSAT"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases-per-rung", type=int, default=2)
    args = parser.parse_args()

    # Frozen before results.  Width 4 avoids making the root itself a width-3
    # resolution specimen, while the increasing density encourages elimination
    # products and therefore representation-volume growth.
    rungs = (
        ("W4_N8_M20", 8, 20, 5100),
        ("W4_N10_M30", 10, 30, 5200),
        ("W4_N12_M42", 12, 42, 5300),
        ("W4_N14_M56", 14, 56, 5400),
        ("W4_N16_M64", 16, 64, 5500),
    )
    width = 4
    totals = {
        "examined": 0,
        "SAT": 0,
        "UNSAT": 0,
        "OPEN": 0,
        "crossed_original_N": 0,
        "max_volume_ratio": 0.0,
    }
    rows = []
    first_open = None
    first_high_volume = None

    for rung_id, nvars, nclauses, seed0 in rungs:
        rr = {
            "id": rung_id,
            "examined": 0,
            "SAT": 0,
            "UNSAT": 0,
            "OPEN": 0,
            "crossed_original_N": 0,
            "max_volume_ratio": 0.0,
        }
        for offset in range(args.cases_per_rung):
            seed = seed0 + offset
            cnf = random_width_cnf(nvars, nclauses, width, seed)
            result = core.solve_decision_core(cnf)
            status = result["status"]
            if status not in {"SAT", "UNSAT", "OPEN"}:
                raise AssertionError("UNEXPECTED_DECISION_STATUS")
            N = int(result["N"])
            max_units = int(result["ledger"]["max_state_units"])
            ratio = max_units / max(1, N)
            crossed = max_units > N

            totals["examined"] += 1
            totals[status] += 1
            rr["examined"] += 1
            rr[status] += 1
            totals["max_volume_ratio"] = max(totals["max_volume_ratio"], ratio)
            rr["max_volume_ratio"] = max(rr["max_volume_ratio"], ratio)
            if crossed:
                totals["crossed_original_N"] += 1
                rr["crossed_original_N"] += 1
                if first_high_volume is None:
                    first_high_volume = {
                        "rung": rung_id,
                        "seed": seed,
                        "fingerprint": base.fingerprint(cnf),
                        "N": N,
                        "max_state_units": max_units,
                        "max_volume_ratio": ratio,
                        "status": status,
                        "extension_count": int(result["ledger"]["extension_count"]),
                    }

            if status == "OPEN":
                first_open = {
                    "rung": rung_id,
                    "seed": seed,
                    "fingerprint": base.fingerprint(cnf),
                    "cnf": [list(c) for c in cnf],
                    "N": N,
                    "state_cap": int(result["state_cap"]),
                    "max_state_units": max_units,
                    "max_volume_ratio": ratio,
                    "reason": result["reason"],
                    "missing_bridge": result.get("missing_bridge"),
                    "residual_fingerprint": result["residual_fingerprint"],
                    "residual_units": int(result["residual_units"]),
                    "extension_count": int(result["ledger"]["extension_count"]),
                    "finite_truth_label": brute_force_truth(cnf),
                    "truth_label_method": "EXHAUSTIVE_ASSIGNMENT_RESEARCH_ONLY_AFTER_OPEN",
                    "event_kinds": [event.get("kind") for event in result.get("events", [])],
                    "ledger": result["ledger"],
                }
                break
        rows.append(rr)
        if first_open is not None:
            break

    report = {
        "schema": "JANUS/C025/V0.4-HIGH-VOLUME-RANDOM-CNF-PROBE/v1",
        "status": "FINITE_OPEN_COUNTEREXAMPLE_FOUND" if first_open else "NO_OPEN_IN_BOUNDED_HIGH_VOLUME_SEARCH",
        "decision_core": "PIRC_DECISION_CORE_V0_4",
        "width": width,
        "rungs": rows,
        "totals": totals,
        "first_high_volume": first_high_volume,
        "first_open": first_open,
        "scientific_boundary": {
            "bounded_finite_probe_only": True,
            "aimed_at_high_volume_rescue_region": True,
            "absence_of_open_is_not_totality_proof": True,
            "bruteforce_forbidden_from_theorem_runtime": True,
            "found_open_refutes_only_v0_4_totality": True,
            "HIGH_VOLUME_RESCUE_TOTALITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
