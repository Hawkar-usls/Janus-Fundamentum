#!/usr/bin/env python3
"""Exact replay for v7.8 three-v7.7-wire source-open composition barrier."""

from collections import Counter
from itertools import combinations, permutations

D = range(3)
S3 = list(permutations(D))
ID = (0, 1, 2)
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
# v7.7 exact h_XY = g_Y^{-1} g_X table.
H = {
    (0, 1): (0, 1, 2),
    (0, 2): (2, 0, 1),
    (1, 0): (2, 1, 0),
    (1, 2): (2, 1, 0),
    (2, 0): (0, 2, 1),
    (2, 1): (0, 1, 2),
}
FREE = {"X": (0, 1), "Y": (1, 2)}
TERMINALS = [(w, r) for w in range(3) for r in "XY"]
FULL_ORBIT = frozenset((a, b) for a in D for b in D)
FULL_GAIN = frozenset(S3)


def compose(p, q):
    """Permutation p o q."""
    return tuple(p[q[i]] for i in D)


def inverse(p):
    out = [0, 0, 0]
    for i, v in enumerate(p):
        out[v] = i
    return tuple(out)


def wire_states(fix_role=None):
    """Exact 36 absolute states of one rigid v7.7 wire; 6 after global-gauge fix."""
    out = []
    for tx in D:
        for ty in D:
            if tx == ty:
                continue
            h = H[(tx, ty)]
            for gx in S3:
                # h = gy^{-1} gx => gy = gx h^{-1}
                gy = compose(gx, inverse(h))
                if fix_role == "X" and gx != ID:
                    continue
                if fix_role == "Y" and gy != ID:
                    continue
                colors = {}
                for role in "XY":
                    tau = tx if role == "X" else ty
                    g = gx if role == "X" else gy
                    for port in FREE[role]:
                        colors[(role, port)] = g[REPS[tau][port]]
                out.append((tx, ty, gx, gy, colors))
    return out


ALL_STATES = wire_states()
FIXED_STATES = {role: wire_states(role) for role in "XY"}
assert len(ALL_STATES) == 36
assert len(FIXED_STATES["X"]) == len(FIXED_STATES["Y"]) == 6

# Each v7.7 wire's two open H paths, compressed to edges between its dangling ports.
INTERNAL_PATH_EDGES = [
    ((w, "X", 0), (w, "Y", 1)) for w in range(3)
] + [
    ((w, "X", 1), (w, "Y", 2)) for w in range(3)
]


def perfect_matchings(items):
    """Pair all hidden dangling vertices; forbid a splice inside one terminal C4."""
    if not items:
        yield ()
        return
    a = items[0]
    for i in range(1, len(items)):
        b = items[i]
        if a[:2] == b[:2]:
            continue
        rest = items[1:i] + items[i + 1 :]
        for matching in perfect_matchings(rest):
            yield ((a, b),) + matching


def two_path_topology(splices, outer_vertices):
    """Exactly two open paths, no hidden H-cycle, and precisely four named leaves."""
    vertices = {
        (w, role, port)
        for w in range(3)
        for role in "XY"
        for port in FREE[role]
    }
    adj = {v: [] for v in vertices}
    for a, b in INTERNAL_PATH_EDGES + list(splices):
        adj[a].append(b)
        adj[b].append(a)
    if any(len(adj[v]) > 2 for v in vertices):
        return False
    leaves = {v for v in vertices if len(adj[v]) == 1}
    if leaves != set(outer_vertices):
        return False

    seen = set()
    components = []
    for v in vertices:
        if v in seen:
            continue
        stack = [v]
        cc = []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            cc.append(x)
            stack.extend(y for y in adj[x] if y not in seen)
        components.append(cc)
    return len(components) == 2 and all(
        sum(1 for v in cc if len(adj[v]) == 1) == 2 for cc in components
    )


def terminal_tau_gauge(state, role):
    return (state[0], state[2]) if role == "X" else (state[1], state[3])


def exact_boundary_relation(splices, terminal_a, terminal_b):
    """Return {(tauA,tauB): {h_AB}} with g_A fixed to identity."""
    wa, ra = terminal_a
    state_lists = [ALL_STATES, ALL_STATES, ALL_STATES]
    state_lists[wa] = FIXED_STATES[ra]
    relation = {}

    for s0 in state_lists[0]:
        for s1 in state_lists[1]:
            for s2 in state_lists[2]:
                states = (s0, s1, s2)
                if any(
                    states[e[0]][4][(e[1], e[2])]
                    == states[f[0]][4][(f[1], f[2])]
                    for e, f in splices
                ):
                    continue

                ta, ga = terminal_tau_gauge(states[terminal_a[0]], terminal_a[1])
                tb, gb = terminal_tau_gauge(states[terminal_b[0]], terminal_b[1])
                hab = compose(inverse(gb), ga)
                relation.setdefault((ta, tb), set()).add(hab)
    return relation


def main():
    topology_count = 0
    same_wire_valid = 0
    cross_pair_counts = Counter()
    triple_size_counts = Counter()
    orbit_masks = Counter()
    full_universal = 0

    for terminal_a, terminal_b in combinations(TERMINALS, 2):
        hidden = [
            (w, role, port)
            for w, role in TERMINALS
            if (w, role) not in (terminal_a, terminal_b)
            for port in FREE[role]
        ]
        outer = [
            (terminal_a[0], terminal_a[1], p) for p in FREE[terminal_a[1]]
        ] + [
            (terminal_b[0], terminal_b[1], p) for p in FREE[terminal_b[1]]
        ]

        valid_here = 0
        for splices in perfect_matchings(tuple(hidden)):
            if not two_path_topology(splices, outer):
                continue
            valid_here += 1
            topology_count += 1
            relation = exact_boundary_relation(splices, terminal_a, terminal_b)
            mask = frozenset(relation)
            orbit_masks[mask] += 1
            assert mask == FULL_ORBIT

            size = sum(len(gains) for gains in relation.values())
            triple_size_counts[size] += 1
            if size == 54:
                assert all(frozenset(gains) == FULL_GAIN for gains in relation.values())
                full_universal += 1

        if terminal_a[0] == terminal_b[0]:
            same_wire_valid += valid_here
            assert valid_here == 0
        else:
            cross_pair_counts[(terminal_a, terminal_b)] = valid_here
            assert valid_here == 40

    assert len(cross_pair_counts) == 12
    assert topology_count == 480
    assert same_wire_valid == 0
    assert len(orbit_masks) == 1
    assert orbit_masks[FULL_ORBIT] == 480
    assert triple_size_counts == Counter({54: 288, 50: 96, 46: 48, 52: 48})
    assert full_universal == 288

    print("PASS: external terminal pairs checked = 15")
    print("PASS: same-wire external pairs admit no two-path topology")
    print("PASS: 12 cross-wire pairs x 40 topologies = 480 source-open compositions")
    print("PASS: every topology has FULL_3x3 terminal orbit projection")
    print("PASS: exact gain-refined sizes =", dict(sorted(triple_size_counts.items())))
    print("PASS: fully gauge-transparent universal relations = 288/480")
    print("VERDICT: THREE_V7_7_WIRE_WHOLE_TERMINAL_COMPOSITION_ERASES_ORBIT_LOGIC")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
