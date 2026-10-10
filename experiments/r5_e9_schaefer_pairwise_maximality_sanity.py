#!/usr/bin/env python3
"""Tiny exhaustive sanity checks for E9 Schaefer pairwise maximality lemmas.

Enumerates affine Boolean relations through arity 4 and verifies:
1. affine + Horn (AND-closed) iff definable by pinnings and equalities;
2. affine + bijunctive (majority-closed) iff definable by pinnings,
   equalities and disequalities.

This is a sanity witness, not the theorem proof.
"""

def rowspace(gens):
    out={0}
    for g in gens:
        out |= {x ^ g for x in tuple(out)}
    return tuple(sorted(out))

def affine_relations(n):
    nonzero=list(range(1,1<<n))
    subs=set()
    for mask in range(1<<len(nonzero)):
        gens=[nonzero[i] for i in range(len(nonzero)) if (mask>>i)&1]
        subs.add(rowspace(gens))
    rels=set()
    for S in subs:
        for a in range(1<<n):
            rels.add(tuple(sorted(a ^ x for x in S)))
    return [set(r) for r in rels]

def and_closed(R):
    return all((x & y) in R for x in R for y in R)

def majority(x,y,z):
    return (x & y) | (x & z) | (y & z)

def majority_closed(R):
    return all(majority(x,y,z) in R for x in R for y in R for z in R)

def defined_by_eq_pins(R,n):
    if not R:
        return True
    S=set(range(1<<n))
    for i in range(n):
        vals={ (x>>i)&1 for x in R }
        if len(vals)==1:
            b=next(iter(vals))
            S={x for x in S if ((x>>i)&1)==b}
    for i in range(n):
        for j in range(i+1,n):
            if all(((x>>i)&1)==((x>>j)&1) for x in R):
                S={x for x in S if ((x>>i)&1)==((x>>j)&1)}
    return S==R

def defined_by_xor2_pins(R,n):
    if not R:
        return True
    S=set(range(1<<n))
    for i in range(n):
        vals={ (x>>i)&1 for x in R }
        if len(vals)==1:
            b=next(iter(vals))
            S={x for x in S if ((x>>i)&1)==b}
    for i in range(n):
        for j in range(i+1,n):
            vals={((x>>i)&1)^((x>>j)&1) for x in R}
            if len(vals)==1:
                b=next(iter(vals))
                S={x for x in S if ((((x>>i)&1)^((x>>j)&1))==b)}
    return S==R

def main():
    for n in range(1,5):
        rels=affine_relations(n)
        for R in rels:
            assert and_closed(R) == defined_by_eq_pins(R,n)
            assert majority_closed(R) == defined_by_xor2_pins(R,n)
        print(f"arity {n}: {len(rels)} affine relations PASS")
    print("E9 Schaefer pairwise maximality sanity: PASS")

if __name__=="__main__":
    main()
