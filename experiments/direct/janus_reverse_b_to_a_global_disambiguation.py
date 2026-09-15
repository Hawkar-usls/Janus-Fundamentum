#!/usr/bin/env python3
"""Reverse B->A global exact disambiguation on PHP_6_5_C1.

PHP_6_5 has many locally maximal width-3 coordinate systems. We do not choose
among them locally. Every maximum system is streamed through progressively
stronger exact B-side invariants:

  full-residual adjacent-transposition automorphism
    -> exact orbit-template replay
    -> exact histogram quotient
    -> zero surviving quotient states.

No similarity score or heuristic tie-break is allowed. If multiple globally
exact systems survive, the next target is their common quotient/fiber rather
than an arbitrary representative. P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter
from itertools import product
from math import comb
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole
from experiments.direct import janus_php54_auto_block_discovery_quotient_gate as auto

WIDTH = 3
MAX_EXAMPLES = 8


def capture_php65_root_free_tail():
    captured = None
    original = v2.discover_macro_restore_v2

    def capture(state: base.EngineState):
        nonlocal captured
        out = original(state)
        if out is None and not set(base.vars_of(state.residual)).intersection(state.root_vars):
            captured = state
        return out

    v2.discover_macro_restore_v2 = capture
    try:
        result = v2.solve_fail_closed_v2(
            pigeonhole(6, 5), cap_exponent=1, extension_exponent=1
        )
    finally:
        v2.discover_macro_restore_v2 = original
    if result["status"] != "OPEN" or captured is None:
        raise AssertionError("PHP65_ROOT_FREE_TAIL_CAPTURE_FAILED")
    return result, captured


def enumerate_maximum_systems(residual: base.CNF):
    auto.BLOCK_WIDTH = WIDTH
    grouped, inspected, admitted = auto.enumerate_local_gadgets(residual)
    candidates = []
    for key, rows0 in grouped.items():
        rows = sorted(rows0, key=lambda r: r["vars"])
        packings = auto.maximal_disjoint_packings(rows)
        if not packings:
            continue
        size = len(packings[0])
        if size < 2:
            continue
        for indices in packings:
            blocks = tuple(sorted((rows[i]["block"] for i in indices), key=lambda b: tuple(sorted(b))))
            covered = frozenset(v for b in blocks for v in b)
            candidates.append({
                "key": key,
                "blocks": blocks,
                "covered": covered,
                "block_count": size,
            })
    if not candidates:
        raise AssertionError("NO_LOCAL_MAXIMUM_SYSTEMS")
    max_blocks = max(c["block_count"] for c in candidates)
    candidates = [c for c in candidates if c["block_count"] == max_blocks]
    uniq = {}
    for c in candidates:
        partition = tuple(sorted(tuple(sorted(b)) for b in c["blocks"]))
        uniq[(partition, c["key"])] = c
    finalists = [uniq[k] for k in sorted(uniq, key=repr)]
    return finalists, inspected, admitted, len(grouped), max_blocks


def normalize_system(residual: base.CNF, candidate: dict):
    blocks = []
    alphabets = []
    signatures = []
    for raw_block in candidate["blocks"]:
        clauses = auto.local_clauses(residual, raw_block)
        signature, oriented = auto.oriented_signature(clauses, tuple(sorted(raw_block)))
        oriented_clauses = auto.local_clauses(residual, oriented)
        alphabet = auto.local_state_alphabet(oriented, oriented_clauses)
        signatures.append(signature)
        alphabets.append(alphabet)
        blocks.append(oriented)
    if len(set(signatures)) != 1 or len(set(alphabets)) != 1:
        raise AssertionError("LOCAL_SYSTEM_NOT_UNIFORM_AFTER_ORIENTATION")
    if signatures[0] != candidate["key"][0] or len(alphabets[0]) != candidate["key"][1]:
        raise AssertionError("LOCAL_SYSTEM_SIGNATURE_DRIFT")
    blocks = tuple(sorted(blocks, key=lambda b: tuple(sorted(b))))
    outside = tuple(sorted(set(base.vars_of(residual)) - set(candidate["covered"])))
    return blocks, outside, alphabets[0], signatures[0]


def quotient_survivors(templates, blocks, outside, alphabet):
    hists = tuple(auto.compositions(len(blocks), len(alphabet)))
    outside_states = tuple(product((0, 1), repeat=len(outside)))
    quotient_count = len(hists) * len(outside_states)
    survivors = []
    direct_checks = 0
    for outside_bits in outside_states:
        for hist in hists:
            ok = True
            for template in templates:
                direct_checks += 1
                if not auto.template_holds_direct(template, hist, outside_bits, alphabet):
                    ok = False
                    break
            if ok:
                survivors.append((outside_bits, hist))
                if len(survivors) >= 4:
                    return quotient_count, survivors, direct_checks
    return quotient_count, survivors, direct_checks


def compact_system(blocks, outside, alphabet, signature):
    return {
        "blocks": [list(b) for b in blocks],
        "outside": list(outside),
        "q": len(alphabet),
        "signature": [list(x) for x in signature],
    }


def main() -> None:
    engine_result, state = capture_php65_root_free_tail()
    residual = state.residual
    fingerprint = base.fingerprint(residual)
    finalists, inspected, admitted, signature_classes, max_blocks = enumerate_maximum_systems(residual)

    rejection_counts = Counter()
    rejection_examples = {}
    symmetry_pass = []

    # Cheap exact B invariant first: the chosen blocks must really be
    # exchangeable in the ENTIRE residual, not merely look alike locally.
    for idx, candidate in enumerate(finalists):
        blocks, outside, alphabet, signature = normalize_system(residual, candidate)
        try:
            swap_rows = auto.certify_adjacent_block_swaps(residual, blocks)
        except AssertionError as exc:
            reason = str(exc).split("=")[0]
            rejection_counts[reason] += 1
            rejection_examples.setdefault(reason, compact_system(blocks, outside, alphabet, signature))
            continue
        symmetry_pass.append((idx, blocks, outside, alphabet, signature, swap_rows))

    replay_pass = []
    for idx, blocks, outside, alphabet, signature, swap_rows in symmetry_pass:
        try:
            templates, arities, replay = auto.compile_templates(residual, blocks, outside)
        except AssertionError as exc:
            reason = "TEMPLATE_REPLAY_MISMATCH"
            rejection_counts[reason] += 1
            rejection_examples.setdefault(reason, compact_system(blocks, outside, alphabet, signature))
            continue
        replay_pass.append((idx, blocks, outside, alphabet, signature, swap_rows, templates, arities, replay))

    global_rows = []
    globally_admitted = []
    for idx, blocks, outside, alphabet, signature, swap_rows, templates, arities, replay in replay_pass:
        quotient_count, survivors, direct_checks = quotient_survivors(
            templates, blocks, outside, alphabet
        )
        row = compact_system(blocks, outside, alphabet, signature)
        row.update({
            "candidate_index": idx,
            "generator_count": len(swap_rows),
            "template_count": len(templates),
            "max_block_arity": max(arities.values(), default=0),
            "histogram_count": comb(len(blocks) + len(alphabet) - 1, len(alphabet) - 1),
            "outside_state_count": 2 ** len(outside),
            "quotient_state_count": quotient_count,
            "local_valid_assignment_space": (len(alphabet) ** len(blocks)) * (2 ** len(outside)),
            "raw_assignment_space": 2 ** len(base.vars_of(residual)),
            "direct_decision_checks": direct_checks,
            "survivor_count_observed": len(survivors),
            "survivor_examples": [
                {"outside": list(o), "hist": list(h)} for o, h in survivors
            ],
        })
        if survivors:
            row["status"] = "REJECTED_QUOTIENT_SURVIVOR"
            rejection_counts["QUOTIENT_SURVIVOR_EXISTS"] += 1
            if len(global_rows) < MAX_EXAMPLES:
                global_rows.append(row)
            continue
        row["status"] = "GLOBALLY_EXACT_UNSAT_QUOTIENT"
        globally_admitted.append(row)
        if len(global_rows) < MAX_EXAMPLES:
            global_rows.append(row)

    canonical_partitions = {
        tuple(sorted(tuple(sorted(b)) for b in row["blocks"]))
        for row in globally_admitted
    }
    unique_global = len(canonical_partitions) == 1 and bool(globally_admitted)

    # Do not dump thousands of rows; preserve exact counts plus bounded examples.
    report = {
        "schema": "JANUS/C025/REVERSE-B-TO-A-GLOBAL-DISAMBIGUATION/v2",
        "P_VS_NP": "OPEN",
        "direction": "B_TO_A",
        "case": "PHP_6_5_C1",
        "fingerprint": fingerprint,
        "engine_status": engine_result["status"],
        "engine_reason": engine_result["reason"],
        "local_search": {
            "width": WIDTH,
            "manual_block_ids": False,
            "manual_center_id": False,
            "local_finalist_count": len(finalists),
            "maximum_block_count": max_blocks,
            "tuples_inspected": inspected,
            "gadgets_admitted": admitted,
            "signature_classes": signature_classes,
        },
        "global_B_filter": {
            "rule": "FULL_RESIDUAL_S_k_THEN_EXACT_TEMPLATE_REPLAY_THEN_ZERO_QUOTIENT_SURVIVORS",
            "heuristic_tie_break": False,
            "symmetry_pass_count": len(symmetry_pass),
            "template_replay_pass_count": len(replay_pass),
            "globally_admitted_count": len(globally_admitted),
            "unique_global_coordinate_system": unique_global,
            "rejection_counts": dict(sorted(rejection_counts.items())),
            "rejection_examples": rejection_examples,
        },
        "global_examples": global_rows,
        "globally_admitted_examples": globally_admitted[:MAX_EXAMPLES],
        "result": (
            "UNIQUE_GLOBAL_B_DETERMINES_A"
            if unique_global else
            "MULTIPLE_GLOBAL_B_EQUIVALENT_COORDINATE_SYSTEMS"
            if globally_admitted else
            "NO_GLOBAL_B_ADMISSIBLE_SYSTEM"
        ),
        "interpretation": {
            "positive": "A-side local ambiguity is filtered only by exact B-side global semantics.",
            "if_multiple": "Several surviving exact coordinate systems are evidence to quotient their common fiber rather than choose one.",
            "if_none": "The one-layer block quotient is insufficient; search a nested/fiber representation instead of weakening exactness.",
        },
        "scientific_boundary": {
            "finite_php65_probe": True,
            "family_theorem": "OPEN",
            "arbitrary_CNF_coverage": "OPEN",
            "universal_polynomial_algorithm": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
