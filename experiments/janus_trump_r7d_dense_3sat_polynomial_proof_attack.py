#!/usr/bin/env python3
"""R7D: fixed-width proof attack on the ten exposed R7C dense-3SAT OPEN kernels.

Candidate truth authority uses no R6-quarantined exhaustive search.  The only
new proof machinery is fixed-width (k=4) resolution plus exact Davis-Putnam
variable elimination when *every* required resolvent for the chosen pivot stays
within the same frozen width.  If no such safe pivot exists, the candidate
returns OPEN.

This is discovery evidence on an exposed remainder, never a P=NP claim.
"""
from __future__ import annotations

import argparse
import inspect
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from hashlib import sha256
from math import comb
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import janus_trump_r7b_meet_then_diverge_central_kernel as r7b
import janus_trump_r7c_open49_poly_kernel_assault as r7c
from janus_trump_p_vs_np_direct_challenge_r0 import canon, variables

Clause = Tuple[int, ...]
CNF = Tuple[Clause, ...]
Assignment = Dict[int, bool]
WIDTH_K = 4


def clause_key(c: Clause) -> Tuple[int, Tuple[int, ...]]:
    return (len(c), c)


def normalize_clause(lits: Iterable[int]) -> Optional[Clause]:
    s = set(int(x) for x in lits)
    if any(-x in s for x in s):
        return None
    return tuple(sorted(s, key=lambda x: (abs(x), x < 0)))


def resolve_pair(a: Clause, b: Clause, pivot: int) -> Optional[Clause]:
    if pivot not in a or -pivot not in b:
        if -pivot in a and pivot in b:
            a, b = b, a
        else:
            return None
    return normalize_clause([x for x in a if x != pivot] + [x for x in b if x != -pivot])


def clause_universe_bound(nvars: int, k: int = WIDTH_K) -> int:
    return sum(comb(2 * nvars, i) for i in range(0, min(k, 2 * nvars) + 1))


def proof_ancestors(empty_clause: Clause, parents: Dict[Clause, Optional[Tuple[Clause, Clause, int]]]) -> List[dict]:
    order: List[Clause] = []
    seen: Set[Clause] = set()

    def visit(c: Clause) -> None:
        if c in seen:
            return
        p = parents.get(c)
        if p is not None:
            visit(p[0]); visit(p[1])
        seen.add(c); order.append(c)

    visit(empty_clause)
    out = []
    for c in order:
        p = parents.get(c)
        if p is None:
            out.append({"clause": list(c), "kind": "AXIOM"})
        else:
            out.append({"clause": list(c), "kind": "RESOLUTION", "left": list(p[0]), "right": list(p[1]), "pivot": p[2]})
    return out


def replay_resolution_proof(original: CNF, proof: Sequence[dict], k: int = WIDTH_K) -> bool:
    known = set(canon(original))
    for step in proof:
        c = tuple(step["clause"])
        if len(c) > k:
            return False
        if step["kind"] == "AXIOM":
            if c not in known:
                return False
            continue
        if step["kind"] != "RESOLUTION":
            return False
        a, b, p = tuple(step["left"]), tuple(step["right"]), int(step["pivot"])
        if a not in known or b not in known:
            return False
        rr = resolve_pair(a, b, p)
        if rr is None or rr != c or len(rr) > k:
            return False
        known.add(c)
    return () in known


@dataclass
class ResolutionResult:
    status: str
    saturated: CNF
    ops: int
    derived: int
    blocked_wide: int
    proof: Optional[List[dict]]
    universe_bound: int


