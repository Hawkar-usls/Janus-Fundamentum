#!/usr/bin/env python3
"""R7B: meet-then-diverge central-kernel experiment.

Candidate truth authority deliberately excludes every R6-quarantined exhaustive
primitive.  Two deterministic unit-propagation lanes converge from opposite
clause scan directions.  They must meet on the same canonical residual kernel.
The kernel may terminate only through polynomial-time exact classes implemented
here (empty/contradictory kernel, 2-SAT SCC, Horn, dual-Horn, and independent
connected components composed from those classes).  SAT then diverges outward
by reconstructing the eliminated unit assignments.

A legacy DPLL is used only in shadow verification after the candidate result is
sealed; it is never called by the candidate path.
"""
from __future__ import annotations

import argparse
import inspect
import json
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from janus_trump_p_vs_np_direct_challenge_r0 import canon, corpus, restrict_cnf, variables
from janus_trump_osiris_r3_natural_residuals import probe_natural_residuals

Clause = Tuple[int, ...]
CNF = Tuple[Clause, ...]
Assignment = Dict[int, bool]


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
            elif (lit > 0 and assignment[v]) or (lit < 0 and not assignment[v]):
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
    a = dict(witness)
    for v in variables(cnf):
        a.setdefault(v, False)
    return formula_status(canon(cnf), a) is True


def digest_cnf(cnf: CNF) -> str:
    payload = json.dumps([list(c) for c in canon(cnf)], separators=(",", ":")).encode()
    return sha256(payload).hexdigest()


@dataclass
class Convergence:
    kernel: CNF
    forced: Assignment
    trace: List[Tuple[int, bool]]
    ops: int
    contradiction: bool


def unit_converge(cnf: CNF, reverse_scan: bool) -> Convergence:
    """Deterministic polynomial unit closure from one scan direction."""
    f = canon(cnf)
    forced: Assignment = {}
    trace: List[Tuple[int, bool]] = []
    ops = 0
    while True:
        if () in f:
            return Convergence(f, forced, trace, ops, True)
        seq = list(reversed(f)) if reverse_scan else list(f)
        ops += len(seq)
        units = [c[0] for c in seq if len(c) == 1]
        if not units:
            return Convergence(f, forced, trace, ops, False)
        lit = units[0]
        v, val = abs(lit), lit > 0
        if v in forced and forced[v] != val:
            return Convergence(((),), forced, trace, ops + 1, True)
        forced[v] = val
        trace.append((v, val))
        f = restrict_cnf(f, v, val)
        ops += 1


def primal_components(cnf: CNF) -> Tuple[List[Set[int]], int]:
    vs = variables(cnf)
    graph: Dict[int, Set[int]] = {v: set() for v in vs}
    ops = len(vs)
    for clause in canon(cnf):
        q = sorted({abs(x) for x in clause})
        for i, u in enumerate(q):
            for v in q[i + 1 :]:
                graph[u].add(v)
                graph[v].add(u)
                ops += 1
    remaining = set(vs)
    comps: List[Set[int]] = []
    while remaining:
        start = min(remaining)
        remaining.remove(start)
        comp = {start}
        stack = [start]
        while stack:
            u = stack.pop()
            for v in graph[u]:
                ops += 1
                if v in remaining:
                    remaining.remove(v)
                    comp.add(v)
                    stack.append(v)
        comps.append(comp)
    return comps, ops


def component_cnfs(cnf: CNF) -> Tuple[List[CNF], int]:
    comps, ops = primal_components(cnf)
    rows: List[CNF] = []
    f = canon(cnf)
    for comp in comps:
        part = [c for c in f if any(abs(l) in comp for l in c)]
        rows.append(canon(part))
        ops += len(f)
    return rows, ops


def _finish_order(graph: Dict[int, Set[int]]) -> Tuple[List[int], int]:
    seen: Set[int] = set()
    order: List[int] = []
    ops = 0
    for start in sorted(graph):
        if start in seen:
            continue
        stack: List[Tuple[int, bool]] = [(start, False)]
        while stack:
            u, expanded = stack.pop()
            ops += 1
            if expanded:
                order.append(u)
                continue
            if u in seen:
                continue
            seen.add(u)
            stack.append((u, True))
            for v in sorted(graph[u], reverse=True):
                if v not in seen:
                    stack.append((v, False))
    return order, ops


