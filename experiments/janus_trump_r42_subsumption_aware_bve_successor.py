from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b

Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]

EXPOSED = {"seed": 36001, "n": 28, "ratio": 4.2}
HOLDOUTS = (
    {"seed": 42001, "n": 28, "ratio": 4.2},
    {"seed": 42002, "n": 28, "ratio": 4.2},
    {"seed": 42003, "n": 28, "ratio": 4.2},
    {"seed": 42004, "n": 28, "ratio": 4.2},
    {"seed": 42005, "n": 28, "ratio": 4.2},
    {"seed": 42006, "n": 28, "ratio": 4.2},
    {"seed": 42101, "n": 36, "ratio": 4.3},
    {"seed": 42102, "n": 36, "ratio": 4.3},
    {"seed": 42103, "n": 36, "ratio": 4.3},
)
EXPECTED_EXPOSED_R37B_STALL_HASH = "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"


def canonical_json_sha256(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def formula_hash(formula: Formula) -> str:
    return canonical_json_sha256([list(c) for c in formula])


def clv(formula: Formula) -> Tuple[int, int, int]:
    return r33.measure(formula)


def subsumption_minimize(clauses: Iterable[Iterable[int]]) -> Formula:
    formula = r33.canonical_formula(clauses)
    sets = [set(c) for c in formula]
    keep: List[Clause] = []
    for i, clause in enumerate(formula):
        if any(j != i and sets[j] < sets[i] for j in range(len(formula))):
            continue
        keep.append(clause)
    return r33.canonical_formula(keep)


def all_dp_resolvents(formula: Formula, var: int) -> Tuple[Tuple[Clause, ...], Tuple[Clause, ...], Tuple[Clause, ...], int]:
    pos = tuple(c for c in formula if var in c)
    neg = tuple(c for c in formula if -var in c)
    resolvents = set()
    pair_checks = 0
    for p in pos:
        for n in neg:
            pair_checks += 1
            raw = (set(p) - {var}) | (set(n) - {-var})
            if any(-lit in raw for lit in raw):
                continue
            resolvents.add(r33.canonical_clause(raw))
    return pos, neg, tuple(sorted(resolvents)), pair_checks


def sa_bve_candidate_for_var(formula: Formula, var: int) -> Optional[dict]:
    before = r33.canonical_formula(formula)
    pos, neg, resolvents, pair_checks = all_dp_resolvents(before, var)
    if not pos or not neg:
        return None
    base = tuple(c for c in before if var not in c and -var not in c)
    pool = r33.canonical_formula(list(base) + list(resolvents))
    transformed = subsumption_minimize(pool)
    before_measure = clv(before)
    after_measure = clv(transformed)
    if not after_measure < before_measure:
        return None
    return {
        "var": var,
        "positive": [list(c) for c in pos],
        "negative": [list(c) for c in neg],
        "full_non_tautological_resolvents": [list(c) for c in resolvents],
        "pool_clause_count_before_subsumption": len(pool),
        "transformed": [list(c) for c in transformed],
        "measure_before": list(before_measure),
        "measure_after": list(after_measure),
        "pair_checks": pair_checks,
        "subsumption_pair_upper_ledger": len(pool) * len(pool),
    }


def best_sa_bve_candidate(formula: Formula) -> Tuple[Optional[dict], dict]:
    candidates = []
    ledger = {"variables_checked": 0, "resolution_pair_checks": 0, "subsumption_pair_upper_ledger": 0}
    for var in r33.variables(formula):
        ledger["variables_checked"] += 1
        pos, neg, _, pair_checks = all_dp_resolvents(formula, var)
        ledger["resolution_pair_checks"] += pair_checks
        if not pos or not neg:
            continue
        candidate = sa_bve_candidate_for_var(formula, var)
        if candidate is not None:
            ledger["subsumption_pair_upper_ledger"] += candidate["subsumption_pair_upper_ledger"]
            candidates.append(candidate)
    if not candidates:
        return None, ledger
    candidates.sort(key=lambda x: (tuple(x["measure_after"]), int(x["var"])))
    return candidates[0], ledger


def independent_sa_bve_replay(before_formula: Formula, record: dict) -> dict:
    before = r33.canonical_formula(before_formula)
    var = int(record["var"])
    pos, neg, resolvents, _ = all_dp_resolvents(before, var)
    base = tuple(c for c in before if var not in c and -var not in c)
    expected = subsumption_minimize(list(base) + list(resolvents))
    claimed = r33.canonical_formula(record["transformed"])
    sources_ok = [list(c) for c in pos] == record["positive"] and [list(c) for c in neg] == record["negative"]
    resolvents_ok = [list(c) for c in resolvents] == record["full_non_tautological_resolvents"]
    after_ok = expected == claimed
    progress_ok = clv(claimed) < clv(before)
    var_removed = var not in r33.variables(claimed)
    omitted_resolvents = [r for r in resolvents if r not in claimed]
    claimed_sets = [set(c) for c in claimed]
    omitted_subsumed = all(any(s <= set(r) for s in claimed_sets) for r in omitted_resolvents)
    return {
        "pass": sources_ok and resolvents_ok and after_ok and progress_ok and var_removed and omitted_subsumed,
        "sources_ok": sources_ok,
        "resolvents_ok": resolvents_ok,
        "after_ok": after_ok,
        "progress_ok": progress_ok,
        "var_removed": var_removed,
        "omitted_resolvent_count": len(omitted_resolvents),
        "every_omitted_resolvent_subsumed": omitted_subsumed,
    }


def reconstruct_sa_bve(record: dict, assignment: Dict[int, bool]) -> Dict[int, bool]:
    out = dict(assignment)
    var = int(record["var"])
    source_clauses = [tuple(c) for c in record["positive"]] + [tuple(c) for c in record["negative"]]
    for value in (False, True):
        trial = dict(out)
        trial[var] = value
        if all(r33.eval_clause(c, trial) for c in source_clauses):
            return trial
    raise AssertionError(("SA_BVE_MODEL_RECONSTRUCTION_FAILED", var))


def horn_solve(formula: Formula) -> dict:
    if not r33.is_horn(formula):
        raise AssertionError("not Horn")
    assignment = {v: False for v in r33.variables(formula)}
    trace = []
    scans = 0
    while True:
        changed = False
        for ci, clause in enumerate(formula):
            scans += 1
            pos = [l for l in clause if l > 0]
            neg_vars = [abs(l) for l in clause if l < 0]
            if len(pos) > 1:
                raise AssertionError("Horn recognizer drift")
            if all(assignment[v] for v in neg_vars):
                if not pos:
                    return {"sat": False, "trace": trace, "conflict_clause_index": ci, "clause_scans": scans}
                head = pos[0]
                if not assignment[head]:
                    assignment[head] = True
                    trace.append({"set_true": head, "clause_index": ci})
                    changed = True
        if not changed:
            break
    if not r33.eval_formula(formula, assignment):
        raise AssertionError("Horn least model failed CNF replay")
    return {"sat": True, "assignment": assignment, "trace": trace, "clause_scans": scans}


def independent_horn_status(formula: Formula) -> bool:
    rules = []
    for clause in formula:
        pos = tuple(l for l in clause if l > 0)
        if len(pos) > 1:
            raise AssertionError("not Horn")
        antecedent = frozenset(abs(l) for l in clause if l < 0)
        rules.append((antecedent, pos[0] if pos else None))
    true_set = set()
    while True:
        changed = False
        for antecedent, head in rules:
            if antecedent <= true_set:
                if head is None:
                    return False
                if head not in true_set:
                    true_set.add(head)
                    changed = True
        if not changed:
            return True


def implication_graph(formula: Formula, extra_units: Sequence[int] = ()) -> Tuple[Dict[int, List[int]], Tuple[int, ...]]:
    if not r33.is_2cnf(formula):
        raise AssertionError("not 2CNF")
    vars_set = set(r33.variables(formula)) | {abs(l) for l in extra_units}
    graph: Dict[int, List[int]] = {lit: [] for v in vars_set for lit in (v, -v)}

    def edge(a: int, b: int) -> None:
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, [])

    clauses = list(formula) + [(int(l),) for l in extra_units]
    for clause in clauses:
        if len(clause) == 0:
            return graph, tuple(sorted(vars_set))
        if len(clause) == 1:
            a = clause[0]
            edge(-a, a)
        elif len(clause) == 2:
            a, b = clause
            edge(-a, b)
            edge(-b, a)
        else:
            raise AssertionError("not 2CNF")
    for node in graph:
        graph[node] = sorted(set(graph[node]), key=lambda x: (abs(x), x < 0))
    return graph, tuple(sorted(vars_set))


