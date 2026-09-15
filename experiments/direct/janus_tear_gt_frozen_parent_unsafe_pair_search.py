#!/usr/bin/env python3
"""Search all frozen Policy-0A parent pairs for unsafe low-rank resolvents.

Unlike the reached-pair replay, this audit ignores attempt and addition stopping
when deciding whether an unsafe legal resolvent exists somewhere in the frozen
parent lists of a pre-frontier state.  It still uses Policy-0A's width and
tautology filters.

Each candidate's deterministic pair ordinal is compared with the exact number of
pairs processed by the production trace:

- REACHED: ordinal <= resolution_attempts;
- AFTER_STOP: the pair exists in the frozen lists but lies beyond the actual
  one-pass stopping point.

This separates residual-family structure from protection supplied by pair order
and budgets.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_policy0t_trace_certificate import canonical_clause


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    state_counts: Counter[str] = Counter()
    parent_class_pairs: Counter[tuple[str, str]] = Counter()
    unsafe_examples = []
    earliest_after_stop_gap = None
    maximum_after_stop_gap = 0

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        assignment = context["call_after_pre"][call_id]
        key = tuple(state["key"])
        max_width = int(state["width_limit"])
        reached_attempts = int(state["resolution_attempts"])

        parent_class = {
            clause: str(safety_class(n, clause, assignment, pairs)["classification"])
            for clause in key
        }
        positive: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        negative: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for clause in sorted(key, key=lambda item: (len(item), item)):
            for literal in clause:
                target_map = positive if literal > 0 else negative
                target_map[abs(literal)].append(clause)

        ordinal = 0
        state_unsafe = 0
        state_reached_unsafe = 0
        state_after_unsafe = 0

        for pivot in sorted(set(positive) & set(negative)):
            for left in positive[pivot]:
                for right in negative[pivot]:
                    ordinal += 1
                    counts["all_frozen_pairs"] += 1
                    resolvent_set = (set(left) - {pivot}) | (set(right) - {-pivot})
                    if any(-literal in resolvent_set for literal in resolvent_set):
                        counts["tautological_pairs"] += 1
                        continue
                    if len(resolvent_set) > max_width:
                        counts["over_width_pairs"] += 1
                        continue
                    normalized = canonical_clause(resolvent_set)
                    if normalized is None:
                        counts["normalization_rejected_pairs"] += 1
                        continue
                    if not normalized:
                        counts["empty_resolvents"] += 1
                        continue

                    counts["legal_nonempty_pairs"] += 1
                    structure = safety_class(n, normalized, assignment, pairs)
                    if structure["classification"] != "UNSAFE_ACYCLIC_LOW_RANK":
                        continue

                    state_unsafe += 1
                    counts["unsafe_pairs"] += 1
                    left_class = parent_class[left]
                    right_class = parent_class[right]
                    parent_class_pairs[(left_class, right_class)] += 1
                    reached = ordinal <= reached_attempts
                    timing = "REACHED" if reached else "AFTER_STOP"
                    counts[f"unsafe_{timing.lower()}"] += 1
                    if reached:
                        state_reached_unsafe += 1
                    else:
                        state_after_unsafe += 1
                        gap = ordinal - reached_attempts
                        earliest_after_stop_gap = (
                            gap
                            if earliest_after_stop_gap is None
                            else min(earliest_after_stop_gap, gap)
                        )
                        maximum_after_stop_gap = max(maximum_after_stop_gap, gap)

                    if len(unsafe_examples) < 50:
                        unsafe_examples.append(
                            {
                                "n": n,
                                "state_id": int(state["id"]),
                                "call_id": call_id,
                                "novelty": novelty,
                                "pivot": pivot,
                                "left": left,
                                "right": right,
                                "left_class": left_class,
                                "right_class": right_class,
                                "resolvent": normalized,
                                "structure": structure,
                                "pair_ordinal": ordinal,
                                "reached_attempts": reached_attempts,
                                "timing": timing,
                                "gap_after_stop": max(0, ordinal - reached_attempts),
                            }
                        )

        counts["states"] += 1
        if state_unsafe:
            state_counts["states_with_unsafe_pair"] += 1
        if state_reached_unsafe:
            state_counts["states_with_reached_unsafe_pair"] += 1
        if state_after_unsafe:
            state_counts["states_with_after_stop_unsafe_pair"] += 1

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "state_counts": tuple(sorted(state_counts.items())),
        "parent_class_pairs": tuple(sorted(parent_class_pairs.items())),
        "earliest_after_stop_gap": earliest_after_stop_gap,
        "maximum_after_stop_gap": maximum_after_stop_gap,
        "unsafe_examples": tuple(unsafe_examples),
    }


def self_test() -> None:
    rows = []
    aggregate: Counter[str] = Counter()
    aggregate_states: Counter[str] = Counter()
    aggregate_parent_pairs: Counter[tuple[str, str]] = Counter()
    unsafe_sizes = []

    for n in range(4, 9):
        data = audit(n)
        aggregate.update(dict(data["counts"]))
        aggregate_states.update(dict(data["state_counts"]))
        aggregate_parent_pairs.update(dict(data["parent_class_pairs"]))
        if dict(data["counts"]).get("unsafe_pairs", 0):
            unsafe_sizes.append(n)
        rows.append(
            (
                n,
                data["target"],
                data["counts"],
                data["state_counts"],
                data["earliest_after_stop_gap"],
                data["maximum_after_stop_gap"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  state_counts = {data['state_counts']}")
        print(f"  parent_class_pairs = {data['parent_class_pairs']}")
        print(f"  earliest_after_stop_gap = {data['earliest_after_stop_gap']}")
        print(f"  maximum_after_stop_gap = {data['maximum_after_stop_gap']}")
        print(f"  unsafe_examples = {data['unsafe_examples']}")

    print("JANUS_GT_FROZEN_PARENT_UNSAFE_PAIR_SEARCH = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_counts = {tuple(sorted(aggregate.items()))}")
    print(f"aggregate_state_counts = {tuple(sorted(aggregate_states.items()))}")
    print(f"aggregate_parent_class_pairs = {tuple(sorted(aggregate_parent_pairs.items()))}")
    print(f"unsafe_sizes = {tuple(unsafe_sizes)}")
    print("claim_boundary = finite exhaustive search of frozen parent lists under the policy width filter; not an asymptotic closure theorem")


if __name__ == "__main__":
    self_test()
