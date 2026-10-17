#!/usr/bin/env python3
from itertools import product


def eval_clause(mask, vals):
    # clause represented by list of (index, positive)
    return any((vals[i] if pos else 1-vals[i]) for i,pos in mask)


def residual_equiv(pos_clauses, neg_clauses, n):
    # A_i and B_j are clauses over Y variables 0..n-1.
    for vals in product((0,1), repeat=n):
        branch0=all(eval_clause(A,vals) for A in pos_clauses)
        branch1=all(eval_clause(B,vals) for B in neg_clauses)
        existential=branch0 or branch1
        biclique=all(
            eval_clause(A,vals) or eval_clause(B,vals)
            for A in pos_clauses for B in neg_clauses
        )
        # Empty polarity: empty conjunction is TRUE, hence existential TRUE.
        if not pos_clauses or not neg_clauses:
            biclique=True
        assert existential==biclique


# Exhaustive small clause pool on 3 boundary variables: all nonempty clauses
# with at most one literal per variable and no tautology.
pool=[]
for choices in product((-1,0,1), repeat=3): # -1 neg, 0 absent, +1 pos
    if choices==(0,0,0):
        continue
    C=[]
    for i,c in enumerate(choices):
        if c:
            C.append((i,c==1))
    pool.append(tuple(C))

# Deterministic regression over representative stars, including empty polarity.
tests=[
    ([],[]),
    ([pool[0]],[]),
    ([],[pool[-1]]),
    ([pool[0]],[pool[-1]]),
    ([pool[1],pool[5]],[pool[7],pool[12]]),
    ([pool[2],pool[3],pool[4]],[pool[8],pool[9],pool[10]]),
]
for P,N in tests:
    residual_equiv(P,N,3)

# Exhaust all one-positive/one-negative pairs: this specializes to one DP
# resolvent and subsumes the two-clause one-coherence checker.
for A in pool:
    for B in pool:
        residual_equiv([A],[B],3)

print('PASS')
print('exists_x_F = (AND_i A_i) OR (AND_j B_j)')
print('CNF_projection = AND_{i,j}(A_i OR B_j)')
print('whole_single_variable_path_pivot = DAVIS_PUTNAM_BICLIQUE')
print('E8_D1=EMPTY P_VS_NP=OPEN')
