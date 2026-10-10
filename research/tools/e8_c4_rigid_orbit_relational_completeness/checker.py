#!/usr/bin/env python3
"""Exact finite replay for v7.3 rigid C4 orbit relational completeness."""

from collections import Counter
from itertools import combinations, permutations

D = range(3)
S3 = list(permutations(D))
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

A_BUNDLE = ((0, 0), (1, 1), (2, 3), (3, 2))
B_BUNDLE = ((0, 0), (0, 1), (1, 2), (1, 3), (2, 0), (3, 3))
C_BUNDLE = ((0, 0), (1, 0), (1, 2), (2, 1), (2, 3), (3, 1))

EXPECTED_RELATION_SIZE_COUNTS = {1: 8, 2: 16, 3: 32, 4: 16, 5: 20, 6: 14, 7: 12, 8: 1, 9: 1}


def valid_bundle(bundle):
    left = Counter(p for p, _ in bundle)
    right = Counter(q for _, q in bundle)
    return max(left.values(), default=0) <= 2 and max(right.values(), default=0) <= 2


def allowed_gain_indices(ta, tb, bundle):
    out = []
    for hi, h in enumerate(S3):
        if all(h[REPS[ta][p]] != REPS[tb][q] for p, q in bundle):
            out.append(hi)
    return tuple(out)


def relation_mask(bundle):
    mask = 0
    for ta in D:
        for tb in D:
            if allowed_gain_indices(ta, tb, bundle):
                mask |= 1 << PAIR_INDEX[(ta, tb)]
    return mask


def orbit_rigid(bundle):
    saw = False
    for ta in D:
        for tb in D:
            gains = allowed_gain_indices(ta, tb, bundle)
            if gains:
                saw = True
                if len(gains) != 1:
                    return False
    return saw


def converse(mask):
    out = 0
    for a in D:
        for b in D:
            if mask & (1 << PAIR_INDEX[(a, b)]):
                out |= 1 << PAIR_INDEX[(b, a)]
    return out


def compose(rmask, smask):
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


def mask_pairs(mask):
    return [(a, b) for a in D for b in D if mask & (1 << PAIR_INDEX[(a, b)])]


def catalog_rigid_relations():
    valid_count = 0
    rigid_count = 0
    relations = set()
    examples = {}
    for r in range(1, 9):
        for bundle in combinations(PORT_PAIRS, r):
            if not valid_bundle(bundle):
                continue
            valid_count += 1
            if not orbit_rigid(bundle):
                continue
            rigid_count += 1
            m = relation_mask(bundle)
            relations.add(m)
            examples.setdefault(m, bundle)
    return valid_count, rigid_count, relations, examples


def pp_binary_closure(base):
    closure = set(base)
    closure.add(EQ_MASK)  # variable identification/equality
    changed = True
    while changed:
        changed = False
        current = list(closure)
        for r in current:
            rt = converse(r)
            if rt not in closure:
                closure.add(rt)
                changed = True
        current = list(closure)
        additions = set()
        for r in current:
            for s in current:
                additions.add(r & s)        # conjunction on same variables
                additions.add(compose(r, s))  # exists z R(x,z)&S(z,y)
        old = len(closure)
        closure.update(additions)
        if len(closure) != old:
            changed = True
    return closure


def explicit_neq_certificate():
    for bundle in (A_BUNDLE, B_BUNDLE, C_BUNDLE):
        assert valid_bundle(bundle)
        assert orbit_rigid(bundle)

    A = relation_mask(A_BUNDLE)
    B = relation_mask(B_BUNDLE)
    C = relation_mask(C_BUNDLE)
    BC = compose(B, C)

    assert mask_pairs(A) == [(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)]
    assert mask_pairs(B) == [(0,1),(0,2),(1,1),(2,2)]
    assert mask_pairs(C) == [(1,0),(1,2),(2,0),(2,1)]
    assert mask_pairs(BC) == [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]
    assert (A & BC) == NEQ_MASK
    return A, B, C, BC


def main():
    valid_count, rigid_count, relations, examples = catalog_rigid_relations()
    assert valid_count == 7342
    assert rigid_count == 4728
    assert len(relations) == 120

    size_counts = Counter(m.bit_count() for m in relations)
    assert dict(sorted(size_counts.items())) == EXPECTED_RELATION_SIZE_COUNTS

    A, B, C, BC = explicit_neq_certificate()

    closure = pp_binary_closure(relations)
    assert len(closure) == 512
    assert closure == set(range(512))
    assert NEQ_MASK in closure

    print("PASS: valid labelled C4 port bundles =", valid_count)
    print("PASS: orbit-rigid bundles =", rigid_count)
    print("PASS: distinct rigid binary orbit relations =", len(relations))
    print("PASS: relation cardinality profile =", dict(sorted(size_counts.items())))
    print("PASS: explicit NEQ_3 pp certificate A AND (B o C)")
    print("      A =", mask_pairs(A))
    print("      B =", mask_pairs(B))
    print("      C =", mask_pairs(C))
    print("      B o C =", mask_pairs(BC))
    print("PASS: pp binary closure size = 512 / 512")
    print("VERDICT: RIGID_C4_ORBIT_LANGUAGE_PP_DEFINES_ALL_BINARY_THREE_STATE_RELATIONS")
    print("FIREWALL: abstract CSP hardness is not yet a source-preserving smooth-Hamiltonian reduction")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
