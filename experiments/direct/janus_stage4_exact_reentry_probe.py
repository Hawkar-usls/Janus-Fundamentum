#!/usr/bin/env python3
"""Bounded research probe: does ONE verified Stage4 move re-enter exact typed lanes?

This probe does NOT iterate Stage4. It enumerates the same kind of connected
small CNFs used by the frozen OPEN3 probe, then for each Stage-3 OPEN instance:
  1. build one Stage4 progress proof;
  2. independently verify it;
  3. run the already admitted exact typed lanes on the verified result CNF;
  4. record whether a second Stage4 move would actually be needed.

Finite results are research evidence only. P_VS_NP and universal GPEI remain OPEN.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_one_variable_separator_escape as stage3
from experiments.direct import janus_jec_extension_progress_proof as stage4
from experiments.direct import janus_matching_hall_escape as hall
from experiments.direct import janus_open3_stage4_bounded_coverage_probe as open3_probe

P_VS_NP = "OPEN"


def _exact_reentry(cnf) -> dict:
    hall_result = hall.solve_matching_hall_escape(cnf)
    if hall_result.get("status") in {"SAT", "UNSAT"}:
        if not hall.verify_matching_hall_escape(cnf, hall_result):
            raise AssertionError("HALL_REENTRY_FAILED_REPLAY")
        return {"status": hall_result["status"], "mode": "MATCHING_HALL_CARDINALITY_ESCAPE"}

    result = stage3.solve_one_variable_escape(cnf)
    if result.get("status") in {"SAT", "UNSAT"}:
        if not stage3.verify_one_variable_escape(cnf, result):
            raise AssertionError("STAGE3_REENTRY_FAILED_REPLAY")
        return {"status": result["status"], "mode": result.get("mode")}
    return {"status": "OPEN"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nvars", type=int, default=4)
    parser.add_argument("--clauses", type=int, default=5)
    parser.add_argument("--min-width", type=int, default=3)
    parser.add_argument("--max-width", type=int, default=3)
    parser.add_argument("--cap-exponent", type=int, default=2)
    parser.add_argument("--limit", type=int, default=5000)
    args = parser.parse_args()

    universe = open3_probe.clause_universe(args.nvars, args.min_width, args.max_width)
    totals = {
        "connected_examined": 0,
        "stage3_decided": 0,
        "open3": 0,
        "stage4_no_move": 0,
        "stage4_verified": 0,
        "decided_after_one_stage4": 0,
        "still_open_after_one_stage4": 0,
    }
    first_requires_second = None
    first_closed_after_one = None
    seen = set()

    for raw_rows in combinations(universe, args.clauses):
        cnf = base.canon_cnf(raw_rows)
        if len(cnf) != args.clauses or len(base.vars_of(cnf)) != args.nvars:
            continue
        fingerprint = base.fingerprint(cnf)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        if not open3_probe.primal_connected(cnf):
            continue
        if args.limit and totals["connected_examined"] >= args.limit:
            break
        totals["connected_examined"] += 1

        result3 = stage3.solve_one_variable_escape(cnf)
        if result3.get("status") in {"SAT", "UNSAT"}:
            if not stage3.verify_one_variable_escape(cnf, result3):
                raise AssertionError("STAGE3_DECISION_FAILED_REPLAY")
            totals["stage3_decided"] += 1
            continue

        totals["open3"] += 1
        proof = stage4.discover_initial_extension_progress(
            cnf,
            cap_exponent=args.cap_exponent,
            extension_exponent=1,
        )
        if proof is None:
            totals["stage4_no_move"] += 1
            if first_requires_second is None:
                first_requires_second = {
                    "reason": "NO_FIRST_STAGE4_MOVE",
                    "source_fingerprint": fingerprint,
                    "source_cnf": [list(c) for c in cnf],
                }
            continue
        if not stage4.verify_extension_progress_proof(cnf, proof, require_initial_context=True):
            raise AssertionError("STAGE4_PROGRESS_FAILED_REPLAY")
        totals["stage4_verified"] += 1

        result_cnf = base.canon_cnf(proof.get("result_cnf", []))
        if base.fingerprint(result_cnf) != proof.get("result_fingerprint"):
            raise AssertionError("STAGE4_RESULT_BINDING_FAILED")

        reentry = _exact_reentry(result_cnf)
        record = {
            "source_fingerprint": fingerprint,
            "source_cnf": [list(c) for c in cnf],
            "stage4_result_fingerprint": proof.get("result_fingerprint"),
            "stage4_result_cnf": [list(c) for c in result_cnf],
            "before_phi": proof.get("before_phi"),
            "after_phi": proof.get("after_phi"),
            "proof_bytes": proof.get("proof_bytes"),
            "reentry_status": reentry["status"],
            "reentry_mode": reentry.get("mode"),
        }
        if reentry["status"] in {"SAT", "UNSAT"}:
            totals["decided_after_one_stage4"] += 1
            if first_closed_after_one is None:
                first_closed_after_one = record
        else:
            totals["still_open_after_one_stage4"] += 1
            if first_requires_second is None:
                first_requires_second = record

    report = {
        "schema": "JANUS/C025/STAGE4-EXACT-REENTRY-BOUNDED-PROBE/v1",
        "status": (
            "FINITE_SECOND_STAGE4_REQUIREMENT_FOUND"
            if first_requires_second is not None
            else "NO_SECOND_STAGE4_REQUIREMENT_IN_BOUNDED_PROBE"
        ),
        "search_space": {
            "nvars": args.nvars,
            "clauses": args.clauses,
            "min_width": args.min_width,
            "max_width": args.max_width,
            "cap_exponent": args.cap_exponent,
            "limit": args.limit,
        },
        "totals": totals,
        "first_closed_after_one_stage4": first_closed_after_one,
        "first_requires_second_stage4": first_requires_second,
        "scientific_boundary": {
            "bounded_finite_probe_only": True,
            "one_stage4_move_maximum": True,
            "absence_of_second_stage4_requirement_is_not_universal_closure": True,
            "universal_GPEI_preservation": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
