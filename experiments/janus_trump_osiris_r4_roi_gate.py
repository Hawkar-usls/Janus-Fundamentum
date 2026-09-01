#!/usr/bin/env python3
"""R4: frozen ROI gate for the Osiris double-spiral lane.

Training evidence is frozen from R3A/R3B: 108 natural residuals, 0 cases where
R3 double-spiral charged work beat the exact baseline, despite many exact meets.
Therefore the preregistered R4 predictor is deliberately conservative:
ABSTAIN_TO_EXACT on every holdout state.  The expensive spiral is executed only
AFTER the route decision, in shadow, to audit whether the frozen predictor
skipped any genuinely profitable case.

The holdout formulas are imported from pre-existing direct experiments that were
not R3 training families.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from janus_trump_p_vs_np_direct_challenge_r0 import canon, dpll, variables
from janus_trump_osiris_r3_natural_residuals import (
    exact_search_witness,
    graph_signature,
    seal_pretruth_witness,
    verify_sat,
)
from janus_trump_osiris_r3b_proof_carrying_recovery import (
    _root_candidate_states,
    r3b_candidate,
)
from direct.janus_tear_marginal_collision import SAT_FORMULA, UNSAT_FORMULA
from direct.janus_tear_nonlinear_affine_masking import relation_cnf
from direct.janus_tear_maj3_lift_encoding_match import direct_local_relation_cnf

R4_RULE_ID = "TRUMP_R4_CONSERVATIVE_ROI_GATE_v1"
R4_TRAINING_ROWS = 108
R4_TRAINING_PROFITABLE = 0
R4_TRAINING_MIN_CANDIDATE_TO_BASELINE_RATIO = 2.75


@dataclass(frozen=True)
class RootWorkload:
    family: str
    name: str
    formula: tuple[tuple[int, ...], ...]
    source_path: str


def frozen_roi_prediction(signature: dict) -> str:
    # Frozen before holdout. No truth, family label, or holdout outcome enters.
    assert R4_TRAINING_PROFITABLE == 0
    assert signature["variables"] >= 0
    return "ABSTAIN_TO_EXACT"


def holdout_roots() -> list[RootWorkload]:
    roots: list[RootWorkload] = []
    roots += [
        RootWorkload("TEAR_MARGINAL_COLLISION", "SAT", canon(SAT_FORMULA), "experiments/direct/janus_tear_marginal_collision.py"),
        RootWorkload("TEAR_MARGINAL_COLLISION", "UNSAT", canon(UNSAT_FORMULA), "experiments/direct/janus_tear_marginal_collision.py"),
    ]
    z = canon(relation_cnf(0))
    o = canon(relation_cnf(1))
    roots += [
        RootWorkload("TEAR_NONLINEAR_AFFINE_MASKING", "RELATION_ZERO", z, "experiments/direct/janus_tear_nonlinear_affine_masking.py"),
        RootWorkload("TEAR_NONLINEAR_AFFINE_MASKING", "RELATION_ONE", o, "experiments/direct/janus_tear_nonlinear_affine_masking.py"),
        RootWorkload("TEAR_NONLINEAR_AFFINE_MASKING", "MASKED_CONTRADICTION", canon(z + o), "experiments/direct/janus_tear_nonlinear_affine_masking.py"),
    ]
    for degree in (1, 2):
        c0 = canon(direct_local_relation_cnf(degree, 0))
        c1 = canon(direct_local_relation_cnf(degree, 1))
        roots += [
            RootWorkload("TEAR_MAJ3_LIFT", f"D{degree}_C0", c0, "experiments/direct/janus_tear_maj3_lift_encoding_match.py"),
            RootWorkload("TEAR_MAJ3_LIFT", f"D{degree}_C1", c1, "experiments/direct/janus_tear_maj3_lift_encoding_match.py"),
            RootWorkload("TEAR_MAJ3_LIFT", f"D{degree}_CONTRADICTION", canon(c0 + c1), "experiments/direct/janus_tear_maj3_lift_encoding_match.py"),
        ]
    return roots


def collect_holdout_residuals() -> list[dict]:
    rows: list[dict] = []
    for idx, root in enumerate(holdout_roots()):
        candidates = _root_candidate_states(idx, root.family, len(variables(root.formula)), 0, root.formula)
        if not candidates:
            # Tiny roots can close too quickly to yield an intermediate state.
            # The root itself is still a solver-native state and is sealed pretruth.
            sig = graph_signature(root.formula)
            source = {
                "root_index": idx,
                "family": root.family,
                "workload_name": root.name,
                "source_path": root.source_path,
                "probe_kind": "ROOT_STATE",
            }
            witness = seal_pretruth_witness(source, root.formula, sig, "R4_PENDING_ROI_DECISION")
            candidates = [{"source": source, "cnf": root.formula, "pretruth_witness": witness}]
        for row in candidates:
            row = dict(row)
            src = dict(row["source"])
            src["workload_name"] = root.name
            src["source_path"] = root.source_path
            row["source"] = src
            # Replace R2 route prediction with the R4 decision while truth is null.
            w = dict(row["pretruth_witness"])
            sig = w["signature"]
            decision = frozen_roi_prediction(sig)
            w["frozen_rule_id"] = R4_RULE_ID
            w["route_prediction"] = decision
            w["truth"] = None
            w["candidate_result"] = None
            w["verification_result"] = None
            row["pretruth_witness"] = w
            rows.append(row)
    return rows


def proof_carrying_exact(cnf) -> dict:
    terminal, witness, nodes = exact_search_witness(canon(cnf))
    if terminal == "SAT":
        assert witness is not None and verify_sat(canon(cnf), witness)
    return {"terminal": terminal, "witness": witness, "work": nodes}


def evaluate_row(row: dict) -> dict:
    f = canon(row["cnf"])
    w = row["pretruth_witness"]
    assert w["truth"] is None
    assert w["route_prediction"] == "ABSTAIN_TO_EXACT"

    # Primary guarded route: no spiral is permitted here.
    guarded = proof_carrying_exact(f)
    independent = dpll(f)
    assert independent["status"] == "EXACT"
    baseline_terminal = "SAT" if independent["sat"] else "UNSAT"
    terminal_match = guarded["terminal"] == baseline_terminal
    replay = guarded["terminal"] != "SAT" or verify_sat(f, guarded["witness"])

    # Counterfactual audit only after the frozen route has been executed.
    shadow_w = dict(w)
    shadow_w["route_prediction"] = "TRY_EXACT_MEET"
    shadow = r3b_candidate(f, shadow_w).as_dict()
    shadow_terminal_match = shadow["terminal"] == baseline_terminal
    shadow_replay = shadow["terminal"] != "SAT" or verify_sat(f, shadow["witness"])

    guard_cost = int(w["signature"]["signature_ops"]) + int(guarded["work"])
    shadow_cost = int(shadow["work"]["charged_abstract_ops"])
    shadow_profitable = shadow_cost < guard_cost

    return {
        "source": row["source"],
        "pretruth_witness": w,
        "guarded_route": guarded,
        "independent_exact_verifier": independent,
        "shadow_spiral": shadow,
        "checks": {
            "decision_pretruth": True,
            "guarded_terminal_match": terminal_match,
            "guarded_sat_replay": replay,
            "shadow_terminal_match": shadow_terminal_match,
            "shadow_sat_replay": shadow_replay,
            "shadow_profitable_vs_guarded": shadow_profitable,
        },
        "work": {
            "signature_ops": int(w["signature"]["signature_ops"]),
            "guarded_exact_work": int(guarded["work"]),
            "guarded_total_ops": guard_cost,
            "shadow_spiral_charged_ops": shadow_cost,
            "ops_avoided_by_abstention": shadow_cost - guard_cost,
        },
    }
