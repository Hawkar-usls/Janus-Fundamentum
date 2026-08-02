#!/usr/bin/env python3
"""Policy-selected JANUS Tear frontier audit.

This audit studies the surviving JANUS Tear formulation: not a polynomial
quotient of *all* residual states, but one explicit policy that visits only a
small set of states.

For an affine Boolean system A x = b over GF(2), split variables into a
processed prefix P and unprocessed suffix U. A prefix assignment induces the
residual system

    A_U x_U = b + A_P a.

Among extendable prefixes, distinct residual solution sets are counted exactly
by

    2^d,  d = dim(im A_P intersection im A_U).

All non-extendable prefixes share one empty residual class. Thus d is an exact
semantic frontier dimension for the chosen variable order/cut.

The audit shows:

1. policy sensitivity: E_n(X,Y)=AND_i(x_i<->y_i) has exponential width when all
   X variables are processed before all Y variables, but constant width under
   the interleaved order x1,y1,...;
2. separator-state explosion: a column sweep of an m x m toroidal Tseitin
   system has exact block-boundary dimension 2m-1, hence 2^(2m-1) extendable
   residual affine states;
3. representation sensitivity: the same odd-charge Tseitin system has a linear
   global parity certificate, so affine elimination avoids enumerating the
   separator states.

This is software-only and does not prove P=NP or P!=NP.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Iterable, Sequence


BitVector = int


def gf2_basis(vectors: Iterable[BitVector]) -> dict[int, BitVector]:
    """Return a row-echelon XOR basis keyed by pivot bit."""
    basis: dict[int, BitVector] = {}
    for original in vectors:
        value = original
        while value:
            pivot = value.bit_length() - 1
            previous = basis.get(pivot)
            if previous is None:
                basis[pivot] = value
                break
            value ^= previous
    return basis


def gf2_rank(vectors: Iterable[BitVector]) -> int:
    return len(gf2_basis(vectors))


def gf2_contains(vectors: Iterable[BitVector], target: BitVector) -> bool:
    basis = gf2_basis(vectors)
    value = target
    while value:
        pivot = value.bit_length() - 1
        previous = basis.get(pivot)
        if previous is None:
            return False
        value ^= previous
    return True


def intersection_dimension(
    left: Sequence[BitVector],
    right: Sequence[BitVector],
) -> int:
    """dim(span(left) ∩ span(right)) by Grassmann's identity."""
    return gf2_rank(left) + gf2_rank(right) - gf2_rank((*left, *right))


@dataclass(frozen=True)
class FrontierRecord:
    cut: int
    processed_rank: int
    unprocessed_rank: int
    intersection_dimension: int
    extendable_residual_classes: int
    includes_empty_class: bool

    @property
    def total_residual_classes(self) -> int:
        return self.extendable_residual_classes + int(self.includes_empty_class)


def frontier_record(
    columns: Sequence[BitVector],
    order: Sequence[int],
    cut: int,
) -> FrontierRecord:
    if sorted(order) != list(range(len(columns))):
        raise ValueError("order must be a permutation of all column indices")
    if not 0 <= cut <= len(columns):
        raise ValueError("cut out of range")

    processed = [columns[index] for index in order[:cut]]
    unprocessed = [columns[index] for index in order[cut:]]
    processed_rank = gf2_rank(processed)
    unprocessed_rank = gf2_rank(unprocessed)
    dimension = intersection_dimension(processed, unprocessed)

    # The full system is assumed consistent for residual-class counting.
    # Distinct extendable residual RHS vectors form one affine intersection
    # with direction im(A_P) ∩ im(A_U).
    extendable = 1 << dimension

    # If rank(A_P)>d, some prefix-induced RHS vectors lie outside im(A_U);
    # all such prefixes simplify to the same empty residual function.
    includes_empty = processed_rank > dimension

    return FrontierRecord(
        cut=cut,
        processed_rank=processed_rank,
        unprocessed_rank=unprocessed_rank,
        intersection_dimension=dimension,
        extendable_residual_classes=extendable,
        includes_empty_class=includes_empty,
    )


def profile(
    columns: Sequence[BitVector],
    order: Sequence[int],
) -> list[FrontierRecord]:
    return [
        frontier_record(columns, order, cut)
        for cut in range(len(columns) + 1)
    ]


