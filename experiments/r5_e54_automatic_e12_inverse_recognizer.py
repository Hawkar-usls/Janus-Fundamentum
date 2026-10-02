#!/usr/bin/env python3
"""Exact controls for R5 E54 automatic E12 inverse recognition.

The reconstruction algorithm is driven only by the raw incidence structure:
  1. build the conflict graph on Exact-One variable-columns;
  2. count independent neighbor triples c(v);
  3. use c(v)=8 columns as D7 anchors;
  4. from each anchor recover 3 t-rows, 6 D1..D6 columns, 12 z/Z rows,
     10 L/P columns, and 6 boundary rows;
  5. split the 12 z/Z rows into two six-row sides via shared L/P columns;
  6. project each gadget to two boundary triples and build the boundary quotient.

On the frozen q=6 E12/E17 target this recovers six disjoint 17-column gadgets and
a 12x12 quotient with rank 12 and determinant -81=(-9)^2. The quotient has unique
rational solution (1/3)1, hence is Boolean-UNSAT.

Labels are used only to construct the fixture and to print diagnostics; reconstruction
uses incidence sets and graph structure only.

P_VS_NP remains OPEN.
"""

from itertools import combinations
from fractions import Fraction
from collections import Counter


def rx_fixture():
    q = 6
    source_sets = [tuple(sorted({i, (i + 1) % q, (i + 3) % q})) for i in range(q)]
    return q, source_sets


def build_target(q, source_sets):
    cols = []
    labels = []
    x = [f"x:{i}" for i in range(q)]
    xp = [f"xp:{i}" for i in range(q)]
    for j, C in enumerate(source_sets):
        a, b, c = C
        bx = [x[a], x[b], x[c]]
        bxp = [xp[a], xp[b], xp[c]]
        z = [f"g{j}:z{i}" for i in range(1, 7)]
        Z = [f"g{j}:Z{i}" for i in range(1, 7)]
        t = [f"g{j}:t{i}" for i in range(1, 4)]
        block = [
            {bx[0], z[0], z[3]}, {bx[1], z[1], z[4]}, {bx[2], z[2], z[5]},
            {z[0], z[1], z[2]}, {z[3], z[4], z[5]},
            {bxp[0], Z[0], Z[3]}, {bxp[1], Z[1], Z[4]}, {bxp[2], Z[2], Z[5]},
            {Z[0], Z[1], Z[2]}, {Z[3], Z[4], Z[5]},
            {z[1], z[5], t[0]}, {z[2], z[3], t[1]}, {z[0], z[4], t[2]},
            {Z[1], Z[5], t[1]}, {Z[2], Z[3], t[2]}, {Z[0], Z[4], t[0]},
            {t[0], t[1], t[2]},
        ]
        names = (
            [f"g{j}:L{i}" for i in range(1, 6)]
            + [f"g{j}:P{i}" for i in range(1, 6)]
            + [f"g{j}:D{i}" for i in range(1, 8)]
        )
        cols.extend(block)
        labels.extend(names)
    return labels, cols


def incidence(cols):
    rows = sorted(set().union(*cols))
    ri = {e: i for i, e in enumerate(rows)}
    col_rows = [{ri[e] for e in C} for C in cols]
    row_cols = [set() for _ in rows]
    for c, Rs in enumerate(col_rows):
        for r in Rs:
            row_cols[r].add(c)
    return rows, col_rows, row_cols


def conflict(col_rows):
    n = len(col_rows)
    adj = [set() for _ in range(n)]
    for i, j in combinations(range(n), 2):
        if col_rows[i] & col_rows[j]:
            adj[i].add(j)
            adj[j].add(i)
    return adj


def claw_count(adj, v):
    out = 0
    for T in combinations(sorted(adj[v]), 3):
        if all(b not in adj[a] for a, b in combinations(T, 2)):
            out += 1
    return out


def components(vertices, adjacency):
    unseen = set(vertices)
    out = []
    while unseen:
        s = next(iter(unseen))
        unseen.remove(s)
        comp = {s}
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adjacency[u]:
                if v in unseen:
                    unseen.remove(v)
                    comp.add(v)
                    stack.append(v)
        out.append(comp)
    return out


