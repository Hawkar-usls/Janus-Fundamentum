#!/usr/bin/env python3
"""Exact finite barrier for direct semilattice/Płonka absorption of the
three-sheet selector relation.

Relation:
  T(s,a,b,c)
  s=0 -> MAJ(a,b,c)
  s=1 -> MAJ(a,not b,c)
  s=2 -> MAJ(a,b,not c)

Checks:
1. enumerate all labelled binary semilattice operations on {0,1,2};
2. enumerate all idempotent Boolean binary operations independently on a,b,c;
3. test multi-sorted binary preservation of T;
4. expand Boolean coordinates to all 16 binary Boolean operations and classify
   every preserving tuple.

No SAT solver or heuristic search is used.
"""
from __future__ import annotations

import itertools
import json

BITS=(0,1)
SHEETS=(0,1,2)

def maj(a:int,b:int,c:int)->int:
    return int(a+b+c>=2)

def rel_t():
    out=[]
    for s in SHEETS:
        for a,b,c in itertools.product(BITS, repeat=3):
            ok=(
                maj(a,b,c) if s==0 else
                maj(a,1-b,c) if s==1 else
                maj(a,b,1-c)
            )
            if ok:
                out.append((s,a,b,c))
    return tuple(out)

def op3(table,x,y):
    return table[3*x+y]

def op2(table,x,y):
    return table[2*x+y]

def semilattice_ops_3():
    ans=[]
    for table in itertools.product(SHEETS, repeat=9):
        if any(op3(table,x,x)!=x for x in SHEETS):
            continue
        if any(op3(table,x,y)!=op3(table,y,x)
               for x,y in itertools.product(SHEETS, repeat=2)):
            continue
        if any(op3(table,op3(table,x,y),z)!=op3(table,x,op3(table,y,z))
               for x,y,z in itertools.product(SHEETS, repeat=3)):
            continue
        ans.append(table)
    return tuple(ans)

def bool_ops():
    return tuple(itertools.product(BITS, repeat=4))

def is_idempotent_bool(table):
    return op2(table,0,0)==0 and op2(table,1,1)==1

def preserves(T,Tset,sop,fa,fb,fc):
    for u,v in itertools.product(T, repeat=2):
        w=(
            op3(sop,u[0],v[0]),
            op2(fa,u[1],v[1]),
            op2(fb,u[2],v[2]),
            op2(fc,u[3],v[3]),
        )
        if w not in Tset:
            return False
    return True

def table2_name(t):
    names={
        (0,0,0,0):"CONST_0",
        (1,1,1,1):"CONST_1",
        (0,0,0,1):"AND",
        (0,1,1,1):"OR",
        (0,0,1,1):"PROJ_1",
        (0,1,0,1):"PROJ_2",
    }
    return names.get(tuple(t), "".join(map(str,t)))

def receipt():
    T=rel_t()
    Tset=set(T)
    semis=semilattice_ops_3()
    bops=bool_ops()
    ibops=tuple(t for t in bops if is_idempotent_bool(t))

    preserving_idempotent=[]
    for si,sop in enumerate(semis):
        for fa,fb,fc in itertools.product(ibops, repeat=3):
            if preserves(T,Tset,sop,fa,fb,fc):
                preserving_idempotent.append({
                    "selector_semilattice_index":si,
                    "boolean_ops":[table2_name(fa),table2_name(fb),table2_name(fc)]
                })

    preserving_all=[]
    for si,sop in enumerate(semis):
        for fa,fb,fc in itertools.product(bops, repeat=3):
            if preserves(T,Tset,sop,fa,fb,fc):
                preserving_all.append({
                    "selector_semilattice_index":si,
                    "boolean_ops":[table2_name(fa),table2_name(fb),table2_name(fc)]
                })

    bool_triples=sorted({tuple(x["boolean_ops"]) for x in preserving_all})

    assert len(T)==12
    assert len(semis)==9
    assert len(ibops)==4
    assert len(preserving_idempotent)==0
    assert len(preserving_all)==9
    assert bool_triples==[("CONST_1","CONST_1","CONST_1")]

    return {
        "schema":"janus.r5_e8_6i.explicit_selector_pseudopartition_barrier.v1",
        "status":"PASS_EXACT_FINITE_CLASSIFICATION",
        "relation":{
            "name":"T",
            "arity":4,
            "tuple_count":len(T),
            "definition":[
                "s=0 => MAJ(a,b,c)",
                "s=1 => MAJ(a,NOT b,c)",
                "s=2 => MAJ(a,b,NOT c)"
            ]
        },
        "selector_sort":{
            "domain_size":3,
            "binary_semilattice_operations":len(semis)
        },
        "visible_boolean_sorts":{
            "all_binary_operations":len(bops),
            "idempotent_binary_operations":len(ibops),
            "idempotent_names":[table2_name(x) for x in ibops]
        },
        "idempotent_multisorted_test":{
            "candidate_count":len(semis)*(len(ibops)**3),
            "preserving_count":len(preserving_idempotent),
            "preserving":preserving_idempotent,
            "verdict":"NO_DIRECT_SEMILATTICE_PLUS_IDEMPOTENT_BOOLEAN_BINARY_POLYMORPHISM_PRESERVES_T"
        },
        "all_boolean_operations_test":{
            "candidate_count":len(semis)*(len(bops)**3),
            "preserving_count":len(preserving_all),
            "preserving_boolean_coordinate_triples":[list(x) for x in bool_triples],
            "selector_semilattices_represented":sorted({x["selector_semilattice_index"] for x in preserving_all}),
            "verdict":"ONLY_CONST_1_ON_ALL_THREE_BOOLEAN_VISIBLE_COORDINATES_SURVIVES_FOR_EACH_SELECTOR_SEMILATTICE"
        },
        "scientific_meaning":[
            "DIRECT_EXPLICIT_SELECTOR_SEMILATTICE_PSEUDOPARTITION_ABSORPTION_WITH_IDEMPOTENT_BOOLEAN_VISIBLE_SORTS_IS_BLOCKED",
            "ALLOWING_NONIDEMPOTENT_BOOLEAN_BINARY_OPERATIONS_ONLY_ADDS_THE_TRIVIAL_ALL_CONST_1_VISIBLE_COLLAPSE",
            "THIS_DOES_NOT_BLOCK_GENERAL_PLONKA_SBM_OR_DISJUNCTIVE_REFINEMENT_COMPOSITIONS"
        ],
        "firewall":{
            "P_VS_NP":"OPEN",
            "D1":"EMPTY",
            "GENERAL_SHEET_ABSORPTION":"OPEN_OUTSIDE_THIS_DIRECT_BINARY_POLYMORPHISM_MODEL"
        }
    }

if __name__=="__main__":
    print(json.dumps(receipt(),indent=2,sort_keys=True))
