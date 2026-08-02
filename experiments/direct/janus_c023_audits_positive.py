"""C023 positive and exact mixed-interface audits."""
from __future__ import annotations
import random
from typing import Any
from janus_c023_primitives import *
from janus_c023_affine import *
from janus_c023_basis import *
from janus_c023_solver import *
from janus_c023_generators import *

def audit_small_exact_fuzz(rng: random.Random, cases: int = 300) -> dict[str, Any]:
    mismatches = 0
    false_accepts = 0
    open_count = 0
    sat_count = 0
    unsat_count = 0
    max_dimension = 0
    total_states = 0
    total_bruteforce = 0

    for _ in range(cases):
        k = rng.randint(2, 6)
        ap = rng.randint(0, 2)
        hp = rng.randint(0, 2)
        interface = list(range(1, k + 1))
        affine_private = list(range(k + 1, k + ap + 1))
        horn_private = list(range(k + ap + 1, k + ap + hp + 1))
        affine_universe = interface + affine_private
        all_vars = affine_universe + horn_private

        equations = random_affine_equations(
            rng, affine_universe, rng.randint(0, max(1, 2 * len(affine_universe)))
        )
        horn_vars = interface + horn_private
        horn = canonical_cnf(
            random_horn_clause(rng, horn_vars)
            for _ in range(rng.randint(0, max(1, 3 * len(horn_vars))))
        )

        result = mixed_affine_horn_solve(
            equations, horn, interface, affine_universe, state_budget=1 << k
        )
        truth, witness, checks = brute_force_mixed(equations, horn, all_vars)
        total_bruteforce += checks
        total_states += result.stats.quotient_states
        if result.status == "OPEN":
            open_count += 1
            continue
        if result.sat != truth:
            mismatches += 1
        if result.sat:
            sat_count += 1
            if (
                result.witness is None
                or not satisfies_affine(equations, result.witness)
                or not satisfies_cnf(horn, result.witness)
            ):
                false_accepts += 1
        else:
            unsat_count += 1
        if result.quotient_dimension is not None:
            max_dimension = max(max_dimension, result.quotient_dimension)

    return {
        "cases": cases,
        "sat": sat_count,
        "unsat": unsat_count,
        "open": open_count,
        "mismatches": mismatches,
        "false_accepts": false_accepts,
        "max_quotient_dimension": max_dimension,
        "total_quotient_states": total_states,
        "total_bruteforce_assignments_checked": total_bruteforce,
    }


def low_dimension_affine_fixture(
    rng: random.Random,
    k: int,
    d: int,
    unsat: bool,
) -> tuple[list[Equation], CNF, list[int], list[int]]:
    interface = list(range(1, k + 1))
    equations: list[Equation] = []
    groups = [[] for _ in range(d)]
    for i, v in enumerate(interface):
        groups[i % d].append(v)

    planted = {v: bool(rng.getrandbits(1)) for v in interface}
    for group in groups:
        leader = group[0]
        for v in group[1:]:
            equations.append(((leader, v), int(planted[leader] ^ planted[v])))

    horn_private = list(range(k + 1, k + 5))
    horn_vars = interface + horn_private
    full_planted = dict(planted)
    full_planted.update({v: bool(rng.getrandbits(1)) for v in horn_private})

    clauses: list[Clause] = []
    for _ in range(2 * k):
        for _attempt in range(100):
            clause = random_horn_clause(rng, horn_vars)
            if any(full_planted[abs(lit)] == (lit > 0) for lit in clause):
                clauses.append(clause)
                break
        else:
            raise RuntimeError("failed to sample planted Horn clause")

    if unsat:
        equations.append(((1,), int(planted[1])))
        clauses.append((1 if not planted[1] else -1,))

    horn = canonical_cnf(clauses)
    assert is_horn(horn)
    if not unsat:
        assert satisfies_affine(equations, full_planted)
        assert satisfies_cnf(horn, full_planted)
    return equations, horn, interface, interface


def audit_wide_low_dimension(rng: random.Random, cases: int = 120) -> dict[str, Any]:
    sat = 0
    unsat = 0
    failures = 0
    total_raw_log2 = 0
    total_states = 0
    max_k = 0
    max_d = 0
    rows = []

    sizes = [20, 32, 48, 64]
    for i in range(cases):
        k = sizes[i % len(sizes)]
        d = 2 + (i % 5)
        is_unsat = (i % 4 == 3)
        equations, horn, interface, affine_universe = low_dimension_affine_fixture(
            rng, k, d, is_unsat
        )
        result = mixed_affine_horn_solve(
            equations, horn, interface, affine_universe, state_budget=128
        )
        if result.status != "EXACT" or result.sat == is_unsat:
            failures += 1
        elif result.sat:
            sat += 1
        else:
            unsat += 1
        total_raw_log2 += k
        total_states += result.stats.quotient_states
        max_k = max(max_k, k)
        max_d = max(max_d, result.quotient_dimension or 0)
        if i < 20:
            rows.append({
                "interface_variables": k,
                "raw_assignments": str(1 << k),
                "quotient_dimension": result.quotient_dimension,
                "states_examined": result.stats.quotient_states,
                "status": result.status,
                "sat": result.sat,
                "forced_by_horn": result.stats.forced_by_horn,
                "forced_by_affine": result.stats.forced_by_affine,
            })

    return {
        "cases": cases,
        "sat": sat,
        "unsat": unsat,
        "failures": failures,
        "max_interface_variables": max_k,
        "max_quotient_dimension": max_d,
        "total_quotient_states": total_states,
        "sum_log2_raw_interface_states": total_raw_log2,
        "rows": rows,
        "interpretation": (
            "Wide interfaces are tractable when affine projection leaves only "
            "a logarithmic/constant number of semantic degrees of freedom."
        ),
    }


def audit_forced_value_exchange() -> dict[str, Any]:
    k = 48
    interface = list(range(1, k + 1))
    equations: list[Equation] = [((1, v), 0) for v in range(2, k + 1)]
    horn = canonical_cnf([(1,)])
    result = mixed_affine_horn_solve(
        equations, horn, interface, interface, state_budget=4
    )
    return {
        "interface_variables": k,
        "dimension_before": result.stats.dimension_before_propagation,
        "dimension_after": result.stats.dimension_after_propagation,
        "forced_by_horn": result.stats.forced_by_horn,
        "forced_by_affine": result.stats.forced_by_affine,
        "quotient_states": result.stats.quotient_states,
        "status": result.status,
        "sat": result.sat,
        "witness_valid": (
            result.witness is not None
            and satisfies_affine(equations, result.witness)
            and satisfies_cnf(horn, result.witness)
        ),
    }

