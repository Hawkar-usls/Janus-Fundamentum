#!/usr/bin/env python3
"""R5 E81: exact q=8 counterexample to static global delta vertex partition.

The cyclic q=8 RXC3 source has columns {j,j+1,j+3} mod 8.  It is square,
cubic, connected and linear/C4-free.

E81 exhausts every nonempty Tanner-vertex subset, computes exact projected
ExactOne_3/Equality_3 boundary relations, and keeps the connected delta-support
clusters.  Frozen result:

  * exactly 200 connected delta-support clusters;
  * by size: {1:8, 12:48, 13:120, 14:24};
  * all 200 are even binary;
  * the only singleton delta clusters are the 8 check vertices;
  * no connected delta cluster contains all 8 variable vertices;
  * there is NO exact partition of the 16 Tanner vertices into nonempty
    delta-support modules.

Thus the universal STATIC Tanner-vertex partition premise used as the target in
E77/E78 is false even inside the square-cubic-linear RXC3 class.

This does not invalidate E78's conditional gluing theorem.  It falsifies the
universal existence premise for disjoint exact vertex partitions.  P_VS_NP
remains OPEN.
"""

from collections import Counter
from functools import lru_cache

from r5_e77_source_aligned_delta_composition_frontier import (
    source_matrix,
    tanner_adj,
    connected_mask,
    boundary_relation,
    symmetric_exchange_failure,
)
from r5_e79_binary_reconstruction_matchgate_firewall import reconstruct_even_binary


Q = 8
Q8_SETS = [tuple(sorted({j, (j+1) % Q, (j+3) % Q})) for j in range(Q)]
EXPECTED_BY_SIZE = {1:8, 12:48, 13:120, 14:24}


def verify_source(A):
    q = len(A)
    assert q == Q
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(q)) == 3 for j in range(q))
    for a in range(q):
        for b in range(a+1, q):
            assert sum(A[i][a] * A[i][b] for i in range(q)) <= 1
    adj = tanner_adj(A)
    assert connected_mask((1 << (2*q)) - 1, adj)


def exhaustive_delta_rows(A):
    q = len(A)
    adj = tanner_adj(A)
    rows = []
    connected_count = 0
    for mask in range(1, 1 << (2*q)):
        if not connected_mask(mask, adj):
            continue
        connected_count += 1
        arity, family, edges, a, b = boundary_relation(A, mask)
        if not family:
            continue
        if symmetric_exchange_failure(family, arity) is not None:
            continue
        reconstruct_even_binary(family, arity)
        rows.append({
            "mask": mask,
            "size": mask.bit_count(),
            "arity": arity,
            "family": frozenset(family),
            "edges": edges,
            "checks": a,
            "variables": b,
        })
    return connected_count, rows


def exact_partition_exists(q, rows):
    full = (1 << (2*q)) - 1
    by_vertex = [[] for _ in range(2*q)]
    for row in rows:
        m = row["mask"]
        for u in range(2*q):
            if (m >> u) & 1:
                by_vertex[u].append(m)

    @lru_cache(maxsize=None)
    def solve(state):
        if state == full:
            return True
        first = next(u for u in range(2*q) if not ((state >> u) & 1))
        for m in by_vertex[first]:
            if state & m:
                continue
            if solve(state | m):
                return True
        return False

    return solve(0)


def main():
    A = source_matrix(Q, Q8_SETS)
    verify_source(A)

    connected_count, rows = exhaustive_delta_rows(A)
    assert connected_count == 18043
    assert len(rows) == 200
    assert dict(sorted(Counter(r["size"] for r in rows).items())) == EXPECTED_BY_SIZE

    # Only singleton ExactOne check vertices survive as delta modules.
    singleton_masks = {r["mask"] for r in rows if r["size"] == 1}
    assert singleton_masks == {1 << i for i in range(Q)}

    # Every nontrivial delta module is already huge.
    nontrivial = [r for r in rows if r["size"] > 1]
    assert min(r["size"] for r in nontrivial) == 12

    # No delta module can absorb all variable vertices.  Since two disjoint
    # nontrivial modules would require at least 12+12 > 16 vertices, a complete
    # partition would need exactly one nontrivial module containing all variables
    # plus singleton checks.  Such a module does not exist.
    all_variables = sum(1 << (Q+j) for j in range(Q))
    assert not any((r["mask"] & all_variables) == all_variables for r in rows)

    # Independent exact-cover replay.
    assert exact_partition_exists(Q, rows) is False

    print("R5 E81 q8 static global delta-partition counterexample: PASS")
    print("source: cyclic {j,j+1,j+3} mod 8; square/cubic/linear/C4-free/connected")
    print("connected Tanner subsets=18043")
    print("connected delta-support clusters=200 by_size=", EXPECTED_BY_SIZE)
    print("all 200 delta relations are even binary")
    print("singleton delta modules are exactly the 8 check vertices")
    print("no delta module contains all 8 variable vertices")
    print("exact full delta-module vertex partition exists=False")
    print("STATIC_GLOBAL_DELTA_VERTEX_PARTITION theorem is FALSIFIED")
    print("E78 conditional gluing theorem remains valid; its universal premise does not")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
