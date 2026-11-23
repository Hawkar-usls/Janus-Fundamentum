#!/usr/bin/env python3
"""Persistent-phosphor analog-memory control for the JANUS Exact-One study.

No physical experiment, quantum simulation, or NP oracle is claimed.
The model assumes independent, non-interacting trap populations with
first-order exponential release. Its role is to falsify an unjustified
inference from "many parallel phosphor traps" to an Exact-One solver.

Run: python experiments/direct/pla_glow_trap_memory_probe.py --self-test
"""
from __future__ import annotations

import argparse
import json
from math import exp

from ramanujan_mock_theta_exactone_probe import (
    circulant_rows,
    exact_partition,
    validate_square_cubic_linear,
)


# Illustrative parameters, not fitted experimental values. Units: seconds^-1.
RATES = (1.0 / 15.0, 1.0 / 90.0, 1.0 / 480.0)
WEIGHTS = (0.5, 0.3, 0.2)
TIMES_SECONDS = (0, 10, 30, 60, 120, 300)


def local_intensity(exposure: float, time_seconds: float) -> float:
    """Ideal intensity from independent trapped excitations at one site."""
    if exposure < 0 or time_seconds < 0:
        raise ValueError("Excitation and readout times must be nonnegative")
    return exposure * sum(
        w * rate * exp(-rate * time_seconds)
        for w, rate in zip(WEIGHTS, RATES)
    )


def spatial_afterglow(exposures: tuple[float, ...], time_seconds: float) -> tuple[float, ...]:
    return tuple(local_intensity(pump, time_seconds) for pump in exposures)


def integrated_afterglow(exposures: tuple[float, ...], time_seconds: float) -> float:
    """A single photodiode measurement: no spatial readout."""
    return sum(spatial_afterglow(exposures, time_seconds))


def run_controls() -> dict:
    # These fixtures have equal size/degree/cycle rank but different SAT status.
    # They also have different GF(2) ranks; existing affine algebra distinguishes them.
    n = 12
    unsat_rows = circulant_rows(n, (0, 1, 3))
    sat_rows = circulant_rows(n, (0, 1, 5))
    for rows in (unsat_rows, sat_rows):
        validate_square_cubic_linear(rows, n)
    _, unsat_solutions = exact_partition(unsat_rows, n)
    _, sat_solutions = exact_partition(sat_rows, n)
    assert len(unsat_solutions) == 0
    assert len(sat_solutions) == 3

    same_uniform_pump = tuple(1.0 for _ in range(n))
    # No mathematical constraints are encoded into trap interactions in this
    # null model. Therefore BOTH instances have the same afterglow.
    null_sat = [integrated_afterglow(same_uniform_pump, t) for t in TIMES_SECONDS]
    null_unsat = [integrated_afterglow(same_uniform_pump, t) for t in TIMES_SECONDS]
    assert null_sat == null_unsat
    assert all(a > b > 0 for a, b in zip(null_sat, null_sat[1:]))

    # The model retains a spatial memory of the pump pattern.
    left_half = tuple(1.0 if k < 6 else 0.0 for k in range(n))
    right_half = tuple(0.0 if k < 6 else 1.0 for k in range(n))
    assert spatial_afterglow(left_half, 30) != spatial_afterglow(right_half, 30)

    # But a single integrated sensor cannot distinguish equal-total-dose
    # patterns with identical local rate spectra.
    for t in TIMES_SECONDS:
        assert abs(integrated_afterglow(left_half, t)
                   - integrated_afterglow(right_half, t)) < 1e-12

    assert all(
        spatial_afterglow(left_half, t)[0] >
        spatial_afterglow(left_half, t)[6]
        for t in TIMES_SECONDS
    )

    return {
        "status": "IDEALIZED_NULL_MODEL_NOT_PHYSICAL_MEASUREMENT",
        "equation": "I_i(t) = pump_i * sum_j weight_j*rate_j*exp(-rate_j*t)",
        "times_seconds": list(TIMES_SECONDS),
        "illustrative_decay_rates_per_second": list(RATES),
        "trap_weights": list(WEIGHTS),
        "sat_count_fixture": len(sat_solutions),
        "unsat_count_fixture": len(unsat_solutions),
        "uniform_pump_integrated_intensity": null_sat,
        "uniform_pump_readout_collision": null_sat == null_unsat,
        "different_spatial_pump_patterns_retained": True,
        "same_total_dose_integrated_readout_collision": True,
        "claim_boundary": (
            "Passive independent traps act as fading optical memory, "
            "not as Exact-One constraint evaluators. Other coupled "
            "physical architectures require independent analysis."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_controls()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS: independent-trap readout cannot distinguish equal-dose SAT and UNSAT controls")
        print("PASS: spatial optical memory, aggregate-sensor collision, monotone decay")
        print("NOTE: idealized parameters, not measured PLA Glow behavior")


if __name__ == "__main__":
    main()
