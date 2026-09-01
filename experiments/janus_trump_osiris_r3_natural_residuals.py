#!/usr/bin/env python3
"""R3: natural unenriched TRUMP residual shadow experiment.

This module does not change canonical TRUMP proof authority.  It reuses the
already-frozen TRUMP direct-challenge corpus and solver-native CNF operations.
Residuals are produced by a pre-truth structural probe: at each probe state the
same occurrence pivot used by the frozen DPLL is selected, both truth values
are expanded, deterministic unit propagation is applied, and nonterminal child
states are sealed before any SAT/UNSAT oracle is queried.

The frozen R2 memory rule is tested prospectively:
    density <= 0.70 and >= 4 vars -> TRY_EXACT_MEET
    otherwise                    -> EXACT_FALLBACK

A prediction never has proof authority.  Exact truth is checked independently
by the frozen TRUMP DPLL and SAT witnesses must replay on the residual CNF.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
import json
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from janus_trump_p_vs_np_direct_challenge_r0 import canon, corpus, dpll, restrict_cnf, variables

Clause = Tuple[int, ...]
CNF = Tuple[Clause, ...]
Assignment = Dict[int, bool]

R2_DENSITY_THRESHOLD = 0.70
R2_MIN_VARS_FOR_MEET = 4
R2_MAX_PAIR_PROPOSALS = 12
R3_PROBE_MAX_DEPTH = 2
R3_MAX_RESIDUALS = 48
R3_MIN_RESIDUALS = 24
R3_MIN_SOURCE_FAMILIES = 4


def formula_status(cnf: CNF, assignment: Assignment) -> Optional[bool]:
    all_true = True
    for clause in canon(cnf):
        if not clause:
            return False
        clause_true = False
        unknown = False
        for lit in clause:
            v = abs(lit)
            if v not in assignment:
                unknown = True
                continue
            val = assignment[v]
            if (lit > 0 and val) or (lit < 0 and not val):
                clause_true = True
                break
        if clause_true:
            continue
        if not unknown:
            return False
        all_true = False
    return True if all_true else None


def verify_sat(cnf: CNF, witness: Optional[Assignment]) -> bool:
    if witness is None:
        return False
    full = dict(witness)
    for v in variables(cnf):
        full.setdefault(v, False)
    return formula_status(canon(cnf), full) is True


def formula_digest(cnf: CNF) -> str:
    payload = json.dumps([list(c) for c in canon(cnf)], separators=(",", ":")).encode()
    return sha256(payload).hexdigest()


def unit_close(cnf: CNF) -> CNF:
    """Deterministic unit closure using the same first-unit semantics as DPLL."""
    f = canon(cnf)
    while True:
        if not f or () in f:
            return f
        units = [c[0] for c in f if len(c) == 1]
        if not units:
            return f
        lit = units[0]
        f = restrict_cnf(f, abs(lit), lit > 0)


def occurrence_pivot(cnf: CNF) -> Optional[int]:
    freq = Counter(abs(l) for c in canon(cnf) for l in c)
    if not freq:
        return None
    return max(freq, key=lambda x: (freq[x], -x))


def build_primal_graph(cnf: CNF) -> Tuple[Dict[int, Set[int]], int]:
    graph = {v: set() for v in variables(cnf)}
    ops = len(graph)
    for clause in canon(cnf):
        q = sorted({abs(x) for x in clause})
        for i, u in enumerate(q):
            for v in q[i + 1 :]:
                ops += 1
                graph[u].add(v)
                graph[v].add(u)
    return graph, ops


def graph_signature(cnf: CNF) -> dict:
    f = canon(cnf)
    graph, ops = build_primal_graph(f)
    n = len(graph)
    edges = sum(len(nb) for nb in graph.values()) // 2
    density = 0.0 if n < 2 else (2.0 * edges) / (n * (n - 1))
    clause_hist = Counter(len(c) for c in f)
    degrees = sorted(len(graph[v]) for v in graph)
    density_bucket = round(density, 2)
    structural_key_obj = {
        "variables": n,
        "clauses": len(f),
        "clause_size_histogram": sorted((int(k), int(v)) for k, v in clause_hist.items()),
        "degree_multiset": degrees,
        "density_bucket_0_01": density_bucket,
    }
    structural_key = sha256(json.dumps(structural_key_obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        **structural_key_obj,
        "edges": edges,
        "density": density,
        "structural_key": structural_key,
        "signature_ops": ops,
    }


def frozen_r2_route_prediction(signature: dict) -> str:
    if signature["variables"] >= R2_MIN_VARS_FOR_MEET and signature["density"] <= R2_DENSITY_THRESHOLD:
        return "TRY_EXACT_MEET"
    return "EXACT_FALLBACK"


def seal_pretruth_witness(source: dict, cnf: CNF, signature: dict, prediction: str) -> dict:
    payload = {
        "schema": "JANUS/TRUMP/R3/PRETRUTH-WITNESS/v1.0",
        "source": source,
        "formula_sha256": formula_digest(cnf),
        "signature": signature,
        "frozen_rule_id": "TRUMP_R2_PATTERN_RULE_DENSITY_ROUTE_v1",
        "route_prediction": prediction,
        "truth": None,
        "candidate_result": None,
        "verification_result": None,
    }
    witness_sha = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {**payload, "witness_sha256": witness_sha}


def probe_natural_residuals(max_depth: int = R3_PROBE_MAX_DEPTH, max_residuals: int = R3_MAX_RESIDUALS) -> List[dict]:
    """Produce residuals without querying SAT/UNSAT truth.

    Roots come only from the previously frozen TRUMP R0 corpus.  Selection is
    determined by root order, probe depth, pivot, branch value, and formula
    digest.  No oracle result is available during this phase.
    """
    rows: List[dict] = []
    seen = set()
    for root_index, (family, size, variant, root) in enumerate(corpus()):
        root = unit_close(canon(root))
        frontier = [(root, 0, "ROOT")]
        while frontier and len(rows) < max_residuals:
            f, depth, path = frontier.pop(0)
            if depth >= max_depth or not f or () in f:
                continue
            pivot = occurrence_pivot(f)
            if pivot is None:
                continue
            for value in (False, True):
                child = unit_close(restrict_cnf(f, pivot, value))
                if not child or () in child:
                    continue
                child_digest = formula_digest(child)
                if child_digest == formula_digest(root) or child_digest in seen:
                    continue
                if len(variables(child)) < 3:
                    continue
                seen.add(child_digest)
                source = {
                    "root_index": root_index,
                    "family": family,
                    "size": size,
                    "variant": variant,
                    "probe_depth": depth + 1,
                    "probe_path": f"{path}/{pivot}={'T' if value else 'F'}",
                    "pivot": pivot,
                    "branch_value": value,
                    "root_formula_sha256": formula_digest(root),
                }
                sig = graph_signature(child)
                prediction = frozen_r2_route_prediction(sig)
                witness = seal_pretruth_witness(source, child, sig, prediction)
                rows.append({"source": source, "cnf": child, "pretruth_witness": witness})
                frontier.append((child, depth + 1, source["probe_path"]))
                if len(rows) >= max_residuals:
                    break
        if len(rows) >= max_residuals:
            break
    return rows


def _components_without(graph: Dict[int, Set[int]], separator: Set[int]) -> Tuple[List[Set[int]], int]:
    remaining = set(graph) - separator
    comps: List[Set[int]] = []
    ops = len(remaining)
    while remaining:
        start = min(remaining)
        remaining.remove(start)
        stack = [start]
        comp = {start}
        while stack:
            u = stack.pop()
            for v in graph[u]:
                ops += 1
                if v in separator or v not in remaining:
                    continue
                remaining.remove(v)
                comp.add(v)
                stack.append(v)
        comps.append(comp)
    return comps, ops


def _greedy_split(comps: List[Set[int]]) -> Optional[Tuple[Set[int], Set[int]]]:
    if len(comps) < 2:
        return None
    ordered = sorted(comps, key=lambda c: (-len(c), min(c)))
    left: Set[int] = set()
    right: Set[int] = set()
    for comp in ordered:
        (left if len(left) <= len(right) else right).update(comp)
    return None if not left or not right else (left, right)


def split_by_separator(cnf: CNF, separator: Set[int], left: Set[int], right: Set[int]) -> Tuple[CNF, CNF, CNF]:
    lc: List[Clause] = []
    cc: List[Clause] = []
    rc: List[Clause] = []
    for clause in canon(cnf):
        nonsep = {abs(x) for x in clause if abs(x) not in separator}
        if not nonsep:
            cc.append(clause)
        elif nonsep.issubset(left):
            lc.append(clause)
        elif nonsep.issubset(right):
            rc.append(clause)
        else:
            raise ValueError("not an exact separator")
    return canon(lc), canon(cc), canon(rc)


def exact_search_witness(cnf: CNF, order: Optional[Sequence[int]] = None, initial: Optional[Assignment] = None):
    f0 = canon(cnf)
    base = dict(initial or {})
    universe = list(order) if order is not None else variables(f0)
    order2 = [v for v in universe if v not in base]
    nodes = 0

    def rec(i: int, a: Assignment):
        nonlocal nodes
        nodes += 1
        st = formula_status(f0, a)
        if st is False:
            return None
        if st is True:
            w = dict(a)
            for v in order2[i:]:
                w[v] = False
            return w
        if i >= len(order2):
            return None
        v = order2[i]
        for val in (False, True):
            a[v] = val
            hit = rec(i + 1, a)
            if hit is not None:
                return hit
        a.pop(v, None)
        return None

    w = rec(0, base)
    return ("SAT" if w is not None else "UNSAT"), w, nodes


@dataclass
class CandidateResult:
    terminal: str
    witness: Optional[Assignment]
    mode: str
    separator: Optional[List[int]]
    structural_ops: int
    proposals_tested: int
    boundary_attempts: int
    wing_nodes: int
    fallback_work: int

    @property
    def charged_work(self) -> int:
        return self.structural_ops + self.proposals_tested + self.boundary_attempts + self.wing_nodes + self.fallback_work

    def as_dict(self) -> dict:
        return {
            "terminal": self.terminal,
            "witness": None if self.witness is None else {str(k): bool(v) for k, v in sorted(self.witness.items())},
            "mode": self.mode,
            "separator": self.separator,
            "work": {
                "structural_ops": self.structural_ops,
                "proposals_tested": self.proposals_tested,
                "boundary_attempts": self.boundary_attempts,
                "wing_nodes": self.wing_nodes,
                "fallback_work": self.fallback_work,
                "charged_abstract_ops": self.charged_work,
            },
        }


def r3_candidate(cnf: CNF, pretruth_witness: dict) -> CandidateResult:
    f = canon(cnf)
    sig = pretruth_witness["signature"]
    prediction = pretruth_witness["route_prediction"]
    if prediction == "EXACT_FALLBACK":
        oracle = dpll(f)
        assert oracle["status"] == "EXACT"
        return CandidateResult(
            terminal="SAT" if oracle["sat"] else "UNSAT",
            witness=None,
            mode="R2_RULE_EXACT_FALLBACK",
            separator=None,
            structural_ops=int(sig["signature_ops"]),
            proposals_tested=0,
            boundary_attempts=0,
            wing_nodes=0,
            fallback_work=int(oracle["work"]),
        )

    graph, structural_ops = build_primal_graph(f)
    ranked = []
    for u, v in combinations(sorted(graph), 2):
        score = len(graph[u]) + len(graph[v])
        ranked.append((-score, (u, v)))
    ranked.sort(key=lambda row: (row[0], row[1]))
    proposals = 0
    admitted = None
    for _, pair in ranked[:R2_MAX_PAIR_PROPOSALS]:
        proposals += 1
        sep = set(pair)
        comps, ops = _components_without(graph, sep)
        structural_ops += ops
        split = _greedy_split(comps)
        if split is None:
            continue
        left, right = split
        try:
            split_by_separator(f, sep, left, right)
        except ValueError:
            continue
        admitted = (sep, left, right)
        break

    if admitted is None:
        oracle = dpll(f)
        assert oracle["status"] == "EXACT"
        return CandidateResult(
            terminal="SAT" if oracle["sat"] else "UNSAT",
            witness=None,
            mode="R2_RULE_TRY_NO_SEPARATOR_EXACT_FALLBACK",
            separator=None,
            structural_ops=structural_ops,
            proposals_tested=proposals,
            boundary_attempts=0,
            wing_nodes=0,
            fallback_work=int(oracle["work"]),
        )

    sep, left, right = admitted
    lc, cc, rc = split_by_separator(f, sep, left, right)
    sep_order = sorted(sep)
    left_order = sorted(left)
    right_order = sorted(right, reverse=True)
    attempts = 0
    wing_nodes = 0
    for vals in product((False, True), repeat=len(sep_order)):
        attempts += 1
        boundary = dict(zip(sep_order, vals))
        if formula_status(cc, boundary) is False:
            continue
        lt, lw, ln = exact_search_witness(lc, left_order, boundary)
        wing_nodes += ln
        if lt == "UNSAT":
            continue
        rt, rw, rn = exact_search_witness(rc, right_order, boundary)
        wing_nodes += rn
        if rt == "UNSAT":
            continue
        assert lw is not None and rw is not None
        combined = dict(boundary)
        combined.update({v: x for v, x in lw.items() if v in left})
        combined.update({v: x for v, x in rw.items() if v in right})
        for v in variables(f):
            combined.setdefault(v, False)
        if verify_sat(f, combined):
            return CandidateResult(
                terminal="SAT",
                witness=combined,
                mode="R2_RULE_EXACT_DOUBLE_SPIRAL_MEET",
                separator=sorted(sep),
                structural_ops=structural_ops,
                proposals_tested=proposals,
                boundary_attempts=attempts,
                wing_nodes=wing_nodes,
                fallback_work=0,
            )
    return CandidateResult(
        terminal="UNSAT",
        witness=None,
        mode="R2_RULE_EXACT_DOUBLE_SPIRAL_MEET",
        separator=sorted(sep),
        structural_ops=structural_ops,
        proposals_tested=proposals,
        boundary_attempts=attempts,
        wing_nodes=wing_nodes,
        fallback_work=0,
    )


def evaluate_residual(row: dict) -> dict:
    f = row["cnf"]
    witness = row["pretruth_witness"]
    assert witness["truth"] is None
    assert witness["candidate_result"] is None
    assert witness["verification_result"] is None

    candidate = r3_candidate(f, witness)
    oracle = dpll(f)
    baseline_exact = oracle["status"] == "EXACT"
    baseline_terminal = None if not baseline_exact else ("SAT" if oracle["sat"] else "UNSAT")
    terminal_match = baseline_exact and candidate.terminal == baseline_terminal
    replay = candidate.terminal != "SAT" or verify_sat(f, candidate.witness)
    verified = terminal_match and replay

    experience = {
        "witness_sha256": witness["witness_sha256"],
        "formula_sha256": witness["formula_sha256"],
        "structural_key": witness["signature"]["structural_key"],
        "route_prediction": witness["route_prediction"],
        "candidate_mode": candidate.mode,
        "candidate_terminal": candidate.terminal,
        "baseline_terminal": baseline_terminal,
        "verification_pass": verified,
        "candidate_charged_ops": candidate.charged_work,
        "baseline_dpll_work": int(oracle["work"]),
    }
    experience_sha = sha256(json.dumps(experience, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "source": row["source"],
        "pretruth_witness": witness,
        "candidate": candidate.as_dict(),
        "independent_exact_verifier": oracle,
        "checks": {
            "baseline_exact": baseline_exact,
            "terminal_match": terminal_match,
            "sat_witness_replay": replay,
            "verified_experience_eligible": verified,
        },
        "verified_experience": {**experience, "experience_sha256": experience_sha} if verified else None,
    }


def summarize(rows: List[dict]) -> dict:
    families = sorted({r["source"]["family"] for r in rows})
    pretruth_unique = len({r["pretruth_witness"]["witness_sha256"] for r in rows})
    all_pretruth = all(r["pretruth_witness"]["truth"] is None for r in rows)
    baseline_exact = sum(r["checks"]["baseline_exact"] for r in rows)
    matches = sum(r["checks"]["terminal_match"] for r in rows)
    replay_fail = sum(1 for r in rows if r["candidate"]["terminal"] == "SAT" and not r["checks"]["sat_witness_replay"])
    verified = sum(r["checks"]["verified_experience_eligible"] for r in rows)
    meet_rows = [r for r in rows if r["candidate"]["mode"] == "R2_RULE_EXACT_DOUBLE_SPIRAL_MEET"]
    try_rows = [r for r in rows if r["pretruth_witness"]["route_prediction"] == "TRY_EXACT_MEET"]
    fallback_rows = [r for r in rows if r["pretruth_witness"]["route_prediction"] == "EXACT_FALLBACK"]

    by_sig = defaultdict(list)
    for r in rows:
        by_sig[r["pretruth_witness"]["signature"]["structural_key"]].append(r)
    repeat_groups = []
    for key, members in by_sig.items():
        root_ids = {(m["source"]["root_index"], m["source"]["family"], m["source"]["size"], m["source"]["variant"]) for m in members}
        if len(root_ids) >= 2:
            repeat_groups.append({
                "structural_key": key,
                "members": len(members),
                "distinct_roots": len(root_ids),
                "families": sorted({m["source"]["family"] for m in members}),
                "all_verified": all(m["checks"]["verified_experience_eligible"] for m in members),
            })

    baseline_work = sum(int(r["independent_exact_verifier"]["work"]) for r in rows if r["checks"]["baseline_exact"])
    candidate_work = sum(int(r["candidate"]["work"]["charged_abstract_ops"]) for r in rows)
    try_beneficial = sum(
        1 for r in try_rows
        if r["candidate"]["mode"] == "R2_RULE_EXACT_DOUBLE_SPIRAL_MEET"
        and int(r["candidate"]["work"]["charged_abstract_ops"]) <= int(r["independent_exact_verifier"]["work"])
    )

    acquisition_pass = len(rows) >= R3_MIN_RESIDUALS and len(families) >= R3_MIN_SOURCE_FAMILIES
    epistemic_pass = all_pretruth and pretruth_unique == len(rows) and baseline_exact == len(rows) and matches == len(rows) and replay_fail == 0 and verified == len(rows)
    recurrence_pass = len(repeat_groups) >= 1
    meet_exposure_pass = len(meet_rows) >= 1
    work_pass = candidate_work < baseline_work

    return {
        "residual_acquisition_gate": {
            "pass": acquisition_pass,
            "residuals": len(rows),
            "required_residuals": R3_MIN_RESIDUALS,
            "source_families": families,
            "source_family_count": len(families),
            "required_source_families": R3_MIN_SOURCE_FAMILIES,
            "selection_truth_independent": True,
            "custom_R3_generator_used": False,
        },
        "epistemic_gate": {
            "pass": epistemic_pass,
            "unique_pretruth_witnesses": pretruth_unique,
            "all_witnesses_truth_null_before_execution": all_pretruth,
            "independent_exact_verifier_passes": baseline_exact,
            "terminal_matches": matches,
            "sat_replay_failures": replay_fail,
            "verified_experiences": verified,
        },
        "natural_recurrence_gate": {
            "pass": recurrence_pass,
            "repeat_group_count": len(repeat_groups),
            "repeat_groups": repeat_groups,
            "definition": "same frozen pre-truth structural key appears in at least two distinct frozen TRUMP roots",
        },
        "double_spiral_exposure_gate": {
            "pass": meet_exposure_pass,
            "predicted_try_cases": len(try_rows),
            "predicted_fallback_cases": len(fallback_rows),
            "exact_meet_cases": len(meet_rows),
            "try_cases_not_worse_than_baseline": try_beneficial,
        },
        "secondary_work_gate": {
            "pass": work_pass,
            "metric": "charged_abstract_ops_vs_frozen_TRUMP_DPLL_work",
            "baseline_total": baseline_work,
            "candidate_total": candidate_work,
            "saved": baseline_work - candidate_work,
            "saved_fraction": 0.0 if baseline_work == 0 else (baseline_work - candidate_work) / baseline_work,
            "claim_ceiling": "natural residual shadow metric only; not wall-clock or general solver speedup",
        },
    }
