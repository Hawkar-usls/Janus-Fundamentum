#!/usr/bin/env python3
"""R5 E77: source-aligned linear-delta composition frontier.

E76 produced one positive linear-delta cluster, but it was not source-aligned to
the frozen E12 hardness target.  E77 moves the test to the RXC3 quotient itself.

For a cubic Tanner cluster, project the ExactOne_3 / Equality_3 constraints to
its dangling half-edges and test Bouchet symmetric exchange.

Frozen controls:

1. RXC3 q=6 hardness source (12 Tanner vertices): exhaustive scan of all 2^12
   vertex subsets finds exactly 99 connected delta boundary supports.  The first
   nontrivial one has 3 checks + 4 variables, boundary arity 5, support

       F = {5,17}.

   Twisting by 5 gives {0,20}, exactly one 2x2 skew block.  By the E53 gadget
   quotient, taking the same source cluster in both unprimed/primed copies lifts
   to F x F on the E12 boundary; after twisting this is represented by two
   disjoint 2x2 skew blocks.

2. Connected square-cubic-linear q=9 source (18 Tanner vertices): exhaustive
   scan of all 2^18 vertex subsets finds exactly 412 connected delta supports.
   No nontrivial delta support exists below size 14.  At size 14 there are six
   2-state linear-even delta supports.

3. Delta-cluster partitions.  The minimum possible value of the largest piece
   in an exact vertex partition into connected delta-support clusters is 10 for
   q=6 and 15 for q=9.  Thus the first source-aligned delta decompositions in
   these controls are dominated by near-global pieces; E76 does not yet yield a
   bounded-local universal decomposition.

Scientific ceiling: this is a positive composition frontier plus an anti-loop,
not a universal polynomial algorithm.  The remaining task is to construct, for
every E12 hardness target, a polynomial-time family of linear/projected-linear
boundary clusters whose representations and gluing stay polynomially bounded.
P_VS_NP remains OPEN.
"""

from fractions import Fraction


Q6_SETS = [
    (0,1,3),
    (1,2,4),
    (2,3,5),
    (0,3,4),
    (1,4,5),
    (0,2,5),
]

Q9_SETS = [
    (0,5,8),
    (0,1,4),
    (1,2,3),
    (0,3,7),
    (4,7,8),
    (1,5,6),
    (2,4,6),
    (2,5,7),
    (3,6,8),
]

EXPECTED_Q6_BY_SIZE = {1:6, 7:6, 8:21, 9:30, 10:36}
EXPECTED_Q9_BY_SIZE = {1:9, 12:2, 13:36, 14:99, 15:148, 16:99, 17:18, 18:1}
EXPECTED_Q9_SIZE_FAMILY = {
    (1,3):9,
    (12,1):2,
    (13,1):36,
    (14,1):93,
    (14,2):6,
    (15,1):136,
    (15,2):12,
    (16,1):93,
    (16,2):6,
    (17,1):18,
    (18,1):1,
}


def source_matrix(q, sets):
    A = [[0]*q for _ in range(q)]
    assert len(sets) == q
    for j,C in enumerate(sets):
        assert len(C) == 3 and len(set(C)) == 3
        for i in C:
            A[i][j] = 1
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(q)) == 3 for j in range(q))
    return A


def tanner_adj(A):
    q = len(A)
    adj = [set() for _ in range(2*q)]
    for i in range(q):
        for j in range(q):
            if A[i][j]:
                adj[i].add(q+j)
                adj[q+j].add(i)
    return adj


def connected_mask(mask, adj):
    if not mask:
        return False
    root = (mask & -mask).bit_length()-1
    seen = 1 << root
    stack = [root]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if ((mask >> v) & 1) and not ((seen >> v) & 1):
                seen |= 1 << v
                stack.append(v)
    return seen == mask


