"""C023 proof-carrying mixed affine/Horn solver."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from janus_c023_primitives import *
from janus_c023_affine import *
from janus_c023_basis import *

# ---------------------------------------------------------------------------
# Honest mixed-language solver
# ---------------------------------------------------------------------------

@dataclass
class MixedStats:
    propagation_rounds: int = 0
    horn_probe_calls: int = 0
    horn_rule_scans: int = 0
    horn_probe_certificates: int = 0
    horn_probe_certificate_steps: int = 0
    affine_solves: int = 0
    affine_row_operations: int = 0
    forced_by_horn: int = 0
    forced_by_affine: int = 0
    dimension_before_propagation: int | None = None
    dimension_after_propagation: int | None = None
    quotient_states: int = 0
    state_horn_calls: int = 0
    state_horn_rule_scans: int = 0
    state_unsat_certificates: int = 0
    witness_checks: int = 0
    basis_rewrite_attempted: int = 0
    basis_rewrite_supported: int = 0
    basis_rewrite_target: str | None = None
    basis_rewrite_solver_steps: int = 0
    basis_rewrite_solved: int = 0


@dataclass
class MixedResult:
    status: str
    sat: bool | None
    witness: dict[int, bool] | None
    fixed: dict[int, bool]
    stats: MixedStats
    reason: str
    quotient_dimension: int | None


def horn_forced_values(
    formula: CNF,
    interface: list[int],
    fixed: dict[int, bool],
    stats: MixedStats,
) -> tuple[dict[int, bool], bool]:
    base = horn_solve(formula, fixed)
    stats.horn_probe_calls += 1
    stats.horn_rule_scans += base.rule_scans
    if not base.sat:
        stats.horn_probe_certificates += 1
        assert base.certificate is not None
        stats.horn_probe_certificate_steps += len(base.certificate.fired_rules) + 1
        return {}, True

    forced: dict[int, bool] = {}
    for v in interface:
        if v in fixed:
            continue
        low = horn_solve(formula, {**fixed, v: False})
        high = horn_solve(formula, {**fixed, v: True})
        stats.horn_probe_calls += 2
        stats.horn_rule_scans += low.rule_scans + high.rule_scans
        for result in (low, high):
            if not result.sat:
                stats.horn_probe_certificates += 1
                assert result.certificate is not None
                stats.horn_probe_certificate_steps += len(result.certificate.fired_rules) + 1

        if not low.sat and not high.sat:
            return {}, True
        if not low.sat:
            forced[v] = True
        elif not high.sat:
            forced[v] = False
    return forced, False


def mixed_affine_horn_solve(
    equations: list[Equation],
    horn: CNF,
    interface: list[int],
    affine_universe: list[int],
    state_budget: int,
) -> MixedResult:
    if not is_horn(horn):
        raise ValueError("Horn module failed syntactic gate")
    interface = sorted(set(interface))
    affine_universe = sorted(set(affine_universe) | set(interface))
    stats = MixedStats()
    fixed: dict[int, bool] = {}

    initial = affine_solve(equations, affine_universe, fixed)
    stats.affine_solves += 1
    stats.affine_row_operations += initial.row_operations
    if not initial.consistent:
        if not verify_affine_conflict(equations, fixed, initial):
            raise AssertionError("affine conflict certificate failed")
        return MixedResult(
            "EXACT", False, None, fixed, stats,
            "AFFINE_CONTRADICTION", None,
        )
    stats.dimension_before_propagation = project_affine(initial, interface).dimension

    while True:
        stats.propagation_rounds += 1
        changed = False

        affine = affine_solve(equations, affine_universe, fixed)
        stats.affine_solves += 1
        stats.affine_row_operations += affine.row_operations
        if not affine.consistent:
            if not verify_affine_conflict(equations, fixed, affine):
                raise AssertionError("affine conflict certificate failed")
            return MixedResult(
                "EXACT", False, None, fixed, stats,
                "AFFINE_CONTRADICTION_AFTER_PROPAGATION", None,
            )

        for v, value in affine_forced_values(affine, interface).items():
            if v not in fixed:
                fixed[v] = value
                stats.forced_by_affine += 1
                changed = True
            elif fixed[v] != value:
                raise AssertionError("inconsistent affine forced values")

        horn_forced, horn_conflict = horn_forced_values(horn, interface, fixed, stats)
        if horn_conflict:
            return MixedResult(
                "EXACT", False, None, fixed, stats,
                "HORN_CONTRADICTION_DURING_PROPAGATION", None,
            )
        for v, value in horn_forced.items():
            if v not in fixed:
                fixed[v] = value
                stats.forced_by_horn += 1
                changed = True
            elif fixed[v] != value:
                fixed[v] = value
                changed = True

        if not changed:
            break

    affine = affine_solve(equations, affine_universe, fixed)
    stats.affine_solves += 1
    stats.affine_row_operations += affine.row_operations
    if not affine.consistent:
        if not verify_affine_conflict(equations, fixed, affine):
            raise AssertionError("affine conflict certificate failed")
        return MixedResult(
            "EXACT", False, None, fixed, stats,
            "AFFINE_CONTRADICTION_AT_QUOTIENT", None,
        )

    remaining_interface = [v for v in interface if v not in fixed]
    projected = project_affine(affine, remaining_interface)
    d = projected.dimension
    stats.dimension_after_propagation = d

    stats.basis_rewrite_attempted += 1
    basis_result = rewrite_horn_over_affine_basis(
        horn, fixed, affine, projected, remaining_interface
    )
    if basis_result.supported:
        stats.basis_rewrite_supported += 1
        stats.basis_rewrite_target = basis_result.target_language
        stats.basis_rewrite_solver_steps += basis_result.solver_steps
        stats.basis_rewrite_solved += 1
        if not basis_result.sat:
            return MixedResult(
                "EXACT", False, None, fixed, stats,
                f"BASIS_LANGUAGE_UNSAT:{basis_result.target_language}", d,
            )
        witness = recover_basis_witness(
            basis_result, affine, projected, remaining_interface
        )
        assert witness is not None
        for v, value in fixed.items():
            witness[v] = value
        stats.witness_checks += 1
        if not satisfies_affine(equations, witness):
            raise AssertionError("basis witness failed affine module")
        if not satisfies_cnf(horn, witness):
            raise AssertionError("basis witness failed Horn module")
        return MixedResult(
            "EXACT", True, witness, fixed, stats,
            f"BASIS_LANGUAGE_SAT:{basis_result.target_language}", d,
        )

    required_states = 1 << d
    if required_states > state_budget:
        return MixedResult(
            "OPEN", None, None, fixed, stats,
            f"QUOTIENT_STATE_BUDGET_EXCEEDED:{required_states}>{state_budget}",
            d,
        )

    for selector in range(required_states):
        stats.quotient_states += 1
        full_mask = projected.particular_full_mask
        for i, direction in enumerate(projected.direction_full_masks):
            if (selector >> i) & 1:
                full_mask ^= direction

        affine_assignment = affine.assignment_from_mask(full_mask)
        interface_assignment = {v: affine_assignment[v] for v in interface}
        horn_result = horn_solve(horn, interface_assignment)
        stats.state_horn_calls += 1
        stats.state_horn_rule_scans += horn_result.rule_scans

        if not horn_result.sat:
            stats.state_unsat_certificates += 1
            assert horn_result.certificate is not None
            if not verify_horn_certificate(horn, horn_result.certificate):
                raise AssertionError("state Horn certificate failed")
            continue

        assert horn_result.assignment is not None
        witness = dict(affine_assignment)
        for v, value in horn_result.assignment.items():
            if v in witness and witness[v] != value:
                raise AssertionError("interface witness mismatch")
            witness[v] = value
        stats.witness_checks += 1
        if not satisfies_affine(equations, witness):
            raise AssertionError("mixed witness failed affine module")
        if not satisfies_cnf(horn, witness):
            raise AssertionError("mixed witness failed Horn module")
        return MixedResult(
            "EXACT", True, witness, fixed, stats,
            "SAT_WITNESS", d,
        )

    return MixedResult(
        "EXACT", False, None, fixed, stats,
        "ALL_AFFINE_QUOTIENT_STATES_HAVE_HORN_TEARS", d,
    )

