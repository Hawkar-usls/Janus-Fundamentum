from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g24_pairwise_counterpolarity_closure_replay as r50g24

GATE = "JANUS_TRUMP_R50G25A_POST_DP_BCE_BVE_JOINT_DIRECT_DEBT_HYPERGRAPH"
TARGET_FIRST_RULES = {
    "R33:BLOCKED_CLAUSE_ELIMINATION",
    "R33:BOUNDED_VARIABLE_ELIMINATION",
}
EXPECTED_PAIR_TRIALS = 1774
EXPECTED_TARGET_OCCURRENCES = 1673


def canon(formula):
    return r50g24.canon(formula)


def variables(formula):
    return r50g24.r50g23.r33.variables(canon(formula))


def blocked_candidates(formula):
    formula = canon(formula)
    out = []
    for clause in formula:
        cset = set(clause)
        for lit in clause:
            blocked = True
            opposite_count = 0
            for other in formula:
                if -lit not in other:
                    continue
                opposite_count += 1
                resolvent = (cset - {lit}) | (set(other) - {-lit})
                if not any(-x in resolvent for x in resolvent):
                    blocked = False
                    break
            if blocked:
                out.append({
                    "clause": tuple(clause),
                    "blocking_literal": int(lit),
                    "opposite_parent_count": opposite_count,
                })
    return out


def all_bve_candidates(formula):
    r33 = r50g24.r50g23.r33
    formula = canon(formula)
    current = r33.measure(formula)
    out = []
    for x in r33.variables(formula):
        pos = [c for c in formula if x in c]
        neg = [c for c in formula if -x in c]
        if not pos or not neg:
            continue
        resolvents = []
        for p in pos:
            for n in neg:
                rr = (set(p) - {x}) | (set(n) - {-x})
                if any(-lit in rr for lit in rr):
                    continue
                resolvents.append(r33.canonical_clause(rr))
        resolvents = sorted(set(resolvents))
        removed = set(pos + neg)
        transformed = r33.canonical_formula([c for c in formula if c not in removed] + resolvents)
        if len(resolvents) <= len(removed) and r33.measure(transformed) < current:
            out.append({
                "pivot": int(x),
                "positive_parent_count": len(pos),
                "negative_parent_count": len(neg),
                "resolvent_count": len(resolvents),
                "measure_after": list(r33.measure(transformed)),
            })
    return out


def all_binary_additions(formula):
    formula = canon(formula)
    existing = set(formula)
    vs = list(variables(formula))
    out = []
    for a, b in itertools.combinations(vs, 2):
        for la in (a, -a):
            for lb in (b, -b):
                clause = r50g24.r50g23.r33.canonical_clause((la, lb))
                if clause in existing:
                    continue
                out.append(clause)
    return sorted(set(out))


def bce_requirement_hit(requirement, addition):
    lit = int(requirement["blocking_literal"])
    if -lit not in addition:
        return False
    clause = set(requirement["clause"])
    resolvent = (clause - {lit}) | (set(addition) - {-lit})
    return not any(-x in resolvent for x in resolvent)


