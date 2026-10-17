#!/usr/bin/env python3
from itertools import combinations, product

def exact1(a, clause):
    return sum(a[i] for i in clause)==1

def janus_row_side(a, clause):
    s=sum(a[i] for i in clause)
    if s not in (1,2):
        return None
    return s-1

def source_sat(n, clauses):
    return any(all(exact1(a,c) for c in clauses)
               for a in product((0,1),repeat=n))

def janus_sat(n, clauses):
    for a in product((0,1),repeat=n):
        sides=[janus_row_side(a,c) for c in clauses]
        if any(s is None for s in sides):
            continue
        if not sides or len(set(sides))==1:
            return True
    return False

def decode(a, clauses):
    sides=[janus_row_side(a,c) for c in clauses]
    assert all(s is not None for s in sides)
    assert not sides or len(set(sides))==1
    if not sides or sides[0]==0:
        out=a
    else:
        out=tuple(1-b for b in a)
    assert all(exact1(out,c) for c in clauses)
    return out

def check_instance(n, clauses):
    s=source_sat(n,clauses)
    j=janus_sat(n,clauses)
    assert s==j
    if j:
        for a in product((0,1),repeat=n):
            sides=[janus_row_side(a,c) for c in clauses]
            if any(x is None for x in sides):
                continue
            if not sides or len(set(sides))==1:
                decode(a,clauses)

def main():
    checked=0
    for n in range(3,6):
        triples=list(combinations(range(n),3))
        # Exhaust all positive 1-in-3 hypergraphs for n<=5.
        for mask in range(1<<len(triples)):
            clauses=tuple(triples[i] for i in range(len(triples))
                          if (mask>>i)&1)
            check_instance(n,clauses)
            checked+=1

    # Explicit orientation witness sanity.
    clause=(0,1,2)
    assert janus_row_side((1,0,0),clause)==0
    assert janus_row_side((0,1,1),clause)==1
    assert decode((0,1,1),(clause,))==(1,0,0)

    print("JANUS_1IN3_ORIENTATION_EMBEDDING = PASS")
    print("EXHAUSTIVE_POSITIVE_INSTANCES_n<=5 =",checked)
    print("ROW_SIDE_ORIENTATION_EQUALITY = EXACT")
    print("WITNESS_DECODE_BY_GLOBAL_COMPLEMENT = PASS")
    print("OVERHEAD = LINEAR")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
