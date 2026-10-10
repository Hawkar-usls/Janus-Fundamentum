#!/usr/bin/env python3
"""Exact 1-independence barrier for the frozen three-sheet binding.

For each signed OR3 clause the frozen cover contains exactly three
Delta_sheet relations. A source-compatible Horn-like Gamma∨Delta*
representation may use at most one Gamma-disjunct, hence at least two
of the three frozen sheet relations must belong to Delta.

This checker enumerates every Delta subset of the 8 threshold-2 relations
satisfying that representability condition and verifies that each contains
a complementary pair M_tau, M_not_tau. Such a pair is an exact
1-independence falsifier: each relation alone is satisfiable, while their
conjunction on the same three variables is unsatisfiable.
"""
from __future__ import annotations
import itertools, json

BITS=(0,1)
TAUS=tuple(itertools.product(BITS, repeat=3))
INDEX={t:i for i,t in enumerate(TAUS)}

def flip(t,k):
    x=list(t); x[k]^=1
    return tuple(x)

def complement(t):
    return tuple(1-b for b in t)

def maj_signed(t,row):
    lits=[row[i]^t[i] for i in range(3)]
    return int(sum(lits)>=2)

FROZEN_COVERS=[]
for t in TAUS:
    # M_tau OR M_flip2 OR M_flip3
    FROZEN_COVERS.append(tuple(sorted({
        INDEX[t],
        INDEX[flip(t,1)],
        INDEX[flip(t,2)],
    })))

def relation_nonempty(i):
    return any(maj_signed(TAUS[i],row) for row in itertools.product(BITS,repeat=3))

def conjunction_nonempty(i,j):
    return any(
        maj_signed(TAUS[i],row) and maj_signed(TAUS[j],row)
        for row in itertools.product(BITS,repeat=3)
    )

def receipt():
    valid=[]
    for mask in range(1<<8):
        D={i for i in range(8) if (mask>>i)&1}
        if all(len(D.intersection(c))>=2 for c in FROZEN_COVERS):
            pairs=[]
            for i in sorted(D):
                j=INDEX[complement(TAUS[i])]
                if i<j and j in D:
                    pairs.append((i,j))
            assert pairs
            for i,j in pairs:
                assert relation_nonempty(i)
                assert relation_nonempty(j)
                assert not conjunction_nonempty(i,j)
            valid.append({
                "delta":[TAUS[i] for i in sorted(D)],
                "delta_size":len(D),
                "complementary_pairs":[[TAUS[i],TAUS[j]] for i,j in pairs],
            })

    assert len(valid)==25
    assert min(x["delta_size"] for x in valid)==6
    return {
        "schema":"janus.r5_e8_6i.three_sheet_1_independence_barrier.v1",
        "status":"PASS_EXACT_FINITE_CLASSIFICATION",
        "base_relations":8,
        "frozen_cover_count":len(set(FROZEN_COVERS)),
        "source_horn_like_requirement":"AT_LEAST_TWO_OF_THREE_FROZEN_SHEET_DISJUNCTS_MUST_BE_IN_DELTA",
        "valid_delta_subsets":len(valid),
        "minimum_delta_size":min(x["delta_size"] for x in valid),
        "every_valid_delta_contains_complementary_pair":True,
        "falsifier":"M_tau(x,y,z) AND M_not_tau(x,y,z) is UNSAT although each singleton subinstance is SAT",
        "verdict":"DELTA_IS_NOT_1_INDEPENDENT_WITH_RESPECT_TO_ANY_GAMMA_COMPATIBLE_WITH_THE_FROZEN_THREE_SHEET_HORN_LIKE_BINDING",
        "details":valid,
        "firewall":{
            "direct_frozen_1_independence_route":"BLOCKED",
            "nontrivial_refinement_escape":"OPEN",
            "P_VS_NP":"OPEN",
            "D1":"EMPTY"
        }
    }

if __name__=="__main__":
    print(json.dumps(receipt(),indent=2,sort_keys=True))
