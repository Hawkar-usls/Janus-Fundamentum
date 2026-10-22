#!/usr/bin/env python3
"""BABEL-24 independent connected SCL27 all-degree Gram UNKNOWN falsifier.

Exact integer + Fraction only. Frozen 27x27 linear cubic regular SAT fixture.
Full degree-1 rational ideal-span proof: 7x7 determinant exactly 8.
A valid SAT model forces all multiplier columns to have rank at most 7.
No claim about UNSAT Fourier lower bounds, general SAT or P=NP.
"""
import hashlib
import itertools
import json
import random
from collections import Counter
from fractions import Fraction

ROWS = (
    (0,1,2), (0,3,6), (0,5,7), (3,5,20), (1,7,11),
    (3,8,12), (6,7,8), (2,5,8), (2,10,14),
    (9,10,11), (9,12,15), (9,14,22), (12,13,14),
    (10,13,16), (1,6,17), (15,16,17), (4,17,20),
    (11,13,21), (4,18,19), (15,18,24), (18,23,25),
    (21,22,23), (16,19,25), (19,21,26), (24,25,26),
    (4,23,26), (20,22,24)
)
ROW_SHA256 = "9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed"
SELECTED = ((0,0),(0,4),(2,0),(3,0),(4,0),(14,0),(15,0))
EXPECTED_MODEL_ONE_INDICES = (2,3,7,9,13,17,19,23,24)


def independent_reconstructor():
    """Discovery provenance, independently reconstruct all frozen rows."""
    def affine(off):
        pt=lambda x,y:off+3*x+y
        return [tuple(sorted(line)) for k in range(3) for line in (
            [pt(k,y) for y in range(3)],
            [pt(x,k) for x in range(3)],
            [pt(x,y) for x in range(3) for y in range(3) if (x+y)%3==k]
        )]
    rows=[list(r) for b in range(3) for r in affine(9*b)]
    rng=random.Random(278)
    edges=((0,1),(1,2),(2,0))
    for step in range(3+(278%7)):
        a,b=edges[step%3]
        ra=rng.randrange(9*a,9*a+9)
        rb=rng.randrange(9*b,9*b+9)
        ia,ib=rng.randrange(3),rng.randrange(3)
        rows[ra][ia],rows[rb][ib]=rows[rb][ib],rows[ra][ia]
    return tuple(tuple(sorted(row)) for row in rows)


def structure():
    assert independent_reconstructor()==ROWS
    n=len(ROWS)
    assert n==27
    assert hashlib.sha256(json.dumps(ROWS,separators=(",",":")).encode()).hexdigest()==ROW_SHA256
    assert all(len(row)==3 and len(set(row))==3 and all(0<=j<n for j in row)
               for row in ROWS)
    assert Counter(j for row in ROWS for j in row)==Counter({j:3 for j in range(n)})
    pairs=[tuple(sorted((a,b))) for row in ROWS for a,b in itertools.combinations(row,2)]
    assert len(set(pairs))==3*n
    adjacency=[set() for _ in range(n)]
    for row in ROWS:
        for i in row:adjacency[i].update(row)
    seen={0};stack=[0]
    while stack:
        for j in adjacency[stack.pop()]-seen:
            seen.add(j);stack.append(j)
    assert len(seen)==n


def basis_exact():
    n=len(ROWS)
    high={}
    for row in ROWS:
        w=sum(1<<j for j in row)
        while w:
            p=w.bit_length()-1
            if p in high:w^=high[p]
            else:high[p]=w;break
    # Independent low-pivot rank implementation.
    low={}
    for row in ROWS:
        w=sum(1<<j for j in row)
        while w:
            p=(w&-w).bit_length()-1
            if p in low:w^=low[p]
            else:low[p]=w;break
    assert len(high)==len(low)==24
    basis=[]
    for free in range(n):
        if free in high:continue
        v=1<<free
        # IMPORTANT: flip pivot *coordinate* bit, not pivot equation vector.
        for p in sorted(high):
            if (high[p]&v).bit_count()%2:v^=1<<p
        assert all((v&sum(1<<j for j in row)).bit_count()%2==0
                   for row in ROWS)
        basis.append(v)
    assert len(basis)==3
    return basis


def actual_sat_models(basis):
    n=len(ROWS)
    good=[]
    for co in range(1<<len(basis)):
        v=0
        for i,b in enumerate(basis):
            if co>>i&1:v^=b
        x=((1<<n)-1)^v
        if all(sum(x>>j&1 for j in row)==1 for row in ROWS):
            ones=tuple(j for j in range(n) if x>>j&1)
            assert len(ones)==n//3
            good.append((co,ones))
    assert good==[(7,EXPECTED_MODEL_ONE_INDICES)],good
    return good


