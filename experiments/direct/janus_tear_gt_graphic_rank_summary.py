#!/usr/bin/env python3
"""Compact summary for the C024 branch and Resolution graphic-rank audits."""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_graphic_rank_branch_audit import audit as branch_audit
from janus_tear_gt_resolution_graphic_rank_audit import audit as resolution_audit


def selected(counts, names):
    table = dict(counts)
    return tuple((name, table.get(name, 0)) for name in names)


def self_test() -> None:
    branch_rows = []
    resolution_rows = []
    branch_total: Counter[str] = Counter()
    resolution_total: Counter[str] = Counter()
    maximum_loss_from_min = 0
    maximum_loss_from_max = 0

    for n in range(4, 9):
        branch = branch_audit(n)
        resolution = resolution_audit(n)
        branch_total.update(dict(branch["counts"]))
        resolution_total.update(dict(resolution["counts"]))
        maximum_loss_from_min = max(
            maximum_loss_from_min, resolution["maximum_loss_from_min"]
        )
        maximum_loss_from_max = max(
            maximum_loss_from_max, resolution["maximum_loss_from_max"]
        )

        branch_rows.append(
            {
                "n": n,
                "target": branch["target"],
                "minimum_psi_change": branch["minimum_psi_change"],
                "counts": selected(
                    branch["counts"],
                    (
                        "branch_edges",
                        "clause_transitions",
                        "strict_width_decreases",
                        "novel_width_decreases",
                        "nonnovel_width_decreases",
                        "rank_decreases",
                        "novel_rank_decreases",
                        "nonnovel_rank_decreases",
                    ),
                ),
                "nonnovel_width_drop_rank_loss": branch[
                    "nonnovel_width_drop_rank_loss"
                ],
                "violation_count": branch["violation_count"],
            }
        )
        resolution_rows.append(
            {
                "n": n,
                "target": resolution["target"],
                "counts": selected(
                    resolution["counts"],
                    (
                        "resolution_events",
                        "pre_frontier_resolution_events",
                        "rank_loss_below_both_parents",
                        "rank_loss_below_larger_parent",
                        "spanning_tree_resolvents",
                        "dangerous_origins",
                        "direct_cross_component_units",
                    ),
                ),
                "maximum_loss_from_min": resolution[
                    "maximum_loss_from_min"
                ],
                "maximum_loss_from_max": resolution[
                    "maximum_loss_from_max"
                ],
                "dangerous_score_histogram": resolution[
                    "dangerous_score_histogram"
                ],
                "direct_unit_novelty_histogram": resolution[
                    "direct_unit_novelty_histogram"
                ],
            }
        )

    assert all(row["minimum_psi_change"] >= 0 for row in branch_rows)
    assert all(row["violation_count"] == 0 for row in branch_rows)
    assert maximum_loss_from_max <= 1

    print("JANUS_GT_GRAPHIC_RANK_SUMMARY = PASS")
    print(f"branch_rows = {tuple(branch_rows)}")
    print(f"resolution_rows = {tuple(resolution_rows)}")
    print(
        "branch_aggregate = "
        f"{selected(tuple(branch_total.items()), ('branch_edges','clause_transitions','strict_width_decreases','novel_width_decreases','nonnovel_width_decreases','rank_decreases','novel_rank_decreases','nonnovel_rank_decreases'))}"
    )
    print(
        "resolution_aggregate = "
        f"{selected(tuple(resolution_total.items()), ('resolution_events','pre_frontier_resolution_events','rank_loss_below_both_parents','rank_loss_below_larger_parent','spanning_tree_resolvents','dangerous_origins','direct_cross_component_units'))}"
    )
    print(f"maximum_loss_from_min = {maximum_loss_from_min}")
    print(f"maximum_loss_from_max = {maximum_loss_from_max}")
    print("branch_theorem = novelty plus graphic rank is nondecreasing")
    print("resolution_theorem = one inference loses at most one rank unit relative to the larger-rank parent")
    print("claim_boundary = compact finite audit summary; cumulative asymptotic proof charge remains open")


if __name__ == "__main__":
    self_test()
