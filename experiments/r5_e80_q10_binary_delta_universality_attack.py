#!/usr/bin/env python3
"""R5 E80: exact q=10 cyclic RXC3 attack on binary-delta universality.

The q=10 cyclic source is the natural continuation of the frozen q=6 family:
column j meets checks {j, j+1, j+3} mod q.  It is square, cubic, connected and
linear/C4-free.

E80 exhausts every nonempty Tanner-vertex subset (2^20-1), keeps connected
clusters, computes the exact projected ExactOne_3/Equality_3 boundary relation,
tests Bouchet symmetric exchange, and then applies the E79 GF(2) reconstruction
test to every delta-support cluster.

Frozen expected result:
  * 1845 connected delta-support clusters;
  * size distribution {1:10,12:10,13:80,14:300,15:530,16:540,17:340,18:35};
  * every one of the 1845 relations is even binary;
  * exact minimum possible largest piece in a full delta-cluster partition is
    17/20, attained by part sizes [1,1,1,17].

This is a stronger finite control, not a universal theorem.  P_VS_NP remains
OPEN.
"""

from collections import Counter

from r5_e77_source_aligned_delta_composition_frontier import (
    source_matrix,
    tanner_adj,
    connected_mask,
    boundary_relation,
    symmetric_exchange_failure,
    min_max_partition,
)
from r5_e79_binary_reconstruction_matchgate_firewall import reconstruct_even_binary


Q = 10
Q10_SETS = [tuple(sorted({j, (j+1) % Q, (j+3) % Q})) for j in range(Q)]
EXPECTED_BY_SIZE = {1:10, 12:10, 13:80, 14:300, 15:530, 16:540, 17:340, 18:35}


def verify_source(A):
    q = len(A)
    assert q == Q
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(q)) == 3 for j in range(q))

    # Linearity / Tanner C4-freeness: two source columns share at most one check.
    for a in range(q):
        for b in range(a+1, q):
            assert sum(A[i][a] * A[i][b] for i in range(q)) <= 1

    adj = tanner_adj(A)
    full = (1 << (2*q)) - 1
    assert connected_mask(full, adj)


def exhaustive_rows(A):
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

        # E79 constructive test: twist by one feasible set, reconstruct the
        # zero-diagonal GF(2) matrix from pair flips, and regenerate the complete
        # feasible family by principal nonsingularity.
        reconstruct_even_binary(family, arity)
        rows.append({
            "mask": mask,
            "size": mask.bit_count(),
            "checks": a,
            "variables": b,
            "arity": arity,
            "family": frozenset(family),
            "edges": edges,
        })

    return connected_count, rows


def main():
    A = source_matrix(Q, Q10_SETS)
    verify_source(A)

    connected_count, rows = exhaustive_rows(A)
    assert connected_count == 180537
    assert len(rows) == 1845

    by_size = Counter(row["size"] for row in rows)
    assert dict(sorted(by_size.items())) == EXPECTED_BY_SIZE

    mm, parts = min_max_partition(Q, rows)
    assert mm == 17
    assert sorted(row["size"] for row in parts) == [1,1,1,17]

    big = next(row for row in parts if row["size"] == 17)
    assert len(big["family"]) == 1

    print("R5 E80 exact q10 binary-delta universality attack: PASS")
    print("source: cyclic columns {j,j+1,j+3} mod 10; square/cubic/linear/C4-free/connected")
    print("all nonempty Tanner subsets=1048575; connected=180537")
    print("connected delta-support clusters=1845 by_size=", EXPECTED_BY_SIZE)
    print("binary reconstruction failures=0; all 1845 delta relations are even binary")
    print("exact minimum maximum full delta-piece size=17/20; part_sizes=[1,1,1,17]")
    print("GLOBAL_BINARY_DELTA_CONSTRUCTIBILITY remains OPEN")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
