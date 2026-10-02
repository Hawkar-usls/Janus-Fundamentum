#!/usr/bin/env python3
"""Exact exhaustive blocker for the full single-ternary Boolean tractable-algebra catalogue.

Catalogue:
- every ternary Boolean operation depending on at least two variables (248 total);
- CONST_0 and CONST_1.

By Schaefer/Post, any Boolean constraint language preserved by a non-essentially-unary
operation is tractable; CONST_0/CONST_1 are trivially tractable. The six excluded
essentially-unary nonconstant operations (projections and negated projections) do not
supply a tractable invariant class.

For the paired clauses
    R+ = (x OR y OR z)
    R- = (NOT x OR NOT y OR NOT z)
we exhaustively compute all variable-wise algebra-label triples preserving BOTH relations.

Result:
- exactly 1494 ordered triples survive;
- every surviving triple contains both CONST_0 and CONST_1;
- 1488 have exactly two constants (one 0, one 1) and one arbitrary nonessential op;
- 6 have three constants, not all equal.

Hence the induced paired-clause relation retracts to the Boolean NAE relation on
{CONST_0, CONST_1}. The prototype CSP for this single-operation Boolean catalogue is
therefore homomorphically equivalent, on the paired-clause sublanguage, to monotone
NAE-3SAT and does not create a polynomial prototype layer unless P=NP.

This is a finite-domain exhaustive theorem checker, not heuristic evidence.
"""
from __future__ import annotations
import itertools
import json

C0 = 0
C1 = 255

def bit(mask: int, idx: int) -> int:
    return (mask >> idx) & 1

def dep_count(mask: int) -> int:
    out = 0
    for coord in range(3):
        depends = False
        for x in itertools.product((0,1), repeat=3):
            y = list(x)
            y[coord] ^= 1
            i = (x[0] << 2) | (x[1] << 1) | x[2]
            j = (y[0] << 2) | (y[1] << 1) | y[2]
            if bit(mask, i) != bit(mask, j):
                depends = True
                break
        out += int(depends)
    return out

def catalogue() -> list[int]:
    nonessential = [m for m in range(256) if dep_count(m) >= 2]
    assert len(nonessential) == 248
    return nonessential + [C0, C1]

def zero_one_support_masks(f: int) -> tuple[int,int]:
    zb = 0
    ob = 0
    for idx in range(8):
        if bit(f, idx):
            ob |= 1 << idx
        else:
            zb |= 1 << idx
    return zb, ob

def pair_bad_pos(zf: int, zg: int) -> int:
    bad = 0
    for a in range(8):
        if not ((zf >> a) & 1):
            continue
        for b in range(8):
            if not ((zg >> b) & 1):
                continue
            u = a | b
            for c in range(8):
                if (u | c) == 7:
                    bad |= 1 << c
    return bad

def pair_bad_neg(of: int, og: int) -> int:
    bad = 0
    for a in range(8):
        if not ((of >> a) & 1):
            continue
        for b in range(8):
            if not ((og >> b) & 1):
                continue
            u = a & b
            for c in range(8):
                if (u & c) == 0:
                    bad |= 1 << c
    return bad

def build_receipt() -> dict:
    B = catalogue()
    z = {}
    o = {}
    for f in B:
        z[f], o[f] = zero_one_support_masks(f)

    survivors = []
    count_by_constants = {0:0,1:0,2:0,3:0}
    violations = []

    for f in B:
        for g in B:
            bp = pair_bad_pos(z[f], z[g])
            bn = pair_bad_neg(o[f], o[g])
            for h in B:
                preserves_positive = (z[h] & bp) == 0
                preserves_negative = (o[h] & bn) == 0
                if preserves_positive and preserves_negative:
                    constants = sum(x in (C0,C1) for x in (f,g,h))
                    count_by_constants[constants] += 1
                    has_c0 = C0 in (f,g,h)
                    has_c1 = C1 in (f,g,h)
                    if not (has_c0 and has_c1):
                        violations.append((f,g,h))
                    survivors.append((f,g,h))

    assert len(B) == 250
    assert len(survivors) == 1494
    assert count_by_constants == {0:0,1:0,2:1488,3:6}
    assert violations == []

    # Restricted/retracted core on constants is exactly Boolean NAE:
    const_survivors = sorted(t for t in survivors if all(x in (C0,C1) for x in t))
    expected_nae = sorted(
        t for t in itertools.product((C0,C1), repeat=3)
        if len(set(t)) == 2
    )
    assert const_survivors == expected_nae

    # Any nonconstant label can be retracted to C0 and every survivor stays a survivor,
    # since every survivor already contains both C0 and C1.
    survivor_set = set(survivors)
    for t in survivors:
        rt = tuple(C0 if x not in (C0,C1) else x for x in t)
        assert rt in survivor_set

    return {
        "schema":"janus.r5_e8_6i.full_boolean_single_ternary_catalogue_blocker.v1",
        "status":"PASS_EXACT_FULL_CATALOGUE_BLOCKER",
        "catalogue":{
            "all_ternary_boolean_operations":256,
            "nonessentially_unary_operations":248,
            "constant_operations":2,
            "excluded_essentially_unary_nonconstant_operations":6,
            "tractable_single_operation_labels":250
        },
        "paired_clause":{
            "positive":"(x OR y OR z)",
            "negative":"(NOT x OR NOT y OR NOT z)",
            "semantic_intersection":"NAE(x,y,z)"
        },
        "exhaustive_result":{
            "surviving_ordered_label_triples":1494,
            "by_number_of_constant_labels":{"0":0,"1":0,"2":1488,"3":6},
            "every_survivor_contains_CONST_0":True,
            "every_survivor_contains_CONST_1":True,
            "all_nonconstant_triple_exists":False
        },
        "prototype_core":{
            "constant_domain":["CONST_0","CONST_1"],
            "restricted_relation":"BOOLEAN_NAE",
            "retraction":"ALL_NONCONSTANT_LABELS_TO_CONST_0",
            "homomorphic_equivalence_to_NAE":True
        },
        "verdict":{
            "FULL_SINGLE_TERNARY_BOOLEAN_TRACTABLE_ALGEBRA_CATALOGUE":"NO_PROTOTYPE_SIMPLIFICATION_ON_PAIRED_CLAUSE_NAE_SUBLANGUAGE",
            "PROTOTYPE_CSP_HARDNESS_CONTROL":"NAE_3SAT",
            "NEXT_ALLOWED_DIRECTION":"MULTI_OPERATION_OR_LIFTED_DOMAIN_CERTIFICATES_ONLY"
        },
        "firewall":{
            "P_VS_NP":"OPEN",
            "D1":"EMPTY",
            "SUCCESSOR_ALGORITHM":"LOCKED",
            "THIS_IS_NOT_A_LOWER_BOUND_FOR_ALL_INDUCED_ALGEBRA_FAMILIES":True
        }
    }

if __name__ == "__main__":
    print(json.dumps(build_receipt(), ensure_ascii=False, indent=2, sort_keys=True))