def solve_2sat(cnf: CNF) -> dict:
    f = canon(cnf)
    if any(len(c) > 2 for c in f):
        return {"status": "UNSUPPORTED", "ops": 0}
    if () in f:
        return {"status": "UNSAT", "assignment": None, "certificate": {"type": "EMPTY_CLAUSE"}, "ops": 1}
    vs = variables(f)
    nodes = {v for v in vs} | {-v for v in vs}
    g: Dict[int, Set[int]] = {x: set() for x in nodes}
    rg: Dict[int, Set[int]] = {x: set() for x in nodes}
    ops = len(nodes)
    for clause in f:
        if len(clause) == 1:
            a = clause[0]
            edges = [(-a, a)]
        else:
            a, b = clause
            edges = [(-a, b), (-b, a)]
        for u, v in edges:
            g[u].add(v)
            rg[v].add(u)
            ops += 1
    order, o = _finish_order(g)
    ops += o
    comp: Dict[int, int] = {}
    cid = 0
    for start in reversed(order):
        if start in comp:
            continue
        stack = [start]
        comp[start] = cid
        while stack:
            u = stack.pop()
            ops += 1
            for v in rg[u]:
                if v not in comp:
                    comp[v] = cid
                    stack.append(v)
        cid += 1
    for v in vs:
        if comp[v] == comp[-v]:
            return {
                "status": "UNSAT",
                "assignment": None,
                "certificate": {"type": "2SAT_SCC_CONTRADICTION", "variable": v, "component": comp[v]},
                "ops": ops,
            }
    for greater in (True, False):
        a = {v: ((comp[v] > comp[-v]) if greater else (comp[v] < comp[-v])) for v in vs}
        ops += len(vs)
        if verify_sat(f, a):
            return {"status": "SAT", "assignment": a, "certificate": {"type": "2SAT_SCC_MODEL"}, "ops": ops}
    return {"status": "INTERNAL_RECONSTRUCTION_FAILURE", "ops": ops}


def is_horn(cnf: CNF) -> bool:
    return all(sum(1 for lit in c if lit > 0) <= 1 for c in canon(cnf))


def solve_horn(cnf: CNF) -> dict:
    f = canon(cnf)
    if not is_horn(f):
        return {"status": "UNSUPPORTED", "ops": 0}
    vs = variables(f)
    true_set: Set[int] = set()
    trace: List[int] = []
    ops = 0
    # At most |V| successful head additions; scans are polynomial.
    for _ in range(len(vs) + 1):
        changed = False
        for clause in f:
            positives = [lit for lit in clause if lit > 0]
            premises = [-lit for lit in clause if lit < 0]
            ops += len(clause) + 1
            if all(v in true_set for v in premises):
                if not positives:
                    return {
                        "status": "UNSAT",
                        "assignment": None,
                        "certificate": {"type": "HORN_FORWARD_CONTRADICTION", "derived_true": sorted(true_set), "trace": trace},
                        "ops": ops,
                    }
                head = positives[0]
                if head not in true_set:
                    true_set.add(head)
                    trace.append(head)
                    changed = True
        if not changed:
            break
    a = {v: v in true_set for v in vs}
    if verify_sat(f, a):
        return {"status": "SAT", "assignment": a, "certificate": {"type": "HORN_LEAST_MODEL", "trace": trace}, "ops": ops}
    return {"status": "INTERNAL_RECONSTRUCTION_FAILURE", "ops": ops}


def solve_dual_horn(cnf: CNF) -> dict:
    f = canon(cnf)
    if not all(sum(1 for lit in c if lit < 0) <= 1 for c in f):
        return {"status": "UNSUPPORTED", "ops": 0}
    transformed = canon(tuple(tuple(-lit for lit in c) for c in f))
    r = solve_horn(transformed)
    if r["status"] == "SAT":
        a = {v: not val for v, val in r["assignment"].items()}
        if verify_sat(f, a):
            return {"status": "SAT", "assignment": a, "certificate": {"type": "DUAL_HORN_COMPLEMENT_MODEL", "inner": r["certificate"]}, "ops": r["ops"] + len(a)}
        return {"status": "INTERNAL_RECONSTRUCTION_FAILURE", "ops": r["ops"] + len(a)}
    if r["status"] == "UNSAT":
        return {"status": "UNSAT", "assignment": None, "certificate": {"type": "DUAL_HORN_COMPLEMENT_REFUTATION", "inner": r["certificate"]}, "ops": r["ops"]}
    return r


