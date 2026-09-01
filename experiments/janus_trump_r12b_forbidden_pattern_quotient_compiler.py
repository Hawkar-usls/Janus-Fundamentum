#!/usr/bin/env python3
"""R12B: forbidden-pattern minimal-basis quotient compiler.

Candidate lane only:
  * canonical non-tautological clauses of width <=4 are forbidden partial patterns;
  * derivation labels/history are not states;
  * clauses dominated by a stronger subsuming clause are removed from the active
    semantic basis (their proof provenance remains archived);
  * resolution never creates width >4 states;
  * no DPLL, branching, assignment enumeration, DP elimination, or oracle routing.

The exact R10/R11 bridge witness is invoked only after a candidate fixed point.
"""
from __future__ import annotations

import argparse
import inspect
import json
import math
import time
from collections import defaultdict, deque
from hashlib import sha256
from itertools import combinations
from pathlib import Path

import janus_trump_r10_exact_semantic_bridge_interface as r10
import janus_trump_r11_exact_interface_structure_microscope as r11
import janus_trump_r12_direct_width4_interface_compiler as r12

WIDTH_CAP = 4
OPEN_INDICES = (3, 7)
WALL_SECONDS_PER_WORLD = 600
PROGRESS_INTERVAL_SECONDS = 5
EXPECTED = {
    3: {"allowed": 135, "truth_sha256": "9032c5d24f3e2bea515f78c57b0a019c8918f5c3f4677314e65da2035e68b29c"},
    7: {"allowed": 127, "truth_sha256": "93004dbf4c532e8522191785bc8f98b5625c7c5a04e3f6a2b5b61fb097bfc066"},
}


def canonical_clause(lits):
    vals = set(int(x) for x in lits)
    if 0 in vals:
        raise ValueError("literal 0 is invalid")
    if any(-x in vals for x in vals):
        return None
    return tuple(sorted(vals, key=lambda x: (abs(x), x < 0)))


def resolve_on(a, b, pivot_lit):
    if pivot_lit not in a or -pivot_lit not in b:
        raise ValueError("invalid pivot orientation")
    return canonical_clause(
        [x for x in a if x != pivot_lit]
        + [x for x in b if x != -pivot_lit]
    )


def clause_subsumes(a, b):
    """Exact semantic dominance: clause a implies clause b when a subseteq b."""
    return len(a) <= len(b) and all(lit in b for lit in a)


def state_universe_bound(n, width_cap=WIDTH_CAP):
    return sum(math.comb(n, i) * (2 ** i) for i in range(width_cap + 1))


def active_subsumer(active, clause):
    """Find an active literal-subset of clause in O(2^k), k<=4."""
    for r in range(len(clause) + 1):
        for sub in combinations(clause, r):
            c = canonical_clause(sub)
            if c in active:
                return c
    return None


def active_supersets(active, by_lit, clause):
    if not clause:
        return list(active)
    pivot = min(clause, key=lambda lit: len(by_lit.get(lit, ())))
    pool = tuple(by_lit.get(pivot, ()))
    return [d for d in pool if d != clause and clause_subsumes(clause, d)]


def minimal_basis(clauses):
    ordered = sorted({canonical_clause(c) for c in clauses if canonical_clause(c) is not None}, key=lambda c: (len(c), c))
    out = []
    for c in ordered:
        if any(clause_subsumes(a, c) for a in out):
            continue
        out = [a for a in out if not clause_subsumes(c, a)]
        out.append(c)
    return tuple(sorted(out, key=lambda c: (len(c), c)))


