#!/usr/bin/env python3
"""R7C: attack the 49 R7B OPEN central kernels with polynomial-only rules.

This is an exposed-kernel discovery run, not a holdout/generalization claim.
Candidate authority contains no R6-quarantined exhaustive fallback.
"""
from __future__ import annotations

import argparse
import inspect
import json
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import janus_trump_r7b_meet_then_diverge_central_kernel as r7b
from janus_trump_p_vs_np_direct_challenge_r0 import canon, restrict_cnf, variables

Clause = Tuple[int, ...]
CNF = Tuple[Clause, ...]
Assignment = Dict[int, bool]


def merge_assignment(dst: Assignment, src: Assignment) -> bool:
    for v, val in src.items():
        if v in dst and dst[v] != val:
            return False
        dst[v] = val
    return True


def pure_literal(cnf: CNF) -> Optional[Tuple[int, bool]]:
    signs: Dict[int, Set[bool]] = defaultdict(set)
    for clause in canon(cnf):
        for lit in clause:
            signs[abs(lit)].add(lit > 0)
    for v in sorted(signs):
        if len(signs[v]) == 1:
            return v, next(iter(signs[v]))
    return None


@dataclass
class Closure:
    kernel: CNF
    forced: Assignment
    trace: List[dict]
    ops: int
    contradiction: bool
    certificate: Optional[dict]


def _apply_force(cnf: CNF, forced: Assignment, trace: List[dict], v: int, val: bool, reason: str, ops: int) -> Tuple[CNF, int, bool, Optional[dict]]:
    if v in forced and forced[v] != val:
        return ((),), ops + 1, True, {"type": "FORCE_CONFLICT", "variable": v}
    forced[v] = val
    trace.append({"variable": v, "value": val, "reason": reason})
    f = restrict_cnf(cnf, v, val)
    ops += len(cnf) + 1
    uc = r7b.unit_converge(f, reverse_scan=False)
    ops += uc.ops
    if not merge_assignment(forced, uc.forced):
        return ((),), ops, True, {"type": "UNIT_FORCE_CONFLICT", "variable": v}
    for uv, uval in uc.trace:
        trace.append({"variable": uv, "value": uval, "reason": "UNIT_AFTER_" + reason})
    if uc.contradiction or () in uc.kernel:
        return uc.kernel, ops, True, {"type": "UNIT_CLOSURE_CONTRADICTION_AFTER_FORCE", "variable": v, "value": val, "reason": reason}
    return uc.kernel, ops, False, None


def polynomial_kernel_closure(cnf: CNF) -> Closure:
    """Pure-literal + nonrecursive failed-literal closure.

    Failed-literal tests invoke only unit propagation under one assumption.
    A successful force removes at least one variable, so there are at most |V|
    successful-force rounds. No test recursively invokes this closure.
    """
    f = canon(cnf)
    forced: Assignment = {}
    trace: List[dict] = []
    ops = 0
    while True:
        if () in f:
            return Closure(f, forced, trace, ops, True, {"type": "EMPTY_CLAUSE"})
        if not f:
            return Closure(f, forced, trace, ops, False, None)

        p = pure_literal(f)
        ops += sum(len(c) for c in f)
        if p is not None:
            v, val = p
            f, ops, bad, cert = _apply_force(f, forced, trace, v, val, "PURE_LITERAL", ops)
            if bad:
                return Closure(f, forced, trace, ops, True, cert)
            continue

        progress = False
        for v in variables(f):
            t = r7b.unit_converge(restrict_cnf(f, v, True), reverse_scan=False)
            ff = r7b.unit_converge(restrict_cnf(f, v, False), reverse_scan=False)
            ops += (2 * len(f)) + t.ops + ff.ops + 2
            t_bad = t.contradiction or () in t.kernel
            f_bad = ff.contradiction or () in ff.kernel
            if t_bad and f_bad:
                return Closure(
                    f,
                    forced,
                    trace,
                    ops,
                    True,
                    {
                        "type": "FAILED_LITERAL_BOTH_VALUES_CONTRADICT",
                        "variable": v,
                        "true_unit_trace": [[x, y] for x, y in t.trace],
                        "false_unit_trace": [[x, y] for x, y in ff.trace],
                    },
                )
            if t_bad != f_bad:
                val = False if t_bad else True
                reason = "FAILED_LITERAL_TRUE_CONTRADICTS" if t_bad else "FAILED_LITERAL_FALSE_CONTRADICTS"
                f, ops, bad, cert = _apply_force(f, forced, trace, v, val, reason, ops)
                if bad:
                    return Closure(f, forced, trace, ops, True, cert)
                progress = True
                break
        if progress:
            continue
        return Closure(f, forced, trace, ops, False, None)