def reconstruct_one(anchor, col_rows, row_cols):
    # D7 touches exactly three t-rows.
    trows = set(col_rows[anchor])
    assert len(trows) == 3

    # Each t-row contains anchor plus two D1..D6 columns.
    dcols = set()
    for r in trows:
        assert len(row_cols[r]) == 3
        dcols |= row_cols[r] - {anchor}
    assert len(dcols) == 6

    # Each D1..D6 column has exactly one recovered t-row and two z/Z rows.
    zrows = set()
    for d in dcols:
        shared = col_rows[d] & trows
        assert len(shared) == 1
        zrows |= col_rows[d] - shared
    assert len(zrows) == 12

    # Each z/Z row has one D column and two L/P columns.
    lpcols = set()
    for r in zrows:
        assert len(row_cols[r] & dcols) == 1
        others = row_cols[r] - dcols
        assert len(others) == 2
        lpcols |= others
    assert len(lpcols) == 10

    gadget_cols = {anchor} | dcols | lpcols
    internal_rows = trows | zrows
    assert len(gadget_cols) == 17
    assert len(internal_rows) == 15

    boundary_rows = set()
    for c in lpcols:
        ext = col_rows[c] - internal_rows
        assert len(ext) in (0, 1)
        boundary_rows |= ext
    assert len(boundary_rows) == 6

    # Split z/Z rows into two sides using only co-incidence in L/P columns.
    zadj = {r: set() for r in zrows}
    for c in lpcols:
        zs = list(col_rows[c] & zrows)
        for a, b in combinations(zs, 2):
            zadj[a].add(b)
            zadj[b].add(a)
    zcomps = components(zrows, zadj)
    assert sorted(len(C) for C in zcomps) == [6, 6]

    sides = []
    for ZC in zcomps:
        side_lp = {c for c in lpcols if col_rows[c] & ZC}
        assert len(side_lp) == 5
        B = set()
        for c in side_lp:
            B |= col_rows[c] - internal_rows
        assert len(B) == 3
        sides.append(B)
    assert sides[0].isdisjoint(sides[1])
    assert sides[0] | sides[1] == boundary_rows

    return {
        "anchor": anchor,
        "gadget_cols": gadget_cols,
        "internal_rows": internal_rows,
        "boundary_rows": boundary_rows,
        "sides": sides,
    }


def rank_det_solve(M, rhs):
    A = [[Fraction(x) for x in row] + [Fraction(b)] for row, b in zip(M, rhs)]
    m = len(M)
    n = len(M[0])
    assert m == n
    det = Fraction(1)
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c]), None)
        if p is None:
            return r, Fraction(0), None
        if p != r:
            A[r], A[p] = A[p], A[r]
            det = -det
        z = A[r][c]
        det *= z
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n + 1)]
        pivots.append(c)
        r += 1
    sol = [Fraction(0)] * n
    for rr, c in enumerate(pivots):
        sol[c] = A[rr][-1]
    return r, det, sol


def main():
    q, source_sets = rx_fixture()
    labels, cols = build_target(q, source_sets)
    rows, col_rows, row_cols = incidence(cols)
    assert len(rows) == len(cols) == 102
    assert all(len(Rs) == 3 for Rs in col_rows)
    assert all(len(Cs) == 3 for Cs in row_cols)

    G = conflict(col_rows)
    assert all(len(G[v]) == 6 for v in range(102))
    cc = [claw_count(G, v) for v in range(102)]
    anchors = [v for v, c in enumerate(cc) if c == 8]
    assert len(anchors) == q

    gadgets = [reconstruct_one(a, col_rows, row_cols) for a in anchors]

    # The six recovered 17-column modules are disjoint and cover the whole target.
    seen_cols = set()
    for g in gadgets:
        assert not (seen_cols & g["gadget_cols"])
        seen_cols |= g["gadget_cols"]
    assert seen_cols == set(range(102))

    # Internal rows are gadget-local; the remaining rows are exactly the 2q global
    # boundary elements.
    all_internal = set().union(*(g["internal_rows"] for g in gadgets))
    assert len(all_internal) == 15 * q
    boundary = sorted(set(range(102)) - all_internal)
    assert len(boundary) == 2 * q

    # Each gadget projects to two independent boundary triples.
    side_triples = []
    for g in gadgets:
        side_triples.extend(g["sides"])
    assert len(side_triples) == 2 * q

    br = {r: i for i, r in enumerate(boundary)}
    Q = [[0] * (2 * q) for _ in boundary]
    for j, T in enumerate(side_triples):
        assert T <= set(boundary)
        for r in T:
            Q[br[r]][j] = 1

    assert all(sum(row) == 3 for row in Q)
    assert all(sum(Q[i][j] for i in range(2 * q)) == 3 for j in range(2 * q))

    rank, det, sol = rank_det_solve(Q, [1] * (2 * q))
    assert rank == 2 * q
    assert abs(det) == 81
    assert sol == [Fraction(1, 3)] * (2 * q)

    # Optional diagnostic: true fixture labels confirm anchors were D7, but no part
    # of reconstruction above used that fact.
    assert all(labels[a].endswith(":D7") for a in anchors)

    print("R5 E54 automatic E12 inverse recognizer: PASS")
    print(f"raw target: 102x102; anchors={len(anchors)}; reconstructed gadgets={len(gadgets)}")
    print("quotient: 12x12, rank=12, |det|=81=(-9)^2, unique solution=(1/3)1 -> UNSAT")


if __name__ == "__main__":
    main()
