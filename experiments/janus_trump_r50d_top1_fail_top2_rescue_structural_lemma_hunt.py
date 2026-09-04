from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50b_minimal_deadcore_structural_classification as r50b
import janus_trump_r50c_top2_min_taut_prospective_falsifier as r50c

GATE = "JANUS_TRUMP_R50D_TOP1_FAIL_TOP2_RESCUE_STRUCTURAL_LEMMA_HUNT"
WIDTH_CAP = 4
EXPECTED_ROOTS = 52
EXPECTED_HARD_STATES = 441
EXPECTED_RANK1_SAFE = 429
EXPECTED_RANK2_RESCUES = 12

# Frozen, truth-blind input-side feature family. Outcome fields are recorded separately
# and are forbidden from candidate invariant generation.
INTEGER_FEATURES = (
    "tautological_cross_pair_count",
    "retained_nontautological_pair_count",
    "bad_pair_count_union_ge_5",
    "positive_parent_count",
    "negative_parent_count",
    "minority_parent_count",
    "majority_parent_count",
    "polarity_imbalance",
    "cross_parent_product",
    "chi_star",
    "distinct_bad_parent_clause_count",
    "maximum_bad_parent_reuse",
    "positive_width2_parent_count",
    "positive_width3_parent_count",
    "positive_width4_parent_count",
    "negative_width2_parent_count",
    "negative_width3_parent_count",
    "negative_width4_parent_count",
    "minority_width4_parent_count",
    "majority_width4_parent_count",
    "short_parent_count",
    "retained_union5_count",
    "retained_union6_count",
    "residual_overlap0_count",
    "residual_overlap1_count",
    "bad_residual_overlap0_count",
    "bad_residual_overlap1_count",
)

FRACTION_FEATURES = (
    "tautological_cross_pair_fraction",
    "retained_cross_pair_fraction",
    "bad_cross_pair_fraction",
    "bad_among_retained_fraction",
)

SELECTOR_DERIVED_FEATURES = {
    "tautological_cross_pair_count",
    "tautological_cross_pair_fraction",
}

OPS = ("<", "<=", "=", ">=", ">")


class IntegrityFailure(RuntimeError):
    pass


def canon(formula):
    return r33.canonical_formula(formula)


def fhash(formula):
    return r49i.fhash(canon(formula))


def max_width(formula):
    return r49i.max_width(canon(formula))


def parent_width_counts(formula, var):
    f = canon(formula)
    pos = Counter(len(c) for c in f if int(var) in c)
    neg = Counter(len(c) for c in f if -int(var) in c)
    return {
        "positive_width2_parent_count": int(pos.get(2, 0)),
        "positive_width3_parent_count": int(pos.get(3, 0)),
        "positive_width4_parent_count": int(pos.get(4, 0)),
        "negative_width2_parent_count": int(neg.get(2, 0)),
        "negative_width3_parent_count": int(neg.get(3, 0)),
        "negative_width4_parent_count": int(neg.get(4, 0)),
    }


def _fraction_pair(num, den):
    num = int(num)
    den = int(den)
    if den <= 0:
        return [0, 1]
    q = Fraction(num, den)
    return [int(q.numerator), int(q.denominator)]


def _hist_value(hist, key):
    return int(hist.get(str(int(key)), 0))