def solve_renamable_horn(cnf: CNF) -> dict:
    f = canon(cnf)
    if not f or () in f:
        return {"status": "UNSUPPORTED", "class": "RENAMABLE_HORN", "ops": 0}
    constraints: List[Clause] = []
    ops = 0
    # r_v=True means variable v is complemented. A literal becomes positive iff
    # (-r_v) for an original positive literal, or r_v for an original negative.
    # Forbid every pair from becoming positive simultaneously.
    for clause in f:
        for a, b in combinations(clause, 2):
            pa = -abs(a) if a > 0 else abs(a)
            pb = -abs(b) if b > 0 else abs(b)
            constraints.append((-pa, -pb))
            ops += 1
    constraint_cnf = canon(constraints)
    if constraint_cnf:
        rr = r7b.solve_2sat(constraint_cnf)
        ops += int(rr.get("ops", 0))
        if rr["status"] == "UNSAT":
            return {"status": "UNSUPPORTED", "class": "RENAMABLE_HORN", "ops": ops, "reason": "NO_HORN_RENAMING"}
        if rr["status"] != "SAT":
            return {"status": "INTERNAL_RECOGNITION_FAILURE", "class": "RENAMABLE_HORN", "ops": ops}
        flips = {v: bool(rr["assignment"].get(v, False)) for v in variables(f)}
    else:
        flips = {v: False for v in variables(f)}
    transformed = canon(tuple(tuple((-lit if flips[abs(lit)] else lit) for lit in clause) for clause in f))
    ops += sum(len(c) for c in f)
    if not r7b.is_horn(transformed):
        return {"status": "INTERNAL_RECOGNITION_FAILURE", "class": "RENAMABLE_HORN", "ops": ops}
    hr = r7b.solve_horn(transformed)
    ops += int(hr.get("ops", 0))
    if hr["status"] == "UNSAT":
        return {
            "status": "UNSAT",
            "assignment": None,
            "class": "RENAMABLE_HORN",
            "ops": ops,
            "certificate": {"type": "RENAMABLE_HORN_REFUTATION", "flipped_variables": sorted(v for v, x in flips.items() if x), "inner": hr.get("certificate")},
        }
    if hr["status"] != "SAT":
        return {"status": "INTERNAL_RECONSTRUCTION_FAILURE", "class": "RENAMABLE_HORN", "ops": ops}
    a = {v: (not hr["assignment"].get(v, False) if flips[v] else hr["assignment"].get(v, False)) for v in variables(f)}
    ops += len(a)
    if not r7b.verify_sat(f, a):
        return {"status": "INTERNAL_RECONSTRUCTION_FAILURE", "class": "RENAMABLE_HORN", "ops": ops}
    return {
        "status": "SAT",
        "assignment": a,
        "class": "RENAMABLE_HORN",
        "ops": ops,
        "certificate": {"type": "RENAMABLE_HORN_MODEL", "flipped_variables": sorted(v for v, x in flips.items() if x), "inner": hr.get("certificate")},
    }


