#!/usr/bin/env python3
"""Exact replay for v7.6 C4 cycle-holonomy EQ/NEQ expressive jump."""

from collections import Counter, defaultdict
from itertools import combinations, permutations, product

D = range(3)
S3 = list(permutations(D))
PID = {p: i for i, p in enumerate(S3)}
IDENTITY = (0, 1, 2)
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
PORT_PAIRS = [(p, q) for p in range(4) for q in range(4)]
PAIR_INDEX = {(a, b): 3 * a + b for a in D for b in D}
ALL_REL = (1 << 9) - 1
EQ = sum(1 << PAIR_INDEX[(a, a)] for a in D)
NEQ = ALL_REL ^ EQ
FULL = (2, 2, 2, 2)

# Explicit relaxed NEQ cycle.
NEQ_B = ((0, 0), (1, 0))                 # X -> Z
NEQ_C = ((1, 0), (1, 1))                 # Z -> Y
NEQ_A = ((0, 0), (1, 1), (2, 3), (3, 2)) # Y -> X

# Fully source-realized EQ control.
EQ_B = ((0, 0), (0, 1), (1, 2), (2, 0))
EQ_C = ((1, 0), (2, 2), (3, 0), (3, 1))
EQ_A = ((1, 1), (2, 3), (3, 2), (3, 3))


def addv(a, b):
    return tuple(x + y for x, y in zip(a, b))


def valid_bundle(bundle):
    left = Counter(p for p, _ in bundle)
    right = Counter(q for _, q in bundle)
    return max(left.values(), default=0) <= 2 and max(right.values(), default=0) <= 2


def usage(bundle, side):
    k = 0 if side == "left" else 1
    return tuple(sum(1 for e in bundle if e[k] == i) for i in range(4))


def direct_cycle_counts(B, C, A):
    """Fix g_X=id and count extensions over tau_Z,g_Z,g_Y."""
    counts = {}
    gx = IDENTITY
    for x, y in product(D, D):
        n = 0
        for z in D:
            for gz in S3:
                for gy in S3:
                    if not all(gx[REPS[x][p]] != gz[REPS[z][q]] for p, q in B):
                        continue
                    if not all(gz[REPS[z][p]] != gy[REPS[y][q]] for p, q in C):
                        continue
                    if not all(gy[REPS[y][p]] != gx[REPS[x][q]] for p, q in A):
                        continue
                    n += 1
        counts[(x, y)] = n
    return counts


def check_hamiltonian_12cycle(B, C, A):
    edges = []
    for p, q in B:
        edges.append((("X", p), ("Z", q)))
    for p, q in C:
        edges.append((("Z", p), ("Y", q)))
    for p, q in A:
        edges.append((("Y", p), ("X", q)))
    assert len(edges) == 12
    assert len(set(tuple(sorted(e)) for e in edges)) == 12

    degree = Counter(v for e in edges for v in e)
    assert len(degree) == 12
    assert set(degree.values()) == {2}

    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    start = ("X", 0)
    seen = {start}
    stack = [start]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    assert len(seen) == 12

    # Replay the canonical traversal frozen in the theorem artifact.
    cycle = [start]
    prev = None
    cur = start
    while True:
        ns = adj[cur]
        nxt = ns[0] if ns[0] != prev else ns[1]
        if nxt == start:
            cycle.append(start)
            break
        cycle.append(nxt)
        prev, cur = cur, nxt
    expected = [
        ("X",0),("Z",0),("X",2),("Y",3),("X",3),("Y",2),
        ("Z",2),("X",1),("Y",1),("Z",3),("Y",0),("Z",1),("X",0)
    ]
    assert cycle == expected or cycle == [expected[0]] + list(reversed(expected[1:-1])) + [expected[0]]


# S3 bitset algebra.
COMP_INDEX = [[0] * 6 for _ in range(6)]
INV_INDEX = [0] * 6
for i, p in enumerate(S3):
    inv = tuple(p.index(k) for k in D)
    INV_INDEX[i] = PID[inv]
    for j, q in enumerate(S3):
        COMP_INDEX[i][j] = PID[tuple(p[q[k]] for k in D)]

COMPOSE_BITS = [[0] * 64 for _ in range(64)]
for left in range(64):
    for right in range(64):
        out = 0
        for i in range(6):
            if not (left >> i) & 1:
                continue
            for j in range(6):
                if (right >> j) & 1:
                    out |= 1 << COMP_INDEX[i][j]
        COMPOSE_BITS[left][right] = out

INV_BITS = [0] * 64
for bits in range(64):
    out = 0
    for i in range(6):
        if (bits >> i) & 1:
            out |= 1 << INV_INDEX[i]
    INV_BITS[bits] = out


def gain_bits(a, b, bundle):
    bits = 0
    for i, h in enumerate(S3):
        if all(h[REPS[a][p]] != REPS[b][q] for p, q in bundle):
            bits |= 1 << i
    return bits


def gain_table(bundle):
    return tuple(gain_bits(a, b, bundle) for a in D for b in D)


def compose_gain_tables(gB, gC):
    out = []
    for x in D:
        for y in D:
            bits = 0
            for z in D:
                bits |= COMPOSE_BITS[gC[3 * z + y]][gB[3 * x + z]]
            out.append(bits)
    return tuple(out)


