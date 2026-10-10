#!/usr/bin/env python3
"""Exact truth-table regression for the E8 v4.1 OR3 -> 2CNF+XOR3 gadget."""

from itertools import product
import random


def gadget_extensions(a, b, c):
    out = []
    for y, z in product((0, 1), repeat=2):
        binary_left = bool(a) or (not bool(y))
        affine = (y ^ b ^ z) == 1
        binary_right = (not bool(z)) or bool(c)
        if binary_left and affine and binary_right:
            out.append((y, z))
    return out


def check_single_clause():
    for a, b, c in product((0, 1), repeat=3):
        projected = bool(gadget_extensions(a, b, c))
        assert projected == bool(a or b or c), (a, b, c, projected)


def eval_literal(assignment, lit):
    var, positive = lit
    value = assignment[var]
    return value if positive else 1 - value


def eval_formula(formula, assignment):
    return all(any(eval_literal(assignment, lit) for lit in clause) for clause in formula)


def original_sat(formula):
    vars_ = sorted({v for clause in formula for v, _ in clause})
    for vals in product((0, 1), repeat=len(vars_)):
        a = dict(zip(vars_, vals))
        if eval_formula(formula, a):
            return True
    return False


def gadget_sat(formula):
    vars_ = sorted({v for clause in formula for v, _ in clause})
    for vals in product((0, 1), repeat=len(vars_)):
        a = dict(zip(vars_, vals))
        ok = True
        for clause in formula:
            if len(clause) == 3:
                av, bv, cv = [eval_literal(a, lit) for lit in clause]
                if not gadget_extensions(av, bv, cv):
                    ok = False
                    break
            else:
                if not any(eval_literal(a, lit) for lit in clause):
                    ok = False
                    break
        if ok:
            return True
    return False


def deterministic_formula_regression(seed=411, trials=700):
    rng = random.Random(seed)
    names = ["a", "b", "c", "d"]
    for _ in range(trials):
        m = rng.randint(1, 5)
        formula = []
        for _j in range(m):
            k = rng.choice((2, 3))
            vars_clause = rng.sample(names, k)
            formula.append([(v, bool(rng.getrandbits(1))) for v in vars_clause])
        assert original_sat(formula) == gadget_sat(formula), formula


def main():
    check_single_clause()
    deterministic_formula_regression()
    print("PASS: projected 2CNF+XOR3 gadget relation equals OR3 on all 8 inputs")
    print("PASS: 700 deterministic random 2/3-CNF controls preserve satisfiability")
    print("PASS: construction uses two private auxiliaries and one XOR3 row per 3-clause")


if __name__ == "__main__":
    main()