def input_descriptor(formula, var):
    f = canon(formula)
    var = int(var)
    g = r50b.cross_pair_profile(f, var)
    p = r49i.variable_profile(f, var)
    widths = parent_width_counts(f, var)
    pos = int(p["positive_parent_count"])
    neg = int(p["negative_parent_count"])
    product = pos * neg
    minority = min(pos, neg)
    majority = max(pos, neg)
    if pos < neg:
        minority_w4 = widths["positive_width4_parent_count"]
        majority_w4 = widths["negative_width4_parent_count"]
    elif neg < pos:
        minority_w4 = widths["negative_width4_parent_count"]
        majority_w4 = widths["positive_width4_parent_count"]
    else:
        minority_w4 = min(widths["positive_width4_parent_count"], widths["negative_width4_parent_count"])
        majority_w4 = max(widths["positive_width4_parent_count"], widths["negative_width4_parent_count"])

    retained = int(g["retained_nontautological_pair_count"])
    taut = int(g["tautological_cross_pair_count"])
    bad = int(g["bad_pair_count_union_ge_5"])
    out = {
        "var": var,
        "tautological_cross_pair_count": taut,
        "retained_nontautological_pair_count": retained,
        "bad_pair_count_union_ge_5": bad,
        "positive_parent_count": pos,
        "negative_parent_count": neg,
        "minority_parent_count": minority,
        "majority_parent_count": majority,
        "polarity_imbalance": abs(pos - neg),
        "cross_parent_product": product,
        "chi_star": int(p["chi_star"]),
        "distinct_bad_parent_clause_count": int(g["distinct_bad_parent_clause_count"]),
        "maximum_bad_parent_reuse": int(g["maximum_bad_parent_reuse"]),
        **widths,
        "minority_width4_parent_count": int(minority_w4),
        "majority_width4_parent_count": int(majority_w4),
        "short_parent_count": int(
            widths["positive_width2_parent_count"]
            + widths["positive_width3_parent_count"]
            + widths["negative_width2_parent_count"]
            + widths["negative_width3_parent_count"]
        ),
        "retained_union5_count": _hist_value(g["retained_union_size_histogram"], 5),
        "retained_union6_count": _hist_value(g["retained_union_size_histogram"], 6),
        "residual_overlap0_count": _hist_value(g["signed_residual_intersection_histogram"], 0),
        "residual_overlap1_count": _hist_value(g["signed_residual_intersection_histogram"], 1),
        "bad_residual_overlap0_count": _hist_value(g["bad_signed_residual_intersection_histogram"], 0),
        "bad_residual_overlap1_count": _hist_value(g["bad_signed_residual_intersection_histogram"], 1),
        "tautological_cross_pair_fraction": _fraction_pair(taut, product),
        "retained_cross_pair_fraction": _fraction_pair(retained, product),
        "bad_cross_pair_fraction": _fraction_pair(bad, product),
        "bad_among_retained_fraction": _fraction_pair(bad, retained),
        "retained_union_size_histogram": dict(g["retained_union_size_histogram"]),
        "signed_residual_intersection_histogram": dict(g["signed_residual_intersection_histogram"]),
        "bad_signed_residual_intersection_histogram": dict(g["bad_signed_residual_intersection_histogram"]),
    }
    return out


def outcome_descriptor(formula, var):
    f = canon(formula)
    p = r49i.variable_profile(f, int(var))
    row = r50b.exact_r47j_row(f, int(var), p)
    return {
        "var": int(var),
        "candidate": bool(row.get("candidate", False)),
        "width4_safe": bool(row.get("width4_safe", False)),
        "final_max_width": row.get("final_max_width"),
        "strict_variable_descent": row.get("strict_variable_descent"),
        "no_fresh_variables": row.get("no_fresh_variables"),
        "reason_codes": list(row.get("reason_codes", [])),
        "independent_replay_pass": row.get("independent_replay_pass"),
        "final_CLV": row.get("final_CLV"),
        "final_hash": row.get("final_hash"),
    }


def pair_record(formula, probe, root_index, trace_step, provenance):
    if not probe["applicable"]:
        raise IntegrityFailure("R50D_PAIR_PROBE_NOT_APPLICABLE")
    selected = probe["selected_rows"]
    if len(selected) != 2:
        raise IntegrityFailure(("R50D_EXPECTED_TOP2", len(selected), probe["state_hash"]))
    first_safe_rank = probe["first_safe_rank"]
    if first_safe_rank not in (1, 2):
        raise IntegrityFailure(("R50D_R50C_TOP2_REGRESSION", probe["state_hash"], first_safe_rank))

    v1 = int(selected[0]["var"])
    v2 = int(selected[1]["var"])
    i1 = input_descriptor(formula, v1)
    i2 = input_descriptor(formula, v2)
    o1 = outcome_descriptor(formula, v1)
    o2 = outcome_descriptor(formula, v2)

    if bool(o1["width4_safe"]) != (first_safe_rank == 1):
        raise IntegrityFailure(("R50D_RANK1_OUTCOME_MISMATCH", probe["state_hash"]))
    if not bool(o2["width4_safe"]):
        raise IntegrityFailure(("R50D_RANK2_NOT_SAFE", probe["state_hash"]))

    return {
        "state_hash": probe["state_hash"],
        "state_CLV": probe["state_CLV"],
        "root_index": int(root_index),
        "trace_step": int(trace_step),
        "root_provenance": provenance,
        "class": "RANK1_SAFE_CONTROL" if first_safe_rank == 1 else "RANK1_FAIL_RANK2_RESCUE",
        "rank1": {"input": i1, "outcome": o1},
        "rank2": {"input": i2, "outcome": o2},
        "frozen_named_candidate": {
            "name": "MINORITY_POLARITY_SUPPORT_NONDECREASE",
            "formula": "min(|P_v2|,|N_v2|) >= min(|P_v1|,|N_v1|)",
            "holds": bool(i2["minority_parent_count"] >= i1["minority_parent_count"]),
        },
    }


