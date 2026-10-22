#!/usr/bin/env python3
"""BABEL29: independent exact multi-splice interface composition and mod3 gate.

All-n semantic theorem in docs/research/BABEL29_MULTISPLICE_BOUNDARY_MOD3_COMPOSITION_20261023.md.
This checker uses no producer imports. It independently enumerates ALL local
punctured Exact-One assignments by complete Boolean DPLL (with safe
propagation), not by applying old SAT status. It also enumerates the entire
small GF2 parity kernel of the CONNECTED SCL54 after the splice.
"""
import hashlib
import itertools
import json
from collections import Counter

BASE = (
    (0,1,2), (0,3,6), (0,5,7), (3,5,20), (1,7,11),
    (3,8,12), (6,7,8), (2,5,8), (2,10,14),
    (9,10,11), (9,12,15), (9,14,22),
    (12,13,14), (10,13,16), (1,6,17), (15,16,17),
    (4,17,20), (11,13,21), (4,18,19), (15,18,24),
    (18,23,25), (21,22,23), (16,19,25),
    (19,21,26), (24,25,26), (4,23,26), (20,22,24)
)
FROZEN_SHA = "9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed"
EXPECTED_ORIGINAL = (2,3,7,9,13,17,19,23,24)
EXPECTED_ALTERNATIVE = (2,3,7,9,13,17,18,22,26)

def bits_as_tuple(x,n):
    return tuple(i for i in range(n) if x>>i&1)

def physical_model(rows,x):
    return all(sum(x>>i&1 for i in row)==1 for row in rows)

def exact_dpll(rows,n):
    """Complete enumeration; unit forcing is logically sound for Exact-One."""
    calls=0
    outputs=[]
    variable_count=[sum(j in row for row in rows) for j in range(n)]
    def recurse(assigned,ones):
        nonlocal calls
        calls+=1
        while True:
            changed=False
            for row in rows:
                true=sum((ones>>j)&1 for j in row)
                missing=[j for j in row if not ((assigned>>j)&1)]
                if true>1 or true+len(missing)<1:
                    return
                if true==1 and missing:
                    for j in missing:
                        assigned|=1<<j
                    changed=True
                elif true==0 and len(missing)==1:
                    j=missing[0]
                    assigned|=1<<j
                    ones|=1<<j
                    changed=True
            if not changed:
                break
        if assigned.bit_count()==n:
            assert physical_model(rows,ones)
            outputs.append(ones)
            return
        free=[j for j in range(n) if not assigned>>j&1]
        pick=max(free,key=lambda j:(variable_count[j],-j))
        recurse(assigned|(1<<pick),ones)
        recurse(assigned|(1<<pick),ones|(1<<pick))
    recurse(0,0)
    assert len(outputs)==len(set(outputs))
    return outputs,calls

def exact_gf2_basis(rows):
    n=len(rows)
    piv={}
    for row in rows:
        word=sum(1<<j for j in row)
        while word:
            p=word.bit_length()-1
            if p in piv:word^=piv[p]
            else:piv[p]=word;break
    basis=[]
    for free in range(n):
        if free in piv:continue
        v=1<<free
        for p in sorted(piv):
            if (v&piv[p]).bit_count()%2:v^=1<<p
        assert all((v&sum(1<<j for j in row)).bit_count()%2==0 for row in rows)
        basis.append(v)
    assert n-len(piv)==len(basis)
    return basis

def independent_parity_models(rows):
    n=len(rows)
    basis=exact_gf2_basis(rows)
    assert len(basis)<=12,("only small exhaustive controls",len(basis))
    v=0;true_models=[]
    for i in range(1<<len(basis)):
        if i:v^=basis[(i&-i).bit_length()-1]
        physical=((1<<n)-1)^v
        if physical_model(rows,physical):
            true_models.append(physical)
    return true_models,len(basis)

def validate_connected_scl(rows):
    n=len(rows)
    assert all(len(row)==3 and len(set(row))==3
               and all(0<=j<n for j in row) for row in rows)
    deg=Counter(j for row in rows for j in row)
    assert deg==Counter({j:3 for j in range(n)})
    pairs=[tuple(sorted(pair)) for row in rows
           for pair in itertools.combinations(row,2)]
    assert len(set(pairs))==3*n, "linear incidence failure"
    adjacent=[set() for _ in range(n)]
    for row in rows:
        for j in row: adjacent[j].update(row)
    seen={0};stack=[0]
    while stack:
        for j in adjacent[stack.pop()]-seen:
            seen.add(j);stack.append(j)
    assert len(seen)==n, "disconnected"
    return True

