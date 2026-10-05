#!/usr/bin/env python3
"""R5 E79: binary reconstruction floor + uniform matchgate firewall.

E78 reduced the route to a constructible represented linear-delta decomposition.
E79 separates existence from representation construction on the binary-even lane.

Classical binary delta-matroid fact (Bouchet-Duchamp): after twisting by a
feasible set, a normal binary delta-matroid is determined by its feasible sets
of size at most two.  For an even binary delta-matroid the representing GF(2)
matrix has zero diagonal, so its off-diagonal entry A[i,j] is exactly the
membership bit of {i,j}.  Hence, GIVEN a feasible boundary seed and pair-flip
membership access, the matrix itself is recoverable with O(b^2) queries.

This checker verifies the stronger finite statement left implicit by E77:
all 99 q=6 and all 412 q=9 connected delta-support clusters in the frozen
catalogues are in fact even binary delta-matroids, and their GF(2)
representations are reconstructed from one feasible seed plus pair flips.
It also replays the canonical F={5,17}, twist {0,20}, its E53 product lift,
and the six first nontrivial q=9 size-14 relations.

A second firewall targets the strongest uniform holographic shortcut.  Over
fields of characteristic != 2,3, an invertible 2x2 basis cannot transform both
ExactOne_3 and Equality_3 into parity signatures simultaneously.  Since the
Matchgate Identities imply the parity condition, no single global basis can
make both primitive signatures planar-matchgate signatures.  The research note
contains the symbolic proof; here we exhaustively replay it over GF(5,7,11,13).

Scientific ceiling: E79 does NOT construct the universal decomposition, does
NOT make pair-flip extension queries cheap on arbitrary large modules, and does
NOT rule out clustered/Pfaffian representations or characteristics 2 and 3.
P_VS_NP remains OPEN.
"""

from r5_e77_source_aligned_delta_composition_frontier import (
    Q6_SETS,
    Q9_SETS,
    source_matrix,
    exhaustive_delta_clusters,
    min_max_partition,
)


def gf2_nonsingular_principal(A, mask):
    """Nonsingularity of principal submatrix A[mask] over GF(2)."""
    idx = [i for i in range(len(A)) if (mask >> i) & 1]
    m = len(idx)
    if m == 0:
        return True
    rows = []
    for i in idx:
        bits = 0
        for c,j in enumerate(idx):
            if A[i][j] & 1:
                bits |= 1 << c
        rows.append(bits)

    rank = 0
    for c in range(m):
        pivot = next((r for r in range(rank,m) if (rows[r] >> c) & 1), None)
        if pivot is None:
            continue
        rows[rank],rows[pivot] = rows[pivot],rows[rank]
        for r in range(m):
            if r != rank and ((rows[r] >> c) & 1):
                rows[r] ^= rows[rank]
        rank += 1
    return rank == m


def direct_gf2_family(A):
    n = len(A)
    return {
        mask for mask in range(1 << n)
        if gf2_nonsingular_principal(A, mask)
    }


def reconstruct_even_binary(family, n, seed=None):
    """Reconstruct the unique zero-diagonal GF(2) matrix after a feasible twist."""
    family = set(family)
    assert family
    if seed is None:
        seed = min(family)
    assert seed in family
    twisted = {x ^ seed for x in family}
    assert 0 in twisted

    # Evenness is necessary for a skew/zero-diagonal GF(2) representation.
    assert {x.bit_count() & 1 for x in twisted} == {0}

    A = [[0]*n for _ in range(n)]
    for i in range(n):
        assert (1 << i) not in twisted
    for i in range(n):
        for j in range(i+1,n):
            bit = int(((1 << i) | (1 << j)) in twisted)
            A[i][j] = A[j][i] = bit

    # This is the constructive binary test: the pair table determines A, and A
    # must regenerate the complete twisted feasible family exactly.
    assert direct_gf2_family(A) == twisted
    return seed,A


def matrix_edges(A):
    return {
        (i,j) for i in range(len(A)) for j in range(i+1,len(A)) if A[i][j]
    }


def verify_catalog(name, q, sets, expected_count, expected_minmax, expected_parts):
    A = source_matrix(q, sets)
    rows = exhaustive_delta_clusters(A)
    assert len(rows) == expected_count

    max_arity = 0
    for row in rows:
        max_arity = max(max_arity, row["arity"])
        reconstruct_even_binary(row["family"], row["arity"])

    mm,parts = min_max_partition(q, rows)
    assert mm == expected_minmax
    assert sorted(r["size"] for r in parts) == expected_parts
    for row in parts:
        reconstruct_even_binary(row["family"], row["arity"])

    print(
        f"{name}: delta_clusters={len(rows)} all_even_binary=yes "
        f"max_boundary_arity={max_arity} minmax={mm} "
        f"parts={sorted(r['size'] for r in parts)}"
    )
    return rows,parts