def saturate_forbidden_pattern_basis(frame_cnf, wall_seconds=WALL_SECONDS_PER_WORLD, progress_label="world"):
    """Event-driven width-4 resolution directly in a minimal semantic basis."""
    active = set()
    by_lit = defaultdict(set)
    seen_content = set()
    birth = {}
    proof = []
    queue = deque()
    stats = {
        "initial_input_clauses": len(frame_cnf),
        "input_duplicates_or_dominated": 0,
        "pair_pivots_attempted": 0,
        "tautological_resolvents": 0,
        "too_wide_resolvents": 0,
        "duplicate_content_collapsed": 0,
        "dominated_new_states_collapsed": 0,
        "active_weaker_states_removed": 0,
        "new_content_states": 0,
        "stale_queue_states_skipped": 0,
    }
    variables = {abs(l) for c in frame_cnf for l in c}
    universe = state_universe_bound(len(variables))
    start = time.monotonic()
    next_progress = start + PROGRESS_INTERVAL_SECONDS

    def deactivate(c):
        if c not in active:
            return
        active.remove(c)
        for lit in c:
            by_lit[lit].discard(c)

    def add(raw, record, is_input=False):
        c = canonical_clause(raw)
        if c is None:
            stats["tautological_resolvents"] += 1
            return "TAUTOLOGY", None
        if len(c) > WIDTH_CAP:
            stats["too_wide_resolvents"] += 1
            return "TOO_WIDE", c
        if c in seen_content:
            stats["duplicate_content_collapsed"] += 1
            return "SEEN", c
        stronger = active_subsumer(active, c)
        if stronger is not None:
            seen_content.add(c)
            stats["dominated_new_states_collapsed"] += 1
            if is_input:
                stats["input_duplicates_or_dominated"] += 1
            return "DOMINATED", c
        supers = active_supersets(active, by_lit, c)
        for d in supers:
            deactivate(d)
            stats["active_weaker_states_removed"] += 1
        cid = len(proof)
        seen_content.add(c)
        birth[c] = cid
        proof.append({"clause": c, **record})
        active.add(c)
        for lit in c:
            by_lit[lit].add(c)
        queue.append(c)
        stats["new_content_states"] += 1
        return "NEW", c

    for raw in frame_cnf:
        add(raw, {"kind": "AXIOM"}, is_input=True)

    while queue:
        now = time.monotonic()
        if now - start >= wall_seconds:
            stats["elapsed_seconds"] = now - start
            stats["active_basis_size"] = len(active)
            stats["seen_content_states"] = len(seen_content)
            stats["state_universe_bound_N4"] = universe
            stats["theoretical_pair_pivot_bound"] = 4 * universe * universe
            return {
                "status": "OPEN_RESOURCE",
                "reason": "FROZEN_WALL_ENVELOPE_REACHED_BEFORE_FIXED_POINT",
                "active": active,
                "proof": proof,
                "stats": stats,
            }
        if now >= next_progress:
            print(json.dumps({
                "R12B_PROGRESS": progress_label,
                "elapsed_s": round(now - start, 3),
                "queue": len(queue),
                "active": len(active),
                "seen": len(seen_content),
                "pairs": stats["pair_pivots_attempted"],
                "duplicates": stats["duplicate_content_collapsed"],
                "dominated": stats["dominated_new_states_collapsed"],
                "weaker_removed": stats["active_weaker_states_removed"],
                "too_wide": stats["too_wide_resolvents"],
            }, sort_keys=True), flush=True)
            next_progress = now + PROGRESS_INTERVAL_SECONDS

        c = queue.popleft()
        if c not in active:
            stats["stale_queue_states_skipped"] += 1
            continue
        cbirth = birth[c]
        for lit in c:
            for d in tuple(by_lit.get(-lit, ())):
                if d not in active or d == c:
                    continue
                if birth[d] >= cbirth:
                    continue
                stats["pair_pivots_attempted"] += 1
                r = resolve_on(c, d, lit)
                if r is None:
                    stats["tautological_resolvents"] += 1
                    continue
                if len(r) > WIDTH_CAP:
                    stats["too_wide_resolvents"] += 1
                    continue
                add(r, {
                    "kind": "RESOLUTION",
                    "parents": [cbirth, birth[d]],
                    "pivot_lit": int(lit),
                })

    elapsed = time.monotonic() - start
    stats["elapsed_seconds"] = elapsed
    stats["active_basis_size"] = len(active)
    stats["seen_content_states"] = len(seen_content)
    stats["state_universe_bound_N4"] = universe
    stats["theoretical_pair_pivot_bound"] = 4 * universe * universe
    stats["quotient_ratio_seen_to_active"] = (len(seen_content) / len(active)) if active else None
    return {
        "status": "FIXED_POINT",
        "reason": "QUEUE_EMPTY",
        "active": active,
        "proof": proof,
        "stats": stats,
    }


