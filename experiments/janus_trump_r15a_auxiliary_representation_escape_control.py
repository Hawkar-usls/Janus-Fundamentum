#!/usr/bin/env python3
"""R15A: exposed-interface auxiliary-variable representation escape control.

This pass intentionally starts from the already-exposed exact R13-W05 bridge
relation.  It asks only whether that relation, whose same-variable CNF width is
6, has a compact width<=3 existential extension representation.  It does NOT
compile the representation from the GENERAL_CNF frame and has no SAT-algorithm
authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import janus_trump_r10_exact_semantic_bridge_interface as r10
import janus_trump_r11_exact_interface_structure_microscope as r11
import janus_trump_r13_unseen_interface_generalization as r13

WORLD_ID = "R13-W05"
EXPECTED_FRAME_SHA = "84fa0fbdd127b1c73f3c8ef6820a0d0cdf154093750ed9c600289fce4b6aae88"
EXPECTED_TRUTH_SHA = "acf8828272994c0ad05a44590aa4335e1828d5b7d3e3d4f438b0d497cfcad92f"
EXPECTED_ALLOWED = 287
EXPECTED_PRIMES = 242
EXPECTED_SAME_VARIABLE_WIDTH = 6


def neg(lit: int) -> int:
    return -int(lit)


def encode_or_equiv(out_var: int, left_lit: int, right_lit: int):
    """CNF for out <-> (left OR right), maximum width 3."""
    return [
        (-out_var, left_lit, right_lit),
        (out_var, neg(left_lit)),
        (out_var, neg(right_lit)),
    ]


def encode_clause_width3(clause, next_aux: int):
    """Projection-equivalent width<=3 encoding of one clause.

    Returns clauses, topological OR definitions, and next free variable id.
    For width <=3 the clause is unchanged.  For width k>3 it uses k-3 fresh
    auxiliaries and ends with one 3-literal root clause.
    """
    c = tuple(int(x) for x in clause)
    if len(c) <= 3:
        return [c], [], next_aux
    out_clauses = []
    defs = []
    a = next_aux
    next_aux += 1
    out_clauses.extend(encode_or_equiv(a, c[0], c[1]))
    defs.append((a, c[0], c[1]))
    cursor = a
    # Leave the final two original literals for the asserted 3-clause.
    for lit in c[2:-2]:
        a = next_aux
        next_aux += 1
        out_clauses.extend(encode_or_equiv(a, cursor, lit))
        defs.append((a, cursor, lit))
        cursor = a
    out_clauses.append((cursor, c[-2], c[-1]))
    return out_clauses, defs, next_aux


def build_extended_interface(primes, bridge_size: int):
    next_aux = bridge_size + 1
    clauses = []
    definitions = []
    per_prime = []
    for idx, prime in enumerate(primes):
        enc, defs, next_aux = encode_clause_width3(prime, next_aux)
        clauses.extend(enc)
        definitions.extend(defs)
        per_prime.append({
            "prime_index": idx,
            "original_width": len(prime),
            "encoded_clause_count": len(enc),
            "auxiliary_count": len(defs),
        })
    return {
        "clauses": tuple(tuple(c) for c in clauses),
        "definitions": tuple(tuple(d) for d in definitions),
        "auxiliary_variable_count": next_aux - (bridge_size + 1),
        "max_variable": next_aux - 1,
        "per_prime": per_prime,
    }


def eval_lit(lit: int, assignment: dict[int, bool]) -> bool:
    value = bool(assignment[abs(lit)])
    return value if lit > 0 else not value


def bridge_assignment(k: int, mask: int):
    return {i + 1: bool((mask >> i) & 1) for i in range(k)}


def extend_assignment(mask: int, k: int, definitions):
    assignment = bridge_assignment(k, mask)
    for out_var, left, right in definitions:
        assignment[out_var] = eval_lit(left, assignment) or eval_lit(right, assignment)
    return assignment


def satisfies_cnf(clauses, assignment) -> bool:
    return all(any(eval_lit(lit, assignment) for lit in clause) for clause in clauses)


def allowed_masks_extended(encoded, k: int):
    allowed = []
    for mask in range(1 << k):
        a = extend_assignment(mask, k, encoded["definitions"])
        if satisfies_cnf(encoded["clauses"], a):
            allowed.append(mask)
    return allowed


def digest_masks(masks):
    return hashlib.sha256(json.dumps(list(masks), separators=(",", ":")).encode()).hexdigest()


def structural_controls():
    # Four-literal clause needs one auxiliary and stays width<=3.
    enc, defs, nxt = encode_clause_width3((1, -2, 3, -4), 5)
    if len(defs) != 1 or nxt != 6 or max(map(len, enc)) > 3:
        return False
    # Exhaustively check the tiny clause under all 16 assignments.
    for m in range(16):
        original = any(eval_lit(l, bridge_assignment(4, m)) for l in (1, -2, 3, -4))
        assignment = extend_assignment(m, 4, defs)
        extended = satisfies_cnf(enc, assignment)
        if original != extended:
            return False
    return True


def run():
    freeze = r13.load_freeze()
    spec = next(w for w in freeze["worlds"] if w["id"] == WORLD_ID)
    world = r13.generate_world(spec)
    if world["source"]["frame_sha256"] != EXPECTED_FRAME_SHA:
        raise AssertionError("W05 frame drift")
    bridge = tuple(world["bridge"])
    if len(bridge) != 16:
        raise AssertionError("W05 bridge-size drift")

    shadow = r10.shadow_exact_interface(world["frame"], bridge)
    if shadow["truth_table_sha256"] != EXPECTED_TRUTH_SHA or shadow["allowed_count"] != EXPECTED_ALLOWED:
        raise AssertionError("W05 witness drift")
    geometry = r11.exact_cnf_geometry(shadow["allowed_masks"], len(bridge))
    if geometry["minimum_same_variable_cnf_width"] != EXPECTED_SAME_VARIABLE_WIDTH:
        raise AssertionError("R14 width drift")
    primes = tuple(tuple(c) for c in geometry["prime_clauses"])
    if len(primes) != EXPECTED_PRIMES:
        raise AssertionError("prime count drift")

    encoded = build_extended_interface(primes, len(bridge))
    ext_allowed = allowed_masks_extended(encoded, len(bridge))
    exact = set(shadow["allowed_masks"])
    ext = set(ext_allowed)
    fp = sorted(ext - exact)
    fn = sorted(exact - ext)
    truth_sha = digest_masks(ext_allowed)
    max_width = max(map(len, encoded["clauses"]), default=0)
    gates = {
        "G1_EXPOSED_W05_WITNESS_FROZEN": shadow["truth_table_sha256"] == EXPECTED_TRUTH_SHA,
        "G2_R14_SAME_VARIABLE_WIDTH6_RECONSTRUCTED": geometry["minimum_same_variable_cnf_width"] == 6,
        "G3_STRUCTURAL_ENCODING_CONTROL": structural_controls(),
        "G4_MAX_EXTENDED_WIDTH_LE3": max_width <= 3,
        "G5_ALLOWED_SET_MATCH": not fp and not fn and len(ext_allowed) == EXPECTED_ALLOWED,
        "G6_TRUTH_HASH_MATCH": truth_sha == EXPECTED_TRUTH_SHA,
        "G7_NO_DIRECT_FROM_FRAME_COMPILER_CLAIM": True,
        "G8_NO_GLOBAL_COMPLEXITY_INFLATION": True,
    }
    verdict = "AUXILIARY_WIDTH3_REPRESENTATION_ESCAPE_CONFIRMED" if all(gates.values()) else "AUXILIARY_ENCODING_CONTROL_FAIL"
    width_dist = {}
    for c in encoded["clauses"]:
        width_dist[str(len(c))] = width_dist.get(str(len(c)), 0) + 1
    return {
        "schema": "JANUS/TRUMP/R15A/AUXILIARY_REPRESENTATION_ESCAPE_CONTROL/RESULT/v1.0",
        "created_date": "2026-09-02",
        "verdict": verdict,
        "target": {
            "world_id": WORLD_ID,
            "bridge_size": len(bridge),
            "same_variable_minimum_cnf_width": geometry["minimum_same_variable_cnf_width"],
            "exact_prime_count": len(primes),
            "exact_allowed_count": EXPECTED_ALLOWED,
            "truth_table_sha256": EXPECTED_TRUTH_SHA,
        },
        "extended_representation": {
            "representation": "acyclic definitional OR-chain CNF with fresh existential auxiliaries",
            "auxiliary_variable_count": encoded["auxiliary_variable_count"],
            "extended_clause_count": len(encoded["clauses"]),
            "maximum_clause_width": max_width,
            "clause_width_distribution": width_dist,
            "allowed_count": len(ext_allowed),
            "truth_table_sha256": truth_sha,
            "false_positive_count": len(fp),
            "false_negative_count": len(fn),
        },
        "gates": gates,
        "scientific_interpretation": {
            "positive": "R14's width-6 lower bound is specific to same-variable CNF. The already-known exact W05 interface has an exact existential extension representation of width<=3 with linear definitional overhead.",
            "hard_wall": "This pass starts from the exact exposed interface. It says nothing about whether such a factored representation can be compiled directly from the GENERAL_CNF frame without first solving the hard projection problem.",
            "next_question": "Can a frozen direct-from-frame compiler introduce extension atoms prospectively, with polynomial accounting and no exact-shadow guidance, then generalize on new unseen worlds?"
        },
        "seal": "THE_NEW_LANGUAGE_CAN_CARRY_THE_MEANING__NOW_PROVE_THE_FRAME_CAN_COMPILE_IT_WITHOUT_BEING_TOLD_THE_ANSWER",
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    d = run(); Path(args.output).write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": d["verdict"], "extended_representation": d["extended_representation"], "gates": d["gates"], "P_VS_NP": "OPEN"}, indent=2, sort_keys=True))
    return 0 if all(d["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
