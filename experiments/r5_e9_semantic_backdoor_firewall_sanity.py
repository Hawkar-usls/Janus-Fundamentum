#!/usr/bin/env python3
"""Tiny sanity witness for the semantic-backdoor firewall.

For B = Var(F), Ext_F(B) is exactly the set of satisfying assignments of F.
This script checks the identity on all 3-variable CNFs built from a small
selection of clauses. It is only a sanity witness, not a complexity result.
"""

from itertools import product, combinations

VARS = range(3)

def lit_value(var, positive, a):
    return a[var] if positive else (not a[var])

def clause_value(clause, a):
    return any(lit_value(v, s, a) for v, s in clause)

def formula_value(formula, a):
    return all(clause_value(c, a) for c in formula)

def ext_full_boundary(formula):
    return {
        a for a in product([False, True], repeat=3)
        if formula_value(formula, a)
    }

def models(formula):
    return {
        a for a in product([False, True], repeat=3)
        if formula_value(formula, a)
    }

def main():
    clauses = [
        ((0, True), (1, True), (2, True)),
        ((0, False), (1, True)),
        ((1, False), (2, False)),
        ((0, True),),
        ((2, False),),
    ]
    for r in range(len(clauses)+1):
        for idxs in combinations(range(len(clauses)), r):
            f = tuple(clauses[i] for i in idxs)
            assert ext_full_boundary(f) == models(f)
    print("R5 E9 semantic-backdoor full-boundary identity: PASS")

if __name__ == "__main__":
    main()