def replay_proof(result, frame_cnf):
    if result["status"] != "FIXED_POINT":
        return None
    axioms = {canonical_clause(c) for c in frame_cnf if canonical_clause(c) is not None}
    derived = []
    for cid, rec in enumerate(result["proof"]):
        c = rec["clause"]
        if rec["kind"] == "AXIOM":
            if c not in axioms:
                return False
        elif rec["kind"] == "RESOLUTION":
            a_id, b_id = rec["parents"]
            if not (0 <= a_id < cid and 0 <= b_id < cid):
                return False
            a, b = derived[a_id], derived[b_id]
            pivot = int(rec["pivot_lit"])
            if pivot not in a or -pivot not in b:
                return False
            if resolve_on(a, b, pivot) != c or len(c) > WIDTH_CAP:
                return False
        else:
            return False
        derived.append(c)
    return True


def bridge_only_basis(active, bridge_vars):
    bridge = set(bridge_vars)
    return minimal_basis([c for c in active if {abs(l) for l in c} <= bridge])


def localize_clause(clause, bridge_vars):
    pos = {v: i + 1 for i, v in enumerate(bridge_vars)}
    return canonical_clause([pos[abs(l)] if l > 0 else -pos[abs(l)] for l in clause])


def candidate_firewall():
    funcs = [canonical_clause, resolve_on, clause_subsumes, state_universe_bound,
             active_subsumer, active_supersets, minimal_basis,
             saturate_forbidden_pattern_basis, replay_proof, bridge_only_basis,
             localize_clause]
    src = "\n".join(inspect.getsource(f) for f in funcs)
    forbidden = ["dpll(", "range(1 <<", "exact_search_witness", "robdd(",
                 "shadow_exact_interface", "compile_projection_interface(", "dp_eliminate("]
    hits = [token for token in forbidden if token in src]
    return {"pass": not hits, "forbidden_hits": hits}


def controls():
    sign_distinct = canonical_clause((1, 2)) != canonical_clause((1, -2))
    q = saturate_forbidden_pattern_basis(((1, 2), (-1, 3)), wall_seconds=2, progress_label="control")
    known = canonical_clause((2, 3)) in q["active"] or any(clause_subsumes(c, canonical_clause((2, 3))) for c in q["active"])
    replay = replay_proof(q, ((1, 2), (-1, 3)))
    dom = saturate_forbidden_pattern_basis(((1,), (1, 2), (1, 2, 3)), wall_seconds=2, progress_label="control_dom")
    dominance = dom["status"] == "FIXED_POINT" and dom["active"] == {canonical_clause((1,))}

    tiny_formula = ((1, 2), (-1, 3), (-2, 4), (-3, -4))
    naive = r12.saturate_width4(tiny_formula)
    quotient = saturate_forbidden_pattern_basis(tiny_formula, wall_seconds=2, progress_label="control_equiv")
    naive_basis = minimal_basis(naive["clauses"])
    quotient_basis = tuple(sorted(quotient["active"], key=lambda c: (len(c), c)))
    same_tiny_basis = quotient["status"] == "FIXED_POINT" and naive_basis == quotient_basis
    return {
        "sign_change_stays_distinct": sign_distinct,
        "known_resolvent_or_stronger_derived": known,
        "proof_replay": replay,
        "dominance_basis_collapses_weaker_patterns": dominance,
        "tiny_naive_vs_quotient_basis_equal": same_tiny_basis,
        "pass": bool(sign_distinct and known and replay and dominance and same_tiny_basis),
    }


