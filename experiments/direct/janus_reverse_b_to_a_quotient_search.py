#!/usr/bin/env python3
"""C025 reverse B->A exact quotient search.

Instead of fixing a known block width and pushing RAW CNF forward, this pass
starts from the desired proof object B:

  * exact replay of the frozen residual,
  * certified exchangeability by adjacent-transposition generators,
  * a smaller quotient state space than the local-valid explicit space,
  * an exact UNSAT decision on that quotient,
  * and an explicit resource ledger.

It then searches a bounded width grammar for a coordinate system A->B. Width
is NOT supplied as 3. Candidates are admitted only by exact semantics/replay
and a deterministic resource ordering; similarity to the known PHP structure
is never a criterion.

This is still a finite frozen-case experiment. The width grammar is bounded,
family scaling is unproved, arbitrary-CNF coverage is open, and P_VS_NP=OPEN.
"""
from __future__ import annotations

from collections import Counter
from itertools import product
from math import comb, factorial
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

WIDTH_GRAMMAR = tuple(range(2, 5))
MAX_QUOTIENT_ENUMERATION = 250_000
CAPTURED: base.EngineState | None = None


def capture_frozen_php54() -> tuple[dict, base.EngineState]:
    global CAPTURED
    CAPTURED = None
    original = v2.discover_macro_restore_v2

    def capture(state: base.EngineState):
        global CAPTURED
        out = original(state)
        if out is None and not any(v in set(state.root_vars) for v in base.vars_of(state.residual)):
            CAPTURED = state
        return out

    v2.discover_macro_restore_v2 = capture
    try:
        result = v2.solve_fail_closed_v2(
            pigeonhole(5, 4), cap_exponent=1, extension_exponent=1
        )
    finally:
        v2.discover_macro_restore_v2 = original

    if result["status"] != "OPEN" or CAPTURED is None:
        raise AssertionError("FROZEN_PHP54_CAPTURE_FAILED")
    return result, CAPTURED


def exact_candidate(residual: base.CNF, width: int) -> dict:
    auto.BLOCK_WIDTH = width
    discovery = auto.discover_unique_block_system(residual)
    blocks = discovery["blocks"]
    outside = discovery["outside"]
    local_states = discovery["alphabet"]

    if not blocks or any(len(block) != width for block in blocks):
        raise AssertionError("WIDTH_MISMATCH_AFTER_DISCOVERY")

    swap_rows = auto.certify_adjacent_block_swaps(residual, blocks)
    templates, arities, replay_rows = auto.compile_templates(residual, blocks, outside)
    max_block_arity = max(arities.values(), default=0)

    k = len(blocks)
    q = len(local_states)
    outside_count = len(outside)
    histogram_count = comb(k + q - 1, q - 1)
    quotient_count = (2 ** outside_count) * histogram_count
    local_valid_space = (2 ** outside_count) * (q ** k)
    raw_space = 2 ** len(base.vars_of(residual))

    if quotient_count >= local_valid_space:
        raise AssertionError("NO_EXACT_STATE_COLLAPSE")
    if quotient_count > MAX_QUOTIENT_ENUMERATION:
        raise AssertionError(f"QUOTIENT_ENUMERATION_CAP_EXCEEDED={quotient_count}")

    hists = tuple(auto.compositions(k, q))
    outside_states = tuple(product((0, 1), repeat=outside_count))
    quotient_states = tuple((bits, hist) for bits in outside_states for hist in hists)
    if len(quotient_states) != quotient_count:
        raise AssertionError("QUOTIENT_COUNT_REPLAY_MISMATCH")

    # Exact coverage ledger: histogram orbits cover every assignment satisfying
    # the discovered local gadget constraints exactly once.
    orbit_coverage = 0
    for hist in hists:
        denom = 1
        for count in hist:
            denom *= factorial(count)
        orbit_coverage += factorial(k) // denom
    orbit_coverage *= 2 ** outside_count
    if orbit_coverage != local_valid_space:
        raise AssertionError("HISTOGRAM_ORBIT_COVERAGE_MISMATCH")

    violating = Counter()
    crosschecks = 0
    survivors = []
    for outside_bits, hist in quotient_states:
        failed = []
        for idx, template in enumerate(templates):
            direct = auto.template_holds_direct(template, hist, outside_bits, local_states)
            explicit = auto.explicit_template_holds(
                template, blocks, outside, hist, outside_bits, local_states
            )
            if direct != explicit:
                raise AssertionError("DIRECT_EXPLICIT_TEMPLATE_MISMATCH")
            crosschecks += 1
            if not direct:
                failed.append(idx)
        if failed:
            violating[min(failed)] += 1
        else:
            survivors.append((outside_bits, hist))

    all_rejected = not survivors
    minimum = None
    if all_rejected and len(templates) <= 16:
        minimum = auto.minimum_unsat_template_subset(
            templates, quotient_states, local_states
        )
        if minimum is None:
            raise AssertionError("MINIMUM_UNSAT_TEMPLATE_SYNTHESIS_FAILED")

    certificate_templates = templates if minimum is None else tuple(templates[i] for i in minimum)
    certificate = {
        "kind": "REVERSE_B_TO_A_EXACT_QUOTIENT_CERTIFICATE",
        "source_fingerprint": base.fingerprint(residual),
        "discovered_block_width": width,
        "blocks": [list(b) for b in blocks],
        "outside_variables": list(outside),
        "local_clause_signature": [list(x) for x in discovery["signature"]],
        "local_states": [list(x) for x in local_states],
        "adjacent_swap_generators": [[i, i + 1] for i in range(k - 1)],
        "orbit_templates": [[list(atom) for atom in t] for t in certificate_templates],
        "histogram_sum": k,
    }
    cert_bytes = len(json.dumps(certificate, sort_keys=True, separators=(",", ":")).encode("utf-8"))

    return {
        "width": width,
        "status": "UNSAT" if all_rejected else "SURVIVOR_EXISTS",
        "exact_full_residual_replay": True,
        "all_adjacent_generators_preserve_residual": all(
            row["preserves_residual"] for row in swap_rows
        ),
        "blocks": [list(b) for b in blocks],
        "block_count": k,
        "outside_variables": list(outside),
        "local_state_count": q,
        "local_state_alphabet": [list(x) for x in local_states],
        "template_count": len(templates),
        "max_block_arity": max_block_arity,
        "template_replay": replay_rows,
        "histogram_count": histogram_count,
        "quotient_state_count": quotient_count,
        "local_valid_assignment_space": local_valid_space,
        "raw_assignment_space": raw_space,
        "compression_ratio_local_valid_to_quotient": local_valid_space / quotient_count,
        "compression_ratio_raw_to_quotient": raw_space / quotient_count,
        "direct_vs_explicit_crosschecks": crosschecks,
        "survivor_count": len(survivors),
        "minimum_unsat_template_count": None if minimum is None else len(minimum),
        "minimum_unsat_template_indices": None if minimum is None else list(minimum),
        "certificate_json_bytes": cert_bytes,
        "resource_key": [quotient_count, cert_bytes, width],
        "discovery_ledger": {
            "tuples_inspected": discovery["triples_inspected"],
            "local_gadgets_admitted": discovery["local_gadgets_admitted"],
            "signature_classes": discovery["signature_classes"],
        },
        "violating_template_histogram": {str(k): v for k, v in sorted(violating.items())},
    }


