#!/usr/bin/env python3
import itertools, json


def rref_gf2(rows, w):
    rows=[list(r) for r in rows]
    rank=0
    pivots=[]
    for col in range(w):
        pivot=next((i for i in range(rank,len(rows)) if rows[i][col]),None)
        if pivot is None:
            continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        for i in range(len(rows)):
            if i!=rank and rows[i][col]:
                rows[i]=[a^b for a,b in zip(rows[i],rows[rank])]
        pivots.append(col)
        rank+=1
    inconsistent=any(not any(r[:w]) and r[w] for r in rows)
    rows=sorted(rows, key=lambda r:(next((i for i,x in enumerate(r[:w]) if x),w),r))
    return rows,rank,pivots,inconsistent


def sat_assignment(a, rows, w):
    return all((sum((row[i]&a[i]) for i in range(w))&1)==row[w] for row in rows)


def make_structured_system(w):
    rows=[]
    # A connected affine boundary language with only O(w) equations but exponentially many potential assignments.
    # x_i xor x_{i+1} = (i mod 2), plus one long parity check to make the signature nontrivial.
    for i in range(w-1):
        r=[0]*(w+1)
        r[i]=1; r[i+1]=1; r[w]=i&1
        rows.append(r)
    r=[1]*w+[w&1]
    rows.append(r)
    return rows


def enumerate_solution_count(rows,w):
    count=0
    for bits in itertools.product([0,1], repeat=w):
        if sat_assignment(bits,rows,w): count+=1
    return count

checks=[]
for w in range(2,13):
    rows=make_structured_system(w)
    rr,rank,pivots,bad=rref_gf2(rows,w)
    assert not bad
    # Exhaustive replay only for small fixtures. It verifies that RREF preserves exactly the same boundary relation.
    original_count=enumerate_solution_count(rows,w)
    reduced_count=enumerate_solution_count(rr,w)
    assert original_count==reduced_count
    assert all(sat_assignment(bits,rows,w)==sat_assignment(bits,rr,w)
               for bits in itertools.product([0,1],repeat=w))
    # Dense encoded signature length is polynomial in w; compare symbolically with raw truth-table state space 2^w.
    encoded_bits=len(rr)*(w+1)
    checks.append({
        'w':w,
        'raw_assignment_space':2**w,
        'equations_in':len(rows),
        'rank':rank,
        'solutions':original_count,
        'rref_rows':len(rr),
        'dense_signature_bits_upper_bound':encoded_bits,
        'exact_relation_preserved':True
    })

print(json.dumps({
    'gate_id':'R44J_STRUCTURE_TO_SMALL_SIGNATURE',
    'route':'AFFINE_BOUNDARY_SIGNATURE_GF2_V1',
    'checks':checks,
    'result':'STRUCTURED_BOUNDARY_RELATION_COMPRESSED_EXACTLY',
    'r44i_universal_quotient_barrier_refuted':False,
    'meaning':'The exact boundary object can sometimes be stored as a polynomial symbolic relation rather than as one state per assignment. This is a representation switch on a recognized affine class, not a universal 3CNF theorem.',
    'U1':'OPEN',
    'P_EQUALS_NP':'NOT_PROVED',
    'P_VS_NP':'OPEN',
    'next_gate':'R44K_SIGNATURE_SWITCHBOARD_OUTSIDE_AFFINE_CLASS'
}, sort_keys=True))