def scc_components(graph: Dict[int, List[int]]) -> Dict[int, int]:
    nodes = sorted(graph, key=lambda x: (abs(x), x < 0))
    reverse: Dict[int, List[int]] = {n: [] for n in nodes}
    for a, outs in graph.items():
        for b in outs:
            reverse.setdefault(b, []).append(a)
    seen = set()
    order: List[int] = []

    def dfs1(v: int) -> None:
        seen.add(v)
        for w in graph.get(v, []):
            if w not in seen:
                dfs1(w)
        order.append(v)

    for v in nodes:
        if v not in seen:
            dfs1(v)

    comp: Dict[int, int] = {}

    def dfs2(v: int, cid: int) -> None:
        comp[v] = cid
        for w in reverse.get(v, []):
            if w not in comp:
                dfs2(w, cid)

    cid = 0
    for v in reversed(order):
        if v not in comp:
            dfs2(v, cid)
            cid += 1
    return comp


def two_sat_status(formula: Formula, extra_units: Sequence[int] = ()) -> dict:
    if any(len(c) == 0 for c in formula):
        return {"sat": False, "contradiction_var": None}
    graph, vs = implication_graph(formula, extra_units)
    comp = scc_components(graph)
    bad = next((v for v in vs if comp.get(v) == comp.get(-v)), None)
    return {"sat": bad is None, "contradiction_var": bad, "component_count": len(set(comp.values()))}


