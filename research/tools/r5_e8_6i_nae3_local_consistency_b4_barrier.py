#!/usr/bin/env python3
"""Exact NAE3 local-consistency barrier for the Boolean B4 induced-algebra route.

Scope:
- one 3-variable NAE relation, equivalently
  (x OR y OR z) AND (NOT x OR NOT y OR NOT z);
- standard extension-based local consistency on the original scope;
- B4 = {AND3, OR3, MAJ3, XOR3}.

The checker proves:
1) every unary projection is full {0,1};
2) every binary projection is full {0,1}^2;
3) every assignment to <=2 variables extends to a NAE tuple;
4) no B4 algebra-label triple preserves NAE3.

Therefore arc/path/strong-3 consistency does not remove the witness and cannot
create a B4 induced prototype for it.

This is a scoped barrier only. It does not rule out richer preprocessing that
changes representation, introduces new variables, or uses a different algebra family.
"""
from __future__ import annotations

import itertools
import json

D = (0, 1)
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


def nae3() -> tuple[tuple[int, int, int], ...]:
    return tuple(
        row for row in itertools.product(D, repeat=3)
        if row not in ((0, 0, 0), (1, 1, 1))
    )


def project(relation, coords):
    return tuple(sorted({tuple(row[i] for i in coords) for row in relation}))


def extends(relation, partial: dict[int, int]) -> bool:
    return any(all(row[i] == v for i, v in partial.items()) for row in relation)


def preserves(relation, labels):
    allowed = set(relation)
    for r0, r1, r2 in itertools.product(relation, repeat=3):
        out = tuple(op(labels[j], r0[j], r1[j], r2[j]) for j in range(3))
        if out not in allowed:
            return False
    return True


def build_receipt():
    rel = nae3()

    unary = {
        str(coords): [list(x) for x in project(rel, coords)]
        for coords in itertools.combinations(range(3), 1)
    }
    binary = {
        str(coords): [list(x) for x in project(rel, coords)]
        for coords in itertools.combinations(range(3), 2)
    }

    extension_checks = []
    for size in (0, 1, 2):
        for coords in itertools.combinations(range(3), size):
            for vals in itertools.product(D, repeat=size):
                partial = dict(zip(coords, vals))
                ok = extends(rel, partial)
                extension_checks.append({
                    "partial": {str(k): v for k, v in partial.items()},
                    "extends": ok,
                })
                assert ok

    preserving = [
        labels for labels in itertools.product(LABELS, repeat=3)
        if preserves(rel, labels)
    ]

    assert len(rel) == 6
    assert all(len(v) == 2 for v in unary.values())
    assert all(len(v) == 4 for v in binary.values())
    assert preserving == []

    return {
        "schema": "janus.r5_e8_6i.nae3_local_consistency_b4_barrier.v1",
        "status": "PASS_EXACT_SCOPED_BARRIER",
        "witness": {
            "relation": "NAE3",
            "equivalent_formula": "(x OR y OR z) AND (NOT x OR NOT y OR NOT z)",
            "rows": [list(x) for x in rel],
            "row_count": len(rel),
            "satisfiable": True,
        },
        "local_consistency": {
            "unary_projections": unary,
            "binary_projections": binary,
            "all_partial_assignments_of_size_at_most_2_extend": True,
            "extension_check_count": len(extension_checks),
            "arc_consistent": True,
            "path_consistent": True,
            "strong_3_consistent": True,
            "fixed_point_statement": "STANDARD_EXTENSION_BASED_LOCAL_CONSISTENCY_DOES_NOT_PRUNE_NAE3",
        },
        "induced_algebra": {
            "library": list(LABELS),
            "label_triples_checked": 64,
            "preserving_label_triples": [list(x) for x in preserving],
            "preserving_label_triple_count": len(preserving),
            "verdict": "NO_B4_PROTOTYPE_FOR_NAE3",
        },
        "consequence": {
            "ARC_PATH_STRONG3_PREPROCESSING_RESCUES_B4": False,
            "scope": "ORIGINAL_NAE3_SCOPE__STANDARD_EXTENSION_BASED_LOCAL_CONSISTENCY",
            "does_not_rule_out": [
                "REPRESENTATION_CHANGING_PREPROCESSING",
                "NEW_VARIABLE_INTRODUCTION",
                "NONLOCAL_GLOBAL_PREPROCESSING",
                "RICHER_ALGEBRA_FAMILY",
            ],
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "D1": "EMPTY",
            "SUCCESSOR_ALGORITHM": "LOCKED",
        },
    }


if __name__ == "__main__":
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))