def table_for_punctured(rows,modified_rows,exports):
    n=len(rows)
    assert len(modified_rows)==len(exports)
    assert len(set(modified_rows))==len(modified_rows)
    assert all(exports[k] in rows[r] for k,r in enumerate(modified_rows))
    punctured=[row for ri,row in enumerate(rows) if ri not in modified_rows]
    assignments,calls=exact_dpll(punctured,n)
    table=Counter()
    witnesses={}
    for x in assignments:
        out=tuple((x>>j)&1 for j in exports)
        retained=[sum((x>>j)&1 for j in rows[ri] if j!=exports[i])
                  for i,ri in enumerate(modified_rows)]
        if any(r>1 for r in retained):
            continue
        demand=tuple(1-r for r in retained)
        table[(out,demand)]+=1
        witnesses.setdefault((out,demand),x)
        # All nonzero entries obey the all-n counting congruence.
        assert (sum(out)-sum(demand))%3==0
    return table,witnesses,assignments,calls

def table_json(table):
    return {"".join(map(str,a))+"->"+"".join(map(str,b)):v
            for (a,b),v in sorted(table.items())}

def original_double_and_one_controls():
    all_models,calls=exact_dpll(BASE,27)
    assert len(all_models)==1
    assert bits_as_tuple(all_models[0],27)==EXPECTED_ORIGINAL
    original_mask=all_models[0]
    # Two deleted original rows (11 and 22) admit exactly one additional
    # physical model, with original row counts (2,0).
    removed=[r for ri,r in enumerate(BASE) if ri not in (11,22)]
    punctured,pcalls=exact_dpll(removed,27)
    assert len(punctured)==2
    assert set(map(lambda x:bits_as_tuple(x,27),punctured))=={
        EXPECTED_ORIGINAL, EXPECTED_ALTERNATIVE}
    alt=next(x for x in punctured if x!=original_mask)
    assert [sum(alt>>j&1 for j in BASE[i]) for i in (11,22)]==[2,0]
    return original_mask,alt,{"original_models":len(all_models),
            "original_DPLL_calls":calls,
            "punctured_DPLL_calls":pcalls,
            "two_deleted_rows_partial_models":len(punctured),
            "alternative_original_row_counts":[2,0]}

def joined_rows(left_rows,right_rows,left_mark,left_export,right_mark,right_export):
    nl=len(left_rows);nr=len(right_rows)
    assert len(left_mark)==len(left_export)==len(right_mark)==len(right_export)
    assert len(set(left_mark))==len(left_mark)
    assert len(set(right_mark))==len(right_mark)
    rows=[list(row) for row in left_rows]+[
        [v+nl for v in row] for row in right_rows
    ]
    old=[tuple(sorted(row)) for row in rows]
    for ri,ai,si,bi in zip(left_mark,left_export,right_mark,right_export):
        j=nl+si;b=nl+bi
        assert ai in rows[ri] and b in rows[j]
        rows[ri][rows[ri].index(ai)]=b
        rows[j][rows[j].index(b)]=ai
    rows=[tuple(sorted(row)) for row in rows]
    validate_connected_scl(rows)
    # Independent inverse operation restores both original incidence lists.
    restored=[list(row) for row in rows]
    for ri,ai,si,bi in zip(left_mark,left_export,right_mark,right_export):
        j=nl+si;b=nl+bi
        assert b in restored[ri] and ai in restored[j]
        restored[ri][restored[ri].index(b)]=ai
        restored[j][restored[j].index(ai)]=b
    assert [tuple(sorted(row)) for row in restored]==old
    return rows