def boundary_relation(A, mask):
    """Exact boundary support of an induced Tanner vertex cluster."""
    q = len(A)
    C = [i for i in range(q) if (mask >> i) & 1]
    V = [j for j in range(q) if (mask >> (q+j)) & 1]
    ci = {u:i for i,u in enumerate(C)}
    vj = {v:j for j,v in enumerate(V)}

    edges = []
    for u in C:
        for v in V:
            if A[u][v]:
                edges.append((ci[u], vj[v]))

    a,b = len(C),len(V)
    c_nei = [[] for _ in range(a)]
    v_nei = [[] for _ in range(b)]
    for i,j in edges:
        c_nei[i].append(j)
        v_nei[j].append(i)

    pos = 0
    cb = []
    vb = []
    for i in range(a):
        cb.append(tuple(range(pos, pos+3-len(c_nei[i]))))
        pos += 3-len(c_nei[i])
    for j in range(b):
        vb.append(tuple(range(pos, pos+3-len(v_nei[j]))))
        pos += 3-len(v_nei[j])

    family = set()
    # Equality_3 lets us enumerate one state bit per included variable vertex.
    for ymask in range(1 << b):
        base = 0
        for j in range(b):
            if (ymask >> j) & 1:
                for p in vb[j]:
                    base |= 1 << p

        partial = [base]
        feasible = True
        for i in range(a):
            internal_sum = sum((ymask >> j) & 1 for j in c_nei[i])
            if internal_sum > 1:
                feasible = False
                break
            if internal_sum == 1:
                continue
            if not cb[i]:
                feasible = False
                break
            partial = [z | (1 << p) for z in partial for p in cb[i]]
        if feasible:
            family.update(partial)

    return pos, family, len(edges), a, b


def symmetric_exchange_failure(family, n):
    F = set(family)
    if not F:
        return ("empty",)
    for X in F:
        for Y in F:
            diff = X ^ Y
            for e in range(n):
                if not ((diff >> e) & 1):
                    continue
                repaired = False
                for f in range(n):
                    if not ((diff >> f) & 1):
                        continue
                    Z = X ^ (1 << e) if e == f else X ^ (1 << e) ^ (1 << f)
                    if Z in F:
                        repaired = True
                        break
                if not repaired:
                    return X,Y,e
    return None


def exhaustive_delta_clusters(A):
    q = len(A)
    adj = tanner_adj(A)
    rows = []
    for mask in range(1, 1 << (2*q)):
        if not connected_mask(mask, adj):
            continue
        arity, family, edges, a, b = boundary_relation(A, mask)
        if family and symmetric_exchange_failure(family, arity) is None:
            rows.append({
                "mask": mask,
                "size": mask.bit_count(),
                "checks": a,
                "variables": b,
                "arity": arity,
                "family": frozenset(family),
                "edges": edges,
            })
    return rows


def min_max_partition(q, rows):
    """Exact DP for a vertex partition into connected delta-support clusters."""
    full = (1 << (2*q)) - 1
    by_vertex = [[] for _ in range(2*q)]
    for row in rows:
        m = row["mask"]
        for i in range(2*q):
            if (m >> i) & 1:
                by_vertex[i].append(row)

    INF = 10**9
    best = [INF] * (1 << (2*q))
    prev = [None] * (1 << (2*q))
    best[0] = 0

    for state in range(1 << (2*q)):
        if best[state] == INF or state == full:
            continue
        first = next(i for i in range(2*q) if not ((state >> i) & 1))
        for row in by_vertex[first]:
            m = row["mask"]
            if state & m:
                continue
            ns = state | m
            val = max(best[state], row["size"])
            if val < best[ns]:
                best[ns] = val
                prev[ns] = (state, row)

    assert best[full] < INF
    parts = []
    state = full
    while state:
        old,row = prev[state]
        parts.append(row)
        state = old
    return best[full], parts


def determinant(M):
    n = len(M)
    if n == 0:
        return Fraction(1)
    A = [[Fraction(x) for x in row] for row in M]
    det = Fraction(1)
    for c in range(n):
        p = next((i for i in range(c,n) if A[i][c]), None)
        if p is None:
            return Fraction(0)
        if p != c:
            A[c],A[p] = A[p],A[c]
            det = -det
        z = A[c][c]
        det *= z
        for i in range(c+1,n):
            if A[i][c]:
                f = A[i][c]/z
                for j in range(c,n):
                    A[i][j] -= f*A[c][j]
    return det


def skew_family(n, active_pairs):
    M = [[0]*n for _ in range(n)]
    for a,b in active_pairs:
        M[a][b] = 1
        M[b][a] = -1
    out = set()
    for mask in range(1 << n):
        idx = [i for i in range(n) if (mask >> i) & 1]
        P = [[M[i][j] for j in idx] for i in idx]
        if determinant(P) != 0:
            out.add(mask)
    return out


