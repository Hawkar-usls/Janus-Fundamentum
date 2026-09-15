#!/usr/bin/env python3
"""C025 reverse B->A exact pair-relation + nested-core fiber synthesizer.

No block ids, center ids, or block width are supplied. From a frozen CNF the
machine derives a candidate coordinate system from exact signed binary relation
classes and then subjects that candidate to proof gates:

  signed incidence colors (candidate invariant only)
    -> endpoint-order-invariant signed pair relations
    -> union every nonempty matching relation (degree <= 1)
    -> connected components
    -> repeated component-size class = candidate outer fibers
    -> canonical internal orientation
    -> full-residual adjacent swaps (certificate for S_k)
    -> exact local block alphabet q
    -> exact orbit-template replay
    -> exact local alphabet of the remaining core
    -> histogram(blocks) x core-alphabet nested quotient
    -> zero-survivor exact certificate.

The pair-relation construction is only a deterministic candidate generator. It
is never counted as a semantic proof. Admission requires exact full-residual
symmetry, exact template replay and exhaustive zero-survivor replay of the
finite nested quotient.

Complexity debts are explicit: internal orientation currently uses w!, local
block alphabet synthesis uses 2^w, core alphabet synthesis uses 2^core, and the
histogram count can grow superpolynomially if q grows. Three finite witnesses
do not establish a PHP-family theorem or P=NP. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole
from experiments.direct import janus_php54_auto_block_discovery_quotient_gate as auto
from experiments.direct import janus_reverse_b_to_a_role_fiber_synthesizer as role

MAX_COMPONENT_WIDTH = 8
MAX_EXACT_NESTED_QUOTIENT_STATES = 100_000


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
    if result["status"] != "OPEN" or captured is None:
        raise AssertionError("OPEN_STATE_CAPTURE_FAILED")
    return result, captured


def canonical_pair_relation_key(cnf: base.CNF, a: int, b: int, colors: dict[int, int]):
    """Canonicalize a signed binary incidence relation against endpoint reversal."""
    ab = role.pair_relation_signature(cnf, a, b, colors)
    ba = role.pair_relation_signature(cnf, b, a, colors)
    ka = (colors[a], colors[b], ab)
    kb = (colors[b], colors[a], ba)
    return min(ka, kb, key=repr)


def matching_relation_components(cnf: base.CNF):
    colors, color_classes, refinement_history = role.exact_role_refinement(cnf)
    relations = defaultdict(list)
    variables = base.vars_of(cnf)
    for a, b in combinations(variables, 2):
        key = canonical_pair_relation_key(cnf, a, b, colors)
        if key[2]:
            relations[key].append((a, b))

    matching_keys = []
    matching_edges = []
    for key in sorted(relations, key=repr):
        pairs = relations[key]
        degree = Counter()
        for a, b in pairs:
            degree[a] += 1
            degree[b] += 1
        if pairs and max(degree.values(), default=0) <= 1:
            matching_keys.append({
                "key": repr(key),
                "edge_count": len(pairs),
                "support_count": len(degree),
            })
            matching_edges.extend(pairs)

    adjacency = {v: set() for v in variables}
    for a, b in matching_edges:
        adjacency[a].add(b)
        adjacency[b].add(a)

    seen = set()
    components = []
    for start in variables:
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component = []
        while stack:
            v = stack.pop()
            component.append(v)
            for w in sorted(adjacency[v]):
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        components.append(tuple(sorted(component)))
    components = tuple(sorted(components, key=lambda c: (len(c), c)))

    return {
        "colors": colors,
        "color_classes": color_classes,
        "refinement_history": refinement_history,
        "pair_relation_class_count": len(relations),
        "matching_relation_class_count": len(matching_keys),
        "matching_relation_classes": matching_keys,
        "components": components,
    }


def exact_candidate(cnf: base.CNF, raw_blocks: tuple[tuple[int, ...], ...], state: base.EngineState):
    width = len(raw_blocks[0])
    if width > MAX_COMPONENT_WIDTH:
        raise AssertionError("COMPONENT_WIDTH_EXCEEDS_FROZEN_FINITE_GRAMMAR")

    oriented_blocks = []
    signatures = []
    alphabets = []
    for raw_block in raw_blocks:
        clauses = auto.local_clauses(cnf, raw_block)
        signature, oriented = auto.oriented_signature(clauses, raw_block)
        alphabet = auto.local_state_alphabet(oriented, auto.local_clauses(cnf, oriented))
        signatures.append(signature)
        alphabets.append(alphabet)
        oriented_blocks.append(oriented)

    if len(set(signatures)) != 1:
        raise AssertionError("REPEATED_COMPONENT_LOCAL_SIGNATURE_MISMATCH")
    if len(set(alphabets)) != 1:
        raise AssertionError("REPEATED_COMPONENT_LOCAL_ALPHABET_MISMATCH")
    alphabet = alphabets[0]
    if not (1 < len(alphabet) < (1 << width)):
        raise AssertionError("LOCAL_ALPHABET_NOT_NONTRIVIAL")

    blocks = tuple(sorted(oriented_blocks, key=lambda b: tuple(sorted(b))))
    covered = {v for block in blocks for v in block}
    core = tuple(sorted(set(base.vars_of(cnf)) - covered))

    old_width = auto.BLOCK_WIDTH
    auto.BLOCK_WIDTH = width
    try:
        generators = auto.certify_adjacent_block_swaps(cnf, blocks)
    finally:
        auto.BLOCK_WIDTH = old_width

    templates, arities, replay_rows = auto.compile_templates(cnf, blocks, core)
    max_arity = max(arities.values(), default=0)
    q = len(alphabet)
    histogram_count = comb(len(blocks) + q - 1, q - 1)

    flat_core_state_count = 1 << len(core)
    flat_quotient_count = histogram_count * flat_core_state_count

    # Exact second-layer compression: keep only core assignments satisfying all
    # clauses wholly internal to the discovered core. This never drops a global
    # model, because every global model must satisfy this clause subset.
    core_clauses = auto.local_clauses(cnf, core)
    core_states = auto.local_state_alphabet(core, core_clauses)
    if not core_states:
        raise AssertionError("CORE_LOCAL_CLAUSES_ALREADY_UNSAT")
    core_state_count = len(core_states)
    nested_quotient_count = histogram_count * core_state_count
    if nested_quotient_count > MAX_EXACT_NESTED_QUOTIENT_STATES:
        raise AssertionError(
            f"NESTED_QUOTIENT_EXCEEDS_FROZEN_FINITE_REPLAY_LIMIT={nested_quotient_count}"
        )

    survivors = []
    direct_checks = 0
    for core_bits in core_states:
        for hist in auto.compositions(len(blocks), q):
            holds = True
            for template in templates:
                direct_checks += 1
                if not auto.template_holds_direct(template, hist, core_bits, alphabet):
                    holds = False
                    break
            if holds:
                survivors.append({"core_state": list(core_bits), "hist": list(hist)})
                if len(survivors) >= 4:
                    break
        if len(survivors) >= 4:
            break

    minimum_cap_exponent = next(
        (c for c in range(1, 7) if nested_quotient_count <= state.N ** c),
        None,
    )
    return {
        "width": width,
        "block_count": len(blocks),
        "blocks": [list(b) for b in blocks],
        "core_variables": list(core),
        "core_variable_count": len(core),
        "q": q,
        "local_alphabet": [list(x) for x in alphabet],
        "adjacent_generator_count": len(generators),
        "all_adjacent_generators_preserve_residual": all(x["preserves_residual"] for x in generators),
        "template_count": len(templates),
        "max_block_arity": max_arity,
        "exact_template_replay": True,
        "template_replay_rows": replay_rows,
        "histogram_count": histogram_count,
        "flat_core_state_count": flat_core_state_count,
        "flat_quotient_state_count": flat_quotient_count,
        "core_local_clause_count": len(core_clauses),
        "core_local_state_units": base.state_units(core_clauses),
        "core_local_alphabet_count": core_state_count,
        "core_local_alphabet": [list(x) for x in core_states],
        "nested_quotient_state_count": nested_quotient_count,
        "raw_assignment_space": 1 << len(base.vars_of(cnf)),
        "local_valid_assignment_space_before_core_quotient": (q ** len(blocks)) * flat_core_state_count,
        "direct_decision_checks": direct_checks,
        "survivor_count": len(survivors),
        "survivor_examples": survivors,
        "status": "UNSAT" if not survivors else "OPEN",
        "minimum_observed_cap_exponent": minimum_cap_exponent,
        "under_old_C1_state_cap": nested_quotient_count <= state.state_cap,
        "resource_key": [
            minimum_cap_exponent if minimum_cap_exponent is not None else 7,
            nested_quotient_count,
            len(templates),
            max_arity,
            len(core),
            width,
        ],
    }


def synthesize(state: base.EngineState):
    cnf = state.residual
    relation = matching_relation_components(cnf)
    by_size = defaultdict(list)
    for component in relation["components"]:
        by_size[len(component)].append(component)

    candidates = []
    failures = []
    for width in sorted(by_size):
        components = tuple(by_size[width])
        if len(components) < 2:
            continue
        try:
            candidates.append(exact_candidate(cnf, components, state))
        except AssertionError as exc:
            failures.append({
                "component_width": width,
                "component_count": len(components),
                "reason": str(exc),
            })

    admitted = [c for c in candidates if c["status"] == "UNSAT"]
    admitted.sort(key=lambda c: tuple(c["resource_key"]))
    winner = None
    ambiguity = False
    if admitted:
        best_key = tuple(admitted[0]["resource_key"])
        best = [c for c in admitted if tuple(c["resource_key"]) == best_key]
        if len(best) == 1:
            winner = best[0]
        else:
            ambiguity = True

    return {
        "pair_relation_class_count": relation["pair_relation_class_count"],
        "matching_relation_class_count": relation["matching_relation_class_count"],
        "component_size_histogram": dict(sorted(Counter(map(len, relation["components"])).items())),
        "components": [list(c) for c in relation["components"]],
        "candidate_count": len(candidates),
        "candidate_failures": failures,
        "admitted_count": len(admitted),
        "resource_tie_ambiguity": ambiguity,
        "winner": winner,
        "candidates": candidates,
    }


def probe(pigeons: int, holes: int):
    result, state = capture_case(pigeons, holes)
    return {
        "case": f"PHP_{pigeons}_{holes}_C1",
        "N": state.N,
        "old_state_cap": state.state_cap,
        "engine_status": result["status"],
        "engine_reason": result["reason"],
        "residual_fingerprint": base.fingerprint(state.residual),
        "residual_units": base.state_units(state.residual),
        "live_variables": len(base.vars_of(state.residual)),
        "live_root_variables": sorted(set(base.vars_of(state.residual)).intersection(state.root_vars)),
        "manual_block_ids": False,
        "manual_center_id": False,
        "manual_block_width": False,
        "pair_relation_fiber_synthesis": synthesize(state),
        "P_VS_NP": "OPEN",
    }


def regression_gate(rows: list[dict]):
    by_case = {r["case"]: r for r in rows}
    expected = {
        "PHP_5_4_C1": {
            "fingerprint": "990124522dc5ee1a6871de798a0f3ef40f05c20a28cd9f3d9d2f062841695ea6",
            "width": 3, "block_count": 4, "q": 4,
            "core": 1, "core_q": 2, "nested_quotient": 70, "min_cap_exp": 1,
        },
        "PHP_6_5_C1": {
            "fingerprint": "7110fc5dfba96dfd9517b9f354739b09180e3452d694b85312682d13bd2a6008",
            "width": 4, "block_count": 6, "q": 5,
            "core": 0, "core_q": 1, "nested_quotient": 210, "min_cap_exp": 1,
        },
        "PHP_7_6_C1": {
            "fingerprint": "440b51533ee1bce92a30a076c31d5a9cfbba2713fc2547968b9662b3f980845e",
            "width": 5, "block_count": 5, "q": 6,
            "core": 10, "core_q": 30, "nested_quotient": 7560, "min_cap_exp": 2,
        },
    }
    checks = []
    for case, exp in expected.items():
        row = by_case.get(case)
        if row is None:
            continue
        winner = row["pair_relation_fiber_synthesis"]["winner"]
        ok = (
            row["residual_fingerprint"] == exp["fingerprint"]
            and winner is not None
            and winner["width"] == exp["width"]
            and winner["block_count"] == exp["block_count"]
            and winner["q"] == exp["q"]
            and winner["core_variable_count"] == exp["core"]
            and winner["core_local_alphabet_count"] == exp["core_q"]
            and winner["nested_quotient_state_count"] == exp["nested_quotient"]
            and winner["minimum_observed_cap_exponent"] == exp["min_cap_exp"]
            and winner["survivor_count"] == 0
        )
        checks.append({"case": case, "pass": ok})
        if not ok:
            raise AssertionError(f"PAIR_RELATION_NESTED_REGRESSION_FAILED_{case}")
    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="5:4,6:5,7:6")
    args = ap.parse_args()
    requested = []
    for token in args.cases.split(","):
        p, h = (int(x) for x in token.split(":"))
        if p != h + 1:
            raise SystemExit("Only PHP_(m+1)_m is admitted in this finite regression probe")
        requested.append((p, h))

    rows = [probe(p, h) for p, h in requested]
    checks = regression_gate(rows)
    report = {
        "schema": "JANUS/C025/REVERSE-B-TO-A-PAIR-RELATION-NESTED-FIBER-SYNTHESIZER/v2",
        "direction": "B_TO_A",
        "target": "DERIVE_W_K_Q_CORE_ALPHABET_AND_TEMPLATE_PROGRAM_WITHOUT_BLOCK_WIDTH_INPUT",
        "regression_gate": checks,
        "cases": rows,
        "discovery_grammar": {
            "manual_block_ids": False,
            "manual_center_id": False,
            "manual_block_width": False,
            "signed_unary_colors_are_candidate_invariants_only": True,
            "endpoint_order_invariant_pair_relations": True,
            "all_nonempty_degree_le_one_relation_classes_are_unioned": True,
            "component_partition_is_deterministic": True,
            "full_residual_Sk_is_required": True,
            "exact_template_replay_is_required": True,
            "core_local_alphabet_is_exact": True,
            "zero_nested_quotient_survivors_are_required": True,
            "heuristic_score_promotion": False,
            "randomness": False,
            "SAT_oracle": False,
            "semantic_equivalence_oracle": False,
        },
        "complexity_debts": {
            "pair_relation_discovery_polynomial_in_explicit_residual_size": True,
            "component_discovery_polynomial": True,
            "internal_orientation_currently_enumerates_w_factorial": True,
            "local_block_alphabet_currently_enumerates_2_pow_w": True,
            "core_local_alphabet_currently_enumerates_2_pow_core": True,
            "histogram_count_may_be_superpolynomial_if_q_grows": True,
            "PHP_7_6_nested_quotient_under_C1": False,
            "PHP_7_6_nested_quotient_under_C2_finite_observation": True,
            "general_polynomial_bound": "OPEN",
        },
        "scientific_boundary": {
            "finite_exact_witness_count_if_all_regressions_pass": 3,
            "PHP_family_law": "OPEN",
            "predictive_holdout_PHP_8_7": "NOT_RUN",
            "reason_holdout_not_run": "NO_NON_OVERFIT_PARAMETRIC_LAW_FOR_K_CORE_AND_TEMPLATE_PROGRAM_YET",
            "arbitrary_CNF_coverage": "OPEN",
            "universal_polynomial_algorithm": "OPEN",
            "P_VS_NP": "OPEN",
        },
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
