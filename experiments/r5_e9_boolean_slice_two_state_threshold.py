#!/usr/bin/env python3
from itertools import product, combinations

def majority(a,b,c):
    return tuple(1 if x+y+z>=2 else 0 for x,y,z in zip(a,b,c))

def two_word_relation_is_majority_closed(u,v):
    R={u,v}
    for a in R:
        for b in R:
            for c in R:
                if majority(a,b,c) not in R:
                    return False
    return True

def coord_expr(u_i,v_i):
    # expression in local selector t with t=0 -> u_i, t=1 -> v_i
    if u_i==v_i:
        return ("const",u_i)
    if (u_i,v_i)==(0,1):
        return ("lit",1)   # t
    return ("lit",0)       # not t

def compatible_pairs(U,V,shared):
    # U,V are two-word block tuples (u0,u1),(v0,v1)
    out=set()
    for tu,tv in product((0,1),repeat=2):
        wu=U[tu]; wv=V[tv]
        if all(wu[i]==wv[j] for i,j in shared):
            out.add((tu,tv))
    return out

def is_2cnf_binary_relation(R):
    # Any binary Boolean relation can be encoded by forbidding absent pairs,
    # one 2-clause per absent pair.
    clauses=[]
    for a,b in product((0,1),repeat=2):
        if (a,b) not in R:
            # forbid t=a,u=b: (t != a) OR (u != b)
            clauses.append(((0,1-a),(1,1-b)))
    # exhaustive semantic check
    for t,u in product((0,1),repeat=2):
        sat=all((t==lit1[1]) or (u==lit2[1]) for lit1,lit2 in clauses)
        assert sat == ((t,u) in R)
    return True

def main():
    # Exhaust all distinct pairs of words up to arity 5.
    checks=0
    for k in range(1,6):
        words=list(product((0,1),repeat=k))
        for u,v in combinations(words,2):
            assert two_word_relation_is_majority_closed(u,v)
            for i in range(k):
                coord_expr(u[i],v[i])
            checks+=1

    # Two arbitrary 2-state blocks glued on shared coordinates reduce to a
    # binary relation on their local selectors, hence 2-CNF.
    U=((0,1,1,0),(1,0,1,1))
    V=((1,1,0),(0,1,1))
    R=compatible_pairs(U,V,((1,0),(2,1)))
    assert is_2cnf_binary_relation(R)

    # Sharp 3-state counterrelation: positive 1-in-3.
    ONE3={(1,0,0),(0,1,0),(0,0,1)}
    assert majority((1,0,0),(0,1,0),(0,0,1))==(0,0,0)
    assert (0,0,0) not in ONE3

    print("TWO_WORD_RELATIONS_MAJORITY_CLOSED = PASS")
    print("TWO_WORD_BLOCK_COMPOSITION_TO_2SAT = PASS")
    print("THREE_WORD_SHARP_COUNTERRELATION = POSITIVE_1_IN_3")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
