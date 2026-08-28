#!/usr/bin/env python3
"""KEYMASTER pivot feature microscope for JUXTAPOSE calibration.

The goal is not to invent another proof rule.  It decomposes why a concrete
pivot was cheap or expensive so Keymaster / Pivot-Slime / TOPA can learn from
STRUCTURE rather than from witness-local variable numbers.

For every pivot we log:
  * parent width / co-occurrence / sign-conflict features available before
    constructing canonical output;
  * exact pair-conflict multiplicity (how many complementary non-pivot signs
    each parent pair contains);
  * exact tautology loss;
  * unique-resolvent / duplicate-or-retained-collision loss;
  * width distribution of unique raw resolvents;
  * exact raw C025 units and final canonical compression.

All learned use is advisory.  The existing C025 elimination function remains
proof-state authority.  P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import m2rs_four_front_janus_canonical_core as c25
from experiments.mad_lab import juxtapose_250x250_exact as c250

SCHEMA = "JANUS/KEYMASTER/PIVOT-FEATURE-MICROSCOPE/v1.0.0"
P_VS_NP = "OPEN"


def digest(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def hist(values: Iterable[int]) -> dict[str, int]:
    c = Counter(values)
    return {str(k): c[k] for k in sorted(c)}


def mean(xs: list[int]) -> float:
    return sum(xs) / max(1, len(xs))


def pivot_features(cnf: base.CNF, pivot: int, cap: int) -> dict[str, Any]:
    pos = [c for c in cnf if pivot in c]
    neg = [c for c in cnf if -pivot in c]
    retained = [c for c in cnf if pivot not in c and -pivot not in c]
    others = [v for v in base.vars_of(cnf) if v != pivot]
    pairs = len(pos) * len(neg)

    # O(n*d) structural co-occurrence summary.  This is intentionally separate
    # from exact pair enumeration so future work can measure whether cheap
    # summaries predict the expensive exact outcome.
    per_other: list[dict[str, int]] = []
    single_conflict_mass = 0
    same_sign_mass = 0
    support_overlap_mass = 0
    for v in others:
        pp = sum(v in c for c in pos)
        pm = sum(-v in c for c in pos)
        np = sum(v in c for c in neg)
        nm = sum(-v in c for c in neg)
        conflict = pp * nm + pm * np
        aligned = pp * np + pm * nm
        overlap = (pp + pm) * (np + nm)
        single_conflict_mass += conflict
        same_sign_mass += aligned
        support_overlap_mass += overlap
        per_other.append({
            "var_local": v,
            "pos_parent_plus": pp,
            "pos_parent_minus": pm,
            "neg_parent_plus": np,
            "neg_parent_minus": nm,
            "single_conflict_mass": conflict,
            "same_sign_mass": aligned,
            "support_overlap_mass": overlap,
        })

    raw = set(retained)
    raw_initial_units = base.state_units(tuple(raw))
    pair_conflict_hist = Counter()
    raw_resolvent_width_hist = Counter()
    unique_added_width_hist = Counter()
    tautologies = 0
    non_taut = 0
    unique_resolvents_seen: set[base.Clause] = set()
    unique_added = 0
    collision_with_existing_raw = 0

    for left in pos:
        ls = set(left)
        for right in neg:
            rs = set(right)
            conflicts = 0
            for v in others:
                if (v in ls and -v in rs) or (-v in ls and v in rs):
                    conflicts += 1
            pair_conflict_hist[conflicts] += 1
            if conflicts:
                tautologies += 1
                continue
            non_taut += 1
            res = base.resolve_on(left, right, pivot)
            assert res is not None
            raw_resolvent_width_hist[len(res)] += 1
            unique_resolvents_seen.add(res)
            if res in raw:
                collision_with_existing_raw += 1
                continue
            raw.add(res)
            unique_added += 1
            unique_added_width_hist[len(res)] += 1

    reconstructed_raw_units = base.state_units(tuple(raw))
    out, st = base.eliminate_var_capped(cnf, pivot, max(cap, reconstructed_raw_units + 1))
    assert out is not None
    assert base.verify_elimination_transition(cnf, pivot, out, max(cap, reconstructed_raw_units + 1))
    assert int(st["pairs"]) == pairs
    assert int(st["tautologies"]) == tautologies
    assert int(st["raw_units"]) == reconstructed_raw_units

    raw_clause_count = len(raw)
    canonical_clause_count = len(out)
    canonical_units = base.state_units(out)
    before_units = base.state_units(cnf)

    return {
        "pivot_id_local": pivot,
        "signature": [len(pos) + len(neg), len(pos), len(neg)],
        "before_units": before_units,
        "cap_reference": cap,
        "parent_pairs": pairs,
        "positive_parent_width_histogram": hist([len(c) for c in pos]),
        "negative_parent_width_histogram": hist([len(c) for c in neg]),
        "positive_parent_mean_width": mean([len(c) for c in pos]),
        "negative_parent_mean_width": mean([len(c) for c in neg]),
        "retained_clause_count": len(retained),
        "retained_units": raw_initial_units,
        "cheap_cooccurrence_features": {
            "single_conflict_mass": single_conflict_mass,
            "single_conflict_mass_per_pair": single_conflict_mass / max(1, pairs),
            "same_sign_mass": same_sign_mass,
            "same_sign_mass_per_pair": same_sign_mass / max(1, pairs),
            "support_overlap_mass": support_overlap_mass,
            "support_overlap_mass_per_pair": support_overlap_mass / max(1, pairs),
            "per_other_variable": per_other,
        },
        "exact_pair_structure": {
            "pair_conflict_multiplicity_histogram": {str(k): pair_conflict_hist[k] for k in sorted(pair_conflict_hist)},
            "tautologies": tautologies,
            "tautology_rate": tautologies / max(1, pairs),
            "non_tautological_pairs": non_taut,
            "raw_resolvent_width_histogram_before_dedupe": {str(k): raw_resolvent_width_hist[k] for k in sorted(raw_resolvent_width_hist)},
            "unique_resolvents_seen": len(unique_resolvents_seen),
            "unique_added_resolvents": unique_added,
            "duplicate_or_retained_collision_pairs": collision_with_existing_raw,
            "collision_rate_among_non_taut": collision_with_existing_raw / max(1, non_taut),
            "unique_added_width_histogram": {str(k): unique_added_width_hist[k] for k in sorted(unique_added_width_hist)},
        },
        "exact_outcome": {
            "raw_clause_count": raw_clause_count,
            "raw_units": reconstructed_raw_units,
            "canonical_clause_count": canonical_clause_count,
            "canonical_units": canonical_units,
            "raw_to_canonical_units_ratio": reconstructed_raw_units / max(1, canonical_units),
            "raw_clause_to_canonical_clause_ratio": raw_clause_count / max(1, canonical_clause_count),
            "subsumed_raw_clauses": raw_clause_count - canonical_clause_count,
            "state_reduction_fraction": max(0, before_units - canonical_units) / max(1, before_units),
            "cap_margin_reference": cap - reconstructed_raw_units,
            "fit_under_reference_cap": reconstructed_raw_units <= cap,
        },
    }


def build_payload() -> dict[str, Any]:
    root25 = c25.canonical_witness()
    root250 = c250.construct_250x250_core()
    cases = [
        {
            "id": "25x25-n7",
            "root": root25,
            "cap": c25.CAP,
            "source_fingerprint": base.fingerprint(root25),
        },
        {
            "id": "250x250-n8",
            "root": root250,
            # 105^2 is the first stress cap where all initial pivots fit.
            "cap": 105 * 105,
            "source_fingerprint": base.fingerprint(root250),
        },
    ]
    out_cases = []
    for case in cases:
        rows = [pivot_features(case["root"], v, case["cap"]) for v in base.vars_of(case["root"])]
        by_raw = sorted(rows, key=lambda r: (r["exact_outcome"]["raw_units"], r["pivot_id_local"]))
        for rank, row in enumerate(by_raw, 1):
            row["rank_by_exact_raw_local"] = rank
        out_cases.append({
            "case_id": case["id"],
            "root_fingerprint": case["source_fingerprint"],
            "reference_cap": case["cap"],
            "root_units": base.state_units(case["root"]),
            "rows": sorted(rows, key=lambda r: r["pivot_id_local"]),
            "best_pivot_local": by_raw[0]["pivot_id_local"],
            "best_raw_units": by_raw[0]["exact_outcome"]["raw_units"],
            "worst_pivot_local": by_raw[-1]["pivot_id_local"],
            "worst_raw_units": by_raw[-1]["exact_outcome"]["raw_units"],
        })

    payload = {
        "schema": SCHEMA,
        "status": "EXACT_FEATURE_DECOMPOSITION__CALIBRATION_ONLY",
        "P_VS_NP": P_VS_NP,
        "purpose": "Explain pivot cost mechanisms and provide structural features to Keymaster/Pivot-Slime/TOPA.",
        "cases": out_cases,
        "laws": [
            "PIVOT_ID_IS_WITNESS_LOCAL_NOT_TRANSFERABLE",
            "FEATURE_CORRELATION_IS_NOT_THEOREM",
            "TOPA_RELATION_IS_HYPOTHESIS_UNTIL_REPLAYED",
            "EXACT_C025_ELIMINATION_REMAINS_AUTHORITY",
            "P_VS_NP_IS_OPEN",
        ],
    }
    payload["sha256"] = digest(payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args(list(argv) if argv is not None else None)
    payload = build_payload()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(json.dumps({
        "schema": payload["schema"],
        "cases": [{
            "case_id": c["case_id"],
            "best_pivot": c["best_pivot_local"],
            "best_raw": c["best_raw_units"],
            "worst_pivot": c["worst_pivot_local"],
            "worst_raw": c["worst_raw_units"],
        } for c in payload["cases"]],
        "P_VS_NP": payload["P_VS_NP"],
        "sha256": payload["sha256"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
