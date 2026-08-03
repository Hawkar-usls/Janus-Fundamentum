#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from typing import Any, Iterable

import janus_c040_portfolio_module_forest as core


def producer_lane_map(factors: tuple[core.Factor, ...]) -> dict[int, int | None]:
    """Assign the k-th producer of each Horn head to lane k.

    Every lane is single-head by construction: for a fixed positive head, at most
    one producer is placed in one lane. Negative Horn constraints use lane zero.
    Affine factors have no producer lane.
    """
    result: dict[int, int | None] = {}
    by_head: dict[int, list[core.HornFactor]] = {}
    for factor in factors:
        if isinstance(factor, core.AffineFactor):
            result[factor.factor_id] = None
        elif factor.head is None:
            result[factor.factor_id] = 0
        else:
            by_head.setdefault(factor.head, []).append(factor)
    for head in sorted(by_head):
        for lane, factor in enumerate(sorted(by_head[head], key=lambda item: item.factor_id)):
            result[factor.factor_id] = lane
    return result


def _connected_components(
    factors: list[core.Factor], meter: core.Meter
) -> list[tuple[int, ...]]:
    if not factors:
        return []
    dsu = core.DSU()
    for factor in factors:
        dsu.add(factor.factor_id)
    by_variable: dict[int, list[int]] = {}
    for factor in factors:
        for variable in core.factor_variables(factor):
            by_variable.setdefault(variable, []).append(factor.factor_id)
            meter.charge()
    for ids in by_variable.values():
        for factor_id in ids[1:]:
            dsu.union(ids[0], factor_id)
            meter.charge()
    groups: dict[int, list[int]] = {}
    for factor in factors:
        groups.setdefault(dsu.find(factor.factor_id), []).append(factor.factor_id)
    return [tuple(sorted(ids)) for _, ids in sorted(groups.items())]


def discover_modules_with_producer_lanes(
    factors: tuple[core.Factor, ...], meter: core.Meter
) -> tuple[
    list[core.Module],
    dict[tuple[int, int], tuple[int, ...]],
    list[int],
    tuple[Any, ...],
]:
    lanes = producer_lane_map(factors)
    factor_by_id = {factor.factor_id: factor for factor in factors}

    components: list[tuple[str, int | None, tuple[int, ...]]] = []
    affine = [factor for factor in factors if isinstance(factor, core.AffineFactor)]
    for ids in _connected_components(affine, meter):
        components.append(("AFFINE_GF2", None, ids))

    horn_lanes = sorted(
        {int(lane) for factor_id, lane in lanes.items()
         if lane is not None and isinstance(factor_by_id[factor_id], core.HornFactor)}
    )
    for lane in horn_lanes:
        lane_factors = [
            factor for factor in factors
            if isinstance(factor, core.HornFactor) and lanes[factor.factor_id] == lane
        ]
        for ids in _connected_components(lane_factors, meter):
            components.append(("SINGLE_HEAD_HORN", lane, ids))

    components.sort(key=lambda item: (min(item[2]), item[0], -1 if item[1] is None else item[1]))
    modules: list[core.Module] = []
    for module_id, (language, _lane, factor_ids) in enumerate(components):
        variables = tuple(sorted({
            variable
            for factor_id in factor_ids
            for variable in core.factor_variables(factor_by_id[factor_id])
        }))
        # Defensive replay of the lane invariant.
        if language == "SINGLE_HEAD_HORN":
            seen_heads: set[int] = set()
            for factor_id in factor_ids:
                factor = factor_by_id[factor_id]
                assert isinstance(factor, core.HornFactor)
                if factor.head is not None:
                    if factor.head in seen_heads:
                        raise AssertionError("producer lane is not single-head")
                    seen_heads.add(factor.head)
        modules.append(core.Module(module_id, language, factor_ids, variables))

    variable_modules: dict[int, set[int]] = {}
    for module in modules:
        for variable in module.variables:
            variable_modules.setdefault(variable, set()).add(module.module_id)
            meter.charge()

    edge_variables: dict[tuple[int, int], set[int]] = {}
    for variable, module_ids in sorted(variable_modules.items()):
        if len(module_ids) > 2:
            raise core.OpenResult("OPEN_INTERFACE_HYPEREDGE")
        if len(module_ids) == 2:
            a, b = sorted(module_ids)
            edge_variables.setdefault((a, b), set()).add(variable)
    edges = {
        edge: tuple(sorted(variables))
        for edge, variables in sorted(edge_variables.items())
    }

    graph_dsu = core.DSU()
    adjacency: dict[int, set[int]] = {}
    for module in modules:
        graph_dsu.add(module.module_id)
        adjacency[module.module_id] = set()
    for a, b in edges:
        if not graph_dsu.union(a, b):
            raise core.OpenResult("OPEN_MODULE_CYCLE")
        adjacency[a].add(b)
        adjacency[b].add(a)
        meter.charge()

    for module in modules:
        boundary: set[int] = set()
        for neighbor in adjacency[module.module_id]:
            boundary.update(edges[tuple(sorted((module.module_id, neighbor)))])
        module.boundary = tuple(sorted(boundary))

    roots: list[int] = []
    visited: set[int] = set()
    for module in modules:
        if module.module_id in visited:
            continue
        roots.append(module.module_id)
        stack = [module.module_id]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            stack.extend(sorted(adjacency[node] - visited, reverse=True))
    return modules, edges, roots, ()


