#!/usr/bin/env python3
"""R5: complete abstract Kempe-closed Exact-One six-port countermodel.

This gives a NO-GO for a *proof strategy*, NOT an actual graph gadget:
parity, exact-one port colours and any number of individual two-colour
Kempe-path switches do not force a 000 or 111 boundary state.

For each of the 108 even-parity Exact-One port tuples s, and each
unordered colour pair (a,b), there is precisely ONE perfect matching
of the a/b-coloured ports for which switching ANY subset of the
matched paths preserves the CURRENT Exact-One bit. The matching
is equivariant under each switch of its own colour pair: if s -> s'
by such a switch, its unique matching at s' is unchanged.

All 108 states form exactly three abstract reachable components of size
36 each, one per Exact-One bit. Thus arbitrary path-switch duration
cannot force a forbidden state from boundary axioms alone.

CRITICAL LIMIT: Matchings for different colour pairs are assigned
independently. We DO NOT prove these can arise simultaneously as
the coloured alternating paths in ONE finite cubic multipole. That
geometric compatibility is the genuine missing theorem/obstruction.

Run: python -u experiments/r5_kempe_boundary_only_countermodel.py
"""

from collections import Counter
from itertools import combinations, product

from r5_kempe_coupled_involutions_n8_barrier import (
    COLORS, GOOD, bits, matchings,
)


def moves(ports, pair, matching):
    """All possible independent path-switch choices on one matching."""
    a, b = pair
    for mask in range(1 << len(matching)):
        q = list(ports)
        for j, (u, v) in enumerate(matching):
            if (mask >> j) & 1:
                q[u] = a + b - q[u]
                q[v] = a + b - q[v]
        yield tuple(q)


def stable_matchings(ports, pair):
    """Matchings that preserve precisely the same existing truth bit."""
    roots = tuple(i for i, x in enumerate(ports) if x in pair)
    return tuple(
        mm for mm in matchings(roots)
        if all(bits(t) == bits(ports) for t in moves(ports, pair, mm))
    )


def main():
    states = {
        s for s in product(COLORS, repeat=6)
        if bits(s) in GOOD
        and all(Counter(s)[c] % 2 == 0 for c in COLORS)
    }
    assert len(states) == 108

    transitions = {}
    checks = 0
    for s in sorted(states):
        adj = set()
        for pair in combinations(COLORS, 2):
            matches = stable_matchings(s, pair)
            assert len(matches) == 1, (s, pair, matches)
            matching = matches[0]
            for t in moves(s, pair, matching):
                assert t in states and bits(t) == bits(s)
                assert stable_matchings(t, pair) == (matching,), (
                    "same-colour-pair switch coherence failed",
                    s, pair, t, matching
                )
                adj.add(t)
                checks += 1
        transitions[s] = adj

    # Check reversibility and compute full multi-step reachable components.
    assert all(s in transitions[t] for s in states for t in transitions[s])
    remaining = set(states)
    component_sizes = []
    while remaining:
        root = min(remaining)
        reached = {root}
        frontier = [root]
        while frontier:
            x = frontier.pop()
            for y in transitions[x]:
                if y not in reached:
                    reached.add(y)
                    frontier.append(y)
        assert all(bits(s) == bits(root) for s in reached)
        component_sizes.append((bits(root), len(reached)))
        remaining -= reached

    assert sorted(component_sizes) == [
        ("001", 36), ("010", 36), ("100", 36),
    ], component_sizes
    assert checks == 1440, checks
    print("ABSTRACT_PARITY_EXACTONE_108 PASS")
    print("UNIQUE_STABLE_MATCHING_PER_STATE_PER_COLOUR_PAIR 324/324 PASS")
    print("SAME_PAIR_SWITCH_EQUIVARIANCE", checks, "PASS")
    print("REVERSIBLE_ALL_LENGTH_ABSTRACT_KEMPE_CLOSURE PASS")
    print("THREE_COMPONENTS", sorted(component_sizes), "PASS")
    print("NO_GO_BOUNDARY_ONLY_KEMPE_PROOF PASS")
    print("NOT_A_PHYSICAL_SIXPOLE; CROSS_COLOUR_INVOLUTION_COHERENCE OPEN")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
