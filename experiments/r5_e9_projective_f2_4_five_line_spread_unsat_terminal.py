#!/usr/bin/env python3
"""Exact regression for the F2^4 five-line spread UNSAT terminal.

The mathematical theorem is proved in the companion research note.  This script
is only a finite/executable regression: it verifies a canonical binary 2-spread,
its hyperplane-cover property, ambient-dimension stability, polynomial detector,
and a one-line-deletion negative control.
"""

from itertools import combinations


CANONICAL_SPREAD = (
    frozenset((1, 2, 3)),
    frozenset((4, 8, 12)),
    frozenset((5, 10, 15)),
    frozenset((6, 11, 13)),
    frozenset((7, 9, 14)),
)


def dot2(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def rank_f2(vectors):
    basis = {}
    for x in vectors:
        x = int(x)
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
    return len(basis)


def is_binary_line(L):
    if len(L) != 3 or 0 in L:
        return False
    a, b, c = sorted(L)
    return rank_f2((a, b, c)) == 2 and (a ^ b ^ c) == 0


def line_contained_in_hyperplane(L, t):
    return all(dot2(x, t) == 0 for x in L)


def is_f2_4_spread_certificate(lines):
    """Recognize the five-line certificate without enumerating dual functionals."""
    if len(lines) != 5:
        return False
    if not all(is_binary_line(L) for L in lines):
        return False

    union = set()
    for L in lines:
        if union.intersection(L):
            return False
        union.update(L)

    # The 15 nonzero points must live in one 4D span.  Pairwise disjointness then
    # makes them exactly U\{0} because a binary 4-space has 15 nonzero points.
    return len(union) == 15 and rank_f2(union) == 4


def find_spread_certificate(source_lines):
    for idxs in combinations(range(len(source_lines)), 5):
        block = tuple(source_lines[i] for i in idxs)
        if is_f2_4_spread_certificate(block):
            return idxs
    return None


def hyperplane_census(lines, ambient_dimension):
    census = {}
    for t in range(1 << ambient_dimension):
        hits = tuple(i for i, L in enumerate(lines)
                     if line_contained_in_hyperplane(L, t))
        census[t] = hits
    return census


def main():
    spread = CANONICAL_SPREAD

    assert is_f2_4_spread_certificate(spread)
    assert set().union(*spread) == set(range(1, 16))
    assert rank_f2(set().union(*spread)) == 4

    # Exact F2^4 dual-functional census.
    census4 = hyperplane_census(spread, 4)
    assert len(census4[0]) == 5
    for t in range(1, 16):
        assert len(census4[t]) == 1, (t, census4[t])

        # Reproduce the proof's 7 = 3+1+1+1+1 intersection census.
        K_nonzero = {x for x in range(1, 16) if dot2(x, t) == 0}
        assert len(K_nonzero) == 7
        sizes = sorted(len(set(L).intersection(K_nonzero)) for L in spread)
        assert sizes == [1, 1, 1, 1, 3], (t, sizes)

    # Ambient stability: embed the same U in the low four coordinates of F2^7.
    # High coordinates of t do not change t|_U.  Every one of all 128 dual
    # functionals is still hit by at least one spread line.
    census7 = hyperplane_census(spread, 7)
    for t, hits in census7.items():
        low = t & 0b1111
        expected = 5 if low == 0 else 1
        assert len(hits) == expected, (t, hits, expected)

    # Polynomial-search regression: mix the certificate with decoy binary lines.
    decoys = (
        frozenset((1, 4, 5)),
        frozenset((2, 4, 6)),
        frozenset((3, 8, 11)),
    )
    source_lines = decoys + spread
    cert = find_spread_certificate(source_lines)
    assert cert is not None
    found = tuple(source_lines[i] for i in cert)
    assert is_f2_4_spread_certificate(found)

    # Tight negative control for the canonical spread: removing any one spread
    # line leaves a nonzero functional whose hyperplane contains none of the four
    # remaining lines.  This does not claim minimality for arbitrary covers; it
    # only checks this explicit certificate is irredundant.
    for removed in range(5):
        reduced = tuple(L for i, L in enumerate(spread) if i != removed)
        witnesses = [
            t for t in range(1, 16)
            if not any(line_contained_in_hyperplane(L, t) for L in reduced)
        ]
        assert witnesses, removed
        # Every uncovered witness is covered by the deleted line in the full set.
        assert all(line_contained_in_hyperplane(spread[removed], t)
                   for t in witnesses)

    print("PASS canonical F2^4 spread: 5 lines partition all 15 nonzero points")
    print("PASS hyperplane census: nonzero t -> exactly one contained spread line")
    print("PASS ambient F2^7 embedding: every dual functional remains covered")
    print(f"PASS polynomial detector regression: certificate indices={cert}")
    print("PASS deletion controls: each canonical spread line is essential")
    print("SCIENTIFIC_CEILING=FINITE_REGRESSION_ONLY")
    print("FIVE_LINE_SPREAD_UNSAT_TERMINAL=THEOREM_IN_COMPANION_NOTE")
    print("BOUNDED_CERTIFICATE_COMPLETENESS=OPEN")
    print("E8_D1=EMPTY; P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
