from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

Literal = int
Clause = Tuple[Literal, ...]
Formula = Tuple[Clause, ...]


def lit_key(l: int) -> tuple[int, int]:
    return (abs(l), 1 if l < 0 else 0)


def canonical_clause(clause: Iterable[int]) -> Clause:
    return tuple(sorted(set(int(x) for x in clause), key=lit_key))


def canonical_formula(clauses: Iterable[Iterable[int]]) -> Formula:
    seen, out = set(), []
    for clause in clauses:
        c = canonical_clause(clause)
        if c not in seen:
            seen.add(c)
            out.append(c)
    return tuple(sorted(out))


def is_tautology(clause: Clause) -> bool:
    s = set(clause)
    return any(-l in s for l in s)


def variables(formula: Formula) -> Tuple[int, ...]:
    return tuple(sorted({abs(l) for c in formula for l in c}))


def measure(formula: Formula) -> Tuple[int, int, int]:
    return (len(formula), sum(len(c) for c in formula), len(variables(formula)))


def is_horn(formula: Formula) -> bool:
    return all(sum(1 for l in c if l > 0) <= 1 for c in formula)


def is_2cnf(formula: Formula) -> bool:
    return all(len(c) <= 2 for c in formula)


def eval_clause(clause: Clause, assignment: Dict[int, bool]) -> bool:
    return any(assignment.get(abs(l), False) == (l > 0) for l in clause)


def eval_formula(formula: Formula, assignment: Dict[int, bool]) -> bool:
    return all(eval_clause(c, assignment) for c in formula)


def brute_force_model(formula: Formula) -> Optional[Dict[int, bool]]:
    vs = variables(formula)
    for bits in itertools.product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if eval_formula(formula, a):
            return a
    return None


def pure_literals(formula: Formula) -> List[int]:
    polarity: Dict[int, set[bool]] = defaultdict(set)
    for c in formula:
        for l in c:
            polarity[abs(l)].add(l > 0)
    out = []
    for v, signs in polarity.items():
        if len(signs) == 1:
            out.append(v if True in signs else -v)
    return sorted(out, key=lit_key)


def first_subsumed_clause(formula: Formula) -> Optional[Tuple[int, int]]:
    sets = [set(c) for c in formula]
    candidates = []
    for i, small in enumerate(formula):
        for j, large in enumerate(formula):
            if i != j and sets[i] <= sets[j]:
                candidates.append((large, small, j, i))
    if not candidates:
        return None
    _, _, j, i = min(candidates)
    return j, i


def first_blocked_clause(formula: Formula) -> Optional[Tuple[int, int]]:
    candidates = []
    for i, clause in enumerate(formula):
        cset = set(clause)
        for l in clause:
            ok = True
            for other in formula:
                if -l not in other:
                    continue
                r = (cset - {l}) | (set(other) - {-l})
                if not any(-x in r for x in r):
                    ok = False
                    break
            if ok:
                candidates.append((clause, lit_key(l), i, l))
    if not candidates:
        return None
    _, _, i, l = min(candidates)
    return i, l


def bve_candidate(formula: Formula):
    current = measure(formula)
    for x in variables(formula):
        pos = [c for c in formula if x in c]
        neg = [c for c in formula if -x in c]
        if not pos or not neg:
            continue
        resolvents = []
        for p in pos:
            for n in neg:
                r = (set(p) - {x}) | (set(n) - {-x})
                if any(-l in r for l in r):
                    continue
                resolvents.append(canonical_clause(r))
        resolvents = sorted(set(resolvents))
        removed = set(pos + neg)
        transformed = canonical_formula([c for c in formula if c not in removed] + resolvents)
        if len(resolvents) <= len(removed) and measure(transformed) < current:
            return x, tuple(pos), tuple(neg), tuple(resolvents), transformed
    return None


