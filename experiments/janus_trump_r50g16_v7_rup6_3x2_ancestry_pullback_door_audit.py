from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g15_rup6_hub_bve_blockade_saturation as r50g15

GATE = "JANUS_TRUMP_R50G16_V7_RUP6_3X2_ANCESTRY_PULLBACK_AND_DOOR_AUDIT"
PIVOT = 1
HUB = 7
WIDE6 = r33.canonical_clause((2, 3, 4, 5, 6, 7))
FINAL5 = r33.canonical_clause((2, 3, 4, 5, 6))
EXPECTED_AFTER_VARS = {2, 3, 4, 5, 6, 7}

MANDATORY = (
    (1, 2, 3, 4),
    (-1, 5, 6, 7),
    (-5, 6, 7),
    (-4, 5, 7),
    (2, -7),
    (3, -7),
)
NEG2 = (
    (-2, 4), (-2, 5), (-2, 6),
    (-2, 4, 5), (-2, 4, 6), (-2, 5, 6),
)
NEG3 = (
    (-3, 4), (-3, 5), (-3, 6),
    (-3, 4, 5), (-3, 4, 6), (-3, 5, 6),
)
NEG6 = (
    (-6, 2), (-6, 3), (-6, 4), (-6, 5),
    (-6, 2, 4), (-6, 3, 4), (-6, 4, 5),
)
BLOCKERS = (
    None,
    (-2, -3, 4), (-2, -3, 5), (-2, -3, 6),
    (-2, 4, -6), (-3, 4, -6), (-2, 5, -6), (-3, 5, -6),
    (2, -4, -6), (3, -4, -6), (2, -5, -6), (3, -5, -6),
)


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def candidate_sources():
    for a in NEG2:
        for b in NEG3:
            for c in NEG6:
                for d in BLOCKERS:
                    clauses = list(MANDATORY) + [a, b, c]
                    if d is not None:
                        clauses.append(d)
                    yield canon(clauses), {
                        "neg2": list(a),
                        "neg3": list(b),
                        "neg6": list(c),
                        "blocker": None if d is None else list(d),
                    }


def exact_local_realizer_audit(source):
    f = canon(source)
    if set(r33.variables(f)) != set(range(1, 8)):
        return False, "NOT_EXACT_V7", None
    if max_width(f) > 4:
        return False, "SOURCE_WIDTH_GT4", None
    if not r50g10.exact_pre_bve_clean(f):
        return False, "NOT_PRE_BVE_CLEAN", None

    direct = r50g4.first_r33_micro_candidate(f)
    if direct["kind"] != "PROPOSAL" or direct.get("rule") != "BOUNDED_VARIABLE_ELIMINATION":
        return False, "FIRST_R33_NOT_BVE", {"direct": direct}
    if int(direct.get("var", -1)) != PIVOT:
        return False, "FIRST_BVE_NOT_PIVOT1", {"direct": direct}
    if max_width(direct["after"]) <= 4:
        return False, "PIVOT1_BVE_DOES_NOT_ESCAPE_W4", {"direct": direct}

    dp = r45a.exact_dp_record(f, PIVOT)
    if dp is None:
        return False, "NO_EXACT_DP_RECORD", None
    full_resolvents = {r33.canonical_clause(c) for c in dp["full_non_tautological_resolvents"]}
    if WIDE6 not in full_resolvents:
        return False, "CANONICAL_WIDE6_NOT_GENERATED", {"dp": dp}
    forced = canon(dp["transformed"])
    if WIDE6 not in forced:
        return False, "CANONICAL_WIDE6_SUBSUMED_BEFORE_NORMALIZATION", {"forced": [list(c) for c in forced]}

    reduced = r33.simplify(forced)
    after_r33 = canon(reduced["final_formula"])
    if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
        return False, "POST_DP_R33_TERMINAL", {"terminal": reduced["terminal"], "history": reduced["history"]}
    if set(r33.variables(after_r33)) != EXPECTED_AFTER_VARS:
        return False, "POST_DP_VARIABLE_ELIMINATION", {
            "vars": list(r33.variables(after_r33)),
            "history": reduced["history"],
        }
    if WIDE6 not in after_r33:
        return False, "WIDE6_LOST_BEFORE_RUP", {"history": reduced["history"]}

    ledger = r50g15.exact_hub_bve_ledger(after_r33, HUB)
    if ledger["positive_count"] < 3 or ledger["negative_count"] < 2:
        return False, "HUB_NOT_3x2_SATURATED", {"ledger": ledger}
    if ledger["bve_accepted_for_hub"]:
        return False, "HUB_BVE_NOT_BLOCKED", {"ledger": ledger}

    rup = r35b.run_candidate(after_r33)
    replay = r35b.independent_certificate_replay(after_r33, rup)
    if not replay["pass"]:
        raise AssertionError(("R50G16_RUP_INDEPENDENT_REPLAY_FAIL", replay))
    hit = None
    for row in rup["history"]:
        if (
            r33.canonical_clause(row["source_clause"]) == WIDE6
            and int(row["removed_literal"]) == HUB
            and r33.canonical_clause(row["strengthened_clause"]) == FINAL5
        ):
            hit = row
            break
    if hit is None:
        return False, "NO_CERTIFIED_RUP6_DROP_HUB_IN_HISTORY", {
            "RUP_status": rup["status"],
            "RUP_history": rup["history"],
            "ledger": ledger,
        }

    return True, "REALIZER", {
        "source": [list(c) for c in f],
        "source_hash": r50g4.fhash(f),
        "source_CLV": list(r33.measure(f)),
        "first_R33": {
            "rule": direct["rule"],
            "pivot": int(direct["var"]),
            "proposal_max_width": max_width(direct["after"]),
        },
        "exact_DP": {
            "forced_hash": dp.get("transformed_formula_hash"),
            "forced_CLV": dp["measure_after_forced_DP"],
            "canonical_wide6_generated": True,
            "independent_replay_pass": bool(r45a.independent_dp_replay(f, dp)["pass"]),
        },
        "post_DP_R33": {
            "history": reduced["history"],
            "final_hash": r50g4.fhash(after_r33),
            "final_CLV": list(r33.measure(after_r33)),
            "variables": list(r33.variables(after_r33)),
        },
        "hub_ledger": ledger,
        "RUP": {
            "status": rup["status"],
            "successful_strengthenings": int(rup["successful_strengthenings"]),
            "drop_hub_record": hit,
            "independent_replay_pass": True,
        },
    }


