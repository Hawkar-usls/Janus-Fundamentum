#!/usr/bin/env python3
"""JANUS MAD-LAB: JUXTAPOSE 250:250 exact scaling experiment.

This file answers the natural scaling question after the frozen 25:25 seven-pivot
JUXTAPOSE tournament.

Part A -- exact obstruction at n=7
---------------------------------
A JANUS-canonical CNF is an antichain of signed clauses under literal-set
inclusion because canon_cnf removes exact subsumption.  Signed width-k clauses
on n variables form a layer of size C(n,k) 2^k.  A uniformly random maximal
signed chain hits any fixed width-k clause with probability
1/(C(n,k) 2^k).  Hence every antichain A obeys the signed LYM inequality

    sum_{C in A} 1/(C(n,|C|) 2^|C|) <= 1.

Therefore its literal mass satisfies

    L = sum |C| <= max_k k C(n,k) 2^k.

For n=7 that maximum is 3360, while polarity 250:250 on every one of seven
variables requires L=7*(250+250)=3500.  So an exact canonical n=7 250:250 core
is impossible before any pivot search begins.

Part B -- minimal next dimension n=8
------------------------------------
We construct, without MILP or randomness, an exact width-4 antichain with
1000 clauses, L=4000, and for every variable degree=500 with polarity 250:250.
Start from all C(8,4) 2^4 = 1120 signed width-4 clauses.  Choose 15 complementary
pairs of 4-variable supports (30 supports total, each variable appears in exactly
15 supports).  On every chosen support omit four sign patterns:

    ++++ , ---- , ++-- , --++

Each omitted support contributes two positive and two negative occurrences per
coordinate.  Thus every variable loses 30 positive and 30 negative occurrences
from the full width-4 layer's 280:280, leaving exactly 250:250.  Same width means
all distinct retained clauses are automatically an antichain; JANUS canon_cnf
is replayed as authority anyway.

The resulting frozen constructive core is exhaustively checked over all 2^8
assignments and is UNSAT for this one formula.

Part C -- JUXTAPOSE
-------------------
All eight pivots are pre-positioned.  We replay all 8! = 40320 sequential
activation orders under two *static stress caps*:

  N=104, cap=10816: tests the first threshold where at least one initial pivot
  fits this concrete core.
  N=105, cap=11025: tests the first threshold where all eight initial pivots fit.

These N values are stress-test cap parameters only.  This file does NOT prove
that this static n=8 core is forward-reachable from a legitimate JANUS root with
those N values.  It also does not prove a universal 250:250 theorem.  Keymaster
is an offline deterministic scoreboard only and cannot change exact verdicts.
P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

SCHEMA = "JANUS/MAD-LAB/JUXTAPOSE-250x250-EXACT/v1"
STATUS = "STATIC_250x250_JUXTAPOSE_STRESS__FORWARD_REACHABILITY_UNPROVED"
P_VS_NP = "OPEN"
NVAR = 8
WIDTH = 4
MCLAUSE = 1000
LITERAL_MASS = 4000
TARGET_POS = 250
TARGET_NEG = 250
TARGET_DEGREE = 500
PIVOTS = tuple(range(1, NVAR + 1))
EXPECTED_ORDERS = math.factorial(NVAR)
STRESS_N = (104, 105)


def digest(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def signed_layer_size(n: int, k: int) -> int:
    return math.comb(n, k) * (2 ** k)


def n7_lym_obstruction() -> dict[str, Any]:
    rows = []
    for k in range(1, 8):
        f = signed_layer_size(7, k)
        rows.append({"width": k, "layer_size": f, "literal_mass_if_full_layer": k * f})
    max_row = max(rows, key=lambda r: r["literal_mass_if_full_layer"])
    required = 7 * (TARGET_POS + TARGET_NEG)
    assert max_row["literal_mass_if_full_layer"] == 3360
    assert max_row["width"] == 5
    assert required == 3500
    assert required > max_row["literal_mass_if_full_layer"]
    return {
        "canonical_CNF_is_signed_clause_antichain": True,
        "signed_LYM": "sum_C 1/(binom(n,|C|)*2^|C|) <= 1",
        "literal_mass_bound": "L <= max_k k*binom(n,k)*2^k",
        "n": 7,
        "layers": rows,
        "max_canonical_literal_mass": max_row["literal_mass_if_full_layer"],
        "maximizing_width": max_row["width"],
        "required_literal_mass_for_250_250_every_variable": required,
        "250x250_n7_canonical_core_exists": False,
        "contradiction_gap": required - max_row["literal_mass_if_full_layer"],
    }


def complement_support(support: tuple[int, ...]) -> tuple[int, ...]:
    ss = set(support)
    return tuple(v for v in PIVOTS if v not in ss)


def complementary_support_pairs() -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    seen: set[tuple[int, ...]] = set()
    pairs: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for support in itertools.combinations(PIVOTS, WIDTH):
        if support in seen:
            continue
        comp = complement_support(support)
        seen.add(support)
        seen.add(comp)
        pairs.append(tuple(sorted((support, comp))))
    assert len(pairs) == 35
    return pairs


def construct_250x250_core() -> base.CNF:
    all_clauses: set[base.Clause] = set()
    for support in itertools.combinations(PIVOTS, WIDTH):
        for signs in itertools.product((-1, 1), repeat=WIDTH):
            all_clauses.add(tuple(signs[i] * support[i] for i in range(WIDTH)))
    assert len(all_clauses) == signed_layer_size(NVAR, WIDTH) == 1120

    chosen_pairs = complementary_support_pairs()[:15]
    omitted_supports = [support for pair in chosen_pairs for support in pair]
    assert len(omitted_supports) == 30
    support_degree = Counter(v for support in omitted_supports for v in support)
    assert support_degree == Counter({v: 15 for v in PIVOTS})

    patterns = (
        (1, 1, 1, 1),
        (-1, -1, -1, -1),
        (1, 1, -1, -1),
        (-1, -1, 1, 1),
    )
    omitted: set[base.Clause] = set()
    for support in omitted_supports:
        for signs in patterns:
            omitted.add(tuple(signs[i] * support[i] for i in range(WIDTH)))
    assert len(omitted) == 120

    retained = tuple(sorted(all_clauses - omitted))
    assert len(retained) == MCLAUSE
    canonical = base.canon_cnf(retained)
    assert len(canonical) == MCLAUSE
    assert set(canonical) == set(retained)
    return canonical


def exact_stats(cnf: base.CNF) -> dict[str, Any]:
    pos = [sum(v in c for c in cnf) for v in PIVOTS]
    neg = [sum(-v in c for c in cnf) for v in PIVOTS]
    degree = [p + q for p, q in zip(pos, neg)]
    widths = [len(c) for c in cnf]
    stats = {
        "n": len(base.vars_of(cnf)),
        "m": len(cnf),
        "L": sum(widths),
        "state_units_C025": base.state_units(cnf),
        "width_histogram": {str(k): widths.count(k) for k in sorted(set(widths))},
        "positive": pos,
        "negative": neg,
        "degree": degree,
        "fingerprint_C025": base.fingerprint(cnf),
    }
    assert stats["n"] == NVAR
    assert stats["m"] == MCLAUSE
    assert stats["L"] == LITERAL_MASS
    assert stats["state_units_C025"] == 5001
    assert stats["width_histogram"] == {"4": 1000}
    assert pos == [TARGET_POS] * NVAR
    assert neg == [TARGET_NEG] * NVAR
    assert degree == [TARGET_DEGREE] * NVAR
    return stats


def exact_truth_table(cnf: base.CNF) -> dict[str, Any]:
    models: list[str] = []
    for bits in itertools.product((0, 1), repeat=NVAR):
        assignment = {i + 1: bits[i] for i in range(NVAR)}
        if base.verify_total_assignment(cnf, assignment):
            models.append("".join("+" if b else "-" for b in bits))
    assert not models
    return {
        "assignments_checked": 1 << NVAR,
        "satisfying_count": len(models),
        "UNSAT_exact_for_this_formula": len(models) == 0,
        "truth_table_sha256": digest(models),
    }


@functools.lru_cache(maxsize=None)
def transition(cnf: base.CNF, pivot: int, cap: int) -> tuple[base.CNF | None, tuple[tuple[str, int], ...]]:
    out, st = base.eliminate_var_capped(cnf, pivot, cap)
    compact = tuple(sorted((str(k), int(v)) for k, v in st.items() if isinstance(v, (int, bool))))
    return out, compact


def st_dict(compact: tuple[tuple[str, int], ...]) -> dict[str, int]:
    return dict(compact)


def replay_order(root: base.CNF, order: tuple[int, ...], cap: int, keep_receipts: bool = False) -> dict[str, Any]:
    state = root
    peak_raw = base.state_units(root)
    sum_raw = 0
    sum_pairs = 0
    sum_taut = 0
    terminal_step: int | None = None
    receipts: list[dict[str, Any]] = []
    overflow = False

    for step, pivot in enumerate(order, 1):
        if state == ((),):
            if terminal_step is None:
                terminal_step = step - 1
            if keep_receipts:
                receipts.append({"step": step, "pivot": pivot, "status": "ALREADY_TERMINAL_UNSAT"})
            continue
        if pivot not in set(base.vars_of(state)):
            if keep_receipts:
                receipts.append({"step": step, "pivot": pivot, "status": "ALREADY_ABSENT"})
            continue

        before = base.state_units(state)
        out, compact = transition(state, pivot, cap)
        st = st_dict(compact)
        raw = int(st["raw_units"])
        pairs = int(st.get("pairs", 0))
        taut = int(st.get("tautologies", 0))
        peak_raw = max(peak_raw, raw)
        sum_raw += raw
        sum_pairs += pairs
        sum_taut += taut

        if out is None:
            overflow = True
            if keep_receipts:
                receipts.append({
                    "step": step, "pivot": pivot, "status": "EXACT_OVERFLOW",
                    "before_units": before, "raw_units": raw, "pairs": pairs,
                    "tautologies": taut, "cap": cap,
                })
            break

        assert base.verify_elimination_transition(state, pivot, out, cap)
        after = base.state_units(out)
        if keep_receipts:
            receipts.append({
                "step": step, "pivot": pivot, "status": "EXACT_LAND",
                "before_units": before, "raw_units": raw, "after_units": after,
                "pairs": pairs, "tautologies": taut,
            })
        state = out
        if state == ((),) and terminal_step is None:
            terminal_step = step

    return {
        "order": list(order),
        "overflow": overflow,
        "peak_raw_units": peak_raw,
        "sum_raw_units": sum_raw,
        "sum_pair_work": sum_pairs,
        "sum_tautologies": sum_taut,
        "terminal_unsat": state == ((),),
        "terminal_step": terminal_step,
        "receipts": receipts if keep_receipts else None,
    }


def rank_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int(row["overflow"]),
        row["peak_raw_units"],
        row["sum_raw_units"],
        row["sum_pair_work"],
        row["terminal_step"] if row["terminal_step"] is not None else 10**9,
        tuple(row["order"]),
    )


def tournament(root: base.CNF, N: int) -> dict[str, Any]:
    cap = N * N
    summaries: list[dict[str, Any]] = []
    for order in itertools.permutations(PIVOTS):
        summaries.append(replay_order(root, order, cap, keep_receipts=False))
    assert len(summaries) == EXPECTED_ORDERS
    assert len({tuple(r["order"]) for r in summaries}) == EXPECTED_ORDERS

    safe = [r for r in summaries if not r["overflow"]]
    over = [r for r in summaries if r["overflow"]]
    champion0 = min(safe, key=rank_key) if safe else min(summaries, key=rank_key)
    champion = replay_order(root, tuple(champion0["order"]), cap, keep_receipts=True)
    worst0 = max(safe, key=lambda r: (
        r["peak_raw_units"], r["sum_raw_units"], r["sum_pair_work"],
        -(r["terminal_step"] if r["terminal_step"] is not None else 10**9), tuple(r["order"]),
    )) if safe else None
    worst = None if worst0 is None else replay_order(root, tuple(worst0["order"]), cap, keep_receipts=True)

    peak_hist = Counter(r["peak_raw_units"] for r in summaries)
    terminal_hist = Counter(r["terminal_step"] for r in safe)
    first_pivot = {}
    for p in PIVOTS:
        rows = [r for r in summaries if r["order"][0] == p]
        first_pivot[str(p)] = {
            "orders": len(rows),
            "safe": sum(not r["overflow"] for r in rows),
            "overflow": sum(r["overflow"] for r in rows),
            "peak_values": sorted({r["peak_raw_units"] for r in rows}),
        }

    compact = [{
        "o": r["order"], "x": int(r["overflow"]), "p": r["peak_raw_units"],
        "r": r["sum_raw_units"], "w": r["sum_pair_work"], "t": r["terminal_step"],
    } for r in summaries]

    return {
        "N_stress": N,
        "cap": cap,
        "orders": EXPECTED_ORDERS,
        "safe_orders": len(safe),
        "overflow_orders": len(over),
        "terminal_unsat_safe_orders": sum(r["terminal_unsat"] for r in safe),
        "champion": champion,
        "worst_safe": worst,
        "peak_histogram_all_orders": {str(k): peak_hist[k] for k in sorted(peak_hist)},
        "terminal_step_histogram_safe": {str(k): terminal_hist[k] for k in sorted(terminal_hist) if k is not None},
        "by_first_pivot": first_pivot,
        "all_order_summaries_compact": compact,
        "all_order_summaries_sha256": digest(compact),
    }


def build_payload() -> dict[str, Any]:
    obstruction = n7_lym_obstruction()
    root = construct_250x250_core()
    stats = exact_stats(root)
    truth = exact_truth_table(root)

    # First-step microscope with an uncapped-but-finite cap large enough not to bind.
    first_rows = []
    for pivot in PIVOTS:
        out, compact = transition(root, pivot, 10**9)
        assert out is not None
        st = st_dict(compact)
        first_rows.append({
            "pivot": pivot,
            "signature": [TARGET_DEGREE, TARGET_POS, TARGET_NEG],
            "pairs": st["pairs"],
            "tautologies": st["tautologies"],
            "raw_units_C025": st["raw_units"],
            "canonical_units_C025": base.state_units(out),
        })
    assert all(r["pairs"] == TARGET_POS * TARGET_NEG == 62500 for r in first_rows)
    min_first_raw = min(r["raw_units_C025"] for r in first_rows)
    max_first_raw = max(r["raw_units_C025"] for r in first_rows)
    assert min_first_raw == 10787
    assert max_first_raw == 10849
    assert 103 * 103 < min_first_raw <= 104 * 104
    assert 104 * 104 < max_first_raw <= 105 * 105

    tournaments = [tournament(root, N) for N in STRESS_N]
    t104, t105 = tournaments
    assert t104["safe_orders"] == 30240
    assert t104["overflow_orders"] == 10080
    assert t105["safe_orders"] == EXPECTED_ORDERS
    assert t105["overflow_orders"] == 0
    assert t105["champion"]["order"] == [3, 1, 4, 5, 2, 6, 7, 8]
    assert t105["champion"]["peak_raw_units"] == 10787
    assert t105["champion"]["terminal_step"] == 4

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "name": "JUXTAPOSE-250x250",
        "P_VS_NP": P_VS_NP,
        "n7_exact_obstruction": obstruction,
        "n8_constructive_core": {
            "construction_is_deterministic": True,
            "MILP_used": False,
            "randomness_used": False,
            "JANUS_canonical_CNF": True,
            "stats": stats,
            "truth": truth,
        },
        "first_pivot_microscope": {
            "rows": first_rows,
            "parent_pairs_per_pivot": 62500,
            "min_exact_raw_units": min_first_raw,
            "max_exact_raw_units": max_first_raw,
            "first_N_with_any_initial_pivot_fitting_N_squared": 104,
            "first_N_with_all_initial_pivots_fitting_N_squared": 105,
        },
        "keymaster": {
            "role": "OFFLINE_DETERMINISTIC_PVP_SCOREBOARD_ONLY",
            "all_orders_required": True,
            "pruning_allowed": False,
            "prediction_can_change_verdict": False,
            "theorem_authority": False,
        },
        "tournaments": tournaments,
        "anti_self_deception_gate": {
            "n7_impossibility_is_combinatorial_antichain_bound": True,
            "n8_core_is_static_constructive_witness_only": True,
            "forward_reachability_proved": False,
            "stress_N_values_are_not_claimed_reachable_root_sizes": True,
            "universal_250x250_theorem_proved": False,
            "same_run_theorem_promotion": False,
            "P_VS_NP": P_VS_NP,
        },
    }
    payload["payload_sha256"] = digest(payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args(list(argv) if argv is not None else None)
    payload = build_payload()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    t104, t105 = payload["tournaments"]
    print(json.dumps({
        "schema": payload["schema"],
        "n7_250x250_exists": payload["n7_exact_obstruction"]["250x250_n7_canonical_core_exists"],
        "n7_max_literal_mass": payload["n7_exact_obstruction"]["max_canonical_literal_mass"],
        "n8_stats": payload["n8_constructive_core"]["stats"],
        "first_raw_min": payload["first_pivot_microscope"]["min_exact_raw_units"],
        "first_raw_max": payload["first_pivot_microscope"]["max_exact_raw_units"],
        "N104_safe": t104["safe_orders"],
        "N104_overflow": t104["overflow_orders"],
        "N105_safe": t105["safe_orders"],
        "N105_overflow": t105["overflow_orders"],
        "N105_best_order": t105["champion"]["order"],
        "N105_best_peak": t105["champion"]["peak_raw_units"],
        "N105_terminal_step": t105["champion"]["terminal_step"],
        "P_VS_NP": payload["P_VS_NP"],
        "payload_sha256": payload["payload_sha256"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
