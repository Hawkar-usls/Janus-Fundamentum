#!/usr/bin/env python3
"""JANUS MAD-LAB successor: theorem-safe M2R-S state-spectrum meet probe.

Purpose
-------
Interrogate a *specific reachable abstract state* instead of allowing the
selector to hide the obstruction by moving elsewhere in the graph.

The experiment has two opposing lanes inspired by Tranception's mirror idea:

  FORWARD: M2R-S(LR) -> DIRECT target replay
  REVERSE: M2R-S(RL) -> DIRECT target replay

LR/RL/mirror logic is ranking only.  It never changes an exact proof bound,
never creates an action, and never promotes an OPEN theorem verdict.

Most important anti-self-deception gate:
  BOUND_SAFE != PIVOT_AVAILABILITY_PROVED.

This file can prove that an *abstract action class* has B <= N^2.  It cannot,
by itself, prove that every concrete CNF represented by the state contains a
pivot realizing that class.  Therefore theorem credit remains blocked unless
an external pre-existing availability certificate is supplied.

P vs NP remains OPEN.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from experiments.direct import janus_v05_abstract_frontier_support_mass as A
from experiments.mad_lab import m2rs_tranception_meet as M

LANE = "JANUS_MAD_LAB_M2RS_STATE_SPECTRUM_MEET"
STATUS = "EXPERIMENTAL_SHADOW_ONLY"
P_VS_NP = "OPEN"
PIVOT_AVAILABILITY_AUTHORITY = False


def enumerate_actions(N: int, state: tuple[int, int, int]) -> list[dict[str, Any]]:
    n, m, L = state
    dlo, dhi = A.degree_interval(n, m, L)
    out: list[dict[str, Any]] = []
    if dlo > dhi:
        return out
    for d in range(dlo, dhi + 1):
        for p in range(0, d // 2 + 1):
            q = d - p
            a = dict(M.exact_action_bound(N, n, m, L, d, p, q))
            a["polarity_class"] = "PURE" if p == 0 or q == 0 else "MIXED"
            a["balance"] = min(p, q)
            a["pivot_availability_proved"] = PIVOT_AVAILABILITY_AUTHORITY
            a["theorem_usable"] = bool(a["cap_safe"] and PIVOT_AVAILABILITY_AUTHORITY)
            out.append(a)
    return out


def canonical_row(a: dict[str, Any]) -> list[int]:
    return [
        int(a["d"]), int(a["p"]), int(a["q"]), int(a["raw_base"]),
        int(a["raw_final"]), int(a["m_out"]), int(a["L_out"]), int(a["R_or_J"]),
    ]


def choose(actions: list[dict[str, Any]], direction: str) -> dict[str, Any] | None:
    if not actions:
        return None
    # No mutable retrieval prior in this state probe: the mirror may reverse
    # late tie order, but exact proof resources dominate ranking.
    chosen = min(actions, key=lambda a: M.action_key(a, direction, None))
    return dict(chosen)


def replay_certificate(N: int, state: tuple[int, int, int], chosen: dict[str, Any]) -> dict[str, Any]:
    n, m, L = state
    fresh = M.exact_action_bound(
        N, n, m, L, int(chosen["d"]), int(chosen["p"]), int(chosen["q"])
    )
    fields = ["raw_base", "raw_final", "m_out", "L_out", "R_or_J", "provider", "cap_safe"]
    equal = all(fresh[k] == chosen[k] for k in fields)
    return {
        "exact_inverse_witness_replay": equal,
        "replayed": fresh,
        "checked_fields": fields,
        "replay_digest": M.digest(canonical_row(fresh)),
    }


def row_for(actions: list[dict[str, Any]], d: int, p: int, q: int) -> dict[str, Any] | None:
    lo, hi = sorted((p, q))
    for a in actions:
        if int(a["d"]) == d and int(a["p"]) == lo and int(a["q"]) == hi:
            return dict(a)
    return None


def spectrum_for_d(actions: list[dict[str, Any]], d: int) -> list[dict[str, Any]]:
    rows = [a for a in actions if int(a["d"]) == d]
    rows.sort(key=lambda a: (int(a["p"]), int(a["q"])))
    return [{
        "p": int(a["p"]), "q": int(a["q"]),
        "raw_base": int(a["raw_base"]), "B": int(a["raw_final"]),
        "provider": a["provider"], "cap_safe": bool(a["cap_safe"]),
        "pivot_availability_proved": bool(a["pivot_availability_proved"]),
    } for a in rows]


def probe_state(
    N: int,
    state: tuple[int, int, int],
    target: tuple[int, int, int],
) -> dict[str, Any]:
    actions = enumerate_actions(N, state)
    cap = N * N
    lr = choose(actions, "LR")
    rl = choose(actions, "RL")
    assert lr is not None and rl is not None

    lr_replay = replay_certificate(N, state, lr)
    rl_replay = replay_certificate(N, state, rl)
    candidate_digest = M.digest([canonical_row(a) for a in actions])
    target_row = row_for(actions, *target)
    assert target_row is not None

    safe = [a for a in actions if a["cap_safe"]]
    mixed = [a for a in actions if a["p"] > 0 and a["q"] > 0]
    safe_mixed = [a for a in mixed if a["cap_safe"]]
    best_mixed = min(safe_mixed, key=lambda a: M.action_key(a, "LR", None)) if safe_mixed else None

    same_cert = canonical_row(lr) == canonical_row(rl)
    exact_replay = bool(lr_replay["exact_inverse_witness_replay"] and rl_replay["exact_inverse_witness_replay"])
    meet = "EXACT_CERTIFICATE_MEET" if same_cert and exact_replay else "MIRROR_RANKING_DIVERGENCE"

    # The target action is the DIRECT/personal step.  A safe alternative is
    # shadow evidence only until concrete pivot availability is certified.
    target_direct = {
        "action": [int(target_row["d"]), int(target_row["p"]), int(target_row["q"])],
        "B": int(target_row["raw_final"]),
        "cap": cap,
        "verdict": "LAND" if target_row["cap_safe"] else "OPEN",
        "provider": target_row["provider"],
    }

    abstract_safe_exists = bool(safe)
    availability_proved = PIVOT_AVAILABILITY_AUTHORITY
    theorem_land = bool(abstract_safe_exists and availability_proved)

    result = {
        "lane": LANE,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "N": N,
        "cap": cap,
        "state": list(state),
        "degree_interval": list(A.degree_interval(*state)),
        "candidate_count": len(actions),
        "candidate_set_digest": candidate_digest,
        "execution_order": {
            "forward": ["M2R_S_LR", "DIRECT_TARGET"],
            "reverse": ["M2R_S_RL", "DIRECT_TARGET_MIRROR_REPLAY"],
        },
        "forward_m2rs": {
            "selected": canonical_row(lr),
            "provider": lr["provider"],
            "bound_safe": bool(lr["cap_safe"]),
            "pivot_availability_proved": False,
            "theorem_credit_allowed": False,
            "replay": lr_replay,
        },
        "reverse_m2rs": {
            "selected": canonical_row(rl),
            "provider": rl["provider"],
            "bound_safe": bool(rl["cap_safe"]),
            "pivot_availability_proved": False,
            "theorem_credit_allowed": False,
            "replay": rl_replay,
        },
        "meet": {
            "status": meet,
            "same_normalized_certificate": same_cert,
            "exact_inverse_witness_replay": exact_replay,
            "truth_effect": "NONE__CONSISTENCY_CHECK_ONLY",
        },
        "direct_target": target_direct,
        "min_abstract_B": min(int(a["raw_final"]) for a in actions),
        "min_abstract_action": canonical_row(min(actions, key=lambda a: M.action_key(a, "LR", None))),
        "min_mixed_B": None if best_mixed is None else int(best_mixed["raw_final"]),
        "min_mixed_action": None if best_mixed is None else canonical_row(best_mixed),
        "safe_abstract_count": len(safe),
        "safe_mixed_count": len(safe_mixed),
        "fixed_target_degree_spectrum": spectrum_for_d(actions, target[0]),
        "anti_self_deception_gate": {
            "bound_safe_abstract_class_exists": abstract_safe_exists,
            "pivot_availability_proved": availability_proved,
            "theorem_land": theorem_land,
            "same_run_lemma_promotion": False,
            "claim_ceiling": "ABSTRACT_SAFE_ACTION_CLASS_ONLY__CONCRETE_PIVOT_AVAILABILITY_UNPROVED",
        },
        "theorem_verdict": "OPEN_REPAIR_REQUIRED" if not theorem_land else "REPAIRED_LAND",
    }
    result["result_sha256"] = M.digest(result)
    return result


def prime_shadow_regression(primes: list[int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for N in primes:
        r = M.run_case(N)
        rows.append({
            "N": N,
            "direct": r["direct_verdict"],
            "m2rs_lr": r["m2rs_lr_verdict"],
            "m2rs_rl": r["m2rs_rl_verdict"],
            "meet": r["mirror_meet_status"],
            "theorem_credit_allowed": r["theorem_credit_allowed"],
            "P_VS_NP": r["P_VS_NP"],
        })
    return rows


def selftest() -> None:
    current = probe_state(58, (7, 79, 350), (50, 25, 25))
    historic = probe_state(58, (7, 78, 350), (50, 24, 26))

    assert current["direct_target"]["B"] == 3433
    assert current["direct_target"]["verdict"] == "OPEN"
    assert historic["direct_target"]["verdict"] == "OPEN"
    assert current["anti_self_deception_gate"]["bound_safe_abstract_class_exists"]
    assert not current["anti_self_deception_gate"]["pivot_availability_proved"]
    assert current["theorem_verdict"] == "OPEN_REPAIR_REQUIRED"
    assert historic["theorem_verdict"] == "OPEN_REPAIR_REQUIRED"
    assert current["meet"]["exact_inverse_witness_replay"]
    assert historic["meet"]["exact_inverse_witness_replay"]
    assert current["P_VS_NP"] == "OPEN"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/mad_lab/m2rs_state_spectrum_meet.json"))
    ap.add_argument("--skip-primes", action="store_true")
    args = ap.parse_args()

    selftest()
    current = probe_state(58, (7, 79, 350), (50, 25, 25))
    historic = probe_state(58, (7, 78, 350), (50, 24, 26))
    primes = [] if args.skip_primes else prime_shadow_regression([59, 61, 67, 71, 73, 79, 83, 89, 97])

    payload = {
        "lane": LANE,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "source_branch": "research/janus-mad-lab-m2rs-tranception-meet-2026-08-28",
        "current_door": current,
        "historic_descendant": historic,
        "prime_stress_59_97": primes,
        "negative_control": {
            "N": 58,
            "role": "CURRENT_DOOR_CAP_AUTHORITY",
            "cap": 58 * 58,
            "theorem_credit_allowed": False,
        },
        "final_claim": "M2R-S MAY RANK PROOF-GATED ABSTRACT ACTIONS; IT DOES NOT PROVE THEIR CONCRETE AVAILABILITY. P_VS_NP=OPEN.",
    }
    payload["audit_sha256"] = M.digest(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
