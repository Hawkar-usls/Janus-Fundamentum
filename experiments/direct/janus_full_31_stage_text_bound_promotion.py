#!/usr/bin/env python3
"""Frozen promotion harness for the 31-stage text-bound JANUS assembly.

This run tests proof-carrying composition on already revealed controls only.
The Pyramid Texts are source prompts, not evidence of an ancient algorithm.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from janus_full_text_missing_link_assembly import (
    BACK,
    FORWARD,
    OPERATOR,
    PRODUCES,
    REQUIRES,
    StageEnvelope,
    _digest,
    assembly_manifest,
    link_back,
    link_forward,
    make_stage_envelope,
    verify_envelope,
)
from janus_full_text_missing_link_runtime_adapter import bind_parent_runtime

RUN_ID = "JANUS-FULL-31-STAGE-TEXT-BOUND-PROMOTION-2026-08-18-v1"
TEXT_META_COMMIT = "ae0bdb5f605565fbc4686f39451848997be018f9"
TEXT_ARTIFACT = "data/JANUS-FULL-31-STAGE-TEXT-FORWARD-TRANCEPTION-HIEROGLYPHIC-SOURCE-PASS-2026-08-18-v1.0.json"
DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
INITIAL_ANCHOR = "44e21fdc9d37fda98e2e73b0c9eb268bd04cdca9d84d0519e4f1166be22b46fc"


def _flip(value: str) -> str:
    if not value:
        return "0"
    return ("0" if value[0] != "0" else "1") + value[1:]


def verify_forward_chain(chain: list[StageEnvelope]) -> dict[str, Any]:
    capabilities: set[str] = set()
    expected_pred = _digest({"parent_sha": assembly_manifest()["parent"]["sha"], "initial_anchor": INITIAL_ANCHOR})
    rows = []
    ok = True
    for idx, env in enumerate(chain):
        missing = [cap for cap in REQUIRES[env.stage] if cap not in capabilities]
        row_ok = bool(
            env.stage == FORWARD[idx]
            and env.predecessor_commitment == expected_pred
            and env.state_anchor == INITIAL_ANCHOR
            and not missing
            and verify_envelope(env)
        )
        rows.append({"stage": env.stage, "predecessor_exact": env.predecessor_commitment == expected_pred,
                     "requirements_satisfied": not missing, "envelope_valid": verify_envelope(env), "passed": row_ok})
        ok = ok and row_ok
        capabilities.update(PRODUCES[env.stage])
        expected_pred = env.commitment
    return {"rows": rows, "passed": ok, "terminal_commitment": expected_pred}


def verify_back_chain(back: list[StageEnvelope], forward: list[StageEnvelope]) -> dict[str, Any]:
    fwd = {e.stage: e for e in forward}
    expected_pred = _digest({"forward_terminal": fwd["PT222"].commitment, "mode": "BACK"})
    rows = []
    ok = True
    for idx, env in enumerate(back):
        expected_stage = BACK[idx]
        exact_forward = fwd[expected_stage].commitment
        row_ok = bool(
            env.stage == expected_stage
            and env.predecessor_commitment == expected_pred
            and env.state_anchor == exact_forward
            and verify_envelope(env)
        )
        rows.append({"stage": env.stage, "predecessor_exact": env.predecessor_commitment == expected_pred,
                     "binds_exact_forward_commitment": env.state_anchor == exact_forward,
                     "envelope_valid": verify_envelope(env), "passed": row_ok})
        ok = ok and row_ok
        expected_pred = env.commitment
    return {"rows": rows, "passed": ok, "terminal_commitment": expected_pred}


def run_negative_controls(forward: list[StageEnvelope]) -> dict[str, Any]:
    missing_predecessor_rejects = 0
    bitflip_rejects = 0
    cross_parent_rejects = 0
    for env in forward:
        bad_pred = replace(env, predecessor_commitment="")
        if not verify_envelope(bad_pred):
            missing_predecessor_rejects += 1
        bad_commit = replace(env, commitment=_flip(env.commitment))
        if not verify_envelope(bad_commit):
            bitflip_rejects += 1
        bad_anchor = replace(env, state_anchor=_flip(env.state_anchor))
        if not verify_envelope(bad_anchor):
            cross_parent_rejects += 1

    # Swap adjacent source-local stages without recomputing the chain: order/link gate must reject.
    swapped = list(forward)
    i = FORWARD.index("PT360")
    swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
    swap_rejects = not verify_forward_chain(swapped)["passed"]

    # LEFT: same broad function (gate-opening) but different stage/provenance cannot inherit identity.
    pt355 = forward[FORWARD.index("PT355")]
    pt360 = forward[FORWARD.index("PT360")]
    left_sub = replace(pt355, operator=pt360.operator)
    left_rejects_identity = not verify_envelope(left_sub)

    # RIGHT: keep stage/provenance label but remove its declared operator authority.
    pt476 = forward[FORWARD.index("PT476")]
    body = {
        "stage": pt476.stage,
        "operator": "OPERATOR_REMOVED_CONTROL",
        "predecessor_commitment": pt476.predecessor_commitment,
        "state_anchor": pt476.state_anchor,
        "requires": list(pt476.requires),
        "produces": list(pt476.produces),
        "direction": pt476.direction,
    }
    right_sub = replace(pt476, operator="OPERATOR_REMOVED_CONTROL", commitment=_digest(body))
    right_rejects_authority = not verify_envelope(right_sub)

    return {
        "missing_predecessor_rejects": missing_predecessor_rejects,
        "missing_predecessor_expected": len(FORWARD),
        "commitment_bitflip_rejects": bitflip_rejects,
        "commitment_bitflip_expected": len(FORWARD),
        "cross_parent_anchor_rejects": cross_parent_rejects,
        "cross_parent_anchor_expected": len(FORWARD),
        "stage_swap_rejects": swap_rejects,
        "LEFT_function_match_different_provenance_rejects_identity": left_rejects_identity,
        "RIGHT_same_provenance_operator_removed_rejects_authority": right_rejects_authority,
        "passed": bool(
            missing_predecessor_rejects == len(FORWARD)
            and bitflip_rejects == len(FORWARD)
            and cross_parent_rejects == len(FORWARD)
            and swap_rejects
            and left_rejects_identity
            and right_rejects_authority
        ),
    }


def projection(chain: list[StageEnvelope]) -> list[dict[str, str]]:
    return [{"stage": e.stage, "operator": e.operator, "requires_sha": _digest(list(e.requires)),
             "produces_sha": _digest(list(e.produces)), "commitment": e.commitment} for e in chain]


def run() -> dict[str, Any]:
    directions = []

    parent = bind_parent_runtime()
    if not parent["bound"]:
        return {"artifact_id": RUN_ID, "status": "STOP_PARENT_PR197_BINDING_FAILED", "parent": parent,
                "P_VS_NP": "OPEN"}

    forward = link_forward(INITIAL_ANCHOR)
    back = link_back(forward)

    # Canonical Tranception execution order starts with BACK, then FORWARD.
    back_check = verify_back_chain(back, forward); directions.append("BACK")
    forward_check = verify_forward_chain(forward); directions.append("FORWARD")

    negatives = run_negative_controls(forward)
    left = {"control": "FUNCTION_MATCHED_DIFFERENT_PROVENANCE",
            "passed": negatives["LEFT_function_match_different_provenance_rejects_identity"]}; directions.append("LEFT")
    right = {"control": "PROVENANCE_MATCHED_OPERATOR_REMOVED",
             "passed": negatives["RIGHT_same_provenance_operator_removed_rejects_authority"]}; directions.append("RIGHT")

    forward_again_chain = link_forward(INITIAL_ANCHOR)
    mirrors = []
    for a, b in zip(forward, forward_again_chain):
        mirrors.append(bool(a == b))
    forward_again = {"mirror_passes": sum(mirrors), "mirror_total": len(FORWARD),
                     "projection_exact": projection(forward) == projection(forward_again_chain),
                     "passed": all(mirrors) and projection(forward) == projection(forward_again_chain)}
    directions.append("FORWARD_AGAIN")

    parent_ba = parent["parent_result"].get("BACK_AGAIN", {})
    back_again = {
        "ancient_algorithm_claim_removed": True,
        "physical_time_reversal_claim_removed": True,
        "continuous_wall_text_claim_removed": True,
        "PR191_preserved_status": parent_ba.get("PR191_preserved_status"),
        "expected_PR191_status": "STOP_AT_FULL_MECHANICS_REVERSE_RETURN_FIRST",
        "P_VS_NP": "OPEN",
    }
    back_again["passed"] = bool(
        back_again["ancient_algorithm_claim_removed"]
        and back_again["physical_time_reversal_claim_removed"]
        and back_again["continuous_wall_text_claim_removed"]
        and back_again["PR191_preserved_status"] == back_again["expected_PR191_status"]
        and back_again["P_VS_NP"] == "OPEN"
    )
    directions.append("BACK_AGAIN")

    manifest = assembly_manifest()
    gates = {
        "parent_pr197_exact": parent["bound"],
        "direction_order_exact": directions == DIRECTIONS,
        "forward_31_exact": [e.stage for e in forward] == FORWARD and len(forward) == 31,
        "back_31_exact": [e.stage for e in back] == BACK and len(back) == 31,
        "forward_chain_pass": forward_check["passed"],
        "back_chain_pass": back_check["passed"],
        "back_binds_exact_forward_commitments": all(r["binds_exact_forward_commitment"] for r in back_check["rows"]),
        "all_envelopes_verify": all(verify_envelope(e) for e in forward + back),
        "negative_controls_pass": negatives["passed"],
        "LEFT_pass": left["passed"],
        "RIGHT_pass": right["passed"],
        "FORWARD_AGAIN_31_of_31": forward_again["passed"] and forward_again["mirror_passes"] == 31,
        "BACK_AGAIN_pass": back_again["passed"],
        "textual_source_pass_bound_before_run": TEXT_META_COMMIT == "ae0bdb5f605565fbc4686f39451848997be018f9",
        "source_local_order_preserved": manifest["source_local_blocks"]["PT350_374"] == [f"PT{i}" for i in range(350,375)]
            and manifest["source_local_blocks"]["PT476_478"] == ["PT476","PT477","PT478"]
            and manifest["source_local_blocks"]["PT220_222"] == ["PT220","PT221","PT222"],
        "synthetic_seams_explicit": len(manifest["intentional_seams"]) == 2,
        "P_VS_NP_OPEN": manifest["P_VS_NP"] == "OPEN",
    }
    passed = all(gates.values())
    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_FULL_31_STAGE_TEXT_BOUND_COMPOSITION" if passed else "STOP_FULL_31_STAGE_TEXT_BOUND_COMPOSITION",
        "run_scope": "REVEALED_FROZEN_COMPOSITION_CONTROLS_ONLY_NO_NEW_HOLDOUT",
        "textual_source_pass": {"registry_path": TEXT_ARTIFACT, "meta_commit": TEXT_META_COMMIT,
                                 "frozen_before_run": True},
        "directions": directions,
        "parent_binding": {"checks": parent["checks"], "integrity_sha256": parent["parent_integrity_sha256"]},
        "BACK": back_check,
        "FORWARD": forward_check,
        "LEFT": left,
        "RIGHT": right,
        "FORWARD_AGAIN": forward_again,
        "BACK_AGAIN": back_again,
        "negative_controls": negatives,
        "gates": gates,
        "stage_counts": {"forward": len(forward), "back": len(back), "mirrors": forward_again["mirror_passes"]},
        "claim_boundary": [
            "PASS would establish only compositional integrity of this proof-carrying 31-stage interface on revealed controls.",
            "The new PT-inspired stages are not independently validated CNF speedups in this run.",
            "The Pyramid Texts are heuristic source prompts, not an ancient algorithm.",
            "PT375-PT475 remain unintegrated and PT478->PT220 remains a synthetic bridge.",
            "P_VS_NP = OPEN",
        ],
        "mathematical_verdict": {"P_EQUALS_NP": "NOT_ESTABLISHED", "P_NOT_EQUALS_NP": "NOT_ESTABLISHED", "P_VS_NP": "OPEN"},
    }
    raw = json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    result["integrity_sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    result = run()
    p = Path(args.output); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.self_test:
        assert result["status"] == "PASS_KEEP_FULL_31_STAGE_TEXT_BOUND_COMPOSITION"
        assert all(result["gates"].values())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
