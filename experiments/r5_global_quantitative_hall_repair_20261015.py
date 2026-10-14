#!/usr/bin/env python3
"""Exact quantitative Hall-repair constraints; finite all-subset regression.

Universal theorem: for every Hall set X of a source admissible labeling,
any zero-deficit target changes >= h_X units of X-removal / neighbor release.
This script enumerates labels and X subsets only on frozen tiny controls.
It is NOT a polynomial-time 3-edge-coloring solver.
"""
from collections import Counter
from itertools import combinations
import json

from r5_tutte_deficit_local_trap_20261014 import (
    N12_EDGES, all_signatures, controls, verify_cubic,
)
from r5_tutte_hall_decomposition_20261014 import N10_EDGES
from r5_global_cut_hall_clause_20261015 import global_cut


def all_hall_sets(n, edges, mask, state):
    """Enumerate EVERY positive-deficit X in either side; small graphs only."""
    residual = set(state["remaining"])
    parts = [
        sorted(v for v in residual if ((mask >> v) & 1) == color)
        for color in (0, 1)
    ]
    for side in parts:
        for count in range(1, len(side) + 1):
            for tup in combinations(side, count):
                X = set(tup)
                neighbors = {
                    v for u, v in edges if u in X and v in residual
                } | {
                    u for u, v in edges if v in X and u in residual
                }
                h = len(X) - len(neighbors)
                if h > 0:
                    yield frozenset(X), h, frozenset(neighbors)


def full_neighborhood(edges, X):
    return {v for u, v in edges if u in X} | {
        u for u, v in edges if v in X
    }


def verify_repair(n, edges, source_mask, source, target_mask, target, X, h):
    """Compare exact membership lower bound and its edge-switch relaxation."""
    U0 = set(source["remaining"])
    U1 = set(target["remaining"])
    old_mono = set(source["same"])
    cut = global_cut(edges, source_mask, target_mask)
    near = full_neighborhood(edges, X)
    old_covered_neighbors = near - U0

    removed_from_X = len(X - U1)
    newly_exposed_neighbors = len(old_covered_neighbors & U1)
    membership_repair = removed_from_X + newly_exposed_neighbors
    weighted_added_X = sum(u in X or v in X for u, v in cut)
    weighted_deleted_mono = sum(
        (u in old_covered_neighbors) + (v in old_covered_neighbors)
        for u, v in cut & old_mono
    )
    cut_repair_capacity = weighted_added_X + weighted_deleted_mono
    if target["delta"] == 0:
        assert membership_repair >= h, (
            n, source_mask, target_mask, X, membership_repair, h
        )
        assert cut_repair_capacity >= membership_repair, (
            n, source_mask, target_mask, X,
            membership_repair, cut_repair_capacity
        )
    # Upper bound is unconditional for valid target, even if Delta>0.
    assert cut_repair_capacity >= membership_repair
    return membership_repair, cut_repair_capacity


def evaluate(name, n, edges, expected_hist, exemplar=None):
    verify_cubic(n, edges)
    states = all_signatures(n, edges)
    hist = dict(sorted(Counter(s["delta"] for s in states.values()).items()))
    assert hist == expected_hist, (name, hist)
    terminal = {mask: x for mask, x in states.items() if x["delta"] == 0}
    stats = Counter()
    maximum_deficit = 0
    examples = []
    for sm, source in states.items():
        for X, h, neighbors in all_hall_sets(n, edges, sm, source):
            stats["Hall_sets"] += 1
            maximum_deficit = max(maximum_deficit, h)
            for tm, target in states.items():
                repair, capacity = verify_repair(
                    n, edges, sm, source, tm, target, X, h
                )
                stats["all_admissible_pair_Hall_tests"] += 1
                if tm in terminal:
                    stats["Hall_to_zero_tests"] += 1
                    if repair == h:
                        stats["tight_membership_repair_tests"] += 1
                    if capacity == h:
                        stats["tight_weighted_cut_tests"] += 1
                if source["delta"] > 0 and target["delta"] > 0 and capacity >= h:
                    stats["cut_clause_satisfied_but_not_terminal"] += 1
            if len(examples) < 4:
                examples.append({
                    "mask": sm,
                    "X": sorted(X),
                    "N_R_X": sorted(neighbors),
                    "deficit": h,
                })
    result = {
        "n": n,
        "admissible_labels": len(states),
        "terminal_labels": len(terminal),
        "delta_histogram": hist,
        "largest_Hall_deficit_on_fixture": maximum_deficit,
        "checks": dict(stats),
        "sample_certificates": examples,
    }
    if exemplar is not None:
        sm, X_tup, tm = exemplar
        X = frozenset(X_tup)
        assert sm in states and tm in states
        source, target = states[sm], states[tm]
        witnesses = list(all_hall_sets(n, edges, sm, source))
        assert any(W == X for W, _, _ in witnesses), (name, X)
        h = next(h for W, h, _ in witnesses if W == X)
        repair, capacity = verify_repair(
            n, edges, sm, source, tm, target, X, h
        )
        result["anchor"] = {
            "source_mask": sm, "target_mask": tm,
            "X": sorted(X), "h_X": h,
            "target_delta": target["delta"],
            "membership_repair": repair,
            "weighted_cut_repair_capacity": capacity,
        }
    return result


def run():
    fixtures = {
        "K4": (4, tuple(combinations(range(4), 2)), {0: 6}, None),
        "K33": (6, tuple((a, b) for a in range(3) for b in range(3, 6)),
                {0: 2}, None),
        "Petersen": (10, controls()[2][1], {4: 10}, None),
        "SAT_Hall10": (10, N10_EDGES, {0: 12, 2: 4},
                       (551, (3,), 779)),
        "SAT_Imbalance12": (12, N12_EDGES, {0: 8, 4: 2}, None),
    }
    results = {
        name: evaluate(name, *args) for name, args in fixtures.items()
    }
    assert results["SAT_Hall10"]["anchor"]["h_X"] == 1
    assert results["SAT_Hall10"]["anchor"]["target_delta"] == 0
    assert results["SAT_Imbalance12"]["largest_Hall_deficit_on_fixture"] == 0

    report = {
        "status": "PROVED_ALL_N_BOUND_FINITE_EXHAUSTIVE_REPLAY",
        "bound": (
            "removed_X + newly_uncovered_neighbors >= h_X; "
            "|C intersect E(X)| + sum_{old monochromatic cut edges e} "
            "|e intersect (N_G(X)\\U_old)| >= h_X"
        ),
        "results": results,
        "global_polynomial_improvement": "NOT_CONSTRUCTED",
        "SolveLinearCubicXSAT": "NOT_CONSTRUCTED",
        "P_vs_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    run()