def trace_root_pairs(root, provenance, root_index):
    root = canon(root)
    root_vars = set(r33.variables(root))
    current = root
    seen = set()
    cap = 2 * max(1, len(root_vars)) + 8
    pairs = []

    for step_index in range(cap):
        h = fhash(current)
        if h in seen:
            raise IntegrityFailure(("R50D_TRACE_CYCLE", root_index, h))
        seen.add(h)
        if max_width(current) > WIDTH_CAP:
            raise IntegrityFailure(("R50D_TRACE_WIDTH_DRIFT", root_index, max_width(current)))
        if not set(r33.variables(current)).issubset(root_vars):
            raise IntegrityFailure(("R50D_TRACE_FRESH_VARIABLE", root_index, h))

        probe = r50c.hard_state_probe(current)
        if probe["applicable"]:
            pairs.append(pair_record(current, probe, root_index, step_index, provenance))

        step = r50a.exact_step(current)
        if step["kind"] == "OPEN_OBSTRUCTION":
            raise IntegrityFailure(("R50D_R50A_OPEN_REGRESSION", root_index, h))
        if step["kind"] == "TERMINAL":
            return {
                "root_index": int(root_index),
                "root_hash": fhash(root),
                "provenance": provenance,
                "hard_pair_count": len(pairs),
                "rank1_safe_count": sum(1 for x in pairs if x["class"] == "RANK1_SAFE_CONTROL"),
                "rank2_rescue_count": sum(1 for x in pairs if x["class"] == "RANK1_FAIL_RANK2_RESCUE"),
                "pairs": pairs,
            }
        current = canon(step["successor"])

    raise IntegrityFailure(("R50D_TRACE_STEP_CAP", root_index, cap, fhash(current)))


def run_shard(shard_index=0, shard_count=4):
    shard_index = int(shard_index)
    shard_count = int(shard_count)
    roots = r50c.collect_prospective_roots()
    if len(roots) != EXPECTED_ROOTS:
        raise IntegrityFailure(("R50D_ROOT_CORPUS_DRIFT", len(roots), EXPECTED_ROOTS))
    assigned = [
        (idx, root, provenance)
        for idx, (root, provenance) in enumerate(roots, 1)
        if (idx - 1) % shard_count == shard_index
    ]
    records = [trace_root_pairs(root, provenance, idx) for idx, root, provenance in assigned]
    pairs = [p for r in records for p in r["pairs"]]
    rescues = [p for p in pairs if p["class"] == "RANK1_FAIL_RANK2_RESCUE"]
    controls = [p for p in pairs if p["class"] == "RANK1_SAFE_CONTROL"]

    return {
        "gate": GATE,
        "mode": "SHARD_EXTRACTION",
        "parent_R50C_commit": "f1de3386985960ed104efe3c8b6d3d6798686766",
        "source_R50C_run_id": 33909973868,
        "shard": {"index": shard_index, "count": shard_count},
        "metrics": {
            "assigned_roots": len(assigned),
            "hard_states": len(pairs),
            "rank1_safe_controls": len(controls),
            "rank1_fail_rank2_rescues": len(rescues),
            "named_candidate_rescue_support": sum(
                int(p["frozen_named_candidate"]["holds"]) for p in rescues
            ),
        },
        "roots": [
            {
                "root_index": r["root_index"],
                "root_hash": r["root_hash"],
                "provenance": r["provenance"],
                "hard_pair_count": r["hard_pair_count"],
                "rank1_safe_count": r["rank1_safe_count"],
                "rank2_rescue_count": r["rank2_rescue_count"],
            }
            for r in records
        ],
        "pairs": pairs,
        "firewall": firewall(),
    }


