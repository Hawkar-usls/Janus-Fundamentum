#!/usr/bin/env python3
from itertools import product

PARENT = [
    [2, 3, -4],
    [-1, 2, 4],
    [-2, -5, -6],
    [1, -3, -4],
    [1, -5, 6],
    [-3, 5, -6],
    [-2, 3, 6],
    [-1, 4, 5],
]
PIVOT = 2
VARS = [1, 3, 4, 5, 6]
PI = {1: -3, 3: -5, 4: 6, 5: -1, 6: -4}

EXPECTED_A = [
    [3, -4],
    [-1, 4],
    [1, -3, -4],
    [1, -5, 6],
    [-3, 5, -6],
    [-1, 4, 5],
]
EXPECTED_B = [
    [-5, -6],
    [1, -3, -4],
    [1, -5, 6],
    [-3, 5, -6],
    [3, 6],
    [-1, 4, 5],
]


def canon_clause(c):
    return tuple(sorted(set(c), key=lambda z: (abs(z), z)))


def canon_formula(f):
    return sorted((canon_clause(c) for c in f), key=lambda c: (len(c), c))


def simplify(formula, var, value):
    sat_lit = var if value else -var
    false_lit = -var if value else var
    out = []
    for clause in formula:
        if sat_lit in clause:
            continue
        out.append([lit for lit in clause if lit != false_lit])
    return out


def vars_of(formula):
    return {abs(lit) for clause in formula for lit in clause}


def deficiency(formula):
    return len(formula) - len(vars_of(formula))


def maximal_deficiency(formula):
    best = None
    m = len(formula)
    for mask in range(1 << m):
        sub = [formula[i] for i in range(m) if (mask >> i) & 1]
        d = deficiency(sub)
        if best is None or d > best:
            best = d
    return best


def lit_value(lit, assignment):
    value = assignment[abs(lit)]
    return value if lit > 0 else (not value)


def models(formula, assignment):
    return all(any(lit_value(lit, assignment) for lit in clause) for clause in formula)


def pi_lit(lit):
    image = PI[abs(lit)]
    return image if lit > 0 else -image


def pi_clause(clause):
    return {pi_lit(lit) for lit in clause}


def transport(alpha):
    return {v: lit_value(PI[v], alpha) for v in VARS}


def all_assignments(vars_):
    for bits in product([False, True], repeat=len(vars_)):
        yield dict(zip(vars_, bits))


def main():
    A = simplify(PARENT, PIVOT, False)
    B = simplify(PARENT, PIVOT, True)
    assert canon_formula(A) == canon_formula(EXPECTED_A)
    assert canon_formula(B) == canon_formula(EXPECTED_B)

    # Exact finite maximal-deficiency replay.
    assert maximal_deficiency(PARENT) == 2
    assert maximal_deficiency(A) == 1
    assert maximal_deficiency(B) == 1

    # PI is a signed permutation of the five remaining variables.
    assert set(PI) == set(VARS)
    assert {abs(v) for v in PI.values()} == set(VARS)

    # Polynomially checkable subsumption certificate: for every A clause,
    # some B clause is contained in its signed image.
    witnesses = []
    for clause in A:
        image = pi_clause(clause)
        choices = [set(d) for d in B if set(d).issubset(image)]
        assert choices, (clause, image)
        witnesses.append((set(clause), image, choices[0]))

    # Exhaustively replay the semantic theorem on this fixed instance.
    b_models = 0
    transported_models = 0
    for alpha in all_assignments(VARS):
        if models(B, alpha):
            b_models += 1
            beta = transport(alpha)
            assert models(A, beta)
            transported_models += 1
    assert b_models == 7
    assert transported_models == 7

    a_models = sum(models(A, a) for a in all_assignments(VARS))
    assert a_models == 8

    # SAT(A) OR SAT(B) collapses to SAT(A) because every B model transports.
    sat_A = a_models > 0
    sat_B = b_models > 0
    assert (sat_A or sat_B) == sat_A

    # Every surviving A model lifts directly to the original parent with x2=False.
    for beta in all_assignments(VARS):
        if not models(A, beta):
            continue
        lifted = dict(beta)
        lifted[PIVOT] = False
        assert models(PARENT, lifted)

    print("R44BP EXACT REPLAY PASS")
    print("parent_delta_star=2")
    print("A_delta_star=1")
    print("B_delta_star=1")
    print("B_models=7 transported_to_A=7")
    print("A_models=8")
    print("safe_delete=B(x2=true)")
    print("rank_effect=2->1 on fixed critical instance")
    print("certificate_verification=POLYNOMIAL")
    print("universal_polynomial_discovery=OPEN")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
