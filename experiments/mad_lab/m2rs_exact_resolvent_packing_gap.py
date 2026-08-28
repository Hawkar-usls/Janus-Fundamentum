#!/usr/bin/env python3
"""Exact combinatorial microscope for the N=58, d=50, p=q=25 OPEN ridge.

Why does the abstract raw bound equal 3433?

After eliminating one pivot from (n,m,L)=(7,79,350):
- retained parent clauses: m-d = 29;
- opposite-sign parent pairs: p*q = 625;
- therefore the pre-subsumption raw set contains at most 654 *distinct* clauses;
- every raw clause lives on at most the remaining six variables.

The universe of non-tautological clauses over six variables is the ternary
universe {-1,0,+1}^6.  A clause of width k contributes (1+k) C025 state units.
Selecting the 654 heaviest distinct clauses from that universe gives total raw
state units exactly 3433 (including the outer state header unit).

Thus the famous 3433 is an extremal structure-forgetting packing bound.  To fit
under 58^2=3364, any universally valid structural argument only needs to force
at least 69 units of deficit through tautological pairs, duplicate resolvents,
lower-width resolvents, or other exact structure.

This file proves the finite packing identity and measures the deficit on the
frozen JANUS-canonical 50-regular balanced witness.  It does NOT prove the
required universal 69-unit deficit. P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import m2rs_four_front_janus_canonical_core as C

SCHEMA = "JANUS/MAD-LAB/EXACT-RESOLVENT-PACKING-GAP/v1"
P_VS_NP = "OPEN"
REMAINING_VARS = 6
RETAINED = 79 - 50
PAIR_COUNT = 25 * 25
RAW_CARDINALITY_CAP = RETAINED + PAIR_COUNT
CAP = 58 * 58
ABSTRACT_EXTREMUM = 3433
REQUIRED_DEFICIT = ABSTRACT_EXTREMUM - CAP


def clause_width_universe(n: int) -> list[int]:
    return [sum(x != 0 for x in t) for t in itertools.product((-1, 0, 1), repeat=n)]


def extremal_packing() -> dict[str, Any]:
    widths = clause_width_universe(REMAINING_VARS)
    hist = Counter(widths)
    assert len(widths) == 3 ** REMAINING_VARS == 729
    assert hist == Counter({4: 240, 5: 192, 3: 160, 6: 64, 2: 60, 1: 12, 0: 1})

    ranked = sorted(widths, reverse=True)
    selected = ranked[:RAW_CARDINALITY_CAP]
    contribution = sum(1 + w for w in selected)
    state_units = 1 + contribution
    selected_hist = Counter(selected)

    assert RAW_CARDINALITY_CAP == 654
    assert state_units == ABSTRACT_EXTREMUM
    assert selected_hist == Counter({4: 240, 5: 192, 3: 158, 6: 64})
    assert REQUIRED_DEFICIT == 69
    return {
        "remaining_variables": REMAINING_VARS,
        "ternary_non_tautological_clause_universe_size": len(widths),
        "universe_width_histogram": {str(k): hist[k] for k in sorted(hist)},
        "retained_clause_cap": RETAINED,
        "opposite_sign_pair_cap": PAIR_COUNT,
        "raw_distinct_clause_cardinality_cap": RAW_CARDINALITY_CAP,
        "heaviest_654_width_histogram": {str(k): selected_hist[k] for k in sorted(selected_hist)},
        "heaviest_654_clause_contribution_units": contribution,
        "state_header_units": 1,
        "exact_extremal_state_units": state_units,
        "N2_cap": CAP,
        "required_universal_structural_deficit_to_land": REQUIRED_DEFICIT,
    }


def witness_deficits() -> list[dict[str, Any]]:
    cnf = C.canonical_witness()
    rows = []
    for v in base.vars_of(cnf):
        out, st = base.eliminate_var_capped(cnf, v, CAP)
        assert out is not None
        raw = int(st["raw_units"])
        rows.append({
            "pivot": v,
            "pairs": int(st["pairs"]),
            "tautologies": int(st["tautologies"]),
            "raw_units": raw,
            "packing_deficit_from_3433": ABSTRACT_EXTREMUM - raw,
            "margin_below_cap": CAP - raw,
            "fits": True,
        })
    return rows


def build_payload() -> dict[str, Any]:
    packing = extremal_packing()
    rows = witness_deficits()
    min_deficit = min(r["packing_deficit_from_3433"] for r in rows)
    max_raw = max(r["raw_units"] for r in rows)
    assert max_raw == 949
    assert min_deficit == ABSTRACT_EXTREMUM - 949 == 2484
    assert min_deficit > REQUIRED_DEFICIT
    return {
        "schema": SCHEMA,
        "P_VS_NP": P_VS_NP,
        "packing_identity": packing,
        "frozen_canonical_witness": {
            "fingerprint_C025": C.exact_stats(C.canonical_witness())["fingerprint_C025"],
            "pivot_rows": rows,
            "max_exact_raw_units": max_raw,
            "minimum_observed_packing_deficit": min_deficit,
        },
        "interpretation": {
            "3433_explained_as_structure_forgetting_extremal_packing": True,
            "only_69_units_needed_for_universal_land": True,
            "universal_69_unit_deficit_proved": False,
            "candidate_sources_of_deficit": [
                "TAUTOLOGICAL_RESOLVENT_PAIRS",
                "DUPLICATE_RESOLVENTS",
                "LOWER_WIDTH_RESOLVENTS",
                "CANONICAL_STRUCTURE_CONSTRAINTS",
            ],
            "next_theorem_target": "PROVE_EVERY_REACHABLE_OR_EVERY_JANUS_CANONICAL_50_REGULAR_BALANCED_CORE_FORCES_AT_LEAST_69_RAW_PACKING_UNITS_OF_DEFICIT",
        },
        "anti_self_deception_gate": {
            "finite_packing_identity_exact": True,
            "one_witness_deficit_exact": True,
            "universal_deficit_claim": False,
            "forward_reachability_proved": False,
            "theorem_credit_allowed": False,
            "P_VS_NP": P_VS_NP,
        },
    }


def selftest() -> None:
    p = build_payload()
    assert p["packing_identity"]["exact_extremal_state_units"] == 3433
    assert p["packing_identity"]["required_universal_structural_deficit_to_land"] == 69
    assert p["frozen_canonical_witness"]["max_exact_raw_units"] == 949
    assert p["frozen_canonical_witness"]["minimum_observed_packing_deficit"] == 2484
    assert not p["interpretation"]["universal_69_unit_deficit_proved"]
    assert p["P_VS_NP"] == "OPEN"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/mad_lab/m2rs_exact_resolvent_packing_gap.json"))
    args = ap.parse_args()
    selftest()
    p = build_payload()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(p, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(p, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