def _as_value(descriptor, feature):
    value = descriptor[feature]
    if feature in FRACTION_FEATURES:
        return Fraction(int(value[0]), int(value[1]))
    return int(value)


def _relation(a, b, op):
    if op == "<":
        return b < a
    if op == "<=":
        return b <= a
    if op == "=":
        return b == a
    if op == ">=":
        return b >= a
    if op == ">":
        return b > a
    raise ValueError(op)


def candidate_predicates(pairs):
    rescues = [p for p in pairs if p["class"] == "RANK1_FAIL_RANK2_RESCUE"]
    controls = [p for p in pairs if p["class"] == "RANK1_SAFE_CONTROL"]
    if not rescues:
        raise IntegrityFailure("R50D_NO_RESCUES")

    rows = []
    for feature in INTEGER_FEATURES + FRACTION_FEATURES:
        for op in OPS:
            rescue_holds = []
            for p in rescues:
                a = _as_value(p["rank1"]["input"], feature)
                b = _as_value(p["rank2"]["input"], feature)
                rescue_holds.append(_relation(a, b, op))
            if not all(rescue_holds):
                continue
            control_true = 0
            for p in controls:
                a = _as_value(p["rank1"]["input"], feature)
                b = _as_value(p["rank2"]["input"], feature)
                control_true += int(_relation(a, b, op))
            rows.append({
                "feature": feature,
                "relation": f"v2 {op} v1",
                "rescue_support": len(rescues),
                "rescue_total": len(rescues),
                "control_true": int(control_true),
                "control_total": len(controls),
                "selector_derived": feature in SELECTOR_DERIVED_FEATURES,
                "outcome_blind": True,
            })

    op_complexity = {"<": 0, "=": 0, ">": 0, "<=": 1, ">=": 1}
    def relation_op(row):
        return row["relation"].split()[1]
    rows.sort(
        key=lambda x: (
            bool(x["selector_derived"]),
            Fraction(x["control_true"], max(1, x["control_total"])),
            op_complexity[relation_op(x)],
            x["feature"],
            x["relation"],
        )
    )
    return rows


