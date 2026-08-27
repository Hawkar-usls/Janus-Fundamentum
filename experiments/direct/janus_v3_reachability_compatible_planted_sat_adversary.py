#!/usr/bin/env python3
"""Reachability-ceiling-compatible planted-SAT adversary for C025 v3.

Offline research probe only.  Synthetic root-free states satisfy the proved
necessary live-variable ceiling n<=floor((N-2)/2).  Every generated width-3
clause is satisfied by the planted all-True assignment, preventing a legitimate
UNSAT refutation from masquerading as a representation/cap obstruction.

Passing the live-variable ceiling is necessary, NOT sufficient, for actual
reachability from a legitimate root.  A local gap found here still requires an
exact frozen forward reachability certificate before it can challenge reachable
state totality. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
import random
from itertools import combinations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct import janus_unified_macro_restore_v3 as v3
from experiments.direct import janus_v3_root_free_local_gap_probe as oldprobe
from experiments.direct import janus_v3_sequential_budget_local_gap_microscope as microscope
from experiments.direct import janus_v3_balanced_pressure_adversary_probe as pressure

P_VS_NP = "OPEN"


def planted_width3_universe(nvars: int) -> tuple[base.Clause, ...]:
    """All width-3 clauses satisfied by assignment x_i=True for every i."""
    out = []
    for vs in combinations(range(1, nvars + 1), 3):
        for mask in range(8):
            # bit 1 -> positive literal. Exclude all-negative mask=0 because
            # the planted all-True assignment would falsify it.
            if mask == 0:
                continue
            clause = tuple(v if ((mask >> i) & 1) else -v for i, v in enumerate(vs))
            cc = base.canon_clause(clause)
            assert cc is not None and len(cc) == 3
            out.append(cc)
    return tuple(sorted(set(out), key=lambda c: (len(c), c)))


def planted_assignment(nvars: int) -> dict[int, int]:
    return {v: 1 for v in range(1, nvars + 1)}


def generate(N: int, seed: int) -> base.CNF:
    nvars = (N - 2) // 2
    m = (N * N - 1) // 4
    U = planted_width3_universe(nvars)
    if m > len(U):
        raise ValueError(f"INSUFFICIENT_PLANTED_WIDTH3_UNIVERSE: N={N}, n={nvars}, m={m}, U={len(U)}")
    rng = random.Random((N << 40) ^ 0xC0255A7 ^ seed)
    cnf = base.canon_cnf(rng.sample(U, m))
    if len(cnf) != m:
        raise AssertionError("UNEXPECTED_CANONICAL_COLLAPSE")
    if not base.verify_total_assignment(cnf, planted_assignment(nvars)):
        raise AssertionError("PLANTED_ASSIGNMENT_FAILED")
    return cnf


def run_rung(N: int, seeds: int) -> dict:
    nvars = (N - 2) // 2
    m = (N * N - 1) // 4
    totals = {
        "seeds": seeds,
        "generated": 0,
        "connected_full": 0,
        "planted_sat_verified": 0,
        "earlier_terminal_lane": 0,
        "ordinary_pivot_exists": 0,
        "all_pivot_overflow": 0,
        "zero_cap_admissible_macro": 0,
        "sequential_certified": 0,
        "v3_plan_exists": 0,
        "true_local_v3_gap": 0,
    }
    first_all_overflow = None
    first_gap = None

    for seed in range(seeds):
        try:
            cnf = generate(N, seed)
        except ValueError as exc:
            return {
                "parameters": {"N": N, "nvars": nvars, "clauses": m, "seeds": seeds},
                "status": "RUNG_NOT_GENERATABLE",
                "reason": str(exc),
                "totals": totals,
                "first_all_pivot_overflow": None,
                "first_true_local_v3_gap": None,
            }
        totals["generated"] += 1
        if not oldprobe.connected_and_full(cnf, nvars):
            continue
        totals["connected_full"] += 1
        assert base.state_units(cnf) <= N * N
        assert len(base.vars_of(cnf)) == nvars <= (N - 2) // 2
        assert base.verify_total_assignment(cnf, planted_assignment(nvars))
        totals["planted_sat_verified"] += 1

        # 2SAT is inapplicable for width-3. GF2 may return only if the entire
        # CNF matches its exact recognized language. Bounded-width resolution
        # cannot honestly refute a formula for which we explicitly verify a
        # satisfying total assignment. Keep the generic old lane check anyway.
        lane = oldprobe.earlier_exact_local_lane(cnf)
        if lane is not None:
            totals["earlier_terminal_lane"] += 1
            # If any exact lane claims UNSAT, the planted witness must expose a bug.
            if lane == "BOUNDED_WIDTH_REFUTATION":
                raise AssertionError("BOUNDED_RESOLUTION_REFUTED_PLANTED_SAT_FORMULA")
            continue

        overflow, pivot_rows = oldprobe.all_pivots_overflow(cnf, N * N)
        if not overflow:
            totals["ordinary_pivot_exists"] += 1
            continue
        totals["all_pivot_overflow"] += 1

        macro_fit = pressure.macro_fit_scan(cnf, N)
        if macro_fit["count"] == 0:
            totals["zero_cap_admissible_macro"] += 1
        seq = microscope.sequential_certificate_scan(cnf, N)
        if seq["exists"]:
            totals["sequential_certified"] += 1

        state = oldprobe.make_state(cnf, N)
        plan = v3.discover_extension_tail_plan_v3(state)
        if plan is not None:
            totals["v3_plan_exists"] += 1

        pair_counts = pressure.signaware_pair_counts(cnf)
        row = {
            "N": N,
            "seed": seed,
            "nvars": nvars,
            "reachable_live_ceiling": (N - 2) // 2,
            "clauses": m,
            "state_units": base.state_units(cnf),
            "state_cap": N * N,
            "headroom": N * N - base.state_units(cnf),
            "fingerprint": base.fingerprint(cnf),
            "cnf": cnf,
            "planted_assignment": planted_assignment(nvars),
            "planted_sat_verified": True,
            "max_signaware_pair_frequency": max(pair_counts.values(), default=0),
            "macro_fit": macro_fit,
            "sequential_certificate": seq,
            "pivot_scan": pivot_rows,
            "v3_plan": None if plan is None else {
                "pair": plan.macro_cert.get("represents"),
                "pivots": list(plan.pivots),
                "macro_units": base.state_units(plan.macro_cnf),
                "after_units": base.state_units(plan.after),
            },
        }
        if first_all_overflow is None:
            first_all_overflow = row
        if plan is None:
            totals["true_local_v3_gap"] += 1
            first_gap = {
                **row,
                "claim_ceiling": "LIVE_COUNT_COMPATIBLE_PLANTED_SAT_LOCAL_GAP__EXACT_FORWARD_REACHABILITY_NOT_ESTABLISHED",
            }
            break

    return {
        "parameters": {"N": N, "nvars": nvars, "clauses": m, "seeds": seeds},
        "totals": totals,
        "first_all_pivot_overflow": first_all_overflow,
        "first_true_local_v3_gap": first_gap,
        "status": "TRUE_LOCAL_V3_GAP_FOUND" if first_gap is not None else "NO_TRUE_LOCAL_V3_GAP_IN_SEEDED_RUNG",
    }


def main() -> int:
    rungs = (
        (10, 128),
        (12, 128),
        (14, 128),
        (16, 128),
        (18, 64),
        (20, 64),
    )
    rows = []
    for N, seeds in rungs:
        row = run_rung(N, seeds)
        rows.append(row)
        if row["first_true_local_v3_gap"] is not None:
            break

    first_gap = next((r["first_true_local_v3_gap"] for r in rows if r["first_true_local_v3_gap"] is not None), None)
    report = {
        "schema": "JANUS/C025/V3-REACHABILITY-COMPATIBLE-PLANTED-SAT-ADVERSARY/v1",
        "rungs": rows,
        "first_true_local_v3_gap": first_gap,
        "scientific_boundary": {
            "offline_generated_adversary_only": True,
            "live_variable_ceiling_respected": True,
            "planted_sat_witness_verified": True,
            "passing_live_ceiling_does_not_establish_forward_reachability": True,
            "exact_forward_reachability_certificate_required": True,
            "found_local_gap_does_not_refute_reachable_totality": True,
            "no_gap_does_not_prove_availability": True,
            "generative_layer_has_theorem_authority": False,
            "V3_ROOT_FREE_TAIL_AVAILABILITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    report["status"] = "TRUE_LOCAL_V3_GAP_FOUND" if first_gap is not None else "NO_TRUE_LOCAL_V3_GAP_IN_FROZEN_PLANTED_LADDER"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