def certificate_bytes(record: dict) -> int:
    return len(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def simplify(formula: Formula, max_steps: int = 100000) -> dict:
    original = canonical_formula(formula)
    active = original
    history: List[dict] = []
    check_ops = 0

    def add(record: dict, before: Tuple[int, int, int], after: Tuple[int, int, int]):
        record["measure_before"] = list(before)
        record["measure_after"] = list(after)
        record["certificate_bytes"] = certificate_bytes(record)
        history.append(record)

    for _ in range(max_steps):
        if any(len(c) == 0 for c in active):
            terminal = "EMPTY_CLAUSE_UNSAT"
            break
        if not active:
            terminal = "EMPTY_CNF_SAT"
            break
        before = measure(active)

        tauts = [(c, i) for i, c in enumerate(active) if is_tautology(c)]
        check_ops += sum(len(c) for c in active)
        if tauts:
            _, i = min(tauts)
            clause = active[i]
            active = tuple(c for j, c in enumerate(active) if j != i)
            add({"rule": "TAUTOLOGY_DELETION", "clause": list(clause)}, before, measure(active))
            continue

        units = sorted([c[0] for c in active if len(c) == 1], key=lit_key)
        check_ops += len(active)
        if units:
            l = units[0]
            nf, touched = [], 0
            for c in active:
                if l in c:
                    touched += 1
                    continue
                if -l in c:
                    touched += 1
                    nf.append(tuple(x for x in c if x != -l))
                else:
                    nf.append(c)
            active = canonical_formula(nf)
            add({"rule": "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE", "literal": l, "touched_clauses": touched}, before, measure(active))
            continue

        pures = pure_literals(active)
        check_ops += sum(len(c) for c in active)
        if pures:
            l = pures[0]
            removed = [c for c in active if l in c]
            active = tuple(c for c in active if l not in c)
            add({"rule": "PURE_LITERAL_AUTARKY", "literal": l, "removed_clauses": [list(c) for c in removed]}, before, measure(active))
            continue

        subsumed = first_subsumed_clause(active)
        check_ops += len(active) * len(active)
        if subsumed is not None:
            j, i = subsumed
            large, small = active[j], active[i]
            active = tuple(c for k, c in enumerate(active) if k != j)
            add({"rule": "SUBSUMPTION", "deleted": list(large), "witness_subclause": list(small)}, before, measure(active))
            continue

        blocked = first_blocked_clause(active)
        check_ops += sum(len(c) for c in active) * max(1, len(active))
        if blocked is not None:
            i, l = blocked
            clause = active[i]
            active = tuple(c for j, c in enumerate(active) if j != i)
            add({"rule": "BLOCKED_CLAUSE_ELIMINATION", "clause": list(clause), "blocking_literal": l}, before, measure(active))
            continue

        bve = bve_candidate(active)
        check_ops += max(1, len(variables(active))) * max(1, len(active) * len(active))
        if bve is not None:
            x, pos, neg, resolvents, transformed = bve
            active = transformed
            add({"rule": "BOUNDED_VARIABLE_ELIMINATION", "var": x, "positive": [list(c) for c in pos], "negative": [list(c) for c in neg], "resolvents": [list(c) for c in resolvents]}, before, measure(active))
            continue

        if is_2cnf(active):
            terminal = "2CNF"
        elif is_horn(active):
            terminal = "HORN"
        else:
            terminal = "STALLED_STACK_LEAN_CORE"
        break
    else:
        terminal = "FAIL_STEP_LIMIT"

    return {
        "initial_measure": list(measure(original)),
        "final_measure": list(measure(active)),
        "terminal": terminal,
        "history": history,
        "rule_counts": dict(sorted(Counter(r["rule"] for r in history).items())),
        "total_rule_applications": len(history),
        "total_certificate_bytes": sum(r["certificate_bytes"] for r in history),
        "total_check_operation_count_upper_ledger": check_ops,
        "strict_progress": all(tuple(r["measure_after"]) < tuple(r["measure_before"]) for r in history),
        "final_formula": [list(c) for c in active],
    }


def reconstruct_model(result: dict, final_model: Dict[int, bool]) -> Dict[int, bool]:
    a = dict(final_model)
    for record in reversed(result["history"]):
        rule = record["rule"]
        if rule in {"UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE", "PURE_LITERAL_AUTARKY"}:
            l = int(record["literal"])
            a[abs(l)] = l > 0
        elif rule == "BOUNDED_VARIABLE_ELIMINATION":
            x = int(record["var"])
            pos = [tuple(c) for c in record["positive"]]
            neg = [tuple(c) for c in record["negative"]]
            need_true = any(not eval_clause(tuple(l for l in c if l != x), a) for c in pos)
            need_false = any(not eval_clause(tuple(l for l in c if l != -x), a) for c in neg)
            if need_true and need_false:
                raise AssertionError("BVE reconstruction conflict")
            a[x] = True if need_true else False
        elif rule == "BLOCKED_CLAUSE_ELIMINATION":
            clause = tuple(record["clause"])
            if not eval_clause(clause, a):
                l = int(record["blocking_literal"])
                a[abs(l)] = l > 0
    return a


def semantic_control(name: str, formula: Formula, required_rule: str) -> dict:
    result = simplify(formula)
    final = canonical_formula(result["final_formula"])
    before_model = brute_force_model(canonical_formula(formula))
    after_model = brute_force_model(final)
    before_sat, after_sat = before_model is not None, after_model is not None
    reconstruction_ok = True
    if after_model is not None:
        reconstruction_ok = eval_formula(canonical_formula(formula), reconstruct_model(result, after_model))
    rule_seen = required_rule in result["rule_counts"]
    passed = before_sat == after_sat and reconstruction_ok and result["strict_progress"] and rule_seen
    if not passed:
        raise AssertionError(name)
    return {"name": name, "pass": passed, "sat_before": before_sat, "sat_after": after_sat, "reconstruction_ok": reconstruction_ok, "required_rule": required_rule, "required_rule_seen": rule_seen, "result": result}


def easy_redundant_tail() -> Formula:
    return canonical_formula([(1,), (-1, 2, 3), (-2, 4), (-3, 4), (-4, 5), (5, 6, 7), (-5, 6), (6, -6, 8)])


def blocked_clause_control() -> Formula:
    return canonical_formula([(1, 2), (1, -2, -3), (-1, 3)])


def bve_control() -> Formula:
    return canonical_formula([(-2, -4), (-1, -2), (-1, 3, -5), (1, -4), (2, -3), (4, 5)])


def prism_tseitin(n_vertices: int) -> Formula:
    if n_vertices < 8 or n_vertices % 2:
        raise ValueError("prism family requires even n >= 8")
    k = n_vertices // 2
    edges: List[Tuple[int, int]] = []
    def add_edge(u: int, v: int):
        if u > v:
            u, v = v, u
        if (u, v) not in edges:
            edges.append((u, v))
    for i in range(k):
        add_edge(i, (i + 1) % k)
        add_edge(k + i, k + ((i + 1) % k))
        add_edge(i, k + i)
    incident: Dict[int, List[int]] = defaultdict(list)
    for edge_var, (u, v) in enumerate(edges, 1):
        incident[u].append(edge_var)
        incident[v].append(edge_var)
    charges = [1] + [0] * (n_vertices - 1)
    clauses: List[Clause] = []
    for vertex in range(n_vertices):
        xs = sorted(incident[vertex])
        if len(xs) != 3:
            raise AssertionError("prism must be 3-regular")
        target = charges[vertex]
        for bits in itertools.product((0, 1), repeat=3):
            if sum(bits) % 2 == target:
                continue
            clauses.append(tuple(x if bit == 0 else -x for x, bit in zip(xs, bits)))
    return canonical_formula(clauses)


def deterministic_random_3cnf(seed: int, n: int = 24, ratio: float = 4.2) -> Formula:
    rng = random.Random(seed)
    target = round(n * ratio)
    clauses = set()
    while len(clauses) < target:
        vs = sorted(rng.sample(range(1, n + 1), 3))
        clauses.add(canonical_clause(v if rng.getrandbits(1) else -v for v in vs))
    return canonical_formula(clauses)


def run_audit() -> dict:
    controls = [
        semantic_control("EASY_REDUNDANT_TAIL", easy_redundant_tail(), "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE"),
        semantic_control("BLOCKED_CLAUSE_CONTROL", blocked_clause_control(), "BLOCKED_CLAUSE_ELIMINATION"),
        semantic_control("BVE_CONTROL", bve_control(), "BOUNDED_VARIABLE_ELIMINATION"),
    ]
    tseitin = []
    for n in (8, 12, 16, 20, 24, 28, 32):
        f = prism_tseitin(n)
        r = simplify(f)
        tseitin.append({"n_vertices": n, "edge_variables": len(variables(f)), "initial_measure": r["initial_measure"], "final_measure": r["final_measure"], "terminal": r["terminal"], "total_rule_applications": r["total_rule_applications"], "rule_counts": r["rule_counts"], "strict_progress": r["strict_progress"], "core_fraction_clauses": r["final_measure"][0] / r["initial_measure"][0]})
    random_controls = []
    for seed in (33001, 33002, 33003, 33004):
        f = deterministic_random_3cnf(seed)
        r = simplify(f)
        random_controls.append({"seed": seed, "initial_measure": r["initial_measure"], "final_measure": r["final_measure"], "terminal": r["terminal"], "total_rule_applications": r["total_rule_applications"], "rule_counts": r["rule_counts"], "strict_progress": r["strict_progress"], "core_fraction_clauses": r["final_measure"][0] / r["initial_measure"][0]})
    all_positive = all(c["pass"] for c in controls)
    any_stall = any(x["terminal"] == "STALLED_STACK_LEAN_CORE" for x in tseitin + random_controls)
    verdict = "R33_CERTIFIED_REDUCTION_STACK_STALLS_ON_LEAN_CORE" if all_positive and any_stall else "R33_CERTIFIED_REDUCTION_STACK_REACHES_TRACTABLE_TERMINAL_ON_ALL_FROZEN_CONTROLS__NO_UNIVERSAL_CLAIM" if all_positive else "R33_FAIL_INTEGRITY"
    return {
        "schema": "JANUS_TRUMP_R33_CERTIFIED_SAFE_REDUCTION_STACK_LEAN_CORE_FORENSICS_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "verdict": verdict,
        "candidate_firewall": {"external_SAT_solver_used": False, "assignment_enumeration_inside_candidate": False, "global_semantic_redundancy_check": False, "rule_order_frozen": True, "tie_break_frozen": True},
        "positive_semantic_controls": controls,
        "tseitin_3regular_prism_family": tseitin,
        "deterministic_random_3cnf": random_controls,
        "captain_verdict": {"answer": "CERTIFIED_TAIL_DELETION_IS_REAL_BUT_THE_FROZEN_SAFE_STACK_HAS_A_LEAN_CORE", "key_observation": "The sparse 3-regular Tseitin family reaches a fixpoint with zero rule applications under every frozen R33 rule, so safe deletion alone does not provide a universal progress theorem.", "not_proved": ["universal polynomial progress", "SAT in P", "P=NP"]},
        "R31_obligation_impact": {"obligations_closed": 0, "reason": "R33 supplies certified local reductions but also a concrete nonterminal stall family."},
        "next_gate": {"id": "R34_SINGLE_NEW_CERTIFIED_PROGRESS_RULE_AGAINST_TSEITIN_STALL_CORE", "instruction": "Freeze the smallest reproducible stalled core first. Propose exactly one new polynomial-time detectable, proof-carrying, SAT-preserving rule that strictly reduces that core without invoking SAT. If no such rule is found, preserve OPEN rather than broadening the rule after seeing results.", "secondary_structural_probe": "Measure whether the stalled core exposes a bounded parameter (backdoor, width, representative-family boundary, deficiency) that is itself provably polynomially bounded under a fixed policy. Parameterized/FPT dependence alone is not P."},
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    d = run_audit()
    assert d["verdict"] == "R33_CERTIFIED_REDUCTION_STACK_STALLS_ON_LEAN_CORE"
    assert all(x["pass"] for x in d["positive_semantic_controls"])
    ts = d["tseitin_3regular_prism_family"]
    assert [x["n_vertices"] for x in ts] == [8, 12, 16, 20, 24, 28, 32]
    assert all(x["terminal"] == "STALLED_STACK_LEAN_CORE" for x in ts)
    assert all(x["total_rule_applications"] == 0 for x in ts)
    assert all(x["core_fraction_clauses"] == 1.0 for x in ts)
    print("R33_SELF_TEST_PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_audit(), indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
