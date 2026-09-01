#!/usr/bin/env python3
"""R13 unseen-interface generalization harness.

This file MUST NOT alter the R12B candidate compiler.  It generates the world
specified by the pre-execution world-set freeze, invokes the imported byte-frozen
R12B width<=4 quotient compiler, and only after candidate fixed point invokes the
independent exact witness lane.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import resource
import time
from pathlib import Path

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r8a_unseen_natural_holdout as r8a
import janus_trump_r9_reference_frame_difference_kernel as r9
import janus_trump_r10_exact_semantic_bridge_interface as r10
import janus_trump_r11_exact_interface_structure_microscope as r11
import janus_trump_r12b_forbidden_pattern_quotient_compiler as r12b

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FREEZE_PATH = REPO / "research" / "JANUS_TRUMP_R13_UNSEEN_INTERFACE_WORLD_SET_FREEZE_2026-09-02.json"
WALL_SECONDS = 600


def sha_payload(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def derive_seed(derivation_string: str) -> int:
    return int.from_bytes(hashlib.sha256(derivation_string.encode()).digest()[:8], "big") % (2 ** 31)


def load_freeze() -> dict:
    d = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    assert d["status"] == "FROZEN_BEFORE_CANDIDATE_EXECUTION"
    assert d["compiler_freeze"]["width_cap"] == 4
    assert d["compiler_freeze"]["logic_changes_allowed"] is False
    assert d["world_generation_contract"]["exact_witness_access_before_candidate_fixed_point"] is False
    for w in d["worlds"]:
        assert derive_seed(w["derivation_string"]) == int(w["seed"])
    return d


def generate_world(spec: dict) -> dict:
    sat_core = r8a.load_legacy_sat_core()
    rng = random.Random(int(spec["seed"]))
    suite = spec["suite"]
    n, m, k = int(spec["n"]), int(spec["m"]), int(spec["k"])
    if suite == "PLANTED":
        inst = sat_core.gen_planted(n, m, k, rng)
    elif suite == "UNSAT_CORE":
        inst = sat_core.gen_unsat_core(n, m, k, rng)
    else:
        raise ValueError(f"unknown frozen suite: {suite}")
    root = direct.canon(inst.clauses)
    order, _ = direct.occurrence_order(root)
    if not order:
        raise AssertionError("frozen world generated no pivot")
    pivot = int(order[0])
    branch_value = bool(spec["branch_value"])
    fd = r9.restriction_frame_delta(root, pivot, branch_value)
    frame = tuple(fd["frame"])
    bridge = tuple(fd["active_bridge_vars"])
    source = {
        "world_id": spec["id"],
        "suite": suite,
        "n_requested": n,
        "m_requested": m,
        "k": k,
        "seed": int(spec["seed"]),
        "branch_value": branch_value,
        "root_sha256": r8a.digest(root),
        "pivot": pivot,
        "frame_sha256": fd["frame_sha256"],
        "frame_type": r9.classify_cnf(frame),
        "frame_variable_count": len(r10.vars_of(frame)),
        "frame_clause_count": len(frame),
        "bridge_vars": list(bridge),
        "bridge_variable_count": len(bridge),
        "delta_sha256": fd["delta_sha256"],
        "exact_witness_accessed": False,
    }
    source["pre_candidate_seal_sha256"] = sha_payload(source)
    return {"source": source, "root": root, "frame": frame, "bridge": bridge}


def local_candidate_basis(candidate: dict, bridge: tuple[int, ...]):
    basis = r12b.bridge_only_basis(candidate["active"], bridge)
    return tuple(sorted({r12b.localize_clause(c, bridge) for c in basis}, key=lambda c: (len(c), c)))


def post_candidate_witness(frame, bridge, local):
    """Exact lane. This function is called only after candidate FIXED_POINT."""
    witness_started = time.time()
    shadow = r10.shadow_exact_interface(frame, bridge)
    exact = set(shadow["allowed_masks"])
    candidate_allowed = {
        mask for mask in range(1 << len(bridge))
        if r12b.assignment_satisfies_local(local, mask)
    }
    fp = sorted(candidate_allowed - exact)
    fn = sorted(exact - candidate_allowed)
    geometry = r11.exact_cnf_geometry(shadow["allowed_masks"], len(bridge))
    exact_primes = {tuple(c) for c in geometry["prime_clauses"]}
    candidate_set = set(local)
    missing = sorted(exact_primes - candidate_set, key=lambda c: (len(c), c))
    extra = sorted(candidate_set - exact_primes, key=lambda c: (len(c), c))
    return {
        "witness_started_unix": witness_started,
        "domain_size": 1 << len(bridge),
        "truth_table_sha256": shadow["truth_table_sha256"],
        "shadow_dpll_work": int(shadow["dpll_work"]),
        "candidate_allowed_count": len(candidate_allowed),
        "exact_allowed_count": len(exact),
        "false_positive_count": len(fp),
        "false_negative_count": len(fn),
        "first_false_positive_masks": fp[:16],
        "first_false_negative_masks": fn[:16],
        "candidate_basis_clause_count": len(candidate_set),
        "exact_prime_implicate_count": len(exact_primes),
        "exact_prime_overlap_count": len(candidate_set & exact_primes),
        "missing_exact_prime_count": len(missing),
        "extra_nonprime_candidate_count": len(extra),
        "first_missing_exact_primes": [list(c) for c in missing[:12]],
        "first_extra_candidate_clauses": [list(c) for c in extra[:12]],
        "allowed_set_exact": not fp and not fn,
        "prime_interface_exact": not missing and not extra,
    }


def run_world(world_id: str) -> dict:
    freeze = load_freeze()
    matches = [w for w in freeze["worlds"] if w["id"] == world_id]
    if len(matches) != 1:
        raise ValueError(f"world id not frozen exactly once: {world_id}")
    spec = matches[0]
    generated = generate_world(spec)
    source = generated["source"]
    frame, bridge = generated["frame"], generated["bridge"]

    base = {
        "schema": "JANUS/TRUMP/R13/UNSEEN_INTERFACE_GENERALIZATION/WORLD_RESULT/v1.0",
        "created_date": "2026-09-02",
        "world_id": world_id,
        "source": source,
        "candidate_compiler": {
            "module": "janus_trump_r12b_forbidden_pattern_quotient_compiler",
            "width_cap": r12b.WIDTH_CAP,
            "firewall": r12b.candidate_firewall(),
            "logic_modified_by_r13": False,
        },
        "P_VS_NP": "OPEN",
    }

    if source["frame_type"] != "GENERAL_CNF":
        return {**base, "verdict": "BLOCKED_WORLD_NOT_GENERAL_CNF", "candidate_ran": False,
                "witness_ran": False, "reason": "FROZEN_WORLD_CLASSIFICATION_NOT_GENERAL_CNF__NO_SUBSTITUTION_ALLOWED"}

    candidate_started = time.time()
    candidate = r12b.saturate_forbidden_pattern_basis(frame, WALL_SECONDS, world_id)
    candidate_completed = time.time()
    replay = r12b.replay_proof(candidate, frame)
    candidate_peak_rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    proof_width_max = max((len(rec["clause"]) for rec in candidate["proof"]), default=0)
    candidate_record = {
        "started_unix": candidate_started,
        "completed_unix": candidate_completed,
        "status": candidate["status"],
        "reason": candidate["reason"],
        "stats": candidate["stats"],
        "proof_replay": replay,
        "proof_clause_width_max": proof_width_max,
        "no_created_state_width_gt4": proof_width_max <= 4,
        "peak_rss_kb_after_candidate": candidate_peak_rss_kb,
    }

    if candidate["status"] != "FIXED_POINT":
        return {**base, "verdict": "BLOCKED_RESOURCE_LIMIT", "candidate_ran": True,
                "candidate": candidate_record, "witness_ran": False,
                "scientific_firewall": {"witness_inaccessible_before_fixed_point": True,
                                        "resource_limit_not_negative_evidence": True}}

    local = local_candidate_basis(candidate, bridge)
    candidate_basis_sha = hashlib.sha256(json.dumps([list(c) for c in local], separators=(",", ":")).encode()).hexdigest()
    witness = post_candidate_witness(frame, bridge, local)
    final_peak_rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    witness["candidate_basis_sha256"] = candidate_basis_sha
    witness["peak_rss_kb_after_witness"] = final_peak_rss_kb

    firewall_ok = (
        base["candidate_compiler"]["firewall"]["pass"]
        and replay is True
        and proof_width_max <= 4
        and witness["witness_started_unix"] >= candidate_completed
    )
    exact = witness["allowed_set_exact"] and witness["prime_interface_exact"]
    if not firewall_ok:
        verdict = "FAIL_UNSOUND"
    elif exact:
        verdict = "PASS_EXACT_SCOPED"
    elif witness["false_positive_count"] or witness["false_negative_count"]:
        verdict = "OPEN_WIDTH_WITNESS"
    else:
        verdict = "OPEN_INTERFACE_STRUCTURE_MISMATCH"

    return {
        **base,
        "verdict": verdict,
        "candidate_ran": True,
        "candidate": candidate_record,
        "witness_ran": True,
        "witness": witness,
        "scientific_firewall": {
            "candidate_completed_before_witness_started": witness["witness_started_unix"] >= candidate_completed,
            "exact_witness_did_not_select_or_route_candidate": True,
            "no_width_escalation": proof_width_max <= 4,
            "compiler_firewall_pass": base["candidate_compiler"]["firewall"]["pass"],
            "proof_replay_pass": replay is True,
            "all_pass": firewall_ok,
        },
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = run_world(args.world)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "world_id": result["world_id"],
        "verdict": result["verdict"],
        "frame_type": result["source"]["frame_type"],
        "n": result["source"]["n_requested"],
        "frame_vars": result["source"]["frame_variable_count"],
        "frame_clauses": result["source"]["frame_clause_count"],
        "bridge_vars": result["source"]["bridge_variable_count"],
        "candidate_status": result.get("candidate", {}).get("status"),
        "seen": result.get("candidate", {}).get("stats", {}).get("seen_content_states"),
        "active": result.get("candidate", {}).get("stats", {}).get("active_basis_size"),
        "pairs": result.get("candidate", {}).get("stats", {}).get("pair_pivots_attempted"),
        "fp": result.get("witness", {}).get("false_positive_count"),
        "fn": result.get("witness", {}).get("false_negative_count"),
        "prime_exact": result.get("witness", {}).get("prime_interface_exact"),
        "P_VS_NP": "OPEN",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
