#!/usr/bin/env python3
"""R19 fresh unseen world selector.

Selection is deliberately adversarial on structural burden, but blind to both
candidate behavior and semantic truth.  The ranking rule was preregistered before
any R19 world generation.  This module imports no R18 candidate code and no SAT
solver.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import random
from pathlib import Path

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r8a_unseen_natural_holdout as r8a
import janus_trump_r9_reference_frame_difference_kernel as r9

PARENT_R18B = "08b5b204d01f4318ed8a33646635ee57e315a538"
REPLICATES = 48
CELLS = tuple((suite, n) for n in (56, 64, 72, 80) for suite in ("PLANTED", "UNSAT_CORE"))
R16_EXPOSED_FRAMES = {
    "1c9a589f5b830a5863ecec2d104d4a041f5207e10a3ea4dd81656a4f9062071c",
    "00f3191f14905031fafc087d6c169bc36c8605abfdddc3c7d7a336744e73799e",
    "053688f5c82eb94e294e03ff1af78c4abc69195d6fca7638e6c531054fb5cdac",
    "13ba661067d7bdc389eeff233fc10318ad1e584ecf0d101b9071a3d21cb8ac21",
    "1b21e911ee69fbcdaadbc325eb6a78a6dfaa0c87201a425f502cd7caa1bc8a06",
    "179920edae423db6f588ad74ef259e09d965026dd9d0cb08ccd93ec4a445f591",
    "1093568a55ccfd4991b48002489ce564d3754cf406c361193ef22363b576bce1",
    "1298d8cbbba127ec91d3f004600e9c40b8a49f243c74212d71150ad219ce0fbe",
}


def derive_spec(suite: str, n: int, rep: int) -> dict:
    s = f"R19|R18B={PARENT_R18B}|suite={suite}|n={n}|rep={rep}"
    digest = hashlib.sha256(s.encode()).digest()
    seed = int.from_bytes(digest[:8], "big") % (2 ** 31)
    branch = bool(digest[8] & 1)
    return {
        "suite": suite,
        "n": int(n),
        "m": round(4.26 * int(n)),
        "k": 3,
        "rep": int(rep),
        "derivation_string": s,
        "seed": seed,
        "branch_value": branch,
    }


def structural_world(spec: dict) -> dict:
    sat_core = r8a.load_legacy_sat_core()
    rng = random.Random(int(spec["seed"]))
    if spec["suite"] == "PLANTED":
        inst = sat_core.gen_planted(spec["n"], spec["m"], spec["k"], rng)
    elif spec["suite"] == "UNSAT_CORE":
        inst = sat_core.gen_unsat_core(spec["n"], spec["m"], spec["k"], rng)
    else:
        raise ValueError(spec["suite"])
    root = direct.canon(inst.clauses)
    order, _ = direct.occurrence_order(root)
    if not order:
        return {**spec, "eligible": False, "reason": "NO_PIVOT"}
    pivot = int(order[0])
    fd = r9.restriction_frame_delta(root, pivot, bool(spec["branch_value"]))
    frame = tuple(fd["frame"])
    bridge = tuple(fd["active_bridge_vars"])
    frame_type = r9.classify_cnf(frame)
    frame_hash = fd["frame_sha256"]
    frame_vars = len({abs(l) for c in frame for l in c})
    internal_vars = frame_vars - len(bridge)
    stress_score = len(frame) * internal_vars
    eligible = (
        frame_type == "GENERAL_CNF"
        and 6 <= len(bridge) <= 16
        and frame_hash not in R16_EXPOSED_FRAMES
    )
    return {
        **spec,
        "eligible": eligible,
        "reason": "ELIGIBLE" if eligible else "STRUCTURAL_FILTER",
        "root_sha256": r8a.digest(root),
        "pivot": pivot,
        "frame_sha256": frame_hash,
        "frame_type": frame_type,
        "frame_variable_count": frame_vars,
        "frame_clause_count": len(frame),
        "bridge_vars": list(bridge),
        "bridge_variable_count": len(bridge),
        "internal_variable_count": internal_vars,
        "structural_stress_score": stress_score,
        "delta_sha256": fd["delta_sha256"],
    }


def select_worlds() -> dict:
    selected = []
    cell_audit = []
    blocked = []
    for cell_index, (suite, n) in enumerate(CELLS, start=1):
        pool = [structural_world(derive_spec(suite, n, rep)) for rep in range(REPLICATES)]
        eligible = [x for x in pool if x["eligible"]]
        eligible.sort(key=lambda x: (
            -int(x["structural_stress_score"]),
            -int(x["frame_clause_count"]),
            -int(x["internal_variable_count"]),
            x["frame_sha256"],
        ))
        audit = {
            "suite": suite,
            "n": n,
            "pool_size": len(pool),
            "eligible_count": len(eligible),
            "bridge_sizes_in_eligible_pool": sorted({x["bridge_variable_count"] for x in eligible}),
            "maximum_structural_stress_score": max((x["structural_stress_score"] for x in eligible), default=None),
        }
        if not eligible:
            blocked.append({"suite":suite,"n":n,"reason":"NO_ELIGIBLE_WORLD_UNDER_FROZEN_SELECTOR"})
            cell_audit.append(audit)
            continue
        chosen = dict(eligible[0])
        chosen["id"] = f"R19-W{cell_index:02d}"
        chosen["selection_rank_within_cell"] = 1
        chosen.pop("eligible", None); chosen.pop("reason", None)
        selected.append(chosen)
        audit.update({
            "selected_id": chosen["id"],
            "selected_rep": chosen["rep"],
            "selected_frame_sha256": chosen["frame_sha256"],
            "selected_bridge_size": chosen["bridge_variable_count"],
            "selected_internal_variables": chosen["internal_variable_count"],
            "selected_frame_clauses": chosen["frame_clause_count"],
            "selected_structural_stress_score": chosen["structural_stress_score"],
        })
        cell_audit.append(audit)
    firewall = selector_firewall()
    status = "R19_SELECTOR_PASS" if len(selected) == len(CELLS) and not blocked and firewall["pass"] else "R19_SELECTOR_BLOCKED"
    return {
        "schema":"JANUS/TRUMP/R19/FRESH_UNSEEN_DAG_HOLDOUT/WORLD_SELECTION_RESULT/v1.0",
        "created_date":"2026-09-02",
        "status":status,
        "parent_R18B_result_summary_commit":PARENT_R18B,
        "selector_firewall":firewall,
        "selected_world_count":len(selected),
        "selected_worlds":selected,
        "cell_audit":cell_audit,
        "blocked_cells":blocked,
        "truth_accessed":False,
        "candidate_accessed":False,
        "semantic_witness_accessed":False,
        "selection_is_adversarial_on_frozen_structural_score":True,
        "seal":"THE_NEW_EXAM_WAS_CHOSEN_TO_BE_STRUCTURALLY_HARD_WITHOUT_READING_THE_MACHINE_OR_THE_TRUTH",
        "P_VS_NP":"OPEN",
    }


def selector_firewall() -> dict:
    src = "\n".join(inspect.getsource(f) for f in (derive_spec, structural_world, select_worlds))
    forbidden = [
        "janus_trump_r18", "candidate_compile", "Solver(", "dpll(",
        "allowed_masks", "truth_table", "shadow_exact_interface", "exact_cnf_geometry",
    ]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "forbidden_hits": hits}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args()
    out=select_worlds()
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":out["status"],
        "selected_world_count":out["selected_world_count"],
        "selected":[{"id":w["id"],"suite":w["suite"],"n":w["n"],"rep":w["rep"],"frame":w["frame_sha256"],"bridge":w["bridge_variable_count"],"internal":w["internal_variable_count"],"clauses":w["frame_clause_count"],"stress":w["structural_stress_score"]} for w in out["selected_worlds"]],
        "firewall":out["selector_firewall"],
        "truth_accessed":out["truth_accessed"],
        "candidate_accessed":out["candidate_accessed"],
        "P_VS_NP":"OPEN",
    },indent=2,sort_keys=True))
    return 0 if out["status"]=="R19_SELECTOR_PASS" else 2


if __name__=="__main__": raise SystemExit(main())