def equality_columns(n: int) -> list[BitVector]:
    """Columns of x_i + y_i = 0 for i=1..n."""
    if n < 1:
        raise ValueError("n must be positive")
    unit = [1 << index for index in range(n)]
    return unit + unit


def equality_orders(n: int) -> tuple[list[int], list[int]]:
    bad = list(range(n)) + list(range(n, 2 * n))
    good = [
        index
        for pair in ((i, n + i) for i in range(n))
        for index in pair
    ]
    return bad, good


def equality_case(n: int) -> dict[str, object]:
    columns = equality_columns(n)
    bad, good = equality_orders(n)
    bad_profile = profile(columns, bad)
    good_profile = profile(columns, good)
    return {
        "n": n,
        "clauses_in_standard_2cnf_encoding": 2 * n,
        "bad_order": "x1,...,xn,y1,...,yn",
        "bad_max_frontier_dimension": max(
            record.intersection_dimension for record in bad_profile
        ),
        "bad_max_extendable_classes": max(
            record.extendable_residual_classes for record in bad_profile
        ),
        "good_order": "x1,y1,x2,y2,...,xn,yn",
        "good_max_frontier_dimension": max(
            record.intersection_dimension for record in good_profile
        ),
        "good_max_total_classes": max(
            record.total_residual_classes for record in good_profile
        ),
        "interpretation": (
            "The all-residual explosion is real for a bad policy, but the same "
            "formula family has a constant-width interleaved policy."
        ),
    }


Edge = tuple[str, int, int]


def vertex_id(x: int, y: int, side: int) -> int:
    return (x % side) * side + (y % side)


def torus_columns(side: int) -> tuple[list[BitVector], list[Edge]]:
    """Vertex-edge incidence columns of an m x m torus over GF(2)."""
    if side < 3:
        raise ValueError("side must be at least 3")
    columns: list[BitVector] = []
    labels: list[Edge] = []
    for x in range(side):
        for y in range(side):
            horizontal = (
                (1 << vertex_id(x, y, side))
                | (1 << vertex_id(x + 1, y, side))
            )
            vertical = (
                (1 << vertex_id(x, y, side))
                | (1 << vertex_id(x, y + 1, side))
            )
            columns.extend((horizontal, vertical))
            labels.extend((("H", x, y), ("V", x, y)))
    return columns, labels


def column_sweep_order(labels: Sequence[Edge]) -> list[int]:
    """Process every edge whose canonical start x-coordinate is in the column."""
    return sorted(
        range(len(labels)),
        key=lambda index: (
            labels[index][1],
            labels[index][0],
            labels[index][2],
        ),
    )


def torus_block_records(side: int) -> list[FrontierRecord]:
    columns, labels = torus_columns(side)
    order = column_sweep_order(labels)
    block_size = 2 * side
    return [
        frontier_record(columns, order, block_size * processed_columns)
        for processed_columns in range(side + 1)
    ]


def torus_case(side: int) -> dict[str, object]:
    columns, labels = torus_columns(side)
    order = column_sweep_order(labels)
    records = torus_block_records(side)
    internal = records[1:-1]
    expected_dimension = 2 * side - 1
    observed_dimensions = [
        record.intersection_dimension for record in internal
    ]

    # The incidence matrix of a connected graph has rank |V|-1 over GF(2).
    total_rank = gf2_rank(columns)
    expected_total_rank = side * side - 1

    # Odd total charge is outside the incidence-column span because every
    # column has even Hamming parity. This is the global Tseitin certificate.
    odd_charge_rhs = 1
    odd_rhs_in_image = gf2_contains(columns, odd_charge_rhs)

    # A representative even charge (two marked vertices) must lie in the image.
    even_charge_rhs = (1 << 0) | (1 << 1)
    even_rhs_in_image = gf2_contains(columns, even_charge_rhs)

    return {
        "side": side,
        "variables": 2 * side * side,
        "vertex_equations": side * side,
        "matrix_rank": total_rank,
        "expected_connected_incidence_rank": expected_total_rank,
        "block_boundary_dimensions": observed_dimensions,
        "exact_internal_block_dimension": expected_dimension,
        "extendable_classes_per_internal_block_cut": 1 << expected_dimension,
        "largest_signature_bits": expected_dimension,
        "odd_charge_global_certificate": {
            "rhs_hamming_parity": 1,
            "rhs_in_column_image": odd_rhs_in_image,
            "certificate": (
                "XOR all vertex equations: every edge occurs twice, so the "
                "left side is 0 while the odd charge sum is 1."
            ),
            "certificate_equation_references": side * side,
        },
        "even_charge_control": {
            "rhs_hamming_parity": 0,
            "rhs_in_column_image": even_rhs_in_image,
        },
        "interpretation": (
            "A sweep policy carries only O(side) bits per frontier signature, "
            "but encounters 2^(2*side-1) possible extendable signatures. "
            "Global affine recognition bypasses this enumeration."
        ),
    }