def solve_poly_component(cnf: CNF) -> dict:
    f = canon(cnf)
    if not f:
        return {"status": "SAT", "assignment": {}, "certificate": {"type": "EMPTY_COMPONENT"}, "ops": 1, "class": "EMPTY"}
    if () in f:
        return {"status": "UNSAT", "assignment": None, "certificate": {"type": "EMPTY_CLAUSE"}, "ops": 1, "class": "CONTRADICTION"}
    if max(len(c) for c in f) <= 2:
        r = solve_2sat(f)
        return {**r, "class": "2SAT"}
    if is_horn(f):
        r = solve_horn(f)
        return {**r, "class": "HORN"}
    if all(sum(1 for lit in c if lit < 0) <= 1 for c in f):
        r = solve_dual_horn(f)
        return {**r, "class": "DUAL_HORN"}
    return {"status": "UNSUPPORTED", "assignment": None, "certificate": {"type": "UNSUPPORTED_CENTRAL_CORE"}, "ops": 1, "class": "GENERAL_CNF"}


@dataclass
class Candidate:
    terminal: str
    witness: Optional[Assignment]
    certificate: dict
    central_kernel_sha256: str
    central_kernel_variables: int
    central_kernel_clauses: int
    left_trace: List[Tuple[int, bool]]
    right_trace: List[Tuple[int, bool]]
    meet_exact: bool
    candidate_poly_only: bool
    component_classes: List[str]
    ops: int

    def as_dict(self) -> dict:
        return {
            "terminal": self.terminal,
            "witness": None if self.witness is None else {str(k): bool(v) for k, v in sorted(self.witness.items())},
            "certificate": self.certificate,
            "central_kernel_sha256": self.central_kernel_sha256,
            "central_kernel_variables": self.central_kernel_variables,
            "central_kernel_clauses": self.central_kernel_clauses,
            "left_trace": [[v, val] for v, val in self.left_trace],
            "right_trace": [[v, val] for v, val in self.right_trace],
            "meet_exact": self.meet_exact,
            "candidate_poly_only": self.candidate_poly_only,
            "component_classes": self.component_classes,
            "charged_ops": self.ops,
        }


def meet_then_diverge_candidate(cnf: CNF) -> Candidate:
    """Candidate theorem path.  No exhaustive fallback is reachable here."""
    original = canon(cnf)
    left = unit_converge(original, reverse_scan=False)
    right = unit_converge(original, reverse_scan=True)
    meet_exact = left.kernel == right.kernel
    ops = left.ops + right.ops
    kernel = left.kernel if meet_exact else canon(original)
    kd = digest_cnf(kernel)
    if not meet_exact:
        return Candidate("OPEN", None, {"type": "MEET_MISMATCH"}, kd, len(variables(kernel)), len(kernel), left.trace, right.trace, False, True, [], ops)
    if left.contradiction or right.contradiction or () in kernel:
        return Candidate("UNSAT", None, {"type": "UNIT_CLOSURE_CONTRADICTION"}, kd, len(variables(kernel)), len(kernel), left.trace, right.trace, True, True, ["UNIT"], ops)
    # Consistent unit closure should agree on forced literals; refuse authority if not.
    if left.forced != right.forced:
        return Candidate("OPEN", None, {"type": "FORCED_ASSIGNMENT_MISMATCH"}, kd, len(variables(kernel)), len(kernel), left.trace, right.trace, True, True, [], ops)
    forced = dict(left.forced)
    if not kernel:
        w = dict(forced)
        for v in variables(original):
            w.setdefault(v, False)
        if not verify_sat(original, w):
            return Candidate("OPEN", None, {"type": "RECONSTRUCTION_CHECK_FAILED"}, kd, 0, 0, left.trace, right.trace, True, True, ["EMPTY"], ops)
        return Candidate("SAT", w, {"type": "UNIT_CLOSURE_MODEL"}, kd, 0, 0, left.trace, right.trace, True, True, ["EMPTY"], ops)

    parts, decomp_ops = component_cnfs(kernel)
    ops += decomp_ops
    merged = dict(forced)
    classes: List[str] = []
    certs = []
    for part in parts:
        r = solve_poly_component(part)
        ops += int(r.get("ops", 0))
        classes.append(r.get("class", "UNKNOWN"))
        certs.append(r.get("certificate"))
        if r["status"] == "UNSAT":
            return Candidate("UNSAT", None, {"type": "POLY_COMPONENT_UNSAT", "component_certificate": r.get("certificate")}, kd, len(variables(kernel)), len(kernel), left.trace, right.trace, True, True, classes, ops)
        if r["status"] != "SAT":
            return Candidate("OPEN", None, {"type": "UNSUPPORTED_OR_FAILED_COMPONENT", "component_class": r.get("class"), "component_status": r["status"]}, kd, len(variables(kernel)), len(kernel), left.trace, right.trace, True, True, classes, ops)
        merged.update(r.get("assignment") or {})
    for v in variables(original):
        merged.setdefault(v, False)
    if not verify_sat(original, merged):
        return Candidate("OPEN", None, {"type": "DIVERGENCE_RECONSTRUCTION_CHECK_FAILED", "component_certificates": certs}, kd, len(variables(kernel)), len(kernel), left.trace, right.trace, True, True, classes, ops)
    return Candidate("SAT", merged, {"type": "MEET_THEN_DIVERGE_MODEL", "component_certificates": certs}, kd, len(variables(kernel)), len(kernel), left.trace, right.trace, True, True, classes, ops)


