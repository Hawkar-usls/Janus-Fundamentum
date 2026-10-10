#!/usr/bin/env python3
from itertools import product, combinations

def exact1_sat(num_vars, clauses):
    for a in product((0,1), repeat=num_vars):
        if all(sum(a[v] for v in c)==1 for c in clauses):
            return True
    return False

def dual_edges(num_vars, clauses):
    occ=[[] for _ in range(num_vars)]
    for ci,c in enumerate(clauses):
        for v in c:
            occ[v].append(ci)
    assert all(len(x)<=2 for x in occ)
    edges=[]
    for v,cs in enumerate(occ):
        if len(cs)==2:
            edges.append((v,(cs[0],cs[1])))
        elif len(cs)==1:
            edges.append((v,(cs[0],None)))
    return edges

def matching_sat(num_vars, clauses):
    m=len(clauses)
    edges=dual_edges(num_vars,clauses)
    # Small exact checker: enumerate selected variables and test dual matching cover.
    for mask in range(1<<len(edges)):
        covered=[0]*m
        ok=True
        for i,(v,(a,b)) in enumerate(edges):
            if not ((mask>>i)&1):
                continue
            covered[a]+=1
            if covered[a]>1:
                ok=False; break
            if b is not None:
                covered[b]+=1
                if covered[b]>1:
                    ok=False; break
        if ok and all(x==1 for x in covered):
            return True
    return False

def main():
    checked=0
    # Enumerate small 3-uniform formulas and retain occurrence<=2.
    for n in range(3,7):
        triples=list(combinations(range(n),3))
        # keep exhaustive search modest
        max_masks=min(1<<len(triples), 4096)
        for mask in range(max_masks):
            clauses=tuple(triples[i] for i in range(len(triples)) if (mask>>i)&1)
            occ=[0]*n
            for c in clauses:
                for v in c:
                    occ[v]+=1
            if max(occ,default=0)>2:
                continue
            assert exact1_sat(n,clauses)==matching_sat(n,clauses)
            checked+=1

    print("POSITIVE_1IN3_OCCURRENCE_LE2_TO_DUAL_MATCHING = PASS")
    print("SMALL_EXACT_INSTANCES_CHECKED =",checked)
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