def cycle_terminal_mask(path_gain, A_gain):
    out = 0
    for x in D:
        for y in D:
            # A is Y->X. Need h_YX = inverse(h_XY).
            if A_gain[3 * y + x] & INV_BITS[path_gain[3 * x + y]]:
                out |= 1 << PAIR_INDEX[(x, y)]
    return out


def enumerate_gain_types():
    raw_count = 0
    gain_types = {}
    for r in range(1, 9):
        for bundle in combinations(PORT_PAIRS, r):
            if not valid_bundle(bundle):
                continue
            raw_count += 1
            ld = usage(bundle, "left")
            rd = usage(bundle, "right")
            gt = gain_table(bundle)
            gain_types.setdefault((ld, rd, gt), bundle)
    assert raw_count == 7342
    assert len(gain_types) == 6511
    return [(ld, rd, gt, b) for (ld, rd, gt), b in gain_types.items()]


def reusable_triangle_gate(types):
    by_left_exact = defaultdict(list)
    for t in types:
        by_left_exact[t[0]].append(t)

    raw_BC_type_pairs = 0
    path_states = {}
    for B in types:
        need_left_C = tuple(2 - x for x in B[1])
        for C in by_left_exact.get(need_left_C, ()):
            raw_BC_type_pairs += 1
            path_gain = compose_gain_tables(B[2], C[2])
            # Z is saturated by construction. Only terminal usage and exact
            # transfer gain table are relevant to closing the triangle.
            path_states.setdefault((B[0], C[1], path_gain), (B[3], C[3]))

    assert raw_BC_type_pairs == 358416
    assert len(path_states) == 46114

    fit_cache = {}

    def closers(cap_left, cap_right):
        key = (cap_left, cap_right)
        if key not in fit_cache:
            fit_cache[key] = [
                t for t in types
                if all(t[0][i] <= cap_left[i] for i in range(4))
                and all(t[1][i] <= cap_right[i] for i in range(4))
            ]
        return fit_cache[key]

    tested = 0
    for (used_X, used_Y, path_gain), _witness in path_states.items():
        cap_A_left = tuple(2 - x for x in used_Y)
        cap_A_right = tuple(2 - x for x in used_X)
        for A in closers(cap_A_left, cap_A_right):
            # X uses B.left + A.right. Y uses C.right + A.left.
            # Require at least two external H half-edges at each terminal.
            if sum(used_X) + sum(A[1]) > 6:
                continue
            if sum(used_Y) + sum(A[0]) > 6:
                continue
            tested += 1
            terminal = cycle_terminal_mask(path_gain, A[2])
            assert terminal != EQ
            assert terminal != NEQ

    assert tested == 771960
    return raw_BC_type_pairs, len(path_states), tested


def main():
    # Explicit cyclic NEQ expressive jump.
    neq_counts = direct_cycle_counts(NEQ_B, NEQ_C, NEQ_A)
    expected_neq = {
        (0,0):0,(0,1):3,(0,2):3,
        (1,0):3,(1,1):0,(1,2):3,
        (2,0):3,(2,1):3,(2,2):0,
    }
    assert neq_counts == expected_neq
    assert addv(usage(NEQ_B, "left"), usage(NEQ_A, "right")) == (2,2,1,1)
    assert addv(usage(NEQ_C, "right"), usage(NEQ_A, "left")) == (2,2,1,1)
    assert addv(usage(NEQ_B, "right"), usage(NEQ_C, "left")) == (2,2,0,0)

    # Fully source-realized EQ control.
    eq_counts = direct_cycle_counts(EQ_B, EQ_C, EQ_A)
    expected_eq = {
        (0,0):1,(0,1):0,(0,2):0,
        (1,0):0,(1,1):1,(1,2):0,
        (2,0):0,(2,1):0,(2,2):1,
    }
    assert eq_counts == expected_eq
    assert addv(usage(EQ_B, "left"), usage(EQ_A, "right")) == FULL
    assert addv(usage(EQ_C, "right"), usage(EQ_A, "left")) == FULL
    assert addv(usage(EQ_B, "right"), usage(EQ_C, "left")) == FULL
    check_hamiltonian_12cycle(EQ_B, EQ_C, EQ_A)
    assert sum(eq_counts.values()) * 6 == 18

    # Exhaustive reusable binary triangle gate.
    types = enumerate_gain_types()
    bc, paths, tested = reusable_triangle_gate(types)

    print("PASS: relaxed three-C4 cycle terminal relation = NEQ_3 exactly")
    print("PASS: NEQ fixed-root extension counts = [[0,3,3],[3,0,3],[3,3,0]]")
    print("PASS: true 12-vertex smooth-C4 Hamiltonian control realizes EQ_3 exactly")
    print("PASS: source EQ control has 18 proper 3-colourings")
    print("PASS: valid raw bundles = 7342; exact gain-state bundle types = 6511")
    print("PASS: saturated-Z ordered B/C gain-type pairs =", bc)
    print("PASS: distinct saturated-Z path gain states =", paths)
    print("PASS: reusable capacity-compatible triangle closings tested =", tested)
    print("PASS: no reusable saturated-internal three-C4 EQ_3/NEQ_3 wire found in the full gain-state closure")
    print("VERDICT: CYCLE_HOLONOMY_ADDS_EXPRESSIVE_POWER; FOURPLUS_COMPONENT_SOURCE_COMPLETION_REQUIRED")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
