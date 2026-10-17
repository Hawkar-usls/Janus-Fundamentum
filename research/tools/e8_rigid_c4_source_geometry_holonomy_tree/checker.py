#!/usr/bin/env python3
"""Exact replay for v7.4 rigid-C4 source geometry / holonomy frontier."""

from collections import Counter
from itertools import combinations, permutations, product

D = range(3)
S3 = list(permutations(D))
ID = (0, 1, 2)
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
PORT_PAIRS = [(p, q) for p in range(4) for q in range(4)]
PAIR_INDEX = {(a, b): 3 * a + b for a in D for b in D}
ALL_MASK = (1 << 9) - 1
EQ_MASK = sum(1 << PAIR_INDEX[(a, a)] for a in D)
NEQ_MASK = ALL_MASK ^ EQ_MASK

A = ((0, 0), (1, 1), (2, 3), (3, 2))
B = ((0, 0), (0, 1), (1, 2), (1, 3), (2, 0), (3, 3))
C = ((0, 0), (1, 0), (1, 2), (2, 1), (2, 3), (3, 1))


def valid_bundle(bundle):
    left = Counter(p for p, _ in bundle)
    right = Counter(q for _, q in bundle)
    return max(left.values(), default=0) <= 2 and max(right.values(), default=0) <= 2


def allowed_gains(ta, tb, bundle):
    out = []
    for hi, h in enumerate(S3):
        if all(h[REPS[ta][p]] != REPS[tb][q] for p, q in bundle):
            out.append(hi)
    return tuple(out)


def rigid(bundle):
    saw = False
    for a in D:
        for b in D:
            g = allowed_gains(a, b, bundle)
            if g:
                saw = True
                if len(g) != 1:
                    return False
    return saw


def relation_mask(bundle):
    out = 0
    for a in D:
        for b in D:
            if allowed_gains(a, b, bundle):
                out |= 1 << PAIR_INDEX[(a, b)]
    return out


def compose_rel(rmask, smask):
    out = 0
    for a in D:
        for c in D:
            if any(
                (rmask & (1 << PAIR_INDEX[(a, b)]))
                and (smask & (1 << PAIR_INDEX[(b, c)]))
                for b in D
            ):
                out |= 1 << PAIR_INDEX[(a, c)]
    return out


def converse(mask):
    out = 0
    for a in D:
        for b in D:
            if mask & (1 << PAIR_INDEX[(a, b)]):
                out |= 1 << PAIR_INDEX[(b, a)]
    return out


def pcompose(p, q):
    """Permutation p after q."""
    return tuple(p[q[i]] for i in D)


def port_degree(bundle, side):
    if side == "left":
        return tuple(sum(1 for p, _ in bundle if p == i) for i in range(4))
    return tuple(sum(1 for _, q in bundle if q == i) for i in range(4))


def mask_pairs(mask):
    return [(a, b) for a in D for b in D if mask & (1 << PAIR_INDEX[(a, b)])]


def catalog_rigid_masks():
    masks = set()
    valid = 0
    rigid_count = 0
    for r in range(1, 9):
        for bundle in combinations(PORT_PAIRS, r):
            if not valid_bundle(bundle):
                continue
            valid += 1
            if not rigid(bundle):
                continue
            rigid_count += 1
            masks.add(relation_mask(bundle))
    return valid, rigid_count, masks


def composition_converse_closure(base):
    closure = set(base)
    changed = True
    while changed:
        changed = False
        current = list(closure)
        additions = {converse(r) for r in current}
        for r in current:
            for s in current:
                additions.add(compose_rel(r, s))
        old = len(closure)
        closure.update(additions)
        changed = len(closure) != old
    return closure


def direct_gauge_satisfiable(tx, tz, ty):
    # Global colour symmetry fixes gx = identity.
    gx = ID
    for gy in S3:
        for gz in S3:
            if not all(gx[REPS[tx][p]] != gy[REPS[ty][q]] for p, q in A):
                continue
            if not all(gx[REPS[tx][p]] != gz[REPS[tz][q]] for p, q in B):
                continue
            if not all(gz[REPS[tz][p]] != gy[REPS[ty][q]] for p, q in C):
                continue
            return True
    return False


