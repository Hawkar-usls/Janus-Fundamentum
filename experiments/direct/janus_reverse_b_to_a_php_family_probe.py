#!/usr/bin/env python3
"""Finite PHP family transfer probe for the reverse B->A quotient search.

The same reverse-search code is applied unchanged to PHP_(m+1)_m cases.  No
block ids, center id, or block width are supplied.  If the C=1 engine reaches a
root-free OPEN residual, the bounded width grammar {2,3,4} is searched and the
best exact quotient certificate is reported.  Capture failure is a scientific
negative/unknown, not an excuse to change the grammar per instance.

Finite family evidence only.  P_VS_NP=OPEN.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole
from experiments.direct import janus_reverse_b_to_a_quotient_search as reverse


def capture_case(pigeons: int, holes: int):
    captured = None
    original = v2.discover_macro_restore_v2

    def capture(state: base.EngineState):
        nonlocal captured
        out = original(state)
        if out is None:
            captured = state
        return out

    v2.discover_macro_restore_v2 = capture
    try:
        result = v2.solve_fail_closed_v2(
            pigeonhole(pigeons, holes), cap_exponent=1, extension_exponent=1
        )
    finally:
        v2.discover_macro_restore_v2 = original
    return result, captured


def probe(pigeons: int, holes: int) -> dict:
    result, state = capture_case(pigeons, holes)
    row = {
        "case": f"PHP_{pigeons}_{holes}_C1",
        "pigeons": pigeons,
        "holes": holes,
        "engine_status": result["status"],
        "engine_reason": result["reason"],
        "N": result["N"],
        "state_cap": result["state_cap"],
        "manual_block_ids": False,
        "manual_center_id": False,
        "manual_block_width": False,
        "width_search_grammar": list(reverse.WIDTH_GRAMMAR),
        "P_VS_NP": "OPEN",
    }
    if state is None:
        row["reverse_status"] = "NO_CAPTURED_OPEN_STATE"
        return row

    residual = state.residual
    row.update({
        "captured_residual_fingerprint": base.fingerprint(residual),
        "captured_live_variables": len(base.vars_of(residual)),
        "captured_root_variables_live": sorted(
            set(base.vars_of(residual)).intersection(state.root_vars)
        ),
        "captured_residual_units": base.state_units(residual),
    })
    if row["captured_root_variables_live"]:
        row["reverse_status"] = "CAPTURE_HAS_LIVE_ROOTS_NOT_COMPARABLE_TO_PHP54_TAIL"
        return row

    candidates = []
    failures = []
    for width in reverse.WIDTH_GRAMMAR:
        try:
            candidates.append(reverse.exact_candidate(residual, width))
        except AssertionError as exc:
            failures.append({"width": width, "reason": str(exc)})

    admitted = [
        c for c in candidates
        if c["status"] == "UNSAT"
        and c["exact_full_residual_replay"]
        and c["all_adjacent_generators_preserve_residual"]
    ]
    row["failed_widths"] = failures
    row["admitted_candidate_count"] = len(admitted)
    if not admitted:
        row["reverse_status"] = "NO_EXACT_UNSAT_QUOTIENT_IN_FROZEN_WIDTH_GRAMMAR"
        row["candidates"] = candidates
        return row

    winner = min(admitted, key=lambda c: tuple(c["resource_key"]))
    row.update({
        "reverse_status": "EXACT_B_TO_A_QUOTIENT_FOUND",
        "discovered_width": winner["width"],
        "block_count": winner["block_count"],
        "outside_variable_count": len(winner["outside_variables"]),
        "local_state_count": winner["local_state_count"],
        "histogram_count": winner["histogram_count"],
        "quotient_state_count": winner["quotient_state_count"],
        "local_valid_assignment_space": winner["local_valid_assignment_space"],
        "raw_assignment_space": winner["raw_assignment_space"],
        "certificate_json_bytes": winner["certificate_json_bytes"],
        "max_block_arity": winner["max_block_arity"],
        "survivor_count": winner["survivor_count"],
        "blocks": winner["blocks"],
        "outside_variables": winner["outside_variables"],
        "resource_key": winner["resource_key"],
    })
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pigeons", type=int, required=True)
    ap.add_argument("--holes", type=int, required=True)
    args = ap.parse_args()
    if args.pigeons != args.holes + 1:
        raise SystemExit("This probe is frozen to PHP_(m+1)_m")

    row = probe(args.pigeons, args.holes)
    report = {
        "schema": "JANUS/C025/REVERSE-B-TO-A-PHP-FAMILY-PROBE/v1",
        "direction": "B_TO_A",
        "same_code_and_width_grammar_as_php54": True,
        "row": row,
        "parametric_hypothesis_gate": {
            "candidate_formula_if_q4_c1_repeats": "Q(k)=2*C(k+3,3)=((k+1)(k+2)(k+3))/3",
            "formula_status": "HYPOTHESIS_UNTIL_MULTIPLE_INDEPENDENT_ROWS_REPLAY",
        },
        "scientific_boundary": {
            "finite_family_probe_only": True,
            "no_family_theorem_from_finite_samples": True,
            "arbitrary_CNF_coverage": "OPEN",
            "universal_polynomial_algorithm": "OPEN",
            "P_VS_NP": "OPEN",
        },
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
