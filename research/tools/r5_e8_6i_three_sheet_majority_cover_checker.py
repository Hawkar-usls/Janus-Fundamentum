#!/usr/bin/env python3
"""Exact three-sheet majority cover identity for OR3.

The checker proves by full Boolean truth-table replay that

    OR(a,b,c)
      = MAJ(a,b,c)
        OR MAJ(a,not b,c)
        OR MAJ(a,b,not c).

It also checks all eight signed 3-clause variants by applying the identity
to literal truth values.

This is a decomposition identity only. Introducing an independent sheet
selector per clause is an exact repackaging of 3-SAT, not a polynomial
algorithm.
"""
from __future__ import annotations

import itertools
import json

BITS=(0,1)
SIGNS=tuple(itertools.product((1,-1),repeat=3))


def maj(a:int,b:int,c:int)->int:
    return int(a+b+c>=2)


def sheet_values(a:int,b:int,c:int)->tuple[int,int,int]:
    return (
        maj(a,b,c),
        maj(a,1-b,c),
        maj(a,b,1-c),
    )


def clause_value(row,signs)->int:
    lits=[row[i] if signs[i]==1 else 1-row[i] for i in range(3)]
    return int(any(lits))


def signed_sheet_values(row,signs):
    l=[row[i] if signs[i]==1 else 1-row[i] for i in range(3)]
    return sheet_values(*l)


def build_receipt():
    table=[]
    for row in itertools.product(BITS,repeat=3):
        sheets=sheet_values(*row)
        target=int(any(row))
        assert int(any(sheets))==target
        table.append({
            "literal_truths":list(row),
            "OR3":target,
            "sheets":list(sheets),
        })

    signed_checks=0
    for signs in SIGNS:
        for row in itertools.product(BITS,repeat=3):
            target=clause_value(row,signs)
            sheets=signed_sheet_values(row,signs)
            assert int(any(sheets))==target
            signed_checks+=1
    assert signed_checks==64

    # Minimality among the four majority sheets that exclude 000.
    all_sheets=(
        lambda a,b,c:maj(a,b,c),
        lambda a,b,c:maj(a,b,1-c),
        lambda a,b,c:maj(a,1-b,c),
        lambda a,b,c:maj(1-a,b,c),
    )
    target_rows={r for r in itertools.product(BITS,repeat=3) if any(r)}
    minimum=None
    minimum_covers=[]
    for k in range(1,5):
        for ids in itertools.combinations(range(4),k):
            union={
                r for r in itertools.product(BITS,repeat=3)
                if any(all_sheets[i](*r) for i in ids)
            }
            if union==target_rows:
                minimum=k
                minimum_covers.append(ids)
        if minimum is not None:
            break
    assert minimum==3
    assert len(minimum_covers)==4

    return {
        "schema":"janus.r5_e8_6i.three_sheet_majority_cover.v1",
        "status":"PASS_EXACT_BOOLEAN_IDENTITY",
        "identity":"OR3(a,b,c)=MAJ(a,b,c) OR MAJ(a,NOT b,c) OR MAJ(a,b,NOT c)",
        "truth_table":table,
        "signed_clause_checks":signed_checks,
        "minimal_cover":{
            "candidate_majority_sheets_excluding_000":4,
            "minimum_sheet_count":minimum,
            "minimum_cover_count":len(minimum_covers),
            "minimum_covers":[list(x) for x in minimum_covers]
        },
        "interpretation":{
            "A3_local_mechanism_can_realize_each_sheet":"YES",
            "local_OR3_coverage_by_three_sheets":"EXACT",
            "independent_clause_sheet_selector":"EXACT_3SAT_REPACKAGING_NOT_ALGORITHMIC_PROGRESS",
            "next_missing_object":"POLYNOMIAL_ALGEBRAIC_SHEET_COMPOSITION_WITHOUT_HIDDEN_SEMANTIC_SELECTOR"
        },
        "firewall":{
            "P_VS_NP":"OPEN",
            "D1":"EMPTY",
            "SUCCESSOR_ALGORITHM":"LOCKED"
        }
    }


if __name__=="__main__":
    print(json.dumps(build_receipt(),ensure_ascii=False,indent=2,sort_keys=True))
