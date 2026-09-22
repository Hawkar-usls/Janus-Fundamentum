#!/usr/bin/env python3
"""Exact B9 induced-algebra family classifier for R5 E8 6I.

B9 contains the canonical ternary Boolean tractability controls:
  C0, C1, AND3, OR3, MAJ3,
and all four ternary Boolean Mal'tsev operations.

For every non-empty subfamily B <= B9 this checker classifies:
  1) whether the source-native homomorphism Gamma_3SAT -> Gamma_3SAT^B exists;
  2) for covering families, whether Gamma_3SAT is a retract of Gamma_3SAT^B.

The classification is finite and exhaustive. It is not a general lower bound on
all possible tractable algebras or lifted domains.
"""
from __future__ import annotations

import itertools
import json

BITS=(0,1)
INPUTS=tuple(itertools.product(BITS, repeat=3))
SIGNS=tuple(itertools.product((1,-1), repeat=3))


def clause_relation(signs):
    out=[]
    for row in itertools.product(BITS, repeat=3):
        lits=[row[i] if signs[i]==1 else 1-row[i] for i in range(3)]
        if any(lits):
            out.append(row)
    assert len(out)==7
    return tuple(out)


def maltsev_tables():
    tabs=[]
    for vals in itertools.product(BITS, repeat=8):
        tab=dict(zip(INPUTS, vals))
        ok=True
        for x in BITS:
            for y in BITS:
                if tab[(x,y,y)]!=x or tab[(y,y,x)]!=x:
                    ok=False
                    break
            if not ok:
                break
        if ok:
            tabs.append(tab)
    assert len(tabs)==4
    return tabs


OPS={}
OPS["C0"]={x:0 for x in INPUTS}
OPS["C1"]={x:1 for x in INPUTS}
OPS["AND3"]={x:(x[0]&x[1]&x[2]) for x in INPUTS}
OPS["OR3"]={x:(x[0]|x[1]|x[2]) for x in INPUTS}
OPS["MAJ3"]={x:int(sum(x)>=2) for x in INPUTS}
for i,tab in enumerate(maltsev_tables()):
    OPS[f"MALTSEV_{i}"]=tab

LABELS=tuple(OPS)
assert len(LABELS)==9


def preserves(relation, labels):
    allowed=set(relation)
    for r0,r1,r2 in itertools.product(relation, repeat=3):
        out=tuple(OPS[labels[j]][(r0[j],r1[j],r2[j])] for j in range(3))
        if out not in allowed:
            return False
    return True


# Preservation depends only on the operation labels, so compute once for full B9.
INDUCED={}
for signs in SIGNS:
    rel=clause_relation(signs)
    INDUCED[signs]=tuple(
        labels for labels in itertools.product(LABELS, repeat=3)
        if preserves(rel, labels)
    )


def gamma_to_induced_homs(B):
    B=set(B)
    homs=[]
    for a0,a1 in itertools.product(sorted(B), repeat=2):
        ok=True
        for signs in SIGNS:
            allowed={t for t in INDUCED[signs] if all(x in B for x in t)}
            for row in clause_relation(signs):
                image=tuple(a0 if bit==0 else a1 for bit in row)
                if image not in allowed:
                    ok=False
                    break
            if not ok:
                break
        if ok:
            homs.append((a0,a1))
    return tuple(homs)


def retractions(B):
    B=tuple(B)
    if "C0" not in B or "C1" not in B:
        return ()
    others=tuple(x for x in B if x not in ("C0","C1"))
    out=[]
    for bits in itertools.product(BITS, repeat=len(others)):
        color={"C0":0,"C1":1, **dict(zip(others,bits))}
        ok=True
        for signs in SIGNS:
            original=set(clause_relation(signs))
            for t in INDUCED[signs]:
                if not all(x in B for x in t):
                    continue
                image=tuple(color[x] for x in t)
                if image not in original:
                    ok=False
                    break
            if not ok:
                break
        if ok:
            out.append(color)
    return tuple(out)


