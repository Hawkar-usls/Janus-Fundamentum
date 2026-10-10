#!/usr/bin/env python3
"""Finite exact controls for the actual-row-basis rank-3 matching router.

The arbitrary-n theorem is in the paired research note.  This script is only a
regression/falsifier: it uses exact Fraction arithmetic and tiny exhaustive
controls; it does not claim that its small recursive matching routine is the
production polynomial matching implementation.
"""
from fractions import Fraction
from itertools import combinations


def rank_q(M):
    if not M:
        return 0
    X = [[Fraction(v) for v in row] for row in M]
    m, n = len(X), len(X[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if X[i][c]), None)
        if p is None:
            continue
        X[r], X[p] = X[p], X[r]
        q = X[r][c]
        X[r] = [z / q for z in X[r]]
        for i in range(m):
            if i != r and X[i][c]:
                q = X[i][c]
                X[i] = [X[i][j] - q * X[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def actual_row_basis(A):
    basis = []
    inds = []
    rr = 0
    for i, row in enumerate(A):
        nr = rank_q(basis + [row])
        if nr > rr:
            basis.append(row[:])
            inds.append(i)
            rr = nr
    assert rr == rank_q(A)
    return inds, basis


def classify(B, n):
    supports = []
    C = {1: [], 2: [], 3: []}
    for j in range(n):
        s = tuple(i for i, row in enumerate(B) if row[j])
        assert 1 <= len(s) <= 3
        supports.append(s)
        C[len(s)].append(j)
    return supports, C


def saturating_matching(vertices, edges, mandatory):
    """Tiny exact regression search for a matching saturating mandatory.

    The theorem uses ordinary polynomial general-graph matching.  This routine
    is intentionally only for <=15-vertex finite controls.
    """
    inc = {v: [] for v in vertices}
    for ei, (u, v) in enumerate(edges):
        inc[u].append((ei, v))
        inc[v].append((ei, u))

    mandatory = set(mandatory)

    def rec(used, chosen):
        todo = [v for v in mandatory if v not in used]
        if not todo:
            return chosen[:]
        # Fail-first mandatory vertex.
        v = min(todo, key=lambda z: sum(1 for _, w in inc[z] if w not in used))
        for ei, w in inc[v]:
            if v in used or w in used:
                continue
            used.add(v); used.add(w); chosen.append(ei)
            out = rec(used, chosen)
            if out is not None:
                return out
            chosen.pop(); used.remove(v); used.remove(w)
        return None

    return rec(set(), [])


def router(A):
    n = len(A)
    inds, B = actual_row_basis(A)
    r = len(B)
    k = n - r
    supports, C = classify(B, n)
    a, b, c = len(C[1]), len(C[2]), len(C[3])
    delta = 3 * r - n
    assert a + b + c == n
    assert a + 2*b + 3*c == 3*r
    assert 2*a + b == 3*k
    assert b + 2*c == delta == 2*n - 3*k

    singleton_rows = {supports[j][0] for j in C[1]}
    singleton_choice = {}
    for j in C[1]:
        singleton_choice.setdefault(supports[j][0], j)

    triples = [supports[j] for j in C[3]]
    pairs = [supports[j] for j in C[2]]

    for mask in range(1 << c):
        used = set()
        chosen3 = []
        ok = True
        for q, triple in enumerate(triples):
            if not ((mask >> q) & 1):
                continue
            if any(v in used for v in triple):
                ok = False
                break
            used.update(triple)
            chosen3.append(C[3][q])
        if not ok:
            continue

        vertices = [v for v in range(r) if v not in used]
        allowed_pair_cols = []
        allowed_edges = []
        for col, edge in zip(C[2], pairs):
            u, v = edge
            if u in used or v in used:
                continue
            allowed_pair_cols.append(col)
            allowed_edges.append((u, v))

        mandatory = [v for v in vertices if v not in singleton_rows]
        match_idx = saturating_matching(vertices, allowed_edges, mandatory)
        if match_idx is None:
            continue

        x = [0] * n
        for j in chosen3:
            x[j] = 1
        covered = set(used)
        for ei in match_idx:
            col = allowed_pair_cols[ei]
            x[col] = 1
            covered.update(allowed_edges[ei])
        for v in vertices:
            if v in covered:
                continue
            j = singleton_choice.get(v)
            if j is None:
                raise AssertionError("uncovered mandatory row")
            x[j] = 1
            covered.add(v)

        assert covered == set(range(r))
        assert all(sum(B[i][j]*x[j] for j in range(n)) == 1 for i in range(r))
        assert all(sum(A[i][j]*x[j] for j in range(n)) == 1 for i in range(n))
        return True, x, {"rank": r, "nullity": k, "a": a, "b": b, "c": c, "delta": delta, "basis_rows": inds}

    return False, None, {"rank": r, "nullity": k, "a": a, "b": b, "c": c, "delta": delta, "basis_rows": inds}


def brute(A):
    n = len(A)
    if n > 18:
        raise ValueError("finite checker brute force only")
    for mask in range(1 << n):
        x = [(mask >> j) & 1 for j in range(n)]
        if all(sum(A[i][j]*x[j] for j in range(n)) == 1 for i in range(n)):
            return True, x
    return False, None


def from_rows(rows, n):
    A = [[0]*n for _ in range(n)]
    for i, row in enumerate(rows):
        for j in row:
            A[i][j] = 1
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    return A


def fano7():
    # Cyclic Fano plane blocks {i,i+1,i+3} mod 7.
    return from_rows([tuple(sorted((i, (i+1)%7, (i+3)%7))) for i in range(7)], 7)


def td33():
    rows = []
    def v(g, a): return 3*g + a
    for x in range(3):
        for y in range(3):
            rows.append((v(0, x), v(1, y), v(2, (x+y) % 3)))
    return from_rows(rows, 9)


def hostile15():
    rows = [
        (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
        (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
        (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
    ]
    return from_rows(rows, 15)


def perfect_matchings(items):
    items = tuple(items)
    if not items:
        yield ()
        return
    a = items[0]
    for p in range(1, len(items)):
        b = items[p]
        rest = items[1:p] + items[p+1:]
        for tail in perfect_matchings(rest):
            yield ((a,b),) + tail


def doily15():
    verts = range(6)
    cols = list(combinations(verts, 2))
    ci = {e:i for i,e in enumerate(cols)}
    rows = []
    for M in perfect_matchings(tuple(verts)):
        rows.append(tuple(sorted(ci[tuple(sorted(e))] for e in M)))
    assert len(rows) == 15
    return from_rows(rows, 15)


def main():
    controls = {
        "FANO7": fano7(),
        "TD33": td33(),
        "HOSTILE_UNSAT15": hostile15(),
        "DOILY15": doily15(),
    }
    expected = {
        "FANO7": False,
        "TD33": True,
        "HOSTILE_UNSAT15": False,
        "DOILY15": True,
    }
    report = {}
    for name, A in controls.items():
        got, x, meta = router(A)
        brute_got, _ = brute(A)
        assert got == brute_got == expected[name], (name, got, brute_got)
        if got:
            assert all(sum(A[i][j]*x[j] for j in range(len(A))) == 1 for i in range(len(A)))
        report[name] = {"sat": got, **meta}

    print("PASS_ACTUAL_ROW_BASIS_RANK3_MATCHING_ROUTER")
    for name, meta in report.items():
        print(name, meta)
    print("SCIENTIFIC_CEILING=FPT_2^c_NOT_UNIVERSAL_POLY")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
