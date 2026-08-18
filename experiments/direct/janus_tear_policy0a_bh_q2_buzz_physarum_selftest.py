#!/usr/bin/env python3
"""Fail-closed self-tests for BH-Q2 Buzz/Physarum signed singularities."""

from __future__ import annotations

from itertools import product

from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    Policy0ABHQ2,
    apply_signed_map,
    compose_current_to_representative,
    invert_signed_map,
    signed_incidence_canonicalize,
    signed_map_roundtrip_ok,
    signed_typed_signature,
)
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
from janus_tear_policy0a_masked_tseitin import CNF, canonical_cnf
from janus_tear_policy0a_q1_lazy_typed_prefilter_probe import Policy0AQ1Lazy


def evaluate(cnf: CNF, assignment: dict[int, bool]) -> bool:
    for clause in cnf:
        if not any(
            assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)]
            for lit in clause
        ):
            return False
    return True


def first_witness(cnf: CNF) -> dict[int, bool] | None:
    variables = sorted({abs(lit) for clause in cnf for lit in clause})
    for bits in product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        if evaluate(cnf, assignment):
            return assignment
    return None


def map_assignment(assignment: dict[int, bool], mapping: dict[int, tuple[int, bool]]) -> dict[int, bool]:
    out: dict[int, bool] = {}
    for source, (target, flip) in mapping.items():
        value = bool(assignment[source]) ^ bool(flip)
        if target in out and out[target] != value:
            raise AssertionError("assignment map is not functional")
        out[target] = value
    return out


def signed_witness_roundtrip_test() -> None:
    original = canonical_cnf(
        (
            (1, 2, 3, 4),
            (1, -2),
            (1, -2, 3),
            (-1, 2, -3, 4),
            (-1, -2, 4),
            (2, 3),
            (-3, 4),
            (-4, 2, 3),
        )
    )
    external_map = {
        1: (4, True),
        2: (1, False),
        3: (3, True),
        4: (2, False),
    }
    transformed = apply_signed_map(original, external_map)
    assert transformed != original
    assert signed_typed_signature(original) == signed_typed_signature(transformed)

    q_original = signed_incidence_canonicalize(original)
    q_transformed = signed_incidence_canonicalize(transformed)
    assert q_original.key == q_transformed.key, (
        q_original.key.mode,
        q_transformed.key.mode,
    )

    transformed_to_original = compose_current_to_representative(
        q_transformed.old_to_canonical,
        q_original.old_to_canonical,
    )
    assert signed_map_roundtrip_ok(transformed_to_original)
    assert apply_signed_map(transformed, transformed_to_original) == original
    inverse = invert_signed_map(transformed_to_original)
    assert apply_signed_map(original, inverse) == transformed
    assert any(flip for _, flip in transformed_to_original.values())

    witness = first_witness(transformed)
    assert witness is not None
    assert evaluate(transformed, witness)
    lifted = map_assignment(witness, transformed_to_original)
    assert evaluate(original, lifted)
    returned = map_assignment(lifted, inverse)
    assert returned == witness
    assert evaluate(transformed, returned)

    print("BH_Q2_SIGNED_EXACT_REPLAY = PASS")
    print("BH_Q2_BUZZ_WITNESS_LIFT_AND_RETURN = PASS")


def frozen_q1_equivalence_test() -> None:
    total_q1_states = 0
    total_q2_states = 0
    total_flip_absorptions = 0
    total_buzz_checks = 0
    total_buzz_passes = 0
    total_escapes = 0

    for order in range(3, 10):
        cnf, variable_count = graph_tautology_cnf(order)
        q1 = Policy0AQ1Lazy().solve(cnf, variable_count)
        q2 = Policy0ABHQ2().solve(cnf, variable_count)

        assert q2.answer == q1.answer, (order, q1.answer, q2.answer)
        assert q2.cap_exceeded == q1.cap_exceeded, order
        assert q2.residual_states <= q1.residual_states, (
            order,
            q1.residual_states,
            q2.residual_states,
        )
        assert q2.buzz_return_passes <= q2.buzz_return_checks
        assert q2.hawking_escape_count >= 0

        total_q1_states += q1.residual_states
        total_q2_states += q2.residual_states
        total_flip_absorptions += q2.polarity_flip_absorptions
        total_buzz_checks += q2.buzz_return_checks
        total_buzz_passes += q2.buzz_return_passes
        total_escapes += q2.hawking_escape_count

        print(
            "GT%d Q1_states=%d Q2_states=%d singularities=%d flip_absorptions=%d buzz=%d/%d escapes=%d"
            % (
                order,
                q1.residual_states,
                q2.residual_states,
                q2.singularity_entries,
                q2.polarity_flip_absorptions,
                q2.buzz_return_passes,
                q2.buzz_return_checks,
                q2.hawking_escape_count,
            )
        )

    print("BH_Q2_Q1_FROZEN_CALIBRATION_BOOLEAN_EQUIVALENCE = PASS")
    print("BH_Q2_STATES_NOT_GREATER_THAN_Q1 = PASS")
    print("TOTAL_Q1_STATES = %d" % total_q1_states)
    print("TOTAL_Q2_STATES = %d" % total_q2_states)
    print("TOTAL_POLARITY_FLIP_ABSORPTIONS = %d" % total_flip_absorptions)
    print("TOTAL_BUZZ_RETURN_CHECKS = %d" % total_buzz_checks)
    print("TOTAL_BUZZ_RETURN_PASSES = %d" % total_buzz_passes)
    print("TOTAL_HAWKING_ESCAPES = %d" % total_escapes)
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    signed_witness_roundtrip_test()
    frozen_q1_equivalence_test()
