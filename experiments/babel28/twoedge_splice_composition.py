#!/usr/bin/env python3
"""BABEL28 independent exact 2-state incidence-splice SAT composition audit.

Standard library only, no imports from prior BABEL producer code. Exact GF2
enumeration is restricted to small SCL27/SCL54 fixtures. All-n theorem in doc.
"""
import hashlib
import itertools
import json
from collections import Counter

U=(
    (0,1,2),(0,3,6),(0,5,7),(3,5,20),(1,7,11),
    (3,8,12),(6,7,8),(2,5,8),(2,10,14),
    (9,10,11),(9,12,15),(9,14,22),
    (12,13,14),(10,13,16),(1,6,17),(15,16,17),
    (4,17,20),(11,13,21),(4,18,19),(15,18,24),
    (18,23,25),(21,22,23),(16,19,25),
    (19,21,26),(24,25,26),(4,23,26),(20,22,24)
)
SHA="9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed"
MODEL_ONES=(2,3,7,9,13,17,19,23,24)


def mask(row):return sum(1<<j for j in row)


def valid_structure(rows):
    n=len(rows)
    assert all(len(r)==3 and len(set(r))==3 for r in rows)
    assert Counter(v for row in rows for v in row)==Counter({v:3 for v in range(n)})
    pairs=[tuple(sorted(pair)) for row in rows for pair in itertools.combinations(row,2)]
    assert len(set(pairs))==3*n
    adj=[set() for _ in range(n)]
    for row in rows:
        for v in row:adj[v].update(row)
    q=[0];seen={0}
    while q:
        for a in adj[q.pop()]-seen:seen.add(a);q.append(a)
    assert len(seen)==n
    return True


def gf2_basis(rows):
    n=len(rows);pivs={}
    for row in rows:
        x=mask(row)
        while x:
            p=x.bit_length()-1
            if p in pivs:x^=pivs[p]
            else:pivs[p]=x;break
    out=[]
    for free in range(n):
        if free in pivs:continue
        v=1<<free
        for p in sorted(pivs):
            if (v&pivs[p]).bit_count()%2:v^=1<<p
        assert all((v&mask(row)).bit_count()%2==0 for row in rows)
        out.append(v)
    return out


def models_by_parity(rows):
    n=len(rows);basis=gf2_basis(rows)
    assert len(basis)<=12,("finite oracle only",n,len(basis))
    models=[];v=0
    for i in range(1<<len(basis)):
        if i:v^=basis[(i&-i).bit_length()-1]
        x=((1<<n)-1)^v
        if all(sum((x>>j)&1 for j in row)==1 for row in rows):
            models.append(x)
    return models,len(basis)


def local_spectra(rows,a):
    models,d=models_by_parity(rows)
    return (sum(not(x>>a&1) for x in models),
            sum(bool(x>>a&1) for x in models)),models,d


def independent_join(a,b):
    assert a in U[0] and b in [27+j for j in U[0]]
    old=list(U)+[tuple(v+27 for v in row) for row in U]
    updated=[list(row) for row in old]
    updated[0][updated[0].index(a)]=b
    updated[27][updated[27].index(b)]=a
    final=[tuple(sorted(row)) for row in updated]
    assert valid_structure(final)
    for ri,(old_row,new_row) in enumerate(zip(old,final)):
        assert mask(old_row)^mask(new_row) == (((1<<a)|(1<<b)) if ri in (0,27) else 0)
    return final


def recover_original_components(joined):
    """Recognize TWO oriented crossing incidences and reverse them."""
    r,s=0,27
    cross_in_left=[v for v in joined[r] if v>=27]
    cross_in_right=[v for v in joined[s] if v<27]
    assert len(cross_in_left)==len(cross_in_right)==1
    b=cross_in_left[0];a=cross_in_right[0]
    # Exactly two crossing incidences globally.
    assert sum(v>=27 for row in joined[:27] for v in row)==1
    assert sum(v<27 for row in joined[27:] for v in row)==1
    restored=[list(row) for row in joined]
    restored[r][restored[r].index(b)]=a
    restored[s][restored[s].index(a)]=b
    left=[tuple(sorted(row)) for row in restored[:27]]
    right=[tuple(sorted(v-27 for v in row)) for row in restored[27:]]
    assert tuple(left)==tuple(U)
    assert tuple(right)==tuple(U)
    assert valid_structure(left) and valid_structure(right)
    assert len(left)%3==len(right)%3==0
    return left,right,a,b


def audit(a,b,expected_count):
    joined=independent_join(a,b)
    left,right,aa,bb=recover_original_components(joined)
    assert aa==a and bb==b
    profile_L,models_L,dL=local_spectra(left,a)
    profile_R,models_R,dR=local_spectra(right,b-27)
    assert len(models_L)==len(models_R)==1
    expected=profile_L[0]*profile_R[0]+profile_L[1]*profile_R[1]
    assert expected==expected_count
    joint_models,djoint=models_by_parity(joined)
    assert len(joint_models)==expected_count, (a,b,expected_count,len(joint_models))
    products=set()
    for xL in models_L:
        for xR in models_R:
            if ((xL>>a)&1)==((xR>>(b-27))&1):
                products.add(xL|(xR<<27))
    assert set(joint_models)==products
    for x in joint_models:
        assert all(sum(x>>j&1 for j in row)==1 for row in joined)
    return {
        "n":len(joined),"a":a,"b":b,
        "component_L_boundary":profile_L,"component_R_boundary":profile_R,
        "component_L_dimK":dL,"component_R_dimK":dR,
        "connected_join_dimK":djoint,
        "exact_2state_count":expected,
        "independent_full_GF2_sat_count":len(joint_models),
        "independent_restored_components":"BOTH_EXACTLY_FROZEN_U",
        "all_row_models_replayed":True,
        "SAT_status":"SAT" if joint_models else "UNSAT",
        "rows_sha256":hashlib.sha256(json.dumps(joined,separators=(",",":")).encode()).hexdigest()
    }


def main():
    assert hashlib.sha256(json.dumps(U,separators=(",",":")).encode()).hexdigest()==SHA
    assert valid_structure(U)
    base_models,bd=models_by_parity(U)
    assert len(base_models)==1 and bd==3
    assert tuple(i for i in range(27) if (base_models[0]>>i)&1)==MODEL_ONES
    # Equal boundary bits on the two component models: SAT.
    positive=audit(0,27,1)
    # Unequal original boundary bits on TWO SAT components: UNSAT.
    negative=audit(0,29,0)
    assert positive["component_L_boundary"]==[1,0] or positive["component_L_boundary"]==(1,0)
    assert negative["component_R_boundary"]==[0,1] or negative["component_R_boundary"]==(0,1)
    print(json.dumps({
        "gate":"BABEL28_EXACT_TWO_EDGE_SPLICE_2STATE_COMPOSITION",
        "all_n_solution_bijection":"PROVED",
        "local_boundary_count_formula":"N_L0*N_R0+N_L1*N_R1",
        "connected_SAT_control":positive,
        "connected_UNSAT_control":negative,
        "general_SCL_POLY_boundary_discovery":"OPEN",
        "universal_poly_solver":"NOT_PROVED",
        "P_vs_NP":"OPEN"
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
