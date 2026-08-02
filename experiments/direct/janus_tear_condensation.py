#!/usr/bin/env python3
"""JANUS Tear condensation experiment.

This is a deliberately narrow experiment on the C018 toroidal Tseitin family.

It compares two kinds of summaries:

1. bounded-local "tear signatures" that record only charge markers visible
   inside a fixed toroidal Manhattan radius; and
2. a global component-parity tear that records the XOR of charges in each
   connected component.

For the C018 twin construction, the bounded-local signature multisets are
identical, while the global component-parity tear distinguishes SAT from UNSAT.

The experiment does not solve general SAT and does not prove P = NP.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from itertools import product
from typing import Sequence

Point = tuple[int, int]
ComponentCharges = tuple[Point, ...]
ChargeLayout = tuple[ComponentCharges, ...]
LocalSignature = tuple[Point, ...]


@dataclass(frozen=True)
class TearTwin:
    radius: int
    side: int
    sat_charges: ChargeLayout
    unsat_charges: ChargeLayout


def wrapped_delta(target: int, root: int, modulus: int) -> int:
    """Return the unique shortest signed displacement on an odd cycle."""
    delta = (target - root) % modulus
    if delta > modulus // 2:
        delta -= modulus
    return delta


def make_twin(radius: int) -> TearTwin:
    """Construct the charge layouts used by the simplified C018 audit."""
    if radius < 1:
        raise ValueError("radius must be at least 1")

    side = 8 * radius + 13
    separation = 4 * radius + 6

    # SAT: both charges live in one component, so both component parities are 0.
    sat_charges: ChargeLayout = (
        ((0, 0), (separation, 0)),
        (),
    )

    # UNSAT: one charge lives in each component, so both parities are 1.
    unsat_charges: ChargeLayout = (
        ((0, 0),),
        ((0, 0),),
    )

    return TearTwin(
        radius=radius,
        side=side,
        sat_charges=sat_charges,
        unsat_charges=unsat_charges,
    )


def local_signature(
    root: Point,
    charges: Sequence[Point],
    side: int,
    radius: int,
) -> LocalSignature:
    """Record translation-normalized visible charge offsets around one root."""
    visible: list[Point] = []
    for charge_x, charge_y in charges:
        dx = wrapped_delta(charge_x, root[0], side)
        dy = wrapped_delta(charge_y, root[1], side)
        if abs(dx) + abs(dy) <= radius:
            visible.append((dx, dy))
    return tuple(sorted(visible))


def local_tear_multiset(
    side: int,
    radius: int,
    layout: ChargeLayout,
) -> Counter[LocalSignature]:
    """Collect all bounded-local tear signatures across all components."""
    signatures: Counter[LocalSignature] = Counter()
    for charges in layout:
        for root in product(range(side), repeat=2):
            signatures[local_signature(root, charges, side, radius)] += 1
    return signatures


def component_parity_tear(layout: ChargeLayout) -> tuple[int, ...]:
    """Return one global XOR invariant per connected component."""
    return tuple(len(charges) % 2 for charges in layout)


def tseitin_status_from_tear(tear: Sequence[int]) -> str:
    """A connected Tseitin component is satisfiable iff its charge parity is 0."""
    return "SAT" if all(bit == 0 for bit in tear) else "UNSAT"


def run_case(radius: int) -> dict[str, object]:
    twin = make_twin(radius)

    sat_local = local_tear_multiset(
        twin.side,
        twin.radius,
        twin.sat_charges,
    )
    unsat_local = local_tear_multiset(
        twin.side,
        twin.radius,
        twin.unsat_charges,
    )

    sat_global = component_parity_tear(twin.sat_charges)
    unsat_global = component_parity_tear(twin.unsat_charges)

    return {
        "radius": radius,
        "side": twin.side,
        "vertices_per_two_components": 2 * twin.side * twin.side,
        "local_signature_multisets_equal": sat_local == unsat_local,
        "local_signature_type_count": len(sat_local),
        "sat_global_tear": sat_global,
        "unsat_global_tear": unsat_global,
        "sat_status_from_global_tear": tseitin_status_from_tear(sat_global),
        "unsat_status_from_global_tear": tseitin_status_from_tear(unsat_global),
        "interpretation": (
            "Bounded-local tears cannot see how the two charges are distributed "
            "between components, but one global parity bit per component can."
        ),
        "claim_boundary": (
            "This is a family-specific invariant for Tseitin systems, not a "
            "general SAT algorithm or a P=NP result."
        ),
    }


def self_test() -> None:
    for radius in range(1, 9):
        result = run_case(radius)
        assert result["local_signature_multisets_equal"] is True
        assert tuple(result["sat_global_tear"]) == (0, 0)
        assert tuple(result["unsat_global_tear"]) == (1, 1)
        assert result["sat_status_from_global_tear"] == "SAT"
        assert result["unsat_status_from_global_tear"] == "UNSAT"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius", type=int, default=3)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        print("JANUS_TEAR_SELF_TEST = PASS")
        return 0

    print(json.dumps(run_case(args.radius), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
