#!/usr/bin/env python3
from fractions import Fraction
from collections import deque


def color3_cnf(nv, edges):
    clauses = []
    tags = []
    for v in range(nv):
        clauses.append(tuple(v * 3 + c + 1 for c in range(3)))
        tags.append(("ALO", v, None))
        for i in range(3):
            for j in range(i + 1, 3):
                clauses.append((-(v * 3 + i + 1), -(v * 3 + j + 1)))
                tags.append(("AMO", v, (i, j)))
    for u, v in edges:
        for c in range(3):
            clauses.append((-(u * 3 + c + 1), -(v * 3 + c + 1)))
            tags.append(("EDGE", (u, v), c))
    return clauses, tags


def signed_matrix(clauses, nvars):
    A = []
    for clause in clauses:
        row = [0] * nvars
        for lit in clause:
            row[abs(lit) - 1] = 1 if lit > 0 else -1
        A.append(row)
    return A


def rank_q(A):
    M = [[Fraction(x) for x in row] for row in A]
    if not M:
        return 0
    m, n = len(M), len(M[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c] != 0), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        p = M[r][c]
        M[r] = [x / p for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                q = M[i][c]
                M[i] = [a - q * b for a, b in zip(M[i], M[r])]
        r += 1
    return r


def explicit_dual_weights(nv, edges, tags):
    deg = [0] * nv
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    y = []
    for kind, a, b in tags:
        if kind == "ALO":
            y.append(2 + deg[a])
        elif kind in ("AMO", "EDGE"):
            y.append(1)
        else:
            raise AssertionError(kind)
    return y


def max_matching(clauses, variables, edges):
    adj = {c: [v for v in variables if (c, v) in edges] for c in clauses}
    mate_v, mate_c = {}, {}
    def aug(c, seen):
        for v in adj[c]:
            if v in seen:
                continue
            seen.add(v)
            if v not in mate_v or aug(mate_v[v], seen):
                old = mate_v.get(v)
                mate_v[v] = c
                mate_c[c] = v
                if old is not None and old != c:
                    mate_c.pop(old, None)
                return True
        return False
    for c in clauses:
        aug(c, set())
    return mate_c, mate_v


def dm_clause_core(clauses_lits, nvars):
    C = list(range(len(clauses_lits)))
    V = list(range(nvars))
    E = set()
    for ci, clause in enumerate(clauses_lits):
        for lit in clause:
            E.add((ci, abs(lit) - 1))
    mc, mv = max_matching(C, V, E)
    RC = {c for c in C if c not in mc}
    RV = set()
    q = deque(("c", c) for c in RC)
    while q:
        side, u = q.popleft()
        if side == "c":
            for v in V:
                if (u, v) in E and mc.get(u) != v and v not in RV:
                    RV.add(v)
                    q.append(("v", v))
        else:
            c = mv.get(u)
            if c is not None and c not in RC:
                RC.add(c)
                q.append(("c", c))
    return RC


def verify_graph(nv, edges):
    edges = [tuple(sorted(e)) for e in edges]
    assert len(set(edges)) == len(edges)
    clauses, tags = color3_cnf(nv, edges)
    nvars = 3 * nv
    A = signed_matrix(clauses, nvars)

    # Every local vertex block has the frozen 4-row pattern and rank 3.
    for v in range(nv):
        rows = []
        for row, tag in zip(A, tags):
            if tag[0] in ("ALO", "AMO") and tag[1] == v:
                rows.append(row[3*v:3*v+3])
        assert sorted(rows) == sorted([[1,1,1],[-1,-1,0],[-1,0,-1],[0,-1,-1]])
        assert rank_q(rows) == 3

    # Hence full column rank; explicit strictly positive dual balances every column.
    assert rank_q(A) == nvars
    y = explicit_dual_weights(nv, edges, tags)
    assert all(w > 0 for w in y)
    for j in range(nvars):
        assert sum(y[i] * A[i][j] for i in range(len(A))) == 0

    # Matching-autarky DM kernel is also the whole formula on finite controls.
    core = dm_clause_core(clauses, nvars)
    assert core == set(range(len(clauses)))


def main():
    graphs = [
        (1, []),
        (4, [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]),  # K4
        (5, [(0,1),(1,2),(2,3),(3,4),(4,0)]),        # C5
        (6, [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0),(0,3)]),
    ]
    for nv, edges in graphs:
        verify_graph(nv, edges)
    print("PASS every finite COLOR3 control has full column rank and explicit y>0 with A^T y=0")
    print("PASS local vertex clauses force the linear-autarky cone to {0}")
    print("PASS matching-autarky DM kernel is the whole COLOR3 formula on controls")


if __name__ == '__main__':
    main()
