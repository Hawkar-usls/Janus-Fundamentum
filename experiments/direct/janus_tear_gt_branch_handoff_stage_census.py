#!/usr/bin/env python3
"""Census the complete P -> raw branch child B -> pre-unit key K' handoff.

T1 and T2a leave one local obligation: branch handoff.  A branch assignment may
join quotient components while more than two remain, so abstract cycle-shield
collapse births are possible.

For every executed child transition of every pre-frontier GT_4,...,GT_8 state,
this checker separates:

    P  parent post-unit residual
    B  raw child input immediately after the branch literal
    K' child residual after pre-unit closure, when an exact key is admitted

It records:

- relation-component shapes and whether the branch assignment is acyclic;
- same-cut pairs in P, B, and K';
- B-pairs transmitted from P versus newly born under the branch contraction;
- source safety classes of every birth;
- directed-cycle shields collapsed by the branch;
- child pre-unit/terminal extinction of every raw B same-cut pair;
- branch-variable frequency and whether the branch joins components.

The checker is a finite theorem-discovery certificate.  It asserts exact trace
replay and the observed absence of same-cut exact keys through GT_8, but no
arbitrary-n branch-handoff theorem.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product

from janus_tear_abstract_post_unit_same_cut_birth_n4 import (
    clause_data,
    is_pre_same_cut,
)
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_double_bridge_transition_birth import enumerate_double_bridges
from janus_tear_gt_novel_branch_audit_v2 import comparison_closure, components
from janus_tear_gt_rank_safety_dichotomy import safety_class

Clause = tuple[int, ...]


def closure_parts(n: int, assignment, pairs):
    closure = comparison_closure(n, assignment, pairs)
    if not closure.acyclic:
        return None, None
    parts = tuple(components(closure))
    index = {
        vertex: part_id
        for part_id, part in enumerate(parts)
        for vertex in part
    }
    return parts, index


def residual_sources(
    clauses: tuple[Clause, ...], assignment: dict[int, bool]
) -> dict[Clause, tuple[Clause, ...]]:
    result: dict[Clause, list[Clause]] = defaultdict(list)
    for source in clauses:
        residual = reduce_clause(source, assignment)
        if residual is None:
            continue
        result[tuple(residual)].append(source)
    return {
        residual: tuple(sources)
        for residual, sources in result.items()
    }


def same_cut_pairs(n, clauses, assignment, pairs):
    return tuple(
        record
        for record in enumerate_double_bridges(
            n, tuple(clauses), assignment, pairs
        )
        if record["left_bridge"]["cut"]
        == record["right_bridge"]["cut"]
    )


def unit_assignments(events):
    assignments: dict[int, bool] = {}
    contradiction = False
    for event in events:
        kind = str(event["kind"])
        if kind == "opposite_units":
            contradiction = True
            break
        if kind != "unit":
            continue
        literal = int(event["literal"])
        variable = abs(literal)
        value = literal > 0
        if variable in assignments and assignments[variable] != value:
            contradiction = True
            break
        assignments[variable] = value
        if event.get("after") is None:
            contradiction = True
            break
    return assignments, contradiction


def branch_frequency(cnf, variable: int):
    frequencies = Counter(
        abs(literal) for clause in cnf for literal in clause
    )
    maximum = max(frequencies.values())
    return frequencies[variable], maximum, tuple(sorted(
        candidate
        for candidate, frequency in frequencies.items()
        if frequency == maximum
    ))


def bridge_count(n, clause, assignment, pairs):
    _classes, bridges = clause_data(n, (clause,), assignment, pairs)
    return sum(
        1 for candidate, _literal in bridges if candidate == clause
    )


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    branch_shape_transitions: Counter[
        tuple[tuple[int, ...], tuple[int, ...]]
    ] = Counter()
    branch_frequency_histogram: Counter[int] = Counter()
    maximum_tie_histogram: Counter[int] = Counter()
    birth_source_classes: Counter[tuple[str, str]] = Counter()
    birth_role_pairs: Counter[tuple[str, str]] = Counter()
    cycle_collapse_classes: Counter[str] = Counter()
    cycle_collapse_bridge_counts: Counter[int] = Counter()
    raw_pair_extinction: Counter[str] = Counter()
    child_pre_unit_counts: Counter[int] = Counter()
    child_terminal_labels: Counter[str] = Counter()
    raw_birth_examples = []
    raw_pair_examples = []
    transition_rows = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            continue

        post = tuple(tuple(clause) for clause in state["post_result"])
        parent_assignment = dict(context["state_after_post"][state_id])
        parent_parts, parent_index = closure_parts(
            n, parent_assignment, pairs
        )
        assert parent_parts is not None and parent_index is not None
        parent_same_cut = same_cut_pairs(
            n, post, parent_assignment, pairs
        )
        counts["parent_same_cut_occurrences"] += len(parent_same_cut)

        branch_var = int(state["branch_var"])
        frequency, maximum, maximizers = branch_frequency(post, branch_var)
        assert frequency == maximum
        assert branch_var == min(maximizers)
        branch_frequency_histogram[frequency] += 1
        maximum_tie_histogram[len(maximizers)] += 1
        branch_low, branch_high = pairs[branch_var]
        branch_joins_components = (
            parent_index[branch_low] != parent_index[branch_high]
        )
        counts[
            "component_joining_branch_states"
            if branch_joins_components
            else "internal_branch_states"
        ] += 1

        pre_classes, pre_bridges = clause_data(
            n, post, parent_assignment, pairs
        )

        for child in state.get("children", ()):
            counts["branch_child_records"] += 1
            value = bool(child["value"])
            branch_literal = int(child["literal"])
            assert branch_literal == (branch_var if value else -branch_var)
            branch_assignment = {branch_var: value}

            if child.get("call") is None:
                counts["direct_conflict_children"] += 1
                child_terminal_labels["DIRECT_CONFLICT"] += 1
                continue

            child_call_id = int(child["call"])
            child_call = policy.calls[child_call_id]
            raw_child = tuple(tuple(clause) for clause in child_call["input"])
            counts["executed_children"] += 1

            after_branch_assignment = dict(parent_assignment)
            assert branch_var not in after_branch_assignment
            after_branch_assignment[branch_var] = value
            branch_parts, _branch_index = closure_parts(
                n, after_branch_assignment, pairs
            )
            if branch_parts is None:
                counts["cyclic_branch_assignments"] += 1
                raw_same_cut = ()
            else:
                counts["acyclic_branch_assignments"] += 1
                branch_shape_transitions[(
                    tuple(sorted(len(part) for part in parent_parts)),
                    tuple(sorted(len(part) for part in branch_parts)),
                )] += 1
                raw_same_cut = same_cut_pairs(
                    n, raw_child, after_branch_assignment, pairs
                )
            counts["raw_child_same_cut_occurrences"] += len(raw_same_cut)

            source_map = residual_sources(post, branch_assignment)
            assert set(raw_child) == set(source_map)

            collapsed_sources = set()
            collapsed_rows = []
            if branch_parts is not None:
                for residual, sources in source_map.items():
                    post_class = str(safety_class(
                        n, residual, after_branch_assignment, pairs
                    )["classification"])
                    for source in sources:
                        if pre_classes[source] != "DIRECTED_CYCLE":
                            continue
                        if post_class == "DIRECTED_CYCLE":
                            continue
                        collapsed_sources.add(source)
                        counts["branch_cycle_shield_collapses"] += 1
                        cycle_collapse_classes[post_class] += 1
                        bridges = bridge_count(
                            n, residual, after_branch_assignment, pairs
                        )
                        cycle_collapse_bridge_counts[bridges] += 1
                        if bridges:
                            counts["collapsed_sources_with_bridge"] += 1
                        collapsed_rows.append({
                            "source": source,
                            "residual": residual,
                            "post_class": post_class,
                            "bridge_literals": bridges,
                        })

            raw_pair_rows = []
            for record in raw_same_cut:
                pivot = int(record["pivot"])
                left = tuple(record["left"])
                right = tuple(record["right"])
                source_pairs = tuple(product(
                    source_map[left], source_map[right]
                ))
                transmitted = any(
                    is_pre_same_cut(
                        left_source,
                        right_source,
                        pivot,
                        pre_bridges,
                    )
                    for left_source, right_source in source_pairs
                )
                if transmitted:
                    counts["raw_transmitted_same_cut_pairs"] += 1
                    birth = False
                else:
                    counts["raw_branch_same_cut_births"] += 1
                    birth = True
                    for left_source, right_source in source_pairs:
                        classes = tuple(sorted((
                            pre_classes[left_source],
                            pre_classes[right_source],
                        )))
                        birth_source_classes[classes] += 1
                    if any(
                        left_source in collapsed_sources
                        or right_source in collapsed_sources
                        for left_source, right_source in source_pairs
                    ):
                        counts["births_using_cycle_collapse"] += 1
                    else:
                        counts["births_without_cycle_collapse"] += 1
                    roles = tuple(sorted((
                        str(record["left_bridge"]["role"]),
                        str(record["right_bridge"]["role"]),
                    )))
                    birth_role_pairs[roles] += 1
                    if len(raw_birth_examples) < 80:
                        raw_birth_examples.append({
                            "n": n,
                            "parent_state": state_id,
                            "parent_call": call_id,
                            "novelty": novelty,
                            "child_call": child_call_id,
                            "branch_literal": branch_literal,
                            "parent_parts": parent_parts,
                            "branch_parts": branch_parts,
                            "pivot": pivot,
                            "left": left,
                            "right": right,
                            "source_pairs": source_pairs,
                            "source_classes": tuple(
                                tuple(sorted((
                                    pre_classes[left_source],
                                    pre_classes[right_source],
                                )))
                                for left_source, right_source in source_pairs
                            ),
                            "roles": roles,
                        })

                raw_pair_rows.append({
                    "pivot": pivot,
                    "left": left,
                    "right": right,
                    "transmitted": transmitted,
                    "birth": birth,
                    "source_pairs": source_pairs,
                })

            pre_events = tuple(child_call.get("pre_units", ()))
            pre_assignment, pre_contradiction = unit_assignments(pre_events)
            child_pre_unit_counts[len(pre_assignment)] += 1
            child_terminal = str(child_call["terminal"])
            child_terminal_labels[child_terminal] += 1

            child_key_raw = child_call.get("pre_result")
            child_key = (
                None
                if child_key_raw is None or child_key_raw == ()
                else tuple(tuple(clause) for clause in child_key_raw)
            )
            child_same_cut = ()
            child_assignment = dict(after_branch_assignment)
            child_assignment.update(pre_assignment)
            child_parts, _child_index = closure_parts(
                n, child_assignment, pairs
            )
            if child_key is not None and child_parts is not None:
                child_same_cut = same_cut_pairs(
                    n, child_key, child_assignment, pairs
                )
            counts["child_exact_key_same_cut_occurrences"] += len(
                child_same_cut
            )

            for raw_record in raw_pair_rows:
                left_residual = reduce_clause(
                    tuple(raw_record["left"]), pre_assignment
                )
                right_residual = reduce_clause(
                    tuple(raw_record["right"]), pre_assignment
                )
                if pre_contradiction or child_key is None:
                    outcome = "TERMINAL_BEFORE_EXACT_KEY"
                elif left_residual is None and right_residual is None:
                    outcome = "BOTH_SOURCE_CLAUSES_REMOVED"
                elif left_residual is None:
                    outcome = "LEFT_SOURCE_CLAUSE_REMOVED"
                elif right_residual is None:
                    outcome = "RIGHT_SOURCE_CLAUSE_REMOVED"
                elif (
                    int(raw_record["pivot"]) not in left_residual
                    or -int(raw_record["pivot"]) not in right_residual
                ):
                    outcome = "COMPLEMENTARY_PIVOT_REMOVED"
                elif (
                    left_residual not in child_key
                    or right_residual not in child_key
                ):
                    outcome = "SOURCE_PAIR_NOT_BOTH_IN_EXACT_KEY"
                else:
                    reappears = any(
                        int(record["pivot"]) == int(raw_record["pivot"])
                        and tuple(record["left"]) == left_residual
                        and tuple(record["right"]) == right_residual
                        for record in child_same_cut
                    )
                    outcome = (
                        "REAPPEARS_SAME_CUT"
                        if reappears
                        else "SURVIVES_BUT_NOT_SAME_CUT"
                    )
                raw_pair_extinction[outcome] += 1
                if len(raw_pair_examples) < 100:
                    raw_pair_examples.append({
                        "n": n,
                        "parent_state": state_id,
                        "child_call": child_call_id,
                        "branch_literal": branch_literal,
                        "raw_pair": raw_record,
                        "pre_units": tuple(sorted(pre_assignment.items())),
                        "child_terminal": child_terminal,
                        "child_parts": child_parts,
                        "left_residual": left_residual,
                        "right_residual": right_residual,
                        "outcome": outcome,
                    })

            transition_rows.append({
                "n": n,
                "parent_state": state_id,
                "parent_call": call_id,
                "novelty": novelty,
                "target": target,
                "branch_variable": branch_var,
                "branch_literal": branch_literal,
                "branch_frequency": frequency,
                "maximum_tie_count": len(maximizers),
                "branch_joins_components": branch_joins_components,
                "parent_parts": parent_parts,
                "branch_parts": branch_parts,
                "parent_same_cut_count": len(parent_same_cut),
                "raw_same_cut_count": len(raw_same_cut),
                "cycle_collapses": tuple(collapsed_rows),
                "pre_unit_count": len(pre_assignment),
                "pre_contradiction": pre_contradiction,
                "child_terminal": child_terminal,
                "child_parts": child_parts,
                "child_same_cut_count": len(child_same_cut),
            })

    assert counts["child_exact_key_same_cut_occurrences"] == 0
    assert raw_pair_extinction["REAPPEARS_SAME_CUT"] == 0

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "branch_shape_transitions": tuple(
            sorted(branch_shape_transitions.items(), key=repr)
        ),
        "branch_frequency_histogram": tuple(
            sorted(branch_frequency_histogram.items())
        ),
        "maximum_tie_histogram": tuple(sorted(maximum_tie_histogram.items())),
        "birth_source_classes": tuple(
            sorted(birth_source_classes.items(), key=repr)
        ),
        "birth_role_pairs": tuple(sorted(birth_role_pairs.items(), key=repr)),
        "cycle_collapse_classes": tuple(sorted(cycle_collapse_classes.items())),
        "cycle_collapse_bridge_counts": tuple(
            sorted(cycle_collapse_bridge_counts.items())
        ),
        "raw_pair_extinction": tuple(sorted(raw_pair_extinction.items())),
        "child_pre_unit_counts": tuple(sorted(child_pre_unit_counts.items())),
        "child_terminal_labels": tuple(sorted(child_terminal_labels.items())),
        "raw_birth_examples": tuple(raw_birth_examples),
        "raw_pair_examples": tuple(raw_pair_examples),
        "transition_rows": tuple(transition_rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_shapes: Counter = Counter()
    aggregate_frequency: Counter[int] = Counter()
    aggregate_ties: Counter[int] = Counter()
    aggregate_birth_classes: Counter = Counter()
    aggregate_birth_roles: Counter = Counter()
    aggregate_collapse_classes: Counter[str] = Counter()
    aggregate_collapse_bridges: Counter[int] = Counter()
    aggregate_extinction: Counter[str] = Counter()
    aggregate_pre_units: Counter[int] = Counter()
    aggregate_terminals: Counter[str] = Counter()
    birth_examples = []
    pair_examples = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_shapes.update(dict(data["branch_shape_transitions"]))
        aggregate_frequency.update(dict(data["branch_frequency_histogram"]))
        aggregate_ties.update(dict(data["maximum_tie_histogram"]))
        aggregate_birth_classes.update(dict(data["birth_source_classes"]))
        aggregate_birth_roles.update(dict(data["birth_role_pairs"]))
        aggregate_collapse_classes.update(dict(data["cycle_collapse_classes"]))
        aggregate_collapse_bridges.update(dict(data["cycle_collapse_bridge_counts"]))
        aggregate_extinction.update(dict(data["raw_pair_extinction"]))
        aggregate_pre_units.update(dict(data["child_pre_unit_counts"]))
        aggregate_terminals.update(dict(data["child_terminal_labels"]))
        birth_examples.extend(data["raw_birth_examples"])
        pair_examples.extend(data["raw_pair_examples"])
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  branch_shape_transitions = {data['branch_shape_transitions']}")
        print(f"  branch_frequency_histogram = {data['branch_frequency_histogram']}")
        print(f"  maximum_tie_histogram = {data['maximum_tie_histogram']}")
        print(f"  birth_source_classes = {data['birth_source_classes']}")
        print(f"  birth_role_pairs = {data['birth_role_pairs']}")
        print(f"  cycle_collapse_classes = {data['cycle_collapse_classes']}")
        print(f"  cycle_collapse_bridge_counts = {data['cycle_collapse_bridge_counts']}")
        print(f"  raw_pair_extinction = {data['raw_pair_extinction']}")
        print(f"  child_pre_unit_counts = {data['child_pre_unit_counts']}")
        print(f"  child_terminal_labels = {data['child_terminal_labels']}")
        print(f"  raw_birth_examples = {data['raw_birth_examples']}")
        print(f"  raw_pair_examples = {data['raw_pair_examples']}")

    assert aggregate_counts["child_exact_key_same_cut_occurrences"] == 0
    assert aggregate_extinction["REAPPEARS_SAME_CUT"] == 0
    print("JANUS_GT_BRANCH_HANDOFF_STAGE_CENSUS = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_SHAPES = {tuple(sorted(aggregate_shapes.items(), key=repr))}")
    print(f"AGGREGATE_BRANCH_FREQUENCY = {tuple(sorted(aggregate_frequency.items()))}")
    print(f"AGGREGATE_MAXIMUM_TIES = {tuple(sorted(aggregate_ties.items()))}")
    print(f"AGGREGATE_BIRTH_CLASSES = {tuple(sorted(aggregate_birth_classes.items(), key=repr))}")
    print(f"AGGREGATE_BIRTH_ROLES = {tuple(sorted(aggregate_birth_roles.items(), key=repr))}")
    print(f"AGGREGATE_COLLAPSE_CLASSES = {tuple(sorted(aggregate_collapse_classes.items()))}")
    print(f"AGGREGATE_COLLAPSE_BRIDGES = {tuple(sorted(aggregate_collapse_bridges.items()))}")
    print(f"AGGREGATE_EXTINCTION = {tuple(sorted(aggregate_extinction.items()))}")
    print(f"AGGREGATE_PRE_UNITS = {tuple(sorted(aggregate_pre_units.items()))}")
    print(f"AGGREGATE_TERMINALS = {tuple(sorted(aggregate_terminals.items()))}")
    print(f"BIRTH_EXAMPLES = {tuple(birth_examples)}")
    print(f"PAIR_EXAMPLES = {tuple(pair_examples)}")
    print(
        "claim_boundary = exact finite P-to-B-to-K-prime branch handoff "
        "census through GT_8 before novelty n-2; arbitrary-n T2b open"
    )


if __name__ == "__main__":
    self_test()
