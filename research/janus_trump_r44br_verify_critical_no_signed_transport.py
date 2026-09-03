#!/usr/bin/env python3
import itertools
import json
from pathlib import Path

JSON_PATH = Path(__file__).with_name("JANUS_TRUMP_R44BR_CRITICAL_SIBLING_NO_SIGNED_TRANSPORT_COUNTEREXAMPLE_2026-09-03.json")


def vars_of(formula):
    return {abs(lit) for clause in formula for lit in clause}


def deficiency(formula):
    return len(formula) - len(vars_of(formula))


def maximal_deficiency(formula):
    best = -10**9
    best_masks = []
    m = len(formula)
    for mask in range(1 << m):
        sub = [formula[i] for i in range(m) if (mask >> i) & 1]
        d = deficiency(sub)
        if d > best:
            best = d
            best_masks = [mask]
        elif d == best:
            best_masks.append(mask)
    return best, best_masks


def simplify(formula, var, value):
    sat_lit = var if value else -var
    false_lit = -sat_lit
    out = []
    for clause in formula:
        if sat_lit in clause:
            continue
        out.append([lit for lit in clause if lit != false_lit])
    return out


def model_count(formula):
    variables = sorted(vars_of(formula))
    count = 0
    first = None
    for bits in itertools.product([False, True], repeat=len(variables)):
        a = dict(zip(variables, bits))
        ok = all(any(a[abs(lit)] if lit > 0 else not a[abs(lit)] for lit in clause) for clause in formula)
        if ok:
            count += 1
            if first is None:
                first = a
    return count, first


def transport_valid(target, source, pi):
    source_sets = [set(c) for c in source]
    for clause in target:
        image = set()
        for lit in clause:
            mapped = pi[abs(lit)]
            image.add(mapped if lit > 0 else -mapped)
        if not any(d.issubset(image) for d in source_sets):
            return False
    return True


def count_transports(target, source):
    variables = sorted(vars_of(target))
    assert vars_of(source) == set(variables)
    tested = 0
    valid = 0
    for perm in itertools.permutations(variables):
        rho = dict(zip(variables, perm))
        for signs in itertools.product([1, -1], repeat=len(variables)):
            pi = {v: rho[v] * sign for v, sign in zip(variables, signs)}
            tested += 1
            if transport_valid(target, source, pi):
                valid += 1
    return tested, valid


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
    assert A == data["siblings"]["A_x2_false"]["clauses"]
    assert B == data["siblings"]["B_x2_true"]["clauses"]

    ka, _ = maximal_deficiency(A)
    kb, _ = maximal_deficiency(B)
    assert ka == data["siblings"]["A_x2_false"]["maximal_deficiency"] == 0
    assert kb == data["siblings"]["B_x2_true"]["maximal_deficiency"] == 1

    ca, ma = model_count(A)
    cb, mb = model_count(B)
    assert ca == data["siblings"]["A_x2_false"]["sat_model_count"] == 11
    assert cb == data["siblings"]["B_x2_true"]["sat_model_count"] == 7
    assert {str(k): v for k, v in ma.items()} == data["siblings"]["A_x2_false"]["example_model"]
    assert {str(k): v for k, v in mb.items()} == data["siblings"]["B_x2_true"]["example_model"]

    tested_ba, valid_ba = count_transports(A, B)
    tested_ab, valid_ab = count_transports(B, A)
    cert = data["signed_transport_exhaustion"]
    assert tested_ba == tested_ab == cert["signed_permutations_per_direction"] == 3840
    assert valid_ba == cert["B_to_A_valid_transports"] == 0
    assert valid_ab == cert["A_to_B_valid_transports"] == 0

    print("R44BR EXACT COUNTEREXAMPLE REPLAY PASS")
    print("parent_maxdef=2 critical=true")
    print("siblings_maxdef=0,1")
    print("siblings_sat_models=11,7")
    print("signed_permutations_each_direction=3840")
    print("valid_transports_B_to_A=0")
    print("valid_transports_A_to_B=0")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
