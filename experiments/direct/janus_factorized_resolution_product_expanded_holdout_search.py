#!/usr/bin/env python3
"""Expanded blind holdout selector for the C025 resolution-product gate.

This program implements only the frozen expanded-holdout preregistration.  It
contains no factorized-resolution representation, no factorizer scoring, and no
future solver primitive.  Formula challenges are selected by a deterministic
SHA-256 counter sampler; truth decisions remain exact and independently replayed.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_one_variable_separator_escape as stage3
from experiments.direct import janus_open3_stage4_bounded_coverage_probe as probe


PREREG = "research/C025_FACTORIZED_RESOLUTION_PRODUCT_EXPANDED_HOLDOUT_PREREGISTRATION_2026-08-26.json"
SEED = "JANUS-C025-FRP-EXPANDED-HOLDOUT-2026-08-26-v1"
TRAINING_FINGERPRINT = "990124522dc5ee1a6871de798a0f3ef40f05c20a28cd9f3d9d2f062841695ea6"
CAP_EXPONENT = 2
MAX_DEPTH = 3

RUNGS = (
    {"id": "E1", "nvars": 8, "clauses": 24, "min_width": 3, "max_width": 4, "accepted_limit": 64, "max_attempts": 4096},
    {"id": "E2", "nvars": 12, "clauses": 48, "min_width": 3, "max_width": 4, "accepted_limit": 64, "max_attempts": 4096},
    {"id": "E3", "nvars": 16, "clauses": 80, "min_width": 3, "max_width": 5, "accepted_limit": 64, "max_attempts": 4096},
    {"id": "E4", "nvars": 20, "clauses": 120, "min_width": 3, "max_width": 5, "accepted_limit": 64, "max_attempts": 4096},
)


def _cnf_json(cnf: base.CNF) -> list[list[int]]:
    return [list(c) for c in cnf]


def _is_tautological_literals(literals: Iterable[int]) -> bool:
    values = set(literals)
    return any(-literal in values for literal in values)


def explicit_elimination_diagnostic(cnf: base.CNF, pivot: int) -> dict:
    positive = [clause for clause in cnf if pivot in clause]
    negative = [clause for clause in cnf if -pivot in clause]
    untouched = [clause for clause in cnf if pivot not in clause and -pivot not in clause]

    instances = []
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
            instances.append(clause)
            width_hist[len(clause)] += 1

    unique_resolvents = tuple(sorted(set(instances)))
    result = base.canon_cnf((*untouched, *unique_resolvents))
    return {
        "probe_pivot": int(pivot),
        "positive_occurrences": len(positive),
        "negative_occurrences": len(negative),
        "raw_resolution_pairs": len(positive) * len(negative),
        "non_tautological_resolvent_instances": len(instances),
        "unique_resolvents_after_dedup": len(unique_resolvents),
        "duplicate_resolvent_instances": len(instances) - len(unique_resolvents),
        "resolvent_width_histogram": {str(k): int(v) for k, v in sorted(width_hist.items())},
        "explicit_result_cnf": _cnf_json(result),
        "explicit_result_fingerprint": base.fingerprint(result),
        "explicit_result_state_units": base.state_units(result),
    }


def _draw_index(rung_id: str, attempt: int, draw: int, universe_len: int) -> int:
    payload = f"{SEED}|{rung_id}|{attempt}|{draw}".encode("ascii")
    value = int.from_bytes(sha256(payload).digest()[:8], "big", signed=False)
    return value % universe_len


def sampled_formula(rung: dict, universe: list[base.Clause], attempt: int) -> base.CNF:
    selected: set[int] = set()
    draw = 0
    while len(selected) < rung["clauses"]:
        selected.add(_draw_index(rung["id"], attempt, draw, len(universe)))
        draw += 1
    return base.canon_cnf(universe[index] for index in sorted(selected))


def _eligible_sources(rung: dict, counters: Counter):
    universe = probe.clause_universe(rung["nvars"], rung["min_width"], rung["max_width"])
    seen: set[str] = set()
    accepted = 0

    for attempt in range(rung["max_attempts"]):
        counters["sampler_attempts"] += 1
        cnf = sampled_formula(rung, universe, attempt)
        if len(cnf) != rung["clauses"]:
            counters["rejected_clause_count"] += 1
            continue
        if len(base.vars_of(cnf)) != rung["nvars"]:
            counters["rejected_variable_coverage"] += 1
            continue
        if not probe.primal_connected(cnf):
            counters["rejected_disconnected"] += 1
            continue
        fp = base.fingerprint(cnf)
        if fp in seen:
            counters["rejected_duplicate_fingerprint"] += 1
            continue
        seen.add(fp)
        accepted += 1
        counters["accepted_formulas"] += 1
        yield attempt, accepted, cnf, fp
        if accepted >= rung["accepted_limit"]:
            return


def _context_from_sequence(
    source: base.CNF,
    sequence: tuple[int, ...],
    cap: int,
    cache: dict[tuple[int, ...], base.CNF | None],
    counters: Counter,
) -> base.CNF | None:
    if sequence in cache:
        counters["prefix_cache_hits"] += 1
        return cache[sequence]
    if not sequence:
        cache[sequence] = source
        return source

    parent = _context_from_sequence(source, sequence[:-1], cap, cache, counters)
    if parent is None:
        cache[sequence] = None
        return None
    pivot = sequence[-1]
    if pivot not in base.vars_of(parent):
        counters["chain_pivot_not_live"] += 1
        cache[sequence] = None
        return None

    counters["capped_chain_elimination_attempts"] += 1
    out, stats = base.eliminate_var_capped(parent, pivot, cap)
    counters["capped_chain_resolution_pairs"] += int(stats.get("pairs", 0))
    if out is None:
        counters["capped_chain_overcap"] += 1
        cache[sequence] = None
        return None
    if not base.verify_elimination_transition(parent, pivot, out, cap):
        raise AssertionError("CHAIN_ELIMINATION_REPLAY_FAILED")
    counters["capped_chain_fit"] += 1
    cache[sequence] = out
    return out


def _freeze_hit(
    *,
    rung: dict,
    sampler_attempt: int,
    accepted_index: int,
    source: base.CNF,
    source_fp: str,
    root_N: int,
    cap: int,
    sequence: tuple[int, ...],
    context: base.CNF,
    diagnostic: dict,
) -> dict:
    return {
        "rung": rung["id"],
        "sampler_attempt_index": int(sampler_attempt),
        "accepted_formula_index": int(accepted_index),
        "source_cnf": _cnf_json(source),
        "source_fingerprint": source_fp,
        "root_N": int(root_N),
        "root_state_cap": int(cap),
        "successful_elimination_depth": len(sequence),
        "pivot_sequence": [int(v) for v in sequence],
        "context_cnf": _cnf_json(context),
        "context_fingerprint": base.fingerprint(context),
        "context_state_units": base.state_units(context),
        **diagnostic,
    }


def main() -> int:
    total = Counter()
    source_stream = sha256()
    context_stream = sha256()
    first_holdout = None

    for rung in RUNGS:
        rc = Counter()
        for sampler_attempt, accepted_index, source, source_fp in _eligible_sources(rung, rc):
            if source_fp == TRAINING_FINGERPRINT:
                rc["training_fingerprint_exclusions"] += 1
                continue

            result3 = stage3.solve_one_variable_escape(source)
            if result3.get("status") in {"SAT", "UNSAT"}:
                if not stage3.verify_one_variable_escape(source, result3):
                    raise AssertionError("STAGE3_RETURNED_UNVERIFIED_DECISION")
                rc["stage3_decided"] += 1
                continue
            rc["stage3_open"] += 1

            source_stream.update(f"{rung['id']}:{sampler_attempt}:{accepted_index}:{source_fp}\n".encode())
            root_N = base.input_size_units(source)
            cap = root_N ** CAP_EXPONENT
            root_vars = tuple(base.vars_of(source))
            cache: dict[tuple[int, ...], base.CNF | None] = {(): source}

            for depth in range(1, MAX_DEPTH + 1):
                for sequence in permutations(root_vars, depth):
                    rc[f"depth_{depth}_sequences_examined"] += 1
                    context = _context_from_sequence(source, sequence, cap, cache, rc)
                    if context is None:
                        continue
                    rc[f"depth_{depth}_reachable_contexts"] += 1
                    context_fp = base.fingerprint(context)
                    context_stream.update(
                        f"{rung['id']}:{sampler_attempt}:{accepted_index}:{depth}:{','.join(map(str, sequence))}:{context_fp}\n".encode()
                    )
                    for pivot in base.vars_of(context):
                        rc["diagnostic_pivots_examined"] += 1
                        diagnostic = explicit_elimination_diagnostic(context, pivot)
                        rc["diagnostic_resolution_pairs"] += diagnostic["raw_resolution_pairs"]
                        if diagnostic["explicit_result_state_units"] > cap:
                            first_holdout = _freeze_hit(
                                rung=rung,
                                sampler_attempt=sampler_attempt,
                                accepted_index=accepted_index,
                                source=source,
                                source_fp=source_fp,
                                root_N=root_N,
                                cap=cap,
                                sequence=sequence,
                                context=context,
                                diagnostic=diagnostic,
                            )
                            break
                    if first_holdout is not None:
                        break
                if first_holdout is not None:
                    break
            if first_holdout is not None:
                break

        total.update({f"{rung['id']}_{key}": value for key, value in rc.items()})
        total["rungs_executed"] += 1
        total["accepted_formulas_total"] += rc["accepted_formulas"]
        total["stage3_open_total"] += rc["stage3_open"]
        total["stage3_decided_total"] += rc["stage3_decided"]
        total["diagnostic_pivots_examined_total"] += rc["diagnostic_pivots_examined"]
        if first_holdout is not None:
            break

    status = (
        "BLIND_CHAINED_RESOLUTION_OVERCAP_HOLDOUT_FROZEN"
        if first_holdout is not None
        else "NO_CHAINED_OVERCAP_HOLDOUT_FOUND_IN_EXPANDED_BLIND_SAMPLE"
    )
    payload = {
        "schema": "JANUS/C025/FACTORIZED-RESOLUTION-PRODUCT-EXPANDED-HOLDOUT-RESULT/v1",
        "status": status,
        "preregistration": PREREG,
        "factorizer_imported_or_executed": False,
        "training_fingerprint_excluded": TRAINING_FINGERPRINT,
        "cap_exponent": CAP_EXPONENT,
        "max_successful_chain_depth_before_probe": MAX_DEPTH,
        "counters": dict(sorted(total.items())),
        "eligible_source_stream_sha256": source_stream.hexdigest(),
        "reachable_context_stream_sha256": context_stream.hexdigest(),
        "holdout": first_holdout,
        "scientific_boundary": {
            "selection_independent_of_future_factorizer_behavior": True,
            "root_cap_recomputed_from_intermediate_state": False,
            "hardware_profile_affects_selection": False,
            "finite_holdout_is_not_totality": True,
            "arbitrary_CNF": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