def synthesize(shard_dir):
    shard_dir = Path(shard_dir)
    files = sorted(shard_dir.glob("JANUS_TRUMP_R50D_*_SHARD_*_OF_4.json"))
    if len(files) != 4:
        raise IntegrityFailure(("R50D_EXPECTED_4_SHARDS", len(files), [str(x) for x in files]))
    shards = [json.loads(p.read_text()) for p in files]
    pairs = [p for d in shards for p in d["pairs"]]
    rescues = [p for p in pairs if p["class"] == "RANK1_FAIL_RANK2_RESCUE"]
    controls = [p for p in pairs if p["class"] == "RANK1_SAFE_CONTROL"]

    root_indices = sorted({int(r["root_index"]) for d in shards for r in d["roots"]})
    if len(root_indices) != EXPECTED_ROOTS:
        raise IntegrityFailure(("R50D_SYNTH_ROOT_DRIFT", len(root_indices), EXPECTED_ROOTS))
    if len(pairs) != EXPECTED_HARD_STATES:
        raise IntegrityFailure(("R50D_HARD_STATE_DRIFT", len(pairs), EXPECTED_HARD_STATES))
    if len(controls) != EXPECTED_RANK1_SAFE:
        raise IntegrityFailure(("R50D_RANK1_SAFE_DRIFT", len(controls), EXPECTED_RANK1_SAFE))
    if len(rescues) != EXPECTED_RANK2_RESCUES:
        raise IntegrityFailure(("R50D_RESCUE_COUNT_DRIFT", len(rescues), EXPECTED_RANK2_RESCUES))

    named_support = sum(int(p["frozen_named_candidate"]["holds"]) for p in rescues)
    failure_reasons = Counter(code for p in rescues for code in p["rank1"]["outcome"]["reason_codes"])
    candidates = candidate_predicates(pairs)
    nonselector = [x for x in candidates if not x["selector_derived"]]

    verdict = (
        "FINITE_R50C_12_RESCUES_SUPPORT_MINORITY_POLARITY_TRANSFER_CANDIDATE__LEMMA_OPEN"
        if named_support == len(rescues)
        else "EXPLICIT_R50C_RESCUE_FALSIFIES_MINORITY_POLARITY_TRANSFER_CANDIDATE"
    )

    return {
        "gate": GATE,
        "mode": "SYNTHESIS",
        "verdict": verdict,
        "source": {
            "R50C_run_id": 33909973868,
            "R50C_head": "f1de3386985960ed104efe3c8b6d3d6798686766",
            "aggregate_R50C_result_was_known_before_R50D": True,
            "detailed_input_feature_relation_was_frozen_before_R50D_extraction": True,
            "claim_level": "LATE_FROZEN_SECONDARY_HOLDOUT_AUDIT__NOT_PROSPECTIVE_DATA_GENERATION",
        },
        "metrics": {
            "roots": len(root_indices),
            "hard_states": len(pairs),
            "rank1_safe_controls": len(controls),
            "rank1_fail_rank2_rescues": len(rescues),
            "named_candidate_rescue_support": named_support,
            "named_candidate_control_support": sum(
                int(p["rank2"]["input"]["minority_parent_count"] >= p["rank1"]["input"]["minority_parent_count"])
                for p in controls
            ),
            "rank1_failure_reason_histogram": dict(sorted(failure_reasons.items())),
            "input_side_universal_rescue_predicate_count": len(candidates),
            "nonselector_universal_rescue_predicate_count": len(nonselector),
        },
        "frozen_named_candidate": {
            "name": "MINORITY_POLARITY_SUPPORT_NONDECREASE",
            "definition": "m_F(v)=min(|P_v|,|N_v|)",
            "candidate_relation": "m_F(v2) >= m_F(v1)",
            "rescue_support": named_support,
            "rescue_total": len(rescues),
            "control_support": sum(
                int(p["rank2"]["input"]["minority_parent_count"] >= p["rank1"]["input"]["minority_parent_count"])
                for p in controls
            ),
            "control_total": len(controls),
            "theorem_status": "OPEN",
            "sufficient_for_rank2_safety_proved": False,
        },
        "top_nonselector_input_predicates": nonselector[:20],
        "all_universal_input_predicates": candidates,
        "rescue_pairs": rescues,
        "interpretation": {
            "R50D_is_structural_discovery_not_universal_proof": True,
            "outcome_fields_used_for_candidate_generation": False,
            "R50E_required_before_any_transfer_lemma_claim": True,
            "next_target": "derive a symbolic mechanism connecting minority-polarity support and disappearance of width-5 residual clauses, then falsify on a new unseen reachable corpus",
        },
        "firewall": firewall(),
    }


def firewall():
    return {
        "HEURISTIC_PROOF_AUTHORITY": False,
        "ML_PROOF_AUTHORITY": False,
        "RANDOM_PROOF_AUTHORITY": False,
        "R50D_FINITE_12_IS_TRANSFER_LEMMA": False,
        "TOP2_UNIVERSAL_COVERAGE": "OPEN",
        "UNIVERSAL_R50A_PROGRESS": "OPEN",
        "UNIVERSAL_W4_COVERAGE": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard-index", type=int)
    ap.add_argument("--shard-count", type=int, default=4)
    ap.add_argument("--synthesize-dir")
    args = ap.parse_args()

    if args.synthesize_dir:
        out = synthesize(args.synthesize_dir)
        path = Path("artifacts/JANUS_TRUMP_R50D_TOP1_FAIL_TOP2_RESCUE_STRUCTURAL_LEMMA_HUNT_SYNTHESIS.json")
    else:
        if args.shard_index is None:
            raise SystemExit("--shard-index required unless --synthesize-dir is used")
        out = run_shard(args.shard_index, args.shard_count)
        path = Path(
            f"artifacts/JANUS_TRUMP_R50D_TOP1_FAIL_TOP2_RESCUE_STRUCTURAL_LEMMA_HUNT_SHARD_{args.shard_index}_OF_{args.shard_count}.json"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "mode": out["mode"],
        "verdict": out.get("verdict"),
        "metrics": out.get("metrics"),
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