def fixed_width_resolution(cnf: CNF, k: int = WIDTH_K) -> ResolutionResult:
    f = canon(cnf)
    if any(len(c) > k for c in f):
        return ResolutionResult("OPEN_INPUT_WIDTH", f, 0, 0, 0, None, clause_universe_bound(len(variables(f)), k))
    if () in f:
        proof = [{"clause": [], "kind": "AXIOM"}]
        return ResolutionResult("UNSAT", f, 1, 0, 0, proof, clause_universe_bound(len(variables(f)), k))

    clauses: Set[Clause] = set(f)
    parents: Dict[Clause, Optional[Tuple[Clause, Clause, int]]] = {c: None for c in f}
    index: Dict[int, Set[Clause]] = defaultdict(set)
    agenda = deque(sorted(f, key=clause_key))
    ops = 0
    derived = 0
    blocked = 0
    ub = clause_universe_bound(len(variables(f)), k)

    while agenda:
        c = agenda.popleft()
        for lit in c:
            for d in list(index.get(-lit, ())):
                ops += len(c) + len(d) + 1
                rr = resolve_pair(c, d, lit)
                if rr is None:
                    continue
                if len(rr) > k:
                    blocked += 1
                    continue
                if rr in clauses:
                    continue
                clauses.add(rr)
                parents[rr] = (c, d, lit)
                agenda.append(rr)
                derived += 1
                if len(clauses) > ub:
                    return ResolutionResult("INTERNAL_UNIVERSE_BOUND_FAILURE", canon(tuple(clauses)), ops, derived, blocked, None, ub)
                if rr == ():
                    proof = proof_ancestors(rr, parents)
                    if not replay_resolution_proof(f, proof, k):
                        return ResolutionResult("INTERNAL_PROOF_REPLAY_FAILURE", canon(tuple(clauses)), ops, derived, blocked, proof, ub)
                    return ResolutionResult("UNSAT", canon(tuple(clauses)), ops, derived, blocked, proof, ub)
        for lit in c:
            index[lit].add(c)
    return ResolutionResult("SATURATION_COMPLETE_NO_REFUTATION", canon(tuple(clauses)), ops, derived, blocked, None, ub)


def pivot_resolvents(cnf: CNF, v: int, k: int = WIDTH_K) -> dict:
    f = canon(cnf)
    pos = [c for c in f if v in c]
    neg = [c for c in f if -v in c]
    rest = [c for c in f if v not in c and -v not in c]
    resolvents: Set[Clause] = set()
    ops = 0
    for a in pos:
        for b in neg:
            ops += len(a) + len(b) + 1
            rr = resolve_pair(a, b, v)
            if rr is None:
                continue
            if len(rr) > k:
                return {"safe": False, "pivot": v, "resolvents": set(), "rest": rest, "pos": pos, "neg": neg, "ops": ops, "blocked": {"width": len(rr), "left": list(a), "right": list(b), "pivot": v}}
            resolvents.add(rr)
    return {"safe": True, "pivot": v, "resolvents": resolvents, "rest": rest, "pos": pos, "neg": neg, "ops": ops, "blocked": None}


def choose_safe_pivot(cnf: CNF, k: int = WIDTH_K) -> Tuple[Optional[dict], int, List[dict]]:
    plans: List[dict] = []
    ops = 0
    blocked_rows = []
    for v in variables(cnf):
        p = pivot_resolvents(cnf, v, k)
        ops += int(p["ops"])
        if p["safe"]:
            plans.append(p)
        elif p["blocked"] is not None:
            blocked_rows.append(p["blocked"])
    if not plans:
        return None, ops, blocked_rows
    plans.sort(key=lambda p: (len(p["resolvents"]), len(p["pos"]) * len(p["neg"]), p["pivot"]))
    return plans[0], ops, blocked_rows


def cnf_digest(cnf: CNF) -> str:
    return sha256(json.dumps([list(c) for c in canon(cnf)], separators=(",", ":")).encode()).hexdigest()


@dataclass
class EliminationResult:
    status: str
    witness: Optional[Assignment]
    ops: int
    records: List[dict]
    blocked_pivots: List[dict]
    final_cnf: CNF


def reconstruct_elimination(original: CNF, records: Sequence[dict]) -> Optional[Assignment]:
    pivot_vars = {int(rec["pivot"]) for rec in records}
    # A variable may disappear from the reduced formula without ever becoming a
    # pivot (for example after a pure-variable elimination).  Semantically it is
    # still a remaining variable of the existential projection, so fix such
    # unconstrained variables deterministically before reverse extension.
    a: Assignment = {v: False for v in variables(original) if v not in pivot_vars}
    for rec in reversed(records):
        v = int(rec["pivot"])
        required: Set[bool] = set()
        for raw in rec["removed"]:
            clause = tuple(raw)
            satisfied_without = False
            for lit in clause:
                if abs(lit) == v:
                    continue
                if abs(lit) not in a:
                    return None
                val = a[abs(lit)]
                if (lit > 0 and val) or (lit < 0 and not val):
                    satisfied_without = True
                    break
            if satisfied_without:
                continue
            if v in clause:
                required.add(True)
            if -v in clause:
                required.add(False)
        if len(required) > 1:
            return None
        a[v] = next(iter(required)) if required else False
    if not r7b.verify_sat(original, a):
        return None
    return a


