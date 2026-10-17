#!/usr/bin/env python3
from itertools import combinations, product


def find_forbidden_odd_square(rows, ncols):
    m=len(rows)
    for k in range(3,min(m,ncols)+1,2):
        for R in combinations(range(m),k):
            for C in combinations(range(ncols),k):
                Cset=set(C)
                if not all(len(rows[i] & Cset)==2 for i in R):
                    continue
                if all(sum(c in rows[i] for i in R)==2 for c in C):
                    return (R,C)
    return None


def exact_witnesses(rows,n):
    return [x for x in product((0,1),repeat=n)
            if all(sum(x[j] for j in row)==1 for row in rows)]

# Balanced positive control: all-ones 3x3 matrix.
J3=[{0,1,2},{0,1,2},{0,1,2}]
assert find_forbidden_odd_square(J3,3) is None
W=exact_witnesses(J3,3)
assert set(W)=={(1,0,0),(0,1,0),(0,0,1)}
assert all(sum(x)/3 == 1/3 for x in [(1,1,1)])  # row-sum sanity

# Fano plane incidence: cubic, 3-uniform, linear, unbalanced, Exact-One UNSAT.
FANO=[
 {0,1,2},
 {0,3,4},
 {0,5,6},
 {1,3,5},
 {1,4,6},
 {2,3,6},
 {2,4,5},
]
cert=find_forbidden_odd_square(FANO,7)
assert cert is not None
R,C=cert
assert len(R)==len(C)%2==1
assert all(len(FANO[i]&set(C))==2 for i in R)
assert all(sum(c in FANO[i] for i in R)==2 for c in C)
assert exact_witnesses(FANO,7)==[]

print({
 'status':'PASS_BALANCED_SET_PARTITIONING_EXACTONE_CONTROLS',
 'balanced_positive':'J3',
 'balanced_positive_witness_count':len(W),
 'unbalanced_control':'FANO_7',
 'forbidden_odd_square_order':len(R),
 'forbidden_rows':R,
 'forbidden_cols':C,
 'fano_exactone_witness_count':0,
 'theorem_basis':'external balanced-set-partitioning integrality; finite controls only',
 'E8_D1':'EMPTY',
 'P_VS_NP':'OPEN',
})