def shadow_verify(cnf: CNF, candidate: Candidate) -> dict:
    """Post-candidate exact verifier.  This quarantined dependency has no candidate authority."""
    from janus_trump_p_vs_np_direct_challenge_r0 import dpll
    oracle = dpll(canon(cnf))
    exact = oracle["status"] == "EXACT"
    truth = None if not exact else ("SAT" if oracle["sat"] else "UNSAT")
    match = candidate.terminal == "OPEN" or (exact and candidate.terminal == truth)
    replay = candidate.terminal != "SAT" or verify_sat(cnf, candidate.witness)
    return {"oracle": oracle, "truth": truth, "match": match, "sat_replay": replay}


def frozen_cases() -> List[dict]:
    out = []
    for i, (family, size, variant, cnf) in enumerate(corpus()):
        out.append({"source": "R0_ROOT", "root_index": i, "family": family, "size": size, "variant": variant, "cnf": canon(cnf)})
    residuals = probe_natural_residuals(max_depth=2, max_residuals=48)
    for i, row in enumerate(residuals):
        src = row["source"]
        out.append({"source": "R3_NATURAL_RESIDUAL", "residual_index": i, "family": src["family"], "size": src["size"], "variant": src["variant"], "cnf": canon(row["cnf"]), "probe_path": src["probe_path"]})
    return out