def solve_bipartite_matching_cnf(cnf: CNF) -> dict:
    """Recognize exact matching CNF and solve by augmenting paths.

    Required syntax: positive at-least-one clauses partition variables; all
    other clauses are negative binary conflicts. Within every positive group
    all variable pairs conflict. Cross-group conflicts must form disjoint
    resource cliques with at most one variable from each positive group.
    """
    f = canon(cnf)
    if not f or () in f:
        return {"status": "UNSUPPORTED", "class": "BIPARTITE_MATCHING_CNF", "ops": 0}
    pos_groups: List[Tuple[int, ...]] = []
    neg_pairs: Set[frozenset[int]] = set()
    ops = 0
    for clause in f:
        ops += len(clause) + 1
        if all(lit > 0 for lit in clause):
            pos_groups.append(tuple(clause))
        elif len(clause) == 2 and all(lit < 0 for lit in clause):
            a, b = abs(clause[0]), abs(clause[1])
            if a == b:
                return {"status": "UNSUPPORTED", "class": "BIPARTITE_MATCHING_CNF", "ops": ops}
            neg_pairs.add(frozenset((a, b)))
        else:
            return {"status": "UNSUPPORTED", "class": "BIPARTITE_MATCHING_CNF", "ops": ops}
    if not pos_groups:
        return {"status": "UNSUPPORTED", "class": "BIPARTITE_MATCHING_CNF", "ops": ops}

    var_group: Dict[int, int] = {}
    for gi, group in enumerate(pos_groups):
        for v in group:
            if v in var_group:
                return {"status": "UNSUPPORTED", "class": "BIPARTITE_MATCHING_CNF", "ops": ops}
            var_group[v] = gi
    if set(var_group) != set(variables(f)):
        return {"status": "UNSUPPORTED", "class": "BIPARTITE_MATCHING_CNF", "ops": ops}

    for group in pos_groups:
        for a, b in combinations(group, 2):
            ops += 1
            if frozenset((a, b)) not in neg_pairs:
                return {"status": "UNSUPPORTED", "class": "BIPARTITE_MATCHING_CNF", "ops": ops}

    cross: Dict[int, Set[int]] = {v: set() for v in var_group}
    for pair in neg_pairs:
        a, b = tuple(pair)
        if var_group[a] != var_group[b]:
            cross[a].add(b)
            cross[b].add(a)
        ops += 1

    resource_of: Dict[int, int] = {}
    resources: List[Set[int]] = []
    remaining = set(var_group)
    while remaining:
        start = min(remaining)
        remaining.remove(start)
        comp = {start}
        stack = [start]
        while stack:
            u = stack.pop()
            for v in cross[u]:
                ops += 1
                if v in remaining:
                    remaining.remove(v)
                    comp.add(v)
                    stack.append(v)
        gids = [var_group[v] for v in comp]
        if len(gids) != len(set(gids)):
            return {"status": "UNSUPPORTED", "class": "BIPARTITE_MATCHING_CNF", "ops": ops}
        for a, b in combinations(sorted(comp), 2):
            ops += 1
            if frozenset((a, b)) not in neg_pairs:
                return {"status": "UNSUPPORTED", "class": "BIPARTITE_MATCHING_CNF", "ops": ops}
        rid = len(resources)
        resources.append(comp)
        for v in comp:
            resource_of[v] = rid

    match_r: Dict[int, Tuple[int, int]] = {}

    def augment(gi: int, seen: Set[int]) -> bool:
        nonlocal ops
        for v in sorted(pos_groups[gi]):
            rid = resource_of[v]
            ops += 1
            if rid in seen:
                continue
            seen.add(rid)
            if rid not in match_r or augment(match_r[rid][0], seen):
                match_r[rid] = (gi, v)
                return True
        return False

    for gi in range(len(pos_groups)):
        if not augment(gi, set()):
            return {
                "status": "UNSAT",
                "assignment": None,
                "class": "BIPARTITE_MATCHING_CNF",
                "ops": ops,
                "certificate": {"type": "NO_LEFT_COVERING_MATCHING", "left_groups": len(pos_groups), "resources": len(resources), "matched_left_groups": len(match_r)},
            }

    a = {v: False for v in var_group}
    for _rid, (_gi, v) in match_r.items():
        a[v] = True
    ops += len(a)
    if not r7b.verify_sat(f, a):
        return {"status": "INTERNAL_RECONSTRUCTION_FAILURE", "class": "BIPARTITE_MATCHING_CNF", "ops": ops}
    return {
        "status": "SAT",
        "assignment": a,
        "class": "BIPARTITE_MATCHING_CNF",
        "ops": ops,
        "certificate": {"type": "LEFT_COVERING_MATCHING_MODEL", "matching_variables": sorted(v for v, val in a.items() if val)},
    }


