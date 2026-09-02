from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35_nonaffine_core_freeze_structure_intake as r35
import janus_trump_r35b_single_literal_rup_vivification as r35b

SEED = 36001
N = 28
RATIO = 4.2
EXPECTED_FIXPOINT_HASH = "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"
EXPECTED_FIXPOINT_CLV = [45, 105, 13]

Literal = int
Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]


def formula_hash(formula: Formula) -> str:
    return r35.canonical_json_sha256([list(c) for c in formula])


def materialize_r37b_fixpoint() -> dict:
    formula = r33.deterministic_random_3cnf(SEED, n=N, ratio=RATIO)
    cycles = []
    transformations = 0
    restarts = 0
    for cycle_index in range(1000):
        before = formula
        before_hash = formula_hash(before)
        rr = r33.simplify(before)
        after_r33 = r33.canonical_formula(rr["final_formula"])
        transformations += rr["total_rule_applications"]
        if rr["terminal"] != "STALLED_STACK_LEAN_CORE":
            raise AssertionError(("R37B fixpoint unexpectedly reached R33 terminal", rr["terminal"]))
        rec = r34.recognize_complete_affine_cnf(after_r33)
        if rec["recognized"]:
            raise AssertionError("R37B fixpoint unexpectedly became affine")
        rup = r35b.run_candidate(after_r33)
        checker = r35b.independent_certificate_replay(after_r33, rup)
        if not checker["pass"]:
            raise AssertionError(("RUP replay failed", cycle_index, checker))
        after_rup = r33.canonical_formula(rup["final_formula"])
        transformations += rup["successful_strengthenings"]
        cycles.append({
            "cycle": cycle_index,
            "before_measure_CLV": list(r33.measure(before)),
            "before_hash": before_hash,
            "R33_rule_applications": rr["total_rule_applications"],
            "R33_after_measure_CLV": list(r33.measure(after_r33)),
            "R33_after_hash": formula_hash(after_r33),
            "RUP_strengthenings": rup["successful_strengthenings"],
            "RUP_after_measure_CLV": list(r33.measure(after_rup)),
            "RUP_after_hash": formula_hash(after_rup),
            "RUP_status": rup["status"],
        })
        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            raise AssertionError("R37B fixpoint unexpectedly became RUP UNSAT")
        if formula_hash(after_rup) == formula_hash(after_r33):
            formula = after_rup
            break
        restarts += 1
        formula = after_rup
    else:
        raise AssertionError("R37B materialization restart bound exceeded")

    h = formula_hash(formula)
    m = list(r33.measure(formula))
    if h != EXPECTED_FIXPOINT_HASH or m != EXPECTED_FIXPOINT_CLV:
        raise AssertionError(("R37B fixpoint drift", h, m))
    if len(cycles) != 3 or restarts != 2 or transformations != 184:
        raise AssertionError(("R37B cycle receipt drift", len(cycles), restarts, transformations))
    return {"formula": formula, "hash": h, "measure_CLV": m, "cycles": cycles, "restart_count": restarts, "successful_transformations": transformations}


def two_sat_satisfiable(variables: Iterable[int], clauses: List[Tuple[int, int]], units: Iterable[int] = ()) -> bool:
    vs = sorted(set(int(v) for v in variables))
    graph: Dict[int, List[int]] = {lit: [] for v in vs for lit in (v, -v)}
    reverse: Dict[int, List[int]] = {lit: [] for v in vs for lit in (v, -v)}

    def add_imp(a: int, b: int) -> None:
        graph[a].append(b)
        reverse[b].append(a)

    for a, b in clauses:
        add_imp(-a, b)
        add_imp(-b, a)
    for u in units:
        add_imp(-u, u)

    seen: Set[int] = set()
    order: List[int] = []
    def dfs1(start: int) -> None:
        stack = [(start, 0)]
        seen.add(start)
        while stack:
            u, idx = stack[-1]
            nbrs = graph[u]
            if idx < len(nbrs):
                v = nbrs[idx]
                stack[-1] = (u, idx + 1)
                if v not in seen:
                    seen.add(v)
                    stack.append((v, 0))
            else:
                order.append(u)
                stack.pop()
    for node in sorted(graph, key=lambda x: (abs(x), x < 0)):
        if node not in seen:
            dfs1(node)

    comp: Dict[int, int] = {}
    cid = 0
    for start in reversed(order):
        if start in comp:
            continue
        cid += 1
        stack = [start]
        comp[start] = cid
        while stack:
            u = stack.pop()
            for v in reverse[u]:
                if v not in comp:
                    comp[v] = cid
                    stack.append(v)
    return all(comp[v] != comp[-v] for v in vs)


