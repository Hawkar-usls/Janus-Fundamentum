from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25a_bce_bve_joint_debt_hypergraph as r50g25a

GATE = "JANUS_TRUMP_R50G25B_SOURCE_REALIZABILITY_OF_MINIMUM_JOINT_DEBT"
EXPECTED_PARENT_OCCURRENCES = 1673
EXPECTED_PARENT_UNIQUE_STATES = 1212
EXPECTED_PARENT_GE3_UNIQUE = 991
EXPECTED_PARENT_GE3_WEIGHTED = 1317
PIVOT = 1


def canon(formula):
    return r50g25a.canon(formula)


def incidence_system(formula):
    formula = canon(formula)
    bces = r50g25a.blocked_candidates(formula)
    bves = r50g25a.all_bve_candidates(formula)
    requirements = []
    for idx, row in enumerate(bces):
        requirements.append(("BCE", idx, row))
    for idx, row in enumerate(bves):
        requirements.append(("BVE", idx, row))

    additions = r50g25a.all_binary_additions(formula)
    mask_to_clause = {}
    support = [0] * len(requirements)
    for addition in additions:
        mask = 0
        for i, (kind, _idx, row) in enumerate(requirements):
            hit = False
            if kind == "BCE":
                hit = r50g25a.bce_requirement_hit(row, addition)
            else:
                x = int(row["pivot"])
                hit = x in addition or -x in addition
            if hit:
                mask |= 1 << i
                support[i] += 1
        if mask:
            old = mask_to_clause.get(mask)
            if old is None or tuple(addition) < tuple(old):
                mask_to_clause[mask] = tuple(addition)

    if requirements and any(x == 0 for x in support):
        raise AssertionError(("R50G25B_UNREACHABLE_REQUIREMENT_DRIFT", support))

    # With unit cost per clause, a mask strictly contained in another mask is
    # never needed to minimize static incidence-cover cardinality. Keep only
    # maximal masks, preserving one deterministic clause witness per mask.
    masks = sorted(mask_to_clause, key=lambda m: (-m.bit_count(), m))
    maximal = []
    for mask in masks:
        if any((mask | kept) == kept for kept in maximal):
            continue
        maximal.append(mask)

    entries = [(mask_to_clause[m], m) for m in maximal]
    entries.sort(key=lambda x: (x[0], x[1]))
    return {
        "requirements": requirements,
        "full_mask": (1 << len(requirements)) - 1,
        "entries": entries,
        "raw_addition_count": len(additions),
        "maximal_mask_count": len(entries),
    }


def exact_minimum_cover(formula):
    system = incidence_system(formula)
    full = system["full_mask"]
    if full == 0:
        return {
            "minimum": 0,
            "clauses": [],
            "raw_addition_count": system["raw_addition_count"],
            "maximal_mask_count": system["maximal_mask_count"],
            "requirement_count": 0,
        }

    entries = system["entries"]
    frontier = {0: ()}
    seen_depth = {0: 0}
    max_depth = len(system["requirements"])
    for depth in range(1, max_depth + 1):
        nxt = {}
        for covered, witness in frontier.items():
            for clause, mask in entries:
                merged = covered | mask
                if merged == covered:
                    continue
                candidate = witness + (tuple(clause),)
                if merged == full:
                    return {
                        "minimum": depth,
                        "clauses": [list(c) for c in candidate],
                        "raw_addition_count": system["raw_addition_count"],
                        "maximal_mask_count": system["maximal_mask_count"],
                        "requirement_count": len(system["requirements"]),
                    }
                previous = seen_depth.get(merged)
                if previous is not None and previous <= depth:
                    continue
                seen_depth[merged] = depth
                old = nxt.get(merged)
                if old is None or candidate < old:
                    nxt[merged] = candidate
        frontier = nxt
        if not frontier:
            break
    raise AssertionError("R50G25B_FINITE_INCIDENCE_SYSTEM_HAS_NO_COVER")


def first_r33_label(formula):
    reduced = r50g25a.r50g24.r50g23.r33.simplify(canon(formula))
    history = reduced.get("history", [])
    if history:
        return "R33:" + str(history[0]["rule"]), reduced
    return "R33_TERMINAL:" + str(reduced.get("terminal")), reduced


