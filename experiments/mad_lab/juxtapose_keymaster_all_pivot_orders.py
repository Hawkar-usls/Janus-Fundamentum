#!/usr/bin/env python3
"""JANUS MAD-LAB: JUXTAPOSE exhaustive seven-pivot activation tournament.

Name: JUXTAPOSE, after Phantom Lancer's ultimate.

All seven pivots are considered pre-positioned at the frozen root CNF.  We do
NOT activate them simultaneously.  Instead, every one of the 7! = 5040 possible
activation orders is replayed exactly with the pre-existing C025 elimination
verifier.  No order may be pruned, skipped, learned-away, or promoted by an
heuristic.

The historical JANUS Keymaster is adapted here only as an OFFLINE deterministic
PVP scoreboard over already-verified trajectories.  Its old random exploration,
Tachyon prediction, adaptive mutation, and learned strategy preference have no
theorem authority and are disabled.  Keymaster cannot change a proof verdict.

Ranking is lexicographic and exact, not a weighted heuristic:
  1. zero overflow beats overflow;
  2. lower peak raw C025 units;
  3. lower cumulative raw units;
  4. lower cumulative resolution-pair work;
  5. lower peak canonical units;
  6. earlier exact terminal UNSAT step;
  7. lexicographically smaller pivot order only as a deterministic tie-break.

This is a finite audit of one frozen JANUS-canonical (7,79,350), 50-regular,
25:25 witness.  It does not prove forward reachability or universal pivot
availability.  P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import m2rs_four_front_janus_canonical_core as core

SCHEMA = "JANUS/MAD-LAB/JUXTAPOSE-KEYMASTER-ALL-PIVOT-ORDERS/v1"
STATUS = "JUXTAPOSE_EXHAUSTIVE_ORDER_TOURNAMENT__FINITE_WITNESS_ONLY"
P_VS_NP = "OPEN"
N = core.N
CAP = core.CAP
PIVOTS = tuple(range(1, core.NVAR + 1))
EXPECTED_ORDERS = 5040


def digest(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def replay_order(root: base.CNF, order: tuple[int, ...], keep_receipts: bool = True) -> dict[str, Any]:
    state = root
    receipts: list[dict[str, Any]] = []
    root_units = base.state_units(root)
    peak_raw = root_units
    peak_canonical = root_units
    sum_raw = 0
    sum_pairs = 0
    sum_tautologies = 0
    overflow_count = 0
    terminal_step: int | None = None
    exact_activations = 0

    for step, pivot in enumerate(order, 1):
        if state == ((),):
            if terminal_step is None:
                terminal_step = step - 1
            if keep_receipts:
                receipts.append({
                    "step": step,
                    "pivot": pivot,
                    "status": "PREPOSITIONED_PIVOT_NOT_NEEDED__ALREADY_TERMINAL_UNSAT",
                })
            continue

        live = set(base.vars_of(state))
        if pivot not in live:
            if keep_receipts:
                receipts.append({
                    "step": step,
                    "pivot": pivot,
                    "status": "PREPOSITIONED_PIVOT_ALREADY_ABSENT",
                    "before_units": base.state_units(state),
                })
            continue

        before_units = base.state_units(state)
        out, st = base.eliminate_var_capped(state, pivot, CAP)
        raw_units = int(st["raw_units"])
        pairs = int(st.get("pairs", 0))
        tautologies = int(st.get("tautologies", 0))
        peak_raw = max(peak_raw, raw_units)
        sum_raw += raw_units
        sum_pairs += pairs
        sum_tautologies += tautologies
        exact_activations += 1

        if out is None:
            overflow_count += 1
            if keep_receipts:
                receipts.append({
                    "step": step,
                    "pivot": pivot,
                    "status": "EXACT_OVERFLOW",
                    "before_units": before_units,
                    "raw_units": raw_units,
                    "pairs": pairs,
                    "tautologies": tautologies,
                    "cap": CAP,
                })
            break

        assert base.verify_elimination_transition(state, pivot, out, CAP)
        after_units = base.state_units(out)
        peak_canonical = max(peak_canonical, after_units)
        if keep_receipts:
            receipts.append({
                "step": step,
                "pivot": pivot,
                "status": "EXACT_LAND",
                "before_units": before_units,
                "raw_units": raw_units,
                "after_units": after_units,
                "pairs": pairs,
                "tautologies": tautologies,
            })
        state = out
        if state == ((),) and terminal_step is None:
            terminal_step = step

    if state == ((),) and terminal_step is None:
        terminal_step = len(order)

    terminal_unsat = state == ((),)
    rank_tuple = [
        overflow_count,
        peak_raw,
        sum_raw,
        sum_pairs,
        peak_canonical,
        terminal_step if terminal_step is not None else 10**9,
        *order,
    ]
    return {
        "order": list(order),
        "order_sha256": digest(order),
        "overflow_count": overflow_count,
        "peak_raw_units": peak_raw,
        "sum_raw_units": sum_raw,
        "sum_pair_work": sum_pairs,
        "sum_tautologies": sum_tautologies,
        "peak_canonical_units": peak_canonical,
        "exact_activations": exact_activations,
        "terminal_unsat": terminal_unsat,
        "terminal_step": terminal_step,
        "terminal_cnf": None if overflow_count else [list(c) for c in state],
        "terminal_fingerprint": None if overflow_count else base.fingerprint(state),
        "keymaster_exact_rank_tuple": rank_tuple,
        "receipts": receipts if keep_receipts else None,
    }


def exact_semantic_signature(cnf: base.CNF, remaining: tuple[int, ...]) -> str:
    """Truth signature over remaining variables; used only as an audit checksum."""
    bits_out: list[int] = []
    for bits in itertools.product((0, 1), repeat=len(remaining)):
        assignment = {v: bits[i] for i, v in enumerate(remaining)}
        bits_out.append(int(base.verify_total_assignment(cnf, assignment)))
    return "".join(map(str, bits_out))


def keymaster_tournament(root: base.CNF) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    best_summary: dict[str, Any] | None = None
    worst_summary: dict[str, Any] | None = None

    # Exhaustive by construction.  No Keymaster pruning is permitted.
    for order in itertools.permutations(PIVOTS):
        row = replay_order(root, order, keep_receipts=False)
        summaries.append(row)
        if best_summary is None or tuple(row["keymaster_exact_rank_tuple"]) < tuple(best_summary["keymaster_exact_rank_tuple"]):
            best_summary = row
        # Worst is exact inverse preference on the physically meaningful metrics;
        # lexicographic order remains only a deterministic final tie-break.
        worst_key = (
            row["overflow_count"],
            row["peak_raw_units"],
            row["sum_raw_units"],
            row["sum_pair_work"],
            row["peak_canonical_units"],
            -(row["terminal_step"] if row["terminal_step"] is not None else 10**9),
            tuple(row["order"]),
        )
        if worst_summary is None:
            worst_summary = row
        else:
            w = worst_summary
            prev_key = (
                w["overflow_count"], w["peak_raw_units"], w["sum_raw_units"],
                w["sum_pair_work"], w["peak_canonical_units"],
                -(w["terminal_step"] if w["terminal_step"] is not None else 10**9), tuple(w["order"]),
            )
            if worst_key > prev_key:
                worst_summary = row

    assert len(summaries) == EXPECTED_ORDERS
    assert len({tuple(r["order"]) for r in summaries}) == EXPECTED_ORDERS
    assert best_summary is not None and worst_summary is not None

    # Re-run champion and anti-champion with full receipts for exact replay.
    champion = replay_order(root, tuple(best_summary["order"]), keep_receipts=True)
    anti_champion = replay_order(root, tuple(worst_summary["order"]), keep_receipts=True)

    # Distributions are useful because the champion alone can hide a broad bad tail.
    def hist(key: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for row in summaries:
            k = str(row[key])
            out[k] = out.get(k, 0) + 1
        return dict(sorted(out.items(), key=lambda kv: int(kv[0])))

    safe = [r for r in summaries if r["overflow_count"] == 0]
    terminal = [r for r in summaries if r["terminal_unsat"]]
    return {
        "orders_expected": EXPECTED_ORDERS,
        "orders_replayed": len(summaries),
        "all_orders_unique": True,
        "all_orders_exhaustive": True,
        "safe_order_count": len(safe),
        "overflow_order_count": EXPECTED_ORDERS - len(safe),
        "terminal_unsat_order_count": len(terminal),
        "peak_raw_histogram": hist("peak_raw_units"),
        "terminal_step_histogram": hist("terminal_step"),
        "champion": champion,
        "anti_champion": anti_champion,
        "champion_tie_count": sum(
            tuple(r["keymaster_exact_rank_tuple"][:-7]) == tuple(champion["keymaster_exact_rank_tuple"][:-7])
            for r in summaries
        ),
        "all_order_summaries": summaries,
        "all_order_summaries_sha256": digest(summaries),
    }


def build_payload() -> dict[str, Any]:
    root = core.canonical_witness()
    stats = core.exact_stats(root)
    core.verify_target_stats(stats)
    truth = core.exact_truth_table(root)
    assert truth["UNSAT_exact_for_this_formula"] is True

    tournament = keymaster_tournament(root)
    champion = tournament["champion"]
    anti = tournament["anti_champion"]

    # No finite tournament may be promoted into a universal theorem.
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "name": "JUXTAPOSE",
        "inspiration": "Phantom Lancer ultimate: pre-positioned pivot copies, sequential activation-order tournament",
        "P_VS_NP": P_VS_NP,
        "N": N,
        "cap": CAP,
        "root_stats": stats,
        "root_truth": truth,
        "pivot_protocol": {
            "prepositioned_pivots": list(PIVOTS),
            "activation_is_sequential": True,
            "simultaneous_elimination_claimed": False,
            "permutations": EXPECTED_ORDERS,
            "no_order_pruning": True,
            "no_heuristic_verdict_change": True,
        },
        "keymaster": {
            "role": "OFFLINE_DETERMINISTIC_PVP_SCOREBOARD_ONLY",
            "historical_random_exploration_disabled": True,
            "tachyon_prediction_disabled": True,
            "learned_strategy_pruning_disabled": True,
            "theorem_authority": False,
            "ranking": [
                "overflow_count",
                "peak_raw_units",
                "sum_raw_units",
                "sum_pair_work",
                "peak_canonical_units",
                "terminal_step",
                "lexicographic_order_tiebreak",
            ],
        },
        "tournament": tournament,
        "result": {
            "best_order": champion["order"],
            "best_peak_raw_units": champion["peak_raw_units"],
            "best_sum_raw_units": champion["sum_raw_units"],
            "best_sum_pair_work": champion["sum_pair_work"],
            "best_terminal_step": champion["terminal_step"],
            "worst_order": anti["order"],
            "worst_peak_raw_units": anti["peak_raw_units"],
            "worst_sum_raw_units": anti["sum_raw_units"],
            "worst_sum_pair_work": anti["sum_pair_work"],
            "worst_terminal_step": anti["terminal_step"],
        },
        "anti_self_deception_gate": {
            "finite_frozen_witness_only": True,
            "all_5040_orders_replayed": True,
            "forward_reachability_proved": False,
            "universal_order_availability_proved": False,
            "keymaster_can_change_truth": False,
            "same_run_lemma_promotion": False,
            "theorem_credit_allowed": False,
            "P_VS_NP": P_VS_NP,
        },
    }
    payload["payload_sha256"] = digest(payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(list(argv) if argv is not None else None)
    payload = build_payload()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(json.dumps({
        "schema": payload["schema"],
        "status": payload["status"],
        "orders": payload["tournament"]["orders_replayed"],
        "safe_orders": payload["tournament"]["safe_order_count"],
        "terminal_unsat_orders": payload["tournament"]["terminal_unsat_order_count"],
        "best_order": payload["result"]["best_order"],
        "best_peak_raw_units": payload["result"]["best_peak_raw_units"],
        "worst_order": payload["result"]["worst_order"],
        "worst_peak_raw_units": payload["result"]["worst_peak_raw_units"],
        "P_VS_NP": payload["P_VS_NP"],
        "payload_sha256": payload["payload_sha256"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
