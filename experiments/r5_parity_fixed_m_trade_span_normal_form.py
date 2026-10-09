#!/usr/bin/env python3
"""
Fixed-M trade-span normal-form replay.

Deterministic replay on the frozen 18x18 control used by the parity trade
frontier.  Verifies:
  * exact residual cubic graph R_M and its 3-edge matching blocks;
  * integer block-cut characterization of fixed-M trades;
  * a det=2 minor in the fixed-M trade matrix (non-TU firewall);
  * connected trade support is a column-matroid circuit;
  * the natural defect function has exactly the fixed-M trade unions as zeros
    on the control, but is neither submodular nor supermodular.

No third-party dependencies.
"""

from collections import Counter, deque
from itertools import combinations


def rank_q(mat):
    a = [list(map(float, row)) for row in mat]
    if not a:
        return 0
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if abs(a[i][c]) > 1e-9), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        q = a[r][c]
        a[r] = [x / q for x in a[r]]
        for i in range(m):
            if i != r and abs(a[i][c]) > 1e-9:
                q = a[i][c]
                a[i] = [a[i][j] - q * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def build_control(r=6):
    offsets = (0, 1, 3)
    b_edges = set()
    factors = []
    for off in offsets:
        f = []
        for i in range(r):
            e = (i, (i + off) % r)
            assert e not in b_edges
            b_edges.add(e)
            f.append(e)
        factors.append(f)
    b_edges = sorted(b_edges)
    eid = {e: i for i, e in enumerate(b_edges)}

    adj_l = {i: set() for i in range(r)}
    adj_r = {j: set() for j in range(r)}
    for i, j in b_edges:
        adj_l[i].add(j)
        adj_r[j].add(i)

    h = []
    for i in range(r):
        h.append(tuple(sorted(eid[(i, j)] for j in adj_l[i])))
    for j in range(r):
        h.append(tuple(sorted(eid[(i, j)] for i in adj_r[j])))
    for f in factors:
        f = sorted(f)
        for a in range(0, r, 3):
            h.append(tuple(sorted(eid[e] for e in f[a:a+3])))

    assert len(h) == len(b_edges) == 18
    return b_edges, h


def incidence(h, nclauses):
    inc = [[0] * len(h) for _ in range(nclauses)]
    for j, edge in enumerate(h):
        for c in edge:
            inc[c][j] = 1
    return inc


def fixed_m_residual(h, m_size=6):
    mset = set(range(m_size))
    residual = list(range(m_size, len(h)))
    rid = {e: i for i, e in enumerate(residual)}

    clause_inc = {c: [] for c in range(len(h))}
    for ei, edge in enumerate(h):
        for c in edge:
            clause_inc[c].append(ei)

    redges = []
    labels = []
    for c in range(len(h)):
        inside = [e for e in clause_inc[c] if e in mset]
        outside = [e for e in clause_inc[c] if e not in mset]
        assert len(inside) == 1 and len(outside) == 2
        redges.append((rid[outside[0]], rid[outside[1]]))
        labels.append(inside[0])

    assert len(set(tuple(sorted(e)) for e in redges)) == len(redges)

    adj = [set() for _ in residual]
    for u, v in redges:
        adj[u].add(v)
        adj[v].add(u)
    assert set(map(len, adj)) == {3}

    blocks = {m: [] for m in range(m_size)}
    for i, m in enumerate(labels):
        blocks[m].append(i)

    for es in blocks.values():
        assert len(es) == 3
        verts = []
        for e in es:
            verts += list(redges[e])
        assert len(set(verts)) == 6  # each block is a 3-edge matching

    return residual, redges, labels, blocks, adj


def independent(redges, s):
    s = set(s)
    return all(not (u in s and v in s) for u, v in redges)


def coherent_blocks(redges, blocks, s):
    s = set(s)
    p = []
    for m, es in blocks.items():
        crossing = [((redges[e][0] in s) ^ (redges[e][1] in s)) for e in es]
        if all(crossing):
            p.append(m)
        elif any(crossing):
            return None
    return tuple(p)


def enumerate_fixed_m_trades(redges, blocks, nres):
    out = []
    for mask in range(1 << nres):
        s = tuple(i for i in range(nres) if (mask >> i) & 1)
        p = coherent_blocks(redges, blocks, s)
        if p is not None and independent(redges, s):
            assert len(s) == len(p)
            out.append((s, p))
    return out


def connected_bipartite_trade_graph(redges, labels, s, p):
    s, p = set(s), set(p)
    # Trade graph vertices are selected residual vars and removed M blocks.
    adj = {("S", u): set() for u in s}
    adj.update({("P", m): set() for m in p})

    for ei, (u, v) in enumerate(redges):
        m = labels[ei]
        if m not in p:
            continue
        chosen = [x for x in (u, v) if x in s]
        assert len(chosen) == 1
        x = chosen[0]
        adj[("S", x)].add(("P", m))
        adj[("P", m)].add(("S", x))

    assert all(len(nb) == 3 for nb in adj.values())
    root = next(iter(adj))
    seen = {root}
    q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == len(adj)


def trade_matrix(redges, labels, blocks, nres):
    # Variables are residual y_u.  For each M-block choose its first edge as
    # reference and impose equality of endpoint sums with the other two.
    rows = []
    for m, es in blocks.items():
        e0 = es[0]
        u0, v0 = redges[e0]
        for e in es[1:]:
            u, v = redges[e]
            row = [0] * nres
            row[u0] += 1
            row[v0] += 1
            row[u] -= 1
            row[v] -= 1
            rows.append(row)
    return rows


def find_det2_minor(mat):
    nr, nc = len(mat), len(mat[0])
    for r1, r2 in combinations(range(nr), 2):
        for c1, c2 in combinations(range(nc), 2):
            det = mat[r1][c1] * mat[r2][c2] - mat[r1][c2] * mat[r2][c1]
            if abs(det) == 2:
                return r1, r2, c1, c2, (
                    (mat[r1][c1], mat[r1][c2]),
                    (mat[r2][c1], mat[r2][c2]),
                )
    return None


def psi(redges, blocks, s):
    s = set(s)
    touched = 0
    for es in blocks.values():
        verts = set()
        for e in es:
            verts.update(redges[e])
        if verts & s:
            touched += 1
    internal = sum(u in s and v in s for u, v in redges)
    return 3 * touched - 3 * len(s) + 2 * internal


def check_defect_firewall(redges, blocks, nres, trade_sets):
    zeros = set()
    values = {}
    for mask in range(1 << nres):
        s = frozenset(i for i in range(nres) if (mask >> i) & 1)
        val = psi(redges, blocks, s)
        assert val >= 0
        values[s] = val
        if val == 0:
            zeros.add(s)

    expected = {frozenset(s) for s, _ in trade_sets}
    assert zeros == expected

    sub_cex = None
    super_cex = None
    sets = list(values)
    for a in sets:
        for b in sets:
            lhs = values[a] + values[b]
            rhs = values[a | b] + values[a & b]
            if sub_cex is None and lhs < rhs:
                sub_cex = (a, b, lhs, rhs)
            if super_cex is None and lhs > rhs:
                super_cex = (a, b, lhs, rhs)
            if sub_cex and super_cex:
                return sub_cex, super_cex
    raise AssertionError("expected both sub/supermodularity counterexamples")


def circuit_check(h, trade_s, trade_p, m_size=6):
    # Columns in original A: removed M variables plus selected residual variables.
    cols = list(trade_p) + [m_size + u for u in trade_s]
    A = incidence(h, len(h))
    sub = [[row[j] for j in cols] for row in A]
    r = rank_q(sub)
    assert r == len(cols) - 1
    for drop in range(len(cols)):
        sub2 = [[row[j] for k, j in enumerate(cols) if k != drop] for row in A]
        assert rank_q(sub2) == len(cols) - 1
    return len(cols), r


def main():
    _, h = build_control()
    residual, redges, labels, blocks, adj = fixed_m_residual(h)

    trades = enumerate_fixed_m_trades(redges, blocks, len(residual))
    nonempty = [(s, p) for s, p in trades if s]
    assert len(trades) == 5
    assert len(nonempty) == 4

    connected = [(s, p) for s, p in nonempty if connected_bipartite_trade_graph(redges, labels, s, p)]
    assert len(connected) == 4
    assert Counter(len(s) for s, _ in connected) == Counter({6: 2, 3: 2})

    D = trade_matrix(redges, labels, blocks, len(residual))
    assert len(D) == 12 and len(D[0]) == 12
    det2 = find_det2_minor(D)
    assert det2 is not None

    # Every connected trade in this control is a real column-matroid circuit.
    circ = [circuit_check(h, s, p) for s, p in connected]

    sub_cex, super_cex = check_defect_firewall(redges, blocks, len(residual), trades)

    print("FIXED_M_RESIDUAL_VERTICES =", len(residual))
    print("FIXED_M_RESIDUAL_EDGES =", len(redges))
    print("R_M_SIMPLE_CUBIC = PASS")
    print("BLOCKS =", len(blocks), "each a 3-edge matching")
    print("FIXED_M_TRADE_UNIONS =", len(trades))
    print("NONEMPTY_CONNECTED_TRADES =", len(connected))
    print("CONNECTED_TRADE_VOLUMES =", dict(sorted(Counter(len(s) for s, _ in connected).items())))
    print("CONNECTED_TRADE_COLUMN_CIRCUIT = PASS")
    print("CIRCUIT_RANK_PAIRS =", circ)
    print("FIXED_M_TRADE_MATRIX_RANK =", rank_q(D))
    print("DET2_MINOR =", det2)
    print("FIXED_M_TRADE_MATRIX_TU = FAIL")
    print("PSI_ZERO_SETS_EXACTLY_TRADE_UNIONS = PASS")
    print("PSI_SUBMODULAR = FAIL", sub_cex)
    print("PSI_SUPERMODULAR = FAIL", super_cex)
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
