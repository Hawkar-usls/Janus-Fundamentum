#!/usr/bin/env python3
"""Executable sanity witnesses for R5 E9 pairwise bridge audit.

No SAT oracle. Exhaustive checks are only over tiny truth tables used to validate
the stated identities and the 2-affine row-space recognition criterion.
"""

from itertools import product
import random


def gf2_rank(rows, n):
    rows = [r for r in rows if r]
    rows = rows[:]
    rank = 0
    col = 0
    while col < n and rank < len(rows):
        pivot = next((i for i in range(rank, len(rows))
                      if (rows[i] >> col) & 1), None)
        if pivot is None:
            col += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> col) & 1):
                rows[i] ^= rows[rank]
        rank += 1
        col += 1
    return rank


def rowspace(rows):
    out = {0}
    for r in rows:
        old = tuple(out)
        out.update(x ^ r for x in old)
    return out


def dot(mask, assignment):
    return (mask & assignment).bit_count() & 1


def relation_of_system(rows, rhs, n):
    return {
        x for x in range(1 << n)
        if all(dot(r, x) == b for r, b in zip(rows, rhs))
    }


def low_equations_true_on_relation(rel, n):
    if not rel:
        return None
    masks = [1 << i for i in range(n)]
    masks += [(1 << i) | (1 << j)
              for i in range(n) for j in range(i + 1, n)]
    x0 = next(iter(rel))
    eqs = []
    for m in masks:
        b = dot(m, x0)
        if all(dot(m, x) == b for x in rel):
            eqs.append((m, b))
    return eqs


def relation_of_equations(eqs, n):
    if eqs is None:
        return set()
    return {
        x for x in range(1 << n)
        if all(dot(m, x) == b for m, b in eqs)
    }


def rowspace_is_2affine(rows, n):
    w = rowspace(rows)
    low = [v for v in w if 1 <= v.bit_count() <= 2]
    return gf2_rank(low, n) == gf2_rank(list(w), n)


def test_rowspace_criterion():
    rng = random.Random(0xE9)
    for n in range(1, 7):
        for _ in range(500):
            m = rng.randint(0, n + 2)
            rows = [rng.randrange(1, 1 << n) for __ in range(m)]
            witness = rng.randrange(1 << n)
            rhs = [dot(r, witness) for r in rows]
            rel = relation_of_system(rows, rhs, n)
            eqs = low_equations_true_on_relation(rel, n)
            brute = relation_of_equations(eqs, n) == rel
            assert rowspace_is_2affine(rows, n) == brute


def test_krom_xor3_clause_gadget():
    for a, b, c in product([0, 1], repeat=3):
        original = bool(a or b or c)
        extension_exists = False
        for y, z in product([0, 1], repeat=2):
            gadget = (
                (a or (not y))
                and bool(y ^ b ^ z)
                and ((not z) or c)
            )
            extension_exists |= gadget
        assert original == extension_exists


def test_horn_2affine_complement_copy():
    # sign=1 means positive x; sign=0 means negative not-x.
    for signs in product([0, 1], repeat=3):
        for xs in product([0, 1], repeat=3):
            original = any(
                x if sign else (not x)
                for sign, x in zip(signs, xs)
            )
            ys = tuple(1 - x for x in xs)  # enforced by x XOR y = 1
            transformed_all_negative_horn = any(
                not (ys[i] if signs[i] else xs[i])
                for i in range(3)
            )
            assert original == transformed_all_negative_horn


def main():
    test_rowspace_criterion()
    test_krom_xor3_clause_gadget()
    test_horn_2affine_complement_copy()
    print("R5 E9 pairwise bridge sanity witnesses: PASS")


if __name__ == "__main__":
    main()