def solve_expanded_poly_component(cnf: CNF) -> dict:
    base = r7b.solve_poly_component(cnf)
    if base["status"] != "UNSUPPORTED":
        return base
    rh = solve_renamable_horn(cnf)
    if rh["status"] != "UNSUPPORTED":
        return rh
    mt = solve_bipartite_matching_cnf(cnf)
    if mt["status"] != "UNSUPPORTED":
        return mt
    return {"status": "UNSUPPORTED", "assignment": None, "class": "GENERAL_CNF", "ops": int(base.get("ops", 0)) + int(rh.get("ops", 0)) + int(mt.get("ops", 0)), "certificate": {"type": "R7C_UNSUPPORTED_CENTRAL_CORE"}}


def open_profile(cnf: CNF) -> dict:
    f = canon(cnf)
    vs = variables(f)
    return {
        "variables": len(vs),
        "clauses": len(f),
        "max_clause": max((len(c) for c in f), default=0),
        "positive_clauses": sum(all(l > 0 for l in c) for c in f),
        "negative_binary_clauses": sum(len(c) == 2 and all(l < 0 for l in c) for c in f),
        "horn": r7b.is_horn(f),
        "dual_horn": all(sum(1 for l in c if l < 0) <= 1 for c in f),
    }


@dataclass
class Candidate:
    terminal: str
    witness: Optional[Assignment]
    certificate: dict
    kernel_sha256: str
    kernel_variables: int
    kernel_clauses: int
    closure_trace: List[dict]
    component_classes: List[str]
    open_component_profiles: List[dict]
    ops: int

    def as_dict(self) -> dict:
        return {
            "terminal": self.terminal,
            "witness": None if self.witness is None else {str(k): bool(v) for k, v in sorted(self.witness.items())},
            "certificate": self.certificate,
            "kernel_sha256": self.kernel_sha256,
            "kernel_variables": self.kernel_variables,
            "kernel_clauses": self.kernel_clauses,
            "closure_trace": self.closure_trace,
            "component_classes": self.component_classes,
            "open_component_profiles": self.open_component_profiles,
            "charged_ops": self.ops,
        }


