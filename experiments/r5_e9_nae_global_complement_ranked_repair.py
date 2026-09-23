#!/usr/bin/env python3
from itertools import product

def nae(vals):
    return not (all(vals) or not any(vals))

def complement(a):
    return tuple(1-b for b in a)

def clause_truth(a, clause):
    # clause entries: (var, polarity), polarity 1 = positive literal
    return tuple((a[i] if pol else 1-a[i]) for i,pol in clause)

def formula_sat(a, clauses):
    return all(nae(clause_truth(a,c)) for c in clauses)

def main():
    clauses = (
        ((0,1),(1,1),(2,1)),
        ((1,0),(2,1),(3,0)),
        ((0,0),(2,0),(3,1)),
    )
    mods=[a for a in product((0,1), repeat=4) if formula_sat(a,clauses)]
    assert mods
    for a in mods:
        assert formula_sat(complement(a), clauses)
    pivot=0
    assert any(a[pivot]==0 for a in mods)
    if any(a[pivot]==1 for a in mods):
        assert all(formula_sat(complement(a),clauses) and complement(a)[pivot]==0
                   for a in mods if a[pivot]==1)
    print("NAE_GLOBAL_COMPLEMENT_REPAIR = PASS")
    print("CANONICAL_PIVOT_FIX_X0 = PASS")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__ == "__main__":
    main()
