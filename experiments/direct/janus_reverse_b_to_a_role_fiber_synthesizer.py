#!/usr/bin/env python3
"""C025 reverse B->A role/fiber synthesizer.

Purpose
-------
Infer the coordinate width itself from a frozen CNF residual rather than
supplying block ids, a center id, or a block width.

Discovery grammar (deterministic; no score promotion):
  raw signed CNF incidence
    -> exact color refinement of variable roles
    -> equal-cardinality repeated role classes
    -> exact pair-relation alignment into candidate blocks
    -> full-residual adjacent block-swap certificate (generates S_k)
    -> exact local alphabet
    -> exact orbit-template replay
    -> exact histogram quotient
    -> zero-survivor UNSAT certificate.

Color refinement and pair signatures are candidate generators only.  They do
not prove semantic equivalence.  A candidate is admitted only after exact full
CNF replay and exact symmetry checks.  Ambiguity fails closed except when one
candidate has a strictly smaller exact resource ledger key.

This remains finite PHP-family research.  P_VS_NP=OPEN.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from itertools import product
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

MAX_COLOR_ROUNDS = 128
MAX_ROLE_WIDTH = 12
MAX_EXACT_QUOTIENT_STATES = 200_000
MAX_CAP_EXPONENT_SCAN = 6


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


def signed_incident_descriptor(cnf: base.CNF, var: int, colors: dict[int, int]):
    rows = []
    for clause in cnf:
        lit = next((x for x in clause if abs(x) == var), None)
        if lit is None:
            continue
        others = tuple(sorted(
            (colors[abs(x)], int(x > 0))
            for x in clause if abs(x) != var
        ))
        rows.append((len(clause), int(lit > 0), others))
    return tuple(sorted(rows))


def exact_role_refinement(cnf: base.CNF):
    """Deterministic 1-WL-style refinement on signed clause incidence.

    This is only a discovery invariant: equal colors are never treated as an
    automorphism proof.  The later adjacent-swap replay is the proof gate.
    """
    vars_ = base.vars_of(cnf)
    colors = {v: 0 for v in vars_}
    history = []
    for round_index in range(MAX_COLOR_ROUNDS):
        descriptors = {
            v: (colors[v], signed_incident_descriptor(cnf, v, colors))
            for v in vars_
        }
        unique = sorted(set(descriptors.values()), key=repr)
        code = {d: i for i, d in enumerate(unique)}
        new_colors = {v: code[descriptors[v]] for v in vars_}
        class_sizes = Counter(new_colors.values())
        history.append({
            "round": round_index + 1,
            "color_count": len(class_sizes),
            "class_size_histogram": dict(sorted(Counter(class_sizes.values()).items())),
        })
        if all(new_colors[v] == colors[v] for v in vars_):
            colors = new_colors
            break
        # Compare partitions rather than numeric labels, because canonical color
        # ids can be renumbered between rounds.
        old_partition = {
            v: frozenset(u for u in vars_ if colors[u] == colors[v]) for v in vars_
        }
        new_partition = {
            v: frozenset(u for u in vars_ if new_colors[u] == new_colors[v]) for v in vars_
        }
        colors = new_colors
        if all(old_partition[v] == new_partition[v] for v in vars_):
            break
    else:
        raise AssertionError("ROLE_REFINEMENT_DID_NOT_STABILIZE")

    classes = defaultdict(list)
    for v, c in colors.items():
        classes[c].append(v)
    classes = {c: tuple(sorted(vs)) for c, vs in classes.items()}
    return colors, classes, history


def pair_relation_signature(cnf: base.CNF, a: int, b: int, colors: dict[int, int]):
    rows = []
    for clause in cnf:
        la = next((x for x in clause if abs(x) == a), None)
        if la is None:
            continue
        lb = next((x for x in clause if abs(x) == b), None)
        if lb is None:
            continue
        others = tuple(sorted(
            (colors[abs(x)], int(x > 0))
            for x in clause if abs(x) not in (a, b)
        ))
        rows.append((len(clause), int(la > 0), int(lb > 0), others))
    return tuple(sorted(rows))


def unique_bijection_by_pair_signature(
    cnf: base.CNF,
    anchor: tuple[int, ...],
    role: tuple[int, ...],
    colors: dict[int, int],
):
    if len(anchor) != len(role):
        raise AssertionError("ROLE_CARDINALITY_MISMATCH")

    pair_sig = {
        (a, b): pair_relation_signature(cnf, a, b, colors)
        for a in anchor for b in role
    }
    candidate_signatures = sorted(set(pair_sig.values()), key=repr)
    bijections = []
    for sig in candidate_signatures:
        mapping = {}
        used = set()
        ok = True
        for a in anchor:
            hits = [b for b in role if pair_sig[(a, b)] == sig]
            if len(hits) != 1 or hits[0] in used:
                ok = False
                break
            mapping[a] = hits[0]
            used.add(hits[0])
        if ok and len(used) == len(role):
            bijections.append((sig, mapping))

    if len(bijections) != 1:
        raise AssertionError(f"PAIR_RELATION_ALIGNMENT_AMBIGUOUS_OR_ABSENT={len(bijections)}")
    return bijections[0]


def relative_local_signature(cnf: base.CNF, block: tuple[int, ...]):
    pos = {v: i for i, v in enumerate(block)}
    rows = []
    for clause in cnf:
        if not clause or not all(abs(lit) in pos for lit in clause):
            continue
        rows.append(tuple(sorted((pos[abs(lit)], int(lit > 0)) for lit in clause)))
    return tuple(sorted(rows))


def build_role_candidate(
    cnf: base.CNF,
    colors: dict[int, int],
    classes: dict[int, tuple[int, ...]],
    block_count: int,
):
    roles = [classes[c] for c in sorted(classes) if len(classes[c]) == block_count]
    if len(roles) < 2:
        raise AssertionError("INSUFFICIENT_EQUAL_CARDINALITY_ROLE_CLASSES")
    if len(roles) > MAX_ROLE_WIDTH:
        raise AssertionError("ROLE_WIDTH_EXCEEDS_FROZEN_FINITE_GRAMMAR")

    anchor = roles[0]
    aligned = [anchor]
    alignment_cert = []
    for role in roles[1:]:
        sig, mapping = unique_bijection_by_pair_signature(cnf, anchor, role, colors)
        aligned.append(tuple(mapping[a] for a in anchor))
        alignment_cert.append({
            "role_color": colors[role[0]],
            "pair_signature": repr(sig),
        })

    blocks = tuple(tuple(aligned[r][i] for r in range(len(aligned))) for i in range(block_count))
    covered = {v for block in blocks for v in block}
    outside = tuple(sorted(set(base.vars_of(cnf)) - covered))
    width = len(roles)

    local_signatures = [relative_local_signature(cnf, block) for block in blocks]
    if len(set(local_signatures)) != 1:
        raise AssertionError("BLOCK_LOCAL_SIGNATURES_NOT_IDENTICAL")

    local_clauses = [auto.local_clauses(cnf, block) for block in blocks]
    alphabets = [auto.local_state_alphabet(block, clauses) for block, clauses in zip(blocks, local_clauses)]
    if len(set(alphabets)) != 1:
        raise AssertionError("BLOCK_LOCAL_ALPHABETS_NOT_IDENTICAL")
    alphabet = alphabets[0]
    if not (1 < len(alphabet) < (1 << width)):
        raise AssertionError("LOCAL_ALPHABET_NOT_NONTRIVIAL")

    old_width = auto.BLOCK_WIDTH
    auto.BLOCK_WIDTH = width
    try:
        swap_rows = auto.certify_adjacent_block_swaps(cnf, blocks)
    finally:
        auto.BLOCK_WIDTH = old_width

    templates, arities, replay_rows = auto.compile_templates(cnf, blocks, outside)
    max_arity = max(arities.values(), default=0)

    q = len(alphabet)
    histogram_count = comb(block_count + q - 1, q - 1)
    outside_state_count = 1 << len(outside)
    quotient_count = histogram_count * outside_state_count
    if quotient_count > MAX_EXACT_QUOTIENT_STATES:
        raise AssertionError(f"QUOTIENT_EXCEEDS_FINITE_REPLAY_LIMIT={quotient_count}")

    survivors = []
    direct_checks = 0
    for outside_bits in product((0, 1), repeat=len(outside)):
        for hist in auto.compositions(block_count, q):
            ok = True
            for template in templates:
                direct_checks += 1
                if not auto.template_holds_direct(template, hist, outside_bits, alphabet):
                    ok = False
                    break
            if ok:
                survivors.append({"outside": list(outside_bits), "hist": list(hist)})
                if len(survivors) >= 4:
                    break
        if len(survivors) >= 4:
            break

    raw_space = 1 << len(base.vars_of(cnf))
    local_valid_space = (q ** block_count) * outside_state_count
    min_cap_exp = None
    for c in range(1, MAX_CAP_EXPONENT_SCAN + 1):
        # The caller substitutes the actual input-size N into the resource key.
        # Here we leave the exponent unresolved until the candidate is attached
        # to an engine state.
        pass

    return {
        "block_count": block_count,
        "width": width,
        "roles": [list(r) for r in roles],
        "blocks": [list(b) for b in blocks],
        "outside_variables": list(outside),
        "q": q,
        "local_alphabet": [list(x) for x in alphabet],
        "local_signature": [[list(x) for x in clause] for clause in local_signatures[0]],
        "alignment_certificate": alignment_cert,
        "adjacent_generators": swap_rows,
        "all_adjacent_generators_preserve_residual": all(r["preserves_residual"] for r in swap_rows),
        "template_count": len(templates),
        "max_block_arity": max_arity,
        "template_replay_rows": replay_rows,
        "exact_full_residual_replay": True,
        "histogram_count": histogram_count,
        "outside_state_count": outside_state_count,
        "quotient_state_count": quotient_count,
        "raw_assignment_space": raw_space,
        "local_valid_assignment_space": local_valid_space,
        "survivor_count": len(survivors),
        "survivor_examples": survivors,
        "direct_decision_checks": direct_checks,
        "status": "UNSAT" if not survivors else "OPEN",
    }


def synthesize_residual(state: base.EngineState):
    cnf = state.residual
    colors, classes, refinement_history = exact_role_refinement(cnf)
    size_hist = Counter(len(vs) for vs in classes.values())

    candidates = []
    failures = []
    for block_count in sorted(k for k in size_hist if k >= 2):
        try:
            c = build_role_candidate(cnf, colors, classes, block_count)
            min_exp = next(
                (e for e in range(1, MAX_CAP_EXPONENT_SCAN + 1)
                 if c["quotient_state_count"] <= state.N ** e),
                None,
            )
            c["minimum_observed_cap_exponent"] = min_exp
            c["under_old_C1_state_cap"] = c["quotient_state_count"] <= state.state_cap
            c["resource_key"] = [
                min_exp if min_exp is not None else MAX_CAP_EXPONENT_SCAN + 1,
                c["quotient_state_count"],
                c["template_count"],
                c["max_block_arity"],
                len(c["outside_variables"]),
                c["width"],
            ]
            candidates.append(c)
        except AssertionError as exc:
            failures.append({"block_count": block_count, "reason": str(exc)})

    admitted = [
        c for c in candidates
        if c["status"] == "UNSAT"
        and c["exact_full_residual_replay"]
        and c["all_adjacent_generators_preserve_residual"]
    ]
    winner = None
    ambiguity = False
    if admitted:
        admitted.sort(key=lambda c: tuple(c["resource_key"]))
        best_key = tuple(admitted[0]["resource_key"])
        best = [c for c in admitted if tuple(c["resource_key"]) == best_key]
        if len(best) == 1:
            winner = best[0]
        else:
            ambiguity = True

    return {
        "refinement_history": refinement_history,
        "role_class_count": len(classes),
        "role_classes": {str(c): list(vs) for c, vs in sorted(classes.items())},
        "role_class_size_histogram": dict(sorted(size_hist.items())),
        "candidate_failures": failures,
        "candidate_count": len(candidates),
        "admitted_count": len(admitted),
        "resource_tie_ambiguity": ambiguity,
        "winner": winner,
        "candidates": candidates,
    }


def probe_case(pigeons: int, holes: int):
    result, state = capture_case(pigeons, holes)
    synthesis = synthesize_residual(state)
    live_roots = sorted(set(base.vars_of(state.residual)).intersection(state.root_vars))
    return {
        "case": f"PHP_{pigeons}_{holes}_C1",
        "pigeons": pigeons,
        "holes": holes,
        "N": state.N,
        "old_state_cap": state.state_cap,
        "engine_status": result["status"],
        "engine_reason": result["reason"],
        "residual_fingerprint": base.fingerprint(state.residual),
        "residual_units": base.state_units(state.residual),
        "live_variables": len(base.vars_of(state.residual)),
        "live_root_variables": live_roots,
        "manual_block_ids": False,
        "manual_center_id": False,
        "manual_block_width": False,
        "role_fiber_synthesis": synthesis,
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="5:4,6:5,7:6")
    args = ap.parse_args()
    cases = []
    for token in args.cases.split(","):
        p, h = (int(x) for x in token.split(":"))
        if p != h + 1:
            raise SystemExit("Only PHP_(m+1)_m is admitted in this finite probe")
        cases.append((p, h))

    rows = [probe_case(p, h) for p, h in cases]
    report = {
        "schema": "JANUS/C025/REVERSE-B-TO-A-ROLE-FIBER-SYNTHESIZER/v1",
        "direction": "B_TO_A",
        "target": "INFER_W_K_Q_AND_TEMPLATE_PROGRAM_FROM_EXACT_B_INVARIANTS_WITHOUT_BLOCK_WIDTH_INPUT",
        "cases": rows,
        "discovery_grammar": {
            "signed_incidence_color_refinement": True,
            "equal_cardinality_role_classes": True,
            "unique_pair_relation_alignment_or_fail_closed": True,
            "full_residual_adjacent_swap_certificate": True,
            "exact_template_replay": True,
            "exact_histogram_quotient": True,
            "heuristic_score_promotion": False,
            "randomness": False,
            "sat_oracle": False,
            "semantic_equivalence_oracle": False,
        },
        "complexity_debts": {
            "color_refinement_is_polynomial": True,
            "pair_relation_alignment_is_polynomial": True,
            "local_alphabet_currently_enumerates_2_pow_w": True,
            "histogram_state_count_may_be_superpolynomial_if_q_grows": True,
            "general_polynomial_bound": "OPEN",
        },
        "scientific_boundary": {
            "finite_php_family_probe": True,
            "family_law": "OPEN_UNTIL_PREDICTIVE_HOLDOUT",
            "arbitrary_CNF_coverage": "OPEN",
            "universal_polynomial_algorithm": "OPEN",
            "P_VS_NP": "OPEN",
        },
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