# ---------- independent post-candidate witness lane ----------
def assignment_satisfies_local(clauses, mask):
    for c in clauses:
        if not any(bool((mask >> (abs(lit) - 1)) & 1) == (lit > 0) for lit in c):
            return False
    return True


def compare_after_fixed_point(index, world, result):
    if result["status"] != "FIXED_POINT":
        return {"verdict": "OPEN_RESOURCE", "witness_ran": False}
    bridge = tuple(world["bridge_vars"])
    basis = bridge_only_basis(result["active"], bridge)
    local = tuple(sorted({localize_clause(c, bridge) for c in basis}, key=lambda c: (len(c), c)))

    shadow = r10.shadow_exact_interface(world["frame"], bridge)
    if shadow["truth_table_sha256"] != EXPECTED[index]["truth_sha256"]:
        raise AssertionError("immutable witness hash drift")
    if shadow["allowed_count"] != EXPECTED[index]["allowed"]:
        raise AssertionError("immutable allowed count drift")

    exact = set(shadow["allowed_masks"])
    candidate = {m for m in range(1 << len(bridge)) if assignment_satisfies_local(local, m)}
    fp = sorted(candidate - exact)
    fn = sorted(exact - candidate)
    geometry = r11.exact_cnf_geometry(shadow["allowed_masks"], len(bridge))
    exact_primes = {tuple(c) for c in geometry["prime_clauses"]}
    candidate_set = set(local)
    missing = sorted(exact_primes - candidate_set, key=lambda c: (len(c), c))
    violated = []
    if fp:
        witness_mask = fp[0]
        violated = [list(c) for c in missing if not assignment_satisfies_local((c,), witness_mask)][:12]
    return {
        "verdict": "MATCH" if not fp and not fn else "MISMATCH",
        "witness_ran": True,
        "bridge_size": len(bridge),
        "candidate_basis_clause_count": len(local),
        "candidate_basis_sha256": sha256(json.dumps([list(c) for c in local], separators=(",", ":")).encode()).hexdigest(),
        "candidate_allowed_count": len(candidate),
        "exact_allowed_count": len(exact),
        "false_positive_count": len(fp),
        "false_negative_count": len(fn),
        "first_false_positive_masks": fp[:16],
        "first_false_negative_masks": fn[:16],
        "exact_prime_implicate_count": len(exact_primes),
        "exact_prime_overlap_count": len(candidate_set & exact_primes),
        "missing_exact_prime_implicate_count": len(missing),
        "violated_missing_prime_witnesses": violated,
        "truth_table_sha256": shadow["truth_table_sha256"],
        "shadow_dpll_work": shadow["dpll_work"],
    }


