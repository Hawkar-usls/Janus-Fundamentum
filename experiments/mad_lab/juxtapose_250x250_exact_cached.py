#!/usr/bin/env python3
"""Cached executable front-end for juxtapose_250x250_exact.

Mathematics is unchanged.  This wrapper ensures each unique
(state,pivot,cap) exact elimination AND its transition verification are computed
once.  The 40320 permutation replays then reuse immutable verified receipts.
"""
from __future__ import annotations

import argparse
import functools
import json
from pathlib import Path
from typing import Any, Iterable

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import juxtapose_250x250_exact as J


@functools.lru_cache(maxsize=None)
def verified_transition(cnf: base.CNF, pivot: int, cap: int):
    out, st = base.eliminate_var_capped(cnf, pivot, cap)
    verified = out is None or base.verify_elimination_transition(cnf, pivot, out, cap)
    assert verified
    compact = tuple(sorted((str(k), int(v)) for k, v in st.items() if isinstance(v, (int, bool))))
    return out, compact, verified


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
        out, compact, verified = verified_transition(state, pivot, cap)
        assert verified
        st = dict(compact)
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

        after = base.state_units(out)
        if keep_receipts:
            receipts.append({
                "step": step, "pivot": pivot, "status": "EXACT_LAND_VERIFIED_CACHED",
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


def build_payload():
    # Patch only performance plumbing.  J.tournament resolves replay_order from
    # its module globals at call time, so every trajectory uses this exact cached
    # verifier.  J.build_payload's first-step microscope still uses J.transition;
    # adapt its expected two-value API with a cache-backed shim.
    J.replay_order = replay_order

    @functools.lru_cache(maxsize=None)
    def two_value_transition(cnf: base.CNF, pivot: int, cap: int):
        out, compact, verified = verified_transition(cnf, pivot, cap)
        assert verified
        return out, compact

    J.transition = two_value_transition
    payload = J.build_payload()
    payload["execution_cache"] = {
        "unique_verified_transition_cache": True,
        "verification_reused_only_after_exact_success": True,
        "cache_changes_mathematical_verdict": False,
        "cache_info": str(verified_transition.cache_info()),
    }
    payload["payload_sha256_after_cache_metadata"] = J.digest(payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args(list(argv) if argv is not None else None)
    p = build_payload()
    text = json.dumps(p, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    t104, t105 = p["tournaments"]
    print(json.dumps({
        "schema": p["schema"],
        "N104_safe": t104["safe_orders"],
        "N104_overflow": t104["overflow_orders"],
        "N105_safe": t105["safe_orders"],
        "N105_overflow": t105["overflow_orders"],
        "N105_best_order": t105["champion"]["order"],
        "N105_best_peak": t105["champion"]["peak_raw_units"],
        "N105_terminal_step": t105["champion"]["terminal_step"],
        "cache": p["execution_cache"],
        "P_VS_NP": p["P_VS_NP"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
