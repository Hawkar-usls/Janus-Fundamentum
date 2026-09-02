#!/usr/bin/env python3
"""R16 prospective world selector. Structural selection only; no truth or candidate access."""
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

PARENT = "49d3ccc412f489efc0542bb991f138fe498fc669"
REPLICATES = 24
CELLS = tuple((suite, n) for n in (24, 32, 40, 48) for suite in ("PLANTED", "UNSAT_CORE"))
EXPOSED = {
    "3777d9c56dae0be077e2141cb4821250f582261812235647528c5cc5a21462b8",
    "9f03fef66a0b9e4968851ed72d4f51bdf8abdac400c0b81f48d4f0d5c1844cf6",
    "fbb0eb0160ed4d4e3c4e1b645471c0cc611ea9a22f776cc97ea9e0d28a0af747",
    "f3b380ed8e0d288079a1e6652c31be5588b71a4bf20a208d17fe03d1da8e08b7",
    "84fa0fbdd127b1c73f3c8ef6820a0d0cdf154093750ed9c600289fce4b6aae88",
    "49ae562a287b2ab6c92152d5fe61a0d1a0faeee23c9cb8e27a881ef01745e98b",
}


def derive_spec(suite: str, n: int, rep: int) -> dict:
    s = f"R16|R15F={PARENT}|suite={suite}|n={n}|rep={rep}"
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
    eligible = frame_type == "GENERAL_CNF" and 6 <= len(bridge) <= 16 and frame_hash not in EXPOSED
    return {
        **spec,
        "eligible": eligible,
        "reason": "ELIGIBLE" if eligible else "STRUCTURAL_FILTER",
        "root_sha256": r8a.digest(root),
        "pivot": pivot,
        "frame_sha256": frame_hash,
        "frame_type": frame_type,
        "frame_variable_count": len({abs(l) for c in frame for l in c}),
        "frame_clause_count": len(frame),
        "bridge_vars": list(bridge),
        "bridge_variable_count": len(bridge),
        "delta_sha256": fd["delta_sha256"],
    }


def selector_firewall() -> dict:
    src = "\n".join(inspect.getsource(f) for f in (derive_spec, structural_world, select_worlds))
    forbidden = ["dpll(", "shadow_exact_interface", "exact_cnf_geometry", "compile_observed(", "allowed_masks", "truth_table"]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "forbidden_hits": hits}


def select_worlds() -> dict:
    selected = []
    cell_audit = []
    blocked = []
    for cell_index, (suite, n) in enumerate(CELLS, start=1):
        pool = [structural_world(derive_spec(suite, n, rep)) for rep in range(REPLICATES)]
        eligible = [x for x in pool if x["eligible"]]
        eligible.sort(key=lambda x: (x["frame_sha256"], x["seed"], x["branch_value"]))
        audit = {
            "suite": suite,
            "n": n,
            "pool_size": len(pool),
            "eligible_count": len(eligible),
            "bridge_sizes_in_eligible_pool": sorted({x["bridge_variable_count"] for x in eligible}),
        }
        if not eligible:
            blocked.append({"suite": suite, "n": n, "reason": "NO_ELIGIBLE_WORLD_UNDER_FROZEN_SELECTOR"})
            cell_audit.append(audit)
            continue
        chosen = dict(eligible[0])
        chosen["id"] = f"R16-W{cell_index:02d}"
        chosen["selection_rank_within_cell"] = 1
        chosen.pop("eligible", None); chosen.pop("reason", None)
        selected.append(chosen)
        audit["selected_id"] = chosen["id"]
        audit["selected_frame_sha256"] = chosen["frame_sha256"]
        audit["selected_bridge_size"] = chosen["bridge_variable_count"]
        cell_audit.append(audit)
    firewall = selector_firewall()
    status = "SELECTOR_PASS" if len(selected) == len(CELLS) and not blocked and firewall["pass"] else "SELECTOR_BLOCKED"
    return {
        "schema": "JANUS/TRUMP/R16/PROSPECTIVE_UNSEEN_FACTORED_BRIDGE_HOLDOUT/WORLD_SELECTION_RESULT/v1.0",
        "created_date": "2026-09-02",
        "status": status,
        "parent_R15F_result_summary_commit": PARENT,
        "selector_firewall": firewall,
        "selected_world_count": len(selected),
        "selected_worlds": selected,
        "cell_audit": cell_audit,
        "blocked_cells": blocked,
        "truth_accessed": False,
        "candidate_accessed": False,
        "seal": "THE_EXAM_WAS_PICKED_BEFORE_ANY_ANSWER_WAS_READ",
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    out = select_worlds()
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": out["status"],
        "selected_world_count": out["selected_world_count"],
        "selected": [
            {"id": w["id"], "suite": w["suite"], "n": w["n"], "seed": w["seed"], "branch": w["branch_value"], "frame": w["frame_sha256"], "bridge": w["bridge_variable_count"]}
            for w in out["selected_worlds"]
        ],
        "firewall": out["selector_firewall"],
        "P_VS_NP": "OPEN",
    }, indent=2, sort_keys=True))
    return 0 if out["status"] == "SELECTOR_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