def run():
    firewall = candidate_firewall()
    ctl = controls()
    rows = []
    for index in OPEN_INDICES:
        world = r10.frozen_world(index)
        candidate = saturate_forbidden_pattern_basis(world["frame"], WALL_SECONDS_PER_WORLD, f"world_{index}")
        replay = replay_proof(candidate, world["frame"])
        comparison = compare_after_fixed_point(index, world, candidate)
        rows.append({
            "global_index": index,
            "frame_sha256": world["frame_sha256"],
            "frame_variables": len(r10.vars_of(world["frame"])),
            "frame_clauses": len(world["frame"]),
            "bridge_variables": len(world["bridge_vars"]),
            "candidate_status": candidate["status"],
            "candidate_reason": candidate["reason"],
            "candidate_stats": candidate["stats"],
            "proof_replay": replay,
            "comparison": comparison,
        })

    fixed = [r for r in rows if r["candidate_status"] == "FIXED_POINT"]
    resource_open = [r for r in rows if r["candidate_status"] == "OPEN_RESOURCE"]
    integrity = (
        firewall["pass"] and ctl["pass"]
        and all(r["proof_replay"] is True for r in fixed)
        and all(r["comparison"].get("false_negative_count", 0) == 0 for r in fixed)
    )
    all_match = len(fixed) == len(rows) and all(r["comparison"]["verdict"] == "MATCH" for r in rows)
    if not integrity:
        verdict = "R12B_FAIL_INTEGRITY__P_VS_NP_OPEN"
    elif resource_open:
        verdict = "R12B_OPEN_RESOURCE__QUOTIENT_FIXED_POINT_NOT_REACHED_ON_ALL_WORLDS__P_VS_NP_OPEN"
    elif all_match:
        verdict = "R12B_QUOTIENT_COMPILER_MATCH_BOTH__SCOPED_COMPILER_PASS__P_VS_NP_OPEN"
    else:
        verdict = "R12B_QUOTIENT_COMPILER_FIXED_POINT_MISMATCH__TRANSITION_GRAMMAR_INCOMPLETE__P_VS_NP_OPEN"

    gates = {
        "G1_CONTROLS": ctl["pass"],
        "G2_CANDIDATE_FIREWALL": firewall["pass"],
        "G3_PROOF_REPLAY_FOR_FIXED_POINTS": all(r["proof_replay"] is True for r in fixed),
        "G4_FROZEN_WITNESS_ONLY_AFTER_FIXED_POINT": all((r["candidate_status"] == "FIXED_POINT") == bool(r["comparison"].get("witness_ran")) for r in rows),
        "G5_NO_FALSE_NEGATIVES_FROM_SOUND_BASIS": all(r["comparison"].get("false_negative_count", 0) == 0 for r in fixed),
        "G6_RESOURCE_OPEN_NOT_NEGATIVE_EVIDENCE": True,
        "G7_NO_THEOREM_INFLATION": True,
    }
    return {
        "schema": "JANUS/TRUMP/R12B/FORBIDDEN_PATTERN_QUOTIENT_COMPILER/RESULT/v1.0",
        "created_date": "2026-09-01",
        "verdict": verdict,
        "representation_contract": {
            "target_invariant_I": "I_F(B)=EXISTS Y F(Y,B)",
            "candidate_representation": "minimal basis of canonical forbidden partial patterns / width<=4 clauses",
            "state_bound": "N_4(n)=SUM binom(n,i)2^i = O(n^4)",
            "control_has_power_to_say_no": True,
        },
        "firewall": firewall,
        "controls": ctl,
        "gates": gates,
        "worlds": rows,
        "all_match": all_match,
        "law": "DO_NOT_DEDUPLICATE_AFTER_DERIVATION__DERIVE_DIRECTLY_IN_THE_QUOTIENT",
        "seal": "DO_NOT_COUNT_DIFFERENT_NAMES_TWICE__DO_NOT_STORE_A_WEAKER_NO_WHEN_A_STRONGER_NO_ALREADY_EXISTS",
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output")
    args = ap.parse_args()
    data = run()
    text = json.dumps(data, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": data["verdict"],
        "gates": data["gates"],
        "worlds": [{
            "index": r["global_index"],
            "status": r["candidate_status"],
            "active": r["candidate_stats"].get("active_basis_size"),
            "seen": r["candidate_stats"].get("seen_content_states"),
            "pairs": r["candidate_stats"].get("pair_pivots_attempted"),
            "duplicates": r["candidate_stats"].get("duplicate_content_collapsed"),
            "dominated": r["candidate_stats"].get("dominated_new_states_collapsed"),
            "weaker_removed": r["candidate_stats"].get("active_weaker_states_removed"),
            "comparison": r["comparison"]["verdict"],
            "candidate_allowed": r["comparison"].get("candidate_allowed_count"),
            "exact_allowed": r["comparison"].get("exact_allowed_count"),
            "false_pos": r["comparison"].get("false_positive_count"),
        } for r in data["worlds"]],
        "P_VS_NP": data["P_VS_NP"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
