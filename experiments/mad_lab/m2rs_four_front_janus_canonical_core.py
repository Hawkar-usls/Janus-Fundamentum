#!/usr/bin/env python3
"""JANUS MAD-LAB: exact canonical 50-regular balanced CNF core + four-front replay.

This successor corrects an intentionally exposed weakness in the first static
clause-universe witness: JANUS canon_cnf performs exact subsumption, so a witness
must survive *that* canonicalizer unchanged before receiving canonical-CNF
status.

Here we freeze an explicit 79-clause antichain witness discovered offline and
verify it using the pre-existing C025 canonical CNF engine.  Discovery method is
not theorem authority; the frozen witness is checked exactly from scratch.

Facts proved by this finite executable audit only:
- canon_cnf leaves all 79 clauses intact;
- (n,m,L)=(7,79,350);
- every variable has degree 50 and polarity split 25:25;
- exhaustive 2^7 truth-table says the formula is UNSAT;
- all seven *concrete* C025 ordinary eliminations fit under cap 58^2;
- four distinct elimination orders (two edges, two centers) all stay in cap and
  end at the empty clause.

This does NOT prove the witness is forward-reachable from a legitimate JANUS
root, does NOT prove all balanced cores behave this way, and does NOT settle
P vs NP. P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_v3_root_free_local_gap_probe as oldprobe
from experiments.mad_lab import m2rs_tranception_meet as M

SCHEMA = "JANUS/MAD-LAB/M2RS-FOUR-FRONT-JANUS-CANONICAL-CORE/v1"
STATUS = "EXACT_JANUS_CANONICAL_CORE__FORWARD_REACHABILITY_UNPROVED"
P_VS_NP = "OPEN"
N = 58
CAP = N * N
NVAR = 7
MCLAUSE = 79
LITERAL_MASS = 350
TARGET_DEGREE = 50
TARGET_POLARITY = 25
THEOREM_CREDIT_ALLOWED = False

# Frozen exact witness.  Width histogram: 45 x width-4, 34 x width-5.
# All clauses are already in literal-normal form; base.canon_cnf is still the
# authority and is replayed below.
FROZEN_DIMACS_CLAUSES: tuple[base.Clause, ...] = (
    (1,2,-3,7),(1,2,3,-7),(1,2,3,7),(-1,-2,-6,7),(-1,2,-6,-7),
    (-1,2,-6,7),(-1,2,6,-7),(-1,2,6,7),(1,-2,-6,-7),(1,-2,-6,7),
    (1,-2,6,-7),(1,-2,6,7),(1,2,-6,-7),(1,2,-6,7),(1,2,6,-7),
    (1,2,6,7),(-3,-5,-6,-7),(-3,-5,-6,7),(-3,-5,6,-7),(-3,-5,6,7),
    (-3,5,-6,-7),(-3,5,-6,7),(-3,5,6,-7),(-3,5,6,7),(3,-5,-6,-7),
    (3,-5,-6,7),(3,-5,6,-7),(3,-5,6,7),(3,5,-6,-7),(-4,-5,-6,-7),
    (-4,-5,-6,7),(-4,-5,6,-7),(-4,-5,6,7),(-4,5,-6,-7),(-4,5,-6,7),
    (-4,5,6,-7),(-4,5,6,7),(4,-5,-6,-7),(4,-5,-6,7),(4,-5,6,-7),
    (4,-5,6,7),(4,5,-6,-7),(4,5,-6,7),(4,5,6,-7),(4,5,6,7),
    (-1,-2,-3,4,-5),(-1,-2,-3,4,5),(-1,-2,3,-4,-5),(-1,-2,3,-4,5),
    (-1,-2,3,4,-5),(-1,-2,3,4,5),(-1,2,-3,-4,-5),(-1,2,-3,4,-5),
    (-1,2,3,-4,5),(-1,2,3,4,-5),(-1,2,3,4,5),(1,-2,-3,-4,-5),
    (1,-2,-3,-4,5),(1,-2,-3,4,5),(1,-2,3,-4,5),(1,-2,3,4,-5),
    (1,-2,3,4,5),(1,2,-3,4,-5),(1,2,-3,4,5),(1,2,3,-4,5),
    (1,2,3,4,5),(-1,-2,-3,-4,6),(-1,2,-3,-4,-6),(-1,2,-3,-4,6),
    (-1,2,-3,4,6),(-1,2,3,-4,-6),(-1,2,3,-4,6),(1,-2,3,-4,6),
    (1,-2,3,4,-6),(-1,-2,-3,-4,7),(-1,-2,3,-4,7),(-1,-2,3,4,-7),
    (1,-2,-3,-4,-7),(1,-2,-3,4,-7),
)


def digest(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonical_witness() -> base.CNF:
    raw = tuple(base.canon_clause(c) for c in FROZEN_DIMACS_CLAUSES)
    assert all(c is not None for c in raw)
    canonical = base.canon_cnf(FROZEN_DIMACS_CLAUSES)
    assert len(FROZEN_DIMACS_CLAUSES) == MCLAUSE
    assert len(set(FROZEN_DIMACS_CLAUSES)) == MCLAUSE
    assert len(canonical) == MCLAUSE, "JANUS canonicalizer must preserve all 79 clauses"
    # Every input clause must occur in canonical output modulo canonical literal order.
    assert set(canonical) == set(raw)
    return canonical


def exact_stats(cnf: base.CNF) -> dict[str, Any]:
    variables = base.vars_of(cnf)
    assert variables == tuple(range(1, NVAR + 1))
    degree = []
    positive = []
    negative = []
    for v in variables:
        p = sum(v in c for c in cnf)
        q = sum(-v in c for c in cnf)
        positive.append(p)
        negative.append(q)
        degree.append(p + q)
    widths = [len(c) for c in cnf]
    return {
        "n": len(variables),
        "m": len(cnf),
        "L": sum(widths),
        "state_units_C025": base.state_units(cnf),
        "width_histogram": {str(w): widths.count(w) for w in sorted(set(widths))},
        "degree": degree,
        "positive": positive,
        "negative": negative,
        "minority": [min(p, q) for p, q in zip(positive, negative)],
        "fingerprint_C025": base.fingerprint(cnf),
    }


def verify_target_stats(stats: dict[str, Any]) -> None:
    assert stats["n"] == NVAR
    assert stats["m"] == MCLAUSE
    assert stats["L"] == LITERAL_MASS
    assert stats["width_histogram"] == {"4": 45, "5": 34}
    assert stats["degree"] == [TARGET_DEGREE] * NVAR
    assert stats["positive"] == [TARGET_POLARITY] * NVAR
    assert stats["negative"] == [TARGET_POLARITY] * NVAR
    assert stats["minority"] == [TARGET_POLARITY] * NVAR


def assignment_satisfies(cnf: base.CNF, bits: tuple[int, ...]) -> bool:
    a = {i + 1: bits[i] for i in range(NVAR)}
    return base.verify_total_assignment(cnf, a)


def exact_truth_table(cnf: base.CNF) -> dict[str, Any]:
    models: list[str] = []
    for bits in itertools.product((0, 1), repeat=NVAR):
        if assignment_satisfies(cnf, bits):
            models.append("".join("+" if b else "-" for b in bits))
    return {
        "assignments_checked": 1 << NVAR,
        "satisfying_count": len(models),
        "satisfying_models": models,
        "UNSAT_exact_for_this_formula": len(models) == 0,
        "truth_table_sha256": digest(models),
    }


def abstract_pivot_rows(cnf: base.CNF) -> list[dict[str, Any]]:
    rows = []
    for v in base.vars_of(cnf):
        p = sum(v in c for c in cnf)
        q = sum(-v in c for c in cnf)
        d = p + q
        cp, cq = sorted((p, q))
        b = M.exact_action_bound(N, NVAR, MCLAUSE, LITERAL_MASS, d, cp, cq)
        rows.append({
            "pivot": v,
            "actual_signature": [d, p, q],
            "abstract_canonical_signature": [d, cp, cq],
            "abstract_B": int(b["raw_final"]),
            "abstract_cap": CAP,
            "abstract_provider": b["provider"],
            "abstract_verdict": "LAND" if b["cap_safe"] else "OPEN",
        })
    return rows


def exact_single_pivot_rows(cnf: base.CNF) -> list[dict[str, Any]]:
    rows = []
    for v in base.vars_of(cnf):
        out, st = base.eliminate_var_capped(cnf, v, CAP)
        rows.append({
            "pivot": v,
            "fit": out is not None,
            "raw_units_C025": int(st["raw_units"]),
            "canonical_units_C025": None if out is None else base.state_units(out),
            "positive": int(st.get("positive", 0)),
            "negative": int(st.get("negative", 0)),
            "pairs": int(st.get("pairs", 0)),
            "tautologies": int(st.get("tautologies", 0)),
            "retained": int(st.get("retained", 0)),
            "cap": CAP,
            "verdict": "EXACT_LAND" if out is not None else "EXACT_OVERFLOW",
        })
    return rows


def four_orders() -> dict[str, list[int]]:
    return {
        "EDGE_LEFT": [1, 2, 3, 4, 5, 6, 7],
        "CENTER_LEFT": [4, 3, 5, 2, 6, 1, 7],
        "CENTER_RIGHT": [4, 5, 3, 6, 2, 7, 1],
        "EDGE_RIGHT": [7, 6, 5, 4, 3, 2, 1],
    }


def replay_elimination_front(name: str, root: base.CNF, order: list[int]) -> dict[str, Any]:
    state = root
    receipts: list[dict[str, Any]] = []
    max_raw = base.state_units(state)
    for step, v in enumerate(order, 1):
        live = set(base.vars_of(state))
        if v not in live:
            receipts.append({
                "step": step,
                "pivot": v,
                "status": "ALREADY_ABSENT",
                "canonical_units": base.state_units(state),
            })
            continue
        out, st = base.eliminate_var_capped(state, v, CAP)
        if out is None:
            receipts.append({
                "step": step,
                "pivot": v,
                "status": "OVERFLOW",
                "raw_units": int(st["raw_units"]),
                "cap": CAP,
            })
            return {
                "front": name,
                "order": order,
                "verdict": "EXACT_OVERFLOW",
                "receipts": receipts,
                "max_raw_units": max(max_raw, int(st["raw_units"])),
                "terminal_cnf": None,
                "terminal_fingerprint": None,
            }
        assert base.verify_elimination_transition(state, v, out, CAP)
        max_raw = max(max_raw, int(st["raw_units"]))
        receipts.append({
            "step": step,
            "pivot": v,
            "status": "EXACT_LAND",
            "before_units": base.state_units(state),
            "raw_units": int(st["raw_units"]),
            "after_units": base.state_units(out),
            "pairs": int(st.get("pairs", 0)),
            "tautologies": int(st.get("tautologies", 0)),
        })
        state = out

    terminal = [list(c) for c in state]
    return {
        "front": name,
        "order": order,
        "order_sha256": digest(order),
        "verdict": "EXACT_TERMINAL" if state == ((),) else "EXACT_REPLAY_COMPLETE",
        "receipts": receipts,
        "max_raw_units": max_raw,
        "terminal_cnf": terminal,
        "terminal_fingerprint": base.fingerprint(state),
    }


def build_payload() -> dict[str, Any]:
    cnf = canonical_witness()
    stats = exact_stats(cnf)
    verify_target_stats(stats)
    truth = exact_truth_table(cnf)
    assert truth["UNSAT_exact_for_this_formula"]

    # Pre-existing exact local portfolio does not receive a free success claim:
    # width-3 resolution intentionally skips these width-4/5 axioms; 2SAT/GF2
    # exact recognizers are inapplicable.  This makes ordinary exact elimination
    # the relevant pre-existing concrete check.
    earlier = oldprobe.earlier_exact_local_lane(cnf)
    assert earlier is None

    abstract_rows = abstract_pivot_rows(cnf)
    exact_rows = exact_single_pivot_rows(cnf)
    assert all(r["actual_signature"] == [50, 25, 25] for r in abstract_rows)
    assert all(r["abstract_B"] == 3433 and r["abstract_verdict"] == "OPEN" for r in abstract_rows)
    assert all(r["fit"] and r["verdict"] == "EXACT_LAND" for r in exact_rows)

    fronts = [replay_elimination_front(k, cnf, v) for k, v in four_orders().items()]
    assert len({digest(f["order"]) for f in fronts}) == 4
    assert all(f["verdict"] == "EXACT_TERMINAL" for f in fronts)
    assert all(f["terminal_cnf"] == [[]] for f in fronts)

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "P_VS_NP": P_VS_NP,
        "N": N,
        "cap": CAP,
        "state": [NVAR, MCLAUSE, LITERAL_MASS],
        "JANUS_canonical_CNF": True,
        "forward_reachability_proved": False,
        "discovery_note": {
            "method": "OFFLINE_MILP_DISCOVERY_THEN_FROZEN_EXACT_VERIFICATION",
            "discovery_has_theorem_authority": False,
            "frozen_witness_verification_is_deterministic": True,
        },
        "correction_of_initial_weak_static_witness": {
            "initial_model_omitted_subsumption": True,
            "initial_79_clause_witness_after_JANUS_canon_cnf": {"m": 50, "L": 206},
            "initial_witness_canonical_status": "REJECTED_NEGATIVE_CONTROL",
            "current_witness_survives_JANUS_canon_cnf": True,
        },
        "witness": {
            "cnf": [list(c) for c in cnf],
            "stats": stats,
        },
        "exact_truth_table": truth,
        "preexisting_exact_local_lane_before_elimination": earlier,
        "abstract_peak_replay": abstract_rows,
        "exact_single_pivot_replay_C025": exact_rows,
        "abstract_open_but_exact_pivot_fits_count": sum(
            a["abstract_verdict"] == "OPEN" and e["fit"]
            for a, e in zip(abstract_rows, exact_rows)
        ),
        "four_front_exact_elimination": {
            "fronts": fronts,
            "all_four_terminal_unsat": all(f["terminal_cnf"] == [[]] for f in fronts),
            "all_four_stay_under_cap": all(f["verdict"] == "EXACT_TERMINAL" for f in fronts),
            "max_raw_units_any_front": max(f["max_raw_units"] for f in fronts),
            "truth_effect_of_order": "NONE__EXACT_EXISTENTIAL_ELIMINATION_REPLAY",
        },
        "interpretation": {
            "balanced_50_regular_JANUS_canonical_core_exists": True,
            "this_core_is_an_exact_cap_obstruction": False,
            "this_core_refutes_counts_only_nonexistence": True,
            "this_core_shows_abstract_OPEN_implies_exact_overflow": False,
            "observed_structural_slack": "TAUTOLOGICAL_RESOLVENTS_AND_CANONICAL_COMPRESSION_MAKE_ALL_SEVEN_CONCRETE_PIVOTS_FIT",
            "next_gate": "SEARCH_OR_RULE_OUT_A_JANUS_CANONICAL_50_REGULAR_BALANCED_CORE_WITH_ALL_CONCRETE_PIVOTS_OVERFLOWING_CAP",
        },
        "anti_self_deception_gate": {
            "same_run_lemma_promotion": False,
            "theorem_credit_allowed": THEOREM_CREDIT_ALLOWED,
            "forward_reachability_proved": False,
            "universal_balanced_core_totality_proved": False,
            "P_VS_NP": P_VS_NP,
            "claim_ceiling": "ONE_EXACT_JANUS_CANONICAL_CORE__STATIC_AND_LOCAL_ELIMINATION_FACTS_ONLY",
        },
    }
    payload["audit_sha256"] = digest(payload)
    return payload


def dimacs_text(cnf: base.CNF) -> str:
    lines = [
        "c JANUS exact canonical 50-regular balanced core",
        "c forward reachability unproved; P_VS_NP=OPEN",
        f"p cnf {NVAR} {len(cnf)}",
    ]
    lines += [" ".join(map(str, c)) + " 0" for c in cnf]
    return "\n".join(lines) + "\n"


def selftest() -> None:
    p = build_payload()
    assert p["JANUS_canonical_CNF"]
    assert p["witness"]["stats"]["degree"] == [50] * 7
    assert p["witness"]["stats"]["positive"] == [25] * 7
    assert p["exact_truth_table"]["UNSAT_exact_for_this_formula"]
    assert p["abstract_open_but_exact_pivot_fits_count"] == 7
    assert p["four_front_exact_elimination"]["all_four_terminal_unsat"]
    assert p["four_front_exact_elimination"]["all_four_stay_under_cap"]
    assert not p["anti_self_deception_gate"]["forward_reachability_proved"]
    assert p["P_VS_NP"] == "OPEN"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path, default=Path("artifacts/mad_lab/m2rs_four_front_janus_canonical_core.json"))
    ap.add_argument("--cnf-out", type=Path, default=Path("artifacts/mad_lab/m2rs_four_front_janus_canonical_core.cnf"))
    args = ap.parse_args()
    selftest()
    p = build_payload()
    cnf = canonical_witness()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.cnf_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(p, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.cnf_out.write_text(dimacs_text(cnf), encoding="utf-8")
    print(json.dumps(p, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