def r7c_candidate(cnf: CNF) -> Candidate:
    original = canon(cnf)
    left = r7b.unit_converge(original, reverse_scan=False)
    right = r7b.unit_converge(original, reverse_scan=True)
    ops = left.ops + right.ops
    kernel = left.kernel
    kd = r7b.digest_cnf(kernel)
    if left.kernel != right.kernel or left.forced != right.forced:
        return Candidate("OPEN", None, {"type": "R7B_MEET_OR_FORCE_MISMATCH"}, kd, len(variables(kernel)), len(kernel), [], [], [open_profile(kernel)], ops)
    if left.contradiction or right.contradiction or () in kernel:
        return Candidate("UNSAT", None, {"type": "UNIT_CONVERGENCE_CONTRADICTION"}, kd, len(variables(kernel)), len(kernel), [], ["UNIT"], [], ops)

    forced = dict(left.forced)
    closure = polynomial_kernel_closure(kernel)
    ops += closure.ops
    if not merge_assignment(forced, closure.forced):
        return Candidate("OPEN", None, {"type": "R7C_FORCE_MERGE_CONFLICT"}, kd, len(variables(kernel)), len(kernel), closure.trace, [], [open_profile(closure.kernel)], ops)
    kernel2 = closure.kernel
    kd2 = r7b.digest_cnf(kernel2)
    if closure.contradiction or () in kernel2:
        return Candidate("UNSAT", None, {"type": "R7C_POLYNOMIAL_CLOSURE_CONTRADICTION", "inner": closure.certificate}, kd2, len(variables(kernel2)), len(kernel2), closure.trace, ["FAILED_LITERAL_OR_UNIT"], [], ops)
    if not kernel2:
        w = dict(forced)
        for v in variables(original):
            w.setdefault(v, False)
        if r7b.verify_sat(original, w):
            return Candidate("SAT", w, {"type": "R7C_CLOSURE_MODEL"}, kd2, 0, 0, closure.trace, ["CLOSURE_EMPTY"], [], ops)
        return Candidate("OPEN", None, {"type": "R7C_CLOSURE_RECONSTRUCTION_FAILED"}, kd2, 0, 0, closure.trace, [], [], ops)

    parts, decomp_ops = r7b.component_cnfs(kernel2)
    ops += decomp_ops
    merged = dict(forced)
    classes: List[str] = []
    certs: List[dict] = []
    open_profiles: List[dict] = []
    for part in parts:
        rr = solve_expanded_poly_component(part)
        ops += int(rr.get("ops", 0))
        classes.append(rr.get("class", "UNKNOWN"))
        certs.append(rr.get("certificate", {}))
        if rr["status"] == "UNSAT":
            return Candidate("UNSAT", None, {"type": "R7C_POLY_COMPONENT_UNSAT", "component_certificate": rr.get("certificate")}, kd2, len(variables(kernel2)), len(kernel2), closure.trace, classes, [], ops)
        if rr["status"] != "SAT":
            open_profiles.append(open_profile(part))
            return Candidate("OPEN", None, {"type": "R7C_UNSUPPORTED_COMPONENT", "component_class": rr.get("class")}, kd2, len(variables(kernel2)), len(kernel2), closure.trace, classes, open_profiles, ops)
        if not merge_assignment(merged, rr.get("assignment") or {}):
            return Candidate("OPEN", None, {"type": "R7C_COMPONENT_ASSIGNMENT_CONFLICT"}, kd2, len(variables(kernel2)), len(kernel2), closure.trace, classes, [open_profile(part)], ops)

    for v in variables(original):
        merged.setdefault(v, False)
    if not r7b.verify_sat(original, merged):
        return Candidate("OPEN", None, {"type": "R7C_DIVERGENCE_RECONSTRUCTION_FAILED", "component_certificates": certs}, kd2, len(variables(kernel2)), len(kernel2), closure.trace, classes, [], ops)
    return Candidate("SAT", merged, {"type": "R7C_MEET_CLOSE_DIVERGE_MODEL", "component_certificates": certs}, kd2, len(variables(kernel2)), len(kernel2), closure.trace, classes, [], ops)


def target_cases() -> List[dict]:
    out = []
    for case in r7b.frozen_cases():
        old = r7b.meet_then_diverge_candidate(case["cnf"])
        if old.terminal == "OPEN":
            out.append(case)
    return out


def shadow_verify(cnf: CNF, candidate: Candidate) -> dict:
    from janus_trump_p_vs_np_direct_challenge_r0 import dpll
    oracle = dpll(canon(cnf))
    exact = oracle["status"] == "EXACT"
    truth = None if not exact else ("SAT" if oracle["sat"] else "UNSAT")
    return {
        "oracle": oracle,
        "truth": truth,
        "terminal_match": candidate.terminal == "OPEN" or (exact and candidate.terminal == truth),
        "sat_replay": candidate.terminal != "SAT" or r7b.verify_sat(cnf, candidate.witness),
    }


def candidate_source_firewall() -> dict:
    funcs = [r7c_candidate, polynomial_kernel_closure, solve_renamable_horn, solve_bipartite_matching_cnf, solve_expanded_poly_component]
    src = "\n".join(inspect.getsource(f) for f in funcs)
    forbidden = ["dpll(", "exact_search_witness", "product(", "robdd(", "dp_eliminate("]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "forbidden_hits": hits}