def main() -> None:
    old_result, state = capture_frozen_php54()
    residual = state.residual
    fingerprint = base.fingerprint(residual)
    if fingerprint != "990124522dc5ee1a6871de798a0f3ef40f05c20a28cd9f3d9d2f062841695ea6":
        raise AssertionError("FROZEN_FINGERPRINT_DRIFT")

    candidates = []
    failures = []
    for width in WIDTH_GRAMMAR:
        try:
            candidates.append(exact_candidate(residual, width))
        except AssertionError as exc:
            failures.append({"width": width, "reason": str(exc)})

    admitted = [
        c for c in candidates
        if c["status"] == "UNSAT"
        and c["exact_full_residual_replay"]
        and c["all_adjacent_generators_preserve_residual"]
    ]
    if not admitted:
        raise AssertionError("NO_EXACT_REVERSE_B_TO_A_QUOTIENT_FOUND")

    # Deterministic proof-resource order, not a heuristic score.
    winner = min(admitted, key=lambda c: tuple(c["resource_key"]))

    report = {
        "schema": "JANUS/C025/REVERSE-B-TO-A-QUOTIENT-SEARCH/v1",
        "P_VS_NP": "OPEN",
        "direction": "B_TO_A",
        "question": "FIND_AN_EXACT_ALGEBRAIC_REPRESENTATION_WHERE_THE_EXPONENTIAL_SPACE_IS_REDUNDANT_COORDINATIZATION",
        "frozen_case": "PHP_5_4_C1",
        "fingerprint": fingerprint,
        "old_engine_status": old_result["status"],
        "manual_block_width": False,
        "width_search_grammar": list(WIDTH_GRAMMAR),
        "admission_rule": "EXACT_REPLAY_AND_EXACT_GENERATOR_SYMMETRY_AND_STRICT_STATE_COLLAPSE_AND_EXACT_QUOTIENT_DECISION",
        "selection_rule": "MIN_LEXICOGRAPHIC_EXACT_RESOURCE_KEY_QUOTIENT_STATES_CERTIFICATE_BYTES_WIDTH",
        "candidates": candidates,
        "failed_widths": failures,
        "winner": winner,
        "reverse_result": {
            "found": True,
            "discovered_width": winner["width"],
            "block_count": winner["block_count"],
            "local_state_count": winner["local_state_count"],
            "quotient_state_count": winner["quotient_state_count"],
            "status": winner["status"],
        },
        "paradox_rule": {
            "name": "JANUS_MATHEMATICAL_ALGEBRAIC_PARADOX_RULE",
            "gate": "EXACT_FORWARD_SEMANTICS_EXACT_REPLAY_AND_RESOURCE_LEDGER_REQUIRED",
            "interpretation": "THE_EXPONENTIAL_COORDINATES_MAY_BE_REDUNDANT_ONLY_IF_THE_SMALLER_REPRESENTATION_REPLAYS_THE_SAME_OBJECT_EXACTLY",
        },
        "scientific_boundary": {
            "finite_frozen_witness": True,
            "width_search_bound_is_fixed_not_general": True,
            "PHP_family_scaling": "OPEN",
            "arbitrary_CNF_coverage": "OPEN",
            "universal_polynomial_algorithm": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
