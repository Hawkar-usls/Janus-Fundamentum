#!/usr/bin/env python3
"""Verify graphic-rank branch monotonicity on every Policy-0A GT clause edge.

Width is not a valid universal potential: GT_8 contains hundreds of nonnovel
width decreases.  This audit replaces width by the graphic rank of the clause's
external-literal multigraph on current Hasse components.

For every actual pre-frontier branch edge and every parent post-propagation
clause not satisfied by that branch, it checks

    rho_after >= rho_before - novelty_increment

and therefore

    novelty_after + rho_after >= novelty_before + rho_before.

The checker includes unchanged clauses, width-decreasing clauses, cycle-edge
removals and internal-loop removals.  It separately confirms that the 612 known
nonnovel width decreases have zero graphic-rank loss.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    DSU,
    clause_component_graph,
    execution_context,
)

Clause = tuple[int, ...]


def graphic_rank(graph: dict[str, object]) -> int:
    component_count = int(graph["component_count"])
    dsu = DSU(component_count)
    for left, right, _literal in graph["external_edges"]:
        dsu.union(int(left), int(right))
    connected_components = len(
        {dsu.find(component) for component in range(component_count)}
    )
    return component_count - connected_components


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    rank_transition_histogram: Counter[tuple[int, int, int]] = Counter()
    psi_change_histogram: Counter[int] = Counter()
    width_change_histogram: Counter[int] = Counter()
    graph_class_histogram: Counter[str] = Counter()
    nonnovel_width_drop_rank_loss: Counter[int] = Counter()
    minimum_psi_change = 10**9
    violations = []
    nonnovel_examples = []
    novel_rank_drop_examples = []

    for state in policy.states.values():
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            continue
        parent_call = int(state["entry_call"])
        parent_novelty = int(levels[parent_call])
        if parent_novelty >= target:
            continue

        before_assignment = context["state_after_post"][int(state["id"])]
        parent_cnf = tuple(state["post_result"])

        for child in state["children"]:
            if child["call"] is None:
                continue
            child_call = int(child["call"])
            branch_literal = int(child["literal"])
            child_novelty = int(levels[child_call])
            delta = child_novelty - parent_novelty
            assert delta in (0, 1)

            branch_assignment = {abs(branch_literal): branch_literal > 0}
            after_assignment = dict(before_assignment)
            after_assignment[abs(branch_literal)] = branch_literal > 0

            counts["branch_edges"] += 1
            counts["novel_branch_edges" if delta else "nonnovel_branch_edges"] += 1

            for clause in parent_cnf:
                residual = reduce_clause(clause, branch_assignment)
                if residual is None:
                    counts["satisfied_clause_transitions"] += 1
                    continue

                before_graph = clause_component_graph(
                    n, clause, before_assignment, pairs
                )
                after_graph = clause_component_graph(
                    n, residual, after_assignment, pairs
                )
                rho_before = graphic_rank(before_graph)
                rho_after = graphic_rank(after_graph)
                psi_before = parent_novelty + rho_before
                psi_after = child_novelty + rho_after
                psi_change = psi_after - psi_before
                width_change = len(residual) - len(clause)

                counts["clause_transitions"] += 1
                graph_class_histogram[str(before_graph["classification"])] += 1
                rank_transition_histogram[(delta, rho_before, rho_after)] += 1
                psi_change_histogram[psi_change] += 1
                width_change_histogram[width_change] += 1
                minimum_psi_change = min(minimum_psi_change, psi_change)

                if len(residual) < len(clause):
                    counts["strict_width_decreases"] += 1
                    if delta:
                        counts["novel_width_decreases"] += 1
                    else:
                        counts["nonnovel_width_decreases"] += 1
                        rank_loss = rho_before - rho_after
                        nonnovel_width_drop_rank_loss[rank_loss] += 1
                        if len(nonnovel_examples) < 12:
                            nonnovel_examples.append(
                                {
                                    "parent_call": parent_call,
                                    "child_call": child_call,
                                    "branch_literal": branch_literal,
                                    "clause": clause,
                                    "residual": residual,
                                    "rho_before": rho_before,
                                    "rho_after": rho_after,
                                    "psi_change": psi_change,
                                    "classification": before_graph["classification"],
                                }
                            )

                if rho_after < rho_before:
                    counts["rank_decreases"] += 1
                    counts[
                        "novel_rank_decreases" if delta else "nonnovel_rank_decreases"
                    ] += 1
                    if delta and len(novel_rank_drop_examples) < 12:
                        novel_rank_drop_examples.append(
                            {
                                "parent_call": parent_call,
                                "child_call": child_call,
                                "branch_literal": branch_literal,
                                "clause": clause,
                                "residual": residual,
                                "rho_before": rho_before,
                                "rho_after": rho_after,
                                "psi_change": psi_change,
                            }
                        )

                if rho_after < rho_before - delta or psi_change < 0:
                    violations.append(
                        {
                            "parent_call": parent_call,
                            "child_call": child_call,
                            "parent_novelty": parent_novelty,
                            "child_novelty": child_novelty,
                            "branch_literal": branch_literal,
                            "clause": clause,
                            "residual": residual,
                            "rho_before": rho_before,
                            "rho_after": rho_after,
                            "psi_before": psi_before,
                            "psi_after": psi_after,
                            "before_graph": before_graph,
                            "after_graph": after_graph,
                        }
                    )

            if child["result"]:
                break

    assert not violations
    assert counts["nonnovel_rank_decreases"] == 0
    assert set(nonnovel_width_drop_rank_loss).issubset({0})

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "minimum_psi_change": 0 if minimum_psi_change == 10**9 else minimum_psi_change,
        "rank_transition_histogram": tuple(sorted(rank_transition_histogram.items())),
        "psi_change_histogram": tuple(sorted(psi_change_histogram.items())),
        "width_change_histogram": tuple(sorted(width_change_histogram.items())),
        "graph_class_histogram": tuple(sorted(graph_class_histogram.items())),
        "nonnovel_width_drop_rank_loss": tuple(sorted(nonnovel_width_drop_rank_loss.items())),
        "violation_count": len(violations),
        "nonnovel_examples": tuple(nonnovel_examples),
        "novel_rank_drop_examples": tuple(novel_rank_drop_examples),
    }


def self_test() -> None:
    rows = []
    aggregate: Counter[str] = Counter()
    aggregate_psi: Counter[int] = Counter()
    aggregate_nonnovel_rank_loss: Counter[int] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate.update(dict(data["counts"]))
        aggregate_psi.update(dict(data["psi_change_histogram"]))
        aggregate_nonnovel_rank_loss.update(
            dict(data["nonnovel_width_drop_rank_loss"])
        )
        rows.append(
            (
                n,
                data["target"],
                data["minimum_psi_change"],
                data["counts"],
                data["nonnovel_width_drop_rank_loss"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  minimum_psi_change = {data['minimum_psi_change']}")
        print(f"  rank_transition_histogram = {data['rank_transition_histogram']}")
        print(f"  psi_change_histogram = {data['psi_change_histogram']}")
        print(f"  width_change_histogram = {data['width_change_histogram']}")
        print(f"  graph_class_histogram = {data['graph_class_histogram']}")
        print(
            "  nonnovel_width_drop_rank_loss = "
            f"{data['nonnovel_width_drop_rank_loss']}"
        )
        print(f"  violation_count = {data['violation_count']}")
        print(f"  nonnovel_examples = {data['nonnovel_examples']}")
        print(f"  novel_rank_drop_examples = {data['novel_rank_drop_examples']}")

    print("JANUS_GT_GRAPHIC_RANK_BRANCH_AUDIT = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_counts = {tuple(sorted(aggregate.items()))}")
    print(f"aggregate_psi_change = {tuple(sorted(aggregate_psi.items()))}")
    print(
        "aggregate_nonnovel_width_drop_rank_loss = "
        f"{tuple(sorted(aggregate_nonnovel_rank_loss.items()))}"
    )
    print("finite_result = graphic-rank potential is nondecreasing on every audited pre-frontier clause branch transition")
    print("claim_boundary = finite execution audit plus separate combinatorial branch lemma; local-Resolution rank generation remains open")


if __name__ == "__main__":
    self_test()