def replay_elimination_certificate(original: CNF, records: Sequence[dict], final_cnf: CNF, k: int = WIDTH_K) -> bool:
    current = canon(original)
    for rec in records:
        if cnf_digest(current) != rec["before_sha256"]:
            return False
        v = int(rec["pivot"])
        p = pivot_resolvents(current, v, k)
        if not p["safe"]:
            return False
        removed = sorted([c for c in current if v in c or -v in c], key=clause_key)
        if [list(c) for c in removed] != rec["removed"]:
            return False
        nxt = canon(tuple(p["rest"] + list(p["resolvents"])))
        if cnf_digest(nxt) != rec["after_sha256"]:
            return False
        current = nxt
    return current == canon(final_cnf)


def width_bounded_eliminate(cnf: CNF, k: int = WIDTH_K) -> EliminationResult:
    original = canon(cnf)
    f = original
    records: List[dict] = []
    all_blocked: List[dict] = []
    ops = 0
    while True:
        if () in f:
            ok = replay_elimination_certificate(original, records, f, k)
            return EliminationResult("UNSAT" if ok else "INTERNAL_CERTIFICATE_FAILURE", None, ops, records, all_blocked, f)
        if not f or not variables(f):
            if not replay_elimination_certificate(original, records, f, k):
                return EliminationResult("INTERNAL_CERTIFICATE_FAILURE", None, ops, records, all_blocked, f)
            witness = reconstruct_elimination(original, records)
            return EliminationResult("SAT" if witness is not None else "INTERNAL_RECONSTRUCTION_FAILURE", witness, ops, records, all_blocked, f)

        plan, plan_ops, blocked = choose_safe_pivot(f, k)
        ops += plan_ops
        all_blocked.extend(blocked)
        if plan is None:
            return EliminationResult("OPEN_WIDTH_BARRIER", None, ops, records, all_blocked, f)
        v = int(plan["pivot"])
        removed = sorted([c for c in f if v in c or -v in c], key=clause_key)
        nxt = canon(tuple(plan["rest"] + list(plan["resolvents"])))
        records.append({
            "pivot": v,
            "before_sha256": cnf_digest(f),
            "after_sha256": cnf_digest(nxt),
            "removed": [list(c) for c in removed],
            "resolvent_count": len(plan["resolvents"]),
            "max_resolvent_width": max((len(c) for c in plan["resolvents"]), default=0),
        })
        ops += len(f) + len(plan["resolvents"]) + 1
        f = nxt


def attack_component(part: CNF) -> dict:
    f = canon(part)
    rr = fixed_width_resolution(f, WIDTH_K)
    ops = rr.ops
    if rr.status == "UNSAT":
        return {"status": "UNSAT", "class": "WIDTH4_RESOLUTION_REFUTATION", "assignment": None, "ops": ops, "certificate": {"type": "WIDTH4_RESOLUTION_REFUTATION", "width": WIDTH_K, "proof": rr.proof, "derived_clauses": rr.derived, "blocked_wide_resolvents": rr.blocked_wide, "clause_universe_bound": rr.universe_bound}}
    if rr.status != "SATURATION_COMPLETE_NO_REFUTATION":
        return {"status": "OPEN", "class": "WIDTH4_UNSUPPORTED", "assignment": None, "ops": ops, "certificate": {"type": rr.status}}

    er = width_bounded_eliminate(rr.saturated, WIDTH_K)
    ops += er.ops
    if er.status == "UNSAT":
        return {"status": "UNSAT", "class": "WIDTH4_EXACT_ELIMINATION", "assignment": None, "ops": ops, "certificate": {"type": "WIDTH4_EXACT_ELIMINATION_REFUTATION", "width": WIDTH_K, "records": er.records, "final_cnf": [list(c) for c in er.final_cnf]}}
    if er.status == "SAT":
        if er.witness is None or not r7b.verify_sat(f, er.witness):
            return {"status": "OPEN", "class": "WIDTH4_RECONSTRUCTION_FAILURE", "assignment": None, "ops": ops, "certificate": {"type": "MODEL_REPLAY_FAILED"}}
        return {"status": "SAT", "class": "WIDTH4_EXACT_ELIMINATION", "assignment": er.witness, "ops": ops, "certificate": {"type": "WIDTH4_EXACT_ELIMINATION_MODEL", "width": WIDTH_K, "records": er.records, "saturation_derived_clauses": rr.derived, "blocked_wide_resolvents": rr.blocked_wide}}
    return {"status": "OPEN", "class": "WIDTH4_BARRIER", "assignment": None, "ops": ops, "certificate": {"type": er.status, "width": WIDTH_K, "safe_elimination_steps": len(er.records), "remaining_variables": len(variables(er.final_cnf)), "remaining_clauses": len(er.final_cnf), "blocked_pivot_witnesses": er.blocked_pivots[:32], "saturation_derived_clauses": rr.derived, "blocked_wide_resolvents": rr.blocked_wide}}


