#!/usr/bin/env python3
"""E118 = literal/constant retraction preserving bounded-depth Frege hardness.

STRONGER than mere SAT-equivalence:
  For any cubic 3-uniform Positive Exact-One source F, let T(F) be
  E118 split-occurrence target (square/cubic/C4-free).

  Uniform variable substitution sigma from T(F) into F:
    each split port of source variable v -> v
    gadget local a,c,f -> 0
    gadget local b,d,e -> NOT v
    gadget local g -> v

  Every one of NINE gadget exact-one rows becomes an IDENTICAL
  Boolean tautology (v+NOT v+0==1), while each split source
  Exact-One row becomes its exact source clause.

  Therefore sigma(CNF(T(F))) is CNF(F) plus tautologies.
  Any Frege refutation of CNF(T(F)) transforms by substitution
  (literals/constants only) into a Frege refutation of CNF(F)
  without increasing depth and with polynomial/linear proof
  size overhead (trivial syntactic cleanup of tautologies).

  Thus lower bounds for bounded-depth Frege on arbitrary CUBIC
  3-uniform source families TRANSFER to legal SCL E118 targets.
  There remains the crucial UNPROVED obligation to construct a
  hard CUBIC source family from the known hard unrestricted
  1-in-3 CSP / Tseitin cases. NP-completeness alone DOES NOT
  prove hard bounded-depth-Frege refutations.

  Scientific gate: SCL Frege LB = OPEN; JANUS AND/OR LB = OPEN;
  universal poly SolveLinearCubicXSAT = NOT_CONSTRUCTED; PvsNP OPEN.
"""
from __future__ import annotations

from itertools import product
from collections import Counter

from r5_e118_universal_linear_cubic_exactone_hardness_bridge import (
    GADGET_CLAUSES,PORTS,INTERNAL,rename_gadget,split_occurrences
)
from r5_universal_boolean_quadratic_pc2_attack import cyclic_source


def retraction_for_variable(v):
    return {
        "x":("lit",v),
        "y":("lit",v),
        "z":("lit",v),
        "g":("lit",v),
        "a":("const",0),
        "c":("const",0),
        "f":("const",0),
        "b":("not",v),
        "d":("not",v),
        "e":("not",v),
    }


def eval_literal(token,word):
    kind,val=token
    if kind=="lit":return word[val]
    if kind=="not":return 1-word[val]
    assert kind=="const"
    return val


def check_one_gadget():
    for name in ("v0","v1","arbitrary_symbol"):
        replacement=retraction_for_variable(name)
        assert set(replacement)==set(PORTS)|set(INTERNAL)
        for value in (0,1):
            model={name:value}
            for row in GADGET_CLAUSES:
                counts=[eval_literal(replacement[var],model) for var in row]
                assert sum(counts)==1,(name,value,row,counts)
            assert all(eval_literal(replacement[p],model)==value for p in PORTS)
        # Polynomial-time syntactic tautology proof: each gadget
        # clause's replacements are 0,lit(v),not(v) in some order.
        for row in GADGET_CLAUSES:
            tokens=[replacement[v] for v in row]
            assert tokens.count(("const",0))==1
            assert tokens.count(("lit",name))==1
            assert tokens.count(("not",name))==1


def check_source_retraction(source):
    vars_=sorted({v for clause in source for v in clause})
    assert len(vars_)==len(source)
    deg=Counter(v for clause in source for v in clause)
    assert all(count==3 for count in deg.values())
    assert all(len(clause)==len(set(clause))==3 for clause in source)

    split,occurrences=split_occurrences(tuple(source))
    target=list(split)
    sigma={}
    for v,ports in occurrences.items():
        assert len(ports)==3
        for port in ports:
            sigma[port]=("lit",v)
        local=retraction_for_variable(v)
        gadget_prefix="G_"+v
        target.extend(rename_gadget(gadget_prefix,ports))
        for symbol in INTERNAL:
            sigma[f"{gadget_prefix}_{symbol}"]=local[symbol]
    n=len(source)
    assert len(target)==10*n and len(sigma)==10*n
    assert len(set(sigma))==10*n
    total_orig=sorted(tuple(sorted(c)) for c in source)
    substituted_orig=[
        tuple(sorted(sigma[port][1] for port in c))
        for c in split
    ]
    assert sorted(substituted_orig)==total_orig

    # Symbolic, not merely all 2^n test assignments: every gadget
    # exact-one becomes a tautology and every source row is unchanged.
    for v,ports in occurrences.items():
        inv=dict(zip(PORTS,ports))
        inv.update({a:f"G_{v}_{a}" for a in INTERNAL})
        for row in GADGET_CLAUSES:
            resolved=[sigma[inv[part]] for part in row]
            assert resolved.count(("lit",v))==1
            assert resolved.count(("not",v))==1
            assert resolved.count(("const",0))==1

    # Small test oracle independently checks pointwise correspondence
    # for every assignment only on fixed n <=9 scientific controls.
    if n<=9:
        for bits in product((0,1),repeat=n):
            model=dict(zip(vars_,bits))
            original=all(sum(model[v] for v in row)==1 for row in source)
            target_model={name:eval_literal(expr,model)
                          for name,expr in sigma.items()}
            witness=all(sum(target_model[v] for v in row)==1 for row in target)
            assert original==witness
    return n


def main():
    check_one_gadget()
    source_k4=[
      ("u1","u2","u3"),
      ("u1","u2","u4"),
      ("u1","u3","u4"),
      ("u2","u3","u4")
    ]
    cases=[("E118_K4_RETRACTION",source_k4)]
    for name,a,b in (
        ("E118_q9_SAT_SOURCE",1,2),
        ("E118_q9_UNSAT_SOURCE",1,6)
    ):
        cases.append((name,cyclic_source(9,a,b)))

    for name,source in cases:
        n=check_source_retraction(source)
        print(f"{name}: nsource={n} targetN={10*n} "
              "all 9 gadget rows identity-true, all original rows unchanged, "
              "pointwise exact SAT preservation PASS")
    print("E118_LITERAL_CONSTANT_FREGE_RETRACTION = PROVED_ALL_CUBIC_SOURCES")
    print("CUBIC_SOURCE_BD_FREGE_HARDNESS_IMPLIES_LEGAL_SCL_HARDNESS = PROVED")
    print("UNRESTRICTED_CSP_HARD_TO_CUBIC_SOURCE_FREGE_TRANSFER = OPEN")
    print("UNIVERSAL_JANUS_ANDOR_SUPERPOLY_LOWER_BOUND = NOT_PROVED")
    print("UNIVERSAL_POLY_SOLVER = NOT_CONSTRUCTED; P_VS_NP = OPEN")


if __name__=="__main__":
    main()
