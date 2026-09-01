#!/usr/bin/env python3
"""R3B recovery validation for the natural residual lane.

R3A remains immutable.  R3B changes only the carrier/observer defects exposed
by R3A: SAT fallback paths now return a replayable witness, and the observer
records solver-native unit and immediate post-restriction states before any
truth query, then selects them round-robin across the existing frozen corpus
families.  The frozen R2 density route rule is unchanged.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import product
from typing import List

from janus_trump_p_vs_np_direct_challenge_r0 import canon, corpus, dpll, restrict_cnf, variables
from janus_trump_osiris_r3_natural_residuals import (
    CandidateResult,
    R2_MAX_PAIR_PROPOSALS,
    _components_without,
    _greedy_split,
    build_primal_graph,
    exact_search_witness,
    formula_digest,
    formula_status,
    frozen_r2_route_prediction,
    graph_signature,
    occurrence_pivot,
    seal_pretruth_witness,
    split_by_separator,
    unit_close,
    verify_sat,
)

R3B_UNIT_TRACE_MAX_STEPS = 3
R3B_BRANCH_PROBE_MAX_DEPTH = 2
R3B_CANDIDATE_STATES_PER_ROOT_CAP = 6
R3B_SELECTED_RESIDUAL_CAP = 60
R3B_MIN_RESIDUALS = 24
R3B_MIN_FAMILIES = 4


def _make_row(source: dict, cnf):
    f = canon(cnf)
    sig = graph_signature(f)
    pred = frozen_r2_route_prediction(sig)
    return {
        "source": source,
        "cnf": f,
        "pretruth_witness": seal_pretruth_witness(source, f, sig, pred),
    }


def _root_candidate_states(root_index, family, size, variant, root) -> List[dict]:
    root = canon(root)
    root_sha = formula_digest(root)
    out: List[dict] = []
    seen = set()

    # Observe intermediate unit-propagation states that R3A's full unit_close
    # intentionally hid.  No SAT/UNSAT oracle is consulted.
    f = root
    for step in range(1, R3B_UNIT_TRACE_MAX_STEPS + 1):
        if not f or () in f:
            break
        units = [c[0] for c in f if len(c) == 1]
        if not units:
            break
        lit = units[0]
        child = canon(restrict_cnf(f, abs(lit), lit > 0))
        if child and () not in child and len(variables(child)) >= 3:
            dg = formula_digest(child)
            if dg not in seen and dg != root_sha:
                seen.add(dg)
                src = {
                    "root_index": root_index,
                    "family": family,
                    "size": size,
                    "variant": variant,
                    "probe_kind": "UNIT_TRACE",
                    "probe_depth": 0,
                    "probe_step": step,
                    "probe_literal": lit,
                    "root_formula_sha256": root_sha,
                }
                out.append(_make_row(src, child))
        f = child
        if len(out) >= R3B_CANDIDATE_STATES_PER_ROOT_CAP:
            return out

    # Branch probe: record the immediate solver-native restriction before unit
    # closure (important for parity families), then continue from unit closure.
    start = unit_close(root)
    frontier = [(start, 0, "ROOT")]
    while frontier and len(out) < R3B_CANDIDATE_STATES_PER_ROOT_CAP:
        state, depth, path = frontier.pop(0)
        if depth >= R3B_BRANCH_PROBE_MAX_DEPTH or not state or () in state:
            continue
        pivot = occurrence_pivot(state)
        if pivot is None:
            continue
        for value in (False, True):
            raw = canon(restrict_cnf(state, pivot, value))
            raw_dg = formula_digest(raw)
            if raw and () not in raw and len(variables(raw)) >= 3 and raw_dg not in seen and raw_dg != root_sha:
                seen.add(raw_dg)
                src = {
                    "root_index": root_index,
                    "family": family,
                    "size": size,
                    "variant": variant,
                    "probe_kind": "POST_RESTRICTION_PRE_UNIT",
                    "probe_depth": depth + 1,
                    "probe_path": f"{path}/{pivot}={'T' if value else 'F'}",
                    "pivot": pivot,
                    "branch_value": value,
                    "root_formula_sha256": root_sha,
                }
                out.append(_make_row(src, raw))
                if len(out) >= R3B_CANDIDATE_STATES_PER_ROOT_CAP:
                    break
            closed = unit_close(raw)
            if closed and () not in closed and len(variables(closed)) >= 3:
                frontier.append((closed, depth + 1, f"{path}/{pivot}={'T' if value else 'F'}"))
        if len(out) >= R3B_CANDIDATE_STATES_PER_ROOT_CAP:
            break
    return out


def probe_family_stratified_residuals() -> List[dict]:
    pools = defaultdict(list)
    family_order = []
    for root_index, (family, size, variant, root) in enumerate(corpus()):
        if family not in family_order:
            family_order.append(family)
        pools[family].extend(_root_candidate_states(root_index, family, size, variant, root))

    selected: List[dict] = []
    offsets = {f: 0 for f in family_order}
    while len(selected) < R3B_SELECTED_RESIDUAL_CAP:
        progress = False
        for family in family_order:
            i = offsets[family]
            if i < len(pools[family]):
                selected.append(pools[family][i])
                offsets[family] += 1
                progress = True
                if len(selected) >= R3B_SELECTED_RESIDUAL_CAP:
                    break
        if not progress:
            break
    return selected


def r3b_candidate(cnf, pretruth_witness: dict) -> CandidateResult:
    f = canon(cnf)
    sig = pretruth_witness["signature"]
    prediction = pretruth_witness["route_prediction"]

    # Proof-carrying fallback: unlike R3A, SAT always carries a replayable model.
    if prediction == "EXACT_FALLBACK":
        terminal, witness, nodes = exact_search_witness(f)
        return CandidateResult(
            terminal=terminal,
            witness=witness,
            mode="R3B_PROOF_CARRYING_EXACT_FALLBACK",
            separator=None,
            structural_ops=int(sig["signature_ops"]),
            proposals_tested=0,
            boundary_attempts=0,
            wing_nodes=0,
            fallback_work=nodes,
        )

    graph, structural_ops = build_primal_graph(f)
    ranked = []
    for u in sorted(graph):
        for v in sorted(x for x in graph if x > u):
            ranked.append((-(len(graph[u]) + len(graph[v])), (u, v)))
    ranked.sort(key=lambda x: (x[0], x[1]))

    proposals = 0
    admitted = None
    for _, pair in ranked[:R2_MAX_PAIR_PROPOSALS]:
        proposals += 1
        sep = set(pair)
        comps, ops = _components_without(graph, sep)
        structural_ops += ops
        split = _greedy_split(comps)
        if split is None:
            continue
        left, right = split
        try:
            split_by_separator(f, sep, left, right)
        except ValueError:
            continue
        admitted = (sep, left, right)
        break

    if admitted is None:
        terminal, witness, nodes = exact_search_witness(f)
        return CandidateResult(
            terminal=terminal,
            witness=witness,
            mode="R3B_TRY_NO_SEPARATOR_PROOF_CARRYING_FALLBACK",
            separator=None,
            structural_ops=structural_ops,
            proposals_tested=proposals,
            boundary_attempts=0,
            wing_nodes=0,
            fallback_work=nodes,
        )

    sep, left, right = admitted
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
            return CandidateResult(
                terminal="SAT", witness=combined,
                mode="R3B_EXACT_DOUBLE_SPIRAL_MEET", separator=sorted(sep),
                structural_ops=structural_ops, proposals_tested=proposals,
                boundary_attempts=attempts, wing_nodes=wing_nodes, fallback_work=0,
            )
    return CandidateResult(
        terminal="UNSAT", witness=None,
        mode="R3B_EXACT_DOUBLE_SPIRAL_MEET", separator=sorted(sep),
        structural_ops=structural_ops, proposals_tested=proposals,
        boundary_attempts=attempts, wing_nodes=wing_nodes, fallback_work=0,
    )


def evaluate_r3b(row: dict) -> dict:
    f = row["cnf"]
    w = row["pretruth_witness"]
    assert w["truth"] is None and w["candidate_result"] is None and w["verification_result"] is None
    candidate = r3b_candidate(f, w)
    oracle = dpll(f)
    exact = oracle["status"] == "EXACT"
    baseline_terminal = None if not exact else ("SAT" if oracle["sat"] else "UNSAT")
    terminal_match = exact and candidate.terminal == baseline_terminal
    replay = candidate.terminal != "SAT" or verify_sat(f, candidate.witness)
    verified = terminal_match and replay
    return {
        "source": row["source"],
        "pretruth_witness": w,
        "candidate": candidate.as_dict(),
        "independent_exact_verifier": oracle,
        "checks": {
            "baseline_exact": exact,
            "terminal_match": terminal_match,
            "sat_witness_replay": replay,
            "verified_experience_eligible": verified,
        },
    }
