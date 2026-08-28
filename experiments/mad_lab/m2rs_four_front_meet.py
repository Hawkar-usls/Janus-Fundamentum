#!/usr/bin/env python3
"""JANUS MAD-LAB: four-front exact-spectrum meet.

Four independent deterministic fronts interrogate one fixed target-degree
polarity line p+q=d:

    EDGE_LEFT      0:d  -> center
    CENTER_LEFT    center -> 0:d
    CENTER_RIGHT   center -> d:0
    EDGE_RIGHT     d:0  -> center

The fronts do not vote on truth.  Every visited row is recomputed through the
pre-existing proof-gated ``exact_action_bound``.  Direction changes only visit
order.  The useful event is a *verdict-front collision*: an edge-born LAND
region and a center-born OPEN region independently discover the same adjacent
boundary from opposite directions.

For even d the two center fronts intentionally start from the same balanced
split as two labelled copies.  This is a traversal device, not duplicate proof
credit.  Mirror equality is checked explicitly on the unfolded signed line.

BOUND_SAFE != CONCRETE_PIVOT_AVAILABILITY_PROVED.
P vs NP remains OPEN.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from experiments.mad_lab import m2rs_tranception_meet as M

LANE = "JANUS_MAD_LAB_M2RS_FOUR_FRONT_MEET"
STATUS = "EXPERIMENTAL_SHADOW_ONLY"
P_VS_NP = "OPEN"
THEOREM_CREDIT_ALLOWED = False


def row(N: int, state: tuple[int, int, int], d: int, p: int) -> dict[str, Any]:
    n, m, L = state
    q = d - p
    a = dict(M.exact_action_bound(N, n, m, L, d, p, q))
    return {
        "p": p,
        "q": q,
        "B": int(a["raw_final"]),
        "raw_base": int(a["raw_base"]),
        "m_out": int(a["m_out"]),
        "L_out": int(a["L_out"]),
        "R_or_J": int(a["R_or_J"]),
        "provider": a["provider"],
        "cap_safe": bool(a["cap_safe"]),
        "verdict": "LAND" if a["cap_safe"] else "OPEN",
    }


def signed_spectrum(N: int, state: tuple[int, int, int], d: int) -> list[dict[str, Any]]:
    return [row(N, state, d, p) for p in range(d + 1)]


def mirror_check(spec: list[dict[str, Any]]) -> dict[str, Any]:
    fields = ["B", "raw_base", "m_out", "L_out", "R_or_J", "provider", "cap_safe"]
    mismatches: list[dict[str, Any]] = []
    d = len(spec) - 1
    for p in range(d + 1):
        q = d - p
        a, b = spec[p], spec[q]
        bad = [f for f in fields if a[f] != b[f]]
        if bad:
            mismatches.append({"p": p, "mirror_p": q, "fields": bad})
    return {
        "checked_fields": fields,
        "exact_signed_mirror": not mismatches,
        "mismatches": mismatches,
    }


def advance_until_flip(
    spec: list[dict[str, Any]],
    start: int,
    step: int,
    stop: int,
    label: str,
) -> dict[str, Any]:
    origin = spec[start]["verdict"]
    visited: list[int] = []
    p = start
    last_same: int | None = None
    first_flip: int | None = None
    while 0 <= p < len(spec):
        visited.append(p)
        if spec[p]["verdict"] == origin:
            last_same = p
        else:
            first_flip = p
            break
        if p == stop:
            break
        p += step
    return {
        "label": label,
        "start_p": start,
        "step": step,
        "origin_verdict": origin,
        "visited_p": visited,
        "last_same_p": last_same,
        "first_flip_p": first_flip,
        "front_receipt_sha256": M.digest([
            [x, spec[x]["B"], spec[x]["verdict"], spec[x]["provider"]]
            for x in visited
        ]),
    }


def boundary_meet(
    spec: list[dict[str, Any]],
    a: dict[str, Any],
    b: dict[str, Any],
    side: str,
) -> dict[str, Any]:
    # Exact collision means both opposing fronts independently identify the
    # same two adjacent signed polarity positions, in reverse roles.
    a0, a1 = a["last_same_p"], a["first_flip_p"]
    b0, b1 = b["last_same_p"], b["first_flip_p"]
    exact = (
        a0 is not None and a1 is not None and b0 is not None and b1 is not None
        and a0 == b1 and a1 == b0 and abs(a0 - a1) == 1
    )
    pair = None
    if exact:
        lo, hi = sorted((a0, a1))
        pair = {
            "positions": [lo, hi],
            "rows": [spec[lo], spec[hi]],
            "opposite_verdicts": spec[lo]["verdict"] != spec[hi]["verdict"],
            "exact_replay_sha256": M.digest([
                [lo, spec[lo]["B"], spec[lo]["provider"], spec[lo]["verdict"]],
                [hi, spec[hi]["B"], spec[hi]["provider"], spec[hi]["verdict"]],
            ]),
        }
    return {
        "side": side,
        "status": "EXACT_VERDICT_FRONT_MEET" if exact else "NO_EXACT_VERDICT_FRONT_MEET",
        "front_a": a["label"],
        "front_b": b["label"],
        "boundary": pair,
        "truth_effect": "NONE__LOCALIZES_EXISTING_EXACT_BOUNDARY_ONLY",
    }


def four_front_probe(
    N: int,
    state: tuple[int, int, int],
    d: int,
    target_p: int | None = None,
) -> dict[str, Any]:
    spec = signed_spectrum(N, state, d)
    cap = N * N
    mid_left = d // 2
    mid_right = (d + 1) // 2

    fronts = {
        "edge_left": advance_until_flip(spec, 0, +1, mid_left, "EDGE_LEFT"),
        "center_left": advance_until_flip(spec, mid_left, -1, 0, "CENTER_LEFT"),
        "center_right": advance_until_flip(spec, mid_right, +1, d, "CENTER_RIGHT"),
        "edge_right": advance_until_flip(spec, d, -1, mid_right, "EDGE_RIGHT"),
    }
    left_meet = boundary_meet(spec, fronts["edge_left"], fronts["center_left"], "LEFT")
    right_meet = boundary_meet(spec, fronts["center_right"], fronts["edge_right"], "RIGHT")
    mirror = mirror_check(spec)

    target = None if target_p is None else spec[target_p]
    unsafe_positions = [r["p"] for r in spec if not r["cap_safe"]]
    safe_positions = [r["p"] for r in spec if r["cap_safe"]]

    result = {
        "lane": LANE,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "N": N,
        "cap": cap,
        "state": list(state),
        "target_degree": d,
        "signed_position_count": len(spec),
        "center_positions": [mid_left, mid_right],
        "four_front_contract": {
            "fronts": ["EDGE_LEFT", "CENTER_LEFT", "CENTER_RIGHT", "EDGE_RIGHT"],
            "movement": "EDGE_TO_CENTER_AND_CENTER_TO_EDGE_SIMULTANEOUSLY",
            "ranking_changes_truth": False,
            "same_run_lemma_promotion": False,
            "concrete_pivot_availability_proved": False,
            "theorem_credit_allowed": THEOREM_CREDIT_ALLOWED,
        },
        "mirror_check": mirror,
        "fronts": fronts,
        "meetings": [left_meet, right_meet],
        "double_exact_verdict_front_meet": (
            left_meet["status"] == "EXACT_VERDICT_FRONT_MEET"
            and right_meet["status"] == "EXACT_VERDICT_FRONT_MEET"
        ),
        "unsafe_positions": unsafe_positions,
        "safe_position_count": len(safe_positions),
        "unsafe_position_count": len(unsafe_positions),
        "target": target,
        "signed_spectrum": spec,
        "anti_self_deception_gate": {
            "abstract_signed_actions_only": True,
            "concrete_cnf_realizability_proved": False,
            "concrete_pivot_availability_proved": False,
            "theorem_credit_allowed": False,
            "claim_ceiling": "EXACT_ABSTRACT_VERDICT_BOUNDARY_LOCALIZATION_ONLY",
        },
        "theorem_verdict": "OPEN_REPAIR_REQUIRED",
    }
    result["result_sha256"] = M.digest(result)
    return result


def prime_first_open_four_front(N: int) -> dict[str, Any]:
    direct = M.direct_replay(N)
    sig = direct["first_open_signature"]
    if sig is None:
        return {
            "N": N,
            "direct_verdict": direct["verdict"],
            "probe": None,
            "theorem_credit_allowed": False,
            "P_VS_NP": "OPEN",
        }
    n, m, L, d, p, q, B = map(int, sig)
    probe = four_front_probe(N, (n, m, L), d, p)
    return {
        "N": N,
        "direct_verdict": direct["verdict"],
        "first_open_signature": sig,
        "first_open_replayed_B": probe["target"]["B"],
        "first_open_B_matches": probe["target"]["B"] == B,
        "double_exact_verdict_front_meet": probe["double_exact_verdict_front_meet"],
        "left_boundary": probe["meetings"][0]["boundary"],
        "right_boundary": probe["meetings"][1]["boundary"],
        "mirror_exact": probe["mirror_check"]["exact_signed_mirror"],
        "probe_sha256": probe["result_sha256"],
        "theorem_credit_allowed": False,
        "P_VS_NP": "OPEN",
    }


def selftest() -> None:
    current = four_front_probe(58, (7, 79, 350), 50, 25)
    historic = four_front_probe(58, (7, 78, 350), 50, 24)

    assert current["target"]["B"] == 3433
    assert current["target"]["verdict"] == "OPEN"
    assert current["mirror_check"]["exact_signed_mirror"], current["mirror_check"]
    assert current["double_exact_verdict_front_meet"], current["meetings"]
    assert current["meetings"][0]["boundary"]["positions"] == [20, 21]
    assert current["meetings"][1]["boundary"]["positions"] == [29, 30]
    assert current["unsafe_positions"] == list(range(21, 30))

    assert historic["target"]["verdict"] == "OPEN"
    assert historic["mirror_check"]["exact_signed_mirror"], historic["mirror_check"]
    assert historic["double_exact_verdict_front_meet"], historic["meetings"]
    # Existing pre-proved rescues leave only the narrow 24:26..26:24 ridge.
    assert historic["unsafe_positions"] == [24, 25, 26]
    assert historic["meetings"][0]["boundary"]["positions"] == [23, 24]
    assert historic["meetings"][1]["boundary"]["positions"] == [26, 27]
    assert current["P_VS_NP"] == "OPEN"
    assert not current["anti_self_deception_gate"]["theorem_credit_allowed"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/mad_lab/m2rs_four_front_meet.json"))
    ap.add_argument("--skip-primes", action="store_true")
    args = ap.parse_args()

    selftest()
    current = four_front_probe(58, (7, 79, 350), 50, 25)
    historic = four_front_probe(58, (7, 78, 350), 50, 24)
    primes = [] if args.skip_primes else [
        prime_first_open_four_front(N) for N in [59, 61, 67, 71, 73, 79, 83, 89, 97]
    ]

    payload = {
        "schema": "JANUS/MAD-LAB/M2RS-FOUR-FRONT-MEET/v1",
        "lane": LANE,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "source_branch": "research/janus-mad-lab-m2rs-state-spectrum-meet-2026-08-28",
        "current_door": current,
        "historic_descendant": historic,
        "prime_stress_59_97": primes,
        "final_claim": (
            "FOUR FRONTS MAY LOCALIZE EXACT ABSTRACT LAND/OPEN BOUNDARIES FROM BOTH DIRECTIONS; "
            "THEY DO NOT PROVE CONCRETE CNF REALIZABILITY OR PIVOT AVAILABILITY. P_VS_NP=OPEN."
        ),
    }
    payload["audit_sha256"] = M.digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