def rebuild_unique_states():
    parent, occurrences = r50g25a.enumerate_pair_post_dp_states()
    if len(occurrences) != EXPECTED_PARENT_OCCURRENCES:
        raise AssertionError(("R50G25B_PARENT_OCCURRENCE_DRIFT", len(occurrences)))

    unique = {}
    for row in occurrences:
        key = tuple(row["forced_formula"])
        entry = unique.setdefault(key, {
            "forced_formula": row["forced_formula"],
            "forced_CLV": row["forced_CLV"],
            "first_rule": row["first_rule"],
            "occurrence_count": 0,
            "witness": {
                "spec": row["spec"],
                "source_hash": row["source_hash"],
                "first_clause": row["first_clause"],
                "second_clause": row["second_clause"],
            },
        })
        if entry["first_rule"] != row["first_rule"]:
            raise AssertionError(("R50G25B_SAME_STATE_FIRST_RULE_DRIFT", key))
        entry["occurrence_count"] += 1

    if len(unique) != EXPECTED_PARENT_UNIQUE_STATES:
        raise AssertionError(("R50G25B_PARENT_UNIQUE_STATE_DRIFT", len(unique)))
    return parent, unique


def run():
    parent, unique = rebuild_unique_states()
    r50g23 = r50g25a.r50g24.r50g23
    r33 = r50g23.r33
    r47j = r50g23.r47j

    skeletons = r50g23.clean_skeletons_from_frozen_r50g22()
    source_by_hash = {item["source_hash"]: item for item in skeletons}
    if len(source_by_hash) != 30:
        raise AssertionError(("R50G25B_FROZEN_SOURCE_HASH_COUNT_DRIFT", len(source_by_hash)))

    minimum_unique = Counter()
    minimum_weighted = Counter()
    realize_unique = Counter()
    realize_weighted = Counter()
    post_realization_first_unique = Counter()
    post_realization_first_weighted = Counter()
    full_r47j_terminal_unique = Counter()
    full_r47j_terminal_weighted = Counter()
    ge3_unique = 0
    ge3_weighted = 0
    exact_realizable_unique = 0
    exact_realizable_weighted = 0
    examples = []
    failures = []

    for key, entry in sorted(unique.items(), key=lambda kv: (kv[1]["forced_CLV"], kv[0])):
        cover = exact_minimum_cover(entry["forced_formula"])
        minimum = int(cover["minimum"])
        count = int(entry["occurrence_count"])
        minimum_unique[minimum] += 1
        minimum_weighted[minimum] += count
        if minimum < 3:
            continue

        ge3_unique += 1
        ge3_weighted += count
        witness = entry["witness"]
        item = source_by_hash.get(witness["source_hash"])
        if item is None:
            raise AssertionError(("R50G25B_SOURCE_HASH_NOT_IN_FROZEN_30", witness["source_hash"]))

        lifted = [tuple(int(x) for x in clause) for clause in cover["clauses"]]
        c1 = tuple(int(x) for x in witness["first_clause"])
        c2 = tuple(int(x) for x in witness["second_clause"])
        source = canon(item["source"])
        mutated_source = canon(list(source) + [c1, c2] + lifted)
        expected_post_dp = canon(list(entry["forced_formula"]) + lifted)

        dp = r47j.r45a.exact_dp_record(mutated_source, PIVOT)
        if dp is None:
            classification = "EXACT_DP_RECORD_MISSING"
            actual_post_dp = None
            macro = None
        else:
            dp_replay = r47j.r45a.independent_dp_replay(mutated_source, dp)
            if not dp_replay.get("pass"):
                raise AssertionError(("R50G25B_DP_REPLAY_FAIL", witness, cover))
            actual_post_dp = canon(dp["transformed"])
            if actual_post_dp != expected_post_dp:
                classification = "DP_INTERACTION_MISMATCH"
                macro = None
            else:
                macro = r47j.macro_candidate_fixpoint(mutated_source, PIVOT)
                if macro is None:
                    classification = "R47J_CANDIDATE_MISSING_AFTER_EXACT_SOURCE_LIFT"
                else:
                    replay = r47j.independent_fixpoint_macro_replay(mutated_source, macro)
                    if not replay.get("pass"):
                        classification = "R47J_INDEPENDENT_REPLAY_FAIL"
                    else:
                        classification = "EXACT_MINIMUM_COVER_SOURCE_REALIZED"

        realize_unique[classification] += 1
        realize_weighted[classification] += count

        row = {
            "state_hash": r50g23.r50g4.fhash(entry["forced_formula"]),
            "forced_CLV": entry["forced_CLV"],
            "occurrence_count": count,
            "original_first_rule": entry["first_rule"],
            "minimum_static_binary_incidence_cover": minimum,
            "minimum_cover_clauses": cover["clauses"],
            "requirement_count": cover["requirement_count"],
            "source_witness": witness,
            "source_realizability": classification,
        }

        if classification == "EXACT_MINIMUM_COVER_SOURCE_REALIZED":
            exact_realizable_unique += 1
            exact_realizable_weighted += count
            label, reduced = first_r33_label(actual_post_dp)
            post_realization_first_unique[label] += 1
            post_realization_first_weighted[label] += count
            terminal = str(macro["normalization"].get("terminal"))
            full_r47j_terminal_unique[terminal] += 1
            full_r47j_terminal_weighted[terminal] += count
            row.update({
                "realized_post_DP_hash": r50g23.r50g4.fhash(actual_post_dp),
                "realized_post_DP_CLV": list(r33.measure(actual_post_dp)),
                "first_R33_rule_after_realized_cover": label,
                "first_R33_terminal_after_realized_cover": reduced.get("terminal"),
                "full_R47J_terminal": macro["normalization"].get("terminal"),
                "full_R47J_round_count": int(macro["normalization"].get("round_count", 0)),
                "full_R47J_restart_count": int(macro["normalization"].get("restart_count", 0)),
                "R47J_independent_replay_pass": True,
            })
            if len(examples) < 12:
                examples.append(row)
        else:
            if len(failures) < 20:
                if actual_post_dp is not None:
                    row["actual_post_DP_hash"] = r50g23.r50g4.fhash(actual_post_dp)
                    row["expected_post_DP_hash"] = r50g23.r50g4.fhash(expected_post_dp)
                failures.append(row)

    if ge3_unique != EXPECTED_PARENT_GE3_UNIQUE:
        raise AssertionError(("R50G25B_GE3_UNIQUE_DRIFT", ge3_unique))
    if ge3_weighted != EXPECTED_PARENT_GE3_WEIGHTED:
        raise AssertionError(("R50G25B_GE3_WEIGHTED_DRIFT", ge3_weighted))

    all_realized = exact_realizable_unique == ge3_unique
    next_gate = (
        "R50G25C_DYNAMIC_REPLACEMENT_ESCAPE_AFTER_SOURCE_REALIZED_MINIMUM_JOINT_DEBT"
        if all_realized
        else "R50G25C_SOURCE_PREIMAGE_OBSTRUCTION_FORENSICS"
    )

    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "parent_unique_post_DP_states": len(unique),
        "parent_ge3_unique_states": ge3_unique,
        "parent_ge3_weighted_occurrences": ge3_weighted,
        "exact_minimum_cover_unique_histogram": {str(k): v for k, v in sorted(minimum_unique.items())},
        "exact_minimum_cover_weighted_histogram": {str(k): v for k, v in sorted(minimum_weighted.items())},
        "source_realizability_unique_partition": dict(sorted(realize_unique.items())),
        "source_realizability_weighted_partition": dict(sorted(realize_weighted.items())),
        "exact_minimum_source_realizable_unique_count": exact_realizable_unique,
        "exact_minimum_source_realizable_weighted_count": exact_realizable_weighted,
        "all_ge3_minimum_covers_source_realizable": all_realized,
        "first_R33_rule_after_realized_minimum_cover_unique_partition": dict(sorted(post_realization_first_unique.items())),
        "first_R33_rule_after_realized_minimum_cover_weighted_partition": dict(sorted(post_realization_first_weighted.items())),
        "full_R47J_terminal_after_realized_minimum_cover_unique_partition": dict(sorted(full_r47j_terminal_unique.items())),
        "full_R47J_terminal_after_realized_minimum_cover_weighted_partition": dict(sorted(full_r47j_terminal_weighted.items())),
        "examples": examples,
        "source_realizability_failures": failures,
        "next_gate": next_gate,
        "interpretation_contract": {
            "exact_minimum_is_static_incidence_cover_only": True,
            "source_realized_cover_is_dynamic_BCE_BVE_closure_proof": False,
            "source_realized_cover_is_hard_core_proof": False,
            "recorded_post_cover_R33_behavior_is_next_gate_evidence_only": True,
            "minimum_generalizes_outside_sealed_states": False,
        },
        "firewall": {
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
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
