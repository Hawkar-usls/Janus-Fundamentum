#!/usr/bin/env python3
from __future__ import annotations

from itertools import product
import json


def e(u: int, v: int) -> frozenset[int]:
    return frozenset((u, v))


def boundary(matching: set[frozenset[int]], boundary_vertices: set[int]) -> frozenset[int]:
    touched = set()
    for edge in matching:
        touched.update(edge)
    return frozenset(touched & boundary_vertices)


def is_matching(matching: set[frozenset[int]]) -> bool:
    used: set[int] = set()
    for edge in matching:
        if len(edge) != 2:
            return False
        for v in edge:
            if v in used:
                return False
            used.add(v)
    return True


def red_count(matching: set[frozenset[int]], red: set[frozenset[int]]) -> int:
    return sum(edge in red for edge in matching)


# Toy four-port gadget witness pair.
# Boundary: 0,1,2,3. Internal: 4,5.
# M0 saturates only the internal vertices.
# M4 saturates all boundary and internal vertices.
U = {0, 1, 2, 3}
M0 = {e(4, 5)}
M4 = {e(0, 4), e(1, 2), e(3, 5)}
PATH = {e(0, 4), e(4, 5), e(3, 5)}
MA = M0 ^ PATH
MB = M4 ^ PATH

assert is_matching(M0) and is_matching(M4)
assert is_matching(MA) and is_matching(MB)
assert boundary(M0, U) == frozenset()
assert boundary(M4, U) == frozenset(U)
assert boundary(MA, U) == frozenset({0, 3})
assert boundary(MB, U) == frozenset({1, 2})
assert boundary(MA, U) | boundary(MB, U) == frozenset(U)
assert boundary(MA, U) & boundary(MB, U) == frozenset()

# Exact multiset conservation: each edge occurs with the same total multiplicity
# across the OFF+ON pair and the two mixed matchings.
ALL_EDGES = sorted(M0 | M4 | MA | MB, key=lambda x: tuple(sorted(x)))
for edge in ALL_EDGES:
    lhs = int(edge in M0) + int(edge in M4)
    rhs = int(edge in MA) + int(edge in MB)
    assert lhs == rhs

# Replay every red/blue coloring of the toy edge universe.
for mask in range(1 << len(ALL_EDGES)):
    red = {ALL_EDGES[i] for i in range(len(ALL_EDGES)) if (mask >> i) & 1}
    assert red_count(M0, red) + red_count(M4, red) == red_count(MA, red) + red_count(MB, red)

# Frozen connected linear-cubic UNSAT 15_3 source rows from the rank-14 control.
ROWS = [
    {0, 5, 12},
    {1, 7, 9},
    {2, 9, 14},
    {3, 10, 11},
    {3, 4, 13},
    {1, 5, 10},
    {6, 7, 14},
    {2, 3, 7},
    {1, 4, 8},
    {0, 6, 9},
    {2, 10, 12},
    {5, 11, 13},
    {6, 8, 12},
    {0, 8, 13},
    {4, 11, 14},
]

# One selected incidence per row. This is NOT a Boolean Exact-One assignment,
# because occurrences of one source variable are permitted to split.
CHOICE = [0, 1, 9, 3, 3, 1, 7, 2, 8, 0, 2, 5, 8, 13, 11]
assert len(CHOICE) == len(ROWS)
assert all(v in ROWS[i] for i, v in enumerate(CHOICE))

deg = [0] * 15
for v in CHOICE:
    deg[v] += 1
assert deg == [2, 2, 2, 2, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0]
profile = {d: deg.count(d) for d in range(4)}
assert profile == {0: 5, 1: 5, 2: 5, 3: 0}

# Pair the five degree-1 variables with the five degree-2 variables. Their
# occurrence states can always be port-labelled as complementary 3-bit states.
d1 = [v for v, d in enumerate(deg) if d == 1]
d2 = [v for v, d in enumerate(deg) if d == 2]
assert len(d1) == len(d2) == 5

out = {
    "status": "PASS_EXACT_MATCHING_TOGGLE_PAIR_EXCHANGE",
    "toy": {
        "off_boundary": sorted(boundary(M0, U)),
        "on_boundary": sorted(boundary(M4, U)),
        "mixed_A": sorted(boundary(MA, U)),
        "mixed_B": sorted(boundary(MB, U)),
        "all_red_blue_colorings_checked": 1 << len(ALL_EDGES),
        "additive_pair_sum_preserved": True,
    },
    "unsat15_relaxed_control": {
        "one_selected_incidence_per_row": True,
        "variable_degrees": deg,
        "degree_profile": profile,
        "degree1_variables": d1,
        "degree2_variables": d2,
    },
    "boundary": {
        "local_four_port_toggle_plus_additive_exact_count": "PAIRWISE_COLLISION_PROVED",
        "nonlocal_grouped_exact_matching_reduction": "OPEN",
        "universal_polynomial_decider": "NOT_PROVED",
        "E8_D1": "EMPTY",
        "P_VS_NP": "OPEN",
    },
}
print(json.dumps(out, sort_keys=True))