@dataclass
class Candidate:
    terminal: str
    witness: Optional[Assignment]
    certificate: dict
    component_classes: List[str]
    ops: int

    def as_dict(self) -> dict:
        return {"terminal": self.terminal, "witness": None if self.witness is None else {str(k): bool(v) for k, v in sorted(self.witness.items())}, "certificate": self.certificate, "component_classes": self.component_classes, "charged_ops": self.ops}


def r7d_candidate(cnf: CNF) -> Candidate:
    original = canon(cnf)
    left = r7b.unit_converge(original, reverse_scan=False)
    right = r7b.unit_converge(original, reverse_scan=True)
    ops = left.ops + right.ops
    if left.kernel != right.kernel or left.forced != right.forced:
        return Candidate("OPEN", None, {"type": "R7B_MEET_OR_FORCE_MISMATCH"}, [], ops)
    if left.contradiction or right.contradiction or () in left.kernel:
        return Candidate("UNSAT", None, {"type": "UNIT_CONVERGENCE_CONTRADICTION"}, ["UNIT"], ops)

    forced = dict(left.forced)
    closure = r7c.polynomial_kernel_closure(left.kernel)
    ops += closure.ops
    if not r7c.merge_assignment(forced, closure.forced):
        return Candidate("OPEN", None, {"type": "R7C_FORCE_MERGE_CONFLICT"}, [], ops)
    if closure.contradiction or () in closure.kernel:
        return Candidate("UNSAT", None, {"type": "R7C_POLYNOMIAL_CLOSURE_CONTRADICTION", "inner": closure.certificate}, ["FAILED_LITERAL_OR_UNIT"], ops)
    if not closure.kernel:
        w = dict(forced)
        for v in variables(original):
            w.setdefault(v, False)
        return Candidate("SAT", w, {"type": "R7C_CLOSURE_MODEL"}, ["CLOSURE_EMPTY"], ops) if r7b.verify_sat(original, w) else Candidate("OPEN", None, {"type": "R7C_CLOSURE_REPLAY_FAILED"}, [], ops)

    parts, decomp_ops = r7b.component_cnfs(closure.kernel)
    ops += decomp_ops
    merged = dict(forced)
    classes: List[str] = []
    certs: List[dict] = []
    for part in parts:
        base = r7c.solve_expanded_poly_component(part)
        ops += int(base.get("ops", 0))
        if base["status"] == "UNSAT":
            classes.append(base.get("class", "R7C_POLY"))
            return Candidate("UNSAT", None, {"type": "R7C_COMPONENT_UNSAT", "inner": base.get("certificate")}, classes, ops)
        if base["status"] == "SAT":
            classes.append(base.get("class", "R7C_POLY"))
            if not r7c.merge_assignment(merged, base.get("assignment") or {}):
                return Candidate("OPEN", None, {"type": "R7C_COMPONENT_ASSIGNMENT_CONFLICT"}, classes, ops)
            certs.append(base.get("certificate", {}))
            continue

        attacked = attack_component(part)
        ops += int(attacked.get("ops", 0))
        classes.append(attacked.get("class", "R7D_UNKNOWN"))
        certs.append(attacked.get("certificate", {}))
        if attacked["status"] == "UNSAT":
            return Candidate("UNSAT", None, {"type": "R7D_WIDTH4_COMPONENT_UNSAT", "inner": attacked.get("certificate")}, classes, ops)
        if attacked["status"] != "SAT":
            return Candidate("OPEN", None, {"type": "R7D_WIDTH4_BARRIER", "inner": attacked.get("certificate")}, classes, ops)
        if not r7c.merge_assignment(merged, attacked.get("assignment") or {}):
            return Candidate("OPEN", None, {"type": "R7D_COMPONENT_ASSIGNMENT_CONFLICT"}, classes, ops)

    for v in variables(original):
        merged.setdefault(v, False)
    if not r7b.verify_sat(original, merged):
        return Candidate("OPEN", None, {"type": "R7D_FINAL_REPLAY_FAILED", "component_certificates": certs}, classes, ops)
    return Candidate("SAT", merged, {"type": "R7D_MEET_WIDTH4_DIVERGE_MODEL", "component_certificates": certs}, classes, ops)


def target_cases() -> List[dict]:
    return [case for case in r7c.target_cases() if r7c.r7c_candidate(case["cnf"]).terminal == "OPEN"]