def main():
    for bundle in (A, B, C):
        assert valid_bundle(bundle)
        assert rigid(bundle)

    # Reproduce the v7.3 abstract NEQ identity.
    Am = relation_mask(A)
    Bm = relation_mask(B)
    Cm = relation_mask(C)
    assert (Am & compose_rel(Bm, Cm)) == NEQ_MASK

    # Exact port-capacity failure of the literal A/B/C variable identification.
    assert port_degree(A, "left") == (1, 1, 1, 1)
    assert port_degree(A, "right") == (1, 1, 1, 1)
    assert port_degree(B, "left") == (2, 2, 1, 1)
    assert port_degree(B, "right") == (2, 1, 1, 2)
    assert port_degree(C, "left") == (1, 2, 2, 1)
    assert port_degree(C, "right") == (2, 2, 1, 1)
    xdeg = tuple(a + b for a, b in zip(port_degree(A, "left"), port_degree(B, "left")))
    ydeg = tuple(a + b for a, b in zip(port_degree(A, "right"), port_degree(C, "right")))
    zdeg = tuple(a + b for a, b in zip(port_degree(B, "right"), port_degree(C, "left")))
    assert xdeg == (3, 3, 2, 2)
    assert ydeg == (3, 3, 2, 2)
    assert zdeg == (3, 3, 3, 3)
    assert max(xdeg) > 2 and max(ydeg) > 2 and max(zdeg) > 2

    # Enumerate the abstractly satisfying triples and verify holonomy failure.
    triples = []
    for tx, tz, ty in product(D, repeat=3):
        ga = allowed_gains(tx, ty, A)
        gb = allowed_gains(tx, tz, B)
        gc = allowed_gains(tz, ty, C)
        if ga and gb and gc:
            assert len(ga) == len(gb) == len(gc) == 1
            triples.append((tx, tz, ty, ga[0], gb[0], gc[0]))
    expected = [
        (0, 1, 2, 4, 5, 5),
        (0, 2, 1, 3, 4, 3),
        (1, 1, 0, 4, 5, 5),
        (1, 1, 2, 4, 5, 5),
        (2, 2, 0, 3, 4, 3),
        (2, 2, 1, 3, 4, 3),
    ]
    assert triples == expected
    for tx, tz, ty, ia, ib, ic in triples:
        composed = pcompose(S3[ic], S3[ib])  # h_zy o h_xz
        assert composed == ID
        assert S3[ia] != ID
        assert S3[ia] != composed
        assert not direct_gauge_satisfiable(tx, tz, ty)

    # Hence the true gauge-aware triangle relation on (x,y) is empty.
    source_pairs = []
    for tx in D:
        for ty in D:
            if any(direct_gauge_satisfiable(tx, tz, ty) for tz in D):
                source_pairs.append((tx, ty))
    assert source_pairs == []

    # Scoped algebra audit: without same-pair intersections, closure stops at 346.
    valid_count, rigid_count, base = catalog_rigid_masks()
    assert valid_count == 7342
    assert rigid_count == 4728
    assert len(base) == 120
    cc = composition_converse_closure(base)
    assert len(cc) == 346
    assert EQ_MASK not in cc
    assert NEQ_MASK not in cc

    print("PASS: v7.3 abstract A AND (B o C) = NEQ_3")
    print("PASS: direct source gluing exceeds port capacity:", xdeg, ydeg, zdeg)
    print("PASS: abstract satisfying orbit triples =", len(triples))
    print("PASS: every triple violates unique-gain cycle holonomy")
    print("PASS: gauge-aware A/B/C triangle terminal relation = EMPTY")
    print("PASS: rigid base masks = 120 from", rigid_count, "rigid bundles")
    print("PASS: composition+converse closure =", len(cc), "/ 512; EQ and NEQ absent")
    print("VERDICT: ABSTRACT_RIGID_PP_COMPLETENESS_IS_NOT_SOURCE_COMPLETENESS")
    print("POSITIVE: all-rigid bundle trees admit exact 3-state tree DP plus unique-gain reconstruction")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