def coefficient_column(row,u,labels):
    out=Counter([u]+[u^labels[j] for j in row])
    return dict(out)


def det_bareiss(matrix):
    a=[row[:] for row in matrix]
    n=len(a);sign=1;last=1
    for k in range(n-1):
        if not a[k][k]:
            pivot=next((i for i in range(k+1,n) if a[i][k]),None)
            if pivot is None:return 0
            a[k],a[pivot]=a[pivot],a[k];sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                val=a[i][j]*pivot-a[i][k]*a[k][j]
                assert val%last==0
                a[i][j]=val//last
            a[i][k]=0
        last=pivot
    return sign*a[-1][-1]


def det_leibniz(matrix):
    n=len(matrix);total=0
    for p in itertools.permutations(range(n)):
        prod=1
        for i,j in enumerate(p):
            prod*=matrix[i][j]
            if not prod:break
        if prod:
            inversions=sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
            total+=(-1 if inversions%2 else 1)*prod
    return total


def exact_fourier_rank_and_gram_falsifier(basis, model_co):
    n=len(ROWS);d=len(basis)
    labels=[sum(1<<i for i,v in enumerate(basis) if v>>j&1)
            for j in range(n)]
    Q1=sorted(set([0]+labels))
    assert Q1==[0,1,2,3,4,6,7]
    columns={(ri,u):coefficient_column(row,u,labels)
             for ri,row in enumerate(ROWS) for u in Q1}
    # Each legal generator g_r chi_u vanishes at real SAT model.
    def ch(q,co):
        return (-1 if (q&co).bit_count()%2 else 1)
    for (_, _),col in columns.items():
        assert sum(v*ch(q,model_co) for q,v in col.items())==0
    # Rational independence: a NONZERO INTEGER determinant, not modular.
    minor=[[columns[key].get(q,0) for key in SELECTED] for q in range(1,8)]
    da=det_bareiss(minor);db=det_leibniz(minor)
    assert da==db==8,(da,db)
    # One model: rational function space vanishing there has dimension 7.
    # So degree1 columns span it exactly. Their Gram residual is point delta.
    coeff={q:Fraction(ch(q,model_co),1<<d) for q in range(1<<d)}
    assert coeff[0]==Fraction(1,8)
    assert sum(abs(v) for q,v in coeff.items() if q)!=coeff[0]
    assert sum(abs(v) for q,v in coeff.items() if q)==Fraction(7,8)
    assert sum(v*v for v in coeff.values())==coeff[0]
    for point in range(1<<d):
        H=sum(v*ch(q,point) for q,v in coeff.items())
        assert H==int(point==model_co),(point,H)
    for col in columns.values():
        assert sum(coeff.get(q,0)*v for q,v in col.items())==0
    assert (1<<d)*coeff[0]==1
    return {
        "full_M1_generators_checked":len(columns),
        "Q1_distinct_shifts":len(Q1),
        "independent_integer_minor_columns":[list(s) for s in SELECTED],
        "independent_integer_minor_rows":[1,2,3,4,5,6,7],
        "determinant_bareiss":da,"determinant_leibniz":db,
        "rank_Q_full_M1":7,
        "vanishing_ideal_dimension":7,
        "exact_gram_projection_h0":str(coeff[0]),
        "l1_tail":str(sum(abs(v) for q,v in coeff.items() if q)),
        "upper_sat_bound":str((1<<d)*coeff[0]),
        "every_degree_k_ge_1":"UNKNOWN_SOUND",
    }


def main():
    structure()
    basis=basis_exact()
    models=actual_sat_models(basis)
    evidence=exact_fourier_rank_and_gram_falsifier(basis,models[0][0])
    print(json.dumps({
        "gate":"BABEL24_CONNECTED_UNIQUE_SAT_GRAM_L1_COMPLETENESS_FALSIFIER",
        "n":len(ROWS),"source_sha256":ROW_SHA256,
        "connected_linear_cubic_square":"EXACT_PASS",
        "GF2_rank":24,"GF2_nullity":3,
        "parity_words_exhaustively_checked":8,
        "SAT_count":len(models),
        "unique_SAT_model_ones":list(models[0][1]),
        "unique_SAT_kernel_coordinates":models[0][0],
        "exact_rational_evidence":evidence,
        "BABEL23_TWO_SUFFICIENT_GATES_UNIVERSALLY_COMPLETE":"DISPROVED",
        "universal_UNSAT_degree2_completeness":"OPEN",
        "P_vs_NP":"OPEN",
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
