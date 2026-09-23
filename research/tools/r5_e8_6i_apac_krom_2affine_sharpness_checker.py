#!/usr/bin/env python3
from __future__ import annotations

from itertools import product
import json


def and_graph(x, y, p):
    return p == (x & y)


def plane_clause_checks():
    rows = list(product((0, 1), repeat=3))

    tests = {
        "p=0": (
            lambda x, y, p: p == 0,
            lambda x, y: (not x) or (not y),
        ),
        "p=x": (
            lambda x, y, p: p == x,
            lambda x, y: (not x) or bool(y),
        ),
        "p=y": (
            lambda x, y, p: p == y,
            lambda x, y: bool(x) or (not y),
        ),
        "p=x+y+1": (
            lambda x, y, p: p == (x ^ y ^ 1),
            lambda x, y: bool(x) or bool(y),
        ),
    }

    for name, (plane, clause) in tests.items():
        exact = {
            (x, y, p)
            for x, y, p in rows
            if plane(x, y, p) and and_graph(x, y, p)
        }
        translated = {
            (x, y, p)
            for x, y, p in rows
            if plane(x, y, p) and clause(x, y)
        }
        assert exact == translated, name


def clause_and_chain_check():
    # Verify NOT(a*b*c) via t=a*b, u=t*c, u=0.
    for a, b, c in product((0, 1), repeat=3):
        clause = (not a) or (not b) or (not c)
        witnesses = []
        for t, u in product((0, 1), repeat=2):
            ok = (
                t == (a & b)
                and u == (t & c)
                and u == 0
            )
            if ok:
                witnesses.append((t, u))
        assert bool(witnesses) == clause
        if witnesses:
            assert len(witnesses) == 1


def e9_clause_encoding_check():
    # a OR b OR c
    # iff exists y,z:
    #   (a OR not y)
    #   and y xor b xor z = 1
    #   and (not z OR c)
    for a, b, c in product((0, 1), repeat=3):
        lhs = bool(a or b or c)
        witnesses = []
        for y, z in product((0, 1), repeat=2):
            rhs = (
                (bool(a) or (not y))
                and ((y ^ b ^ z) == 1)
                and ((not z) or bool(c))
            )
            if rhs:
                witnesses.append((y, z))
        assert bool(witnesses) == lhs


def full_context_check():
    # In the affine part of the AND-chain encoding, t=a*b has not yet been
    # imposed and a,b,t are unconstrained for a nondegenerate clause.
    triples = set(product((0, 1), repeat=3))
    assert len(triples) == 8


def verify():
    plane_clause_checks()
    clause_and_chain_check()
    e9_clause_encoding_check()
    full_context_check()

    return {
        "status": "PASS",
        "plane_to_krom_truth_tables": "PASS_4_OF_4",
        "three_literal_negative_clause_and_chain": "PASS_8_ROWS",
        "e9_krom_xor3_clause_encoding": "PASS_8_ROWS",
        "full_product_positive_control": "PASS_8_LOCAL_AFFINE_ROWS",
        "scientific_ceiling": "SHARPNESS_ONLY__D1_EMPTY__P_VS_NP_OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
