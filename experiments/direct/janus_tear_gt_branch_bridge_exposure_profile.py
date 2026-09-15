#!/usr/bin/env python3
"""Profile the complete finite obstruction set for the branch handoff gate.

The full P -> raw branch child B census through GT_8 found:

    42,966 directed-cycle shield collapses;
    only two collapsed residuals with any bridge literal;
    zero raw same-cut pairs in B;
    one same-cut pair in a parent P (the GT_4 transient).

This checker emits proof-carrying records for exactly those rare objects.

For each bridge-bearing cycle-shield collapse it records:

- parent state/call/novelty and deterministic branch selector data;
- source and residual clause, entry/fresh origin, producing events, and exact
  root-axiom provenance;
- every residual bridge literal, role, and cut;
- every clause containing the complementary literal in B;
- whether that candidate is cyclic, unsafe, internal, spanning-nonbridge, or a
  bridge with the same/different cut.

It also follows the unique GT_4 P same-cut transient across each raw branch
restriction, before child pre-units, and records the exact geometric reason that
same-cut status disappears.

The checker asserts only the already discovered finite counts and absence of a
same-cut partner.  It is a theorem-discovery certificate, not an arbitrary-n
branch-handoff proof.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_branch_handoff_stage_census import (
    branch_frequency,
    closure_parts,
    residual_sources,
    same_cut_pairs,
)
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_double_bridge_root_owner_provenance import replay_provenance
from janus_tear_gt_rank_safety_dichotomy import safety_class

Clause = tuple[int, ...]
RootSource = tuple[str, int | None, Clause]


def unit_assignments(events) -> dict[int, bool]:
    assignments: dict[int, bool] = {}
    for event in events:
        if event["kind"] != "unit":
            continue
        literal = int(event["literal"])
        variable = abs(literal)
        value = literal > 0
        assert variable not in assignments or assignments[variable] == value
        assignments[variable] = value
    return assignments


def root_signature(sources: frozenset[RootSource]):
    return {
        "nonminimality_owners": tuple(sorted({
            int(owner)
            for kind, owner, _clause in sources
            if kind == "N" and owner is not None
        })),
        "transitivity_count": sum(
            1 for kind, _owner, _clause in sources if kind == "T"
        ),
        "root_source_count": len(sources),
    }


def post_provenance(n: int, state_id: int):
    context, _labels, key_provenance = replay_provenance(n)
    policy = context["policy"]
    state = policy.states[state_id]
    key = tuple(tuple(clause) for clause in state["key"])
    key_set = set(key)
    entry_sources = key_provenance[state_id]

    output_roots: dict[Clause, set[RootSource]] = defaultdict(set)
    output_origins: dict[Clause, set[str]] = defaultdict(set)
    output_events: dict[Clause, list[dict[str, object]]] = defaultdict(list)
    for clause in key:
        output_roots[clause].update(entry_sources[clause])
        output_origins[clause].add("ENTRY_KEY")
    for event in state.get("resolution_events", ()):
        left = tuple(event["left"])
        right = tuple(event["right"])
        resolvent = tuple(event["resolvent"])
        output_roots[resolvent].update(entry_sources[left])
        output_roots[resolvent].update(entry_sources[right])
        output_origins[resolvent].add("LOCAL_RESOLVENT")
        output_events[resolvent].append(event)

    output = tuple(tuple(clause) for clause in state["resolution_output"])
    assert set(output) == set(output_roots) == set(output_origins)
    assignments = unit_assignments(state.get("post_units", ()))

    post_roots: dict[Clause, set[RootSource]] = defaultdict(set)
    post_origins: dict[Clause, set[str]] = defaultdict(set)
    post_events: dict[Clause, list[dict[str, object]]] = defaultdict(list)
    for source in output:
        residual = reduce_clause(source, assignments)
        if residual is None:
            continue
        residual = tuple(residual)
        post_roots[residual].update(output_roots[source])
        post_origins[residual].update(output_origins[source])
        post_events[residual].extend(output_events.get(source, ()))

    post = tuple(tuple(clause) for clause in state["post_result"])
    assert set(post) == set(post_roots) == set(post_origins)
    return context, {
        clause: {
            "origins": tuple(sorted(post_origins[clause])),
            "root": root_signature(frozenset(post_roots[clause])),
            "producing_events": tuple({
                "attempt": int(event["attempt"]),
                "pivot": int(event["pivot"]),
                "left": tuple(event["left"]),
                "right": tuple(event["right"]),
            } for event in post_events.get(clause, ())),
        }
        for clause in post
    }


def literal_bridge_record(n, clause, assignment, pairs, literal):
    structure = safety_class(n, clause, assignment, pairs)
    classification = str(structure["classification"])
    result = {
        "classification": classification,
        "bridge": None,
    }
    if classification != "COMPONENT_SPANNING":
        return result
    graph = clause_component_graph(n, clause, assignment, pairs)
    bridge = bridge_record(clause, graph, pairs, literal)
    if bridge is not None:
        result["bridge"] = bridge
    return result


def complementary_candidate_record(
    n: int,
    clause: Clause,
    literal: int,
    assignment,
    pairs,
    target_cut,
):
    status = literal_bridge_record(n, clause, assignment, pairs, literal)
    classification = status["classification"]
    bridge = status["bridge"]
    if classification == "DIRECTED_CYCLE":
        reason = "DIRECTED_CYCLE"
    elif classification == "INTERNAL_ONLY":
        reason = "INTERNAL_ONLY"
    elif classification == "UNSAFE_ACYCLIC_LOW_RANK":
        reason = "UNSAFE_ACYCLIC_LOW_RANK"
    elif classification != "COMPONENT_SPANNING":
        reason = classification
    elif bridge is None:
        reason = "SPANNING_NONBRIDGE"
    elif bridge["cut"] == target_cut:
        reason = "SAME_CUT_BRIDGE_PARTNER"
    else:
        reason = "DIFFERENT_CUT_BRIDGE"
    return {
        "clause": clause,
        "literal": literal,
        "classification": classification,
        "bridge": bridge,
        "reason": reason,
    }


def profile_bridge_exposures(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    partner_reasons: Counter[str] = Counter()
    records = []
    provenance_cache = {}

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target or state["terminal"] not in (
            "BRANCH_UNSAT", "BRANCH_SAT"
        ):
            continue

        post = tuple(tuple(clause) for clause in state["post_result"])
        parent_assignment = dict(context["state_after_post"][state_id])
        pre_classes = {
            clause: str(safety_class(
                n, clause, parent_assignment, pairs
            )["classification"])
            for clause in post
        }
        branch_var = int(state["branch_var"])
        frequency, maximum, maximizers = branch_frequency(post, branch_var)
        assert frequency == maximum and branch_var == min(maximizers)

        for child in state.get("children", ()):
            if child.get("call") is None:
                continue
            child_call_id = int(child["call"])
            branch_literal = int(child["literal"])
            value = bool(child["value"])
            assert branch_literal == (branch_var if value else -branch_var)
            branch_assignment = {branch_var: value}
            raw_child = tuple(
                tuple(clause) for clause in policy.calls[child_call_id]["input"]
            )
            source_map = residual_sources(post, branch_assignment)
            assert set(raw_child) == set(source_map)
            after_assignment = dict(parent_assignment)
            after_assignment[branch_var] = value
            parts, _index = closure_parts(n, after_assignment, pairs)
            assert parts is not None

            for residual, sources in source_map.items():
                post_class = str(safety_class(
                    n, residual, after_assignment, pairs
                )["classification"])
                for source in sources:
                    if pre_classes[source] != "DIRECTED_CYCLE":
                        continue
                    if post_class == "DIRECTED_CYCLE":
                        continue

                    bridge_rows = []
                    if post_class == "COMPONENT_SPANNING":
                        graph = clause_component_graph(
                            n, residual, after_assignment, pairs
                        )
                        for literal in residual:
                            bridge = bridge_record(
                                residual, graph, pairs, int(literal)
                            )
                            if bridge is None:
                                continue
                            counts["bridge_literals_exposed"] += 1
                            complement = -int(literal)
                            candidates = tuple(
                                clause
                                for clause in raw_child
                                if complement in clause
                            )
                            candidate_rows = tuple(
                                complementary_candidate_record(
                                    n,
                                    candidate,
                                    complement,
                                    after_assignment,
                                    pairs,
                                    bridge["cut"],
                                )
                                for candidate in candidates
                            )
                            for candidate in candidate_rows:
                                partner_reasons[candidate["reason"]] += 1
                                if candidate["reason"] == (
                                    "SAME_CUT_BRIDGE_PARTNER"
                                ):
                                    counts["same_cut_partners"] += 1
                            if not candidates:
                                partner_reasons[
                                    "NO_COMPLEMENTARY_LITERAL_CLAUSE"
                                ] += 1
                            bridge_rows.append({
                                "literal": int(literal),
                                "endpoints": pairs[abs(int(literal))],
                                "role": str(bridge["role"]),
                                "cut": bridge["cut"],
                                "complementary_literal": complement,
                                "candidate_count": len(candidates),
                                "candidates": candidate_rows,
                            })

                    if not bridge_rows:
                        continue
                    counts["bridge_bearing_cycle_collapses"] += 1
                    if state_id not in provenance_cache:
                        _ctx, provenance_cache[state_id] = post_provenance(
                            n, state_id
                        )
                    records.append({
                        "n": n,
                        "state_id": state_id,
                        "call_id": call_id,
                        "novelty": novelty,
                        "target": target,
                        "child_call_id": child_call_id,
                        "branch_variable": branch_var,
                        "branch_literal": branch_literal,
                        "branch_frequency": frequency,
                        "maximum_variables": maximizers,
                        "parent_component_parts": closure_parts(
                            n, parent_assignment, pairs
                        )[0],
                        "child_component_parts": parts,
                        "source": source,
                        "source_provenance": provenance_cache[state_id][source],
                        "residual": residual,
                        "post_class": post_class,
                        "bridges": tuple(bridge_rows),
                    })

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "partner_reasons": tuple(sorted(partner_reasons.items())),
        "records": tuple(records),
    }


def profile_gt4_transient():
    n = 4
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    records = []
    counts: Counter[str] = Counter()

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        post = state.get("post_result")
        if post is None:
            continue
        post = tuple(tuple(clause) for clause in post)
        assignment = dict(context["state_after_post"][state_id])
        parent_pairs = same_cut_pairs(n, post, assignment, pairs)
        if not parent_pairs:
            continue

        for pair in parent_pairs:
            counts["parent_same_cut_pairs"] += 1
            pivot = int(pair["pivot"])
            left = tuple(pair["left"])
            right = tuple(pair["right"])
            parent_record = {
                "pivot": pivot,
                "left": left,
                "right": right,
                "left_bridge": pair["left_bridge"],
                "right_bridge": pair["right_bridge"],
            }
            child_rows = []

            for child in state.get("children", ()):
                if child.get("call") is None:
                    continue
                child_call_id = int(child["call"])
                branch_literal = int(child["literal"])
                branch_var = abs(branch_literal)
                branch_assignment = {
                    branch_var: branch_literal > 0
                }
                raw_child = tuple(
                    tuple(clause)
                    for clause in policy.calls[child_call_id]["input"]
                )
                source_map = residual_sources(post, branch_assignment)
                assert set(raw_child) == set(source_map)
                left_residual = reduce_clause(left, branch_assignment)
                right_residual = reduce_clause(right, branch_assignment)
                child_assignment = dict(assignment)
                child_assignment.update(branch_assignment)
                raw_pairs = same_cut_pairs(
                    n, raw_child, child_assignment, pairs
                )
                counts["raw_child_same_cut_pairs"] += len(raw_pairs)

                left_status = (
                    None
                    if left_residual is None
                    else literal_bridge_record(
                        n,
                        tuple(left_residual),
                        child_assignment,
                        pairs,
                        pivot,
                    )
                )
                right_status = (
                    None
                    if right_residual is None
                    else literal_bridge_record(
                        n,
                        tuple(right_residual),
                        child_assignment,
                        pairs,
                        -pivot,
                    )
                )

                if left_residual is None or right_residual is None:
                    reason = "CLAUSE_REMOVED_BY_BRANCH"
                elif left_status["bridge"] is None:
                    reason = "LEFT_PIVOT_NOT_A_BRIDGE"
                elif right_status["bridge"] is None:
                    reason = "RIGHT_PIVOT_NOT_A_BRIDGE"
                elif (
                    left_status["bridge"]["cut"]
                    != right_status["bridge"]["cut"]
                ):
                    reason = "BRIDGE_CUTS_SEPARATED"
                else:
                    reason = "SAME_CUT_SURVIVES"
                assert reason != "SAME_CUT_SURVIVES"

                child_rows.append({
                    "child_call_id": child_call_id,
                    "branch_literal": branch_literal,
                    "raw_child": raw_child,
                    "left_residual": left_residual,
                    "right_residual": right_residual,
                    "left_status": left_status,
                    "right_status": right_status,
                    "raw_same_cut_count": len(raw_pairs),
                    "extinction_reason": reason,
                })

            records.append({
                "state_id": state_id,
                "call_id": call_id,
                "novelty": int(levels[call_id]),
                "parent": parent_record,
                "children": tuple(child_rows),
            })

    assert counts["parent_same_cut_pairs"] == 1
    assert counts["raw_child_same_cut_pairs"] == 0
    assert len(records) == 1
    assert len(records[0]["children"]) == 2
    return {
        "counts": tuple(sorted(counts.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_reasons: Counter[str] = Counter()
    exposure_records = []
    for n in range(4, 9):
        data = profile_bridge_exposures(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_reasons.update(dict(data["partner_reasons"]))
        exposure_records.extend(data["records"])
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  partner_reasons = {data['partner_reasons']}")
        print(f"  records = {data['records']}")

    transient = profile_gt4_transient()
    print(f"GT4_TRANSIENT_COUNTS = {transient['counts']}")
    print(f"GT4_TRANSIENT_RECORDS = {transient['records']}")

    assert aggregate_counts["bridge_bearing_cycle_collapses"] == 2
    assert aggregate_counts["bridge_literals_exposed"] == 2
    assert aggregate_counts["same_cut_partners"] == 0
    assert len(exposure_records) == 2

    print("JANUS_GT_BRANCH_BRIDGE_EXPOSURE_PROFILE = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_PARTNER_REASONS = {tuple(sorted(aggregate_reasons.items()))}")
    print(f"EXPOSURE_RECORDS = {tuple(exposure_records)}")
    print(
        "claim_boundary = exact finite profile of the two bridge-bearing "
        "branch cycle-shield collapses and the unique GT_4 inherited "
        "same-cut transient through GT_8; arbitrary-n T2b remains open"
    )


if __name__ == "__main__":
    self_test()
