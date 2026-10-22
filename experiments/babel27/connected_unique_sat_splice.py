#!/usr/bin/env python3
"""BABEL27 independent connected unique-SAT splice / Gram degree no-go.

All-n math in docs. This exact checker confirms finite structural controls
without importing any BABEL producer and without enumerating large K spaces.
"""
import hashlib
import itertools
import json
from collections import Counter

BASE = (
    (0,1,2),(0,3,6),(0,5,7),(3,5,20),(1,7,11),
    (3,8,12),(6,7,8),(2,5,8),(2,10,14),
    (9,10,11),(9,12,15),(9,14,22),
    (12,13,14),(10,13,16),(1,6,17),(15,16,17),
    (4,17,20),(11,13,21),(4,18,19),(15,18,24),
    (18,23,25),(21,22,23),(16,19,25),
    (19,21,26),(24,25,26),(4,23,26),(20,22,24)
)
BASE_SHA = "9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed"
BASE_TRUE = (2,3,7,9,13,17,19,23,24)
SIZES = (1,2,3,5,9,20,64)


def mask(row):
    return sum(1<<i for i in row)


def validate(rows):
    n=len(rows)
    assert all(len(row)==3 and len(set(row))==3 and all(0<=v<n for v in row)
               for row in rows)
    assert Counter(v for row in rows for v in row)==Counter({v:3 for v in range(n)})
    seen_pairs=set()
    for row in rows:
        for pair in itertools.combinations(sorted(row),2):
            assert pair not in seen_pairs,("nonlinear",pair)
            seen_pairs.add(pair)
    assert len(seen_pairs)==3*n
    adjacency=[[] for _ in range(n)]
    for row in rows:
        for v in row:
            adjacency[v].append(row)
    seen={0};queue=[0]
    while queue:
        here=queue.pop()
        for row in adjacency[here]:
            for nxt in row:
                if nxt not in seen:seen.add(nxt);queue.append(nxt)
    assert len(seen)==n,("disconnected",n,len(seen))
    return True


def rank_and_basis(rows):
    n=len(rows);piv={}
    for row in rows:
        w=mask(row)
        while w:
            p=w.bit_length()-1
            if p in piv:w^=piv[p]
            else:piv[p]=w;break
    basis=[]
    for free in range(n):
        if free in piv:continue
        v=1<<free
        for p in sorted(piv):
            if (piv[p]&v).bit_count()%2:v^=1<<p
        assert all((v&mask(r)).bit_count()%2==0 for r in rows)
        basis.append(v)
    return len(piv),basis


def low_pivot_rank(rows):
    piv={}
    for row in rows:
        w=mask(row)
        while w:
            p=(w&-w).bit_length()-1
            if p in piv:w^=piv[p]
            else:piv[p]=w;break
    return len(piv)


def x_true_mask(t):
    base=sum(1<<k for k in BASE_TRUE)
    return sum(base<<(27*i) for i in range(t))


def is_sat(rows,x):
    return all(sum((x>>v)&1 for v in row)==1 for row in rows)


def enumerate_physical_models(rows,basis):
    total=len(basis)
    assert total<=13,"independent exhaustive oracle must stay small"
    n=len(rows);allones=(1<<n)-1
    good=[]
    v=0
    for step in range(1<<total):
        if step:v^=basis[(step&-step).bit_length()-1]
        x=allones^v
        if is_sat(rows,x):good.append(x)
    return good


def splice_new_base(previous,step):
    """Join connected previous block of 27*(step-1) with fresh copy."""
    old_n=len(previous)
    before=list(previous)+[tuple(v+old_n for v in r) for r in BASE]
    assert old_n==27*(step-1)
    old_x=x_true_mask(step-1)
    new_x=sum(1<<(old_n+v) for v in BASE_TRUE)
    r=0;s=old_n
    a=min(v for v in before[r] if ((old_x>>v)&1)==0)
    b=min(v for v in before[s] if ((new_x>>v)&1)==0)
    assert ((old_x>>a)&1)==((new_x>>b)&1)==0
    after=[list(row) for row in before]
    after[r][after[r].index(a)]=b
    after[s][after[s].index(b)]=a
    joined=[tuple(sorted(row)) for row in after]
    # Compute the exact rank-one incidence update in GF(2).
    for i,(row_old,row_new) in enumerate(zip(before,joined)):
        delta=mask(row_old)^mask(row_new)
        assert delta==( ((1<<a)|(1<<b)) if i in (r,s) else 0),(step,i,delta)
    assert is_sat(joined,x_true_mask(step))
    return joined,{"left_incidence_row":r,"right_incidence_row":s,
                   "left_zero_literal":a,"right_zero_literal":b,
                   "rank_one_update_exact":True}