def search_frozen_family():
    counts = Counter()
    tested = 0
    first = None
    first_spec = None
    for source, spec in candidate_sources():
        tested += 1
        ok, reason, detail = exact_local_realizer_audit(source)
        counts[reason] += 1
        if ok:
            first = detail
            first_spec = spec
            break
    return {
        "tested_until_first_realizer_or_exhaustion": tested,
        "full_family_size": len(NEG2) * len(NEG3) * len(NEG6) * len(BLOCKERS),
        "rejection_histogram_before_first": dict(sorted(counts.items())),
        "first_realizer": first,
        "first_realizer_spec": first_spec,
    }


def door_audit(realizer):
    if realizer is None:
        return None
    f = canon(realizer["source"])
    same = r50g10.exact_door_row(f, PIVOT)
    alternate = r50g10.profile_all_alternate_doors(f, PIVOT)
    same_unsafe = not bool(same["r47j_safe"])
    all_alt_closed = bool(alternate["all_alternate_doors_closed"])
    all_doors_closed = same_unsafe and all_alt_closed
    return {
        "same_pivot": same,
        "same_pivot_unsafe": same_unsafe,
        "alternate": alternate,
        "all_doors_closed": all_doors_closed,
    }


def run():
    search = search_frozen_family()
    doors = door_audit(search["first_realizer"])

    if search["first_realizer"] is None:
        verdict = "NO_REALIZER_IN_FROZEN_CANONICAL_AUGMENTATION_FAMILY__UNIVERSAL_STATUS_OPEN"
    elif doors["all_doors_closed"]:
        verdict = "EXPLICIT_V7_ALL_DOORS_CLOSED_COUNTEREXAMPLE_FOUND_IN_FROZEN_FAMILY"
    elif not doors["same_pivot_unsafe"]:
        verdict = "EXPLICIT_V7_RUP6_3x2_ANCESTRY_REALIZER_FOUND__SAME_PIVOT_R47J_SAFE"
    else:
        verdict = "EXPLICIT_V7_RUP6_3x2_ANCESTRY_REALIZER_FOUND__CERTIFIED_ALTERNATE_DOOR_EXISTS"

    return {
        "gate": GATE,
        "mode": "FROZEN_DETERMINISTIC_CANONICAL_PULLBACK_FAMILY_PLUS_EXACT_DOOR_AUDIT",
        "source_level_facts_used": [
            "R50G15_RUP6_HUB_BLOCKADE_REQUIRES_3x2_OR_STRONGER_SATURATION",
            "EXACT_DP_INTRODUCES_NO_FRESH_VARIABLES",
            "R50G14_V7_UNSAFE_TRACE_CANNOT_LOSE_AN_ADDITIONAL_VARIABLE",
            "R49H_OPEN_IFF_CHI_STAR_LE_4_FOR_BIPOLAR_PIVOT",
            "R47J_SAFE_IFF_TERMINAL_OR_FINAL_WIDTH_LE_4"
        ],
        "frozen_family_search": search,
        "door_audit": doors,
        "critical_next_obligation": (
            "IF_REALIZER_HAS_OPEN_DOOR__ISOLATE_WHICH_ANCESTRY_OR_SATURATION_FEATURE_FORCES_THAT_DOOR_UNIVERSALLY;_IF_NO_REALIZER__DO_NOT_PROMOTE_NO_FIND_AND_ATTACK_THE_FIRST_DOMINANT_REJECTION_SYMBOLICALLY;_IF_ALL_DOORS_CLOSED__PIVOT_TO_REACHABILITY_OR_REFUTE_THE_REACHABLE_THEOREM_IF_REACHABILITY_IS_CERTIFIED"
        ),
        "verdict": verdict,
        "firewall": {
            "FINITE_FAMILY_NO_FIND_IMPLIES_UNIVERSAL_IMPOSSIBILITY": False,
            "FINITE_REALIZER_WITH_OPEN_DOOR_IMPLIES_UNIVERSAL_ALTERNATE_DOOR": False,
            "RUP_BEARING_V7_HUB_CYCLE_ELIMINATED": False,
            "V7_IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
