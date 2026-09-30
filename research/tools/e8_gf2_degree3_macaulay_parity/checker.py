#!/usr/bin/env python3
from itertools import combinations, product

# Polynomials over GF(2) in the Boolean quotient x_i^2=x_i.
# A polynomial is the frozenset of squarefree monomials with coefficient 1.
ZERO = frozenset()
ONE = frozenset({()})


def padd(p, q):
    return p.symmetric_difference(q)


def pmul(p, q):
    out = set()
    for a in p:
        for b in q:
            m = tuple(sorted(set(a) | set(b)))
            if m in out:
                out.remove(m)
            else:
                out.add(m)
    return frozenset(out)


def xvar(i):
    return frozenset({(i,)})


def false_factor(lit):
    i = abs(lit) - 1
    # Positive literal x is false at x=0 -> indicator 1+x.
    # Negative literal !x is false at x=1 -> indicator x.
    return frozenset({(), (i,)}) if lit > 0 else frozenset({(i,)})


def clause_poly(clause):
    p = ONE
    for lit in clause:
        p = pmul(p, false_factor(lit))
    return p


def xor3_cnf(vars0, rhs):
    """Four 3-clauses encoding xor(vars0)=rhs; vars0 are 0-based."""
    clauses = []
    for vals in product((0, 1), repeat=3):
        if (sum(vals) & 1) != rhs:
            # Clause false exactly at this forbidden assignment.
            clauses.append(tuple((i + 1) if a == 0 else -(i + 1)
                                 for i, a in zip(vars0, vals)))
    return clauses


def k4_tseitin(charges):
    vertices = range(4)
    edges = [(i, j) for i in vertices for j in range(i + 1, 4)]
    edge_id = {e: k for k, e in enumerate(edges)}
    clauses = []
    scopes = []
    for v in vertices:
        inc = tuple(edge_id[e] for e in edges if v in e)
        scopes.append(inc)
        clauses.extend(xor3_cnf(inc, charges[v]))
    return edges, scopes, clauses


def all_monomials(n, degree=3):
    out = [()]
    for d in range(1, degree + 1):
        out.extend(combinations(range(n), d))
    return out


def poly_to_bits(p, index):
    value = 0
    for mon in p:
        value ^= 1 << index[mon]
    return value


def bits_to_poly(value, monomials):
    return frozenset(monomials[i] for i in range(len(monomials))
                     if (value >> i) & 1)


def reduce_row(value, basis):
    while value:
        pivot = value.bit_length() - 1
        if pivot not in basis:
            break
        value ^= basis[pivot]
    return value


def insert_row(value, basis):
    value = reduce_row(value, basis)
    if not value:
        return None
    pivot = value.bit_length() - 1
    basis[pivot] = value
    return value


def degree3_closure(clauses, n):
    monomials = all_monomials(n, 3)
    index = {m: i for i, m in enumerate(monomials)}
    basis = {}
    queue = []

    for clause in clauses:
        row = poly_to_bits(clause_poly(clause), index)
        new = insert_row(row, basis)
        if new is not None:
            queue.append(new)

    # Linear span + multiplication by one variable whenever the multilinearized
    # result still has degree <= 3. Linearity means it suffices to multiply a
    # spanning set; every newly independent remainder is queued.
    qi = 0
    while qi < len(queue):
        row = queue[qi]
        qi += 1
        p = bits_to_poly(row, monomials)
        for i in range(n):
            q = pmul(p, xvar(i))
            if q and max(map(len, q)) > 3:
                continue
            new = insert_row(poly_to_bits(q, index), basis)
            if new is not None:
                queue.append(new)

    one = 1 << index[()]
    derives_one = reduce_row(one, basis) == 0
    return derives_one, len(basis), len(monomials)


def eval_clause(clause, assignment):
    for lit in clause:
        bit = assignment[abs(lit) - 1]
        if (lit > 0 and bit) or (lit < 0 and not bit):
            return True
    return False


def brute_sat(clauses, n):
    for a in product((0, 1), repeat=n):
        if all(eval_clause(c, a) for c in clauses):
            return a
    return None


def unit_propagation_conflict(clauses, assumptions, n):
    val = [None] * n
    for lit in assumptions:
        i = abs(lit) - 1
        want = 1 if lit > 0 else 0
        if val[i] is not None and val[i] != want:
            return True
        val[i] = want

    changed = True
    while changed:
        changed = False
        for clause in clauses:
            satisfied = False
            unassigned = []
            for lit in clause:
                i = abs(lit) - 1
                if val[i] is None:
                    unassigned.append(lit)
                else:
                    truth = val[i] if lit > 0 else 1 - val[i]
                    if truth:
                        satisfied = True
                        break
            if satisfied:
                continue
            if not unassigned:
                return True
            if len(unassigned) == 1:
                lit = unassigned[0]
                i = abs(lit) - 1
                want = 1 if lit > 0 else 0
                if val[i] is not None and val[i] != want:
                    return True
                if val[i] is None:
                    val[i] = want
                    changed = True
    return False


def assert_pair_probe_silent(clauses, n):
    literals = [s * (i + 1) for i in range(n) for s in (1, -1)]
    for p in literals:
        assert not unit_propagation_conflict(clauses, (p,), n), ("singleton", p)
    for p, q in combinations(literals, 2):
        if p == -q:
            continue
        assert not unit_propagation_conflict(clauses, (p, q), n), ("pair", p, q)


def parity_polynomial(scope, rhs):
    p = frozenset({(i,) for i in scope})
    if rhs:
        p = padd(p, ONE)
    return p


def main():
    # Local identity: the four forbidden-assignment clause polynomials of one
    # XOR3 relation sum exactly to its affine parity equation.
    for rhs in (0, 1):
        scope = (0, 1, 2)
        total = ZERO
        for clause in xor3_cnf(scope, rhs):
            total = padd(total, clause_poly(clause))
        assert total == parity_polynomial(scope, rhs), (rhs, total)

    # Odd K4 Tseitin: UNSAT globally, but pair probing is silent.
    edges, scopes, odd = k4_tseitin((1, 0, 0, 0))
    assert len(edges) == 6 and len(odd) == 16
    assert brute_sat(odd, 6) is None
    assert_pair_probe_silent(odd, 6)

    # The four extracted parity equations sum to the constant 1.
    parity_sum = ZERO
    for scope, rhs in zip(scopes, (1, 0, 0, 0)):
        parity_sum = padd(parity_sum, parity_polynomial(scope, rhs))
    assert parity_sum == ONE

    derives_one, rank_odd, dim = degree3_closure(odd, 6)
    assert derives_one

    # Even-charge K4 Tseitin is satisfiable and sound degree-3 closure must not
    # derive 1. This is a strong same-geometry SAT control.
    _, _, even = k4_tseitin((0, 0, 0, 0))
    witness = brute_sat(even, 6)
    assert witness is not None
    derives_one_even, rank_even, dim_even = degree3_closure(even, 6)
    assert dim_even == dim
    assert not derives_one_even

    # Ordinary non-XOR SAT control.
    sat_control = [(1, 2, 3), (-1, 2, 3), (1, -2, 3)]
    assert brute_sat(sat_control, 3) is not None
    assert not degree3_closure(sat_control, 3)[0]

    print("PASS E8 GF2 degree-3 Macaulay parity kernel")
    print(f"K4 odd Tseitin: pair-probe silent, PC3 derives 1; row-rank={rank_odd}/{dim}")
    print(f"K4 even Tseitin: SAT witness={witness}; PC3 does not derive 1; row-rank={rank_even}/{dim_even}")


if __name__ == "__main__":
    main()
