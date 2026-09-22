#!/usr/bin/env python3
"""Exact fixed-library killer test for R5 E8 6I induced-algebra admission.

This checker is intentionally finite and exhaustive. It does not solve SAT.
It freezes the Boolean ternary algebra library
    B4 = {AND3, OR3, MAJ3, XOR3}
and computes the induced algebra-label relations for all eight signed 3-clause
relations. It then proves two fixed facts by exhaustive enumeration:

1. The conjunction (x∨y∨z) ∧ (¬x∨¬y∨¬z) admits no single variable-wise
   B4 label assignment preserving both relations.
2. There is no homomorphism Gamma_3SAT -> Gamma_3SAT^B4.

These facts falsify only the B4 induced-algebra shortcut. They do not rule out
larger/lifted algebra families and do not resolve P vs NP.
"""
from __future__ import annotations

import itertools
import json

LABELS = ("AND3", "OR3", "MAJ3", "XOR3")


def op(label: str, a: int, b: int, c: int) -> int:
    if label == "AND3":
        return a & b & c
    if label == "OR3":
        return a | b | c
    if label == "MAJ3":
        return int(a + b + c >= 2)
    if label == "XOR3":
        return a ^ b ^ c
    raise KeyError(label)


def clause_relation(signs: tuple[int, int, int]) -> tuple[tuple[int, int, int], ...]:
    rows = []
    for row in itertools.product((0, 1), repeat=3):
        literals = [row[i] if signs[i] == 1 else 1 - row[i] for i in range(3)]
        if any(literals):
            rows.append(row)
    assert len(rows) == 7
    return tuple(rows)


def preserves(
    relation: tuple[tuple[int, int, int], ...],
    labels: tuple[str, str, str],
) -> bool:
    allowed = set(relation)
    for r0, r1, r2 in itertools.product(relation, repeat=3):
        out = tuple(op(labels[j], r0[j], r1[j], r2[j]) for j in range(3))
        if out not in allowed:
            return False
    return True


def induced_relation(signs: tuple[int, int, int]) -> tuple[tuple[str, str, str], ...]:
    rel = clause_relation(signs)
    out = [
        labels
        for labels in itertools.product(LABELS, repeat=3)
        if preserves(rel, labels)
    ]
    return tuple(sorted(out))


def gamma_to_induced_homomorphisms(
    induced: dict[tuple[int, int, int], tuple[tuple[str, str, str], ...]]
) -> list[tuple[str, str]]:
    homs = []
    for zero_label, one_label in itertools.product(LABELS, repeat=2):
        image = {0: zero_label, 1: one_label}
        ok = True
        for signs, label_relation in induced.items():
            allowed = set(label_relation)
            for row in clause_relation(signs):
                if tuple(image[x] for x in row) not in allowed:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            homs.append((zero_label, one_label))
    return homs


def build_receipt() -> dict:
    sign_patterns = tuple(itertools.product((1, -1), repeat=3))
    induced = {s: induced_relation(s) for s in sign_patterns}

    positive = (1, 1, 1)
    negative = (-1, -1, -1)
    pos_set = set(induced[positive])
    neg_set = set(induced[negative])
    intersection = sorted(pos_set & neg_set)
    homs = gamma_to_induced_homomorphisms(induced)

    # Exact frozen assertions.
    assert len(pos_set) == 13
    assert len(neg_set) == 13
    assert intersection == []
    assert homs == []
    assert all(len(induced[s]) == 13 for s in sign_patterns)

    return {
        "schema": "janus.r5_e8_6i.induced_algebra_b4_killer_test.v1",
        "status": "PASS_EXACT_B4_FALSIFIER",
        "library": list(LABELS),
        "operation_arity": 3,
        "clause_language": "ALL_EIGHT_SIGNED_3CLAUSE_RELATIONS",
        "preservation_check": {
            "algebra_label_triples_per_relation": 64,
            "relation_rows": 7,
            "input_row_triples_checked_per_label_triple": 343,
            "method": "EXHAUSTIVE_DEFINITIONAL_CLOSURE_CHECK",
        },
        "positive_clause": {
            "formula": "(x OR y OR z)",
            "allowed_algebra_label_triples": [list(x) for x in induced[positive]],
            "count": len(pos_set),
        },
        "negative_clause": {
            "formula": "(NOT x OR NOT y OR NOT z)",
            "allowed_algebra_label_triples": [list(x) for x in induced[negative]],
            "count": len(neg_set),
        },
        "two_clause_witness": {
            "formula": "(x OR y OR z) AND (NOT x OR NOT y OR NOT z)",
            "original_formula_satisfiable": True,
            "common_B4_variablewise_algebra_assignments": intersection,
            "common_assignment_count": len(intersection),
            "verdict": "NO_B4_INDUCED_ALGEBRA_PROTOTYPE",
        },
        "template_bridge": {
            "candidate_maps_D01_to_B4_checked": 16,
            "gamma_3sat_to_gamma_B4_homomorphisms": [list(x) for x in homs],
            "count": len(homs),
            "verdict": "NO_GAMMA_3SAT_TO_GAMMA_B4_HOMOMORPHISM",
        },
        "scientific_meaning": [
            "VARIABLE_SPECIFIC_CHOICE_AMONG_AND3_OR3_MAJ3_XOR3_IS_NOT_UNIVERSAL_FOR_3CNF",
            "THE_STANDARD_BOOLEAN_SCHAEFER_B4_LIBRARY_DOES_NOT_CLOSE_THE_6I_COVERAGE_GATE",
            "THIS_DOES_NOT_RULE_OUT_RICHER_OR_LIFTED_TRACTABLE_ALGEBRA_FAMILIES",
        ],
        "firewall": {
            "P_VS_NP": "OPEN",
            "D1": "EMPTY",
            "SUCCESSOR_ALGORITHM": "LOCKED",
            "FINITE_FIXED_LIBRARY_FALSIFIER_IS_NOT_A_GENERAL_LOWER_BOUND": True,
        },
    }


def main() -> int:
    receipt = build_receipt()
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