def solve_2cnf(formula: Formula) -> dict:
    base = two_sat_status(formula)
    calls = 1
    if not base["sat"]:
        return {"sat": False, "contradiction_var": base["contradiction_var"], "scc_calls": calls}
    units: List[int] = []
    for v in r33.variables(formula):
        false_try = two_sat_status(formula, tuple(units + [-v]))
        calls += 1
        if false_try["sat"]:
            units.append(-v)
        else:
            true_try = two_sat_status(formula, tuple(units + [v]))
            calls += 1
            if not true_try["sat"]:
                raise AssertionError(("2SAT witness extraction lost satisfiability", v))
            units.append(v)
    assignment = {abs(l): l > 0 for l in units}
    if not r33.eval_formula(formula, assignment):
        raise AssertionError("2SAT extracted model failed CNF replay")
    return {"sat": True, "assignment": assignment, "decision_units": units, "scc_calls": calls}


def solve_declared_terminal(formula: Formula, terminal: str) -> dict:
    if terminal == "EMPTY_CNF_SAT":
        return {"semantic": True, "sat": True, "assignment": {}, "verification_pass": True, "kind": "DIRECT_EMPTY_CNF"}
    if terminal == "EMPTY_CLAUSE_UNSAT":
        ok = any(len(c) == 0 for c in formula)
        return {"semantic": True, "sat": False, "verification_pass": ok, "kind": "DIRECT_EMPTY_CLAUSE"}
    if terminal == "HORN":
        solved = horn_solve(formula)
        if solved["sat"]:
            verify = independent_horn_status(formula) and r33.eval_formula(formula, solved["assignment"])
        else:
            verify = not independent_horn_status(formula)
        return {"semantic": True, "sat": solved["sat"], "assignment": solved.get("assignment"), "verification_pass": verify, "kind": "HORN_FORWARD_CHAIN", "solver": solved}
    if terminal == "2CNF":
        solved = solve_2cnf(formula)
        if solved["sat"]:
            verify = r33.eval_formula(formula, solved["assignment"])
        else:
            verify = not two_sat_status(formula)["sat"]
        return {"semantic": True, "sat": solved["sat"], "assignment": solved.get("assignment"), "verification_pass": verify, "kind": "2SAT_SCC", "solver": solved}
    raise AssertionError(terminal)


def rank_parameters(initial_formula: Formula) -> dict:
    c0, _, v0 = clv(initial_formula)
    lmax = c0 * v0
    return {"C0": c0, "V0": v0, "Lmax": lmax}


