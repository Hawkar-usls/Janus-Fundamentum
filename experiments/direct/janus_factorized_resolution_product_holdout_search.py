#!/usr/bin/env python3
"""Preregistered blind holdout selector for the C025 factorized-resolution gate.

This program deliberately DOES NOT implement, import, score, or simulate the
future factorized-resolution representation.  It only regenerates the frozen
OPEN3 scaling corpus in its preregistered order and searches for the first exact
ordinary-resolution elimination context whose explicit canonical result exceeds
the same frozen state cap.

Selection contract:
  R1 -> R2 -> R3 -> R4
  connected canonical formula order from the frozen OPEN3 probe
  only Stage3-OPEN formulas
  RAW source -> each B2 macro -> each fitting first-elimination state
  each live diagnostic pivot in ascending numeric order
  first explicit exact elimination with state_units(result) > root N^2 cap

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_one_variable_separator_escape as stage3
from experiments.direct import janus_open3_stage4_bounded_coverage_probe as probe
from experiments.direct import janus_unified_macro_restore_v2 as v2

TRAINING_FINGERPRINT = "990124522dc5ee1a6871de798a0f3ef40f05c20a28cd9f3d9d2f062841695ea6"
CAP_EXPONENT = 2
EXTENSION_EXPONENT = 1

RUNGS = (
    {"id": "R1", "nvars": 4, "clauses": 5, "min_width": 3, "max_width": 3, "limit": 5000},
    {"id": "R2", "nvars": 4, "clauses": 6, "min_width": 3, "max_width": 3, "limit": 10000},
    {"id": "R3", "nvars": 5, "clauses": 6, "min_width": 3, "max_width": 3, "limit": 10000},
    {"id": "R4", "nvars": 5, "clauses": 7, "min_width": 3, "max_width": 3, "limit": 20000},
)


def _cnf_json(cnf: base.CNF) -> list[list[int]]:
    return [list(clause) for clause in cnf]


def _is_tautological_literals(literals) -> bool:
    values = set(literals)
    return any(-literal in values for literal in values)


def explicit_elimination_diagnostic(cnf: base.CNF, pivot: int) -> dict:
    """Build the exact ordinary-resolution result with no cap admission logic."""
    positive = [clause for clause in cnf if pivot in clause]
    negative = [clause for clause in cnf if -pivot in clause]
    untouched = [clause for clause in cnf if pivot not in clause and -pivot not in clause]

    resolvent_instances = []
    width_hist = Counter()
    for left in positive:
        left_tail = tuple(lit for lit in left if lit != pivot)
        for right in negative:
            right_tail = tuple(lit for lit in right if lit != -pivot)
            raw = (*left_tail, *right_tail)
            if _is_tautological_literals(raw):
                continue
            clause = base.canon_clause(raw)
            if clause is None:
                continue
            resolvent_instances.append(clause)
            width_hist[len(clause)] += 1

    unique_resolvents = tuple(sorted(set(resolvent_instances)))
    result = base.canon_cnf((*untouched, *unique_resolvents))
    return {
        "pivot": int(pivot),
        "positive_occurrences": len(positive),
        "negative_occurrences": len(negative),
        "raw_resolution_pairs": len(positive) * len(negative),
        "non_tautological_resolvent_instances": len(resolvent_instances),
        "unique_resolvents_after_dedup": len(unique_resolvents),
        "duplicate_resolvent_instances": len(resolvent_instances) - len(unique_resolvents),
        "resolvent_width_histogram": {str(k): int(v) for k, v in sorted(width_hist.items())},
        "explicit_result_cnf": _cnf_json(result),
        "explicit_result_fingerprint": base.fingerprint(result),
        "explicit_result_state_units": base.state_units(result),
    }


def _context_record(
    *,
    rung: dict,
    formula_index: int,
    source: base.CNF,
    source_fingerprint: str,
    N: int,
    cap: int,
    context_kind: str,
    context: base.CNF,
    provenance: dict,
    pivot: int,
    diagnostic: dict,
) -> dict:
    return {
        "rung": rung["id"],
        "formula_enumeration_index": int(formula_index),
        "source_cnf": _cnf_json(source),
        "source_fingerprint": source_fingerprint,
        "source_N": int(N),
        "state_cap": int(cap),
        "context_kind": context_kind,
        "context_provenance": provenance,
        "context_cnf": _cnf_json(context),
        "context_fingerprint": base.fingerprint(context),
        "context_state_units": base.state_units(context),
        "probe_pivot": int(pivot),
        **diagnostic,
    }


def _probe_context(
    *,
    rung: dict,
    formula_index: int,
    source: base.CNF,
    source_fingerprint: str,
    N: int,
    cap: int,
    context_kind: str,
    context: base.CNF,
    provenance: dict,
    counters: Counter,
):
    counters["contexts_examined"] += 1
    for pivot in base.vars_of(context):
        counters["diagnostic_pivots_examined"] += 1
        diagnostic = explicit_elimination_diagnostic(context, pivot)
        if diagnostic["explicit_result_state_units"] > cap:
            return _context_record(
                rung=rung,
                formula_index=formula_index,
                source=source,
                source_fingerprint=source_fingerprint,
                N=N,
                cap=cap,
                context_kind=context_kind,
                context=context,
                provenance=provenance,
                pivot=pivot,
                diagnostic=diagnostic,
            )
    return None


def _eligible_formulas(rung: dict, counters: Counter):
    universe = probe.clause_universe(rung["nvars"], rung["min_width"], rung["max_width"])
    seen_fingerprints = set()
    connected_examined = 0

    for raw_rows in combinations(universe, rung["clauses"]):
        counters["raw_combinations"] += 1
        cnf = base.canon_cnf(raw_rows)
        if len(cnf) != rung["clauses"]:
            continue
        if len(base.vars_of(cnf)) != rung["nvars"]:
            continue
        fingerprint = base.fingerprint(cnf)
        if fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)
        counters["canonical_distinct_examined"] += 1
        if not probe.primal_connected(cnf):
            continue
        if rung["limit"] and connected_examined >= rung["limit"]:
            break
        connected_examined += 1
        counters["connected_examined"] += 1

        result3 = stage3.solve_one_variable_escape(cnf)
        if result3.get("status") in {"SAT", "UNSAT"}:
            if not stage3.verify_one_variable_escape(cnf, result3):
                raise AssertionError("STAGE3_RETURNED_UNVERIFIED_DECISION")
            counters["stage3_decided"] += 1
            continue

        counters["open3"] += 1
        yield connected_examined, cnf, fingerprint


def main() -> int:
    counters = Counter()
    eligible_source_hash = hashlib.sha256()
    context_hash = hashlib.sha256()
    first_holdout = None

    for rung in RUNGS:
        rung_counters = Counter()
        for formula_index, source, source_fp in _eligible_formulas(rung, rung_counters):
            if source_fp == TRAINING_FINGERPRINT:
                rung_counters["training_fingerprint_exclusions"] += 1
                continue

            eligible_source_hash.update((rung["id"] + ":" + source_fp + "\n").encode())
            N = base.input_size_units(source)
            cap = N ** CAP_EXPONENT

            # 1. RAW_OPEN3_SOURCE_STATE
            raw_provenance = {"kind": "RAW_OPEN3_SOURCE_STATE"}
            context_hash.update((rung["id"] + ":RAW:" + base.fingerprint(source) + "\n").encode())
            hit = _probe_context(
                rung=rung,
                formula_index=formula_index,
                source=source,
                source_fingerprint=source_fp,
                N=N,
                cap=cap,
                context_kind="RAW_OPEN3_SOURCE_STATE",
                context=source,
                provenance=raw_provenance,
                counters=rung_counters,
            )
            if hit is not None:
                first_holdout = hit
                break

            # 2. B2 macro states, then 3. each fitting first-elimination state.
            live_before = tuple(base.vars_of(source))
            fresh = max(live_before, default=0) + 1
            for macro_index, (a, b) in enumerate(v2.all_or_pair_candidates(source), start=1):
                rung_counters["macro_candidates_examined"] += 1
                try:
                    macro, cert = v2.apply_or_pair_v2(source, a, b, fresh)
                except ValueError:
                    rung_counters["macro_candidate_value_errors"] += 1
                    continue
                if base.state_units(macro) > cap:
                    rung_counters["macro_states_over_cap_skipped"] += 1
                    continue
                if not v2.verify_or_pair_v2(source, macro, cert):
                    raise AssertionError("MACRO_REPLAY_FAILED")
                rung_counters["macro_states_under_cap"] += 1
                macro_provenance = {
                    "kind": "B2_OR_PAIR_MACRO_STATE",
                    "macro_index": macro_index,
                    "pair": [a, b],
                    "macro_certificate": cert,
                }
                context_hash.update((rung["id"] + ":MACRO:" + base.fingerprint(macro) + ":" + str(macro_index) + "\n").encode())
                hit = _probe_context(
                    rung=rung,
                    formula_index=formula_index,
                    source=source,
                    source_fingerprint=source_fp,
                    N=N,
                    cap=cap,
                    context_kind="B2_OR_PAIR_MACRO_STATE",
                    context=macro,
                    provenance=macro_provenance,
                    counters=rung_counters,
                )
                if hit is not None:
                    first_holdout = hit
                    break

                for first_pivot in live_before:
                    rung_counters["first_elimination_attempts"] += 1
                    out1, stats1 = base.eliminate_var_capped(macro, first_pivot, cap)
                    if out1 is None:
                        rung_counters["first_eliminations_over_cap"] += 1
                        continue
                    if not base.verify_elimination_transition(macro, first_pivot, out1, cap):
                        raise AssertionError("FIRST_ELIMINATION_REPLAY_FAILED")
                    rung_counters["first_eliminations_fit"] += 1
                    first_provenance = {
                        "kind": "FIRST_ELIMINATION_STATE",
                        "macro_index": macro_index,
                        "pair": [a, b],
                        "first_pivot": int(first_pivot),
                        "first_elimination_pairs": int(stats1.get("pairs", 0)),
                        "macro_fingerprint": base.fingerprint(macro),
                    }
                    context_hash.update((rung["id"] + ":FIRST:" + base.fingerprint(out1) + ":" + str(macro_index) + ":" + str(first_pivot) + "\n").encode())
                    hit = _probe_context(
                        rung=rung,
                        formula_index=formula_index,
                        source=source,
                        source_fingerprint=source_fp,
                        N=N,
                        cap=cap,
                        context_kind="FIRST_ELIMINATION_STATE",
                        context=out1,
                        provenance=first_provenance,
                        counters=rung_counters,
                    )
                    if hit is not None:
                        first_holdout = hit
                        break
                if first_holdout is not None:
                    break
            if first_holdout is not None:
                break

        counters.update({f"{rung['id']}_{key}": value for key, value in rung_counters.items()})
        counters["rungs_executed"] += 1
        counters["open3_total"] += rung_counters["open3"]
        counters["stage3_decided_total"] += rung_counters["stage3_decided"]
        counters["connected_examined_total"] += rung_counters["connected_examined"]
        counters["contexts_examined_total"] += rung_counters["contexts_examined"]
        counters["diagnostic_pivots_examined_total"] += rung_counters["diagnostic_pivots_examined"]
        if first_holdout is not None:
            break

    status = "BLIND_NONTRAINING_OVERCAP_HOLDOUT_FROZEN" if first_holdout is not None else "NO_HOLDOUT_FOUND_IN_FROZEN_OPEN3_CORPUS"
    if first_holdout is None:
        if counters["rungs_executed"] != 4:
            raise AssertionError("NO_HIT_MUST_EXECUTE_ALL_FOUR_RUNGS")
        if counters["open3_total"] != 23956:
            raise AssertionError(f"FROZEN_OPEN3_CORPUS_DRIFT:{counters['open3_total']}")

    payload = {
        "schema": "JANUS/C025/FACTORIZED-RESOLUTION-PRODUCT-HOLDOUT-SEARCH-RESULT/v1",
        "status": status,
        "preregistration": "research/C025_FACTORIZED_RESOLUTION_PRODUCT_HOLDOUT_SEARCH_PREREGISTRATION_2026-08-26.json",
        "training_fingerprint_excluded": TRAINING_FINGERPRINT,
        "factorizer_imported_or_executed": False,
        "cap_exponent": CAP_EXPONENT,
        "extension_exponent": EXTENSION_EXPONENT,
        "counters": dict(sorted(counters.items())),
        "eligible_source_stream_sha256": eligible_source_hash.hexdigest(),
        "examined_context_stream_sha256": context_hash.hexdigest(),
        "holdout": first_holdout,
        "scientific_boundary": {
            "selection_independent_of_future_factorizer_behavior": True,
            "selection_uses_only_explicit_resolution_overcap_condition": True,
            "holdout_found_does_not_mean_factorizer_passes": True,
            "no_hit_requires_new_preregistered_expanded_search": first_holdout is None,
            "universal_stage4_totality": "OPEN",
            "arbitrary_CNF": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
