from __future__ import annotations

import json

import janus_trump_r50g25a_bce_bve_joint_debt_hypergraph as full

FIELDS = (
    "gate",
    "parent_gate",
    "parent_pair_trial_count",
    "target_occurrence_count",
    "unique_post_DP_state_count",
    "target_first_rules",
    "first_rule_occurrence_partition",
    "first_rule_unique_state_partition",
    "snapshot_binary_incidence_cover_weighted_partition",
    "snapshot_binary_incidence_cover_unique_partition",
    "weighted_occurrences_requiring_at_least_three_binary_incidences",
    "weighted_occurrences_coverable_by_at_most_two_binary_incidences",
    "unique_requirement_count_histogram",
    "unique_BCE_candidate_count_histogram",
    "unique_BVE_candidate_count_histogram",
    "next_gate",
    "interpretation_contract",
    "firewall",
)


def run():
    out = full.run()
    compact = {key: out[key] for key in FIELDS}
    compact["proof_claim"] = False
    compact["p_vs_np"] = "OPEN"
    compact["sat_in_p"] = "NOT_PROVED"
    return compact


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
