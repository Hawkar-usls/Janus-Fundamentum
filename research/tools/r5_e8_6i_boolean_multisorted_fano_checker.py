#!/usr/bin/env python3
"""Exact Fano-plane blocker for Boolean multi-sorted ternary polymorphism certificates.

We use the paired clause language on each Fano hyperedge:
  R+ = (x OR y OR z)
  R- = (NOT x OR NOT y OR NOT z).

For mixed ternary Boolean operations (f,g,h), exhaustive preservation of both
relations has an exact quotient:
  - the triple contains CONST_0 and CONST_1; or
  - f=g=h=P_i for one of the three positive projections.

All 248 non-essentially-unary operations and the three negated projections have
the same role in this paired relation: they can occur only in the first case.

We then enumerate the six quotient labels
  C0,C1,P0,P1,P2,OTHER
over the seven vertices of the Fano plane.

Exactly three global assignments preserve every paired edge:
  all P0, all P1, all P2.

Therefore no vertex admits a preserving mixed ternary operation whose local
interpretation is constant or non-essentially-unary. This blocks the Boolean
multi-sorted ternary tractability-certificate route on this fixed gadget.

Scope: this is not a blocker for lifted/non-Boolean domains.
"""
from __future__ import annotations

import itertools
import json

C0=0
C1=255


def bit(mask:int, idx:int)->int:
    return (mask>>idx)&1


def dep_count(mask:int)->int:
    out=0
    for coord in range(3):
        depends=False
        for x in itertools.product((0,1), repeat=3):
            y=list(x); y[coord]^=1
            i=(x[0]<<2)|(x[1]<<1)|x[2]
            j=(y[0]<<2)|(y[1]<<1)|y[2]
            if bit(mask,i)!=bit(mask,j):
                depends=True
                break
        out+=int(depends)
    return out


PROJECTIONS=[]
for coord in range(3):
    mask=0
    for x in itertools.product((0,1), repeat=3):
        idx=(x[0]<<2)|(x[1]<<1)|x[2]
        if x[coord]:
            mask|=1<<idx
    PROJECTIONS.append(mask)

NEGATED_PROJECTIONS=[255^p for p in PROJECTIONS]
NONESSENTIAL=[m for m in range(256) if dep_count(m)>=2]
assert len(NONESSENTIAL)==248


def support_masks(f:int):
    zeros=0;ones=0
    for idx in range(8):
        if bit(f,idx):
            ones|=1<<idx
        else:
            zeros|=1<<idx
    return zeros,ones


Z={}
O={}
for f in range(256):
    Z[f],O[f]=support_masks(f)


def pair_bad_pos(zf:int,zg:int)->int:
    bad=0
    for a in range(8):
        if not ((zf>>a)&1):
            continue
        for b in range(8):
            if not ((zg>>b)&1):
                continue
            u=a|b
            for c in range(8):
                if (u|c)==7:
                    bad|=1<<c
    return bad


def pair_bad_neg(of:int,og:int)->int:
    bad=0
    for a in range(8):
        if not ((of>>a)&1):
            continue
        for b in range(8):
            if not ((og>>b)&1):
                continue
            u=a&b
            for c in range(8):
                if (u&c)==0:
                    bad|=1<<c
    return bad


def full_paired_survivors():
    out=set()
    for f in range(256):
        for g in range(256):
            bp=pair_bad_pos(Z[f],Z[g])
            bn=pair_bad_neg(O[f],O[g])
            for h in range(256):
                if (Z[h]&bp)==0 and (O[h]&bn)==0:
                    out.add((f,g,h))
    return out


def quotient_rule_triples():
    out=set()
    for t in itertools.product(range(256), repeat=3):
        if C0 in t and C1 in t:
            out.add(t)
    for p in PROJECTIONS:
        out.add((p,p,p))
    return out


CATS=("C0","C1","P0","P1","P2","OTHER")
TRACTABLE_TARGET_CATS={"C0","C1","OTHER"}

FANO_EDGES=(
    (0,1,2),
    (0,3,4),
    (0,5,6),
    (1,3,5),
    (1,4,6),
    (2,3,6),
    (2,4,5),
)


