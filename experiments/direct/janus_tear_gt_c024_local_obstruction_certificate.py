#!/usr/bin/env python3
"""Unified finite certificate for the C024 local-Resolution obstruction.

This executable recomputes the decisive C024 layers for GT_4,...,GT_8:

1. all frozen parent pairs contain no unsafe acyclic low-rank resolvent;
2. every complementary double-bridge pair is tail/tail with different cuts;
3. every parent-eligible exact-key non-tail bridge has an untouched canonical
   root non-minimality shield;
4. all immediate-local surviving lineages avoid the tail under the exact
   lexicographic Policy-0A branch selector;
5. every raw merged-tail lineage is extinct before a later bad exact key—17 by
   causal post-unit contradiction and one GT_4 case by recursive extinction.

This is an exhaustive finite certificate only.  It does not prove the two
arbitrary-n temporal lemmas or the global cache-frontier counting theorem.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_resolvent_survival_filter import audit as survival_audit
from janus_tear_gt_bridge_endpoint_profile import audit as endpoint_audit
from janus_tear_gt_frozen_parent_unsafe_pair_search import audit as frozen_audit
from janus_tear_gt_merged_tail_extinction_provenance import audit as extinction_audit
from janus_tear_gt_non_tail_bridge_blockers import audit as blocker_audit
from janus_tear_gt_root_nonminimality_bridge_shield import audit as root_shield_audit
from janus_tear_gt_surviving_bad_branch_geometry import audit as branch_geometry_audit
from janus_tear_gt_surviving_branch_frequency_profile import audit as frequency_audit


def self_test() -> None:
    frozen_counts: Counter[str] = Counter()
    endpoint_counts: Counter[str] = Counter()
    endpoint_roles: Counter[str] = Counter()
    endpoint_pair_roles: Counter[tuple[str, str]] = Counter()
    blocker_counts: Counter[str] = Counter()
    root_counts: Counter[str] = Counter()
    root_head_sizes: Counter[int] = Counter()
    root_parallel: Counter[int] = Counter()
    survival_counts: Counter[str] = Counter()
    survival_event_shapes: Counter[tuple[int, int]] = Counter()
    survival_child_shapes: Counter[tuple[int, int]] = Counter()
    branch_counts: Counter[str] = Counter()
    branch_relations: Counter[str] = Counter()
    frequency_counts: Counter[str] = Counter()
    frequency_relations: Counter[str] = Counter()
    frequency_tail_gaps: Counter[int] = Counter()
    extinction_counts: Counter[str] = Counter()
    extinction_conflicts: Counter[str] = Counter()
    extinction_children: Counter[str] = Counter()
    rows = []

    for n in range(4, 9):
        frozen = frozen_audit(n)
        endpoint = endpoint_audit(n)
        blocker = blocker_audit(n)
        root = root_shield_audit(n)
        survival = survival_audit(n)
        branch = branch_geometry_audit(n)
        frequency = frequency_audit(n)
        extinction = extinction_audit(n)

        frozen_counts.update(dict(frozen["counts"]))
        endpoint_counts.update(dict(endpoint["counts"]))
        endpoint_roles.update(dict(endpoint["bridge_roles"]))
        endpoint_pair_roles.update(dict(endpoint["pair_roles"]))
        blocker_counts.update(dict(blocker["counts"]))
        root_counts.update(dict(root["counts"]))
        root_head_sizes.update(dict(root["head_component_sizes"]))
        root_parallel.update(dict(root["parallel_multiplicity"]))
        survival_counts.update(dict(survival["counts"]))
        survival_event_shapes.update(dict(survival["event_shapes"]))
        survival_child_shapes.update(dict(survival["child_shapes"]))
        branch_counts.update(dict(branch["counts"]))
        branch_relations.update(dict(branch["relation_histogram"]))
        frequency_counts.update(dict(frequency["counts"]))
        frequency_relations.update(dict(frequency["selected_relation_histogram"]))
        frequency_tail_gaps.update(dict(frequency["tail_gap_histogram"]))
        extinction_counts.update(dict(extinction["counts"]))
        extinction_conflicts.update(dict(extinction["conflict_kinds"]))
        extinction_children.update(dict(extinction["branch_child_outcomes"]))

        rows.append({
            "n": n,
            "frozen_pairs": dict(frozen["counts"]).get("all_frozen_pairs", 0),
            "legal_resolvents": dict(frozen["counts"]).get("legal_nonempty_pairs", 0),
            "unsafe_resolvents": dict(frozen["counts"]).get("unsafe_pairs", 0),
            "double_bridge_pairs": dict(endpoint["counts"]).get("double_bridge_pairs", 0),
            "same_cut_pairs": dict(endpoint["counts"]).get("same_cut_pairs", 0),
            "exact_key_bad": dict(survival["counts"]).get("exact_key_bad_occurrences", 0),
            "immediate_local": dict(survival["counts"]).get("immediate_local_occurrences", 0),
            "inherited": dict(survival["counts"]).get("inherited_only_occurrences", 0),
            "merged_tail_extinctions": dict(extinction["counts"]).get("fresh_merged_tail_occurrences", 0),
        })

    # All frozen parent pairs: no structural shortcut, even beyond stopping.
    assert frozen_counts["states"] == 615
    assert frozen_counts["all_frozen_pairs"] == 591425
    assert frozen_counts["legal_nonempty_pairs"] == 488757
    assert frozen_counts["unsafe_pairs"] == 0
    assert frozen_counts["unsafe_reached"] == 0
    assert frozen_counts["unsafe_after_stop"] == 0

    # Pairwise bridge geometry.
    assert endpoint_counts["spanning_clause_occurrences"] == 7918
    assert endpoint_counts["spanning_bridge_literals"] == 2828
    assert endpoint_roles == Counter({
        "TAIL_SINGLETON": 2766,
        "NON_SINGLETON_CUT": 44,
        "HEAD_SINGLETON": 18,
    })
    assert endpoint_counts["double_bridge_pairs"] == 611
    assert endpoint_counts["different_cut_pairs"] == 611
    assert endpoint_counts["same_cut_pairs"] == 0
    assert endpoint_pair_roles == Counter({
        ("TAIL_SINGLETON", "TAIL_SINGLETON"): 611,
    })

    # Every individual non-tail bridge is blocked by a spanning nonbridge complement.
    assert blocker_counts["non_tail_bridge_occurrences"] == 62
    assert blocker_counts["COMPLEMENT_SPANNING_NONBRIDGE"] == 62
    assert blocker_counts["COMPLEMENT_SPANNING_BRIDGE"] == 0
    assert blocker_counts["COMPLEMENT_ABSENT"] == 0
    assert blocker_counts["COMPLEMENT_ONLY_NONSPANNING"] == 0

    # Canonical untouched root shields at every parent-eligible exact key.
    assert root_counts == Counter({
        "non_tail_bridge_occurrences": 62,
        "canonical_root_shields": 62,
    })
    assert root_head_sizes == Counter({2: 12, 3: 21, 4: 17, 5: 12})
    assert root_parallel == Counter({1: 12, 2: 21, 3: 17, 4: 12})

    # Exact-key survival package.
    assert survival_counts == Counter({
        "exact_key_bad_occurrences": 62,
        "immediate_local_occurrences": 42,
        "inherited_only_occurrences": 20,
    })
    assert survival_event_shapes == Counter({
        (1, 3): 14,
        (1, 1): 12,
        (1, 2): 11,
        (1, 4): 5,
    })
    assert all(tail == 1 for tail, _ in survival_event_shapes)
    assert survival_child_shapes == Counter({
        (1, 3): 21,
        (1, 4): 17,
        (1, 2): 12,
        (1, 5): 12,
    })

    # Intervening branch never merges the bad tail.
    assert branch_counts == Counter({
        "surviving_local_lineages": 42,
        "novel_branches": 42,
        "zero_child_pre_units": 42,
        "branch_avoids_tail": 42,
        "one_literal_branch_restrictions": 42,
        "head_growth_branches": 39,
        "head_stable_disjoint_branches": 3,
    })
    assert branch_relations == Counter({"HEAD_TO_OTHER": 39, "DISJOINT": 3})

    # Exact lexicographic selector: strict gap or minimum-index tie-break.
    assert frequency_counts == Counter({
        "lineages": 42,
        "selected_complement_in_source": 42,
        "strict_tail_frequency_gap": 23,
        "tail_ties_maximum": 19,
        "tail_excluded_by_tie_break": 19,
    })
    assert frequency_relations == Counter({"HEAD_TO_OTHER": 39, "DISJOINT": 3})
    assert frequency_tail_gaps == Counter({0: 19, 1: 5, 2: 5, 3: 1, 7: 4, 8: 5, 15: 3})

    # Raw non-singleton-tail lineages never become later bad exact-key parents.
    assert extinction_counts["fresh_merged_tail_occurrences"] == 18
    assert extinction_counts["post_unit_conflict_occurrences"] == 17
    assert extinction_counts["branch_unsat_occurrences"] == 1
    assert extinction_counts["branch_extinction_without_bad_child"] == 1
    assert extinction_counts["DIRECT_CONFLICT_SOURCE"] == 4
    assert extinction_counts["ANCESTOR_CONFLICT_SOURCE"] == 13
    assert extinction_counts["COLOCATED_NONCAUSAL"] == 0
    assert extinction_conflicts == Counter({
        "EMPTY_ON_UNIT_ASSIGNMENT": 12,
        "OPPOSITE_UNITS": 5,
    })
    assert extinction_children.get("BAD_EXACT_KEY", 0) == 0
    assert extinction_children == Counter({"NO_EXACT_KEY": 2})

    print("JANUS_GT_C024_LOCAL_OBSTRUCTION_CERTIFICATE = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print("FROZEN = " + repr({
        "states": 615,
        "pairs": 591425,
        "legal_nonempty": 488757,
        "unsafe": 0,
    }))
    print("BRIDGES = " + repr({
        "spanning_clause_occurrences": 7918,
        "bridge_literals": 2828,
        "double_bridge_pairs": 611,
        "tail_tail": 611,
        "same_cut": 0,
    }))
    print("ROOT_SHIELDS = " + repr({
        "exact_key_bad": 62,
        "canonical_shields": 62,
    }))
    print("TEMPORAL_HANDOFF = " + repr({
        "immediate_local": 42,
        "inherited": 20,
        "head_growth": 39,
        "already_shielded_disjoint": 3,
        "tail_merges": 0,
        "strict_frequency_gap": 23,
        "index_tie_break": 19,
    }))
    print("MERGED_TAIL_EXTINCTION = " + repr({
        "total": 18,
        "causal_post_unit_conflict": 17,
        "direct_conflict_source": 4,
        "ancestor_conflict_source": 13,
        "colocated_noncausal": 0,
        "gt4_recursive_extinction": 1,
        "later_bad_exact_key": 0,
    }))
    print(
        "claim_boundary = exhaustive finite local-obstruction certificate through GT_8; "
        "arbitrary-n temporal lemmas and global cache-frontier counting remain open"
    )


if __name__ == "__main__":
    self_test()
