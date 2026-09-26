#!/usr/bin/env python3
"""Universal-selector frontier controls.

This is an OFFLINE FALSIFIER / CONTRACT CHECKER, not an admitted E8-D1 SAT
decider. Brute force appears only in the oracle-reference functions used to
validate the selector specification on tiny fixtures.
"""
from __future__ import annotations
from itertools import product
import json

# Literal encoding: positive int x means x=True, negative -x means x=False.
CNF = tuple[tuple[int, ...], ...]


def simplify(F: CNF, var: int, value: bool) -> CNF:
    sat_lit = var if value else -var
    dead_lit = -sat_lit
    out = []
    for C in F:
        if sat_lit in C:
            continue
        out.append(tuple(l for l in C if l != dead_lit))
    return tuple(out)


def unit_propagate(F: CNF):
    F = tuple(tuple(C) for C in F)
    assignment = {}
    while True:
        if any(len(C) == 0 for C in F):
            return F, assignment, True
        units = [C[0] for C in F if len(C) == 1]
        if not units:
            return F, assignment, False
        lit = units[0]
        v, val = abs(lit), lit > 0
        if v in assignment and assignment[v] != val:
            return F, assignment, True
        assignment[v] = val
        F = simplify(F, v, val)


def failed_literal_up_selector(F: CNF, var: int):
    """Polynomial safe partial selector. Returns 0/1 or None."""
    _, _, c0 = unit_propagate(simplify(F, var, False))
    _, _, c1 = unit_propagate(simplify(F, var, True))
    if c0 and not c1:
        return 1
    if c1 and not c0:
        return 0
    if c0 and c1:
        return "UNSAT_BY_TWO_UP_BRANCHES"
    return None


def variables(F: CNF):
    return sorted({abs(l) for C in F for l in C})


def eval_formula(F: CNF, a: dict[int, bool]) -> bool:
    for C in F:
        if not any(a[abs(l)] == (l > 0) for l in C):
            return False
    return True


def brute_sat(F: CNF) -> bool:
    """OFFLINE ORACLE REFERENCE ONLY."""
    vs = variables(F)
    for bits in product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if eval_formula(F, a):
            return True
    return False


def brute_safe_branch(F: CNF, var: int):
    """OFFLINE ORACLE REFERENCE ONLY: the forbidden semantic shortcut."""
    if brute_sat(simplify(F, var, False)):
        return 0
    if brute_sat(simplify(F, var, True)):
        return 1
    return "UNSAT"


# Guard an unsatisfiable, unit-free 2-CNF core G by x.
# x=True satisfies F. x=False leaves:
# (a v b)(a v -b)(-a v b)(-a v -b), which is UNSAT but unit propagation
# alone derives no contradiction. Therefore failed-literal-UP cannot certify
# the forced value of x.
x, a, b = 1, 2, 3
F_guarded: CNF = (
    (x, a, b),
    (x, a, -b),
    (x, -a, b),
    (x, -a, -b),
)
assert brute_sat(F_guarded)
assert not brute_sat(simplify(F_guarded, x, False))
assert brute_sat(simplify(F_guarded, x, True))
assert failed_literal_up_selector(F_guarded, x) is None
assert brute_safe_branch(F_guarded, x) == 1

out = {
    "status": "PASS_UNIVERSAL_SELECTOR_FRONTIER_CONTROL",
    "fixture": "GUARDED_UNIT_FREE_UNSAT_2CNF",
    "designated_variable": "x",
    "x_false": "UNSAT_BUT_NOT_REFUTED_BY_UNIT_PROPAGATION",
    "x_true": "SAT",
    "failed_literal_UP_selector": "UNKNOWN",
    "oracle_reference_safe_branch": 1,
    "oracle_reference_role": "OFFLINE_FALSIFIER_ONLY__FORBIDDEN_IN_E8_D1",
    "universal_selector": "OPEN__EQUIVALENT_TO_POLYNOMIAL_SAT_DECISION",
    "D1_candidate": "NONE",
    "P_VS_NP": "OPEN",
    "P_EQ_NP": "NOT_PROVED",
}
print(json.dumps(out, sort_keys=True))