def category_edge_ok(t):
    return (
        ("C0" in t and "C1" in t)
        or (t[0]==t[1]==t[2] and t[0] in {"P0","P1","P2"})
    )


def build_receipt():
    survivors=full_paired_survivors()
    quotient=quotient_rule_triples()
    assert survivors==quotient
    assert len(survivors)==1533

    global_solutions=[]
    for assignment in itertools.product(CATS, repeat=7):
        if all(category_edge_ok(tuple(assignment[v] for v in e)) for e in FANO_EDGES):
            global_solutions.append(assignment)

    expected=[
        ("P0",)*7,
        ("P1",)*7,
        ("P2",)*7,
    ]
    assert global_solutions==expected

    target_counts={}
    for v in range(7):
        target_counts[str(v)]=sum(
            1 for a in global_solutions if a[v] in TRACTABLE_TARGET_CATS
        )
    assert all(x==0 for x in target_counts.values())

    # The paired Boolean formula is unsatisfiable: Fano plane is not 2-colourable.
    nae_colourings=0
    for bits in itertools.product((0,1), repeat=7):
        if all(len({bits[v] for v in e})==2 for e in FANO_EDGES):
            nae_colourings+=1
    assert nae_colourings==0

    return {
        "schema":"janus.r5_e8_6i.boolean_multisorted_fano_blocker.v1",
        "status":"PASS_EXACT_BOOLEAN_MULTISORTED_BLOCKER",
        "paired_relation":{
            "positive":"(x OR y OR z)",
            "negative":"(NOT x OR NOT y OR NOT z)",
            "full_mixed_ternary_operation_domain_size":256,
            "surviving_mixed_operation_triples":1533,
            "exact_survivor_rule":"CONTAINS_BOTH_CONST_0_AND_CONST_1_OR_ALL_THREE_EQUAL_ONE_POSITIVE_PROJECTION"
        },
        "operation_categories":{
            "categories":list(CATS),
            "OTHER":"ALL_248_NONESSENTIAL_OPERATIONS_PLUS_3_NEGATED_PROJECTIONS_FOR_RELATION_BEHAVIOUR",
            "tractable_target_categories":sorted(TRACTABLE_TARGET_CATS),
            "positive_projection_categories":["P0","P1","P2"]
        },
        "fano":{
            "vertex_count":7,
            "edge_count":7,
            "edges":[list(e) for e in FANO_EDGES],
            "boolean_NAE_colourings":nae_colourings,
            "category_assignments_checked":6**7,
            "global_preserving_category_assignments":[list(x) for x in global_solutions],
            "global_preserving_assignment_count":len(global_solutions),
            "tractable_target_assignment_count_by_vertex":target_counts
        },
        "theorem_meaning":[
            "THE_ONLY_GLOBAL_MIXED_TERNARY_POLYMORPHISMS_OF_THE_PAIRED_FANO_LANGUAGE_AT_QUOTIENT_LEVEL_ARE_THE_THREE_UNIFORM_PROJECTIONS",
            "NO_SORT_HAS_A_GLOBAL_PRESERVING_TERNARY_POLYMORPHISM_WITH_CONSTANT_OR_NONESSENTIALLY_UNARY_LOCAL_INTERPRETATION",
            "BOOLEAN_MULTI_SORTED_MULTI_OPERATION_TRACTABILITY_CERTIFICATE_IS_NOT_UNIVERSAL_FOR_3CNF"
        ],
        "scope_limit":[
            "DOES_NOT_BLOCK_NON_BOOLEAN_LIFTED_DOMAINS",
            "DOES_NOT_BLOCK_INSTANCE_GENERATED_LIFTS_WITH_NEW_DOMAIN_ELEMENTS",
            "DOES_NOT_RESOLVE_P_VS_NP"
        ],
        "firewall":{"P_VS_NP":"OPEN","D1":"EMPTY","SUCCESSOR_ALGORITHM":"LOCKED"}
    }


if __name__=="__main__":
    print(json.dumps(build_receipt(),ensure_ascii=False,indent=2,sort_keys=True))
