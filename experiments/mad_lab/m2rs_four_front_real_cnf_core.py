#!/usr/bin/env python3
"""JANUS MAD-LAB: four-front exact replay on a realizable static 50-regular CNF core.

This experiment closes one narrow question only:

    Does there exist a *static* distinct, unit-free, non-tautological signed CNF
    with (n,m,L)=(7,79,350), every variable degree 50, and every polarity split
    in the residual OPEN ridge?

Yes: this file constructs an exact witness with p_i=q_i=25 for every variable.
The construction is deterministic and self-verifying.

CRITICAL CLAIM CEILING
----------------------
The repository's full pipeline normalization semantics and reachability relation
are NOT proved equivalent to the static clause-universe model used here.  Thus:

    STATIC REALIZABILITY != JANUS PIPELINE REACHABILITY.

The four fronts below are independent exact replay orders over the same formula.
They are consistency checks only; traversal order never changes truth.
No same-run lemma receives theorem credit.  P vs NP remains OPEN.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

from experiments.mad_lab import m2rs_tranception_meet as M

SCHEMA = "JANUS/MAD-LAB/M2RS-FOUR-FRONT-REAL-CNF-CORE/v1"
LANE = "JANUS_MAD_LAB_M2RS_FOUR_FRONT_REAL_CNF_CORE"
STATUS = "STATIC_WITNESS_EXACT__PIPELINE_REACHABILITY_UNPROVED"
STATIC_MODEL = "DISTINCT_UNIT_FREE_NONTAUTOLOGICAL_SIGNED_CNF"
CLAIM_CEILING = "STATIC_CANONICAL_CORE_REALIZABLE__REACHABILITY_UNPROVED"
P_VS_NP = "OPEN"
THEOREM_CREDIT_ALLOWED = False
N = 58
NVAR = 7
MCLAUSE = 79
LITERAL_MASS = 350
TARGET_DEGREE = 50
TARGET_POS = 25
TARGET_NEG = 25

TernaryClause = tuple[int, ...]
DimacsClause = tuple[int, ...]


def stable_digest(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def cyclic_shifts(t: TernaryClause) -> list[TernaryClause]:
    n = len(t)
    return [tuple(t[(i - j) % n] for i in range(n)) for j in range(n)]


def cyclic_canonical(t: TernaryClause) -> TernaryClause:
    return min(cyclic_shifts(t))


def orbit(t: TernaryClause) -> set[TernaryClause]:
    return set(cyclic_shifts(t))


def orbit_representatives(width: int, positives: int) -> list[TernaryClause]:
    """Enumerate deterministic Z7 orbit representatives of signed clauses."""
    reps: set[TernaryClause] = set()
    for t in itertools.product((-1, 0, 1), repeat=NVAR):
        if sum(x != 0 for x in t) != width:
            continue
        if sum(x == 1 for x in t) != positives:
            continue
        reps.add(cyclic_canonical(tuple(t)))
    return sorted(reps)


def construct_witness() -> tuple[list[TernaryClause], dict[str, Any]]:
    """Construct 77 clauses from cyclic orbits plus two support complements.

    Orbit accounting per variable:
      5 x (width=5, positives=2) -> degree 25, positive 10
      4 x (width=4, positives=2) -> degree 16, positive  8
      2 x (width=4, positives=3) -> degree  8, positive  6
                                                   -----
                                         subtotal degree 49, positive 24

    Two all-positive complementary-support clauses of widths 3 and 4 add one
    occurrence and one positive literal to every variable, yielding 50=25+25.
    """
    chosen = (
        orbit_representatives(5, 2)[:5]
        + orbit_representatives(4, 2)[:4]
        + orbit_representatives(4, 3)[:2]
    )
    assert len(chosen) == 11

    clauses: set[TernaryClause] = set()
    orbit_receipts: list[dict[str, Any]] = []
    for rep in chosen:
        rows = orbit(rep)
        assert len(rows) == 7, (rep, len(rows))
        before = len(clauses)
        clauses.update(rows)
        assert len(clauses) == before + 7, "chosen signed orbits must be disjoint"
        orbit_receipts.append({
            "representative": list(rep),
            "width": sum(x != 0 for x in rep),
            "positives_per_variable_from_orbit": sum(x == 1 for x in rep),
            "orbit_size": 7,
        })

    assert len(clauses) == 77
    extras = [
        (1, 1, 1, 0, 0, 0, 0),
        (0, 0, 0, 1, 1, 1, 1),
    ]
    for c in extras:
        assert c not in clauses
        clauses.add(c)

    witness = sorted(clauses)
    assert len(witness) == MCLAUSE
    construction = {
        "method": "ELEVEN_SIGNED_Z7_ORBITS_PLUS_TWO_COMPLEMENTARY_SUPPORT_CLAUSES",
        "orbit_plan": [
            {"count": 5, "width": 5, "positives_per_orbit_seed": 2},
            {"count": 4, "width": 4, "positives_per_orbit_seed": 2},
            {"count": 2, "width": 4, "positives_per_orbit_seed": 3},
        ],
        "orbit_receipts": orbit_receipts,
        "closing_clauses": [list(c) for c in extras],
        "search_role": "DETERMINISTIC_CONSTRUCTION_NOT_PROOF_BY_HEURISTIC_SEARCH",
    }
    return witness, construction


def to_dimacs_clause(c: TernaryClause) -> DimacsClause:
    out = tuple((i + 1) if s > 0 else -(i + 1) for i, s in enumerate(c) if s)
    return out


def from_dimacs_clause(c: Iterable[int]) -> TernaryClause:
    t = [0] * NVAR
    for lit in c:
        v = abs(int(lit))
        assert 1 <= v <= NVAR
        s = 1 if lit > 0 else -1
        assert t[v - 1] == 0, "duplicate variable or tautology inside clause"
        t[v - 1] = s
    return tuple(t)


def formula_digest(clauses: Iterable[TernaryClause]) -> str:
    return stable_digest([list(c) for c in sorted(clauses)])


def exact_stats(clauses: list[TernaryClause]) -> dict[str, Any]:
    assert len(clauses) == MCLAUSE
    assert len(set(clauses)) == MCLAUSE
    degree = [0] * NVAR
    positive = [0] * NVAR
    negative = [0] * NVAR
    widths: list[int] = []

    for c in clauses:
        assert len(c) == NVAR
        assert all(x in (-1, 0, 1) for x in c)
        w = sum(x != 0 for x in c)
        assert w >= 2, "unit/empty clauses are excluded by the static model"
        widths.append(w)
        for i, s in enumerate(c):
            if s == 0:
                continue
            degree[i] += 1
            if s > 0:
                positive[i] += 1
            else:
                negative[i] += 1

    return {
        "n": NVAR,
        "m": len(clauses),
        "L": sum(widths),
        "width_min": min(widths),
        "width_max": max(widths),
        "width_histogram": {str(k): widths.count(k) for k in sorted(set(widths))},
        "degree": degree,
        "positive": positive,
        "negative": negative,
        "minority": [min(p, q) for p, q in zip(positive, negative)],
        "distinct_clauses": len(set(clauses)),
        "non_tautological_by_ternary_encoding": True,
        "formula_sha256": formula_digest(clauses),
    }


def validate_target_stats(stats: dict[str, Any]) -> None:
    assert stats["n"] == NVAR
    assert stats["m"] == MCLAUSE
    assert stats["L"] == LITERAL_MASS
    assert stats["distinct_clauses"] == MCLAUSE
    assert stats["width_min"] >= 2
    assert stats["degree"] == [TARGET_DEGREE] * NVAR
    assert stats["positive"] == [TARGET_POS] * NVAR
    assert stats["negative"] == [TARGET_NEG] * NVAR
    assert stats["minority"] == [TARGET_POS] * NVAR


def dimacs_text(clauses: list[TernaryClause]) -> str:
    lines = [
        "c JANUS MAD-LAB static 50-regular balanced witness",
        "c STATIC REALIZABILITY ONLY; PIPELINE REACHABILITY UNPROVED",
        f"p cnf {NVAR} {len(clauses)}",
    ]
    for c in clauses:
        d = to_dimacs_clause(c)
        lines.append(" ".join(map(str, d)) + " 0")
    return "\n".join(lines) + "\n"


def parse_dimacs(text: str) -> list[TernaryClause]:
    out: list[TernaryClause] = []
    seen_header = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            parts = line.split()
            assert parts == ["p", "cnf", str(NVAR), str(MCLAUSE)]
            seen_header = True
            continue
        vals = [int(x) for x in line.split()]
        assert vals and vals[-1] == 0
        assert 0 not in vals[:-1]
        out.append(from_dimacs_clause(vals[:-1]))
    assert seen_header
    assert len(out) == MCLAUSE
    return out


def center_left_order(n: int) -> list[int]:
    mid = (n - 1) // 2
    out = [mid]
    step = 1
    while len(out) < n:
        a = mid - step
        b = mid + step
        if a >= 0:
            out.append(a)
        if b < n:
            out.append(b)
        step += 1
    return out


def center_right_order(n: int) -> list[int]:
    mid = (n - 1) // 2
    out = [mid]
    step = 1
    while len(out) < n:
        b = mid + step
        a = mid - step
        if b < n:
            out.append(b)
        if a >= 0:
            out.append(a)
        step += 1
    return out


def replay_order(name: str, clauses: list[TernaryClause], order: list[int]) -> dict[str, Any]:
    assert sorted(order) == list(range(len(clauses)))
    visited: list[TernaryClause] = []
    chain = hashlib.sha256()
    checkpoints: list[dict[str, Any]] = []
    for step, idx in enumerate(order, 1):
        c = clauses[idx]
        visited.append(c)
        chain.update(json.dumps([idx, list(c)], separators=(",", ":")).encode("utf-8"))
        if step in (1, len(clauses) // 2, len(clauses)):
            s = exact_stats(visited) if step == len(clauses) else {
                "m": len(visited),
                "L": sum(sum(x != 0 for x in z) for z in visited),
            }
            checkpoints.append({"step": step, "snapshot": s})

    stats = exact_stats(visited)
    validate_target_stats(stats)
    return {
        "front": name,
        "order_sha256": stable_digest(order),
        "traversal_chain_sha256": chain.hexdigest(),
        "final_formula_sha256": stats["formula_sha256"],
        "final_stats": stats,
        "checkpoints": checkpoints,
    }


def four_front_replay(clauses: list[TernaryClause]) -> dict[str, Any]:
    n = len(clauses)
    orders = {
        "EDGE_LEFT": list(range(n)),
        "CENTER_LEFT": center_left_order(n),
        "CENTER_RIGHT": center_right_order(n),
        "EDGE_RIGHT": list(reversed(range(n))),
    }
    receipts = [replay_order(name, clauses, order) for name, order in orders.items()]
    formula_digests = {r["final_formula_sha256"] for r in receipts}
    traversal_digests = {r["traversal_chain_sha256"] for r in receipts}
    stats_digests = {stable_digest(r["final_stats"]) for r in receipts}
    return {
        "mode": "FOUR_ORDER_EXACT_REPLAY",
        "fronts": receipts,
        "all_formula_digests_equal": len(formula_digests) == 1,
        "all_final_stats_equal": len(stats_digests) == 1,
        "all_traversal_chains_distinct": len(traversal_digests) == 4,
        "consensus": len(formula_digests) == 1 and len(stats_digests) == 1 and len(traversal_digests) == 4,
        "truth_effect": "NONE__CONSISTENCY_CHECK_ONLY",
    }


def actual_pivot_bounds(stats: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(NVAR):
        d = int(stats["degree"][i])
        p = int(stats["positive"][i])
        q = int(stats["negative"][i])
        cp, cq = sorted((p, q))
        b = dict(M.exact_action_bound(N, NVAR, MCLAUSE, LITERAL_MASS, d, cp, cq))
        row = {
            "variable": i + 1,
            "actual_signature": [d, p, q],
            "canonical_signature": [d, cp, cq],
            "B": int(b["raw_final"]),
            "cap": N * N,
            "provider": b["provider"],
            "cap_safe": bool(b["cap_safe"]),
            "verdict": "LAND" if b["cap_safe"] else "OPEN",
        }
        rows.append(row)
    return rows


def build_payload() -> tuple[dict[str, Any], str]:
    clauses, construction = construct_witness()
    stats = exact_stats(clauses)
    validate_target_stats(stats)

    text = dimacs_text(clauses)
    reparsed = parse_dimacs(text)
    parsed_stats = exact_stats(reparsed)
    validate_target_stats(parsed_stats)
    assert parsed_stats["formula_sha256"] == stats["formula_sha256"]

    pivots = actual_pivot_bounds(stats)
    assert len(pivots) == NVAR
    assert all(r["actual_signature"] == [50, 25, 25] for r in pivots)
    assert all(r["B"] == 3433 for r in pivots), pivots
    assert all(r["verdict"] == "OPEN" for r in pivots), pivots

    replay = four_front_replay(clauses)
    assert replay["consensus"]

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "lane": LANE,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "N": N,
        "cap": N * N,
        "state": [NVAR, MCLAUSE, LITERAL_MASS],
        "static_model": STATIC_MODEL,
        "static_model_contract": {
            "distinct_clauses": True,
            "unit_free": True,
            "non_tautological": True,
            "signed_literals": True,
            "repo_normalization_compatibility_proved": False,
            "pipeline_reachability_proved": False,
        },
        "static_realizable": True,
        "construction": construction,
        "witness_stats": stats,
        "dimacs_roundtrip": {
            "exact_reparse": True,
            "formula_sha256": parsed_stats["formula_sha256"],
        },
        "actual_pivot_bounds": pivots,
        "all_seven_actual_pivots_on_peak_open_signature": True,
        "four_front_replay": replay,
        "anti_self_deception_gate": {
            "static_witness_exact": True,
            "repo_normalization_compatibility_proved": False,
            "pipeline_reachability_proved": False,
            "same_run_lemma_promotion": False,
            "theorem_credit_allowed": THEOREM_CREDIT_ALLOWED,
            "claim_ceiling": CLAIM_CEILING,
        },
        "interpretation": {
            "counts_only_nonexistence_route": "REFUTED_IN_THIS_STATIC_MODEL_BY_EXPLICIT_WITNESS",
            "next_required_gate": "PROVE_OR_REFUTE_JANUS_PIPELINE_REACHABILITY_OF_THE_EXACT_WITNESS_CLASS",
            "truth_effect_of_four_front_order": "NONE",
        },
    }
    payload["audit_sha256"] = stable_digest(payload)
    return payload, text


def selftest() -> None:
    payload, text = build_payload()
    assert payload["static_realizable"]
    assert payload["witness_stats"]["degree"] == [50] * 7
    assert payload["witness_stats"]["positive"] == [25] * 7
    assert payload["witness_stats"]["negative"] == [25] * 7
    assert payload["four_front_replay"]["consensus"]
    assert not payload["anti_self_deception_gate"]["pipeline_reachability_proved"]
    assert not payload["anti_self_deception_gate"]["theorem_credit_allowed"]
    assert payload["P_VS_NP"] == "OPEN"
    assert parse_dimacs(text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path, default=Path("artifacts/mad_lab/m2rs_four_front_real_cnf_core.json"))
    ap.add_argument("--cnf-out", type=Path, default=Path("artifacts/mad_lab/m2rs_four_front_real_cnf_core.cnf"))
    args = ap.parse_args()

    selftest()
    payload, text = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.cnf_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.cnf_out.write_text(text, encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
