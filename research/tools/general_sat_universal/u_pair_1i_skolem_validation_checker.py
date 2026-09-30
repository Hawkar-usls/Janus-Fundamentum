#!/usr/bin/env python3
from itertools import product
import random


def eval_clause(clause, a):
    return any(a[abs(lit)-1] if lit > 0 else not a[abs(lit)-1] for lit in clause)


def eval_cnf(formula, a):
    return all(eval_clause(c, a) for c in formula)


def r_g(x, y, formula):
    return bool(x) or (not eval_cnf(formula, y))


def fixed_zero_rule_valid(formula, n):
    for y in product((False, True), repeat=n):
        exists_x = any(r_g(x, y, formula) for x in (False, True))
        if exists_x and not r_g(False, y, formula):
            return False
    return True


def is_unsat(formula, n):
    return not any(eval_cnf(formula, y) for y in product((False, True), repeat=n))


def random_clause(n, rng):
    width = rng.randint(1, min(3, n))
    variables = rng.sample(range(1, n+1), width)
    return tuple(v if rng.getrandbits(1) else -v for v in variables)


def closed_constant_rule_control():
    # SAT: constants form a tiny zero-input Skolem vector.
    sat_formula = [(1, 2), (-1, 2)]
    witness = (False, True)
    assert eval_cnf(sat_formula, witness)

    # UNSAT: no constant assignment can satisfy.
    unsat_formula = [(1,), (-1,)]
    assert not any(eval_cnf(unsat_formula, a) for a in product((False, True), repeat=1))


def main():
    closed_constant_rule_control()

    rng = random.Random(20260917)
    cases = 0
    for n in range(1, 6):
        for _ in range(100):
            m = rng.randint(0, 8)
            formula = [random_clause(n, rng) for _ in range(m)]
            # Exact finite regression of the reduction:
            # fixed f(y)=0 is valid for R_G(x,y)=x OR NOT G(y)
            # iff G is UNSAT.
            assert fixed_zero_rule_valid(formula, n) == is_unsat(formula, n)
            cases += 1

    print(f'PASS: {cases} finite 3CNF controls satisfy SKOLEM_VALID(R_G,0) iff G is UNSAT')
    print('PASS: satisfiable closed controls admit O(n) constant witness rules')
    print('THEOREM ROLE: finite run checks implementation only; coNP-completeness is proved symbolically')
    print('CLAIM CEILING: SKOLEM_DEBT_V1 remains bookkeeping only; P vs NP remains OPEN')


if __name__ == '__main__':
    main()