def main():
    assert hashlib.sha256(json.dumps(BASE,separators=(",",":")).encode()).hexdigest()==BASE_SHA
    assert validate(BASE)
    rb,bb=rank_and_basis(BASE)
    assert rb==low_pivot_rank(BASE)==24
    assert len(bb)==3
    oracle=enumerate_physical_models(BASE,bb)
    assert oracle==[x_true_mask(1)]
    rows=list(BASE)
    records=[]
    previous_rank=rb
    for step in range(1,65):
        receipt=None
        if step>1:
            rows,receipt=splice_new_base(rows,step)
            # Independent exact per-step all-n invariants and connectedness.
            validate(rows)
        if step in SIZES:
            rank,basis=rank_and_basis(rows)
            assert rank==low_pivot_rank(rows)
            nullity=len(basis)
            n=len(rows)
            assert n==27*step
            assert nullity>=2*step+1,(step,nullity)
            assert is_sat(rows,x_true_mask(step))
            if step>1:
                # t-1 global rank-one splices: rank<=24t+(t-1).
                assert rank<=24*step+(step-1)
            full_oracle=None
            if step<=3 and len(basis)<=13:
                full_oracle=enumerate_physical_models(rows,basis)
                assert full_oracle==[x_true_mask(step)]
            E2_upper=n*(1+n+n*(n-1)//2)
            S2_upper=1+4*E2_upper
            full_indicator_support=1<<nullity
            record={
              "blocks":step,"n":n,"connected":True,
              "exact_GF2_rank":rank,"exact_GF2_nullity":nullity,
              "all_n_nullity_lower_bound":2*step+1,
              "unique_SAT_model":"PROVED_BY_INDUCTIVE_ROW_DELETION_LEMMA",
              "physical_model_verified_all_rows":True,
              "exact_full_K_SAT_oracle_performed":full_oracle is not None,
              "exact_full_K_SAT_models":len(full_oracle) if full_oracle is not None else None,
              "indicator_Fourier_support_exact":str(full_indicator_support),
              "degree2_GRAM_sparse_support_ceiling":S2_upper,
              "degree2_idempotence_PROVABLY_IMPOSSIBLE":
                    S2_upper<full_indicator_support,
              "source_splice":receipt
            }
            records.append(record)
            previous_rank=rank
    assert records[-2]["blocks"]==20 and records[-1]["blocks"]==64
    assert records[-2]["degree2_idempotence_PROVABLY_IMPOSSIBLE"]
    assert records[-1]["degree2_idempotence_PROVABLY_IMPOSSIBLE"]
    assert records[0]["exact_full_K_SAT_models"]==1
    assert records[1]["exact_full_K_SAT_models"]==1
    assert records[2]["exact_full_K_SAT_models"]==1
    print(json.dumps({
       "gate":"BABEL27_CONNECTED_UNIQUE_SAT_SPLICE_FOURIER_INDICATOR_NO_GO",
       "all_n_row_deletion_theorem":"PROVED",
       "all_n_splice_semantics":"PROVED_UNIQUE_SAT_AND_CONNECTED",
       "all_n_nullity_bound":"d>=2t+1",
       "all_n_FIXED_k_gram_idempotence_eventual_failure":"PROVED",
       "all_n_linear_degree_necessity":"PROVED_FOR_THIS_REPRESENTATION",
       "research_scope":"SAT_INPUTS_ONLY__NOT_AN_UNSAT_LOWER_BOUND",
       "general_connected_SAT_polynomiality":"NOT_PROVED",
       "P_vs_NP":"OPEN",
       "cases":records
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
