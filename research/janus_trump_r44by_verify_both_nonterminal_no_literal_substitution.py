#!/usr/bin/env python3
import itertools
import json
from pathlib import Path

JSON_PATH = Path(__file__).with_name("JANUS_TRUMP_R44BY_BOTH_NONTERMINAL_CRITICAL_NO_LITERAL_SUBSTITUTION_2026-09-03.json")


def vars_of(formula):
    return {abs(lit) for clause in formula for lit in clause}


def deficiency(formula):
    return len(formula) - len(vars_of(formula))


def maximal_deficiency(formula):
    best = -10**9
    masks = []
    for mask in range(1 << len(formula)):
        sub = [formula[i] for i in range(len(formula)) if (mask >> i) & 1]
        d = deficiency(sub)
        if d > best:
            best = d
            masks = [mask]
        elif d == best:
            masks.append(mask)
    return best, masks


def simplify(formula, var, value):
    sat = var if value else -var
    false = -sat
    out = []
    for clause in formula:
        if sat in clause:
            continue
        out.append([lit for lit in clause if lit != false])
    return out


def models(formula):
    variables = sorted(vars_of(formula))
    out = []
    for bits in itertools.product([False, True], repeat=len(variables)):
        a = dict(zip(variables, bits))
        if all(any(a[abs(lit)] if lit > 0 else not a[abs(lit)] for lit in clause) for clause in formula):
            out.append(a)
    return out


def image_clause(clause, phi):
    out = set()
    for lit in clause:
        z = phi[abs(lit)]
        out.add(z if lit > 0 else -z)
    return out


def substitution_valid(target, source, phi):
    source_sets = [set(c) for c in source]
    for clause in target:
        image = image_clause(clause, phi)
        if any(-lit in image for lit in image):
            continue
        if not any(d.issubset(image) for d in source_sets):
            return False
    return True


def count_substitutions(target, source):
    target_vars = sorted(vars_of(target))
    source_vars = sorted(vars_of(source))
    assert set(target_vars) == set(source_vars)
    signed = [lit for v in source_vars for lit in (v, -v)]
    tested = 0
    valid = 0
    for images in itertools.product(signed, repeat=len(target_vars)):
        phi = dict(zip(target_vars, images))
        tested += 1
        if substitution_valid(target, source, phi):
            valid += 1
    return tested, valid


def stringify_model(model):
    return {str(k): v for k, v in model.items()}


def main():
    data = json.loads(JSON_PATH.read_text())
    parent = data["parent_formula"]
    F = parent["clauses"]
    pivot = parent["pivot"]

    assert len(F) == parent["m"] == 8
    assert len(vars_of(F)) == parent["n"] == 6
    assert deficiency(F) == parent["ordinary_deficiency"] == 2

    k, masks = maximal_deficiency(F)
    assert k == parent["maximal_deficiency"] == 2
    assert masks == [(1 << len(F)) - 1]
    proper_max = max(
        deficiency([F[i] for i in range(len(F)) if (mask >> i) & 1])
        for mask in range((1 << len(F)) - 1)
    )
    assert proper_max == 1

    A = simplify(F, pivot, False)
    B = simplify(F, pivot, True)
    assert A == data["siblings"]["A_x5_false"]["clauses"]
    assert B == data["siblings"]["B_x5_true"]["clauses"]

    ka, _ = maximal_deficiency(A)
    kb, _ = maximal_deficiency(B)
    assert ka == data["siblings"]["A_x5_false"]["maximal_deficiency"] == 1
    assert kb == data["siblings"]["B_x5_true"]["maximal_deficiency"] == 1

    ma = models(A)
    mb = models(B)
    assert len(ma) == data["siblings"]["A_x5_false"]["sat_model_count"] == 9
    assert len(mb) == data["siblings"]["B_x5_true"]["sat_model_count"] == 7
    assert stringify_model(ma[0]) == data["siblings"]["A_x5_false"]["example_model"]
    assert stringify_model(mb[0]) == data["siblings"]["B_x5_true"]["example_model"]

    tested_ba, valid_ba = count_substitutions(A, B)
    tested_ab, valid_ab = count_substitutions(B, A)
    cert = data["literal_substitution_exhaustion"]
    assert tested_ba == tested_ab == cert["candidate_maps_per_direction"] == 100000
    assert valid_ba == cert["B_to_A_valid_many_to_one_substitutions"] == 0
    assert valid_ab == cert["A_to_B_valid_many_to_one_substitutions"] == 0
    assert tested_ba + tested_ab == cert["total_exact_maps_checked"] == 200000

    print("R44BY EXACT BOTH-NONTERMINAL COUNTEREXAMPLE REPLAY PASS")
    print("parent_maxdef=2 critical=true")
    print("siblings_maxdef=1,1")
    print("siblings_sat_models=9,7")
    print("candidate_substitutions_each_direction=100000")
    print("valid_substitutions_B_to_A=0")
    print("valid_substitutions_A_to_B=0")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