def renamable_horn_recognition(formula: Formula) -> dict:
    vs = r33.variables(formula)
    constraints: List[Tuple[int, int]] = []
    for clause in formula:
        for i, a in enumerate(clause):
            for b in clause[i + 1 :]:
                constraints.append((a, b))
    if not two_sat_satisfiable(vs, constraints):
        return {"recognized": False, "reason": "FLIP_2SAT_UNSAT", "constraint_count": len(constraints), "SCC_checks_for_witness": 1}

    units: List[int] = []
    assignment: Dict[int, bool] = {}
    checks = 1
    for v in vs:
        # f_v=False means do not flip.  Encode that as unit -v if still satisfiable.
        if two_sat_satisfiable(vs, constraints, units + [-v]):
            units.append(-v)
            assignment[v] = False
        else:
            if not two_sat_satisfiable(vs, constraints, units + [v]):
                raise AssertionError("2SAT witness extraction drift")
            checks += 1
            units.append(v)
            assignment[v] = True
        checks += 1

    renamed: List[Clause] = []
    for clause in formula:
        renamed.append(tuple((-lit if assignment[abs(lit)] else lit) for lit in clause))
    horn_ok = r33.is_horn(tuple(renamed))
    if not horn_ok:
        raise AssertionError("renamable-Horn witness failed recheck")
    return {
        "recognized": True,
        "reason": "RENAMABLE_HORN",
        "constraint_count": len(constraints),
        "SCC_checks_for_witness": checks,
        "flipped_variables": [v for v in vs if assignment[v]],
        "flip_assignment": {str(v): bool(assignment[v]) for v in vs},
        "renamed_formula_horn_recheck": True,
    }


def dual_horn_recognition(formula: Formula) -> dict:
    bad = [list(c) for c in formula if sum(1 for lit in c if lit < 0) > 1]
    return {"recognized": not bad, "violating_clause_count": len(bad), "first_violating_clause": bad[0] if bad else None}


def beta_acyclic_recognition(formula: Formula) -> dict:
    # Hyperedges are clause variable sets. Repeatedly remove a weakly simplicial
    # variable: all remaining hyperedges containing it must form an inclusion chain.
    edges: Set[frozenset[int]] = {frozenset(abs(l) for l in c) for c in formula if c}
    vertices: Set[int] = set().union(*edges) if edges else set()
    order: List[int] = []
    chain_checks = 0
    while vertices:
        chosen = None
        for v in sorted(vertices):
            incident = sorted((e for e in edges if v in e), key=lambda e: (len(e), tuple(sorted(e))))
            ok = True
            for i in range(len(incident) - 1):
                chain_checks += 1
                if not incident[i] <= incident[i + 1]:
                    ok = False
                    break
            if ok:
                chosen = v
                break
        if chosen is None:
            return {"recognized": False, "reason": "NO_WEAKLY_SIMPLICIAL_VERTEX", "elimination_order": order, "remaining_vertices": sorted(vertices), "remaining_hyperedge_count": len(edges), "chain_checks": chain_checks}
        order.append(chosen)
        vertices.remove(chosen)
        edges = {frozenset(x for x in e if x != chosen) for e in edges}
        edges.discard(frozenset())
    return {"recognized": True, "reason": "BETA_ACYCLIC", "elimination_order": order, "chain_checks": chain_checks}


