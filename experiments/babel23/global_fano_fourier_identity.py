#!/usr/bin/env python3
"""BABEL-23D: independent full-Fourier proof of all-n Fano-coupler identity.

Reconstructs the family DIRECTLY, does NOT import the family producer.
Checks the complete Fourier character coefficient vector as a sparse map;
DOES NOT enumerate 2^d states and DOES NOT use floats/modular-only ranks.
"""
import hashlib
import json
from collections import Counter


LINES=((0,1,3),(1,2,4),(2,3,5),(3,4,6),(0,4,5),(1,5,6),(0,2,6))
MODS={0:(0,0),1:(1,2),5:(2,5)}  # local row -> (edge color, removed literal)


def from_direct_formula(m):
    assert m>=3
    rows=[]
    for block in range(2*m):
        for row_index,line in enumerate(LINES):
            if row_index not in MODS:
                row=tuple(sorted(7*block+i for i in line))
            else:
                color,outvar=MODS[row_index]
                neighbor=(m+(block+color)%m if block<m
                          else (block-m-color)%m)
                row=tuple(sorted(
                    [7*block+i for i in line if i!=outvar]+
                    [7*neighbor+outvar]
                ))
            rows.append(row)
    return rows


def parity_labels(rows):
    n=len(rows)
    assert all(len(row)==3 and len(set(row))==3 for row in rows)
    assert Counter(j for row in rows for j in row)==Counter({j:3 for j in range(n)})
    pairs=[tuple(sorted((u,v))) for row in rows for u in row for v in row if u<v]
    assert len(set(pairs))==3*n
    piv={}
    for row in rows:
        bits=sum(1<<j for j in row)
        while bits:
            high=bits.bit_length()-1
            if high in piv:bits^=piv[high]
            else:piv[high]=bits;break
    basis=[]
    for free in range(n):
        if free in piv:continue
        bits=1<<free
        for high in sorted(piv):
            if (bits&piv[high]).bit_count()%2:
                bits^=1<<high
        assert all((bits&sum(1<<j for j in row)).bit_count()%2==0
                   for row in rows)
        basis.append(bits)
    labels=[sum((1<<k) for k,v in enumerate(basis) if v>>j&1)
            for j in range(n)]
    return basis,labels


def certificate(m):
    rows=from_direct_formula(m)
    basis,labels=parity_labels(rows)
    B=2*m
    out=Counter()
    formal_terms=0
    def add(row_index,shift,weight):
        nonlocal formal_terms
        formal_terms+=1
        freqs=[shift]+[shift^labels[j] for j in rows[row_index]]
        for q in freqs:
            out[q]+=weight
            if not out[q]:del out[q]
    for block in range(B):
        for row in range(1,7):
            add(7*block+row,0,1)
        add(7*block,0,-2)
        add(7*block,labels[7*block+6],-3)
    assert formal_terms==8*B
    assert out=={0:4*B},("FULL_FOURIER_IDENTITY_FAIL",m,out.most_common(12))
    return {
        "m":m,"n":len(rows),"B":B,
        "kernel_dimension":len(basis),
        "formal_degree_leq_1_terms":formal_terms,
        "rational_coefficient_denominator":4*B,
        "final_Fourier_nonzero_frequencies":len(out),
        "final_constant_integer_coefficient":out[0],
        "full_Fourier_replay":"EXACT_PASS",
        "rows_sha256":hashlib.sha256(json.dumps(rows,separators=(",",":")).encode()).hexdigest()
    }


def main():
    checks=[certificate(m) for m in (3,6,9,12)]
    assert [x["kernel_dimension"] for x in checks]==[10,19,28,37]
    print(json.dumps({
        "gate":"BABEL23D_EXPLICIT_ALL_N_FANO_COUPLER_DEGREE1_IDENTITY",
        "all_n_symbolic_derivation":"IN_RESEARCH_THEOREM",
        "independent_all_frequency_exact_replay":"PASS",
        "construction_does_not_enumerate_2_pow_d":True,
        "universal_degree1_SCL_completeness":"NOT_PROVED",
        "P_vs_NP":"OPEN",
        "cases":checks
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
