#!/usr/bin/env python3
"""Compact finite certificate for the C024 pairwise bridge invariant.

This certificate intentionally does not assert the false single-clause claim
that every component-spanning bridge is tail-singleton.  It verifies the exact
pairwise statement observed in every pre-frontier Policy-0A residual key through
GT_8:

- every complementary double-bridge pair is tail/tail;
- therefore the two bridge cuts differ;
- every non-tail bridge has only non-bridge component-spanning complements.

The graph implication from tail/tail to different cuts is proved separately in
`proof_attempts/C024/GT_CORESOLVABLE_TAIL_BRIDGE_INVARIANT.md`.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bridge_endpoint_profile import audit as endpoint_audit
from janus_tear_gt_non_tail_bridge_blockers import audit as blocker_audit


EXPECTED_DOUBLE_BRIDGE = {4: 11, 5: 23, 6: 56, 7: 260, 8: 261}
EXPECTED_NON_TAIL = {4: 1, 5: 4, 6: 8, 7: 21, 8: 28}


def self_test() -> None:
    aggregate_endpoint: Counter[str] = Counter()
    aggregate_blocker: Counter[str] = Counter()
    rows = []

    for n in range(4, 9):
        endpoint = endpoint_audit(n)
        blocker = blocker_audit(n)

        endpoint_counts = dict(endpoint["counts"])
        endpoint_roles = dict(endpoint["bridge_roles"])
        pair_roles = dict(endpoint["pair_roles"])
        blocker_counts = dict(blocker["counts"])

        assert endpoint_counts.get("double_bridge_pairs", 0) == EXPECTED_DOUBLE_BRIDGE[n]
        assert endpoint_counts.get("different_cut_pairs", 0) == EXPECTED_DOUBLE_BRIDGE[n]
        assert endpoint_counts.get("same_cut_pairs", 0) == 0
        assert pair_roles == {("TAIL_SINGLETON", "TAIL_SINGLETON"): EXPECTED_DOUBLE_BRIDGE[n]}

        non_tail = (
            endpoint_roles.get("HEAD_SINGLETON", 0)
            + endpoint_roles.get("NON_SINGLETON_CUT", 0)
        )
        assert non_tail == EXPECTED_NON_TAIL[n]
        assert blocker_counts.get("non_tail_bridge_occurrences", 0) == EXPECTED_NON_TAIL[n]
        assert blocker_counts.get("COMPLEMENT_SPANNING_NONBRIDGE", 0) == EXPECTED_NON_TAIL[n]
        assert blocker_counts.get("COMPLEMENT_SPANNING_BRIDGE", 0) == 0
        assert blocker_counts.get("COMPLEMENT_ABSENT", 0) == 0
        assert blocker_counts.get("COMPLEMENT_ONLY_NONSPANNING", 0) == 0

        aggregate_endpoint.update(endpoint_counts)
        aggregate_blocker.update(blocker_counts)
        rows.append({
            "n": n,
            "spanning_clause_occurrences": endpoint_counts["spanning_clause_occurrences"],
            "spanning_bridge_literals": endpoint_counts["spanning_bridge_literals"],
            "non_tail_bridges": non_tail,
            "double_bridge_pairs": endpoint_counts["double_bridge_pairs"],
            "same_cut_pairs": endpoint_counts.get("same_cut_pairs", 0),
            "non_tail_with_spanning_bridge_complement": blocker_counts.get(
                "COMPLEMENT_SPANNING_BRIDGE", 0
            ),
        })

    assert aggregate_endpoint["spanning_clause_occurrences"] == 7918
    assert aggregate_endpoint["spanning_bridge_literals"] == 2828
    assert aggregate_endpoint["double_bridge_pairs"] == 611
    assert aggregate_endpoint["different_cut_pairs"] == 611
    assert aggregate_endpoint["same_cut_pairs"] == 0
    assert aggregate_blocker["non_tail_bridge_occurrences"] == 62
    assert aggregate_blocker["COMPLEMENT_SPANNING_NONBRIDGE"] == 62
    assert aggregate_blocker["COMPLEMENT_SPANNING_BRIDGE"] == 0

    print("JANUS_GT_CORESOLVABLE_TAIL_BRIDGE_CERTIFICATE = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(
        "AGGREGATE = "
        + repr({
            "spanning_clause_occurrences": 7918,
            "spanning_bridge_literals": 2828,
            "non_tail_bridge_occurrences": 62,
            "double_bridge_pairs": 611,
            "tail_tail_pairs": 611,
            "different_cut_pairs": 611,
            "same_cut_pairs": 0,
            "non_tail_with_spanning_bridge_complement": 0,
        })
    )
    print(
        "claim_boundary = exhaustive finite certificate through GT_8; "
        "arbitrary-n pairwise induction remains open"
    )


if __name__ == "__main__":
    self_test()
