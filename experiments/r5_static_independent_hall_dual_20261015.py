#!/usr/bin/env python3
"""R5 static critical-difference dual and Petersen convexification firewall.

ALL-N mathematical identities are established in the companion checkpoint.
This file is a finite exhaustive regression; exponential enumeration of
vertex masks and independent sets is NOT a polynomial universal solver.
Only Python standard library and the PR #518 frozen source controls.
"""
from collections import Counter
from itertools import combinations
import json

from r5_tutte_deficit_local_trap_20261014 import (
    N12_EDGES, all_signatures, controls, verify_cubic
)
from r5_tutte_hall_decomposition_20261014 import N10_EDGES
from r5_global_cut_hall_clause_20261015 import polynomial_hall_witness


def independent_set_masks_and_neighborhoods(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    family = []
    for X in range(1 << n):
        if any(((X >> u) & 1) and ((X >> v) & 1)
               for u, v in edges):
            continue
        nbr = 0
        for v in range(n):
            if (X >> v) & 1:
                nbr |= adj[v]
        assert not (X & nbr)
        family.append((X, nbr))
    return family


def exact_max_critical_difference(exposure_mask, independent_family):
    values = [
        (exposure_mask & X).bit_count() -
        (exposure_mask & nbr).bit_count()
        for X, nbr in independent_family
    ]
    return max(values)


def quadratic_mono_bit(a, b):
    """Exact degree-2 polynomial: 1-a-b+2ab, a,b in {0,1}."""
    return 1 - a - b + 2*a*b


def quadratic_lift_witness(n, edges, mask, residual_matching):
    """Check exact O(n) quadratic integer equalities (NO mod 2 or 3)."""
    z = set(residual_matching)
    for edge in edges:
        u, v = edge
        a, b = (mask >> u) & 1, (mask >> v) & 1
        assert quadratic_mono_bit(a, b) in (0, 1)
        if quadratic_mono_bit(a, b) == 1:
            assert edge not in z
    for v in range(n):
        assert sum(quadratic_mono_bit((mask >> a) & 1, (mask >> b) & 1)
                   + int((a, b) in z)
                   for a, b in edges if v in (a, b)) == 1


def polynomial_residual_matching(n, edges, mask, state):
    """Deterministic augmenting paths on the fixed candidate residual graph.

    O(n|E|) bound on cubic graphs; independent of the subset-matching
    oracle used in all_signatures(). Returns a concrete residual matching.
    """
    exposed = set(state["remaining"])
    left = sorted(v for v in exposed if ((mask >> v) & 1) == 0)
    right = set(exposed) - set(left)
    adj = {v: [] for v in left}
    for u, v in edges:
        if u in adj and v in right:
            adj[u].append(v)
        if v in adj and u in right:
            adj[v].append(u)
    for u in left:
        adj[u].sort()
    mate_right = {}

    def augment(u, seen):
        for v in adj[u]:
            if v in seen:
                continue
            seen.add(v)
            if v not in mate_right or augment(mate_right[v], seen):
                mate_right[v] = u
                return True
        return False

    for u in left:
        augment(u, set())
    assert len(mate_right) == state["nu"]
    return tuple(sorted(tuple(sorted((u, v)))
                        for v, u in mate_right.items()))


def exact_small_quadratic_feasibility(n, edges, mask):
    """Independent exhaustive z search, only allowed for n<=6."""
    assert n <= 6
    mono = [quadratic_mono_bit((mask >> u) & 1, (mask >> v) & 1)
            for u, v in edges]
    inc = [tuple(i for i, (u, w) in enumerate(edges) if v in (u, w))
           for v in range(n)]
    for zbits in range(1 << len(edges)):
        if all(sum(mono[i] + ((zbits >> i) & 1) for i in row) == 1
               for row in inc):
            return tuple(edges[i] for i in range(len(edges))
                         if (zbits >> i) & 1)
    return None


def verify_fixture(name, n, edges, expected_hist, exact_small=False):
    verify_cubic(n, edges)
    independent = independent_set_masks_and_neighborhoods(n, edges)
    valid = all_signatures(n, edges)
    hist = dict(sorted(Counter(st["delta"] for st in valid.values()).items()))
    assert hist == expected_hist, (name, hist)
    exposures = [0] * n
    zero_masks = []
    for mask, state in valid.items():
        exposed_mask = sum(1 << v for v in state["remaining"])
        for v in state["remaining"]:
            exposures[v] += 1
        static_dual = exact_max_critical_difference(exposed_mask, independent)
        assert static_dual == state["delta"], (name, mask, static_dual, state)
        hall = polynomial_hall_witness(n, edges, state, mask)
        assert hall["matching_size"] == state["nu"]
        found = polynomial_residual_matching(n, edges, mask, state)
        if state["delta"] == 0:
            quadratic_lift_witness(n, edges, mask, found)
            zero_masks.append(mask)
        if exact_small:
            z = exact_small_quadratic_feasibility(n, edges, mask)
            assert (z is not None) == (state["delta"] == 0)
            if z is not None:
                quadratic_lift_witness(n, edges, mask, z)
    if exact_small:
        # Include inadmissible labelings in the independent polynomial test.
        for mask in range(1 << n):
            z = exact_small_quadratic_feasibility(n, edges, mask)
            assert (z is not None) == (mask in zero_masks)
    return {
        "n": n,
        "independent_sets_tested": len(independent),
        "admissible_masks_tested": len(valid),
        "delta_histogram": hist,
        "exposure_counts_over_all_admissible_masks": exposures,
        "zero_delta_masks": zero_masks,
        "small_quadratic_exhaustion": exact_small,
        "static_dual_all_states": "PASS",
        "fixed_state_polynomial_matching": "PASS",
    }


def petersen_convexity_certificate(report, edges):
    n = report["n"]
    assert n == 10
    assert report["admissible_masks_tested"] == 10
    assert report["delta_histogram"] == {4: 10}
    count = report["exposure_counts_over_all_admissible_masks"]
    assert count == [4] * n
    pm_spokes = [(i, i+5) for i in range(5)]
    assert all(x in edges for x in pm_spokes)
    assert sorted([v for e in pm_spokes for v in e]) == list(range(10))
    ind = independent_set_masks_and_neighborhoods(n, edges)
    # Work with integer numerators rather than floating-point averages.
    deficits_times_10 = [
        sum(count[v] for v in range(n) if (X >> v) & 1)
        - sum(count[v] for v in range(n) if (nbr >> v) & 1)
        for X, nbr in ind
    ]
    assert max(deficits_times_10) == 0
    return {
        "source_graph": "Petersen",
        "integer_min_of_max": 4,
        "convex_relaxation_min_of_max": 0,
        "average_exposure_numerator": count,
        "average_exposure_denominator": 10,
        "fractional_vector": "rbar(v)=2/5 for all vertices",
        "PM_witness": pm_spokes,
        "all_independent_sets_checked": len(ind),
        "strict_integrality_gap": 4,
    }


def run():
    fixtures = {
        "K4": (4, tuple(combinations(range(4), 2)), {0: 6}, True),
        "K33": (6, tuple((a, b) for a in range(3) for b in range(3, 6)),
                {0: 2}, True),
        "Petersen": (10, controls()[2][1], {4: 10}, False),
        "SAT_Hall10": (10, N10_EDGES, {0: 12, 2: 4}, False),
        "SAT_Imbalance12": (12, N12_EDGES, {0: 8, 4: 2}, False),
    }
    data = {
        name: verify_fixture(name, *config)
        for name, config in fixtures.items()
    }
    result = {
        "scientific_status": "ALL_N_STATIC_DUAL_THEOREM_AND_FINITE_CERTIFIED_CONVEXITY_GAP",
        "static_identity": (
            "Delta(s)=max_{X independent in G} "
            "[sum_{v in X} r_s(v)-sum_{w in N_G(X)} r_s(w)]"
        ),
        "convex_relaxation_obstruction": petersen_convexity_certificate(
            data["Petersen"], fixtures["Petersen"][1]
        ),
        "quadratic_lift": (
            "mono_uv=1-a_u-a_v+2*a_u*a_v; "
            "forall v: sum_{e incident v}(mono_e+z_e)=1; "
            "a,z binary; O(n) equations"
        ),
        "fixtures": data,
        "polytime_quantifier_elimination": "NOT_CONSTRUCTED",
        "SolveLinearCubicXSAT": "NOT_CONSTRUCTED",
        "P_vs_NP": "OPEN",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    run()
