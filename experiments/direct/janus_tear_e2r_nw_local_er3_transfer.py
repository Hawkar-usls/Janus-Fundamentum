#!/usr/bin/env python3
"""Provider finite transfer-mechanics replay for C025-E2R-L1E."""
from itertools import product


def parity_on(nb, a):
    out = False
    for v in nb:
        out ^= a[v]
    return out


def image_of_generator(n, neighborhoods):
    out = set()
    for bits in product([False, True], repeat=n):
        a = {i+1: bits[i] for i in range(n)}
        out.add(tuple(parity_on(nb, a) for nb in neighborhoods))
    return out


def choose_outside_image(n, neighborhoods):
    image = image_of_generator(n, neighborhoods)
    for b in product([False, True], repeat=len(neighborhoods)):
        if b not in image:
            return b
    raise AssertionError("surjective fixture")


def forbidding_clause(nb, bits):
    return tuple(-v if bit else v for v, bit in zip(nb, bits))


def direct_parity_cnf(neighborhoods, b):
    clauses = []
    for nb, target in zip(neighborhoods, b):
        for bits in product([False, True], repeat=len(nb)):
            if (sum(bits) % 2 == 1) != target:
                clauses.append(forbidding_clause(nb, bits))
    return tuple(clauses)


def clause_satisfied(clause, a):
    return any(a[abs(lit)] if lit > 0 else not a[abs(lit)] for lit in clause)


def projection(v):
    return lambda a: a[v]


def semantic_clause_admitted(nb, target, literal_functions):
    vars_ = tuple(sorted(nb))
    for bits in product([False, True], repeat=len(vars_)):
        a = {v: bits[i] for i, v in enumerate(vars_)}
        if parity_on(nb, a) != target:
            continue
        if not any((fn(a) if positive else not fn(a)) for fn, positive in literal_functions):
            return False
    return True


def containing_neighborhood(support, neighborhoods):
    for i, nb in enumerate(neighborhoods):
        if support <= set(nb):
            return i
    return None


def main():
    n = 3
    neighborhoods = [(1,2), (2,3), (1,2), (2,3)]
    b = choose_outside_image(n, neighborhoods)
    assert b not in image_of_generator(n, neighborhoods)
    cnf = direct_parity_cnf(neighborhoods, b)
    assert len(cnf) == len(neighborhoods) * 2

    for bits in product([False, True], repeat=n):
        a = {i+1: bits[i] for i in range(n)}
        assert not all(clause_satisfied(c, a) for c in cnf)

    cursor = 0
    for nb, target in zip(neighborhoods, b):
        for local_bits in product([False, True], repeat=len(nb)):
            if (sum(local_bits) % 2 == 1) == target:
                continue
            clause = cnf[cursor]
            cursor += 1
            lf = [(projection(abs(lit)), lit > 0) for lit in clause]
            assert semantic_clause_admitted(nb, target, lf)

    i = containing_neighborhood({1,2}, neighborhoods)
    assert i is not None
    nb, target = neighborhoods[i], b[i]
    g, h = projection(1), projection(2)
    s = lambda a: g(a) and (not h(a))
    assert semantic_clause_admitted(nb, target, [(s,False),(g,True)])
    assert semantic_clause_admitted(nb, target, [(s,False),(h,False)])
    assert semantic_clause_admitted(nb, target, [(s,True),(g,False),(h,True)])
    assert containing_neighborhood({1,3}, neighborhoods) is None

    print("C025_E2R_L1E_OUTSIDE_IMAGE_FIXTURE = PASS")
    print("C025_E2R_L1E_DIRECT_PARITY_CNF_UNSAT = PASS")
    print("C025_E2R_L1E_DIRECT_ROOT_AXIOM_SEMANTIC_INCLUSION = PASS")
    print("C025_E2R_L1E_SAME_NEIGHBORHOOD_EXTENSION_AXIOM_INCLUSION = PASS")
    print("C025_E2R_L1E_CROSS_NEIGHBORHOOD_REJECTION = PASS")
    print(f"fixture_root_vars = {n}")
    print(f"fixture_outputs = {len(neighborhoods)}")
    print(f"fixture_direct_clauses = {len(cnf)}")
    print("claim_boundary = finite transfer mechanics only; asymptotic restricted lower bound uses external heavy-width theorem")


if __name__ == "__main__":
    main()