def verify_e77_regressions(rows6, rows9):
    # Canonical q=6 source-aligned cluster from E77.
    wanted_nodes = {0,1,4, 6+0,6+1,6+3,6+4}
    wanted_mask = sum(1 << i for i in wanted_nodes)
    row = next(r for r in rows6 if r["mask"] == wanted_mask)
    assert row["arity"] == 5
    assert row["family"] == frozenset({5,17})
    seed,A = reconstruct_even_binary(row["family"], 5, seed=5)
    assert seed == 5
    assert matrix_edges(A) == {(2,4)}
    assert {x ^ seed for x in row["family"]} == {0,20}

    # Exact E53 quotient lift: F x F.  The reconstructed matrix is two disjoint
    # copies of the same 2x2 skew block.
    product = {
        a | (b << 5)
        for a in row["family"]
        for b in row["family"]
    }
    base = 5 | (5 << 5)
    _,A10 = reconstruct_even_binary(product, 10, seed=base)
    assert matrix_edges(A10) == {(2,4),(7,9)}

    # q=9 C4-free control: all six first nontrivial size-14 / two-state
    # relations reconstruct to exactly one 2x2 GF(2) block after twisting.
    size14 = [r for r in rows9 if r["size"] == 14 and len(r["family"]) == 2]
    assert len(size14) == 6
    for r in size14:
        _,M = reconstruct_even_binary(r["family"], r["arity"])
        assert len(matrix_edges(M)) == 1

    print("E77 regressions: F={5,17} -> {0,20}; E53 lift -> two GF(2) blocks; q9 size14 six/6 reconstructed")


def transformed_symmetric_signatures(a,b,c,d,p):
    """Weight-indexed tensors after applying B=[[a,b],[c,d]] on each leg."""
    ex1 = (
        3*c*a*a,
        d*a*a + 2*a*b*c,
        c*b*b + 2*a*b*d,
        3*d*b*b,
    )
    eq3 = (
        a*a*a + c*c*c,
        a*a*b + c*c*d,
        a*b*b + c*d*d,
        b*b*b + d*d*d,
    )
    return tuple(x % p for x in ex1), tuple(x % p for x in eq3)


def has_matchgate_parity(sig, p):
    """Parity condition: support lies wholly on even or wholly on odd weights."""
    even_signature = sig[1] % p == 0 and sig[3] % p == 0
    odd_signature = sig[0] % p == 0 and sig[2] % p == 0
    return even_signature or odd_signature


def verify_uniform_matchgate_firewall():
    # Symbolic proof in the companion note covers every field char !=2,3.
    # These exhaustive prime-field checks guard the transform formulas and cases.
    for p in (5,7,11,13):
        invertible = 0
        for a in range(p):
            for b in range(p):
                for c in range(p):
                    for d in range(p):
                        if (a*d - b*c) % p == 0:
                            continue
                        invertible += 1
                        f,g = transformed_symmetric_signatures(a,b,c,d,p)
                        assert not (has_matchgate_parity(f,p) and has_matchgate_parity(g,p))
        assert invertible > 0
        print(f"uniform matchgate basis GF({p}): checked {invertible} invertible matrices; simultaneous parity=0")


def main():
    rows6,_ = verify_catalog(
        "RXC3_Q6",
        6,
        Q6_SETS,
        expected_count=99,
        expected_minmax=10,
        expected_parts=[1,1,10],
    )
    rows9,_ = verify_catalog(
        "LINEAR_Q9",
        9,
        Q9_SETS,
        expected_count=412,
        expected_minmax=15,
        expected_parts=[1,1,1,15],
    )
    verify_e77_regressions(rows6, rows9)
    verify_uniform_matchgate_firewall()

    print("R5 E79 binary reconstruction + uniform matchgate firewall: PASS")
    print("finite result: every E77 delta-support cluster on q6/q9 is even binary and GF(2)-reconstructible from one seed plus pair flips")
    print("constructibility floor: binary-even existence + feasible seed + polynomial pair-flip membership oracle => polynomial representation recovery")
    print("firewall: no single invertible 2x2 basis simultaneously matchgate-parity-izes ExactOne_3 and Equality_3 in characteristic !=2,3")
    print("missing theorem: universal polynomial construction of the decomposition and cheap local extension access")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