def verify_q6(rows):
    by_size = {}
    for row in rows:
        by_size[row["size"]] = by_size.get(row["size"],0)+1
    assert by_size == EXPECTED_Q6_BY_SIZE
    assert len(rows) == 99

    # Canonical first nontrivial source-aligned cluster:
    # checks {0,1,4}, variables {0,1,3,4} -> Tanner mask below.
    wanted_nodes = {0,1,4, 6+0,6+1,6+3,6+4}
    wanted_mask = sum(1 << i for i in wanted_nodes)
    row = next(r for r in rows if r["mask"] == wanted_mask)
    assert row["size"] == 7
    assert row["checks"] == 3 and row["variables"] == 4
    assert row["arity"] == 5
    assert row["family"] == frozenset({5,17})

    # Twist by 5 -> {0,20}; 20 has active coordinates {2,4}.
    twisted = {x ^ 5 for x in row["family"]}
    assert twisted == {0,20}
    assert skew_family(5, [(2,4)]) == twisted

    # E53 gives two independent source bits (unprimed/primed).  Thus the paired
    # lift is F x F.  After twisting by (5,5), this is two independent skew
    # blocks, proving an explicit linear-even representation of the lifted
    # source-aligned boundary support.
    product = {a | (b << 5) for a in row["family"] for b in row["family"]}
    base = 5 | (5 << 5)
    twisted_product = {z ^ base for z in product}
    assert skew_family(10, [(2,4),(7,9)]) == twisted_product

    mm, parts = min_max_partition(6, rows)
    assert mm == 10
    assert sorted(r["size"] for r in parts) == [1,1,10]
    big = next(r for r in parts if r["size"] == 10)
    assert big["family"] == frozenset({40})
    return row, mm, parts


def verify_q9(rows):
    by_size = {}
    by_size_family = {}
    for row in rows:
        by_size[row["size"]] = by_size.get(row["size"],0)+1
        key = (row["size"],len(row["family"]))
        by_size_family[key] = by_size_family.get(key,0)+1
    assert by_size == EXPECTED_Q9_BY_SIZE
    assert by_size_family == EXPECTED_Q9_SIZE_FAMILY
    assert len(rows) == 412

    # The source is linear/C4-free.
    A = source_matrix(9,Q9_SETS)
    for a in range(9):
        for b in range(a+1,9):
            assert sum(A[i][a]*A[i][b] for i in range(9)) <= 1

    nontrivial = [r for r in rows if len(r["family"]) > 1 and r["size"] > 1]
    assert min(r["size"] for r in nontrivial) == 14
    size14 = [r for r in nontrivial if r["size"] == 14]
    assert len(size14) == 6
    for r in size14:
        assert len(r["family"]) == 2
        X,Y = tuple(r["family"])
        diff = X ^ Y
        assert diff.bit_count() == 2
        # Twisting by X leaves exactly {0,diff}, represented by one skew block.
        active = [i for i in range(r["arity"]) if (diff >> i) & 1]
        assert len(active) == 2
        assert skew_family(r["arity"], [tuple(active)]) == {0,diff}

    mm, parts = min_max_partition(9, rows)
    assert mm == 15
    assert sorted(r["size"] for r in parts) == [1,1,1,15]
    big = next(r for r in parts if r["size"] == 15)
    assert len(big["family"]) == 1
    return nontrivial, mm, parts


def main():
    q6 = source_matrix(6,Q6_SETS)
    rows6 = exhaustive_delta_clusters(q6)
    first6, mm6, parts6 = verify_q6(rows6)

    q9 = source_matrix(9,Q9_SETS)
    rows9 = exhaustive_delta_clusters(q9)
    nontrivial9, mm9, parts9 = verify_q9(rows9)

    print("R5 E77 source-aligned delta composition frontier: PASS")
    print("q=6 exhaustive connected delta clusters=99 by_size=", EXPECTED_Q6_BY_SIZE)
    print("q=6 first nontrivial: size=7 checks=3 vars=4 arity=5 family={5,17}")
    print("q=6 paired E53 lift: F x F twists to two independent 2x2 skew blocks")
    print("q=6 minimum maximum cluster size in a full delta partition=", mm6,
          "part_sizes=", sorted(r["size"] for r in parts6))
    print("q=9 linear exhaustive connected delta clusters=412 by_size=", EXPECTED_Q9_BY_SIZE)
    print("q=9 first nontrivial delta cluster size=14; count_at_14=6; every one is one skew block after twist")
    print("q=9 minimum maximum cluster size in a full delta partition=", mm9,
          "part_sizes=", sorted(r["size"] for r in parts9))
    print("composition fact used externally: linear delta-matroids are closed under delta-sum")
    print("bottleneck: polynomial-time globally covering decomposition with constructible representations; current full partitions are near-global")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
