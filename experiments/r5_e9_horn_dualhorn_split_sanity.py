#!/usr/bin/env python3
"""Sanity checks for the R5 E9 canonical Horn/dual-Horn split.

The script exhaustively checks all sign patterns of clauses of length <=3:
every clause is Horn or dual-Horn (possibly both), and the canonical
partition preserves the original conjunction exactly.
"""

from itertools import product

def is_horn(signs):
    # True = positive literal, False = negative literal
    return sum(signs) <= 1

def is_dual_horn(signs):
    return sum(not s for s in signs) <= 1

def clause_value(signs, assignment):
    return any(x if sign else (not x)
               for sign, x in zip(signs, assignment))

def main():
    for arity in (1, 2, 3):
        for signs in product([False, True], repeat=arity):
            assert is_horn(signs) or is_dual_horn(signs), (arity, signs)
            for assignment in product([False, True], repeat=arity):
                original = clause_value(signs, assignment)
                # Canonical rule: Horn if possible, otherwise dual-Horn.
                h_clause = original if is_horn(signs) else True
                d_clause = original if not is_horn(signs) else True
                assert original == (h_clause and d_clause)
    print("R5 E9 canonical Horn/dual-Horn split sanity: PASS")

if __name__ == "__main__":
    main()
