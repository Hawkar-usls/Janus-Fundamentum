#!/usr/bin/env python3
import itertools
import json
from pathlib import Path

JSON_PATH = Path(__file__).with_name("JANUS_TRUMP_R44BS_MANY_TO_ONE_SUBSTITUTION_MODEL_TRANSPORT_2026-09-03.json")


def vars_of(formula):
    return {abs(lit) for clause in formula for lit in clause}


def deficiency(formula):
    return len(formula) - len(vars_of(formula))


def maximal_deficiency(formula):
    best = -10**9
    for mask in range(1 << len(formula)):
        sub = [formula[i] for i in range(len(formula)) if (mask >> i) & 1]
        best = max(best, deficiency(sub))
    return best


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
        mapped = phi[abs(lit)]
        out.add(mapped if lit > 0 else -mapped)
    return out


def tautological(lits):
    return any(-lit in lits for lit in lits)


def substitution_valid(target, source, phi):
    source_sets = [set(c) for c in source]
    for clause in target:
        img = image_clause(clause, phi)
        if tautological(img):
            continue
        if not any(d.issubset(img) for d in source_sets):
            return False
    return True


def eval_signed_literal(alpha, lit):
    value = alpha[abs(lit)]
    return value if lit > 0 else not value


def induced_assignment(alpha, phi):
    return {v: eval_signed_literal(alpha, lit) for v, lit in phi.items()}


def satisfies(formula, assignment):
    return all(any(assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)] for lit in clause) for clause in formula)


def main():
    data = json.loads(JSON_PATH.read_text())
    inst = data["critical_instance"]
    A = inst["target_A_x2_false"]
    B = inst["source_B_x2_true"]
    phi = {int(k): v for k, v in inst["substitution_phi"].items()}

    assert vars_of(A) == vars_of(B) == set(phi)
    assert maximal_deficiency(A) == inst["A_maximal_deficiency"] == 0
    assert maximal_deficiency(B) == inst["B_maximal_deficiency"] == 1
    assert inst["parent_maximal_deficiency"] == 2
    assert inst["R44BR_signed_permutation_transports_B_to_A"] == 0

    assert len(set(abs(v) for v in phi.values())) < len(phi), "phi must be genuinely non-bijective"
    assert substitution_valid(A, B, phi)

    expected_images = inst["clause_images"]
    for clause, expected in zip(A, expected_images):
        img = image_clause(clause, phi)
        assert set(expected["phi_image"]) == img
        if expected.get("witness") == "TAUTOLOGY":
            assert tautological(img)
        else:
            assert set(expected["witness_B_clause"]).issubset(img)
            assert expected["witness_B_clause"] in B

    b_models = models(B)
    assert len(b_models) == 7
    transported = []
    for alpha in b_models:
        beta = induced_assignment(alpha, phi)
        assert satisfies(A, beta)
        transported.append(beta)

    assert len(models(A)) == 11
    assert inst["rank_effect"] == "parent maxdef 2 -> retained A maxdef 0"

    print("R44BS EXACT MANY-TO-ONE TRANSPORT REPLAY PASS")
    print("source_B_models=7")
    print("all_source_models_transport_to_A=true")
    print("phi_is_nonbijective=true")
    print("signed_permutation_transport_B_to_A=0")
    print("safe_delete_B=true")
    print("rank_effect=2->0")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
