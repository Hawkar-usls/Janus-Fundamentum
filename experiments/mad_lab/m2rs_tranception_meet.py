#!/usr/bin/env python3
"""JANUS MAD-LAB: M2R-S x Tranception bidirectional meet stress.

Experimental lane only.

Transfer from Tranception is algorithmic, not physical:
- mirror scoring in LR / RL directions;
- direction-dependent flip/tie order;
- frozen prior may rank exact candidates but never changes truth;
- forward selection must survive later DIRECT replay;
- the two streams meet and compare receipts.

M2R-S = Minimum Certified Safe Selector.
For each abstract state it enumerates the already admitted exact action classes,
applies only pre-existing proof-gated bounds, and selects the lexicographically
minimum certified resource tuple. This is a SHADOW selector unless actual action
availability for a concrete CNF is separately certified.

P vs NP remains OPEN.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from experiments.direct import janus_v05_abstract_frontier_support_mass as A
from experiments.direct import janus_v05_abstract_frontier_global_raw_universe as G
from experiments.direct import janus_v05_abstract_frontier_N58_23x27_projection_fiber as PROVED_REPAIR
from experiments.mad_lab.prime_stress_full_closure_v2 import (
    PROVED_BASE_FRONTIER,
    add_box,
    scan_prime_full,
)

LANE = "JANUS_MAD_LAB_M2RS_TRANCEPTION_MEET"
STATUS = "EXPERIMENTAL_NOT_THEOREM"
P_VS_NP = "OPEN"
TRANCEPTION_SOURCE_COMMIT = "e786ca75ac30afb14e45edffc92aa49a05a9da4f"
ACTION_AVAILABILITY_AUTHORITY = False


def digest(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def exact_action_bound(N: int, n: int, m: int, L: int, d: int, p: int, q: int) -> dict[str, Any]:
    raw0, M0, L0, R0 = G.transfer_bounds_global(n, m, L, d, p, q)
    raw, M, Lb, R = int(raw0), int(M0), int(L0), int(R0)
    provider = "GLOBAL_RAW_EXACT_BOUND"
    rescue = PROVED_REPAIR.enhanced_rescue(n, m, L, d, p, q)
    if rescue is not None and int(rescue[0]) < raw:
        raw = int(rescue[0])
        M = int(rescue[1])
        Lb = min(Lb, int(rescue[2]))
        R = int(rescue[3])
        provider = "PREEXISTING_PROVED_RESCUE_CHAIN"
    return {
        "N": N, "state": [n, m, L], "d": d, "p": p, "q": q,
        "raw_base": int(raw0), "raw_final": raw,
        "m_out": M, "L_out": Lb, "R_or_J": R,
        "cap": N * N, "proof_gated_bound": True, "provider": provider,
        "cap_safe": raw <= N * N,
    }


def action_key(action: dict[str, Any], direction: str, prior_action: tuple[int, int, int] | None) -> tuple:
    """Tranception-like fusion, but exact resource tuple dominates all ranking.

    The retrieval-like prior is only a late tie-break and therefore cannot turn
    an unsafe action into a safe one or change the exact proof bound.
    """
    d, p, q = action["d"], action["p"], action["q"]
    if prior_action is None:
        prior_distance = 0
    else:
        prior_distance = abs(d - prior_action[0]) + abs(p - prior_action[1]) + abs(q - prior_action[2])
    canonical = (d, p, q) if direction == "LR" else (-d, -p, -q)
    return (
        action["raw_final"],
        action["m_out"],
        action["L_out"],
        action["R_or_J"],
        prior_distance,
        canonical,
    )


def select_state_action(
    N: int,
    n: int,
    m: int,
    L: int,
    direction: str,
    prior_action: tuple[int, int, int] | None,
) -> dict[str, Any] | None:
    dlo, dhi = A.degree_interval(n, m, L)
    if dlo > dhi:
        return None
    actions: list[dict[str, Any]] = []
    for d in range(dlo, dhi + 1):
        for p in range(0, d // 2 + 1):
            q = d - p
            actions.append(exact_action_bound(N, n, m, L, d, p, q))
    if not actions:
        return None
    chosen = min(actions, key=lambda a: action_key(a, direction, prior_action))
    chosen = dict(chosen)
    chosen["direction"] = direction
    chosen["candidate_count"] = len(actions)
    chosen["selector"] = "MIN_CERTIFIED_RESOURCE_TUPLE"
    chosen["retrieval_prior_role"] = "TIE_BREAK_ONLY"
    chosen["action_availability_certified"] = ACTION_AVAILABILITY_AUTHORITY
    chosen["theorem_credit_allowed"] = False
    chosen["candidate_set_digest"] = digest([
        [a["d"], a["p"], a["q"], a["raw_final"], a["m_out"], a["L_out"], a["R_or_J"]]
        for a in actions
    ])
    chosen["selection_digest"] = digest(chosen)
    return chosen


def m2rs_selective_closure(N: int, direction: str) -> dict[str, Any]:
    """Follow one shadow path using the minimum exact bound in each abstract state.

    This tests the selector idea. It is NOT theorem closure because an abstract
    action class is not automatically an available action for every concrete CNF.
    """
    if N <= PROVED_BASE_FRONTIER:
        return {
            "N": N, "direction": direction,
            "verdict": "CLOSED_BY_PROVED_BASE_FRONTIER",
            "theorem_credit_allowed": False,
        }

    cap = N * N
    roots = A.hard_roots(N)
    max_n = max(roots, default=A.TAIL_N)
    boxes: dict[int, list[tuple[int, int, int]]] = {n: [] for n in range(7, max_n + 1)}
    rootsets = {n: set(rows) for n, rows in roots.items()}
    checked_states = 0
    selected_actions = 0
    prior_action: tuple[int, int, int] | None = None
    ledger: list[dict[str, Any]] = []

    # Dependency topology must remain high-n -> low-n in BOTH mirrors.
    for n in range(max_n, 6, -1):
        candidates = set(rootsets.get(n, set()))
        bs = boxes[n]
        maxM = max((M for M, _, _ in bs), default=0)
        for m in range(7, maxM + 1):
            Lcap = max((min(Lb, Sb - 1 - m) for M, Lb, Sb in bs if M >= m), default=-1)
            if Lcap < 0:
                continue
            Llo = max(2 * m, n, PROVED_BASE_FRONTIER - n - m)
            Lhi = min(Lcap, n * m, cap - 1 - m)
            if Llo > Lhi:
                continue
            for L in range(Llo, Lhi + 1):
                dlo, dhi = A.degree_interval(n, m, L)
                if dlo <= dhi:
                    candidates.add((m, L))

        ordered_states = sorted(candidates, reverse=(direction == "RL"))
        for m, L in ordered_states:
            checked_states += 1
            chosen = select_state_action(N, n, m, L, direction, prior_action)
            if chosen is None:
                continue
            selected_actions += 1
            prior_action = (chosen["d"], chosen["p"], chosen["q"])
            ledger.append({
                "state": chosen["state"],
                "selected": [chosen["d"], chosen["p"], chosen["q"]],
                "raw_final": chosen["raw_final"],
                "selection_digest": chosen["selection_digest"],
            })
            if not chosen["cap_safe"]:
                return {
                    "N": N, "direction": direction,
                    "verdict": "M2RS_SHADOW_OPEN",
                    "cap": cap,
                    "checked_states": checked_states,
                    "selected_actions": selected_actions,
                    "first_unsafe": chosen,
                    "ledger_digest": digest(ledger),
                    "action_availability_certified": False,
                    "theorem_credit_allowed": False,
                    "claim_ceiling": "SELECTOR_BOUND_OPEN__NOT_ACTUAL_CNF_COUNTEREXAMPLE",
                }

            for n2 in range(7, n):
                add_box(boxes[n2], chosen["m_out"], chosen["L_out"], chosen["raw_final"])

    return {
        "N": N, "direction": direction,
        "verdict": "M2RS_SHADOW_PATH_FOUND",
        "cap": cap,
        "checked_states": checked_states,
        "selected_actions": selected_actions,
        "ledger_digest": digest(ledger),
        "action_availability_certified": False,
        "theorem_credit_allowed": False,
        "claim_ceiling": "ABSTRACT_SAFE_SELECTOR_PATH_ONLY__NO_UNIVERSAL_ACTION_AVAILABILITY_CERTIFICATE",
    }


def direct_replay(N: int) -> dict[str, Any]:
    r = scan_prime_full(N)
    o = r.get("first_open")
    return {
        "N": N,
        "verdict": r["verdict"],
        "cap": r.get("cap", N * N),
        "first_open_signature": None if o is None else [
            *o["state"], o["d"], o["p"], o["q"], o["raw_final"]
        ],
        "checked_states": r.get("checked_states", r.get("checked_states_before_open")),
        "checked_transitions": r.get("checked_transitions", r.get("checked_transitions_before_open")),
        "theorem_credit_allowed": False,
        "source_scope": r.get("scope"),
    }


def visit(N: int, direction: str) -> dict[str, Any]:
    # Required order: M2R-S first, DIRECT second.
    m2r = m2rs_selective_closure(N, direction)
    frozen_pre_direct = digest(m2r)
    direct = direct_replay(N)
    if m2r["verdict"] == "M2RS_SHADOW_PATH_FOUND" and direct["verdict"] == "OPEN":
        relation = "SHADOW_SELECTOR_ADVANTAGE_ONLY"
    elif "OPEN" in m2r["verdict"] and direct["verdict"] == "OPEN":
        relation = "BOTH_OPEN"
    else:
        relation = "NO_CONTRADICTION_DETECTED"
    receipt = {
        "N": N, "direction": direction,
        "order": ["M2R_S", "DIRECT"],
        "m2rs": m2r,
        "m2rs_frozen_before_direct_sha256": frozen_pre_direct,
        "direct": direct,
        "relation": relation,
        "same_run_promotion": False,
        "theorem_credit_allowed": False,
        "P_VS_NP": "OPEN",
    }
    receipt["receipt_sha256"] = digest(receipt)
    return receipt


def compare_mirror(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    assert a["N"] == b["N"]
    comparable = {
        "direct_verdict_equal": a["direct"]["verdict"] == b["direct"]["verdict"],
        "direct_first_open_equal": a["direct"]["first_open_signature"] == b["direct"]["first_open_signature"],
        "m2rs_verdict_equal": a["m2rs"]["verdict"] == b["m2rs"]["verdict"],
    }
    verdict = "MIRROR_CONSENSUS" if all(comparable.values()) else "MIRROR_DIVERGENCE"
    return {
        "N": a["N"],
        "verdict": verdict,
        "checks": comparable,
        "LR_receipt": a["receipt_sha256"],
        "RL_receipt": b["receipt_sha256"],
        "proof_effect": "NONE__EXPERIMENTAL_CROSS_CHECK_ONLY",
    }


def run(lo: int, hi: int, meet_window: int = 2) -> dict[str, Any]:
    if hi < lo:
        raise ValueError("hi must be >= lo")
    forward: list[dict[str, Any]] = []
    reverse: list[dict[str, Any]] = []
    left, right = lo, hi

    # Two ordered streams advance toward each other.
    while left <= right:
        forward.append(visit(left, "LR"))
        reverse.append(visit(right, "RL"))
        left += 1
        right -= 1

    # Tranception-style overlap: both directions independently replay a frozen
    # central window, so meeting is observable rather than symbolic.
    mid = (lo + hi) // 2
    meeting_ns = sorted(set(
        N for N in range(max(lo, mid - meet_window + 1), min(hi, mid + meet_window) + 1)
    ))
    meetings = []
    for N in meeting_ns:
        lr = visit(N, "LR")
        rl = visit(N, "RL")
        meetings.append(compare_mirror(lr, rl))

    all_visits = forward + reverse
    return {
        "schema": "JANUS/MAD-LAB/M2RS-TRANCEPTION-MEET/v1",
        "lane": LANE,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "range": [lo, hi],
        "tranception_source": {
            "repository": "Hawkar-usls/tranception",
            "commit": TRANCEPTION_SOURCE_COMMIT,
            "borrowed": [
                "LR_RL_MIRROR_SCORING",
                "DIRECTION_FLIP",
                "RETRIEVAL_PRIOR_AS_RANKING_AUXILIARY",
            ],
            "not_borrowed": ["PHYSICAL_RETROCAUSALITY", "TRUTH_FROM_MODEL_SCORE"],
        },
        "m2rs_contract": {
            "definition": "MINIMUM_CERTIFIED_SAFE_SELECTOR",
            "exact_bound_dominates_ranking": True,
            "retrieval_prior_changes_truth": False,
            "action_availability_certified": False,
            "same_run_new_lemma_use": False,
            "theorem_credit_allowed": False,
        },
        "forward_visits": forward,
        "reverse_visits": reverse,
        "meeting_window": meeting_ns,
        "meeting_checks": meetings,
        "mirror_divergence_count": sum(m["verdict"] == "MIRROR_DIVERGENCE" for m in meetings),
        "shadow_selector_advantage_count": sum(v["relation"] == "SHADOW_SELECTOR_ADVANTAGE_ONLY" for v in all_visits),
        "both_open_count": sum(v["relation"] == "BOTH_OPEN" for v in all_visits),
        "claim_ceiling": [
            "FINITE_MAD_LAB_PASS_IS_NOT_A_THEOREM",
            "M2RS_SAFE_ABSTRACT_ACTION_IS_NOT_CONCRETE_ACTION_AVAILABILITY",
            "MIRROR_CONSENSUS_IS_NOT_PROOF",
            "NO_THEOREM_RUNTIME_IMPORT",
            "P_VS_NP_OPEN",
        ],
    }


def selftest() -> None:
    # Known N58 direct negative control must remain visible.
    d = direct_replay(58)
    assert d["verdict"] == "OPEN", d
    assert d["first_open_signature"][-4:-1] == [50, 24, 26], d

    # M2R-S may find a shadow path or remain open, but it may never gain theorem authority.
    m = m2rs_selective_closure(58, "LR")
    assert m["theorem_credit_allowed"] is False
    assert m.get("action_availability_certified", False) is False

    # Both directions must agree on the deterministic DIRECT negative control.
    lr, rl = visit(58, "LR"), visit(58, "RL")
    c = compare_mirror(lr, rl)
    assert c["checks"]["direct_verdict_equal"]
    assert c["checks"]["direct_first_open_equal"]
    assert lr["order"] == ["M2R_S", "DIRECT"]
    assert rl["order"] == ["M2R_S", "DIRECT"]
    print("M2RS_TRANCEPTION_N58_NEGATIVE_CONTROL=PASS")
    print(f"M2RS_N58_LR={lr['m2rs']['verdict']}")
    print(f"M2RS_N58_RL={rl['m2rs']['verdict']}")
    print(f"DIRECT_N58={lr['direct']['verdict']}")
    print(f"MEET_N58={c['verdict']}")
    print("ACTION_AVAILABILITY_CERTIFICATE=ABSENT")
    print("THEOREM_CREDIT=DENIED")
    print("P_VS_NP=OPEN")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=58)
    ap.add_argument("--max", type=int, default=61)
    ap.add_argument("--meet-window", type=int, default=1)
    ap.add_argument("--out", type=Path, default=Path("m2rs_tranception_meet.json"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    result = run(args.min, args.max, args.meet_window)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"M2RS_TRANCEPTION_RESULT={args.out}")
    print(f"RANGE={args.min}..{args.max}")
    print(f"MIRROR_DIVERGENCES={result['mirror_divergence_count']}")
    print(f"SHADOW_SELECTOR_ADVANTAGES={result['shadow_selector_advantage_count']}")
    print(f"BOTH_OPEN={result['both_open_count']}")
    print("EXPERIMENTAL_NOT_THEOREM")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