def coverage_profile(formula):
    formula = canon(formula)
    bces = blocked_candidates(formula)
    bves = all_bve_candidates(formula)
    requirements = []
    for idx, row in enumerate(bces):
        requirements.append(("BCE", idx, row))
    for idx, row in enumerate(bves):
        requirements.append(("BVE", idx, row))

    if not requirements:
        return {
            "BCE_candidate_count": 0,
            "BVE_candidate_count": 0,
            "requirement_count": 0,
            "binary_addition_universe_size": len(all_binary_additions(formula)),
            "cover_class": "ZERO_NO_BCE_BVE_DEBT",
            "minimum_binary_incidence_cover_lower_bound": 0,
            "uncoverable_requirement_count": 0,
            "max_requirements_hit_by_one_clause": 0,
        }

    additions = all_binary_additions(formula)
    full = (1 << len(requirements)) - 1
    masks = []
    per_requirement_support = [0] * len(requirements)

    for addition in additions:
        mask = 0
        for i, (kind, _idx, row) in enumerate(requirements):
            hit = False
            if kind == "BCE":
                hit = bce_requirement_hit(row, addition)
            elif kind == "BVE":
                x = int(row["pivot"])
                hit = x in addition or -x in addition
            if hit:
                mask |= 1 << i
                per_requirement_support[i] += 1
        if mask:
            masks.append((addition, mask))

    unique_masks = sorted(set(mask for _c, mask in masks))
    uncoverable = sum(1 for count in per_requirement_support if count == 0)
    max_hit = max((mask.bit_count() for mask in unique_masks), default=0)

    if uncoverable:
        cover_class = "UNREACHABLE_BY_POST_DP_BINARY_INCIDENCE_UNIVERSE"
        lower_bound = None
    elif any(mask == full for mask in unique_masks):
        cover_class = "ONE_BINARY_CLAUSE_CAN_PAY_ALL_NECESSARY_INCIDENCES"
        lower_bound = 1
    else:
        pair_cover = False
        for i, m1 in enumerate(unique_masks):
            for m2 in unique_masks[i:]:
                if (m1 | m2) == full:
                    pair_cover = True
                    break
            if pair_cover:
                break
        if pair_cover:
            cover_class = "TWO_BINARY_CLAUSES_CAN_PAY_ALL_NECESSARY_INCIDENCES"
            lower_bound = 2
        else:
            cover_class = "AT_LEAST_THREE_BINARY_CLAUSES_NEEDED_FOR_SNAPSHOT_INCIDENCE_COVER"
            lower_bound = 3

    return {
        "BCE_candidate_count": len(bces),
        "BVE_candidate_count": len(bves),
        "requirement_count": len(requirements),
        "binary_addition_universe_size": len(additions),
        "cover_class": cover_class,
        "minimum_binary_incidence_cover_lower_bound": lower_bound,
        "uncoverable_requirement_count": uncoverable,
        "max_requirements_hit_by_one_clause": max_hit,
        "BCE_candidates": [
            {
                "clause": list(x["clause"]),
                "blocking_literal": int(x["blocking_literal"]),
                "opposite_parent_count": int(x["opposite_parent_count"]),
            }
            for x in bces
        ],
        "BVE_candidates": bves,
    }


def enumerate_pair_post_dp_states():
    # This call is deliberate: R50G25A has no authority unless the exact
    # R50G24 independent replay transcript first passes all hard assertions.
    parent = r50g24.run()
    if parent["pair_trial_count"] != EXPECTED_PAIR_TRIALS:
        raise AssertionError(("R50G25A_PARENT_PAIR_COUNT_DRIFT", parent["pair_trial_count"]))
    if parent["strong_candidate_count"] != 0:
        raise AssertionError(("R50G25A_PARENT_STRONG_SURVIVOR_DRIFT", parent["strong_candidate_count"]))

    skeletons = r50g24.r50g23.clean_skeletons_from_frozen_r50g22()
    rows = []
    pair_count = 0

    for item in skeletons:
        source = canon(item["source"])
        vars_ = r50g24.formula_variables(source)
        base = r50g24.r50g23.audit_one_skeleton(item)
        base_label = str(base["transition_labels"][0])
        base_debt = base["first_transition_direct_blocking_debt"]

        for c1 in r50g24.binary_clauses(r50g24.required_literals(base_debt), vars_):
            if c1 in source:
                continue
            s1 = r50g24.replay_state(source, [c1])
            if not s1["ok"] or s1["first_label"] == base_label:
                continue
            debt2 = s1.get("debt")
            req2 = r50g24.required_literals(debt2)
            if not req2:
                continue

            for c2 in r50g24.binary_clauses(req2, vars_):
                if c2 == c1 or c2 in source:
                    continue
                pair_count += 1
                s2 = r50g24.replay_state(source, [c1, c2])
                if not s2["ok"]:
                    raise AssertionError(("R50G25A_R47J_REPLAY_DRIFT", item["spec"], c1, c2, s2))
                if s2["first_label"] not in TARGET_FIRST_RULES:
                    continue
                rows.append({
                    "spec": item["spec"],
                    "source_hash": item["source_hash"],
                    "first_clause": list(c1),
                    "second_clause": list(c2),
                    "first_rule": s2["first_label"],
                    "forced_formula": canon(s2["forced"]),
                    "forced_CLV": list(r50g24.r50g23.r33.measure(s2["forced"])),
                })

    if pair_count != EXPECTED_PAIR_TRIALS:
        raise AssertionError(("R50G25A_PAIR_ENUMERATION_DRIFT", pair_count))
    if len(rows) != EXPECTED_TARGET_OCCURRENCES:
        raise AssertionError(("R50G25A_TARGET_OCCURRENCE_DRIFT", len(rows)))
    return parent, rows


