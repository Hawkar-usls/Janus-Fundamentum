#!/usr/bin/env python3
"""Exact 3-chain semilattice local OR3 lift / global-completeness control.

Carrier C3:
    0 < 1 < 2
    meet(a,b)=min(a,b)
Decoder:
    pi(1)=1
    pi(0)=pi(2)=0

Eight fixed ternary lifted relations are frozen below, one for every signed
3-clause relation. The checker proves:
  * each lifted relation is meet-closed;
  * its decoder image is exactly the corresponding signed OR3 relation;
  * CSP over the fixed lifted template is semilattice-polymorphic;
  * neither section of pi is a homomorphism from full signed 3SAT into
    this fixed lifted template;
  * a concrete satisfiable four-clause Boolean instance has no lifted
    solution under these fixed relations.

The result isolates LOCAL exact lift coverage from GLOBAL completeness.
It is not a P=NP result.
"""
from __future__ import annotations
import itertools, json

D=(0,1,2)
BITS=(0,1)
SIGNS=tuple(itertools.product((1,-1),repeat=3))

def meet(a,b): return min(a,b)
def dec(a): return 1 if a==1 else 0

RELATIONS={
    (1,1,1):{
        (1,0,0),(1,0,1),(1,1,0),(1,1,1),(2,1,0),(2,1,1),(2,2,1)
    },
    (1,1,-1):{
        (0,0,0),(0,1,0),(1,0,0),(1,0,1),(1,1,0),(1,1,1),(2,1,1)
    },
    (1,-1,1):{
        (0,0,0),(0,0,1),(1,0,0),(1,0,1),(1,1,0),(1,1,1),(2,1,1)
    },
    (1,-1,-1):{
        (0,0,0),(0,0,1),(0,1,0),(1,0,0),(1,0,1),(1,1,0),(1,1,1)
    },
    (-1,1,1):{
        (0,0,0),(0,0,1),(0,1,0),(0,1,1),(1,0,1),(1,1,1),(1,1,2)
    },
    (-1,1,-1):{
        (0,0,0),(0,0,1),(0,1,0),(0,1,1),(1,0,0),(1,1,0),(1,1,1)
    },
    (-1,-1,1):{
        (0,0,0),(0,0,1),(0,1,0),(0,1,1),(1,0,0),(1,0,1),(1,1,1)
    },
    (-1,-1,-1):{
        (0,0,0),(0,0,1),(0,1,0),(0,1,1),(1,0,0),(1,0,1),(1,1,0)
    },
}

def target(signs):
    return {
        row for row in itertools.product(BITS,repeat=3)
        if any(row[i] if signs[i]==1 else 1-row[i] for i in range(3))
    }

def image(R):
    return {tuple(dec(x) for x in t) for t in R}

def closed(R):
    for a,b in itertools.product(R,repeat=2):
        if tuple(meet(a[i],b[i]) for i in range(3)) not in R:
            return False
    return True

def section_hom(section):
    for signs in SIGNS:
        R=RELATIONS[signs]
        for row in target(signs):
            if tuple(section[b] for b in row) not in R:
                return False
    return True

def boolean_sat(formula):
    for row in itertools.product(BITS,repeat=3):
        if all(row in target(s) for s in formula):
            return row
    return None

def lifted_sat(formula):
    for row in itertools.product(D,repeat=3):
        if all(row in RELATIONS[s] for s in formula):
            return row
    return None

def build_receipt():
    for signs in SIGNS:
        assert len(RELATIONS[signs])==7
        assert closed(RELATIONS[signs])
        assert image(RELATIONS[signs])==target(signs)

    sections=[
        {0:0,1:1},
        {0:2,1:1},
    ]
    section_results=[section_hom(s) for s in sections]
    assert section_results==[False,False]

    witness=((1,1,1),(-1,1,1),(-1,1,-1),(-1,-1,-1))
    bw=boolean_sat(witness)
    lw=lifted_sat(witness)
    assert bw is not None
    assert lw is None

    return {
        "schema":"janus.r5_e8_6i.c3_semilattice_local_or3_global_gap.v1",
        "status":"PASS_EXACT_LOCAL_COVERAGE_GLOBAL_COMPLETENESS_FAILURE",
        "carrier":{
            "domain":[0,1,2],
            "operation":"meet(a,b)=min(a,b)",
            "semilattice":True,
            "decoder":{"0":0,"1":1,"2":0},
        },
        "local_relations":{
            "".join("P" if x==1 else "N" for x in signs):{
                "tuple_count":len(RELATIONS[signs]),
                "tuples":[list(t) for t in sorted(RELATIONS[signs])],
                "meet_closed":closed(RELATIONS[signs]),
                "decoded_image":"EXACT_SIGNED_OR3",
            } for signs in SIGNS
        },
        "local_coverage":{
            "all_eight_signed_clauses":True,
            "lifted_template_has_semilattice_polymorphism":True,
            "lifted_CSP_solver":"SOURCE_BOUND_SEMILATTICE_POLYNOMIAL",
        },
        "section_control":{
            "pi_sections":[{"0":0,"1":1},{"0":2,"1":1}],
            "sections_homomorphic_full_3sat_template":section_results,
            "homomorphic_section_count":0,
        },
        "global_counterexample":{
            "formula":[
                "(x OR y OR z)",
                "(NOT x OR y OR z)",
                "(NOT x OR y OR NOT z)",
                "(NOT x OR NOT y OR NOT z)",
            ],
            "sign_patterns":[list(s) for s in witness],
            "boolean_satisfiable":True,
            "boolean_witness":list(bw),
            "fixed_lift_satisfiable":False,
            "verdict":"LOCAL_EXACT_RELATION_IMAGES_DO_NOT_IMPLY_GLOBAL_LIFT_COMPLETENESS",
        },
        "scientific_meaning":[
            "A_FIXED_TRACTABLE_SEMILATTICE_CARRIER_CAN_HAVE_EXACT_LOCAL_LIFTS_FOR_ALL_SIGNED_OR3_RELATIONS",
            "THE_MISSING_RESOURCE_IS_GLOBAL_TEMPLATE_OR_INSTANCE_COMPLETENESS_NOT_LOCAL_CLAUSE_COVERAGE",
            "THIS_FIXED_LIFT_DOES_NOT_GIVE_A_UNIVERSAL_3SAT_REDUCTION",
        ],
        "firewall":{
            "P_VS_NP":"OPEN",
            "D1":"EMPTY",
            "SUCCESSOR_ALGORITHM":"LOCKED",
        },
    }

if __name__=="__main__":
    print(json.dumps(build_receipt(),ensure_ascii=False,indent=2,sort_keys=True))
