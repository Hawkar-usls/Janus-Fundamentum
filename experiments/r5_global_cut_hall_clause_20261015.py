#!/usr/bin/env python3
"""R5 global Hall-cut certificates and alternating matching exchanges.

Proof statements are in docs/r5_global_cut_hall_clause_checkpoint_20261015.md.
The Hall certificate extractor is polynomial-time on a fixed labeling.
The exhaustive all-labeling/all-pair finite regression is exponential:
THIS IS NOT A UNIVERSAL POLYNOMIAL SAT SOLVER.
"""
from collections import Counter, deque
from itertools import combinations
import json

from r5_tutte_deficit_local_trap_20261014 import (
    N12_EDGES, all_signatures, controls, verify_cubic,
)
from r5_tutte_hall_decomposition_20261014 import N10_EDGES


def polynomial_hall_witness(n, edges, state, mask):
    """Kuhn augmentations + alternating reachability in the smaller side.

    Returns X with |X|-|N_R(X)| = |U_min|-nu(R).
    Polynomial O(n*|E|) on cubic simple inputs; no subset enumeration.
    """
    u = set(state["remaining"])
    zero = sorted(v for v in u if ((mask >> v) & 1) == 0)
    one = sorted(u - set(zero))
    left, right = (zero, one) if len(zero) <= len(one) else (one, zero)
    right_set = set(right)
    adj = {v: [] for v in left}
    for a, b in edges:
        if a in adj and b in right_set:
            adj[a].append(b)
        if b in adj and a in right_set:
            adj[b].append(a)
    for v in left:
        adj[v].sort()

    mate_right = {}

    def augment(v, seen):
        for w in adj[v]:
            if w in seen:
                continue
            seen.add(w)
            if w not in mate_right or augment(mate_right[w], seen):
                mate_right[w] = v
                return True
        return False

    for v in left:
        augment(v, set())

    mate_left = {v: w for w, v in mate_right.items()}
    seen_left = set(left) - set(mate_left)
    seen_right = set()
    queue = deque(sorted(seen_left))
    while queue:
        v = queue.popleft()
        for w in adj[v]:
            if mate_left.get(v) == w:
                continue  # alternating step: unmatched L-->R
            if w in seen_right:
                continue
            seen_right.add(w)
            if w in mate_right and mate_right[w] not in seen_left:
                y = mate_right[w]
                seen_left.add(y)
                queue.append(y)

    neighbors = {w for v in seen_left for w in adj[v]}
    assert neighbors == seen_right
    hall_defect = len(seen_left) - len(neighbors)
    assert hall_defect == len(left) - len(mate_right)
    assert len(mate_right) == state["nu"]
    assert state["delta"] == 2 * (
        abs((n - mask.bit_count()) - mask.bit_count()) + hall_defect
    )
    return {
        "X": sorted(seen_left),
        "neighbors": sorted(neighbors),
        "hall_defect": hall_defect,
        "smaller_side": list(left),
        "matching_size": len(mate_right),
    }


def incident_star_for_hall(edges, X):
    """E(N_G[X]): edges incident to X or any original-graph neighbor of X."""
    near = set(X)
    for a, b in edges:
        if a in X or b in X:
            near.update((a, b))
    return {e for e in edges if (e[0] in near or e[1] in near)}


def global_cut(edges, a, b):
    flipped = a ^ b
    return {e for e in edges
            if ((flipped >> e[0]) & 1) != ((flipped >> e[1]) & 1)}


def assert_cut_exchange(n, edges, old_mask, new_mask, old, new):
    """Exact cut-space matching exchange, plus 2|cut| Lipschitz theorem."""
    old_matching = set(old["same"])
    new_matching = set(new["same"])
    cut = global_cut(edges, old_mask, new_mask)
    assert cut == old_matching ^ new_matching
    assert abs(old["delta"] - new["delta"]) <= 2 * len(cut)
    for v in range(n):
        touch = [e for e in cut if v in e]
        old_at_v = [e for e in old_matching if v in e]
        assert len(touch) <= 2
        if len(touch) == 2:
            assert sum(e in old_matching for e in touch) == 1
        if len(touch) == 1 and touch[0] not in old_matching:
            assert len(old_at_v) == 0

    if new["delta"] == 0:
        flip = old_mask ^ new_mask
        flipped_zero = sum(1 for v in range(n)
                           if (flip >> v) & 1 and not ((old_mask >> v) & 1))
        flipped_one = sum(1 for v in range(n)
                          if (flip >> v) & 1 and ((old_mask >> v) & 1))
        assert 2 * (flipped_zero - flipped_one) == n - 2 * old_mask.bit_count()
    return cut


