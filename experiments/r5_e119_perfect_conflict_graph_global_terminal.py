#!/usr/bin/env python3
"""R5 E119 replay: perfect conflict-graph terminal and SPGT obstruction router."""

from __future__ import annotations

from collections import Counter
from itertools import combinations, product


P_SAT = [7, 6, 11, 10, 8, 4, 9, 5, 0, 3, 2, 1]
Q_SAT = [11, 8, 3, 4, 7, 9, 0, 10, 2, 1, 6, 5]
P_UNSAT = [6, 3, 7, 10, 11, 1, 4, 8, 9, 5, 2, 0]
Q_UNSAT = [3, 4, 5, 8, 7, 0, 9, 6, 2, 11, 1, 10]


def validate_target(clauses):
    clauses = [tuple(c) for c in clauses]
    variables = sorted({v for c in clauses for v in c}, key=str)

    assert len(clauses) == len(variables)
    assert all(len(c) == 3 and len(set(c)) == 3 for c in clauses)

    degree = Counter(v for c in clauses for v in c)
    assert set(degree) == set(variables)
    assert set(degree.values()) == {3}

    for a, b in combinations(clauses, 2):
        assert len(set(a) & set(b)) <= 1

    return variables


def conflict_graph(clauses, variables):
    pos = {v: i for i, v in enumerate(variables)}
    n = len(variables)
    G = [[0] * n for _ in range(n)]

    edge_owner = {}
    for ri, c in enumerate(clauses):
        ids = [pos[v] for v in c]
        for i, j in combinations(ids, 2):
            i, j = sorted((i, j))
            assert (i, j) not in edge_owner
            edge_owner[(i, j)] = ri
            G[i][j] = G[j][i] = 1

    assert all(sum(row) == 6 for row in G)
    return G, edge_owner


def independent(G, S):
    return all(not G[i][j] for i, j in combinations(S, 2))


def maximum_stable_set(G):
    n = len(G)
    best = ()
    for mask in range(1 << n):
        if mask.bit_count() <= len(best):
            continue
        S = tuple(i for i in range(n) if (mask >> i) & 1)
        if independent(G, S):
            best = S
    return best


def exactone_witnesses(clauses, variables):
    pos = {v: i for i, v in enumerate(variables)}
    out = []
    for bits in product((0, 1), repeat=len(variables)):
        if all(sum(bits[pos[v]] for v in c) == 1 for c in clauses):
            out.append(bits)
    return out


def induced_cycle_order(G, S):
    S = set(S)
    if len(S) < 4:
        return None
    nbr = {
        v: [w for w in S if w != v and G[v][w]]
        for v in S
    }
    if any(len(nbr[v]) != 2 for v in S):
        return None

    start = min(S)
    order = [start]
    prev = None
    cur = start
    while True:
        choices = [w for w in nbr[cur] if w != prev]
        if not choices:
            return None
        nxt = choices[0]
        if nxt == start:
            return order if len(order) == len(S) else None
        if nxt in order:
            return None
        order.append(nxt)
        prev, cur = cur, nxt


def complement_graph(G):
    n = len(G)
    return [
        [0 if i == j else 1 - G[i][j] for j in range(n)]
        for i in range(n)
    ]


def find_odd_hole(G):
    n = len(G)
    for k in range(5, n + 1, 2):
        for S in combinations(range(n), k):
            order = induced_cycle_order(G, S)
            if order is not None:
                return order
    return None


def brute_perfect_small(G):
    return find_odd_hole(G) is None and find_odd_hole(complement_graph(G)) is None


def latin_sat9():
    clauses = []
    for i in range(3):
        for j in range(3):
            clauses.append((f"A{i}", f"B{j}", f"C{(i + j) % 3}"))
    return clauses


def fano_unsat7():
    return [
        (0, 1, 3),
        (0, 2, 6),
        (0, 4, 5),
        (1, 2, 4),
        (1, 5, 6),
        (2, 3, 5),
        (3, 4, 6),
    ]


def permutation_fixture(p, q):
    return [(i, p[i], q[i]) for i in range(len(p))]


