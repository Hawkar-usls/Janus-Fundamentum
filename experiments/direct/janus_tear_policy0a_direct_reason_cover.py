#!/usr/bin/env python3
"""Compute exact emitted-reason covers for direct Policy-0A cache targets.

For every directly reused residual state, collect the original entry context and
all original cache-hit contexts.  The exact cache DAG is unfolded and translated
by the C022 Resolution mechanism.  An emitted clause covers a direct context iff
it is falsified by every full entry assignment of that state/context occurrence.
A small exact set-cover solver computes the minimum number of emitted clauses
needed to cover all direct contexts of each state.

This measures one fixed reason language (clauses emitted by the C022 translator).
It is not a lower bound against arbitrary reason systems.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from janus_tear_policy0a_reason_reuse_audit import (
    RecordingTranslator,
    assignment_boundary,
    unfold_fc_calls,
)


def direct_contexts(policy: FCTracePolicy) -> dict[int, set[tuple[int, ...]]]:
    result: dict[int, set[tuple[int, ...]]] = defaultdict(set)
    for state_id, state in policy.states.items():
        result[state_id].add(tuple(state["context"]))
    for call in policy.calls.values():
        if call.get("terminal") == "CACHE_HIT":
            result[int(call["cache_target"])].add(tuple(call["context"]))
    return result


def minimum_cover(coverage_masks: set[int], universe: int) -> int:
    masks = {mask & universe for mask in coverage_masks if mask & universe}
    assert masks

    # Remove masks contained in another mask.
    maximal = {
        mask
        for mask in masks
        if not any(mask != other and mask | other == other for other in masks)
    }
    masks_by_bit: dict[int, tuple[int, ...]] = {}
    bit = 1
    while bit <= universe:
        if universe & bit:
            choices = tuple(mask for mask in maximal if mask & bit)
            assert choices
            masks_by_bit[bit] = choices
        bit <<= 1

    @lru_cache(maxsize=None)
    def solve(uncovered: int) -> int:
        if uncovered == 0:
            return 0
        bits = [bit for bit in masks_by_bit if uncovered & bit]
        pivot = min(
            bits,
            key=lambda candidate: len(
                [mask for mask in masks_by_bit[candidate] if mask & uncovered]
            ),
        )
        best = uncovered.bit_count()
        for mask in masks_by_bit[pivot]:
            removed = mask & uncovered
            if not removed:
                continue
            best = min(best, 1 + solve(uncovered & ~mask))
        return best

    return solve(universe)


def self_test() -> None:
    cnf, variable_count = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert result.unique_states == 2427
    assert result.cache_hits == 888
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    wanted = {
        state_id: contexts
        for state_id, contexts in direct_contexts(policy).items()
        if len(contexts) >= 2
    }
    assert len(wanted) == 438

    nodes, root_node, source_state, unfolded_context = unfold_fc_calls(
        policy, root_call
    )
    translator = RecordingTranslator(cnf, nodes)
    final_line = translator.translate(root_node)
    assert translator.proof.clause(final_line) == ()

    nodes_by_state_context: dict[
        tuple[int, tuple[int, ...]], list[int]
    ] = defaultdict(list)
    for node_id, state_id in source_state.items():
        if state_id is not None:
            nodes_by_state_context[(state_id, unfolded_context[node_id])].append(
                node_id
            )

    cover_histogram: dict[int, int] = defaultdict(int)
    context_histogram: dict[int, int] = defaultdict(int)
    total_minimum_reasons = 0
    total_direct_contexts = 0
    maximum_minimum_cover = 0
    maximum_direct_contexts = 0
    states_with_one_reason = 0
    states_requiring_multiple_reasons = 0
    states_where_each_context_needs_distinct_reason = 0

    for state_id, contexts in wanted.items():
        ordered_contexts = tuple(sorted(contexts))
        context_count = len(ordered_contexts)
        maximum_direct_contexts = max(maximum_direct_contexts, context_count)
        total_direct_contexts += context_count
        context_histogram[context_count] += 1

        common_boundaries: list[frozenset[int]] = []
        candidate_clauses: set[tuple[int, ...]] = set()

        for context in ordered_contexts:
            node_ids = nodes_by_state_context[(state_id, context)]
            assert node_ids
            boundaries = [
                assignment_boundary(translator.entry_assignments[node_id])
                for node_id in node_ids
            ]
            common = boundaries[0]
            for boundary in boundaries[1:]:
                common = common & boundary
            common_boundaries.append(common)

            for node_id in node_ids:
                assert translator.return_answers[node_id] is False
                line = translator.return_lines[node_id]
                assert line is not None
                candidate_clauses.add(translator.proof.clause(line))

        coverage_masks: set[int] = set()
        for clause in candidate_clauses:
            mask = 0
            for index, boundary in enumerate(common_boundaries):
                if set(clause) <= boundary:
                    mask |= 1 << index
            if mask:
                coverage_masks.add(mask)

        universe = (1 << context_count) - 1
        covered = 0
        for mask in coverage_masks:
            covered |= mask
        assert covered == universe

        cover = minimum_cover(coverage_masks, universe)
        cover_histogram[cover] += 1
        total_minimum_reasons += cover
        maximum_minimum_cover = max(maximum_minimum_cover, cover)
        states_with_one_reason += cover == 1
        states_requiring_multiple_reasons += cover > 1
        states_where_each_context_needs_distinct_reason += cover == context_count

    assert states_with_one_reason + states_requiring_multiple_reasons == 438

    print("JANUS_POLICY0A_DIRECT_REASON_COVER = PASS")
    print(f"direct_reused_cache_states = {len(wanted)}")
    print(f"direct_contexts_total = {total_direct_contexts}")
    print(f"maximum_direct_contexts_per_state = {maximum_direct_contexts}")
    print(f"states_with_one_reusable_reason = {states_with_one_reason}")
    print(f"states_requiring_multiple_reasons = {states_requiring_multiple_reasons}")
    print(
        "states_where_each_context_needs_distinct_reason = "
        f"{states_where_each_context_needs_distinct_reason}"
    )
    print(f"total_minimum_emitted_reasons = {total_minimum_reasons}")
    print(f"maximum_minimum_reason_cover = {maximum_minimum_cover}")
    print(f"reason_cover_histogram = {tuple(sorted(cover_histogram.items()))}")
    print(f"direct_context_histogram = {tuple(sorted(context_histogram.items()))}")
    print("reason_language = clauses emitted by fully unfolded C022 translation")
    print("claim_boundary = finite exact set cover in one reason language; no arbitrary-reason lower bound")


if __name__ == "__main__":
    self_test()
