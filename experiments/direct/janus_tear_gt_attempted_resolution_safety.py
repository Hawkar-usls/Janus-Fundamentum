#!/usr/bin/env python3
"""Classify every Resolution pair reached by the exact Policy-0A one-pass loop.

The cycle-or-spanning class is not closed under arbitrary Resolution. Policy-0A,
however, uses frozen parent lists, deterministic pair order, and strict attempt
and addition budgets. This audit reconstructs every pair actually reached from
each pre-frontier state key and classifies its legal nonempty resolvent before
checking whether it is new, duplicate, or accepted.

The replay must reproduce the serialized resolution event list, attempts,
additions and final clause set exactly. Unsafe acyclic low-rank candidates are
reported whether new or duplicate.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_policy0t_trace_certificate import canonical_clause, canonical_cnf


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    class_histogram: Counter[str] = Counter()
    unsafe_examples = []
    unsafe_state_histogram: Counter[int] = Counter()
    replayed_event_count = 0

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        key = tuple(state["key"])
        clauses = set(key)
        positive: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        negative: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for clause in sorted(clauses, key=lambda item: (len(item), item)):
            for literal in clause:
                target_map = positive if literal > 0 else negative
                target_map[abs(literal)].append(clause)

        attempt_budget = int(state["attempt_budget"])
        addition_budget = int(state["addition_budget"])
        max_width = int(state["width_limit"])
        expected_events = tuple(state.get("resolution_events", []))
        replayed_events = []
        attempts = 0
        additions = 0
        stopped = False

        for pivot in sorted(set(positive) & set(negative)):
            if stopped:
                break
            for left in positive[pivot]:
                if stopped:
                    break
                for right in negative[pivot]:
                    attempts += 1
                    if attempts > attempt_budget or additions >= addition_budget:
                        # The production loop returns attempts-1 for the pair
                        # whose processing is blocked by either budget.
                        attempts -= 1
                        stopped = True
                        break

                    counts["attempted_pairs"] += 1
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
                        event = {
                            "left": left,
                            "right": right,
                            "pivot": pivot,
                            "resolvent": normalized,
                            "attempt": attempts,
                        }
                        replayed_events.append(event)
                        clauses.add(normalized)
                        additions += 1
                        stopped = True
                        break

                    counts["legal_nonempty_resolvents"] += 1
                    structure = safety_class(
                        n,
                        normalized,
                        context["call_after_pre"][call_id],
                        pairs,
                    )
                    classification = str(structure["classification"])
                    class_histogram[classification] += 1
                    is_new = normalized not in clauses
                    counts[
                        "new_legal_resolvents" if is_new else "duplicate_legal_resolvents"
                    ] += 1

                    if classification == "UNSAFE_ACYCLIC_LOW_RANK":
                        counts["unsafe_legal_resolvents"] += 1
                        unsafe_state_histogram[int(state["id"])] += 1
                        counts[
                            "unsafe_new_resolvents" if is_new else "unsafe_duplicate_resolvents"
                        ] += 1
                        if len(unsafe_examples) < 30:
                            unsafe_examples.append(
                                {
                                    "n": n,
                                    "state_id": int(state["id"]),
                                    "call_id": call_id,
                                    "novelty": novelty,
                                    "pivot": pivot,
                                    "left": left,
                                    "right": right,
                                    "resolvent": normalized,
                                    "is_new": is_new,
                                    "structure": structure,
                                    "attempt": attempts,
                                }
                            )

                    if is_new:
                        clauses.add(normalized)
                        additions += 1
                        replayed_events.append(
                            {
                                "left": left,
                                "right": right,
                                "pivot": pivot,
                                "resolvent": normalized,
                                "attempt": attempts,
                            }
                        )

        assert tuple(replayed_events) == expected_events, (
            n,
            state["id"],
            len(replayed_events),
            len(expected_events),
        )
        assert canonical_cnf(clauses) == tuple(state["resolution_output"])
        assert additions == int(state["resolution_additions"])
        assert attempts == int(state["resolution_attempts"])
        replayed_event_count += len(replayed_events)
        counts["replayed_states"] += 1

    counts["replayed_events"] = replayed_event_count

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "class_histogram": tuple(sorted(class_histogram.items())),
        "unsafe_state_histogram": tuple(sorted(unsafe_state_histogram.items())),
        "unsafe_examples": tuple(unsafe_examples),
    }


def self_test() -> None:
    rows = []
    aggregate: Counter[str] = Counter()
    aggregate_classes: Counter[str] = Counter()
    unsafe_sizes = []

    for n in range(4, 9):
        data = audit(n)
        aggregate.update(dict(data["counts"]))
        aggregate_classes.update(dict(data["class_histogram"]))
        if dict(data["counts"]).get("unsafe_legal_resolvents", 0):
            unsafe_sizes.append(n)
        rows.append(
            (
                n,
                data["target"],
                data["counts"],
                data["class_histogram"],
                data["unsafe_state_histogram"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  class_histogram = {data['class_histogram']}")
        print(f"  unsafe_state_histogram = {data['unsafe_state_histogram']}")
        print(f"  unsafe_examples = {data['unsafe_examples']}")

    print("JANUS_GT_ATTEMPTED_RESOLUTION_SAFETY = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_counts = {tuple(sorted(aggregate.items()))}")
    print(f"aggregate_classes = {tuple(sorted(aggregate_classes.items()))}")
    print(f"unsafe_sizes = {tuple(unsafe_sizes)}")
    print("claim_boundary = finite exact replay of reached parent pairs; unrestricted or over-budget pairs are not classified")


if __name__ == "__main__":
    self_test()
