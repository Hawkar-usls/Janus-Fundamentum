#!/usr/bin/env python3
"""Bounded root-anchored Stage4 depth probe over a frozen small-CNF space.

For every connected Stage-3 OPEN instance in the requested finite enumeration:
  * freeze root CNF, root variables, original N, N^C state cap and N^k extension cap;
  * repeatedly request ONE exact Stage4 proof from the same EngineState;
  * independently replay each proof;
  * apply it without rebasing N/caps and without reusing historical extension ids;
  * after every move, re-enter already admitted exact typed lanes;
  * stop at exact SAT/UNSAT, first Stage4 barrier, or the frozen extension cap.

This is finite research evidence only.  Even complete success on the enumerated
space does not prove universal iterability, GPEI, arbitrary-CNF totality, or P=NP.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_jec_extension_progress_proof as stage4
from experiments.direct import janus_matching_hall_escape as hall
from experiments.direct import janus_one_variable_separator_escape as stage3
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct import janus_open3_stage4_bounded_coverage_probe as open3_probe

P_VS_NP = "OPEN"


def _cnf(rows) -> base.CNF:
    return base.canon_cnf(rows)


def _exact_reentry(cnf: base.CNF) -> dict:
    h = hall.solve_matching_hall_escape(cnf)
    if h.get("status") in {"SAT", "UNSAT"}:
        if not hall.verify_matching_hall_escape(cnf, h):
            raise AssertionError("HALL_REENTRY_REPLAY_FAILED")
        return {"status": h["status"], "mode": "MATCHING_HALL_CARDINALITY_ESCAPE"}

    s = stage3.solve_one_variable_escape(cnf)
    if s.get("status") in {"SAT", "UNSAT"}:
        if not stage3.verify_one_variable_escape(cnf, s):
            raise AssertionError("STAGE3_REENTRY_REPLAY_FAILED")
        return {"status": s["status"], "mode": s.get("mode")}
    return {"status": "OPEN", "mode": None}


def _apply_progress(state: base.EngineState, proof: dict, *, first: bool) -> None:
    source = state.residual
    if not stage4.verify_extension_progress_proof(source, proof, require_initial_context=first):
        raise AssertionError("PROGRESS_PROOF_FAILED_REPLAY")
    if _cnf(proof["root_cnf"]) != state.root:
        raise AssertionError("ROOT_REBASED")
    if int(proof["N"]) != state.N:
        raise AssertionError("N_REBASED")
    if int(proof["state_cap"]) != state.state_cap:
        raise AssertionError("STATE_CAP_REBASED")
    if int(proof["extension_cap"]) != state.extension_cap:
        raise AssertionError("EXTENSION_CAP_REBASED")
    if int(proof["extension_count_before"]) != state.ledger.extension_count:
        raise AssertionError("EXTENSION_COUNT_BEFORE_MISMATCH")

    cert = dict(proof["macro_certificate"])
    new_extension = int(cert["extension"])
    historical = set(v2.historical_extension_ids(state))
    if new_extension in historical:
        raise AssertionError("HISTORICAL_EXTENSION_ID_REUSE")
    if historical and new_extension <= max(historical):
        raise AssertionError("NON_MONOTONE_EXTENSION_ID")

    for step in proof.get("elimination_steps", []):
        state.elimination_history.append(
            base.ElimSnapshot(_cnf(step["before_cnf"]), int(step["pivot"]), "ROOT_ANCHORED_STAGE4")
        )

    state.extension_defs.append(cert)
    state.ledger.extension_count += 1
    state.ledger.extension_definition_bytes += len(
        json.dumps(cert, sort_keys=True, separators=(",", ":")).encode()
    )
    state.ledger.question_count += len(proof.get("elimination_steps", []))
    state.ledger.proof_bytes += int(proof.get("proof_bytes", 0))
    state.ledger.recompression_work += base.state_units(_cnf(proof["macro_cnf"]))
    state.ledger.recompression_work += sum(
        base.state_units(_cnf(step["after_cnf"]))
        for step in proof.get("elimination_steps", [])
    )
    state.residual = _cnf(proof["result_cnf"])
    state.ledger.max_state_units = max(
        state.ledger.max_state_units,
        base.state_units(state.residual),
        base.state_units(_cnf(proof["macro_cnf"])),
    )
    if state.ledger.extension_count != int(proof["extension_count_after"]):
        raise AssertionError("EXTENSION_COUNT_AFTER_MISMATCH")
    if base.state_units(state.residual) > state.state_cap:
        raise AssertionError("RESULT_LEFT_ROOT_STATE_CAP")


def _run_one(root: base.CNF, *, cap_exponent: int, extension_exponent: int) -> dict:
    state = stage4.initial_state(
        root,
        cap_exponent=cap_exponent,
        extension_exponent=extension_exponent,
    )
    root_N = state.N
    root_cap = state.state_cap
    state.ledger.max_state_units = base.state_units(root)
    chain = []

    # The caller selected a Stage3 OPEN root, but exact re-entry is harmless and
    # keeps this routine independently fail-closed.
    decision = _exact_reentry(state.residual)
    if decision["status"] in {"SAT", "UNSAT"}:
        return {"status": decision["status"], "depth": 0, "mode": decision["mode"], "chain": chain}

    for depth in range(1, state.extension_cap + 1):
        proof = stage4.build_from_state(
            state,
            context_mode="INITIAL_CONTEXT" if depth == 1 else "ENGINE_CONTEXT",
        )
        if proof is None:
            return {
                "status": "OPEN",
                "depth": depth - 1,
                "barrier": "NO_NEXT_STAGE4_MOVE",
                "chain": chain,
                "root_N": root_N,
                "root_state_cap": root_cap,
                "max_state_units": state.ledger.max_state_units,
                "extension_count": state.ledger.extension_count,
            }

        _apply_progress(state, proof, first=(depth == 1))
        chain.append({
            "depth": depth,
            "mode": proof["mode"],
            "extension": int(proof["macro_certificate"]["extension"]),
            "before_phi": int(proof["before_phi"]),
            "after_phi": int(proof["after_phi"]),
            "result_fingerprint": proof["result_fingerprint"],
            "proof_bytes": int(proof["proof_bytes"]),
        })

        decision = _exact_reentry(state.residual)
        if decision["status"] in {"SAT", "UNSAT"}:
            return {
                "status": decision["status"],
                "depth": depth,
                "mode": decision["mode"],
                "chain": chain,
                "root_N": root_N,
                "root_state_cap": root_cap,
                "max_state_units": state.ledger.max_state_units,
                "within_root_state_cap": state.ledger.max_state_units <= root_cap,
                "extension_ids": list(v2.historical_extension_ids(state)),
                "cumulative_proof_bytes": state.ledger.proof_bytes,
                "ledger": {
                    "proposal_work": state.ledger.proposal_work,
                    "certificate_discovery_work": state.ledger.certificate_discovery_work,
                    "verification_work": state.ledger.verification_work,
                    "elimination_pair_work": state.ledger.elimination_pair_work,
                    "recompression_work": state.ledger.recompression_work,
                },
            }

    return {
        "status": "OPEN",
        "depth": state.extension_cap,
        "barrier": "ROOT_EXTENSION_CAP_EXHAUSTED",
        "chain": chain,
        "root_N": root_N,
        "root_state_cap": root_cap,
        "max_state_units": state.ledger.max_state_units,
        "extension_count": state.ledger.extension_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nvars", type=int, default=4)
    parser.add_argument("--clauses", type=int, default=5)
    parser.add_argument("--min-width", type=int, default=3)
    parser.add_argument("--max-width", type=int, default=3)
    parser.add_argument("--cap-exponent", type=int, default=2)
    parser.add_argument("--extension-exponent", type=int, default=1)
    parser.add_argument("--limit", type=int, default=5000)
    args = parser.parse_args()

    universe = open3_probe.clause_universe(args.nvars, args.min_width, args.max_width)
    seen = set()
    totals = {
        "connected_examined": 0,
        "stage3_decided": 0,
        "open3": 0,
        "eventually_decided": 0,
        "eventually_sat": 0,
        "eventually_unsat": 0,
        "remaining_open": 0,
    }
    depth_hist = Counter()
    mode_hist = Counter()
    first_open = None
    deepest = None

    for raw_rows in combinations(universe, args.clauses):
        root = base.canon_cnf(raw_rows)
        if len(root) != args.clauses or len(base.vars_of(root)) != args.nvars:
            continue
        fp = base.fingerprint(root)
        if fp in seen:
            continue
        seen.add(fp)
        if not open3_probe.primal_connected(root):
            continue
        if args.limit and totals["connected_examined"] >= args.limit:
            break
        totals["connected_examined"] += 1

        root_decision = stage3.solve_one_variable_escape(root)
        if root_decision.get("status") in {"SAT", "UNSAT"}:
            if not stage3.verify_one_variable_escape(root, root_decision):
                raise AssertionError("ROOT_STAGE3_REPLAY_FAILED")
            totals["stage3_decided"] += 1
            continue

        totals["open3"] += 1
        result = _run_one(
            root,
            cap_exponent=args.cap_exponent,
            extension_exponent=args.extension_exponent,
        )
        if deepest is None or result["depth"] > deepest["result"]["depth"]:
            deepest = {
                "source_fingerprint": fp,
                "source_cnf": [list(c) for c in root],
                "result": result,
            }

        if result["status"] in {"SAT", "UNSAT"}:
            totals["eventually_decided"] += 1
            totals["eventually_sat" if result["status"] == "SAT" else "eventually_unsat"] += 1
            depth_hist[result["depth"]] += 1
            mode_hist[result.get("mode")] += 1
        else:
            totals["remaining_open"] += 1
            if first_open is None:
                first_open = {
                    "source_fingerprint": fp,
                    "source_cnf": [list(c) for c in root],
                    "result": result,
                }

    report = {
        "schema": "JANUS/C025/STAGE4-ROOT-ANCHORED-DEPTH-PROBE/v1",
        "status": (
            "FINITE_OPEN_REMAINS"
            if totals["remaining_open"]
            else "ALL_ENUMERATED_OPEN3_DECIDED_UNDER_ROOT_ANCHORED_ITERATION"
        ),
        "search_space": vars(args),
        "totals": totals,
        "stage4_depth_histogram": {str(k): v for k, v in sorted(depth_hist.items())},
        "final_exact_mode_histogram": dict(sorted(mode_hist.items(), key=lambda kv: str(kv[0]))),
        "deepest_decision_or_attempt": deepest,
        "first_remaining_open": first_open,
        "scientific_boundary": {
            "bounded_finite_probe_only": True,
            "root_budget_rebased": False,
            "grammar_changed_during_probe": False,
            "absence_of_open_is_not_universal_totality": True,
            "universal_stage4_iterability": "OPEN",
            "universal_GPEI_preservation": "OPEN",
            "arbitrary_CNF_totality": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