def mu(formula: Formula, rank: dict) -> int:
    c, l, v = clv(formula)
    if c > rank["C0"] or v > rank["V0"] or l > rank["Lmax"]:
        raise AssertionError(("R42_RANK_BOUND_VIOLATION", clv(formula), rank))
    return c * (rank["Lmax"] + 1) * (rank["V0"] + 1) + l * (rank["V0"] + 1) + v


def reconstruct_full_model(events: List[dict], terminal_assignment: Dict[int, bool], original_formula: Formula) -> dict:
    assignment = {int(v): bool(b) for v, b in terminal_assignment.items()}
    for event in reversed(events):
        if event["kind"] == "SA_BVE":
            assignment = reconstruct_sa_bve(event["record"], assignment)
        elif event["kind"] == "R33":
            assignment = r33.reconstruct_model(event["result"], assignment)
        else:
            raise AssertionError(event["kind"])
    passed = r33.eval_formula(original_formula, assignment)
    return {"pass": passed, "assignment": assignment}


def run_fixed_successor(initial_formula: Formula, label: str) -> dict:
    original = r33.canonical_formula(initial_formula)
    formula = original
    rank = rank_parameters(original)
    rank0 = mu(original, rank)
    cycles: List[dict] = []
    reconstruction_events: List[dict] = []
    ledger = {
        "R33_check_operation_upper_ledger": 0,
        "R33_certificate_bytes": 0,
        "RUP_checks": 0,
        "RUP_UP_clause_scans": 0,
        "RUP_UP_literal_inspections": 0,
        "SA_BVE_variables_checked": 0,
        "SA_BVE_resolution_pair_checks": 0,
        "SA_BVE_subsumption_pair_upper_ledger": 0,
        "GF2_estimated_bit_ops": 0,
        "terminal_Horn_clause_scans": 0,
        "terminal_2SAT_scc_calls": 0,
    }
    terminal_status = None
    semantic_sat: Optional[bool] = None
    terminal_assignment: Optional[Dict[int, bool]] = None
    terminal_verification = None
    terminal_formula = formula
    sa_bve_count = 0

    for cycle_index in range(rank0 + 1):
        before = formula
        before_measure = clv(before)
        before_mu = mu(before, rank)
        cycle: Dict = {"cycle": cycle_index, "before_measure_CLV": list(before_measure), "before_mu": before_mu}

        reduced = r33.simplify(before)
        after_r33 = r33.canonical_formula(reduced["final_formula"])
        r33_changed = after_r33 != before
        if r33_changed and not (clv(after_r33) < before_measure and mu(after_r33, rank) < before_mu):
            raise AssertionError(("R33_GLOBAL_RANK_FAIL", before_measure, clv(after_r33)))
        if reduced["history"]:
            reconstruction_events.append({"kind": "R33", "result": reduced})
        ledger["R33_check_operation_upper_ledger"] += reduced["total_check_operation_count_upper_ledger"]
        ledger["R33_certificate_bytes"] += reduced["total_certificate_bytes"]
        cycle["R33"] = {
            "terminal": reduced["terminal"],
            "rule_applications": reduced["total_rule_applications"],
            "rule_counts": reduced["rule_counts"],
            "after_measure_CLV": list(clv(after_r33)),
            "changed": r33_changed,
        }

        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            solved = solve_declared_terminal(after_r33, reduced["terminal"])
            if not solved["verification_pass"]:
                raise AssertionError(("DECLARED_TERMINAL_VERIFY_FAIL", solved))
            terminal_status = solved["kind"]
            semantic_sat = bool(solved["sat"])
            terminal_assignment = solved.get("assignment")
            terminal_verification = solved
            terminal_formula = after_r33
            if solved["kind"] == "HORN_FORWARD_CHAIN":
                ledger["terminal_Horn_clause_scans"] += solved["solver"]["clause_scans"]
            if solved["kind"] == "2SAT_SCC":
                ledger["terminal_2SAT_scc_calls"] += solved["solver"]["scc_calls"]
            cycle["stop"] = terminal_status
            cycles.append(cycle)
            break

        recognition = r34.recognize_complete_affine_cnf(after_r33)
        cycle["R34"] = {"recognized": recognition["recognized"], "reason": recognition["reason"]}
        if recognition["recognized"]:
            solution = r34.solve_gf2_with_certificate(recognition["equations"])
            verify = r34.verify_affine_certificate(after_r33, recognition, solution)
            if not verify["pass"]:
                raise AssertionError(("AFFINE_VERIFY_FAIL", verify))
            ledger["GF2_estimated_bit_ops"] += solution["estimated_bit_ops"]
            terminal_status = "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT"
            semantic_sat = bool(solution["sat"])
            terminal_assignment = solution.get("assignment")
            terminal_verification = verify
            terminal_formula = after_r33
            cycle["stop"] = terminal_status
            cycles.append(cycle)
            break

        rup = r35b.run_candidate(after_r33)
        rup_replay = r35b.independent_certificate_replay(after_r33, rup)
        if not rup_replay["pass"]:
            raise AssertionError(("RUP_REPLAY_FAIL", cycle_index, rup_replay))
        after_rup = r33.canonical_formula(rup["final_formula"])
        rup_changed = after_rup != after_r33
        if rup_changed and not (clv(after_rup) < clv(after_r33) and mu(after_rup, rank) < mu(after_r33, rank)):
            raise AssertionError(("RUP_GLOBAL_RANK_FAIL", clv(after_r33), clv(after_rup)))
        ledger["RUP_checks"] += rup["ledger"]["rup_checks"]
        ledger["RUP_UP_clause_scans"] += rup["ledger"]["up_clause_scans"]
        ledger["RUP_UP_literal_inspections"] += rup["ledger"]["up_literal_inspections"]
        cycle["R35B_RUP"] = {
            "status": rup["status"],
            "successful_strengthenings": rup["successful_strengthenings"],
            "after_measure_CLV": list(clv(after_rup)),
            "changed": rup_changed,
            "independent_replay_pass": rup_replay["pass"],
        }
        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            terminal_status = "RUP_UNSAT"
            semantic_sat = False
            terminal_verification = rup_replay
            terminal_formula = after_rup
            cycle["stop"] = terminal_status
            cycles.append(cycle)
            break

        bve, bve_ledger = best_sa_bve_candidate(after_rup)
        ledger["SA_BVE_variables_checked"] += bve_ledger["variables_checked"]
        ledger["SA_BVE_resolution_pair_checks"] += bve_ledger["resolution_pair_checks"]
        ledger["SA_BVE_subsumption_pair_upper_ledger"] += bve_ledger["subsumption_pair_upper_ledger"]
        bve_changed = bve is not None
        after_bve = after_rup
        if bve is not None:
            bve_replay = independent_sa_bve_replay(after_rup, bve)
            if not bve_replay["pass"]:
                raise AssertionError(("SA_BVE_REPLAY_FAIL", cycle_index, bve_replay))
            after_bve = r33.canonical_formula(bve["transformed"])
            if not (clv(after_bve) < clv(after_rup) and mu(after_bve, rank) < mu(after_rup, rank)):
                raise AssertionError(("SA_BVE_GLOBAL_RANK_FAIL", clv(after_rup), clv(after_bve)))
            reconstruction_events.append({"kind": "SA_BVE", "record": bve})
            sa_bve_count += 1
            cycle["SA_BVE"] = {
                "applied": True,
                "var": bve["var"],
                "measure_before": bve["measure_before"],
                "measure_after": bve["measure_after"],
                "full_resolvent_count": len(bve["full_non_tautological_resolvents"]),
                "independent_replay": bve_replay,
            }
        else:
            cycle["SA_BVE"] = {"applied": False}

        changed = after_bve != before
        cycle["after_measure_CLV"] = list(clv(after_bve))
        cycle["after_mu"] = mu(after_bve, rank)
        if changed:
            if not cycle["after_mu"] < before_mu:
                raise AssertionError(("FULL_CYCLE_NO_DESCENT", before_mu, cycle["after_mu"]))
            cycle["restart"] = True
            cycles.append(cycle)
            formula = after_bve
            continue

        terminal_status = "STALLED_FIXED_SUCCESSOR"
        semantic_sat = None
        terminal_formula = after_bve
        cycle["stop"] = terminal_status
        cycles.append(cycle)
        break
    else:
        raise AssertionError("R42 integer rank exhausted")

    reconstruction = None
    if semantic_sat is True:
        assert terminal_assignment is not None
        reconstruction = reconstruct_full_model(reconstruction_events, terminal_assignment, original)
        if not reconstruction["pass"]:
            raise AssertionError(("FINAL_ORIGINAL_MODEL_REPLAY_FAIL", label))

    return {
        "label": label,
        "initial_formula_hash": formula_hash(original),
        "initial_measure_CLV": list(clv(original)),
        "rank": {**rank, "initial_mu": rank0},
        "cycles": cycles,
        "cycle_count": len(cycles),
        "SA_BVE_applications": sa_bve_count,
        "terminal_status": terminal_status,
        "semantic_decided": semantic_sat is not None,
        "semantic_sat": semantic_sat,
        "terminal_formula_hash": formula_hash(terminal_formula),
        "terminal_measure_CLV": list(clv(terminal_formula)),
        "terminal_verification": terminal_verification,
        "final_original_model_replay": reconstruction,
        "ledger": ledger,
    }