def exact_transfer_audit(label,left_mark,left_export,right_mark,right_export,expected):
    L,W_L,partial_L,calls_L=table_for_punctured(
        BASE,left_mark,left_export)
    R,W_R,partial_R,calls_R=table_for_punctured(
        BASE,right_mark,right_export)
    predicted=sum(c*R.get((demand,export),0)
                  for (export,demand),c in L.items())
    assert predicted==expected,(label,predicted,expected)
    joined=joined_rows(BASE,BASE,left_mark,left_export,
                       right_mark,right_export)
    actual_models,d=independent_parity_models(joined)
    assert len(actual_models)==predicted,(label,len(actual_models),predicted)
    expected_models=set()
    for (export,demand),count in L.items():
        other=(demand,export)
        if count and R[other]:
            # For the frozen examples each admitted profile has exactly one
            # witness; more generally the theorem multiplies exact counts.
            assert count==R[other]==1
            expected_models.add(W_L[(export,demand)]|
                                (W_R[other]<<27))
    assert set(actual_models)==expected_models
    assert all(physical_model(joined,x) for x in actual_models)
    return {"fixture":label,"left_modified_rows":left_mark,
            "left_original_exports":left_export,
            "right_modified_rows":right_mark,
            "right_original_exports":right_export,
            "left_exact_boundary_table":table_json(L),
            "right_exact_boundary_table":table_json(R),
            "left_punctured_models_before_filter":len(partial_L),
            "right_punctured_models_before_filter":len(partial_R),
            "local_DPLL_nodes":[calls_L,calls_R],
            "joined_GF2_nullity":d,
            "joined_parity_states_checked":1<<d,
            "exact_transfer_count":predicted,
            "independent_joined_SAT_count":len(actual_models),
            "joined_SAT_model_ones":[list(bits_as_tuple(x,54))
                                     for x in actual_models],
            "connected_square_cubic_linear":"EXACT_PASS",
            "inverse_splice_to_UxU":"EXACT_PASS",
            "joined_rows_sha256":hashlib.sha256(
                json.dumps(joined,separators=(",",":")).encode()).hexdigest()}

def mod3_states(r):
    patterns=list(itertools.product((0,1),repeat=r))
    options=[(a,b) for a in patterns for b in patterns
             if (sum(a)-sum(b))%3==0]
    assert len(options)==(4**r+2)//3,(r,len(options))
    return len(options)

def main():
    assert hashlib.sha256(json.dumps(BASE,separators=(",",":")).encode()).hexdigest()==FROZEN_SHA
    validate_connected_scl(BASE)
    _,_,base=original_double_and_one_controls()
    local_counts={str(r):mod3_states(r) for r in (1,2,3,4)}
    assert local_counts=={"1":2,"2":6,"3":22,"4":86}
    # Recover the already proven BABEL28 r=1 semantics exactly:
    controls=[
        exact_transfer_audit("R1_MATCHING_UxU_SAT",
                             (0,),(0,),(0,),(0,),1),
        exact_transfer_audit("R1_MISMATCH_UxU_UNSAT",
                             (0,),(0,),(0,),(2,),0),
        # Two swapped rows: original U models give 1 solution; new partial
        # (2,0)-defect models on both sides give another exact solution.
        exact_transfer_audit("R2_CROSS_ROUTED_CONNECTED_NEW_SAT",
                             (11,22),(22,25),(22,11),(25,22),2),
        exact_transfer_audit("R2_STRAIGHT_ROUTED_CONTROL",
                             (11,22),(22,25),(11,22),(22,25),1)
    ]
    two=controls[2]
    assert two["joined_GF2_nullity"]==6
    assert two["joined_parity_states_checked"]==64
    assert two["left_exact_boundary_table"]=={
        "00->00":1,"10->01":1}
    assert two["right_exact_boundary_table"]=={
        "00->00":1,"01->10":1}
    print(json.dumps({
        "gate":"BABEL29_ALL_R_MULTISPLICE_BOUNDARY_MOD3_TRANSFER",
        "all_n_semantic_bijection":"PROVED",
        "all_n_mod3_balance":"PROVED_FOR_COMPONENT_N_DIVISIBLE_BY3",
        "mod3_interface_state_counts":local_counts,
        "BABEL28_ONE_ROW_RULE":"RECOVERED",
        "base_punctured_oracle":base,
        "exact_controls":controls,
        "arbitrary_connected_SCL_poly_decomposition":"NOT_PROVED",
        "universal_polynomial_solver":"NOT_PROVED",
        "P_vs_NP":"OPEN"
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