def run_audit() -> dict[str, object]:
    equality_records = [equality_case(n) for n in range(1, 13)]
    torus_records = [torus_case(side) for side in range(3, 13)]
    largest = torus_records[-1]
    return {
        "artifact": "JANUS-TEAR-POLICY-FRONTIER-AUDIT",
        "status": "EXPLORATORY_SOFTWARE_ONLY",
        "execution_scope": {
            "swarm_touched": False,
            "devices_touched": False,
            "network_runtime_touched": False,
        },
        "exact_formula": {
            "frontier_dimension": (
                "d = rank(A_P) + rank(A_U) - rank(A)"
            ),
            "extendable_residual_classes": "2^d",
            "empty_class": (
                "one additional class iff rank(A_P) > d"
            ),
        },
        "policy_sensitivity": equality_records,
        "separator_explosion": torus_records,
        "largest_tested_torus": largest,
        "new_conclusion": {
            "rejected": (
                "A polynomial-size Tear payload automatically implies a "
                "polynomial number of Tear states."
            ),
            "supported": (
                "For affine systems, the exact state count of a chosen cut is "
                "controlled by semantic intersection dimension."
            ),
            "surviving_route": (
                "A universal solver would need a polynomial-time policy that "
                "selects variable order, decomposition, and proof language so "
                "that total visited states and certificate work remain polynomial."
            ),
            "warning": (
                "The toroidal family is affine and already solvable by Gaussian "
                "elimination. Its frontier explosion is a lower bound on the "
                "tested sweep/quotient policy, not on all algorithms."
            ),
        },
        "claim_boundary": (
            "This audit neither proves P=NP nor P!=NP. It identifies an exact "
            "policy-width resource and demonstrates order and representation "
            "sensitivity."
        ),
    }


def self_test() -> None:
    # Basic rank/intersection controls.
    assert gf2_rank([0, 1, 2, 3]) == 2
    assert intersection_dimension([1, 2], [2, 4]) == 1

    for n in range(1, 13):
        record = equality_case(n)
        assert record["bad_max_frontier_dimension"] == n
        assert record["bad_max_extendable_classes"] == 2**n
        assert record["good_max_frontier_dimension"] == 1
        assert record["good_max_total_classes"] <= 3

    for side in range(3, 13):
        record = torus_case(side)
        assert record["matrix_rank"] == side * side - 1
        assert all(
            dimension == 2 * side - 1
            for dimension in record["block_boundary_dimensions"]
        )
        assert (
            record["extendable_classes_per_internal_block_cut"]
            == 2 ** (2 * side - 1)
        )
        assert (
            record["odd_charge_global_certificate"]["rhs_in_column_image"]
            is False
        )
        assert record["even_charge_control"]["rhs_in_column_image"] is True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--equality-n", type=int)
    parser.add_argument("--torus-side", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        print("JANUS_TEAR_POLICY_FRONTIER_SELF_TEST = PASS")
        print("EQUALITY_BAD_ORDER_EXPONENT = n")
        print("EQUALITY_INTERLEAVED_MAX_CLASSES <= 3")
        print("TORUS_COLUMN_BLOCK_EXPONENT = 2m-1")
        print("GLOBAL_ODD_PARITY_CERTIFICATE = PASS")
        return 0
    if args.equality_n is not None:
        print(json.dumps(equality_case(args.equality_n), indent=2))
        return 0
    if args.torus_side is not None:
        print(json.dumps(torus_case(args.torus_side), indent=2))
        return 0
    if args.json:
        print(json.dumps(run_audit(), indent=2))
        return 0
    raise SystemExit(
        "use --self-test, --json, --equality-n N, or --torus-side M"
    )


if __name__ == "__main__":
    raise SystemExit(main())