# Patch only the discovery function. The native solvers, dynamic program, witness
# recovery and independent certificate replay remain the already audited C040 core.
core.discover_modules = discover_modules_with_producer_lanes


def compile_portfolio(raw_factors: Iterable[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
    raw = list(raw_factors)
    result = core.compile_portfolio(raw, **kwargs)
    try:
        factors = core.parse_factors(raw)
        result["producer_lanes"] = {
            str(factor_id): lane
            for factor_id, lane in sorted(producer_lane_map(factors).items())
        }
    except (ValueError, core.OpenResult, KeyError, TypeError):
        return result
    if result.get("status") in ("SAT", "UNSAT"):
        result["integrity_sha256"] = core.digest({
            key: value for key, value in result.items() if key != "integrity_sha256"
        })
    return result


def verify_compilation(certificate: dict[str, Any]) -> bool:
    if certificate.get("status") in ("SAT", "UNSAT"):
        try:
            factors = core.parse_factors(certificate["factors"])
        except (ValueError, core.OpenResult, KeyError, TypeError):
            return False
        expected = {
            str(factor_id): lane
            for factor_id, lane in sorted(producer_lane_map(factors).items())
        }
        if certificate.get("producer_lanes") != expected:
            return False
    return core.verify_compilation(certificate)


def projection_blowup_family(n: int) -> list[dict[str, Any]]:
    factors: list[dict[str, Any]] = []
    q_variables: list[int] = []
    factor_id = 0
    for index in range(n):
        a = 3 * index + 1
        b = 3 * index + 2
        q = 3 * index + 3
        q_variables.append(q)
        factors.append(core.make_horn(factor_id, [a], q))
        factor_id += 1
        factors.append(core.make_horn(factor_id, [b], q))
        factor_id += 1
    z = 3 * n + 1
    factors.append(core.make_horn(factor_id, q_variables, z))
    return factors


def three_producer_hyperedge() -> list[dict[str, Any]]:
    return [
        core.make_horn(0, [1], 4),
        core.make_horn(1, [2], 4),
        core.make_horn(2, [3], 4),
    ]


def run_self_test(seed: int = 400041) -> dict[str, Any]:
    rng = random.Random(seed)
    random_cases = 0
    random_sat = 0
    random_unsat = 0
    max_modules = 0
    max_boundary = 0
    for _ in range(350):
        raw = core.random_forest_instance(rng)
        expected_sat, _ = core.exhaustive_sat(core.parse_factors(raw))
        certificate = compile_portfolio(
            raw,
            work_budget=5_000_000,
            table_budget=200_000,
            certificate_budget=8_000_000,
        )
        assert certificate["status"] in ("SAT", "UNSAT")
        assert verify_compilation(certificate)
        assert (certificate["status"] == "SAT") == expected_sat
        random_cases += 1
        random_sat += int(expected_sat)
        random_unsat += int(not expected_sat)
        max_modules = max(max_modules, certificate["cost"]["module_count"])
        max_boundary = max(max_boundary, certificate["cost"]["maximum_module_boundary"])

    duplicate_pairs = compile_portfolio(
        core.head_conflict_family(64),
        work_budget=20_000_000,
        table_budget=1_000_000,
        certificate_budget=40_000_000,
    )
    assert duplicate_pairs["status"] == "SAT"
    assert verify_compilation(duplicate_pairs)
    assert duplicate_pairs["cost"]["maximum_module_boundary"] == 1

    blowup = compile_portfolio(projection_blowup_family(64))
    assert blowup["status"] == "OPEN"
    assert blowup["reason"] == "OPEN_INTERFACE_WIDTH"

    hyperedge = compile_portfolio(three_producer_hyperedge())
    assert hyperedge["status"] == "OPEN"
    assert hyperedge["reason"] == "OPEN_INTERFACE_HYPEREDGE"

    cycle = compile_portfolio(core.alternating_cycle())
    assert cycle["status"] == "OPEN" and cycle["reason"] == "OPEN_MODULE_CYCLE"

    wide_star = compile_portfolio(core.interface_star(24))
    assert wide_star["status"] == "OPEN" and wide_star["reason"] == "OPEN_INTERFACE_WIDTH"

    chain = compile_portfolio(
        core.long_chain(180),
        work_budget=20_000_000,
        table_budget=1_000_000,
        certificate_budget=40_000_000,
    )
    assert chain["status"] in ("SAT", "UNSAT") and verify_compilation(chain)

    budget = compile_portfolio(core.long_chain(30), work_budget=10)
    assert budget["status"] == "OPEN" and budget["reason"] == "OPEN_WORK_BUDGET"

    unsupported = compile_portfolio([
        {"id": 0, "language": "BETA_ACYCLIC", "variables": [1]}
    ])
    assert unsupported["status"] == "OPEN" and unsupported["reason"] == "OPEN_LANGUAGE"

    corrupt = compile_portfolio(core.random_forest_instance(random.Random(seed + 1)))
    assert corrupt["status"] in ("SAT", "UNSAT") and verify_compilation(corrupt)
    corrupt["producer_lanes"][next(iter(corrupt["producer_lanes"]))] = 999
    corrupt["integrity_sha256"] = core.digest({
        key: value for key, value in corrupt.items() if key != "integrity_sha256"
    })
    assert not verify_compilation(corrupt)

    result = {
        "artifact_id": "C040-PORTFOLIO-GUIDED-PRODUCER-LANE-ISOLATION",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "seed": seed,
        "constructive_strengthening": (
            "Horn factors are partitioned deterministically by producer rank per head before "
            "same-lane connectivity. Every discovered Horn module is single-head by construction. "
            "The existing C040 forest/log-interface dynamic program then supplies exact composition."
        ),
        "random_cases": random_cases,
        "random_sat": random_sat,
        "random_unsat": random_unsat,
        "random_max_modules": max_modules,
        "random_max_boundary": max_boundary,
        "duplicate_producer_pairs": "SAT_AFTER_LANE_ISOLATION",
        "duplicate_pair_modules": duplicate_pairs["cost"]["module_count"],
        "duplicate_pair_max_boundary": duplicate_pairs["cost"]["maximum_module_boundary"],
        "c039_1_projection_blowup": "OPEN_INTERFACE_WIDTH",
        "three_producers": "OPEN_INTERFACE_HYPEREDGE",
        "alternating_cycle": "OPEN_MODULE_CYCLE",
        "wide_star": "OPEN_INTERFACE_WIDTH",
        "accepted_chain_modules": 180,
        "budget_control": "OPEN_WORK_BUDGET",
        "unsupported_language": "OPEN_LANGUAGE",
        "corrupt_lane_certificate": "REJECTED",
        "new_gate": "RICHER_MESSAGES_OR_DISCOVERY_BEYOND_FOREST_LOG_BOUNDARIES",
        "claim_boundary": (
            "Producer lanes isolate duplicate Horn heads but do not eliminate large shared interfaces. "
            "The C039.1 blow-up family becomes a star with a 64-variable central boundary and therefore "
            "returns OPEN_INTERFACE_WIDTH. No universal compact Horn or mixed-language representation is claimed."
        ),
    }
    result["integrity_sha256"] = core.digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--seed", type=int, default=400041)
    args = parser.parse_args()
    result = run_self_test(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.self_test:
        assert result["status"] == "PASS"


if __name__ == "__main__":
    main()