def inspect_fixture(name, n, edges, expected, anchor=None):
    verify_cubic(n, edges)
    states = all_signatures(n, edges)  # finite baseline exact oracle
    hist = dict(sorted(Counter(s["delta"] for s in states.values()).items()))
    assert hist == expected, (name, hist)
    all_zero = [s for s in states if states[s]["delta"] == 0]
    checks = 0
    hall_hits = 0
    certificates = {}
    for source_mask, source in states.items():
        cert = polynomial_hall_witness(n, edges, source, source_mask)
        if cert["hall_defect"] > 0:
            # A certificate on the smaller bipartition, derived in O(n*|E|).
            assert len(cert["X"]) > len(cert["neighbors"])
            star = incident_star_for_hall(edges, set(cert["X"]))
            certificates[str(source_mask)] = {
                **cert, "edge_star_size": len(star),
            }
        else:
            star = set()
        for target_mask, target in states.items():
            cut = assert_cut_exchange(
                n, edges, source_mask, target_mask, source, target
            )
            if star and target["delta"] == 0:
                # ANY terminal zero state must destroy the frozen Hall
                # certificate, even if its vertex flip support is huge.
                assert cut & star, (name, source_mask, target_mask, cert)
                hall_hits += 1
            if star and source["delta"] == 2 and target["delta"] < 2:
                assert cut & star
            checks += 1

    data = {
        "admissible_mask_count": len(states),
        "delta_histogram": hist,
        "all_admissible_pairs_checked": checks,
        "hall_to_zero_cut_clause_checks": hall_hits,
        "positive_hall_certificates": certificates,
    }
    if anchor is not None:
        good = [s for s in all_zero]
        deltas = [(m, (anchor ^ m).bit_count(),
                   len(global_cut(edges, anchor, m))) for m in good]
        data["anchor"] = anchor
        data["min_hamming_to_zero"] = min(x[1] for x in deltas)
        data["min_cut_edges_to_zero"] = min(x[2] for x in deltas)
    return data


def run():
    fixtures = {
        "K4": (4, tuple(combinations(range(4), 2)), {0: 6}, None),
        "K33": (6, tuple((u, v) for u in range(3) for v in range(3, 6)),
                {0: 2}, None),
        "Petersen": (10, controls()[2][1], {4: 10}, None),
        "SAT_Hall10": (10, N10_EDGES, {0: 12, 2: 4}, 551),
        "SAT_Imbalance12": (12, N12_EDGES, {0: 8, 4: 2}, 1246),
    }
    report = {name: inspect_fixture(name, *config)
              for name, config in fixtures.items()}
    hall10 = report["SAT_Hall10"]
    assert hall10["hall_to_zero_cut_clause_checks"] == 48
    assert hall10["positive_hall_certificates"]["551"]["X"] == [3]
    assert hall10["positive_hall_certificates"]["551"]["neighbors"] == []
    assert hall10["positive_hall_certificates"]["551"]["hall_defect"] == 1
    assert hall10["min_hamming_to_zero"] == 2
    assert hall10["min_cut_edges_to_zero"] == 4
    # Negative firewall: balance + admissibility + the Hall cut clause
    # do not themselves force a strict decrease in Delta.
    # Mask 682 is valid and balanced, hits the star of X={3},
    # but its deficit is still 2 (the source 551 also has Delta=2).
    hall_obstacle_cut = global_cut(N10_EDGES, 551, 682)
    star551 = incident_star_for_hall(N10_EDGES, {3})
    state682 = all_signatures(10, N10_EDGES)[682]
    assert state682["delta"] == 2
    assert (682).bit_count() == 5
    assert len(hall_obstacle_cut & star551) == 4
    hall10["necessary_clause_false_positive"] = {
        "target_mask": 682,
        "target_delta": state682["delta"],
        "cut_edge_count": len(hall_obstacle_cut),
        "cut_star_hits": len(hall_obstacle_cut & star551),
        "note": "Necessary Hall cut and balance satisfied; NOT a descent",
    }
    assert report["SAT_Imbalance12"]["min_hamming_to_zero"] == 5
    assert report["SAT_Imbalance12"]["min_cut_edges_to_zero"] == 5
    summary = {
        "epistemic_status": "ALL_N_THEOREMS_WITH_FINITE_EXACT_REGRESSION",
        "theorems": [
            "Hall witness X with deficit>0 forces delta(F) to meet E(N_G[X]) for every Delta(s')=0",
            "M(s')=M(s) symmetric_difference delta(F)",
            "|Delta(s')-Delta(s)| <= 2|delta(F)|",
            "M(s) symmetric_difference M(s') is a cut and a matching-alternating path/cycle family",
            "Delta(s')=0 forces exact balance of the original two label classes",
        ],
        "results": report,
        "uniform_polynomial_GlobalCutImprove": "NOT_CONSTRUCTED",
        "P_vs_NP": "OPEN",
    }
    print(json.dumps(summary, sort_keys=True, indent=2))
    return summary


if __name__ == "__main__":
    run()