def structured_controls() -> dict:
    # The positive control is deliberately chosen so legacy raw-resolvent BVE has
    # no candidate while subsumption-aware BVE has a strict class-level step.
    positive = r33.canonical_formula([
        (-2, -3, -4),
        (-1, -2, -3),
        (-1, 3),
        (-1, 3, 5),
        (3, 5),
    ])
    legacy = r33.bve_candidate(positive)
    candidate, _ = best_sa_bve_candidate(positive)
    positive_replay = independent_sa_bve_replay(positive, candidate) if candidate else {"pass": False}

    negative = r33.canonical_formula([(1, 2, 3), (2, 3, 4)])
    negative_candidate, _ = best_sa_bve_candidate(negative)

    horn_sat = r33.canonical_formula([(1,), (-1, 2), (-2, 3)])
    horn_unsat = r33.canonical_formula([(1,), (-1, 2), (-2,)])
    hs = horn_solve(horn_sat)
    hu = horn_solve(horn_unsat)

    two_sat_sat = r33.canonical_formula([(1, 2), (-1, 2), (1, -2)])
    two_sat_unsat = r33.canonical_formula([(1, 2), (1, -2), (-1, 2), (-1, -2)])
    ts = solve_2cnf(two_sat_sat)
    tu = solve_2cnf(two_sat_unsat)

    affine = []
    for n in (8, 16, 24):
        f = r33.prism_tseitin(n)
        result = run_fixed_successor(f, f"AFFINE_TSEITIN_{n}")
        affine.append({"n": n, "terminal_status": result["terminal_status"], "semantic_decided": result["semantic_decided"], "semantic_sat": result["semantic_sat"]})

    return {
        "SA_BVE_POSITIVE": {
            "pass": legacy is None and candidate is not None and positive_replay["pass"],
            "legacy_BVE_candidate": legacy is not None,
            "SA_BVE_var": candidate["var"] if candidate else None,
            "measure_before": list(clv(positive)),
            "measure_after": candidate["measure_after"] if candidate else None,
            "replay": positive_replay,
        },
        "SA_BVE_NEGATIVE": {"pass": negative_candidate is None},
        "HORN_SAT": {"pass": hs["sat"] is True and r33.eval_formula(horn_sat, hs["assignment"])},
        "HORN_UNSAT": {"pass": hu["sat"] is False and independent_horn_status(horn_unsat) is False},
        "2CNF_SAT": {"pass": ts["sat"] is True and r33.eval_formula(two_sat_sat, ts["assignment"])},
        "2CNF_UNSAT": {"pass": tu["sat"] is False and two_sat_status(two_sat_unsat)["sat"] is False},
        "AFFINE_CONTROLS": {"pass": all(x["semantic_decided"] and x["semantic_sat"] is False for x in affine), "rows": affine},
    }