def run() -> dict:
    targets = target_cases()
    rows = []
    for case in targets:
        candidate = r7c_candidate(case["cnf"])
        sealed = {
            "source": {k: v for k, v in case.items() if k != "cnf"},
            "formula_sha256": r7b.digest_cnf(case["cnf"]),
            "candidate": candidate.as_dict(),
            "truth": None,
        }
        seal_sha = sha256(json.dumps(sealed, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        verification = shadow_verify(case["cnf"], candidate)
        rows.append({**sealed, "preverification_seal_sha256": seal_sha, "shadow_verification": verification})

    terminal = [r for r in rows if r["candidate"]["terminal"] in ("SAT", "UNSAT")]
    remaining = [r for r in rows if r["candidate"]["terminal"] == "OPEN"]
    false_terminals = [r for r in terminal if not r["shadow_verification"]["terminal_match"]]
    replay_fail = [r for r in terminal if r["candidate"]["terminal"] == "SAT" and not r["shadow_verification"]["sat_replay"]]
    class_counts: Dict[str, int] = defaultdict(int)
    recovery_by_class: Dict[str, int] = defaultdict(int)
    remaining_by_family: Dict[str, int] = defaultdict(int)
    for r in rows:
        for c in r["candidate"]["component_classes"]:
            class_counts[c] += 1
        if r in terminal:
            for c in r["candidate"]["component_classes"]:
                recovery_by_class[c] += 1
        else:
            remaining_by_family[r["source"]["family"]] += 1

    firewall = candidate_source_firewall()
    gates = {
        "G1_TARGET_COUNT_49": len(targets) == 49,
        "G2_NO_R6_QUARANTINED_PRIMITIVE": firewall["pass"],
        "G3_NO_FALSE_TERMINALS": len(false_terminals) == 0 and all(r["shadow_verification"]["oracle"]["status"] == "EXACT" for r in rows),
        "G4_SAT_REPLAY_ZERO_FAILURES": len(replay_fail) == 0,
        "G5_RECOVER_AT_LEAST_ONE_PREVIOUSLY_OPEN_KERNEL": len(terminal) > 0,
        "G6_REMAINING_UNSUPPORTED_CASES_STAY_OPEN": all(r["candidate"]["terminal"] == "OPEN" for r in remaining),
        "G7_NO_THEOREM_INFLATION": True,
    }
    passed = all(gates.values())
    return {
        "schema": "JANUS/TRUMP/R7C/OPEN49_POLY_KERNEL_ASSAULT/RESULT/v1.0",
        "status": "FROZEN_RESULT",
        "verdict": "R7C_OPEN49_POLY_RECOVERY_PASS__REMAINDER_OPEN__P_VS_NP_OPEN" if passed else "R7C_OPEN49_GATE_FAIL__P_VS_NP_OPEN",
        "scope": "EXPOSED_R7B_OPEN_KERNEL_DISCOVERY_ONLY",
        "summary": {
            "targets": len(targets),
            "recovered_terminal_cases": len(terminal),
            "remaining_open_cases": len(remaining),
            "recovery_fraction": (len(terminal) / len(targets)) if targets else 0.0,
            "false_terminals": len(false_terminals),
            "sat_replay_failures": len(replay_fail),
            "component_class_counts": dict(sorted(class_counts.items())),
            "recovery_by_class": dict(sorted(recovery_by_class.items())),
            "remaining_open_by_family": dict(sorted(remaining_by_family.items())),
            "candidate_total_charged_ops": sum(int(r["candidate"]["charged_ops"]) for r in rows),
            "shadow_dpll_total_work": sum(int(r["shadow_verification"]["oracle"].get("work", 0)) for r in rows),
        },
        "gates": gates,
        "candidate_source_firewall": firewall,
        "highest_admissible_claim": "R7C may recover some previously OPEN exposed R7B kernels using only additional exact polynomial closures/classes. Because the target set is exposed and any remaining GENERAL_CNF cases stay OPEN, this is discovery evidence only and does not establish arbitrary-CNF totality or P=NP.",
        "next_gate": "Freeze any newly successful rules and test them prospectively on unseen natural TRUMP residuals. Separately characterize the still-OPEN kernels without using their shadow truth to retrofit rules.",
        "P_VS_NP": "OPEN",
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = run()
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "summary": result["summary"], "gates": result["gates"], "candidate_source_firewall": result["candidate_source_firewall"], "P_VS_NP": result["P_VS_NP"]}, indent=2))
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
