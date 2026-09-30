#!/usr/bin/env python3
"""Exact regression for E8 v3.7 rank-2 factorization / rainbow-forest carrier."""

from itertools import combinations, product
import random


def det(mat):
    n = len(mat)
    if n == 0:
        return 1
    if n == 1:
        return mat[0][0]
    if n == 2:
        return mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
    if n == 3:
        a, b, c = mat
        return (
            a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0])
        )
    raise ValueError("small determinant only")


def matmul_uvt(U, V):
    return [[sum(U[i][k] * V[j][k] for k in range(2)) for j in range(3)] for i in range(3)]


def independent(rows):
    if len(rows) <= 1:
        return True
    if len(rows) == 2:
        return det(rows) != 0
    # all local matrices have rank at most two
    return False


def check_local_factorization():
    K = [[1, 1, -1], [1, 1, -1], [0, -1, 1]]
    U = [[1, 1], [1, 1], [0, -1]]
    V = [[1, 0], [0, 1], [0, -1]]
    assert matmul_uvt(U, V) == K

    expected = {(), (0,), (1,), (2,), (0, 2)}
    got = set()
    for r in range(4):
        for S in combinations(range(3), r):
            sub = [[K[i][j] for j in S] for i in S]
            pminor_nonzero = det(sub) != 0
            common_ind = independent([U[i] for i in S]) and independent([V[i] for i in S])
            assert pminor_nonzero == common_ind
            if common_ind:
                got.add(S)
    assert got == expected


def eval_formula(formula, assignment):
    return all(any(assignment[v] == sign for v, sign in clause) for clause in formula)


def sat_bruteforce(formula):
    vars_ = sorted({v for clause in formula for v, _ in clause})
    for bits in product([False, True], repeat=len(vars_)):
        a = dict(zip(vars_, bits))
        if eval_formula(formula, a):
            return True
    return False


def occurrence_edges(formula):
    occs = []
    by_var = {}
    for ci, clause in enumerate(formula):
        for pi, (v, sign) in enumerate(clause):
            oid = len(occs)
            occs.append((ci, pi, v, sign))
            by_var.setdefault(v, []).append(oid)

    edges = {}
    for v, ids in by_var.items():
        if len(ids) > 3:
            raise AssertionError("occurrence bound violated")
        signs = [occs[i][3] for i in ids]
        if len(set(signs)) == 1:
            # No sign conflicts: give every occurrence a private graph edge.
            for j, oid in enumerate(ids):
                edges[oid] = ((v, "p", j, 0), (v, "p", j, 1))
        elif len(ids) == 2:
            assert signs[0] != signs[1]
            edges[ids[0]] = ((v, 0), (v, 1))
            edges[ids[1]] = ((v, 1), (v, 2))
        elif len(ids) == 3:
            pos = [oid for oid in ids if occs[oid][3]]
            neg = [oid for oid in ids if not occs[oid][3]]
            majority, minority = (pos, neg) if len(pos) == 2 else (neg, pos)
            assert len(majority) == 2 and len(minority) == 1
            L, R = majority
            M = minority[0]
            edges[L] = ((v, 0), (v, 1))
            edges[M] = ((v, 1), (v, 2))
            edges[R] = ((v, 2), (v, 3))
        else:
            raise AssertionError("mixed degree-one impossible")
    return occs, edges


def rainbow_full_bruteforce(formula):
    occs, edges = occurrence_edges(formula)
    per_clause = [[] for _ in formula]
    for oid, (ci, _pi, _v, _sign) in enumerate(occs):
        per_clause[ci].append(oid)

    # Size m rainbow means exactly one edge from each of the m clause colors.
    for choice in product(*per_clause):
        used = set()
        ok = True
        for oid in choice:
            a, b = edges[oid]
            if a in used or b in used:
                ok = False
                break
            used.add(a)
            used.add(b)
        if ok:
            return True
    return False


def occurrence_bound_ok(formula):
    counts = {}
    for clause in formula:
        # canonical source clauses have distinct variables in a clause
        if len({v for v, _ in clause}) != len(clause):
            return False
        for v, _ in clause:
            counts[v] = counts.get(v, 0) + 1
            if counts[v] > 3:
                return False
    return True


def frozen_controls():
    return [
        # SAT
        [[("x", True), ("y", True)], [("x", False), ("z", True)]],
        # UNSAT 2-CNF control from the earlier syndrome artifact
        [[("x", True), ("y", True)], [("x", True), ("y", False)],
         [("x", False), ("z", True)], [("z", False), ("w", True)],
         [("z", False), ("w", False)]],
        # Mixed degree-three variable with all three local states exercised globally
        [[("x", True), ("a", True)], [("x", True), ("b", False)],
         [("x", False), ("c", True)]],
    ]


def random_controls(seed=51137, trials=1200):
    rng = random.Random(seed)
    vars_ = ["a", "b", "c", "d", "e"]
    checked = 0
    attempts = 0
    while checked < trials and attempts < trials * 100:
        attempts += 1
        m = rng.randint(2, 6)
        formula = []
        for _ in range(m):
            k = rng.choice([2, 3])
            chosen = rng.sample(vars_, k)
            formula.append([(v, bool(rng.getrandbits(1))) for v in chosen])
        if not occurrence_bound_ok(formula):
            continue
        assert sat_bruteforce(formula) == rainbow_full_bruteforce(formula), formula
        checked += 1
    assert checked == trials
    return checked


def main():
    check_local_factorization()
    for f in frozen_controls():
        assert occurrence_bound_ok(f)
        assert sat_bruteforce(f) == rainbow_full_bruteforce(f), f
    n = random_controls()
    print("PASS: exact K3=UV^T local support equals common independence")
    print("PASS: SAT iff full rainbow matching on frozen controls")
    print(f"PASS: SAT iff full rainbow matching on {n} deterministic random bounded-occurrence controls")


if __name__ == "__main__":
    main()
