#!/usr/bin/env python3
from itertools import combinations, product

TARGET={(1,0,0),(0,1,0),(0,0,1)}

def signed_rows(n):
    out=[]
    for supp in combinations(range(n),3):
        for signs in product((-1,1),repeat=3):
            row=[0]*n
            for i,s in zip(supp,signs):
                row[i]=s
            ell=1-sum(1 for s in signs if s==-1)
            out.append((tuple(row),ell))
    return out

def side_masks(n, row, ell):
    m=[0,0]
    for idx,x in enumerate(product((0,1),repeat=n)):
        v=sum(a*b for a,b in zip(row,x))-ell
        if v in (0,1):
            m[v] |= 1<<idx
    return tuple(m)

def relation_from_three(masks, idxs):
    R=set()
    for s in product((0,1),repeat=3):
        z=(masks[idxs[0]][s[0]]
           & masks[idxs[1]][s[1]]
           & masks[idxs[2]][s[2]])
        if z:
            R.add(s)
    return R

def main():
    checked=0
    for n in range(3,7):
        rows=signed_rows(n)
        masks=[side_masks(n,*r) for r in rows]
        for idxs in combinations(range(len(rows)),3):
            checked+=1
            if relation_from_three(masks,idxs)==TARGET:
                raise AssertionError(
                    f"direct realization found at n={n}, rows={[rows[i] for i in idxs]}"
                )
    print("DIRECT_3_ROW_SIGNED_NAE_REALIZATION_OF_1IN3 = NONE_FOR_n<=6")
    print("CHECKED_ROW_TRIPLES =",checked)
    print("SCOPE = DIRECT THREE-ROW SIDE IMAGE ONLY")
    print("GENERAL_JANUS_REALIZABILITY = OPEN")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