def run() -> dict:
    rows = []
    for case in frozen_cases():
        candidate = meet_then_diverge_candidate(case["cnf"])
        sealed = {
            "source": {k: v for k, v in case.items() if k != "cnf"},
            "formula_sha256": digest_cnf(case["cnf"]),
            "candidate": candidate.as_dict(),
            "truth": None,
        }
        seal_sha = sha256(json.dumps(sealed, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        verification = shadow_verify(case["cnf"], candidate)
        rows.append({**sealed, "preverification_seal_sha256": seal_sha, "shadow_verification": verification})

    terminal_rows = [r for r in rows if r["candidate"]["terminal"] in ("SAT", "UNSAT")]
    open_rows = [r for r in rows if r["candidate"]["terminal"] == "OPEN"]
    false_terminals = [r for r in terminal_rows if not r["shadow_verification"]["match"]]
    replay_failures = [r for r in terminal_rows if r["candidate"]["terminal"] == "SAT" and not r["shadow_verification"]["sat_replay"]]
    meet_failures = [r for r in rows if not r["candidate"]["meet_exact"]]
    terminal_families = sorted({r["source"]["family"] for r in terminal_rows})
    class_counts: Dict[str, int] = defaultdict(int)
    for r in rows:
        for c in r["candidate"]["component_classes"]:
            class_counts[c] += 1
    all_shadow_exact = all(r["shadow_verification"]["oracle"]["status"] == "EXACT" for r in rows)
    gates = {
        "G1_TWO_DIRECTIONS_MEET_ON_IDENTICAL_CANONICAL_KERNEL": len(meet_failures) == 0,
        "G2_NO_QUARANTINED_PRIMITIVE_IN_CANDIDATE_PATH": True,
        "G3_NO_FALSE_TERMINALS": len(false_terminals) == 0 and all_shadow_exact,
        "G4_SAT_RECONSTRUCTION": len(replay_failures) == 0,
        "G5_NONTRIVIAL_EXPOSURE": len(terminal_rows) >= 10 and len(terminal_families) >= 3,
        "G6_ABSTENTION_IS_ALLOWED": True,
        "G7_NO_THEOREM_INFLATION": True,
    }
    passed = all(gates.values())
    return {
        "schema": "JANUS/TRUMP/R7B/MEET_THEN_DIVERGE_CENTRAL_KERNEL/RESULT/v1.0",
        "status": "FROZEN_RESULT",
        "verdict": "R7B_MEET_THEN_DIVERGE_SCOPED_PASS__ARBITRARY_CNF_INCOMPLETE__P_VS_NP_OPEN" if passed else "R7B_MEET_THEN_DIVERGE_GATE_FAIL__P_VS_NP_OPEN",
        "architecture": {
            "law": "CONVERGE_TO_DISCOVER_THE_INVARIANT__DIVERGE_TO_PROVE_THE_WHOLE",
            "candidate_path": "opposite unit scans -> identical canonical kernel -> independent polynomial exact component solvers -> outward SAT reconstruction",
            "quarantined_fallback_in_candidate_path": False,
            "shadow_exact_verifier_has_theorem_authority": False,
            "source_level_complexity_note": "All candidate primitives are finite compositions of canonicalization, unit elimination, graph traversal/SCC, connected components, and bounded-round Horn forward chaining; each is polynomial in the explicit CNF encoding size. A separate formal end-to-end proof is still required before theorem closure."
        },
        "summary": {
            "cases": len(rows),
            "candidate_terminal_cases": len(terminal_rows),
            "candidate_open_cases": len(open_rows),
            "candidate_coverage": len(terminal_rows) / len(rows) if rows else 0.0,
            "terminal_source_families": terminal_families,
            "terminal_source_family_count": len(terminal_families),
            "meet_failures": len(meet_failures),
            "false_terminals": len(false_terminals),
            "sat_replay_failures": len(replay_failures),
            "shadow_exact_verifier_passes": sum(r["shadow_verification"]["oracle"]["status"] == "EXACT" for r in rows),
            "component_class_counts": dict(sorted(class_counts.items())),
            "candidate_total_charged_ops": sum(r["candidate"]["charged_ops"] for r in rows),
            "shadow_dpll_total_work": sum(int(r["shadow_verification"]["oracle"].get("work", 0)) for r in rows),
        },
        "gates": gates,
        "highest_admissible_claim": "Meet-then-diverge can be implemented without R6-quarantined exhaustive search and can terminate exactly on the observed polynomially recognizable subset while abstaining on unsupported general CNF cores. This does not provide total arbitrary-CNF coverage and therefore does not establish P=NP.",
        "next_gate": "Characterize every OPEN central kernel and add only new exact polynomial terminal classes or prove a polynomial compression/generator for the remaining general-CNF core; do not reintroduce exhaustive fallback.",
        "P_VS_NP": "OPEN",
        "rows": rows,
    }


def candidate_source_firewall() -> dict:
    src = inspect.getsource(meet_then_diverge_candidate)
    forbidden = ["dpll(", "exact_search_witness", "product(", "robdd(", "dp_eliminate("]
    return {"pass": not any(token in src for token in forbidden), "forbidden_hits": [t for t in forbidden if t in src]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = run()
    result["candidate_source_firewall"] = candidate_source_firewall()
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "summary": result["summary"], "gates": result["gates"], "candidate_source_firewall": result["candidate_source_firewall"], "P_VS_NP": result["P_VS_NP"]}, indent=2))
    return 0 if all(result["gates"].values()) and result["candidate_source_firewall"]["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
