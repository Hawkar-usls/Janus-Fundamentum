#!/usr/bin/env python3
"""Fail-closed Q1/Q0 calibration equivalence test.

Q1 is admitted only if it preserves Q0's Boolean result, residual-state count,
resolution work and certified bytewise-distinct quotient hits on the frozen
GT_3..GT_9 calibration corpus while not increasing Q0 refinement edge visits.
This is software/calibration evidence only.
"""

from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
from janus_tear_policy0a_q0_typed_anchor_gauge_probe import Policy0AQ0
from janus_tear_policy0a_q1_lazy_typed_prefilter_probe import Policy0AQ1Lazy


def main() -> None:
    total_q0_edges = 0
    total_q1_edges = 0
    total_q0_merges = 0
    total_q1_merges = 0

    for order in range(3, 10):
        cnf, variable_count = graph_tautology_cnf(order)
        q0 = Policy0AQ0().solve(cnf, variable_count)
        q1 = Policy0AQ1Lazy().solve(cnf, variable_count)

        assert q0.answer == q1.answer, (order, "answer", q0.answer, q1.answer)
        assert q0.cap_exceeded == q1.cap_exceeded, (order, "cap")
        assert q0.residual_states == q1.residual_states, (
            order, "states", q0.residual_states, q1.residual_states
        )
        assert q0.resolution_attempts == q1.resolution_attempts, (
            order, "attempts", q0.resolution_attempts, q1.resolution_attempts
        )
        assert q0.resolution_additions == q1.resolution_additions, (
            order, "additions", q0.resolution_additions, q1.resolution_additions
        )
        assert q0.bytewise_distinct_hits == q1.bytewise_distinct_hits, (
            order, "certified_merges", q0.bytewise_distinct_hits,
            q1.bytewise_distinct_hits
        )
        assert q1.refinement_edge_visits <= q0.refinement_edge_visits, (
            order, "refinement_regression", q0.refinement_edge_visits,
            q1.refinement_edge_visits
        )

        total_q0_edges += q0.refinement_edge_visits
        total_q1_edges += q1.refinement_edge_visits
        total_q0_merges += q0.bytewise_distinct_hits
        total_q1_merges += q1.bytewise_distinct_hits

        print(
            f"GT_{order}: states={q1.residual_states} "
            f"certified_merges={q1.bytewise_distinct_hits} "
            f"q0_edges={q0.refinement_edge_visits} "
            f"q1_edges={q1.refinement_edge_visits} "
            f"q1_q0_ratio={(q1.refinement_edge_visits / q0.refinement_edge_visits if q0.refinement_edge_visits else 0):.6f}"
        )

    assert total_q0_merges == total_q1_merges
    print(f"TOTAL_Q0_REFINEMENT_EDGE_VISITS = {total_q0_edges}")
    print(f"TOTAL_Q1_REFINEMENT_EDGE_VISITS = {total_q1_edges}")
    print(
        "TOTAL_Q1_Q0_EDGE_RATIO = "
        f"{(total_q1_edges / total_q0_edges if total_q0_edges else 0):.9f}"
    )
    print(f"TOTAL_CERTIFIED_BYTEWISE_DISTINCT_MERGES = {total_q1_merges}")
    print("Q1_Q0_CALIBRATION_EQUIVALENCE = PASS")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