def run():
    parent, occurrences = enumerate_pair_post_dp_states()

    # Collapse duplicate post-DP formulas so structural conclusions are not
    # distorted by many source-level mutation pairs reaching the same state.
    unique = {}
    for row in occurrences:
        key = tuple(row["forced_formula"])
        entry = unique.setdefault(key, {
            "forced_formula": row["forced_formula"],
            "forced_CLV": row["forced_CLV"],
            "first_rule": row["first_rule"],
            "occurrence_count": 0,
            "witnesses": [],
        })
        if entry["first_rule"] != row["first_rule"]:
            raise AssertionError(("R50G25A_SAME_STATE_FIRST_RULE_DRIFT", entry["first_rule"], row["first_rule"]))
        entry["occurrence_count"] += 1
        if len(entry["witnesses"]) < 3:
            entry["witnesses"].append({
                "spec": row["spec"],
                "source_hash": row["source_hash"],
                "first_clause": row["first_clause"],
                "second_clause": row["second_clause"],
            })

    cover_unique = Counter()
    cover_weighted = Counter()
    first_rule_unique = Counter()
    first_rule_weighted = Counter()
    requirement_hist_unique = Counter()
    bce_hist_unique = Counter()
    bve_hist_unique = Counter()
    profiles = []

    for key, entry in sorted(unique.items(), key=lambda kv: (kv[1]["forced_CLV"], kv[0])):
        profile = coverage_profile(entry["forced_formula"])
        count = int(entry["occurrence_count"])
        cls = profile["cover_class"]
        cover_unique[cls] += 1
        cover_weighted[cls] += count
        first_rule_unique[entry["first_rule"]] += 1
        first_rule_weighted[entry["first_rule"]] += count
        requirement_hist_unique[profile["requirement_count"]] += 1
        bce_hist_unique[profile["BCE_candidate_count"]] += 1
        bve_hist_unique[profile["BVE_candidate_count"]] += 1
        profiles.append({
            "state_hash": r50g24.r50g23.r50g4.fhash(entry["forced_formula"]),
            "forced_CLV": entry["forced_CLV"],
            "first_rule": entry["first_rule"],
            "occurrence_count": count,
            "witnesses": entry["witnesses"],
            "debt_profile": profile,
        })

    if sum(cover_weighted.values()) != EXPECTED_TARGET_OCCURRENCES:
        raise AssertionError(("R50G25A_WEIGHTED_COVER_SUM_DRIFT", dict(cover_weighted)))

    ge3_weighted = cover_weighted["AT_LEAST_THREE_BINARY_CLAUSES_NEEDED_FOR_SNAPSHOT_INCIDENCE_COVER"]
    le2_weighted = (
        cover_weighted["ONE_BINARY_CLAUSE_CAN_PAY_ALL_NECESSARY_INCIDENCES"]
        + cover_weighted["TWO_BINARY_CLAUSES_CAN_PAY_ALL_NECESSARY_INCIDENCES"]
    )

    if ge3_weighted > 0:
        next_gate = "R50G25B_SOURCE_REALIZABILITY_OF_MINIMUM_JOINT_DEBT"
    else:
        next_gate = "R50G25B_DYNAMIC_REPLACEMENT_ESCAPE_AFTER_STATIC_DEBT_COVER"

    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "parent_pair_trial_count": parent["pair_trial_count"],
        "target_occurrence_count": len(occurrences),
        "unique_post_DP_state_count": len(unique),
        "target_first_rules": sorted(TARGET_FIRST_RULES),
        "first_rule_occurrence_partition": dict(sorted(first_rule_weighted.items())),
        "first_rule_unique_state_partition": dict(sorted(first_rule_unique.items())),
        "snapshot_binary_incidence_cover_weighted_partition": dict(sorted(cover_weighted.items())),
        "snapshot_binary_incidence_cover_unique_partition": dict(sorted(cover_unique.items())),
        "weighted_occurrences_requiring_at_least_three_binary_incidences": ge3_weighted,
        "weighted_occurrences_coverable_by_at_most_two_binary_incidences": le2_weighted,
        "unique_requirement_count_histogram": {str(k): v for k, v in sorted(requirement_hist_unique.items())},
        "unique_BCE_candidate_count_histogram": {str(k): v for k, v in sorted(bce_hist_unique.items())},
        "unique_BVE_candidate_count_histogram": {str(k): v for k, v in sorted(bve_hist_unique.items())},
        "state_profiles": profiles,
        "next_gate": next_gate,
        "interpretation_contract": {
            "snapshot_cover_is_necessary_not_sufficient": True,
            "post_DP_cover_is_source_reachability_proof": False,
            "covering_existing_BVE_incidence_debt_guarantees_BVE_disabled": False,
            "covering_existing_BCE_support_debt_guarantees_no_new_BCE": False,
            "static_debt_cover_closes_dynamic_replacement_cycle": False,
        },
        "firewall": {
            "R50G25A_PROVES_THREE_CLAUSES_SUFFICIENT": False,
            "R50G25A_PROVES_THREE_CLAUSES_NECESSARY_UNIVERSALLY": False,
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
