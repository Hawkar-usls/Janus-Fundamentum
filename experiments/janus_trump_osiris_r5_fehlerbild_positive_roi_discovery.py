#!/usr/bin/env python3
"""R5 Fehlerbild discovery kernel for TRUMP/Osiris.

The experiment places two proof-carrying witnesses of the same canonical CNF
side by side:

    EXACT(F)  |  SPIRAL(F)

and records the measurable difference

    DELTA_W(F) = W_EXACT(F) - W_SPIRAL(F).

R5 is discovery, not promotion.  It may identify positive-ROI examples, but no
routing authority changes here.  Every separator is selected without SAT/UNSAT
truth and every terminal is checked against the existing exact DPLL; SAT models
must replay on the same canonical CNF.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from typing import Optional

from janus_trump_p_vs_np_direct_challenge_r0 import (
    canon,
    corpus,
    dpll,
    restrict_cnf,
    variables,
)
from janus_trump_osiris_r3_natural_residuals import (
    _components_without,
    _greedy_split,
    build_primal_graph,
    exact_search_witness,
    formula_digest,
    formula_status,
    graph_signature,
    occurrence_pivot,
    split_by_separator,
    unit_close,
    verify_sat,
)
from janus_trump_osiris_r3b_proof_carrying_recovery import (
    probe_family_stratified_residuals,
    r3b_candidate,
)
from janus_trump_osiris_r4_roi_gate import collect_holdout_residuals

R5_RULE_ID = "TRUMP_R5_FEHLERBILD_EXACT_VS_SPIRAL_DISCOVERY_v1"
R5_MAX_VARIABLES = 14
R5_DEEP_PROBE_MAX_DEPTH = 4
R5_DEEP_PROBE_CAP = 160


@dataclass
class R5Candidate:
    terminal: str
    witness: Optional[dict[int, bool]]
    mode: str
    separator: list[int]
    structural_ops: int
    boundary_attempts: int
    wing_nodes: int
    fallback_nodes: int

    @property
    def charged_ops_excluding_pretruth_signature(self) -> int:
        return self.structural_ops + self.boundary_attempts + self.wing_nodes + self.fallback_nodes

    def as_dict(self) -> dict:
        return {
            "terminal": self.terminal,
            "witness": None if self.witness is None else {str(k): bool(v) for k, v in sorted(self.witness.items())},
            "mode": self.mode,
            "separator": self.separator,
            "work": {
                "structural_ops_after_signature": self.structural_ops,
                "boundary_attempts": self.boundary_attempts,
                "wing_nodes": self.wing_nodes,
                "fallback_nodes": self.fallback_nodes,
                "charged_ops_excluding_pretruth_signature": self.charged_ops_excluding_pretruth_signature,
            },
        }


def _r5_witness(source: dict, cnf) -> dict:
    f = canon(cnf)
    sig = graph_signature(f)
    payload = {
        "schema": "JANUS/TRUMP/R5/FEHLERBILD-PRETRUTH-WITNESS/v1.0",
        "source": source,
        "formula_sha256": formula_digest(f),
        "signature": sig,
        "frozen_rule_id": R5_RULE_ID,
        "comparison": "EXACT_VS_SPIRAL",
        "truth": None,
        "exact_result": None,
        "spiral_result": None,
        "delta_w": None,
    }
    digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {**payload, "witness_sha256": digest}


def _solve_exact_split(cnf, sep: set[int], left: set[int], right: set[int], structural_ops: int, mode: str) -> R5Candidate:
    f = canon(cnf)
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
            return R5Candidate(
                terminal="SAT",
                witness=combined,
                mode=mode,
                separator=sep_order,
                structural_ops=structural_ops,
                boundary_attempts=attempts,
                wing_nodes=wing_nodes,
                fallback_nodes=0,
            )

    return R5Candidate(
        terminal="UNSAT",
        witness=None,
        mode=mode,
        separator=sep_order,
        structural_ops=structural_ops,
        boundary_attempts=attempts,
        wing_nodes=wing_nodes,
        fallback_nodes=0,
    )


def r5_spiral_candidate(cnf, pretruth_witness: dict) -> R5Candidate:
    """Frozen structural spiral policy.

    Priority is fixed before outcomes:
      1. empty separator if the primal graph is already disconnected;
      2. best balanced single articulation separator;
      3. legacy R3B size-2 exact-meet attempt;
      4. proof-carrying exact fallback inside legacy R3B.
    """
    f = canon(cnf)
    assert pretruth_witness["truth"] is None

    graph, graph_ops = build_primal_graph(f)
    comps0, comp_ops = _components_without(graph, set())
    structural_ops = graph_ops + comp_ops
    if len(comps0) >= 2:
        split = _greedy_split(comps0)
        if split is not None:
            left, right = split
            return _solve_exact_split(
                f,
                set(),
                left,
                right,
                structural_ops,
                "R5_EMPTY_SEPARATOR_DOUBLE_SPIRAL",
            )

    candidates: list[tuple[tuple[int, int], int, set[int], set[int]]] = []
    for v in sorted(graph):
        comps, ops = _components_without(graph, {v})
        structural_ops += ops
        if len(comps) < 2:
            continue
        split = _greedy_split(comps)
        if split is None:
            continue
        left, right = split
        try:
            split_by_separator(f, {v}, left, right)
        except ValueError:
            continue
        balance = min(len(left), len(right))
        # maximize balance, then prefer the lower stable variable id
        candidates.append(((-balance, v), v, left, right))

    if candidates:
        candidates.sort(key=lambda row: row[0])
        _, v, left, right = candidates[0]
        return _solve_exact_split(
            f,
            {v},
            left,
            right,
            structural_ops,
            "R5_ARTICULATION_DOUBLE_SPIRAL",
        )

    # No zero/one separator: preserve the already-existing exact R3B size-2
    # mechanism.  Its complete charged work is added; nothing is hidden.
    legacy_w = dict(pretruth_witness)
    legacy_w["route_prediction"] = "TRY_EXACT_MEET"
    legacy = r3b_candidate(f, legacy_w)
    terminal = legacy.terminal
    witness = legacy.witness
    if terminal == "SAT":
        assert witness is not None and verify_sat(f, witness)
    return R5Candidate(
        terminal=terminal,
        witness=witness,
        mode="R5_LEGACY_R3B_SIZE2_OR_FALLBACK__" + legacy.mode,
        separator=[] if legacy.separator is None else list(legacy.separator),
        structural_ops=structural_ops + legacy.structural_ops + legacy.proposals_tested,
        boundary_attempts=legacy.boundary_attempts,
        wing_nodes=legacy.wing_nodes,
        fallback_nodes=legacy.fallback_work,
    )


def _root_rows() -> list[dict]:
    out = []
    for root_index, (family, size, variant, root) in enumerate(corpus()):
        f = canon(root)
        n = len(variables(f))
        if 3 <= n <= R5_MAX_VARIABLES:
            source = {
                "arena": "R0_ROOT",
                "root_index": root_index,
                "family": family,
                "size": size,
                "variant": variant,
                "probe_kind": "ROOT_STATE",
            }
            out.append({"source": source, "cnf": f, "pretruth_witness": _r5_witness(source, f)})
    return out


def _deep_probe_rows() -> list[dict]:
    """Deterministic truth-blind solver-native residual probe."""
    out: list[dict] = []
    seen: set[str] = set()
    for root_index, (family, size, variant, root) in enumerate(corpus()):
        start = unit_close(canon(root))
        frontier = [(start, 0, "ROOT")]
        while frontier and len(out) < R5_DEEP_PROBE_CAP:
            state, depth, path = frontier.pop(0)
            if not state or () in state:
                continue
            dg = formula_digest(state)
            n = len(variables(state))
            if depth > 0 and 3 <= n <= R5_MAX_VARIABLES and dg not in seen:
                seen.add(dg)
                source = {
                    "arena": "R0_DEEP_PRETRUTH_RESIDUAL",
                    "root_index": root_index,
                    "family": family,
                    "size": size,
                    "variant": variant,
                    "probe_depth": depth,
                    "probe_path": path,
                }
                out.append({"source": source, "cnf": state, "pretruth_witness": _r5_witness(source, state)})
                if len(out) >= R5_DEEP_PROBE_CAP:
                    break
            if depth >= R5_DEEP_PROBE_MAX_DEPTH:
                continue
            pivot = occurrence_pivot(state)
            if pivot is None:
                continue
            for value in (False, True):
                child = unit_close(restrict_cnf(state, pivot, value))
                if not child or () in child:
                    continue
                frontier.append((child, depth + 1, f"{path}/{pivot}={'T' if value else 'F'}"))
        if len(out) >= R5_DEEP_PROBE_CAP:
            break
    return out


def _reseal_existing(rows: list[dict], arena: str) -> list[dict]:
    out = []
    for row in rows:
        f = canon(row["cnf"])
        if not (3 <= len(variables(f)) <= R5_MAX_VARIABLES):
            continue
        source = dict(row["source"])
        source["arena"] = arena
        out.append({"source": source, "cnf": f, "pretruth_witness": _r5_witness(source, f)})
    return out


def discovery_rows() -> list[dict]:
    candidates = []
    candidates.extend(_root_rows())
    candidates.extend(_deep_probe_rows())
    candidates.extend(_reseal_existing(probe_family_stratified_residuals(), "R3B_EXPOSED_DISCOVERY"))
    candidates.extend(_reseal_existing(collect_holdout_residuals(), "R4_EXPOSED_DISCOVERY"))

    out = []
    seen = set()
    for row in candidates:
        dg = formula_digest(row["cnf"])
        if dg in seen:
            continue
        seen.add(dg)
        out.append(row)
    return out


def evaluate_row(row: dict) -> dict:
    f = canon(row["cnf"])
    w = row["pretruth_witness"]
    assert w["truth"] is None and w["exact_result"] is None and w["spiral_result"] is None

    exact_terminal, exact_witness, exact_nodes = exact_search_witness(f)
    exact_replay = exact_terminal != "SAT" or verify_sat(f, exact_witness)

    spiral = r5_spiral_candidate(f, w)
    spiral_replay = spiral.terminal != "SAT" or verify_sat(f, spiral.witness)

    oracle = dpll(f)
    oracle_exact = oracle["status"] == "EXACT"
    oracle_terminal = None if not oracle_exact else ("SAT" if oracle["sat"] else "UNSAT")

    terminal_agreement = exact_terminal == spiral.terminal
    oracle_agreement = oracle_exact and exact_terminal == oracle_terminal and spiral.terminal == oracle_terminal

    signature_ops = int(w["signature"]["signature_ops"])
    exact_total = signature_ops + int(exact_nodes)
    spiral_total = signature_ops + spiral.charged_ops_excluding_pretruth_signature
    delta_w = exact_total - spiral_total
    positive = bool(terminal_agreement and oracle_agreement and exact_replay and spiral_replay and delta_w > 0)

    return {
        "source": row["source"],
        "pretruth_witness": w,
        "exact_witness_lane": {
            "terminal": exact_terminal,
            "witness": None if exact_witness is None else {str(k): bool(v) for k, v in sorted(exact_witness.items())},
            "search_nodes": exact_nodes,
            "sat_replay": exact_replay,
        },
        "spiral_witness_lane": spiral.as_dict(),
        "independent_exact_verifier": oracle,
        "checks": {
            "decision_pretruth": True,
            "terminal_agreement": terminal_agreement,
            "oracle_agreement": oracle_agreement,
            "exact_sat_replay": exact_replay,
            "spiral_sat_replay": spiral_replay,
        },
        "fehlerbild": {
            "signature_ops_paid_by_both": signature_ops,
            "exact_total_ops": exact_total,
            "spiral_total_ops": spiral_total,
            "delta_w_exact_minus_spiral": delta_w,
            "positive_roi": positive,
        },
    }


def run_discovery() -> dict:
    rows = discovery_rows()
    evaluated = [evaluate_row(row) for row in rows]
    exact_ok = all(r["checks"]["oracle_agreement"] and r["checks"]["terminal_agreement"] for r in evaluated)
    replay_ok = all(r["checks"]["exact_sat_replay"] and r["checks"]["spiral_sat_replay"] for r in evaluated)
    positives = [r for r in evaluated if r["fehlerbild"]["positive_roi"]]
    mode_counts = Counter(r["spiral_witness_lane"]["mode"] for r in evaluated)
    families = sorted({r["source"].get("family", "UNKNOWN") for r in evaluated})
    exact_sum = sum(r["fehlerbild"]["exact_total_ops"] for r in evaluated)
    spiral_sum = sum(r["fehlerbild"]["spiral_total_ops"] for r in evaluated)

    positive_digest = [
        {
            "formula_sha256": r["pretruth_witness"]["formula_sha256"],
            "source": r["source"],
            "mode": r["spiral_witness_lane"]["mode"],
            "separator": r["spiral_witness_lane"]["separator"],
            "variables": r["pretruth_witness"]["signature"]["variables"],
            "clauses": r["pretruth_witness"]["signature"]["clauses"],
            "structural_key": r["pretruth_witness"]["signature"]["structural_key"],
            "delta_w": r["fehlerbild"]["delta_w_exact_minus_spiral"],
            "exact_total_ops": r["fehlerbild"]["exact_total_ops"],
            "spiral_total_ops": r["fehlerbild"]["spiral_total_ops"],
        }
        for r in positives
    ]

    gates = {
        "G1_PRETRUTH_SELECTION": all(r["checks"]["decision_pretruth"] for r in evaluated),
        "G2_EXACTNESS": exact_ok,
        "G3_SAT_REPLAY": replay_ok,
        "G4_FEHLERBILD_DIFFERENCE": all("delta_w_exact_minus_spiral" in r["fehlerbild"] for r in evaluated),
        "G5_NO_THEOREM_INFLATION": True,
    }
    gate_pass = bool(evaluated) and all(gates.values())
    if positives:
        verdict = "R5_DISCOVERY_PASS__POSITIVE_ROI_EXAMPLES_FOUND__FREEZE_FOR_R5B__P_VS_NP_OPEN"
    else:
        verdict = "R5_DISCOVERY_PASS__NO_POSITIVE_ROI_FOUND__KEEP_SPIRAL_RECOGNIZER_ONLY__P_VS_NP_OPEN"
    if not gate_pass:
        verdict = "R5_DISCOVERY_INVARIANT_FAIL__DO_NOT_PROMOTE__P_VS_NP_OPEN"

    return {
        "schema": "JANUS/TRUMP/R5/FEHLERBILD-POSITIVE-ROI-DISCOVERY-RESULT/v1.0",
        "rule_id": R5_RULE_ID,
        "verdict": verdict,
        "summary": {
            "rows": len(evaluated),
            "families": len(families),
            "family_names": families,
            "positive_roi_rows": len(positives),
            "exact_total_ops_sum": exact_sum,
            "spiral_total_ops_sum": spiral_sum,
            "aggregate_delta_w": exact_sum - spiral_sum,
            "mode_counts": dict(sorted(mode_counts.items())),
        },
        "positive_roi_examples": positive_digest,
        "gates": gates,
        "discovery_only": True,
        "routing_authority_changed": False,
        "P_VS_NP": "OPEN",
        "next_gate": (
            "R5B_FREEZE_POSITIVE_SIGNATURES_AND_TEST_UNEXPOSED_HOLDOUT"
            if positives
            else "KEEP_SPIRAL_RECOGNIZER_ONLY_OR_DISCOVER_NEW_STRUCTURAL_POLICY"
        ),
        "rows": evaluated,
    }
