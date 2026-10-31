#!/usr/bin/env python3
"""Static Gamma/Delta partition barrier for the frozen Delta_sheet language.

We test every partition of the 8 signed threshold-2 sheet relations into
Gamma and Delta.

Horn-like source-family admission requires every frozen three-sheet OR3 cover
to contain at most one Gamma relation.

Source 1-independence (k=1) implies, by taking an empty Gamma core, that every
finite Delta-only set whose individual constraints are satisfiable must be
jointly satisfiable. Hence Delta must in particular have GS.

For every Horn-admissible static partition, Delta necessarily contains a
complementary pair M_tau and M_not_tau; on the same variable triple these are
AT_LEAST_2 and AT_MOST_1 and are jointly unsatisfiable.

No complexity assumption or SAT solver is used.
"""
from __future__ import annotations
import itertools, json

BITS=(0,1)
SIGNS=tuple(itertools.product(BITS, repeat=3))
ID={s:i for i,s in enumerate(SIGNS)}

def xor(a,b):
    return tuple(x^y for x,y in zip(a,b))

def covers():
    # frozen canonical three-sheet identity flips visible positions 2 or 3
    out=[]
    for s in SIGNS:
        out.append(tuple(sorted({
            ID[s],
            ID[xor(s,(0,1,0))],
            ID[xor(s,(0,0,1))],
        })))
    return tuple(sorted(set(out)))

def comp_id(i):
    s=SIGNS[i]
    return ID[tuple(1-x for x in s)]

def receipt():
    cov=covers()
    assert len(cov)==8

    survivors=[]
    for mask in range(1<<8):
        gamma={i for i in range(8) if (mask>>i)&1}
        delta=set(range(8))-gamma

        horn_ok=all(len(gamma & set(c))<=1 for c in cov)
        if not horn_ok:
            continue

        complementary=[]
        for i in range(8):
            j=comp_id(i)
            if i<j and i in delta and j in delta:
                complementary.append((i,j))

        survivors.append({
            "gamma":sorted(gamma),
            "delta":sorted(delta),
            "gamma_size":len(gamma),
            "delta_size":len(delta),
            "delta_complementary_pairs":[list(x) for x in complementary],
        })

    assert len(survivors)==25
    assert max(x["gamma_size"] for x in survivors)==2
    assert min(x["delta_size"] for x in survivors)==6
    assert min(len(x["delta_complementary_pairs"]) for x in survivors)>=2

    return {
        "schema":"janus.r5_e8_6i.static_gamma_delta_1independence_barrier.v1",
        "status":"PASS_EXACT_STATIC_PARTITION_BARRIER",
        "sheet_relations":8,
        "all_partitions":256,
        "three_sheet_covers":[list(c) for c in cov],
        "horn_like_rule":"each three-sheet OR3 disjunction contains at most one Gamma relation",
        "horn_admissible_partitions":len(survivors),
        "max_gamma_size":max(x["gamma_size"] for x in survivors),
        "min_delta_size":min(x["delta_size"] for x in survivors),
        "min_complementary_pairs_in_delta":min(len(x["delta_complementary_pairs"]) for x in survivors),
        "source_logic":[
            "1-independence of Delta with respect to Gamma implies GS(Delta) by choosing an empty Gamma core",
            "M_tau and M_not_tau on the same triple are jointly unsatisfiable",
        ],
        "verdict":"NO_STATIC_PARTITION_OF_THE_8_FROZEN_SHEETS_CAN_SIMULTANEOUSLY_SATISFY_HORN_COVER_ADMISSION_AND_1_INDEPENDENCE",
        "survivors":survivors,
        "firewall":{
            "blocks_only":"STATIC_RELATION_LANGUAGE_PARTITION_OF_EXISTING_8_SHEETS",
            "does_not_block":[
                "representation-changing refinement",
                "derived/refined relation languages",
                "instance-specific global certificates",
                "non-static Gamma/Delta constructions explicitly covered by a source theorem"
            ],
            "P_VS_NP":"OPEN",
            "D1":"EMPTY"
        }
    }

if __name__=="__main__":
    print(json.dumps(receipt(),indent=2,sort_keys=True))
