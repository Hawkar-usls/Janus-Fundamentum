#!/usr/bin/env python3
"""Ascending-prime stress runner for JANUS MAD-LAB.

Runs primes from small to large, by default 2..937. For each prime N it scans
one frozen exact abstract lane: all valid n=7 hard-root boundary states in
canonical (m,d,p) order, and stops at the first unresolved action for that N.
It then continues to the next prime.

This is a stress/discovery experiment, not a theorem frontier. A prime with no
OPEN proves only that this frozen n=7 root lane had no unresolved action under
the currently imported exact bound/repair chain. It does not prove N, skipped
composite sizes, unbounded totality, SAT in P, or P=NP.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from experiments.direct import janus_v05_abstract_frontier_support_mass as A
from experiments.mad_lab.m2r_jump_counter import ActionCandidate
from experiments.mad_lab.m2r_self_repair import M2RSurgeon
from experiments.mad_lab.reverse_prime_probe import is_prime
from experiments.mad_lab.spider_method_gate import FrozenPlan, verify_seal

LANE = "JANUS_MAD_LAB"
STATUS = "EXPERIMENTAL_NOT_THEOREM"
P_VS_NP = "OPEN"
SCOPE = "N7_HARD_ROOT_BOUNDARY_FIRST_OPEN_SCAN"


def primes_ascending(lo: int, hi: int) -> list[int]:
    return [n for n in range(max(2, lo), hi + 1) if is_prime(n)]


def n7_root_states(N: int):
    n = 7
    if N < 1 + n + 7 + 3 * n:
        return
    for m in range(7, N):
        L = N - 1 - n - m
        if L < 3 * n or L < 2 * m or L > n * m:
            continue
        dlo, dhi = A.degree_interval(n, m, L)
        if dlo <= dhi:
            yield m, L, dlo, dhi


def scan_prime(N: int, surgeon: M2RSurgeon) -> dict:
    plan = FrozenPlan(
        experiment_id=f"MAD-ASC-PRIME-N{N}",
        N=N,
        scope=SCOPE,
        action_order="n=7 fixed; m ascending; d ascending; p ascending with p<=q",
        repair_chain=(
            "GLOBAL_RAW",
            "INCIDENCE_SURPLUS",
            "PROVED_N58_LOCAL_RESCUES_THROUGH_23X27_WHEN_APPLICABLE",
        ),
        falsification_rule="First exact unresolved final_raw>N^2 is recorded OPEN and rolled back; never patched in the same run.",
        discovery_or_confirmation="DISCOVERY",
    )
    frozen = plan.seal()
    assert verify_seal(frozen)

    scanned_states = 0
    scanned_actions = 0
    repaired_actions = 0
    max_seen_debt = 0
    max_seen = None

    for m, L, dlo, dhi in n7_root_states(N) or ():
        scanned_states += 1
        for d in range(dlo, dhi + 1):
            for p in range(0, d // 2 + 1):
                q = d - p
                scanned_actions += 1
                action = ActionCandidate(N, 7, m, L, d, p, q, f"N{N}_m{m}_L{L}_d{d}_{p}x{q}")
                r = surgeon.repair(action)
                if r.improvement > 0:
                    repaired_actions += 1
                debt = max(0, r.final_raw - r.cap)
                if debt > max_seen_debt:
                    max_seen_debt = debt
                    max_seen = asdict(r)
                if r.verdict == "OPEN_REPAIR_REQUIRED":
                    return {
                        "N": N,
                        "prime": True,
                        "scope": SCOPE,
                        "verdict": "OPEN",
                        "frozen_plan": frozen,
                        "scanned_states_before_open": scanned_states,
                        "scanned_actions_before_open": scanned_actions,
                        "repaired_actions_before_open": repaired_actions,
                        "first_open": asdict(r),
                        "rollback_performed_logically": True,
                        "claim_ceiling": "FIRST_OPEN_IN_FROZEN_N7_ROOT_LANE_ONLY",
                    }

    return {
        "N": N,
        "prime": True,
        "scope": SCOPE,
        "verdict": "NO_OPEN_IN_SCANNED_LANE",
        "frozen_plan": frozen,
        "scanned_states": scanned_states,
        "scanned_actions": scanned_actions,
        "repaired_actions": repaired_actions,
        "max_seen_debt": max_seen_debt,
        "max_seen": max_seen,
        "claim_ceiling": "N7_ROOT_LANE_ONLY__NOT_FINITE_N_THEOREM",
    }


def run(lo: int = 2, hi: int = 937) -> dict:
    surgeon = M2RSurgeon()
    ps = primes_ascending(lo, hi)
    results = []
    for i, N in enumerate(ps, 1):
        r = scan_prime(N, surgeon)
        results.append(r)
        if r["verdict"] == "OPEN":
            o = r["first_open"]
            print(
                f"PRIME_STRESS {i}/{len(ps)} N={N} OPEN "
                f"raw={o['final_raw']} cap={o['cap']} debt={o['final_raw']-o['cap']} "
                f"label={o['action_label']}"
            )
        else:
            print(
                f"PRIME_STRESS {i}/{len(ps)} N={N} NO_OPEN_IN_SCANNED_LANE "
                f"actions={r['scanned_actions']} repaired={r['repaired_actions']}"
            )

    opens = [r for r in results if r["verdict"] == "OPEN"]
    clean = [r for r in results if r["verdict"] != "OPEN"]
    summary = {
        "schema": "JANUS/MAD-LAB/ASCENDING-PRIME-STRESS/v1",
        "lane": LANE,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "prime_min": lo,
        "prime_max": hi,
        "prime_count": len(ps),
        "scope": SCOPE,
        "discovery_only": True,
        "open_prime_count": len(opens),
        "no_open_in_scanned_lane_count": len(clean),
        "first_open_prime": opens[0]["N"] if opens else None,
        "last_prime_scanned": ps[-1] if ps else None,
        "results": results,
        "scientific_boundary": {
            "proves_composites": False,
            "proves_each_prime_N": False,
            "proves_unbounded_totality": False,
            "pattern_hits_require_future_frozen_confirmation": True,
            "same_run_new_lemma_use": False,
            "P_VS_NP": "OPEN"
        }
    }
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=2)
    ap.add_argument("--max", type=int, default=937)
    ap.add_argument("--out", type=Path, default=Path("prime_stress_result.json"))
    args = ap.parse_args()
    if args.max < args.min:
        raise SystemExit("--max must be >= --min")
    result = run(args.min, args.max)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"ASCENDING_PRIME_STRESS_RESULT={args.out}")
    print(f"ASCENDING_PRIME_STRESS_PRIMES={result['prime_count']}")
    print(f"ASCENDING_PRIME_STRESS_OPEN_PRIMES={result['open_prime_count']}")
    print("DISCOVERY_ONLY__NOT_THEOREM")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
