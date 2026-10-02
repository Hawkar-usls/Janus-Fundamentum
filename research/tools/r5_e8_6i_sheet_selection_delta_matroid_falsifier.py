#!/usr/bin/env python3
from itertools import product

# Minimal frozen two-clause witness:
# C0 = (~x, ~y, ~z)
# C1 = ( x, ~y, ~z)
FORMULA = (
    ((0, False), (1, False), (2, False)),
    ((0, True),  (1, False), (2, False)),
)

def lit_value(lit, assignment):
    var, positive = lit
    value = assignment[var]
    return value if positive else 1 - value

def majority(values):
    return sum(values) >= 2

def sheet_accepts(clause, sheet, assignment):
    values = [lit_value(lit, assignment) for lit in clause]
    # Frozen three-sheet convention:
    # 0 = M0(a,b,c)
    # 1 = M1(a,not b,c)
    # 2 = M2(a,b,not c)
    if sheet == 1:
        values[1] = 1 - values[1]
    elif sheet == 2:
        values[2] = 1 - values[2]
    return majority(values)

def selection_satisfiable(selection):
    for assignment in product((0, 1), repeat=3):
        if all(
            sheet_accepts(clause, sheet, assignment)
            for clause, sheet in zip(FORMULA, selection)
        ):
            return True
    return False

FEASIBLE_SELECTIONS = tuple(
    selection
    for selection in product(range(3), repeat=2)
    if selection_satisfiable(selection)
)

def as_set(selection):
    return frozenset((clause_index, sheet) for clause_index, sheet in enumerate(selection))

FEASIBLE_SETS = frozenset(as_set(selection) for selection in FEASIBLE_SELECTIONS)

def symmetric_exchange_holds():
    for X in FEASIBLE_SETS:
        for Y in FEASIBLE_SETS:
            diff = X ^ Y
            for e in diff:
                witness = False
                for f in diff:
                    toggle = {e} if f == e else {e, f}
                    if (X ^ toggle) in FEASIBLE_SETS:
                        witness = True
                        break
                if not witness:
                    return False, (X, Y, e)
    return True, None

def basis_exchange_holds():
    for A in FEASIBLE_SETS:
        for B in FEASIBLE_SETS:
            for e in A - B:
                if not any(((A - {e}) | {f}) in FEASIBLE_SETS for f in B - A):
                    return False, (A, B, e)
    return True, None

if __name__ == "__main__":
    expected = (
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1),
        (2, 0), (2, 2),
    )
    assert FEASIBLE_SELECTIONS == expected, FEASIBLE_SELECTIONS

    matroid_ok, matroid_witness = basis_exchange_holds()
    delta_ok, delta_witness = symmetric_exchange_holds()

    assert not matroid_ok
    assert not delta_ok

    print("FORMULA = (~x OR ~y OR ~z) AND (x OR ~y OR ~z)")
    print("FEASIBLE_SHEET_SELECTIONS =", FEASIBLE_SELECTIONS)
    print("MATROID_BASE_EXCHANGE = FAIL")
    print("MATROID_WITNESS =", matroid_witness)
    print("DELTA_MATROID_SYMMETRIC_EXCHANGE = FAIL")
    print("DELTA_MATROID_WITNESS =", delta_witness)
    print("VERDICT = DIRECT_GLOBAL_SHEET_SELECTION_DELTA_MATROID_MODEL_FALSIFIED")