def extra_structure(formula: Formula) -> dict:
    width = Counter(len(c) for c in formula)
    pos = Counter(sum(1 for l in c if l > 0) for c in formula)
    neg = Counter(sum(1 for l in c if l < 0) for c in formula)
    dual_horn_count = sum(1 for c in formula if sum(1 for l in c if l < 0) <= 1)
    return {
        "clause_width_histogram": {str(k): v for k, v in sorted(width.items())},
        "positive_literal_count_per_clause_histogram": {str(k): v for k, v in sorted(pos.items())},
        "negative_literal_count_per_clause_histogram": {str(k): v for k, v in sorted(neg.items())},
        "dual_Horn_clause_count": dual_horn_count,
        "dual_Horn_clause_fraction": dual_horn_count / len(formula) if formula else 1.0,
    }


def run_intake() -> dict:
    frozen = materialize_r37b_fixpoint()
    formula = frozen["formula"]
    base_structure = r35.structure_intake(formula)
    renamable = renamable_horn_recognition(formula)
    dual = dual_horn_recognition(formula)
    beta = beta_acyclic_recognition(formula)
    extra = extra_structure(formula)

    if renamable["recognized"]:
        verdict = "R38_FIXPOINT_FROZEN__RENAMABLE_HORN_RECOGNIZED"
    elif dual["recognized"]:
        verdict = "R38_FIXPOINT_FROZEN__DUAL_HORN_RECOGNIZED"
    elif beta["recognized"]:
        verdict = "R38_FIXPOINT_FROZEN__BETA_ACYCLIC_RECOGNIZED"
    else:
        verdict = "R38_FIXPOINT_FROZEN__NO_AUDITED_STANDARD_TERMINAL_RECOGNIZED"

    return {
        "schema": "JANUS_TRUMP_R38_PORTFOLIO_FIXPOINT_FREEZE_STRUCTURE_INTAKE_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict,
        "frozen_fixpoint": {
            "seed": SEED,
            "measure_CLV": frozen["measure_CLV"],
            "canonical_formula_sha256": frozen["hash"],
            "cycle_count": len(frozen["cycles"]),
            "restart_count": frozen["restart_count"],
            "successful_transformations": frozen["successful_transformations"],
            "clauses": [list(c) for c in formula],
        },
        "structure_intake": {**base_structure, **extra},
        "exact_class_recognition": {
            "renamable_Horn": renamable,
            "dual_Horn": dual,
            "beta_acyclic": beta,
            "q_Horn": {"tested": False, "reason": "R38_CONTRACT_REQUIRES_SEPARATE_AUDITED_EXACT_RECOGNIZER_IF_NEEDED"},
        },
        "candidate_firewall": {
            "new_reduction_rule_added": False,
            "new_terminal_solver_added": False,
            "external_SAT_solver_used": False,
            "assignment_enumeration_used": False,
            "known_R36_SAT_truth_used": False,
            "FPT_or_width_probe_promoted_to_P_claim": False,
        },
        "captain_verdict": {
            "law": "RECOGNIZE THE EXACT FIXPOINT LANGUAGE BEFORE ADDING ANOTHER RULE.",
            "next_if_recognized": "Integrate only the standard polynomial solver for the first recognized class in a separate preregistered gate.",
            "next_if_none": "Return exact fixpoint to TOPA/Captain; q-Horn is eligible only via a separately audited exact recognizer."
        },
        "R31_obligation_impact": {"obligations_closed": 0},
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    d = run_intake()
    f = d["frozen_fixpoint"]
    assert f["canonical_formula_sha256"] == EXPECTED_FIXPOINT_HASH
    assert f["measure_CLV"] == EXPECTED_FIXPOINT_CLV
    assert f["cycle_count"] == 3 and f["restart_count"] == 2 and f["successful_transformations"] == 184
    assert not any(d["candidate_firewall"].values())
    if d["exact_class_recognition"]["renamable_Horn"]["recognized"]:
        assert d["exact_class_recognition"]["renamable_Horn"]["renamed_formula_horn_recheck"] is True
    print("R38_SELF_TEST_PASS", d["verdict"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_intake(), indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
