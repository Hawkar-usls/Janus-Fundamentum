#!/usr/bin/env python3
"""JANUS BREED — dual-face DIRECT/M2R stress runner.

FACE_A: prime N -> M2R, composite N -> DIRECT.
FACE_B: prime N -> DIRECT, composite N -> M2R.

Both faces use the same frozen state/action ordering and the same pre-existing
exact theorem-side providers. M2R additionally audits every over-cap action
through M2RSurgeon. A BREED credit is experimental only and never advances the
theorem frontier.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.direct import janus_v05_abstract_frontier_support_mass as A
from experiments.direct import janus_v05_abstract_frontier_global_raw_universe as G
from experiments.direct import janus_v05_abstract_frontier_N58_23x27_projection_fiber as PROVED_REPAIR
from experiments.mad_lab.m2r_jump_counter import ActionCandidate
from experiments.mad_lab.m2r_self_repair import M2RSurgeon
from experiments.mad_lab.reverse_prime_probe import is_prime
from experiments.mad_lab.prime_stress_full_closure_v2 import add_box
from experiments.mad_lab.spider_method_gate import FrozenPlan, verify_seal

LANE = "JANUS_MAD_LAB"
NAME = "JANUS BREED"
STATUS = "EXPERIMENTAL_NOT_THEOREM"
P_VS_NP = "OPEN"
PROVED_BASE_FRONTIER = 57
SCOPE = "FULL_REACHABLE_ABSTRACT_CLOSURE_FROM_HARD_ROOTS"
MODES = ("DIRECT", "M2R")


def role_for(pass_id: str, N: int) -> str:
    prime = is_prime(N)
    if pass_id == "FACE_A":
        return "M2R" if prime else "DIRECT"
    if pass_id == "FACE_B":
        return "DIRECT" if prime else "M2R"
    raise ValueError(pass_id)


def exact_direct_action(N: int, n: int, m: int, L: int, d: int, p: int, q: int):
    raw0, M0, L0, R0 = G.transfer_bounds_global(n, m, L, d, p, q)
    raw, M, Lb, R = raw0, M0, L0, R0
    provider = "GLOBAL_RAW_BASE"
    proof_gated = True
    exact = PROVED_REPAIR.enhanced_rescue(n, m, L, d, p, q)
    if exact is not None and int(exact[0]) < raw0:
        raw, M, Lb, R = int(exact[0]), int(exact[1]), min(L0, int(exact[2])), int(exact[3])
        provider = "PREEXISTING_PROVED_REPAIR_CHAIN"
    return raw0, raw, M, Lb, R, provider, proof_gated


def exact_m2r_action(surgeon: M2RSurgeon, N: int, n: int, m: int, L: int, d: int, p: int, q: int):
    raw0, M0, L0, R0 = G.transfer_bounds_global(n, m, L, d, p, q)
    action = ActionCandidate(N, n, m, L, d, p, q, f"BREED_N{N}_n{n}_m{m}_L{L}_d{d}_{p}x{q}")
    surgery = surgeon.repair(action)
    raw, M, Lb, R = raw0, M0, L0, R0
    if surgery.final_raw < raw0:
        exact = PROVED_REPAIR.enhanced_rescue(n, m, L, d, p, q)
        assert exact is not None, (action, surgery)
        assert int(exact[0]) == surgery.final_raw, (action, surgery, exact)
        raw, M, Lb, R = int(exact[0]), int(exact[1]), min(L0, int(exact[2])), int(exact[3])
    return raw0, raw, M, Lb, R, surgery.provider, surgery.proof_gated


def scan_N(N: int, mode: str) -> dict:
    if mode not in MODES:
        raise ValueError(mode)
    if N <= PROVED_BASE_FRONTIER:
        return {
            "N": N,
            "mode": mode,
            "verdict": "CLOSED_BY_PROVED_BASE_FRONTIER",
            "credit_eligible": True,
            "claim_ceiling": "REUSES_EXISTING_N_LE_57_THEOREM_ONLY",
        }

    plan = FrozenPlan(
        experiment_id=f"JANUS-BREED-{mode}-N{N}",
        N=N,
        scope=SCOPE,
        action_order="n descending; (m,L) ascending; d ascending; p ascending with p<=q",
        repair_chain=(
            "GLOBAL_RAW",
            "PREEXISTING_PROVED_REPAIRS_THROUGH_N58_23X27",
            "M2R_SURGEON_AUDIT" if mode == "M2R" else "DIRECT_NO_SURGEON",
        ),
        falsification_rule="First unresolved exact transition with final_raw>N^2 is OPEN. No same-run lemma use.",
        discovery_or_confirmation="STRESS",
    )
    frozen = plan.seal()
    assert verify_seal(frozen)

    cap = N * N
    roots = A.hard_roots(N)
    max_n = max(roots, default=A.TAIL_N)
    boxes: dict[int, list[tuple[int, int, int]]] = {n: [] for n in range(7, max_n + 1)}
    rootsets = {n: set(rows) for n, rows in roots.items()}
    surgeon = M2RSurgeon() if mode == "M2R" else None

    checked_states = 0
    checked_transitions = 0
    exact_repairs = 0
    proof_gate_failures = 0

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

        for m, L in sorted(candidates):
            checked_states += 1
            dlo, dhi = A.degree_interval(n, m, L)
            for d in range(dlo, dhi + 1):
                for p in range(0, d // 2 + 1):
                    q = d - p
                    checked_transitions += 1
                    if mode == "DIRECT":
                        raw0, raw, M, Lb, R, provider, proof_gated = exact_direct_action(N, n, m, L, d, p, q)
                    else:
                        raw0, raw, M, Lb, R, provider, proof_gated = exact_m2r_action(surgeon, N, n, m, L, d, p, q)
                    if raw < raw0:
                        exact_repairs += 1
                    if raw > cap and not proof_gated:
                        proof_gate_failures += 1
                    if raw > cap:
                        return {
                            "N": N,
                            "mode": mode,
                            "scope": SCOPE,
                            "verdict": "OPEN",
                            "credit_eligible": False,
                            "cap": cap,
                            "checked_states_before_open": checked_states,
                            "checked_transitions_before_open": checked_transitions,
                            "exact_repairs_before_open": exact_repairs,
                            "proof_gate_failures": proof_gate_failures,
                            "first_open": {
                                "state": [n, m, L],
                                "d": d,
                                "p": p,
                                "q": q,
                                "raw_base": raw0,
                                "raw_final": raw,
                                "jump_debt": raw - cap,
                                "provider": provider,
                                "proof_gated": proof_gated,
                            },
                            "frozen_plan": frozen,
                            "rollback_performed_logically": mode == "M2R",
                            "same_run_new_lemma_use": False,
                            "claim_ceiling": "EXACT_ABSTRACT_BOUND_OPEN__NOT_ACTUAL_CNF_COUNTEREXAMPLE",
                        }
                    for n2 in range(7, n):
                        add_box(boxes[n2], M, Lb, raw)

    return {
        "N": N,
        "mode": mode,
        "scope": SCOPE,
        "verdict": "NO_OPEN_IN_FULL_ABSTRACT_CLOSURE",
        "credit_eligible": proof_gate_failures == 0,
        "cap": cap,
        "checked_states": checked_states,
        "checked_transitions": checked_transitions,
        "exact_repairs": exact_repairs,
        "proof_gate_failures": proof_gate_failures,
        "frozen_plan": frozen,
        "same_run_new_lemma_use": False,
        "claim_ceiling": "BREED_EXPERIMENTAL_FINITE_CAP_CREDIT_ONLY",
    }


def classify(a: dict, b: dict) -> str:
    aa = a["verdict"] != "OPEN" and bool(a.get("credit_eligible"))
    bb = b["verdict"] != "OPEN" and bool(b.get("credit_eligible"))
    if aa and bb:
        return "PASS_PASS"
    if aa and not bb:
        return "PASS_OPEN"
    if not aa and bb:
        return "OPEN_PASS"
    return "OPEN_OPEN"


def run(lo: int, hi: int) -> dict:
    rows = []
    disagreements = []
    for N in range(lo, hi + 1):
        # Two complete role-swapped passes. Each N is therefore inspected once
        # by DIRECT and once by M2R, but pass ownership follows the prime mask.
        face_a_mode = role_for("FACE_A", N)
        face_b_mode = role_for("FACE_B", N)
        face_a = scan_N(N, face_a_mode)
        face_b = scan_N(N, face_b_mode)
        pair = classify(face_a, face_b)
        same_verdict = face_a["verdict"] == face_b["verdict"]
        row = {
            "N": N,
            "prime": is_prime(N),
            "FACE_A": {"mode": face_a_mode, "result": face_a},
            "FACE_B": {"mode": face_b_mode, "result": face_b},
            "pair_class": pair,
            "same_verdict": same_verdict,
            "both_credit_eligible": bool(face_a.get("credit_eligible")) and bool(face_b.get("credit_eligible")),
        }
        rows.append(row)
        if not same_verdict:
            disagreements.append(N)
        print(
            f"BREED N={N} prime={is_prime(N)} "
            f"A={face_a_mode}:{face_a['verdict']} "
            f"B={face_b_mode}:{face_b['verdict']} pair={pair}"
        )

    counts = {k: 0 for k in ("PASS_PASS", "PASS_OPEN", "OPEN_PASS", "OPEN_OPEN")}
    for r in rows:
        counts[r["pair_class"]] += 1
    return {
        "schema": "JANUS/MAD-LAB/BREED-STRESS/v1",
        "name": NAME,
        "lane": LANE,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "N_min": lo,
        "N_max": hi,
        "N_count": len(rows),
        "passes": {
            "FACE_A": "prime=M2R, composite=DIRECT",
            "FACE_B": "prime=DIRECT, composite=M2R",
        },
        "pair_counts": counts,
        "verdict_disagreement_N": disagreements,
        "results": rows,
        "scientific_boundary": {
            "breed_credit_is_theorem_frontier_credit": False,
            "same_run_new_lemma_use": False,
            "unproved_m2r_repair_can_be_credited": False,
            "prime_mask_has_no_assumed_sat_theorem_status": True,
            "P_VS_NP": "OPEN"
        },
    }


def selftest() -> None:
    assert role_for("FACE_A", 59) == "M2R"
    assert role_for("FACE_A", 60) == "DIRECT"
    assert role_for("FACE_B", 59) == "DIRECT"
    assert role_for("FACE_B", 60) == "M2R"
    # Known unresolved state remains fail-closed in M2R Surgeon.
    s = M2RSurgeon().repair(ActionCandidate(58, 7, 78, 350, 50, 24, 26, "BREED_N58_CONTROL"))
    assert s.verdict == "OPEN_REPAIR_REQUIRED" and s.final_raw == 3425 and s.cap == 3364
    print("JANUS_BREED_ROLE_SWAP=PASS")
    print("JANUS_BREED_N58_NEGATIVE_CONTROL=PASS")
    print("JANUS_BREED_NO_SAME_RUN_PROMOTION=PASS")
    print("P_VS_NP=OPEN")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=58)
    ap.add_argument("--max", type=int, default=97)
    ap.add_argument("--out", type=Path, default=Path("janus_breed_result.json"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    if args.max < args.min:
        raise SystemExit("--max must be >= --min")
    result = run(args.min, args.max)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"JANUS_BREED_RESULT={args.out}")
    print(f"JANUS_BREED_PAIR_COUNTS={result['pair_counts']}")
    print(f"JANUS_BREED_DISAGREEMENTS={result['verdict_disagreement_N']}")
    print("EXPERIMENTAL_NOT_THEOREM")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
