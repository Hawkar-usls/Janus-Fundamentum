#!/usr/bin/env python3
import itertools
import json
from pathlib import Path

JSON_PATH = Path(__file__).with_name("JANUS_TRUMP_R44BX_NONCONSTANT_BINARY_AFFINE_MODEL_TRANSPORT_2026-09-03.json")


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
    vs = sorted(vars_of(formula))
    out = []
    for bits in itertools.product([False, True], repeat=len(vs)):
        a = dict(zip(vs, bits))
        if all(any(a[abs(lit)] if lit > 0 else not a[abs(lit)] for lit in clause) for clause in formula):
            out.append(a)
    return out


def affine_value(spec, assignment):
    value = bool(spec["constant"])
    for v in spec["support"]:
        value ^= bool(assignment[v])
    return value


def target_clause_value(clause, amap, assignment):
    for lit in clause:
        value = affine_value(amap[str(abs(lit))], assignment)
        if lit < 0:
            value = not value
        if value:
            return True
    return False


def source_clause_value(clause, assignment):
    return any(assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)] for lit in clause)


def involved_in_target_clause(clause, amap):
    out = set()
    for lit in clause:
        out.update(amap[str(abs(lit))]["support"])
    return out


def is_tautology(clause, amap):
    vs = sorted(involved_in_target_clause(clause, amap))
    for bits in itertools.product([False, True], repeat=len(vs)):
        a = dict(zip(vs, bits))
        if not target_clause_value(clause, amap, a):
            return False
    return True


def source_clause_implies(source_clause, target_clause, amap):
    vs = sorted(involved_in_target_clause(target_clause, amap) | {abs(lit) for lit in source_clause})
    for bits in itertools.product([False, True], repeat=len(vs)):
        a = dict(zip(vs, bits))
        if source_clause_value(source_clause, a) and not target_clause_value(target_clause, amap, a):
            return False
    return True


def induced_target_assignment(source_assignment, amap):
    return {int(v): affine_value(spec, source_assignment) for v, spec in amap.items()}


def satisfies(formula, assignment):
    return all(any(assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)] for lit in clause) for clause in formula)


def main():
    data = json.loads(JSON_PATH.read_text())
    inst = data["critical_instance"]
    source = inst["source_A_x5_false"]
    target = inst["target_B_x5_true"]
    amap = inst["machine_form"]

    assert maximal_deficiency(source) == inst["A_maximal_deficiency"] == 1
    assert maximal_deficiency(target) == inst["B_maximal_deficiency"] == 0
    assert inst["parent_maximal_deficiency"] == 2
    assert inst["R44BW_literal_substitution_transports_A_to_B"] == 0

    # No constant-only target function, and every support has arity 1 or 2.
    for spec in amap.values():
        assert 1 <= len(spec["support"]) <= 2
        assert len(set(spec["support"])) == len(spec["support"])

    certs = inst["target_clause_certificates"]
    assert len(certs) == len(target)
    for clause, cert in zip(target, certs):
        assert clause == cert["target_clause"]
        if cert["certificate"] == "TAUTOLOGY":
            assert is_tautology(clause, amap)
        elif cert["certificate"] == "SOURCE_CLAUSE_IMPLIES":
            source_clause = cert["source_clause"]
            assert source_clause in source
            assert source_clause_implies(source_clause, clause, amap)
        else:
            raise AssertionError(cert)

    source_models = models(source)
    assert len(source_models) == 5
    for alpha in source_models:
        beta = induced_target_assignment(alpha, amap)
        assert satisfies(target, beta)

    print("R44BX EXACT BINARY-AFFINE TRANSPORT REPLAY PASS")
    print("constant_only_functions_allowed=false")
    print("affine_support_bound=2")
    print("source_A_models=5")
    print("all_source_models_transport_to_B=true")
    print("R44BW_literal_substitution_A_to_B=0")
    print("safe_delete_A=true")
    print("rank_effect=2->0")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
