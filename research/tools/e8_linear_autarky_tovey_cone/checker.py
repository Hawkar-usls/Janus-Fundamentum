#!/usr/bin/env python3
import itertools


def signed_matrix(clauses, nvars):
    A = []
    for clause in clauses:
        row = [0] * nvars
        for lit in clause:
            v = abs(lit) - 1
            s = 1 if lit > 0 else -1
            assert row[v] in (0, s), "tautological/mixed duplicate literal in checker control"
            row[v] = s
        A.append(row)
    return A


def matvec(A, z):
    return [sum(a * b for a, b in zip(row, z)) for row in A]


def nonnegative(vals):
    return all(v >= 0 for v in vals)


def rounded_assignment(z):
    return [1 if t > 0 else 0 if t < 0 else None for t in z]


def clause_touched_and_satisfied(clause, assignment):
    touched = False
    sat = False
    for lit in clause:
        val = assignment[abs(lit) - 1]
        if val is None:
            continue
        touched = True
        truth = val == 1
        if lit < 0:
            truth = not truth
        sat |= truth
    return touched, sat


def verify_rounding_autarky(clauses, z):
    A = signed_matrix(clauses, len(z))
    assert nonnegative(matvec(A, z))
    assn = rounded_assignment(z)
    for clause in clauses:
        touched, sat = clause_touched_and_satisfied(clause, assn)
        assert (not touched) or sat


def tovey_reduce(original, nvars):
    occurrences = [[] for _ in range(nvars)]
    inherited = []
    next_copy = 0
    for clause in original:
        new_clause = []
        for lit in clause:
            v = abs(lit) - 1
            s = 1 if lit > 0 else -1
            copy = next_copy
            next_copy += 1
            occurrences[v].append(copy)
            new_clause.append((copy, s))
        inherited.append(new_clause)

    red_clauses = []
    inherited_rows = []
    for row in inherited:
        clause = tuple((copy + 1) if s > 0 else -(copy + 1) for copy, s in row)
        inherited_rows.append(len(red_clauses))
        red_clauses.append(clause)

    link_rows = []
    for v, copies in enumerate(occurrences):
        assert len(copies) >= 2, "checker uses cleaned hard-core controls"
        for j, c in enumerate(copies):
            d = copies[(j + 1) % len(copies)]
            link_rows.append(len(red_clauses))
            red_clauses.append((-(c + 1), d + 1))

    return red_clauses, next_copy, occurrences, inherited_rows, link_rows


def replication(occurrences, w):
    q = sum(len(xs) for xs in occurrences)
    z = [None] * q
    for v, copies in enumerate(occurrences):
        for c in copies:
            z[c] = w[v]
    assert all(t is not None for t in z)
    return z


def source_return_symbolic_control():
    # Every variable occurs twice, so every Tovey cycle is nontrivial.
    original = [
        (1, 2, 3),
        (-1, -2, -3),
    ]
    A = signed_matrix(original, 3)
    red, q, occ, inherited_rows, link_rows = tovey_reduce(original, 3)
    B = signed_matrix(red, q)
    assert q == 6

    # Matrix-level identity B*R = [A; 0] in the inherited/link row ordering.
    basis = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    for w in basis:
        z = replication(occ, w)
        bz = matvec(B, z)
        aw = matvec(A, w)
        assert [bz[i] for i in inherited_rows] == aw
        assert all(bz[i] == 0 for i in link_rows)

    # Exhaustive bounded integer replay: link feasibility forces equality around each cycle.
    for z in itertools.product(range(-2, 3), repeat=q):
        bz = matvec(B, z)
        links_ok = all(bz[i] >= 0 for i in link_rows)
        if not links_ok:
            continue
        for copies in occ:
            vals = {z[c] for c in copies}
            assert len(vals) == 1
        w = tuple(z[copies[0]] for copies in occ)
        assert [bz[i] for i in inherited_rows] == matvec(A, w)
        assert nonnegative(bz) == nonnegative(matvec(A, w))

    # Exhaustive cone equivalence on a bounded box in original coordinates.
    for w in itertools.product(range(-3, 4), repeat=3):
        z = replication(occ, w)
        assert nonnegative(matvec(A, w)) == nonnegative(matvec(B, z))


def rounding_controls():
    clauses = [
        (1, 2, -3),
        (-1, 2, 3),
        (1, -2, 3),
    ]
    # Search a finite box for all nonzero cone vectors and verify sign-rounding autarky.
    found = 0
    A = signed_matrix(clauses, 3)
    for z in itertools.product(range(-3, 4), repeat=3):
        if z == (0, 0, 0):
            continue
        if nonnegative(matvec(A, z)):
            verify_rounding_autarky(clauses, z)
            found += 1
    assert found > 0


def main():
    source_return_symbolic_control()
    rounding_controls()
    print("PASS linear-autarky sign-rounding finite replay")
    print("PASS Tovey link-cycle cone collapse: B*R=[A;0]")
    print("PASS exhaustive bounded source-return cone controls")


if __name__ == "__main__":
    main()
