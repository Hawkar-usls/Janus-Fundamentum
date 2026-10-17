#!/usr/bin/env python3
"""Exact Hall/imbalance decomposition and cut-switch regression.

Finite exhaustive tests only; this is NOT a polynomial-time universal solver.
Proofs for all cubic graphs appear in the companion markdown checkpoint.
Python standard library; imports the frozen 2026-10-14 Tutte verifier.
"""
from collections import Counter
from itertools import combinations
import json

from r5_tutte_deficit_local_trap_20261014 import (
    N12_EDGES, all_signatures, controls, signature, verify_cubic,
)

# Connected, bridgeless, simple 10-vertex cubic graph.
# Edge list is frozen; do not regenerate from a randomized library API.
N10_EDGES = (
    (0, 3), (0, 5), (0, 7), (1, 2), (1, 4),
    (1, 6), (2, 3), (2, 8), (3, 5), (4, 6),
    (4, 9), (5, 8), (6, 9), (7, 8), (7, 9),
)


def hall_decomposition(n, edges, mask, state):
    """Brute-force Hall witness for small finite controls only."""
    m0 = [e for e in state["same"] if not ((mask >> e[0]) & 1)]
    m1 = [e for e in state["same"] if ((mask >> e[0]) & 1)]
    n0 = n - mask.bit_count()
    n1 = mask.bit_count()
    u0 = set(v for v in state["remaining"] if not ((mask >> v) & 1))
    u1 = set(state["remaining"]) - u0

    # Cubic degree sum: 3(n0-n1)=2(m0-m1).
    assert 3 * (n0 - n1) == 2 * (len(m0) - len(m1))
    assert len(u0) - len(u1) == -2 * (n0 - n1)

    smaller = sorted(u0 if len(u0) <= len(u1) else u1)
    other = u1 if len(u0) <= len(u1) else u0
    hall = 0
    witness = ()
    neighbors_witness = set()
    for k in range(len(smaller) + 1):
        for subset in combinations(smaller, k):
            members = set(subset)
            neighbors = {v for u, v in edges if u in members and v in other}
            neighbors |= {u for u, v in edges if v in members and u in other}
            h = len(subset) - len(neighbors)
            if h > hall:
                hall, witness, neighbors_witness = h, subset, neighbors
    assert state["delta"] == 2 * abs(n0 - n1) + 2 * hall
    return {
        "n0": n0, "n1": n1, "u0": sorted(u0), "u1": sorted(u1),
        "imbalance_contribution": 2 * abs(n0 - n1),
        "hall_deficiency": hall,
        "hall_witness": list(witness),
        "hall_neighbors": sorted(neighbors_witness),
        "delta": state["delta"],
    }


def monochromatic_edges(edges, mask):
    return {e for e in edges
            if ((mask >> e[0]) & 1) == ((mask >> e[1]) & 1)}


def cut_edges(edges, flip_mask):
    return {e for e in edges
            if ((flip_mask >> e[0]) & 1) != ((flip_mask >> e[1]) & 1)}


def verify_cut_switch(n, edges, initial):
    """All 2^n global flips, including ones passing through invalid states."""
    old = monochromatic_edges(edges, initial)
    for flips in range(1 << n):
        final = initial ^ flips
        assert monochromatic_edges(edges, final) == (
            old ^ cut_edges(edges, flips)), (initial, flips)


def test_case(n, edges, expected_histogram, anchor=None):
    verify_cubic(n, edges)
    states = all_signatures(n, edges)
    histogram = dict(sorted(Counter(
        state["delta"] for state in states.values()).items()))
    assert histogram == expected_histogram, (n, histogram)
    for mask, state in states.items():
        hall_decomposition(n, edges, mask, state)
    if anchor is not None:
        verify_cut_switch(n, edges, anchor)
    return states, histogram


def run():
    ten, h10 = test_case(10, N10_EDGES, {0: 12, 2: 4}, anchor=551)
    twelve, h12 = test_case(12, N12_EDGES, {0: 8, 4: 2}, anchor=1246)

    trap10 = hall_decomposition(10, N10_EDGES, 551, ten[551])
    assert trap10["n0"] == trap10["n1"] == 5
    assert trap10["u0"] == [3] and trap10["u1"] == [9]
    assert trap10["imbalance_contribution"] == 0
    assert trap10["hall_deficiency"] == 1
    assert trap10["hall_witness"] == [3]
    assert trap10["hall_neighbors"] == []
    assert ten[551]["same"] == ((0, 5), (1, 2), (4, 6), (7, 8))
    assert ten[779]["delta"] == 0
    assert ten[565]["delta"] == 0
    assert (551 ^ 565).bit_count() == 2

    trap12 = hall_decomposition(12, N12_EDGES, 1246, twelve[1246])
    assert sorted((trap12["n0"], trap12["n1"])) == [5, 7]
    assert trap12["imbalance_contribution"] == 4
    assert trap12["hall_deficiency"] == 0
    assert twelve[1295]["delta"] == 0
    assert min((1246 ^ m).bit_count() for m in twelve
               if twelve[m]["delta"] < 4) == 5

    ctr = {}
    for n, edges, hist in controls():
        states, observed = test_case(n, edges, hist)
        ctr[str(n)] = {
            "delta_histogram": observed,
            "admissible_labelings": len(states),
        }

    report = {
        "status": "EXACT_DECOMPOSITION_AND_FINITE_REGRESSION_NOT_SOLVER",
        "universal_identity": "Delta(s)=2*abs(n0-n1)+2*HallDef(smaller U part)",
        "cut_switch_identity": "Mono(s XOR f)=Mono(s) XOR cut(f)",
        "connected_SAT_hall_obstruction_n10": {
            "edges": N10_EDGES,
            "mask": 551,
            "matching": ten[551]["same"],
            "breakdown": trap10,
            "SAT_mask": 779,
            "2_flip_SAT_mask": 565,
            "delta_histogram": h10,
            "admissible_labelings": len(ten),
        },
        "connected_SAT_imbalance_obstruction_n12": {
            "mask": 1246,
            "breakdown": trap12,
            "SAT_mask": 1295,
            "minimal_strict_improvement_flips": 5,
            "delta_histogram": h12,
            "admissible_labelings": len(twelve),
        },
        "controls": ctr,
        "general_polynomial_algorithm": "NOT_CONSTRUCTED",
        "P_vs_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    run()