def run_audit() -> dict:
    controls = structured_controls()
    controls_pass = all(v["pass"] for v in controls.values())

    exposed_formula = r33.deterministic_random_3cnf(EXPOSED["seed"], n=EXPOSED["n"], ratio=EXPOSED["ratio"])
    exposed = run_fixed_successor(exposed_formula, "EXPOSED_R37B_STALL_36001")

    holdouts = []
    for spec in HOLDOUTS:
        f = r33.deterministic_random_3cnf(spec["seed"], n=spec["n"], ratio=spec["ratio"])
        row = run_fixed_successor(f, f"HOLDOUT_{spec['seed']}")
        holdouts.append({**spec, **row})

    exposed_repaired = exposed["semantic_decided"] and exposed["terminal_formula_hash"] != EXPECTED_EXPOSED_R37B_STALL_HASH
    unseen_stalls = [x for x in holdouts if not x["semantic_decided"]]

    if not controls_pass:
        verdict = "R42_FAIL_INTEGRITY"
    elif not exposed["semantic_decided"]:
        verdict = "R42_EXPOSED_STALL_NOT_REPAIRED__SUCCESSOR_REFUTED"
    elif unseen_stalls:
        verdict = "R42_EXPOSED_STALL_REPAIRED__UNSEEN_STALL_REMAINS__SUCCESSOR_REFUTED_FOR_L2"
    else:
        verdict = "R42_EXPOSED_AND_PREREGISTERED_HOLDOUTS_DECIDED__L2_STILL_UNPROVED"

    first_stall = None
    if not exposed["semantic_decided"]:
        first_stall = {"source": "EXPOSED", "seed": 36001, "formula_hash": exposed["terminal_formula_hash"], "measure_CLV": exposed["terminal_measure_CLV"]}
    elif unseen_stalls:
        s = unseen_stalls[0]
        first_stall = {"source": "UNSEEN_HOLDOUT", "seed": s["seed"], "formula_hash": s["terminal_formula_hash"], "measure_CLV": s["terminal_measure_CLV"]}

    return {
        "schema": "JANUS_TRUMP_R42_SUBSUMPTION_AWARE_BVE_SUCCESSOR_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict,
        "fixed_controller_id": "TRUMP_R42_FIXED_SUCCESSOR_R33_R34_R35B_SA_BVE_v1",
        "fixed_operator_order": [
            "R33_CERTIFIED_SAFE_REDUCTION_TO_FIXPOINT",
            "SOLVE_ALREADY_DECLARED_HORN_OR_2CNF_TERMINAL_IF_REACHED",
            "R34_AFFINE_COMPLETE_BUNDLE_RECOGNITION_AND_GF2_SOLVE",
            "R35B_SINGLE_LITERAL_RUP_TO_FIXPOINT",
            "SUBSUMPTION_AWARE_BVE_ONE_BEST_EXACT_STEP",
            "RESTART_IF_ANY_CERTIFIED_CHANGE_ELSE_STALL",
        ],
        "structured_controls": controls,
        "exposed_regression": exposed,
        "exposed_repaired": exposed_repaired,
        "unseen_holdouts": holdouts,
        "unseen_holdout_count": len(holdouts),
        "unseen_stall_count": len(unseen_stalls),
        "first_new_stall": first_stall,
        "captain_verdict": {
            "if_stall": "FREEZE_FIRST_NEW_STALL_AND RETURN TO CLASS-LEVEL MECHANISM EXTRACTION; THIS R42 SNAPSHOT MAY NOT BE PATCHED POST HOC.",
            "if_no_stall": "FINITE SUCCESS DOES NOT CLOSE L2; ATTACK SYMBOLIC DECIDE_OR_DESCEND COVERAGE FOR THIS SAME FROZEN SNAPSHOT.",
        },
        "proof_ladder": {
            "highest_verified_level": "L1_LOCAL_FINITE_INSTANCE_EXACTNESS_ONLY",
            "L2_UNIVERSAL_3CNF_COVERAGE": False,
            "L3_ONE_UNIFORM_TOTAL_TRUMP_RESOLVER": False,
            "L4_WORST_CASE_POLYNOMIAL_UNIFORM_TRUMP_RESOLVER": False,
        },
        "complexity_firewall": {
            "SA_BVE_assignment_enumeration_used": False,
            "external_SAT_solver_used": False,
            "new_terminal_language_added": False,
            "all_test_success_may_imply_L2": False,
            "empirical_runtime_may_imply_L4": False,
        },
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    c = structured_controls()
    assert all(v["pass"] for v in c.values()), c
    print("R42_SELF_TEST_PASS", json.dumps({k: v["pass"] for k, v in c.items()}, sort_keys=True))


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
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
