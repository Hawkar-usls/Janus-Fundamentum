#!/usr/bin/env python3
from itertools import product


def rref_gf2(rows, n):
    """Canonical RREF for augmented GF(2) rows encoded as (coeff_bits, rhs)."""
    rows = [[a, b] for a, b in rows]
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, len(rows)) if (rows[i][0] >> c) & 1), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        pa, pb = rows[r]
        for i in range(len(rows)):
            if i != r and ((rows[i][0] >> c) & 1):
                rows[i][0] ^= pa
                rows[i][1] ^= pb
        r += 1
        if r == len(rows):
            break
    if any(a == 0 and b == 1 for a, b in rows):
        return ("INCONSISTENT",)
    nz = [(a, b) for a, b in rows if a]
    nz.sort(key=lambda row: (row[0] & -row[0]).bit_length())
    return tuple(nz)


def false_value(lit):
    return 0 if lit > 0 else 1


def clause_false(clause, assignment):
    return all(assignment[abs(lit) - 1] == false_value(lit) for lit in clause)


def clause_space(clause, n):
    rows = []
    seen = {}
    for lit in clause:
        i = abs(lit) - 1
        val = false_value(lit)
        if i in seen and seen[i] != val:
            return ("INCONSISTENT",)
        seen[i] = val
    for i, val in seen.items():
        rows.append((1 << i, val))
    return rref_gf2(rows, n)


def in_space(space, assignment):
    if space == ("INCONSISTENT",):
        return False
    for a, b in space:
        lhs = 0
        for i, bit in enumerate(assignment):
            if (a >> i) & 1:
                lhs ^= bit
        if lhs != b:
            return False
    return True


def intersect(spaces, n):
    rows = []
    for sp in spaces:
        if sp == ("INCONSISTENT",):
            return sp
        rows.extend(sp)
    return rref_gf2(rows, n)


def rank(space):
    assert space != ("INCONSISTENT",)
    return len(space)


def verify_clause_geometry():
    controls = [
        ((1, 2, 3), 3),
        ((-1, 2, -3), 3),
        ((1, -2), 2),
        ((-1,), 1),
        ((1, -1), 1),  # tautological clause -> empty falsifying set
    ]
    for clause, n in controls:
        sp = clause_space(clause, n)
        for assignment in product((0, 1), repeat=n):
            assert clause_false(clause, assignment) == in_space(sp, assignment), (clause, assignment, sp)


def verify_exponential_family(max_m=8):
    for m in range(1, max_m + 1):
        n = 3 * m
        clause_spaces = []
        for j in range(m):
            clause = (3*j + 1, 3*j + 2, 3*j + 3)
            clause_spaces.append(clause_space(clause, n))

        states = {}
        for mask in range(1 << m):
            chosen = [clause_spaces[j] for j in range(m) if (mask >> j) & 1]
            sp = intersect(chosen, n)
            assert sp != ("INCONSISTENT",)
            assert rank(sp) == 3 * mask.bit_count(), (m, mask, rank(sp))
            assert sp not in states, (m, mask, states.get(sp))
            states[sp] = mask
        assert len(states) == (1 << m)

        # All-ones is a direct SAT/noncover witness for the disjoint positive clauses.
        ones = (1,) * n
        assert all(not in_space(sp, ones) for sp in clause_spaces)

        # A point is covered iff at least one whole triple is zero.
        if m <= 4:
            for assignment in product((0, 1), repeat=n):
                covered = any(in_space(sp, assignment) for sp in clause_spaces)
                semantic = any(assignment[3*j:3*j+3] == (0, 0, 0) for j in range(m))
                assert covered == semantic

        print(f"m={m}: {len(states)} distinct nonempty intersections; rank max={3*m}")


def main():
    verify_clause_geometry()
    verify_exponential_family()
    print("PASS E8 affine forbidden-subspace intersection-lattice barrier")


if __name__ == "__main__":
    main()
