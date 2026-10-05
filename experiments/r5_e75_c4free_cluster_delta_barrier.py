#!/usr/bin/env python3
"""R5 E75: bounded C4-free cluster delta-matroid barrier.

E74 proves that one Equality_3 star, the E63 P5 interface, and the E53
Eq3 x Eq3 quotient are not delta-matroids.  E75 asks whether grouping several
nearby Tanner vertices can repair the obstruction.

For every connected simple bipartite INTERNAL cluster H with:
  * total vertices s <= 9,
  * check side carrying ExactOne_3,
  * variable side carrying Equality_3,
  * internal degree <= 3,
  * no C4,
  * missing incident edges represented as distinct boundary stubs so every
    Tanner vertex has ambient degree exactly three,

we enumerate the exact projected boundary support and test Bouchet's symmetric
exchange axiom.

Result: apart from the trivial one-vertex ExactOne_3 cluster, every nonempty
connected C4-free cluster of size 1..9 containing an Equality_3 vertex is
NON-delta.  In particular every connected cluster with 2..9 vertices is
non-delta.

This applies directly to every connected <=9-vertex cluster in a linear
square-cubic carrier, because linearity of the incidence matrix makes the
Tanner graph C4-free.

Scientific ceiling: finite-radius firewall only.  Clusters of size >=10,
unbounded grouping, weighted cancellation, and non-support-preserving
holographic transformations remain open.  P_VS_NP remains OPEN.
"""

from itertools import combinations


EXPECTED_TOTAL = {
    1: 2,
    2: 1,
    3: 2,
    4: 6,
    5: 24,
    6: 135,
    7: 972,
    8: 8628,
    9: 91440,
}

EXPECTED_DELTA = {
    1: 1,  # singleton ExactOne_3 only
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 0,
    9: 0,
}


def connected(a, b, edges):
    if a + b == 1:
        return True
    if not edges:
        return False
    adj = [[] for _ in range(a + b)]
    for i, j in edges:
        adj[i].append(a + j)
        adj[a + j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == a + b


def c4_free(a, b, edge_set):
    for i1, i2 in combinations(range(a), 2):
        common = 0
        for j in range(b):
            if (i1, j) in edge_set and (i2, j) in edge_set:
                common += 1
                if common >= 2:
                    return False
    return True


def boundary_relation(a, b, edges):
    """Exact support projected to dangling boundary edges.

    Variable-side Equality_3 lets us enumerate only one Boolean state y_j per
    variable vertex.  Check-side boundary bits are then forced to zero if one
    internal selected neighbour is present, or choose exactly one dangling edge
    if no internal selected neighbour is present.
    """
    c_nei = [[] for _ in range(a)]
    v_nei = [[] for _ in range(b)]
    for i, j in edges:
        c_nei[i].append(j)
        v_nei[j].append(i)

    c_boundary = [[] for _ in range(a)]
    v_boundary = [[] for _ in range(b)]
    pos = 0
    for i in range(a):
        d = len(c_nei[i])
        assert d <= 3
        c_boundary[i] = list(range(pos, pos + 3 - d))
        pos += 3 - d
    for j in range(b):
        d = len(v_nei[j])
        assert d <= 3
        v_boundary[j] = list(range(pos, pos + 3 - d))
        pos += 3 - d
    boundary_arity = pos

    family = set()
    for ymask in range(1 << b):
        y = [(ymask >> j) & 1 for j in range(b)]

        base = 0
        # Equality_3: every dangling edge at variable j equals y_j.
        for j in range(b):
            if y[j]:
                for p in v_boundary[j]:
                    base |= 1 << p

        partial = [base]
        feasible = True
        for i in range(a):
            internal_sum = sum(y[j] for j in c_nei[i])
            if internal_sum > 1:
                feasible = False
                break
            if internal_sum == 1:
                # ExactOne already satisfied: all dangling check bits are zero.
                continue

            # No internal selected edge: exactly one dangling check edge is one.
            if not c_boundary[i]:
                feasible = False
                break
            partial = [
                mask | (1 << p)
                for mask in partial
                for p in c_boundary[i]
            ]

        if feasible:
            family.update(partial)

    return boundary_arity, family


def symmetric_exchange_failure(family, n):
    F = set(family)
    assert F, "empty support is not used as a delta-matroid certificate"
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
                    return X, Y, e
    return None


def enumerate_size(s):
    total = 0
    delta = 0
    nonempty = 0

    if s == 1:
        # One check vertex: ExactOne_3 = {100,010,001}, a matroid basis family.
        arity, fam = boundary_relation(1, 0, [])
        assert arity == 3 and fam == {1, 2, 4}
        total += 1
        nonempty += 1
        assert symmetric_exchange_failure(fam, arity) is None
        delta += 1

        # One variable vertex: Equality_3 = {000,111}, non-delta.
        arity, fam = boundary_relation(0, 1, [])
        assert arity == 3 and fam == {0, 7}
        total += 1
        nonempty += 1
        assert symmetric_exchange_failure(fam, arity) is not None
        return total, nonempty, delta

    for a in range(1, s):
        b = s - a
        possible = [(i, j) for i in range(a) for j in range(b)]

        for mask in range(1, 1 << len(possible)):
            # A connected s-vertex graph needs at least s-1 internal edges.
            if mask.bit_count() < s - 1:
                continue
            edges = [possible[t] for t in range(len(possible)) if (mask >> t) & 1]

            cdeg = [0] * a
            vdeg = [0] * b
            for i, j in edges:
                cdeg[i] += 1
                vdeg[j] += 1
            if max(cdeg) > 3 or max(vdeg) > 3:
                continue
            if not connected(a, b, edges):
                continue
            edge_set = set(edges)
            if not c4_free(a, b, edge_set):
                continue

            arity, family = boundary_relation(a, b, edges)
            total += 1
            assert family
            nonempty += 1

            if symmetric_exchange_failure(family, arity) is None:
                delta += 1

    return total, nonempty, delta


def main():
    rows = []
    for s in range(1, 10):
        total, nonempty, delta = enumerate_size(s)
        assert total == EXPECTED_TOTAL[s]
        assert nonempty == total
        assert delta == EXPECTED_DELTA[s]
        rows.append((s, total, delta))
        print(f"cluster_size={s} labelled_C4free_topologies={total} delta_supports={delta}")

    assert sum(t for _s, t, _d in rows) == 101210
    assert sum(d for _s, _t, d in rows) == 1

    print("R5 E75 bounded C4-free cluster delta barrier: PASS")
    print("exhausted 101210 labelled connected C4-free cubic-boundary topologies through 9 Tanner vertices")
    print("only delta support: singleton ExactOne_3 check")
    print("every connected 2..9 vertex cluster is non-delta; singleton Equality_3 is non-delta")
    print("consequence: no support-preserving delta-matroid/matching compilation by connected clusters of <=9 vertices on linear carriers")
    print("live escape: cluster size >=10, unbounded/global cancellation, or non-support-preserving weighted/holographic mechanism")
    print("scientific ceiling: P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