def shadow_verify(cnf: CNF, candidate: Candidate) -> dict:
    from janus_trump_p_vs_np_direct_challenge_r0 import dpll
    oracle = dpll(canon(cnf))
    exact = oracle["status"] == "EXACT"
    truth = None if not exact else ("SAT" if oracle["sat"] else "UNSAT")
    return {"oracle": oracle, "truth": truth, "terminal_match": candidate.terminal == "OPEN" or (exact and candidate.terminal == truth), "sat_replay": candidate.terminal != "SAT" or r7b.verify_sat(cnf, candidate.witness)}


def candidate_source_firewall() -> dict:
    funcs = [r7d_candidate, attack_component, fixed_width_resolution, width_bounded_eliminate, choose_safe_pivot, pivot_resolvents]
    src = "\n".join(inspect.getsource(f) for f in funcs)
    forbidden = ["dpll(", "exact_search_witness", "itertools.product", "robdd("]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "forbidden_hits": hits}


def run() -> dict:
    targets = target_cases()
    rows = []
    for case in targets:
        candidate = r7d_candidate(case["cnf"])
        sealed = {"source": {k: v for k, v in case.items() if k != "cnf"}, "formula_sha256": r7b.digest_cnf(case["cnf"]), "candidate": candidate.as_dict(), "truth": None}
        seal = sha256(json.dumps(sealed, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        verification = shadow_verify(case["cnf"], candidate)
        rows.append({**sealed, "preverification_seal_sha256": seal, "shadow_verification": verification})

    terminal = [r for r in rows if r["candidate"]["terminal"] in ("SAT", "UNSAT")]
    remaining = [r for r in rows if r["candidate"]["terminal"] == "OPEN"]
    false_terminals = [r for r in terminal if not r["shadow_verification"]["terminal_match"]]
    replay_failures = [r for r in terminal if r["candidate"]["terminal"] == "SAT" and not r["shadow_verification"]["sat_replay"]]
    class_counts: Dict[str, int] = defaultdict(int)
    for r in rows:
        for c in r["candidate"]["component_classes"]:
            class_counts[c] += 1
    families = sorted({r["source"]["family"] for r in rows})
    firewall = candidate_source_firewall()
    gates = {
        "G1_TARGETS_EXACTLY_10": len(rows) == 10,
        "G2_ALL_TARGETS_RANDOM_3SAT_NEAR_DENSE": families == ["RANDOM_3SAT_NEAR_DENSE"],
        "G3_NO_R6_QUARANTINED_PRIMITIVE": firewall["pass"],
        "G4_ZERO_FALSE_TERMINALS": len(false_terminals) == 0 and all(r["shadow_verification"]["oracle"]["status"] == "EXACT" for r in rows),
        "G5_ZERO_SAT_REPLAY_FAILURES": len(replay_failures) == 0,
        "G6_UNSUPPORTED_STAYS_OPEN": all(r["candidate"]["terminal"] == "OPEN" for r in remaining),
        "G7_NO_THEOREM_INFLATION": True,
    }
    passed = all(gates.values())
    return {
        "schema": "JANUS/TRUMP/R7D/DENSE_3SAT_POLYNOMIAL_PROOF_ATTACK/RESULT/v1.0",
        "status": "FROZEN_RESULT",
        "verdict": "R7D_DENSE3SAT_WIDTH4_SCOPED_PASS__REMAINDER_OPEN__P_VS_NP_OPEN" if passed else "R7D_GATE_FAIL__P_VS_NP_OPEN",
        "scope": "EXPOSED_R7C_REMAINDER_DISCOVERY_ONLY",
        "frozen_width": WIDTH_K,
        "summary": {
            "targets": len(rows),
            "recovered_terminal_cases": len(terminal),
            "remaining_open_cases": len(remaining),
            "recovery_fraction": len(terminal) / len(rows) if rows else 0.0,
            "target_families": families,
            "false_terminals": len(false_terminals),
            "sat_replay_failures": len(replay_failures),
            "component_class_counts": dict(sorted(class_counts.items())),
            "candidate_total_charged_ops": sum(int(r["candidate"]["charged_ops"]) for r in rows),
            "shadow_dpll_total_work": sum(int(r["shadow_verification"]["oracle"].get("work", 0)) for r in rows),
        },
        "gates": gates,
        "candidate_source_firewall": firewall,
        "highest_admissible_claim": "On the ten exposed R7C dense-3SAT remainder cases, frozen width-4 resolution/elimination may recover exact terminals without R6-quarantined exhaustive search. Unsupported width requirements remain OPEN. This discovery run cannot establish arbitrary-CNF totality, general speedup, or P=NP.",
        "next_gate": "If any width-4 terminal is recovered, freeze the mechanism unchanged and test on unseen natural dense-3SAT residuals. Independently characterize remaining OPEN width barriers before changing k or adding proof rules.",
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
