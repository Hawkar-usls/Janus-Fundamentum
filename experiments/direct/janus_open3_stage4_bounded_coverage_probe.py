#!/usr/bin/env python3
"""Bounded falsification probe for the current stage-4 JEC grammar.

Enumerate small connected canonical CNFs from a fixed clause universe.  For each
formula:
  stages 1-3 -> if decided, ignore;
  stages 1-3 -> OPEN, then ask stage 4 for one exact progress proof.

The probe is explicitly NOT a theorem.  Its most valuable outcome is a finite
OPEN_3 instance for which the current OR-pair extension grammar finds no exact
strict-progress move.  Such an instance is a concrete target for the next
representation primitive.

Default search: 3 variables, four clauses, clause widths 2..3.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
from itertools import combinations, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_one_variable_separator_escape as stage3
from experiments.direct import janus_jec_extension_progress_proof as stage4


def clause_universe(nvars: int, min_width: int, max_width: int):
    rows = []
    variables = tuple(range(1, nvars + 1))
    for width in range(min_width, max_width + 1):
        for support in combinations(variables, width):
            for signs in product((0, 1), repeat=width):
                clause = tuple(-v if sign else v for v, sign in zip(support, signs))
                rows.append(base.canon_clause(clause))
    return tuple(sorted(set(rows), key=lambda clause: (len(clause), clause)))


def primal_connected(cnf: base.CNF) -> bool:
    variables = base.vars_of(cnf)
    if not variables:
        return False
    adjacency = {variable: set() for variable in variables}
    for clause in cnf:
        scope = sorted({abs(literal) for literal in clause})
        if not scope:
            return False
        for left in scope:
            for right in scope:
                if left != right:
                    adjacency[left].add(right)
    seen = {variables[0]}
    stack = [variables[0]]
    while stack:
        variable = stack.pop()
        for neighbor in adjacency[variable]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == len(variables)


def _frozen_instance_record(cnf: base.CNF, fingerprint: str) -> dict:
    return {
        "fingerprint": fingerprint,
        "cnf": [list(clause) for clause in cnf],
        "variables": list(base.vars_of(cnf)),
        "clauses": len(cnf),
        "state_units": base.state_units(cnf),
        "N": base.input_size_units(cnf),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nvars", type=int, default=3)
    parser.add_argument("--clauses", type=int, default=4)
    parser.add_argument("--min-width", type=int, default=2)
    parser.add_argument("--max-width", type=int, default=3)
    parser.add_argument("--cap-exponent", type=int, default=2)
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="0 means exhaustive; otherwise process at most this many connected canonical CNFs",
    )
    args = parser.parse_args()

    universe = clause_universe(args.nvars, args.min_width, args.max_width)
    totals = {
        "raw_combinations": 0,
        "canonical_distinct_examined": 0,
        "connected_examined": 0,
        "stage3_decided": 0,
        "open3": 0,
        "stage4_progress": 0,
        "open_after_stage4": 0,
    }
    seen_fingerprints = set()
    first_open3 = None
    first_barrier = None
    connected_limit_reached = False

    for raw_rows in combinations(universe, args.clauses):
        totals["raw_combinations"] += 1
        cnf = base.canon_cnf(raw_rows)
        if len(cnf) != args.clauses:
            continue
        if len(base.vars_of(cnf)) != args.nvars:
            continue
        fingerprint = base.fingerprint(cnf)
        if fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)
        totals["canonical_distinct_examined"] += 1
        if not primal_connected(cnf):
            continue
        if args.limit and totals["connected_examined"] >= args.limit:
            connected_limit_reached = True
            break
        totals["connected_examined"] += 1

        result3 = stage3.solve_one_variable_escape(cnf)
        if result3.get("status") in {"SAT", "UNSAT"}:
            if not stage3.verify_one_variable_escape(cnf, result3):
                raise AssertionError("STAGE3_RETURNED_UNVERIFIED_DECISION")
            totals["stage3_decided"] += 1
            continue

        totals["open3"] += 1
        if first_open3 is None:
            first_open3 = {
                **_frozen_instance_record(cnf, fingerprint),
                "stage3_mode": result3.get("mode"),
                "stage3_reason": result3.get("reason"),
            }

        proof = stage4.discover_initial_extension_progress(
            cnf,
            cap_exponent=args.cap_exponent,
            extension_exponent=1,
        )
        if proof is not None:
            if not stage4.verify_extension_progress_proof(cnf, proof, require_initial_context=True):
                raise AssertionError("STAGE4_RETURNED_UNVERIFIED_PROGRESS")
            totals["stage4_progress"] += 1
        else:
            totals["open_after_stage4"] += 1
            if first_barrier is None:
                first_barrier = {
                    **_frozen_instance_record(cnf, fingerprint),
                    "stage3_mode": result3.get("mode"),
                    "stage3_reason": result3.get("reason"),
                    "stage4_cap_exponent": args.cap_exponent,
                }
                break

    status = (
        "FINITE_COUNTEREXAMPLE_TO_CURRENT_STAGE4_GRAMMAR_FOUND"
        if first_barrier is not None
        else "NO_COUNTEREXAMPLE_IN_BOUNDED_PROBE"
    )
    report = {
        "schema": "JANUS/C025/OPEN3-STAGE4-BOUNDED-COVERAGE-PROBE/v2",
        "status": status,
        "search_space": {
            "nvars": args.nvars,
            "clause_count": args.clauses,
            "min_width": args.min_width,
            "max_width": args.max_width,
            "clause_universe_size": len(universe),
            "cap_exponent": args.cap_exponent,
            "limit": args.limit,
            "connected_limit_reached": connected_limit_reached,
        },
        "totals": totals,
        "first_open3": first_open3,
        "first_barrier": first_barrier,
        "scientific_boundary": {
            "bounded_finite_probe_only": True,
            "absence_of_counterexample_is_not_totality_proof": True,
            "presence_of_counterexample_refutes_only_current_stage4_grammar_at_frozen_cap": True,
            "zero_open3_means_no_stage4_coverage_was_exercised": totals["open3"] == 0,
            "universal_OPEN3_move_availability": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
