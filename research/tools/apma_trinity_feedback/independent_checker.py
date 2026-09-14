from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import research.tools.apma_trinity_feedback.feedback as cand
import research.tools.apma_trinity_unicyclic.unicyclic as uni
import research.tools.apma_trinity_sovereign.trinity as base


def truth_sat(source, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if all(any(a[abs(l)] == (l > 0) for l in c) for c in source):
            return True
    return False


def k23_source(unsat=False):
    # Typed module interaction graph K_{2,3}: V=5, E=6, cycle rank=2.
    src = [
        (-1, -2, -3),
        (-4, -5, -6),
        (1, 4, -7),
        (2, 5, -8),
        (3, 6, -9),
    ]
    if unsat:
        # Contradictory 2CNF leaf attached through variable 7; preserves the
        # multicycle core but forces UNSAT without changing candidate logic.
        src.extend([(7,), (-7,)])
    return tuple(src), 9


def wide_k2k(k):
    # Two connected Horn modules H1,H2 and k disconnected dual-Horn modules.
    # Interaction graph is K_{2,k}; canonical feedback interface grows with k.
    clauses = []
    nextv = 2 * k + 3
    c1, c2 = 2 * k + 1, 2 * k + 2
    # Keep each Horn side internally connected by a private connector.
    for i in range(k):
        p = nextv; nextv += 1
        clauses.append((-c1, -(i + 1), -p))
    for i in range(k):
        p = nextv; nextv += 1
        clauses.append((-c2, -(k + i + 1), -p))
    for i in range(k):
        p = nextv; nextv += 1
        clauses.append((i + 1, k + i + 1, -p))
    return tuple(clauses), nextv - 1


def hyperedge_source():
    # variable 1 occurs in three distinct typed modules.
    return ((-1, -2, -3), (1, 4, -5), (1, 6)), 6


def unicyclic_source():
    return ((-1, -3, -4), (-1, 2, 5), (-2, -3)), 5


def forest_source():
    return ((-1, -2, -3), (1, 4, -5)), 5


def direct_cert(source, n):
    s = base._typed_state(base.canonical_source(source))
    assert s is not None
    return cand.feedback_certificate(s, base.canonical_source(source), n)


def main():
    checks = {}

    sat_src, sat_n = k23_source(False)
    unsat_src, unsat_n = k23_source(True)
    sat_truth = truth_sat(sat_src, sat_n)
    unsat_truth = truth_sat(unsat_src, unsat_n)
    zsat = cand.run_trinity(sat_src, sat_n)
    zunsat = cand.run_trinity(unsat_src, unsat_n)

    checks["k23_truth_sat"] = sat_truth is True
    checks["k23_truth_unsat"] = unsat_truth is False
    checks["k23_feedback_door_sat"] = zsat["proposal"].get("door") == cand.FEEDBACK
    checks["k23_feedback_door_unsat"] = zunsat["proposal"].get("door") == cand.FEEDBACK
    checks["k23_sat_exact"] = zsat["sovereign"]["decision"] == "COMMIT_SAT"
    checks["k23_unsat_exact"] = zunsat["sovereign"]["decision"] == "COMMIT_UNSAT"
    checks["k23_cycle_rank_two"] = zsat["proposal"]["evidence"]["cycle_rank"] == 2

    B = zunsat["proposal"]["evidence"]["feedback_interface"]
    checks["unsat_all_sigma_exhausted"] = (
        zunsat["demiurge"]["tested_sigma_count"] == 2 ** len(B)
        and len(zunsat["demiurge"]["rejected_sigma"]) == 2 ** len(B)
    )

    # Polynomial envelope checks on the admitted controls.
    envelope_ok = True
    envelope_rows = []
    for z in (zsat, zunsat):
        ev = z["proposal"]["evidence"]
        ex = z["demiurge"]
        L = 1 + z["n"] + len(z["proposal"].get("_never", []))
        # Recompute exact encoding L from source rather than trusting candidate evidence.
        src = sat_src if z is zsat else unsat_src
        L = 1 + z["n"] + len(src) + sum(len(c) for c in src)
        M = ev["module_count"]
        outer = 2 ** ev["feedback_interface_width"]
        envelope_ok &= outer <= L
        envelope_ok &= ex["row_count"] <= M * L * L
        envelope_ok &= ex["native_solve_calls"] <= M * L * L
        envelope_rows.append({
            "L": L,
            "M": M,
            "B": ev["feedback_interface_width"],
            "outer": outer,
            "rows": ex["row_count"],
            "native_solve_calls": ex["native_solve_calls"],
        })
    checks["symbolic_envelope_controls"] = bool(envelope_ok)

    # Overflow must fail closed under the canonical tree, even if another tree
    # might have a different B. We make no existential optimal-tree claim.
    wide_src, wide_n = wide_k2k(12)
    wide_cert, wide_diag = direct_cert(wide_src, wide_n)
    checks["feedback_width_overflow_open"] = (
        wide_cert is None
        and wide_diag.get("feedback_status") == "OPEN_FEEDBACK_INTERFACE_WIDTH"
    )

    hyp_src, hyp_n = hyperedge_source()
    hyp_cert, hyp_diag = direct_cert(hyp_src, hyp_n)
    checks["hyperedge_open"] = (
        hyp_cert is None
        and hyp_diag.get("feedback_status") == "OPEN_INTERFACE_HYPEREDGE"
    )

    # Regression routing: predecessor doors remain authoritative first.
    u_src, u_n = unicyclic_source()
    zu = cand.run_trinity(u_src, u_n)
    checks["unicyclic_predecessor_preserved"] = (
        zu["proposal"].get("door") == uni.UNICYCLIC
    )
    f_src, f_n = forest_source()
    zf = cand.run_trinity(f_src, f_n)
    checks["old_door_precedence_preserved"] = zf["proposal"].get("door") != cand.FEEDBACK

    # Tamper rejection must compare against independently recomputed proposal.
    bad = dict(zsat["proposal"])
    bad["evidence"] = dict(bad["evidence"])
    bad["evidence"]["feedback_interface"] = []
    tampered = cand.run_trinity(sat_src, sat_n, forced_proposal=bad)
    checks["tampered_proposal_rejected"] = (
        tampered["sovereign"]["decision"] == "ROLLBACK_CAPTAIN_REJECT"
    )

    # Candidate source guard: no whole-formula brute-force truth enumerator,
    # stochastic branch, scoring, ML, or heuristic pruning is permitted.
    src_text = Path(cand.__file__).read_text(encoding="utf-8")
    forbidden = [
        "truth_sat(", "random.", "numpy", "sklearn", "torch", "score(",
        "heuristic", "sample(", "bruteforce", "brute_force",
    ]
    hits = [x for x in forbidden if x in src_text.lower()]
    checks["candidate_source_guard"] = not hits

    checks["firewall_p_vs_np_open"] = (
        zsat["scientific_status"]["P_VS_NP"] == "OPEN"
        and zsat["scientific_status"]["SAT_IN_P"] == "NOT_PROVED"
        and zsat["scientific_status"]["WIDE_INTERFACE_COMPRESSION"] == "NOT_CLAIMED"
    )

    out = {
        "artifact": "JANUS-TRUMP-APMA-FEEDBACK-INTERFACE-TRANSFER-GATE-2026-09-15-v1.0",
        "authority": "SCOPED_GATE_CHECKER__FINITE_CONTROLS_NOT_THEOREM_EVIDENCE",
        "checks": checks,
        "positive_controls": {
            "sat": {
                "decision": zsat["sovereign"]["decision"],
                "evidence": zsat["proposal"]["evidence"],
                "tested_sigma_count": zsat["demiurge"]["tested_sigma_count"],
            },
            "unsat": {
                "decision": zunsat["sovereign"]["decision"],
                "evidence": zunsat["proposal"]["evidence"],
                "tested_sigma_count": zunsat["demiurge"]["tested_sigma_count"],
                "rejected_sigma": zunsat["demiurge"].get("rejected_sigma"),
            },
        },
        "negative_controls": {
            "wide": wide_diag,
            "hyperedge": hyp_diag,
        },
        "complexity_controls": envelope_rows,
        "source_guard_hits": hits,
        "scientific_firewall": {
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "WIDE_INTERFACE_COMPRESSION": "NOT_CLAIMED",
            "UNIVERSAL_DISCOVERY": "NOT_CLAIMED",
        },
    }
    out["verdict"] = (
        "PASS_SCOPED_CANONICAL_LOG_FEEDBACK_INTERFACE_TRANSFER_GATE"
        if all(checks.values())
        else "FAIL_SCOPED_CANONICAL_LOG_FEEDBACK_INTERFACE_TRANSFER_GATE"
    )
    print(json.dumps(out, sort_keys=True))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