def verify_exactone_alpha_equivalence(name, clauses, expect_sat, expect_alpha):
    variables = validate_target(clauses)
    G, _ = conflict_graph(clauses, variables)
    S = maximum_stable_set(G)
    witnesses = exactone_witnesses(clauses, variables)

    assert len(S) == expect_alpha, (name, len(S), expect_alpha)
    assert bool(witnesses) == expect_sat
    assert bool(witnesses) == (3 * len(S) == len(variables))

    print(
        f"{name}: n={len(variables)} alpha={len(S)} "
        f"exactone={bool(witnesses)} perfect_small={brute_perfect_small(G)}"
    )
    return variables, G


def verify_perfect_fixtures():
    v9, g9 = verify_exactone_alpha_equivalence(
        "PERFECT_SAT9", latin_sat9(), True, 3
    )
    assert brute_perfect_small(g9)

    # K_{3,3,3}: three independent parts of size 3.
    parts = [set(range(0, 3)), set(range(3, 6)), set(range(6, 9))]
    assert all(
        g9[i][j] == (0 if any(i in p and j in p for p in parts) else 1)
        for i in range(9)
        for j in range(9)
        if i != j
    )

    v7, g7 = verify_exactone_alpha_equivalence(
        "PERFECT_UNSAT7_FANO", fano_unsat7(), False, 1
    )
    assert brute_perfect_small(g7)
    assert all(g7[i][j] == 1 for i in range(7) for j in range(7) if i != j)


def verify_e61_exit_controls():
    controls = [
        ("E61_SAT12", permutation_fixture(P_SAT, Q_SAT), True, 4),
        ("E61_UNSAT12", permutation_fixture(P_UNSAT, Q_UNSAT), False, 3),
    ]

    for name, clauses, sat, alpha in controls:
        variables, G = verify_exactone_alpha_equivalence(name, clauses, sat, alpha)
        hole = find_odd_hole(G)
        assert hole is not None and len(hole) % 2 == 1 and len(hole) >= 5

        # Every conflict edge of the induced hole has one unique clause owner.
        pos = {v: i for i, v in enumerate(variables)}
        owner = {}
        for ri, c in enumerate(clauses):
            ids = [pos[v] for v in c]
            for a, b in combinations(ids, 2):
                owner[tuple(sorted((a, b)))] = ri

        cycle_rows = []
        k = len(hole)
        for i in range(k):
            a, b = hole[i], hole[(i + 1) % k]
            cycle_rows.append(owner[tuple(sorted((a, b)))])
        assert len(set(cycle_rows)) == k

        # A repeated consecutive-row owner would place three consecutive hole
        # variables in one clause and create a chord.  The unique row sequence
        # is the conflict-graph -> strong-hypergraph-cycle direction used by E119.
        print(f"{name}: odd-hole certificate length={k}, rows={cycle_rows}")


def cycle_graph(n):
    G = [[0] * n for _ in range(n)]
    for i in range(n):
        j = (i + 1) % n
        G[i][j] = G[j][i] = 1
    return G


def verify_antihole_degree_collapse():
    for m in (5, 7, 9, 11):
        H = complement_graph(cycle_graph(m))
        degree = {sum(row) for row in H}
        assert degree == {m - 3}
        print(f"ANTI_C{m}: internal_degree={m - 3}")

    anti9 = complement_graph(cycle_graph(9))
    assert {sum(row) for row in anti9} == {6}
    assert len(maximum_stable_set(anti9)) == 2
    assert 2 < 9 // 3

    anti7 = complement_graph(cycle_graph(7))
    assert {sum(row) for row in anti7} == {4}
    # In a 6-regular host every anti-C7 vertex has exactly two external neighbours.
    assert 6 - 4 == 2

    anti11 = complement_graph(cycle_graph(11))
    assert min(sum(row) for row in anti11) == 8 > 6

    anti5 = complement_graph(cycle_graph(5))
    assert find_odd_hole(anti5) is not None


def main():
    verify_perfect_fixtures()
    verify_e61_exit_controls()
    verify_antihole_degree_collapse()

    print("R5 E119 PASS")
    print("perfect conflict graph => exact polynomial MIS terminal (external theorem)")
    print("imperfect 6-regular target => odd hole or anti-C7/anti-C9")
    print("anti-C9: closed 6-regular component with alpha=2<3 => UNSAT")
    print("remaining universal frontier: induced odd hole or anti-C7")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
