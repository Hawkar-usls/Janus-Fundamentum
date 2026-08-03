#!/usr/bin/env python3
"""Explain why non-tail spanning bridges never form a double-bridge pair.

The bridge endpoint profile found a sharp finite fact through GT_8:
all complementary double-bridge pairs use TAIL_SINGLETON bridges, although a
small number of individual spanning clauses contain HEAD_SINGLETON or
NON_SINGLETON_CUT bridges.

For every such non-tail bridge occurrence this audit classifies all clauses in
the same exact cache key containing the complementary literal:

- COMPLEMENT_ABSENT;
- COMPLEMENT_ONLY_NONSPANNING;
- COMPLEMENT_SPANNING_NONBRIDGE;
- COMPLEMENT_SPANNING_BRIDGE (a falsifier of the tail-pair invariant).

This is a diagnostic census intended to expose the next inductive obstruction.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import orientation_class
from janus_tear_gt_rank_safety_dichotomy import safety_class


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    by_bad_role: Counter[tuple[str, str]] = Counter()
    by_orientation: Counter[tuple[str, str, str]] = Counter()
    complement_class_histogram: Counter[tuple[str, ...]] = Counter()
    examples = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]
        key = tuple(state["key"])
        graphs = {
            clause: clause_component_graph(n, clause, assignment, pairs)
            for clause in key
        }
        classes = {
            clause: str(safety_class(n, clause, assignment, pairs)["classification"])
            for clause in key
        }
        orientations = {
            clause: str(orientation_class(clause, graphs[clause], pairs)["classification"])
            for clause in key
        }

        for clause in key:
            if classes[clause] != "COMPONENT_SPANNING":
                continue
            for literal in clause:
                record = bridge_record(clause, graphs[clause], pairs, int(literal))
                if record is None or record["role"] == "TAIL_SINGLETON":
                    continue

                bad_role = str(record["role"])
                counts["non_tail_bridge_occurrences"] += 1
                complements = [other for other in key if -int(literal) in other]
                categories = []
                complement_details = []
                for other in complements:
                    if classes[other] != "COMPONENT_SPANNING":
                        category = "NONSPANNING"
                        other_bridge = None
                    else:
                        other_bridge = bridge_record(
                            other, graphs[other], pairs, -int(literal)
                        )
                        category = "SPANNING_BRIDGE" if other_bridge is not None else "SPANNING_NONBRIDGE"
                    categories.append(category)
                    complement_details.append({
                        "clause": other,
                        "class": classes[other],
                        "orientation": orientations[other],
                        "category": category,
                        "bridge": other_bridge,
                    })

                if not complements:
                    blocker = "COMPLEMENT_ABSENT"
                elif "SPANNING_BRIDGE" in categories:
                    blocker = "COMPLEMENT_SPANNING_BRIDGE"
                elif "SPANNING_NONBRIDGE" in categories:
                    blocker = "COMPLEMENT_SPANNING_NONBRIDGE"
                else:
                    blocker = "COMPLEMENT_ONLY_NONSPANNING"

                counts[blocker] += 1
                by_bad_role[(bad_role, blocker)] += 1
                by_orientation[(orientations[clause], bad_role, blocker)] += 1
                complement_class_histogram[tuple(sorted(categories))] += 1
                if len(examples) < 80:
                    examples.append({
                        "n": n,
                        "state_id": int(state["id"]),
                        "call_id": call_id,
                        "novelty": novelty,
                        "clause": clause,
                        "orientation": orientations[clause],
                        "literal": int(literal),
                        "bridge": record,
                        "blocker": blocker,
                        "complements": tuple(complement_details),
                    })

    assert counts["COMPLEMENT_SPANNING_BRIDGE"] == 0
    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "by_bad_role": tuple(sorted(by_bad_role.items())),
        "by_orientation": tuple(sorted(by_orientation.items())),
        "complement_class_histogram": tuple(sorted(complement_class_histogram.items(), key=repr)),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_bad: Counter[tuple[str, str]] = Counter()
    aggregate_orientation: Counter[tuple[str, str, str]] = Counter()
    aggregate_complements: Counter[tuple[str, ...]] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_bad.update(dict(data["by_bad_role"]))
        aggregate_orientation.update(dict(data["by_orientation"]))
        aggregate_complements.update(dict(data["complement_class_histogram"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  by_bad_role = {data['by_bad_role']}")
        print(f"  by_orientation = {data['by_orientation']}")
        print(f"  complement_class_histogram = {data['complement_class_histogram']}")
        print(f"  examples = {data['examples']}")

    print("JANUS_GT_NON_TAIL_BRIDGE_BLOCKERS = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_bad_roles = {tuple(sorted(aggregate_bad.items()))}")
    print(f"aggregate_orientation = {tuple(sorted(aggregate_orientation.items()))}")
    print(f"aggregate_complement_classes = {tuple(sorted(aggregate_complements.items(), key=repr))}")
    print("claim_boundary = finite blocker census through GT_8; recursive polarity exclusion remains open")


if __name__ == "__main__":
    self_test()