def classify():
    rows=[]
    for size in range(1,len(LABELS)+1):
        for B in itertools.combinations(LABELS,size):
            homs=gamma_to_induced_homs(B)
            rets=retractions(B) if homs else ()
            rows.append({
                "B":list(B),
                "size":size,
                "contains_C0_C1":("C0" in B and "C1" in B),
                "coverage_homomorphisms":[list(x) for x in homs],
                "coverage":bool(homs),
                "retraction_count":len(rets),
                "retract_equivalent_to_original_3SAT":bool(rets),
            })
    return rows


def build_receipt():
    rows=classify()
    covering=[x for x in rows if x["coverage"]]
    failing=[x for x in rows if not x["coverage"]]
    assert len(rows)==2**9-1==511
    assert len(covering)==2**7==128
    assert len(failing)==383
    assert all(x["contains_C0_C1"] for x in covering)
    assert all(not x["contains_C0_C1"] for x in failing)
    assert all(x["coverage_homomorphisms"]==[["C0","C1"]] for x in covering)
    assert all(x["retract_equivalent_to_original_3SAT"] for x in covering)

    full=next(x for x in rows if len(x["B"])==9)
    assert full["retraction_count"]==32

    # In every full-B9 retraction, AND is forced to 0 and OR to 1.
    full_rets=retractions(LABELS)
    assert all(r["AND3"]==0 and r["OR3"]==1 for r in full_rets)
    assert len({tuple(r[x] for x in ("MAJ3","MALTSEV_0","MALTSEV_1","MALTSEV_2","MALTSEV_3")) for r in full_rets})==32

    return {
        "schema":"janus.r5_e8_6i.boolean_b9_induced_algebra_family_classifier.v1",
        "status":"PASS_EXACT_511_SUBFAMILY_CLASSIFICATION",
        "library":list(LABELS),
        "library_description":[
            "C0/C1 = constant ternary tractable algebras",
            "AND3/OR3 = semilattice-fold Schaefer controls",
            "MAJ3 = bijunctive/majority control",
            "MALTSEV_0..3 = all ternary Boolean Mal'tsev operations"
        ],
        "full_B9_induced_relation_size_per_signed_clause": {
            "".join("+" if s==1 else "-" for s in signs):len(INDUCED[signs])
            for signs in SIGNS
        },
        "subfamily_count":511,
        "coverage_family_count":len(covering),
        "coverage_failure_family_count":len(failing),
        "coverage_characterization":"Gamma_3SAT -> Gamma_3SAT^B iff {C0,C1} subseteq B",
        "unique_coverage_map_for_every_covering_B":["C0","C1"],
        "covering_family_retraction_characterization":"Every covering B retracts Gamma_3SAT^B onto Gamma_3SAT by fixing C0->0,C1->1; at least one retraction exists for every covering B.",
        "full_B9_retraction_count":full["retraction_count"],
        "full_B9_forced_retraction_values":{"AND3":0,"OR3":1},
        "full_B9_free_retraction_labels":["MAJ3","MALTSEV_0","MALTSEV_1","MALTSEV_2","MALTSEV_3"],
        "scientific_meaning":[
            "THE_CANONICAL_BOOLEAN_TERNARY_TRACTABILITY_LIBRARY_DOES_NOT_CLOSE_6I",
            "WITHOUT_BOTH_CONSTANT_ALGEBRAS_SOURCE_NATIVE_COVERAGE_FAILS",
            "WITH_BOTH_CONSTANT_ALGEBRAS_THE_INDUCED_TEMPLATE_RETRACTS_TO_ORIGINAL_3SAT",
            "THEREFORE_THIS_WHOLE_FIXED_B9_SUBFAMILY_UNIVERSE_IS_EITHER_INCOMPLETE_OR_ZERO_PROGRESS"
        ],
        "scope_limit":[
            "NOT_A_CLASSIFICATION_OF_ALL_TRACTABLE_BOOLEAN_ALGEBRAS_OF_ARBITRARY_SIGNATURE",
            "NOT_A_LOWER_BOUND_FOR_LIFTED_DOMAINS",
            "NOT_A_P_VS_NP_RESULT"
        ],
        "firewall":{"P_VS_NP":"OPEN","D1":"EMPTY","SUCCESSOR_ALGORITHM":"LOCKED"}
    }


def main():
    print(json.dumps(build_receipt(),ensure_ascii=False,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
