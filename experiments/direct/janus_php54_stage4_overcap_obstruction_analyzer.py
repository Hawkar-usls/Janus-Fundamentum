#!/usr/bin/env python3
"""Exact diagnostic of the frozen PHP_5_4 Stage-4 negative specimen.

This is NOT a new solver primitive and does not modify Stage-4 grammar.
It replays the already frozen root-free residual and the unchanged
B2-OR-pair + first-elimination grammar, then inspects every second elimination
that fails the same frozen cap.

Goal: expose the structural reason for the cap wall without guessing a repair.
For each over-cap second elimination we charge exact occurrence counts and the
full pre-canonical resolvent product size.  We also canonicalize resolvents only
for DIAGNOSTIC grouping to measure duplication/template reuse; that grouping is
never used to admit a solver transition.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct import janus_jec_extension_progress_proof_gate as frozen_gate
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole


def _capture_state() -> base.EngineState:
    frozen_gate.CAPTURED = None
    previous = v2.discover_macro_restore_v2
    v2.discover_macro_restore_v2 = frozen_gate.capture_root_free_barrier
    try:
        result = v2.solve_fail_closed_v2(
            pigeonhole(5, 4),
            cap_exponent=1,
            extension_exponent=1,
        )
    finally:
        v2.discover_macro_restore_v2 = previous
    if result.get("status") != "OPEN" or frozen_gate.CAPTURED is None:
        raise AssertionError("FROZEN_PHP54_BARRIER_NOT_REPLAYED")
    state = frozen_gate.CAPTURED
    if base.fingerprint(state.residual) != "990124522dc5ee1a6871de798a0f3ef40f05c20a28cd9f3d9d2f062841695ea6":
        raise AssertionError("FROZEN_SPECIMEN_FINGERPRINT_DRIFT")
    return state


def _tautological(clause: tuple[int, ...]) -> bool:
    literals = set(clause)
    return any(-literal in literals for literal in literals)


def _resolvent_diagnostic(cnf: base.CNF, pivot: int) -> dict:
    positive = [clause for clause in cnf if pivot in clause]
    negative = [clause for clause in cnf if -pivot in clause]
    untouched = [clause for clause in cnf if pivot not in clause and -pivot not in clause]

    raw_pair_count = len(positive) * len(negative)
    non_tautological = []
    width_histogram = Counter()
    signature_histogram = Counter()

    for left in positive:
        left_rest = tuple(literal for literal in left if literal != pivot)
        for right in negative:
            right_rest = tuple(literal for literal in right if literal != -pivot)
            raw = tuple(sorted(set((*left_rest, *right_rest)), key=lambda x: (abs(x), x < 0)))
            if _tautological(raw):
                continue
            clause = base.canon_clause(raw)
            non_tautological.append(clause)
            width_histogram[len(clause)] += 1
            # Variable-renaming-free coarse literal-polarity/width signature.
            pos = sum(1 for literal in clause if literal > 0)
            neg = len(clause) - pos
            signature_histogram[(len(clause), pos, neg)] += 1

    unique_resolvents = tuple(sorted(set(non_tautological)))
    multiplicity = Counter(non_tautological)
    repeated = sorted(
        (
            {"clause": list(clause), "multiplicity": count}
            for clause, count in multiplicity.items()
            if count > 1
        ),
        key=lambda row: (-row["multiplicity"], row["clause"]),
    )
    reconstructed = base.canon_cnf((*untouched, *unique_resolvents))

    return {
        "pivot": pivot,
        "positive_occurrences": len(positive),
        "negative_occurrences": len(negative),
        "untouched_clauses": len(untouched),
        "raw_resolution_pairs": raw_pair_count,
        "non_tautological_resolvent_instances": len(non_tautological),
        "unique_resolvents_after_diagnostic_dedup": len(unique_resolvents),
        "duplicate_resolvent_instances": len(non_tautological) - len(unique_resolvents),
        "max_resolvent_multiplicity": max(multiplicity.values(), default=0),
        "repeated_resolvents_top16": repeated[:16],
        "resolvent_width_histogram": {str(k): v for k, v in sorted(width_histogram.items())},
        "coarse_signature_histogram": {
            f"w{width}_p{pos}_n{neg}": count
            for (width, pos, neg), count in sorted(signature_histogram.items())
        },
        "diagnostic_dedup_state_units": base.state_units(reconstructed),
        "diagnostic_dedup_fingerprint": base.fingerprint(reconstructed),
    }


def main() -> int:
    state = _capture_state()
    source = state.residual
    live = tuple(base.vars_of(source))
    fresh = max([*live, *state.root_vars], default=0) + 1
    cap = state.state_cap

    records = []
    first_fit_states = {}
    macro_count = 0
    first_attempts = 0
    first_fits = 0
    second_attempts = 0
    second_over_cap = 0

    for a, b in v2.all_or_pair_candidates(source):
        macro_count += 1
        macro, cert = v2.apply_or_pair_v2(source, a, b, fresh)
        if base.state_units(macro) > cap:
            raise AssertionError("FROZEN_SPECTRUM_EXPECTED_ALL_MACROS_UNDER_CAP")
        if not v2.verify_or_pair_v2(source, macro, cert):
            raise AssertionError("MACRO_REPLAY_FAILED")

        for p1 in live:
            first_attempts += 1
            out1, stats1 = base.eliminate_var_capped(macro, p1, cap)
            if out1 is None:
                continue
            if not base.verify_elimination_transition(macro, p1, out1, cap):
                raise AssertionError("FIRST_ELIM_REPLAY_FAILED")
            first_fits += 1
            key1 = base.fingerprint(out1)
            first_fit_states.setdefault(
                key1,
                {
                    "fingerprint": key1,
                    "state_units": base.state_units(out1),
                    "variables": list(base.vars_of(out1)),
                    "clauses": len(out1),
                    "provenance": [],
                },
            )["provenance"].append({"pair": [a, b], "first_pivot": p1})

            live1 = set(base.vars_of(out1))
            for p2 in live:
                if p2 == p1 or p2 not in live1:
                    continue
                second_attempts += 1
                out2, stats2 = base.eliminate_var_capped(out1, p2, cap)
                if out2 is not None:
                    raise AssertionError("FROZEN_SPECTRUM_EXPECTED_ZERO_SECOND_ELIM_FITS")
                second_over_cap += 1
                diagnostic = _resolvent_diagnostic(out1, p2)
                records.append(
                    {
                        "macro_pair": [a, b],
                        "first_pivot": p1,
                        "first_state_fingerprint": key1,
                        "first_state_units": base.state_units(out1),
                        "first_elimination_pairs": int(stats1.get("pairs", 0)),
                        "second_stats_from_frozen_eliminator": stats2,
                        **diagnostic,
                    }
                )

    if (macro_count, first_attempts, first_fits, second_attempts, second_over_cap) != (160, 2080, 16, 192, 192):
        raise AssertionError(
            f"FROZEN_SPECTRUM_COUNT_DRIFT:{macro_count},{first_attempts},{first_fits},{second_attempts},{second_over_cap}"
        )

    pair_hist = Counter(row["raw_resolution_pairs"] for row in records)
    unique_hist = Counter(row["unique_resolvents_after_diagnostic_dedup"] for row in records)
    dup_hist = Counter(row["duplicate_resolvent_instances"] for row in records)
    dedup_units_hist = Counter(row["diagnostic_dedup_state_units"] for row in records)

    best_diagnostic_compressions = sorted(
        records,
        key=lambda row: (
            row["diagnostic_dedup_state_units"],
            row["unique_resolvents_after_diagnostic_dedup"],
            -row["duplicate_resolvent_instances"],
            row["macro_pair"],
            row["first_pivot"],
            row["pivot"],
        ),
    )[:32]

    payload = {
        "schema": "JANUS/C025/PHP54-STAGE4-OVERCAP-OBSTRUCTION-ANALYSIS/v1",
        "P_VS_NP": "OPEN",
        "specimen": {
            "source_fingerprint": base.fingerprint(source),
            "source_cnf": [list(clause) for clause in source],
            "N": state.N,
            "state_cap": cap,
            "state_units": base.state_units(source),
            "live_variables": list(live),
            "extension_count_before": state.ledger.extension_count,
        },
        "frozen_replay_counts": {
            "macro_candidates": macro_count,
            "first_elimination_attempts": first_attempts,
            "first_elimination_fits": first_fits,
            "unique_first_fit_states": len(first_fit_states),
            "second_elimination_attempts": second_attempts,
            "second_elimination_over_cap": second_over_cap,
            "second_elimination_fits": 0,
            "strict_drop_plan_count": 0,
        },
        "obstruction_summary": {
            "raw_resolution_pair_histogram": {str(k): v for k, v in sorted(pair_hist.items())},
            "unique_resolvent_histogram_after_diagnostic_dedup": {str(k): v for k, v in sorted(unique_hist.items())},
            "duplicate_resolvent_instance_histogram": {str(k): v for k, v in sorted(dup_hist.items())},
            "diagnostic_dedup_state_units_histogram": {str(k): v for k, v in sorted(dedup_units_hist.items())},
            "min_diagnostic_dedup_state_units": min(dedup_units_hist, default=None),
            "max_diagnostic_dedup_state_units": max(dedup_units_hist, default=None),
            "cap": cap,
        },
        "first_fit_states": sorted(first_fit_states.values(), key=lambda row: row["fingerprint"]),
        "best_diagnostic_compressions": best_diagnostic_compressions,
        "all_second_overcap_records_sha256": hashlib.sha256(
            json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "scientific_boundary": {
            "diagnostic_only": True,
            "solver_grammar_changed": False,
            "diagnostic_dedup_is_not_an_admitted_transition": True,
            "new_representation_primitive_synthesized": False,
            "universal_stage4_totality": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
