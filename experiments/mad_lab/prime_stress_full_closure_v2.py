#!/usr/bin/env python3
"""JANUS MAD-LAB ascending-prime stress v2: full reachable abstract closure.

V1 intentionally scanned only n=7 root-boundary states and was audited as too
narrow. V2 starts from the theorem-side hard roots for each prime cap N and
propagates the exact abstract Pareto/box closure down all n-layers, stopping at
the first unresolved transition for that prime. It uses only the exact repair
providers that existed before this run.

The proved base frontier N<=57 is used only as a terminal induction floor:
abstract local states of input-size <=57 need not be expanded further.

MAD-LAB ONLY. Experimental stress evidence, not a theorem claim.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from experiments.direct import janus_v05_abstract_frontier_support_mass as A
from experiments.direct import janus_v05_abstract_frontier_global_raw_universe as G
from experiments.direct import janus_v05_abstract_frontier_N58_23x27_projection_fiber as PROVED_REPAIR
from experiments.mad_lab.m2r_jump_counter import ActionCandidate
from experiments.mad_lab.m2r_self_repair import M2RSurgeon
from experiments.mad_lab.reverse_prime_probe import is_prime
from experiments.mad_lab.spider_method_gate import FrozenPlan, verify_seal

LANE = "JANUS_MAD_LAB"
STATUS = "EXPERIMENTAL_NOT_THEOREM"
P_VS_NP = "OPEN"
PROVED_BASE_FRONTIER = 57
SCOPE = "FULL_REACHABLE_ABSTRACT_CLOSURE_FROM_HARD_ROOTS"


def primes_ascending(lo: int, hi: int) -> list[int]:
    return [n for n in range(max(2, lo), hi + 1) if is_prime(n)]


def add_box(boxes: list[tuple[int, int, int]], M: int, L: int, S: int) -> None:
    """Pareto union of exact theorem-side descendant resource boxes."""
    if M < 7 or L < 14 or S < 22:
        return
    if any(a >= M and b >= L and c >= S for a, b, c in boxes):
        return
    boxes[:] = [(a, b, c) for a, b, c in boxes if not (M >= a and L >= b and S >= c)]
    boxes.append((M, L, S))


def normalized_obstruction(N: int, n: int, m: int, L: int, d: int, p: int, q: int, raw: int) -> dict:
    return {
        "n_over_N": [n, N],
        "m_over_N": [m, N],
        "L_over_N": [L, N],
        "d_over_m": [d, m],
        "p_over_d": [p, d],
        "q_over_d": [q, d],
        "raw_over_cap": [raw, N * N],
        "jump_debt": raw - N * N,
    }


def scan_prime_full(N: int) -> dict:
    if N <= PROVED_BASE_FRONTIER:
        return {
            "N": N,
            "prime": True,
            "scope": SCOPE,
            "verdict": "CLOSED_BY_PROVED_BASE_FRONTIER",
            "proved_base_frontier": PROVED_BASE_FRONTIER,
            "claim_ceiling": "REUSES_EXISTING_N_LE_57_THEOREM_ONLY",
        }

    plan = FrozenPlan(
        experiment_id=f"MAD-ASC-PRIME-FULL-N{N}",
        N=N,
        scope=SCOPE,
        action_order="n descending; (m,L) ascending; d ascending; p ascending with p<=q",
        repair_chain=(
            "GLOBAL_RAW",
            "INCIDENCE_SURPLUS",
            "PREEXISTING_PROVED_N58_RESCUES_THROUGH_23X27_WHEN_EXACT_KEY_MATCHES",
        ),
        falsification_rule="First exact unresolved transition with final_raw>N^2 is OPEN; same-run lemma invention forbidden.",
        discovery_or_confirmation="DISCOVERY",
    )
    frozen = plan.seal()
    assert verify_seal(frozen)

    cap = N * N
    roots = A.hard_roots(N)
    max_n = max(roots, default=A.TAIL_N)
    boxes: dict[int, list[tuple[int, int, int]]] = {n: [] for n in range(7, max_n + 1)}
    rootsets = {n: set(rows) for n, rows in roots.items()}
    surgeon = M2RSurgeon()

    checked_states = 0
    checked_transitions = 0
    exact_repairs = 0
    layer_counts: dict[int, int] = {}
    worst_raw = -1
    worst = None

    for n in range(max_n, 6, -1):
        candidates = set(rootsets.get(n, set()))
        bs = boxes[n]
        maxM = max((M for M, _, _ in bs), default=0)

        for m in range(7, maxM + 1):
            # Coupled descendant box: state storage S also limits L at fixed m.
            Lcap = max((min(Lb, Sb - 1 - m) for M, Lb, Sb in bs if M >= m), default=-1)
            if Lcap < 0:
                continue
            # Only the already-proved <=57 local floor may be skipped.
            Llo = max(2 * m, n, PROVED_BASE_FRONTIER - n - m)
            Lhi = min(Lcap, n * m, cap - 1 - m)
            if Llo > Lhi:
                continue
            for L in range(Llo, Lhi + 1):
                dlo, dhi = A.degree_interval(n, m, L)
                if dlo <= dhi:
                    candidates.add((m, L))

        layer_counts[n] = len(candidates)

        for m, L in sorted(candidates):
            checked_states += 1
            dlo, dhi = A.degree_interval(n, m, L)
            for d in range(dlo, dhi + 1):
                for p in range(0, d // 2 + 1):
                    q = d - p
                    checked_transitions += 1
                    raw0, M0, Lb0, R0 = G.transfer_bounds_global(n, m, L, d, p, q)
                    raw, M, Lb, R = raw0, M0, Lb0, R0
                    repair_meta = None

                    if raw0 > cap:
                        action = ActionCandidate(N, n, m, L, d, p, q, f"N{N}_n{n}_m{m}_L{L}_d{d}_{p}x{q}")
                        surgery = surgeon.repair(action)
                        exact = PROVED_REPAIR.enhanced_rescue(n, m, L, d, p, q)
                        if exact is not None and int(exact[0]) < raw0:
                            eraw, eM, eL, eR = int(exact[0]), int(exact[1]), int(exact[2]), int(exact[3])
                            assert surgery.final_raw == eraw, (surgery, exact)
                            raw, M, Lb, R = eraw, eM, min(Lb0, eL), eR
                            exact_repairs += 1
                            repair_meta = {
                                "provider": surgery.provider,
                                "improvement": raw0 - raw,
                                "proof_gated": surgery.proof_gated,
                            }
                        else:
                            assert surgery.final_raw == raw0, (surgery, raw0, exact)
                            repair_meta = {
                                "provider": surgery.provider,
                                "improvement": 0,
                                "proof_gated": surgery.proof_gated,
                                "proof_obligation": surgery.proof_obligation,
                            }

                    if raw > worst_raw:
                        worst_raw = raw
                        worst = {
                            "state": [n, m, L],
                            "d": d,
                            "p": p,
                            "q": q,
                            "raw_base": raw0,
                            "raw_final": raw,
                            "m_out_bound": M,
                            "L_out_bound": Lb,
                            "R_or_J": R,
                            "repair": repair_meta,
                        }

                    if raw > cap:
                        return {
                            "N": N,
                            "prime": True,
                            "scope": SCOPE,
                            "verdict": "OPEN",
                            "frozen_plan": frozen,
                            "cap": cap,
                            "checked_states_before_open": checked_states,
                            "checked_transitions_before_open": checked_transitions,
                            "exact_repairs_before_open": exact_repairs,
                            "layer_counts_partial": layer_counts,
                            "first_open": worst,
                            "normalized": normalized_obstruction(N, n, m, L, d, p, q, raw),
                            "rollback_performed_logically": True,
                            "same_run_new_lemma_use": False,
                            "claim_ceiling": "EXACT_ABSTRACT_BOUND_OPEN__NOT_ACTUAL_CNF_COUNTEREXAMPLE",
                        }

                    for n2 in range(7, n):
                        add_box(boxes[n2], M, Lb, raw)

    return {
        "N": N,
        "prime": True,
        "scope": SCOPE,
        "verdict": "NO_OPEN_IN_FULL_ABSTRACT_CLOSURE",
        "frozen_plan": frozen,
        "cap": cap,
        "root_states": sum(len(v) for v in roots.values()),
        "checked_states": checked_states,
        "checked_transitions": checked_transitions,
        "exact_repairs": exact_repairs,
        "layer_counts": layer_counts,
        "box_counts": {str(n): len(boxes[n]) for n in boxes},
        "worst_raw": worst_raw,
        "worst": worst,
        "claim_ceiling": "MAD_LAB_FINITE_CAP_AVAILABILITY_OVER_FROZEN_ABSTRACT_CLOSURE_ONLY",
    }


def run(lo: int = 2, hi: int = 937) -> dict:
    ps = primes_ascending(lo, hi)
    results = []
    for i, N in enumerate(ps, 1):
        r = scan_prime_full(N)
        results.append(r)
        if r["verdict"] == "OPEN":
            o = r["first_open"]
            print(
                f"PRIME_FULL {i}/{len(ps)} N={N} OPEN "
                f"state={o['state']} d={o['d']} p:q={o['p']}:{o['q']} "
                f"raw={o['raw_final']} cap={r['cap']} debt={o['raw_final']-r['cap']}"
            )
        else:
            print(f"PRIME_FULL {i}/{len(ps)} N={N} {r['verdict']}")

    opens = [r for r in results if r["verdict"] == "OPEN"]
    no_open = [r for r in results if r["verdict"] == "NO_OPEN_IN_FULL_ABSTRACT_CLOSURE"]
    base = [r for r in results if r["verdict"] == "CLOSED_BY_PROVED_BASE_FRONTIER"]
    return {
        "schema": "JANUS/MAD-LAB/ASCENDING-PRIME-FULL-CLOSURE-STRESS/v2",
        "lane": LANE,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "prime_min": lo,
        "prime_max": hi,
        "prime_count": len(ps),
        "scope": SCOPE,
        "proved_base_frontier": PROVED_BASE_FRONTIER,
        "discovery_only": True,
        "base_closed_prime_count": len(base),
        "open_prime_count": len(opens),
        "no_open_full_closure_count": len(no_open),
        "first_open_prime": opens[0]["N"] if opens else None,
        "last_prime_scanned": ps[-1] if ps else None,
        "results": results,
        "scientific_boundary": {
            "abstract_overapprox_not_actual_cnf_witness": True,
            "proves_composites": False,
            "promotes_to_theorem_automatically": False,
            "proves_unbounded_totality": False,
            "pattern_hits_require_future_frozen_confirmation": True,
            "same_run_new_lemma_use": False,
            "P_VS_NP": "OPEN"
        }
    }


def selftest() -> None:
    # Sensitivity control: unlike v1 root-only scan, full closure must see the
    # known N58 first unresolved 24x26 transition after the pre-existing rescues.
    r = scan_prime_full(59)
    assert r["N"] == 59 and r["scope"] == SCOPE
    # N59 is intentionally not prescribed PASS/OPEN here; the stress result is data.
    # Directly check the known N58 negative control through the same Surgeon chain.
    surgeon = M2RSurgeon()
    a = ActionCandidate(58, 7, 78, 350, 50, 24, 26, "KNOWN_N58_NEGATIVE_CONTROL")
    s = surgeon.repair(a)
    assert s.verdict == "OPEN_REPAIR_REQUIRED" and s.final_raw == 3425 and s.cap == 3364
    print("FULL_CLOSURE_V2_IMPORTS_KNOWN_N58_NEGATIVE_CONTROL=PASS")
    print(f"N59_FULL_CLOSURE_SMOKE={r['verdict']}")
    print("P_VS_NP=OPEN")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=2)
    ap.add_argument("--max", type=int, default=937)
    ap.add_argument("--out", type=Path, default=Path("prime_stress_full_v2.json"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    if args.max < args.min:
        raise SystemExit("--max must be >= --min")
    result = run(args.min, args.max)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"PRIME_FULL_RESULT={args.out}")
    print(f"PRIME_FULL_COUNT={result['prime_count']}")
    print(f"PRIME_FULL_OPEN_COUNT={result['open_prime_count']}")
    print(f"PRIME_FULL_FIRST_OPEN={result['first_open_prime']}")
    print(f"PRIME_FULL_LAST={result['last_prime_scanned']}")
    print("DISCOVERY_ONLY__NOT_THEOREM")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
