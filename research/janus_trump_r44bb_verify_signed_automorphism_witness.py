#!/usr/bin/env python3
"""Deterministic finite verifier for the R44BB-AUTOMORPH witness.

The canonical witness is the checked-in JSON artifact.  This script deliberately
contains no private copy of its clauses, automorphism, profiles, or expected
counts.  CI is not theorem authority; it verifies the finite evidence object.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json

ARTIFACT = Path(
    "research/JANUS_TRUMP_R44BB_BOUNDED_DEGREE_SIGNED_AUTOMORPHISM_SAFE_CHOICE_2026-09-03.json"
)
raw = ARTIFACT.read_bytes()
data = json.loads(raw)
w = data["exact_finite_witness"]

N = int(w["n"])
CLAUSES = [tuple(map(int, c)) for c in w["clauses"]]
PERM = {int(k): int(v) for k, v in w["signed_automorphism"]["variable_permutation"].items()}
FLIPPED = set(map(int, w["signed_automorphism"]["polarity_reversal_variables"]))
EXPECTED_PROFILES = {
    int(k): tuple(map(int, v)) for k, v in w["polarity_profiles_pos_neg"].items()
}


def canon_clause(c):
    return tuple(sorted(c, key=lambda z: (abs(z), z < 0)))


def sat_clause(c, bits):
    return any(bits[abs(l)-1] if l > 0 else not bits[abs(l)-1] for l in c)


def transformed_clause(c):
    out = []
    for lit in c:
        v, s = abs(lit), 1 if lit > 0 else -1
        if v in FLIPPED:
            s = -s
        out.append(s * PERM[v])
    return canon_clause(out)


def translation_group():
    base = sorted(map(canon_clause, CLAUSES))
    good = []
    for mask in range(1 << N):
        image = []
        for c in CLAUSES:
            d = []
            for lit in c:
                v, s = abs(lit), 1 if lit > 0 else -1
                if mask & (1 << (v-1)):
                    s = -s
                d.append(s*v)
            image.append(canon_clause(d))
        if sorted(image) == base:
            good.append(mask)
    return good


def profiles():
    out = {v: [0, 0] for v in range(1, N+1)}
    for c in CLAUSES:
        for lit in c:
            out[abs(lit)][0 if lit > 0 else 1] += 1
    return {v: tuple(x) for v, x in out.items()}


def surplus():
    supports = [set(map(abs, c)) for c in CLAUSES]
    best = 10**9
    for mask in range(1, 1 << N):
        size = mask.bit_count()
        gamma = sum(
            1 for S in supports
            if any(mask & (1 << (v-1)) for v in S)
        )
        best = min(best, gamma-size)
    return best


def local_affine_consequences_empty():
    for c in CLAUSES:
        vars_ = [abs(l) for l in c]
        local_models = []
        for vals in product((0, 1), repeat=3):
            ass = dict(zip(vars_, vals))
            if any((ass[abs(l)] == 1) if l > 0 else (ass[abs(l)] == 0) for l in c):
                local_models.append(vals)
        assert len(local_models) == 7
        for a in product((0, 1), repeat=3):
            if a == (0, 0, 0):
                continue
            for b in (0, 1):
                if all((sum(ai*xi for ai, xi in zip(a, m)) & 1) == b for m in local_models):
                    return False
    return True


def simplify(value_var, value):
    out = []
    for c in CLAUSES:
        satisfied = False
        d = []
        for lit in c:
            if abs(lit) != value_var:
                d.append(lit)
                continue
            lit_true = value if lit > 0 else not value
            if lit_true:
                satisfied = True
                break
        if not satisfied:
            out.append(tuple(d))
    return out


def binary_unsat(subformula):
    binary = [c for c in subformula if len(c) <= 2]
    if any(len(c) == 0 for c in binary):
        return True
    verts = [i for i in range(-N, N+1) if i != 0]
    G = {l: [] for l in verts}
    R = {l: [] for l in verts}

    def add(a, b):
        G[a].append(b)
        R[b].append(a)

    for c in binary:
        if len(c) == 1:
            l = c[0]
            add(-l, l)
        else:
            a, b = c
            add(-a, b)
            add(-b, a)

    seen, order = set(), []

    def dfs(v):
        seen.add(v)
        for z in G[v]:
            if z not in seen:
                dfs(z)
        order.append(v)

    for v in verts:
        if v not in seen:
            dfs(v)

    comp = {}

    def rdfs(v, k):
        comp[v] = k
        for z in R[v]:
            if z not in comp:
                rdfs(z, k)

    k = 0
    for v in reversed(order):
        if v not in comp:
            rdfs(v, k)
            k += 1
    return any(comp[v] == comp[-v] for v in range(1, N+1))


def blocked_pairs():
    out = []
    F = [set(c) for c in CLAUSES]
    for i, C in enumerate(F):
        for lit in C:
            blocked = True
            for j, D in enumerate(F):
                if i == j or -lit not in D:
                    continue
                resolvent = (C-{lit}) | (D-{-lit})
                if not any(-x in resolvent for x in resolvent):
                    blocked = False
                    break
            if blocked:
                out.append((i, lit))
    return out


def main():
    # Artifact-shape and automorphism-domain checks.
    assert data["id"] == "JANUS_TRUMP_R44BB_BOUNDED_DEGREE_SIGNED_AUTOMORPHISM_SAFE_CHOICE_2026-09-03"
    assert N == 15
    assert len(CLAUSES) == int(w["m"])
    assert all(len(c) == 3 and len(set(map(abs, c))) == 3 for c in CLAUSES)
    assert all(1 <= abs(l) <= N for c in CLAUSES for l in c)
    assert set(PERM) == set(range(1, N+1))
    assert set(PERM.values()) == set(range(1, N+1)), "variable_permutation must be bijective"
    assert FLIPPED <= set(range(1, N+1))

    supports = [frozenset(map(abs, c)) for c in CLAUSES]
    assert len(set(supports)) == len(CLAUSES)
    assert all(len(a & b) <= 1 for a, b in combinations(supports, 2))

    p = profiles()
    assert p == EXPECTED_PROFILES
    assert all(pos*neg > pos+neg for pos, neg in p.values())
    assert surplus() == int(w["surplus"])

    base = set(map(canon_clause, CLAUSES))
    assert {transformed_clause(c) for c in CLAUSES} == base
    assert PERM[3] == 3 and 3 in FLIPPED
    assert translation_group() == [0]

    assert local_affine_consequences_empty()
    assert all(
        not binary_unsat(simplify(v, val))
        for v in range(1, N+1) for val in (False, True)
    )
    assert blocked_pairs() == []

    count = count_x3_0 = 0
    for bits in product((False, True), repeat=N):
        if all(sat_clause(c, bits) for c in CLAUSES):
            count += 1
            if bits[2] is False:
                count_x3_0 += 1
    assert count == int(w["model_count"])
    assert count_x3_0 == int(w["model_count_with_x3_0"])

    print("R44BB-AUTOMORPH canonical witness: PASS")
    print(f"artifact_sha256={hashlib.sha256(raw).hexdigest()}")
    print(f"n={N} m={len(CLAUSES)} surplus={w['surplus']} models={count} models[x3=0]={count_x3_0}")
    print("JSON-bound signed automorphism and prior-primitive silence checks: PASS")
    print("CI verifies finite evidence only; general theorem authority is mathematical.")


if __name__ == "__main__":
    main()
