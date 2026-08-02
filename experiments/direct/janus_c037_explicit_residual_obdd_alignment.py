#!/usr/bin/env python3
"""
C037 JANUS explicit residual automaton / OBDD alignment.

For a fixed variable order, this artifact builds the explicit DAG of exact CNF
residuals reachable by prefix assignments, then computes the coarsest
continuation-equivalence partition bottom-up.

Every transition is replayed by exact restriction. Every pair of distinct
quotient states receives an explicit suffix assignment that distinguishes their
continuation behavior. Equal quotient states are justified inductively by equal
pairs of child classes.

The resulting quotient is exactly the reduced ordered binary decision diagram
for the chosen order. The procedure is polynomial in the explicit reachable
state graph and certificate volume, but that graph can be exponential in the
source formula. The implementation therefore returns OPEN on explicit budgets.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from collections import defaultdict
from dataclasses import dataclass

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Assignment = dict[int, bool]

TRUE: CNF = tuple()
FALSE: CNF = (tuple(),)


def canon_clause(clause: Clause):
    literals = set(clause)
    if any(-lit in literals for lit in literals):
        return None
    return tuple(sorted(literals, key=lambda lit: (abs(lit), lit < 0)))


def normalize_cnf(formula: CNF) -> CNF:
    clauses = []
    for clause in formula:
        canonical = canon_clause(clause)
        if canonical is not None:
            clauses.append(canonical)
    clauses = sorted(set(clauses), key=lambda clause: (len(clause), clause))

    kept = []
    for clause in clauses:
        current = set(clause)
        if any(set(previous) <= current for previous in kept):
            continue
        kept.append(clause)
    return tuple(kept)


def variables(formula: CNF) -> list[int]:
    return sorted({abs(literal) for clause in formula for literal in clause})


def restrict_cnf(formula: CNF, assignment: Assignment) -> CNF:
    residual = []
    for clause in formula:
        satisfied = False
        remaining = []
        for literal in clause:
            variable = abs(literal)
            if variable in assignment:
                if assignment[variable] == (literal > 0):
                    satisfied = True
                    break
            else:
                remaining.append(literal)
        if not satisfied:
            residual.append(tuple(remaining))
    return normalize_cnf(tuple(residual))


def evaluate(formula: CNF, assignment: Assignment) -> bool:
    return all(
        any(assignment.get(abs(literal), False) == (literal > 0)
            for literal in clause)
        for clause in formula
    )


def terminal_label(residual: CNF):
    if residual == TRUE:
        return True
    if residual == FALSE:
        return False
    return None


@dataclass
class ExplicitGraph:
    status: str
    formula: CNF
    order: tuple[int, ...]
    layers: list[set[CNF]]
    transitions: dict[tuple[int, CNF, bool], CNF]
    state_count: int
    max_width: int
    reason: str | None


@dataclass
class QuotientPackage:
    status: str
    graph: ExplicitGraph
    class_of: list[dict[CNF, int]]
    representatives: list[dict[int, CNF]]
    separators: list[tuple[int, int, int, tuple[bool, ...], bool, bool]]
    sat: bool | None
    witness: Assignment | None
    quotient_nodes: int
    max_quotient_width: int
    separator_volume: int
    reason: str | None


def build_explicit_graph(
    formula: CNF,
    order: tuple[int, ...],
    state_budget: int,
) -> ExplicitGraph:
    formula = normalize_cnf(formula)
    if not set(variables(formula)) <= set(order):
        raise ValueError("variable order must contain every formula variable")

    layers = [{formula}]
    transitions: dict[tuple[int, CNF, bool], CNF] = {}

    for depth, variable in enumerate(order):
        next_layer: set[CNF] = set()
        for state in layers[-1]:
            for value in (False, True):
                child = restrict_cnf(state, {variable: value})
                transitions[(depth, state, value)] = child
                next_layer.add(child)

        projected_count = sum(len(layer) for layer in layers) + len(next_layer)
        if projected_count > state_budget:
            return ExplicitGraph(
                "OPEN",
                formula,
                order,
                layers,
                transitions,
                sum(len(layer) for layer in layers),
                max(len(layer) for layer in layers),
                "STATE_BUDGET",
            )
        layers.append(next_layer)

    return ExplicitGraph(
        "EXACT",
        formula,
        order,
        layers,
        transitions,
        sum(len(layer) for layer in layers),
        max(len(layer) for layer in layers),
        None,
    )


def minimize_layered(graph: ExplicitGraph):
    """Compute exact continuation classes for the explicit layered DAG."""
    if graph.status != "EXACT":
        raise ValueError("cannot minimize an OPEN graph")

    depth_count = len(graph.order)
    class_of: list[dict[CNF, int]] = [
        {} for _ in range(depth_count + 1)
    ]
    representatives: list[dict[int, CNF]] = [
        {} for _ in range(depth_count + 1)
    ]

    terminal_buckets: dict[tuple[str, bool], list[CNF]] = defaultdict(list)
    for state in graph.layers[depth_count]:
        label = terminal_label(state)
        if label is None:
            raise AssertionError("all variables were assigned but residual is nonterminal")
        terminal_buckets[("TERMINAL", label)].append(state)

    for class_id, (_, states) in enumerate(
        sorted(terminal_buckets.items(), key=lambda item: repr(item[0]))
    ):
        for state in states:
            class_of[depth_count][state] = class_id
        representatives[depth_count][class_id] = states[0]

    for depth in range(depth_count - 1, -1, -1):
        buckets: dict[tuple[int, int], list[CNF]] = defaultdict(list)
        for state in graph.layers[depth]:
            zero_child = graph.transitions[(depth, state, False)]
            one_child = graph.transitions[(depth, state, True)]
            signature = (
                class_of[depth + 1][zero_child],
                class_of[depth + 1][one_child],
            )
            buckets[signature].append(state)

        for class_id, (_, states) in enumerate(sorted(buckets.items())):
            for state in states:
                class_of[depth][state] = class_id
            representatives[depth][class_id] = states[0]

    return class_of, representatives


def class_separator(
    graph: ExplicitGraph,
    class_of: list[dict[CNF, int]],
    representatives: list[dict[int, CNF]],
    depth: int,
    class_a: int,
    class_b: int,
) -> tuple[bool, ...]:
    """Return an explicit continuation distinguishing two quotient classes."""
    if class_a == class_b:
        raise ValueError("equal classes have no separating continuation")

    final_depth = len(graph.order)
    state_a = representatives[depth][class_a]
    state_b = representatives[depth][class_b]

    if depth == final_depth:
        label_a = terminal_label(state_a)
        label_b = terminal_label(state_b)
        if label_a == label_b:
            raise AssertionError("distinct final classes must have distinct labels")
        return tuple()

    for value in (False, True):
        child_a = graph.transitions[(depth, state_a, value)]
        child_b = graph.transitions[(depth, state_b, value)]
        child_class_a = class_of[depth + 1][child_a]
        child_class_b = class_of[depth + 1][child_b]
        if child_class_a != child_class_b:
            return (value,) + class_separator(
                graph,
                class_of,
                representatives,
                depth + 1,
                child_class_a,
                child_class_b,
            )

    raise AssertionError("distinct classes have identical child signatures")


def evaluate_suffix(
    residual: CNF,
    order: tuple[int, ...],
    depth: int,
    suffix: tuple[bool, ...],
) -> bool:
    assignment = {
        order[depth + index]: value
        for index, value in enumerate(suffix)
    }
    terminal = restrict_cnf(residual, assignment)
    label = terminal_label(terminal)
    if label is None:
        raise AssertionError("separator does not assign the full suffix")
    return label


def recover_sat_witness(
    graph: ExplicitGraph,
    class_of: list[dict[CNF, int]],
    representatives: list[dict[int, CNF]],
):
    final_depth = len(graph.order)
    can_accept: list[dict[int, bool]] = [
        {} for _ in range(final_depth + 1)
    ]
    choice: dict[tuple[int, int], tuple[bool, int]] = {}

    for class_id, state in representatives[final_depth].items():
        can_accept[final_depth][class_id] = bool(terminal_label(state))

    for depth in range(final_depth - 1, -1, -1):
        for class_id, state in representatives[depth].items():
            selected = None
            for value in (False, True):
                child = graph.transitions[(depth, state, value)]
                child_class = class_of[depth + 1][child]
                if can_accept[depth + 1][child_class]:
                    selected = (value, child_class)
                    break
            can_accept[depth][class_id] = selected is not None
            if selected is not None:
                choice[(depth, class_id)] = selected

    root = next(iter(graph.layers[0]))
    root_class = class_of[0][root]
    if not can_accept[0][root_class]:
        return False, None

    assignment: Assignment = {}
    current_class = root_class
    for depth, variable in enumerate(graph.order):
        value, current_class = choice[(depth, current_class)]
        assignment[variable] = value

    if not evaluate(graph.formula, assignment):
        raise AssertionError("recovered witness does not satisfy the source formula")
    return True, assignment


def compile_quotient(
    formula: CNF,
    order: list[int] | tuple[int, ...],
    state_budget: int = 100_000,
    separator_budget: int = 1_000_000,
) -> QuotientPackage:
    graph = build_explicit_graph(
        formula,
        tuple(order),
        state_budget,
    )
    if graph.status != "EXACT":
        return QuotientPackage(
            "OPEN", graph, [], [], [], None, None, 0, 0, 0, graph.reason
        )

    class_of, representatives = minimize_layered(graph)
    separators = []
    separator_volume = 0

    for depth in range(len(graph.order) + 1):
        class_ids = sorted(representatives[depth])
        for left_index, class_a in enumerate(class_ids):
            for class_b in class_ids[left_index + 1:]:
                suffix = class_separator(
                    graph,
                    class_of,
                    representatives,
                    depth,
                    class_a,
                    class_b,
                )
                state_a = representatives[depth][class_a]
                state_b = representatives[depth][class_b]
                label_a = evaluate_suffix(state_a, graph.order, depth, suffix)
                label_b = evaluate_suffix(state_b, graph.order, depth, suffix)
                if label_a == label_b:
                    raise AssertionError("invalid separating continuation")

                separator_volume += 1 + len(suffix)
                if separator_volume > separator_budget:
                    return QuotientPackage(
                        "OPEN",
                        graph,
                        class_of,
                        representatives,
                        separators,
                        None,
                        None,
                        sum(len(level) for level in representatives),
                        max(len(level) for level in representatives),
                        separator_volume,
                        "SEPARATOR_BUDGET",
                    )

                separators.append(
                    (depth, class_a, class_b, suffix, label_a, label_b)
                )

    sat, witness = recover_sat_witness(graph, class_of, representatives)
    return QuotientPackage(
        "EXACT",
        graph,
        class_of,
        representatives,
        separators,
        sat,
        witness,
        sum(len(level) for level in representatives),
        max(len(level) for level in representatives),
        separator_volume,
        None,
    )


def verify_package(package: QuotientPackage) -> bool:
    if package.status != "EXACT":
        return False

    graph = package.graph
    depth_count = len(graph.order)

    if graph.layers[0] != {normalize_cnf(graph.formula)}:
        return False

    for depth, variable in enumerate(graph.order):
        for state in graph.layers[depth]:
            for value in (False, True):
                child = restrict_cnf(state, {variable: value})
                if graph.transitions.get((depth, state, value)) != child:
                    return False
                if child not in graph.layers[depth + 1]:
                    return False

    for depth in range(depth_count + 1):
        if set(package.class_of[depth]) != set(graph.layers[depth]):
            return False
        if set(package.representatives[depth]) != set(
            package.class_of[depth].values()
        ):
            return False

        grouped: dict[int, list[CNF]] = defaultdict(list)
        for state, class_id in package.class_of[depth].items():
            grouped[class_id].append(state)

        for class_id, representative in package.representatives[depth].items():
            if representative not in grouped[class_id]:
                return False

        for states in grouped.values():
            if depth == depth_count:
                if len({terminal_label(state) for state in states}) != 1:
                    return False
            else:
                signatures = set()
                for state in states:
                    zero_child = graph.transitions[(depth, state, False)]
                    one_child = graph.transitions[(depth, state, True)]
                    signatures.add(
                        (
                            package.class_of[depth + 1][zero_child],
                            package.class_of[depth + 1][one_child],
                        )
                    )
                if len(signatures) != 1:
                    return False

    expected_pairs = {
        (depth, class_a, class_b)
        for depth in range(depth_count + 1)
        for left_index, class_a in enumerate(
            sorted(package.representatives[depth])
        )
        for class_b in sorted(package.representatives[depth])[left_index + 1:]
    }
    seen_pairs = set()

    for depth, class_a, class_b, suffix, label_a, label_b in package.separators:
        key = (depth, class_a, class_b)
        if key not in expected_pairs or key in seen_pairs:
            return False
        seen_pairs.add(key)

        if len(suffix) != depth_count - depth:
            return False

        state_a = package.representatives[depth][class_a]
        state_b = package.representatives[depth][class_b]
        replay_a = evaluate_suffix(state_a, graph.order, depth, suffix)
        replay_b = evaluate_suffix(state_b, graph.order, depth, suffix)
        if replay_a == replay_b:
            return False
        if replay_a != label_a or replay_b != label_b:
            return False

    if seen_pairs != expected_pairs:
        return False

    sat, witness = recover_sat_witness(
        graph,
        package.class_of,
        package.representatives,
    )
    if sat != package.sat:
        return False
    if sat:
        if package.witness != witness:
            return False
        if package.witness is None:
            return False
        if not evaluate(graph.formula, package.witness):
            return False
    elif package.witness is not None:
        return False

    return True


def equality_cnf(pair_count: int) -> CNF:
    clauses = []
    for index in range(1, pair_count + 1):
        left = index
        right = pair_count + index
        clauses.extend(((-left, right), (left, -right)))
    return tuple(clauses)


def interleaved_order(pair_count: int) -> list[int]:
    return [
        variable
        for index in range(1, pair_count + 1)
        for variable in (index, pair_count + index)
    ]


def blocked_order(pair_count: int) -> list[int]:
    return list(range(1, pair_count + 1)) + list(
        range(pair_count + 1, 2 * pair_count + 1)
    )


def equality_order_audit(max_pairs: int = 8):
    rows = []
    for pair_count in range(1, max_pairs + 1):
        formula = equality_cnf(pair_count)

        good = compile_quotient(
            formula,
            interleaved_order(pair_count),
            state_budget=50_000,
            separator_budget=2_000_000,
        )
        bad = compile_quotient(
            formula,
            blocked_order(pair_count),
            state_budget=50_000,
            separator_budget=2_000_000,
        )

        if good.status != "EXACT" or bad.status != "EXACT":
            raise AssertionError("small equality controls must compile exactly")
        if not verify_package(good) or not verify_package(bad):
            raise AssertionError("equality proof package failed replay")

        if good.max_quotient_width > 3:
            raise AssertionError("interleaved equality width exceeded three")
        if bad.max_quotient_width != 2 ** pair_count:
            raise AssertionError("blocked equality width is not exactly 2^n")

        rows.append(
            {
                "pairs": pair_count,
                "interleaved_max_width": good.max_quotient_width,
                "blocked_max_width": bad.max_quotient_width,
                "blocked_state_count": bad.graph.state_count,
                "blocked_separator_volume": bad.separator_volume,
            }
        )

    budget_control = compile_quotient(
        equality_cnf(12),
        blocked_order(12),
        state_budget=2_000,
        separator_budget=100_000,
    )
    if budget_control.status != "OPEN":
        raise AssertionError("large blocked equality control must return OPEN")

    return {
        "rows": rows,
        "budget_control": {
            "pairs": 12,
            "status": budget_control.status,
            "reason": budget_control.reason,
            "states_before_open": budget_control.graph.state_count,
            "largest_completed_width": budget_control.graph.max_width,
        },
    }


def horn_undermerge_audit():
    formula = ((-3,), (-2,), (-1, 3))
    package = compile_quotient(
        formula,
        [1, 2, 3],
        state_budget=1_000,
        separator_budget=1_000,
    )
    if package.status != "EXACT" or not verify_package(package):
        raise AssertionError("Horn under-merge package failed")

    raw_width = len(package.graph.layers[2])
    quotient_width = len(package.representatives[2])
    if raw_width != 3 or quotient_width != 2:
        raise AssertionError("expected one semantic merge at depth two")

    return {
        "raw_states_at_depth_2": raw_width,
        "quotient_states_at_depth_2": quotient_width,
        "merged_syntactic_states": raw_width - quotient_width,
        "separator_records": len(package.separators),
        "sat": package.sat,
    }


def random_3cnf(rng: random.Random, variable_count: int, clause_count: int) -> CNF:
    clauses = []
    for _ in range(clause_count):
        variables_ = [
            rng.randint(1, variable_count)
            for _ in range(3)
        ]
        clauses.append(
            tuple(
                variable if rng.getrandbits(1) else -variable
                for variable in variables_
            )
        )
    return tuple(clauses)


def nand3_neq_cnf(source: CNF, variable_count: int) -> CNF:
    clauses = []
    for variable in range(1, variable_count + 1):
        complement = variable_count + variable
        clauses.append((variable, complement))
        clauses.append((-variable, -complement))

    for clause in source:
        falsity_indicators = [
            variable_count + abs(literal)
            if literal > 0
            else abs(literal)
            for literal in clause
        ]
        clauses.append(tuple(-indicator for indicator in falsity_indicators))

    return normalize_cnf(tuple(clauses))


def continuation_vector(
    residual: CNF,
    order: tuple[int, ...],
    depth: int,
):
    remaining = order[depth:]
    return tuple(
        terminal_label(
            restrict_cnf(
                residual,
                dict(zip(remaining, bits)),
            )
        )
        for bits in itertools.product((False, True), repeat=len(remaining))
    )


def nand3_neq_pressure(seed: int = 360_036, cases: int = 250):
    rng = random.Random(seed)
    total_explicit_states = 0
    total_quotient_nodes = 0
    merged_states = 0
    separator_records = 0
    strict_merge_cases = 0
    maximum_state_to_quotient_ratio = 1.0

    for _ in range(cases):
        variable_count = rng.randint(2, 5)
        clause_count = rng.randint(variable_count, 2 * variable_count + 2)
        source = random_3cnf(rng, variable_count, clause_count)
        formula = nand3_neq_cnf(source, variable_count)
        order = interleaved_order(variable_count)

        package = compile_quotient(
            formula,
            order,
            state_budget=10_000,
            separator_budget=200_000,
        )
        if package.status != "EXACT":
            raise AssertionError("small NAND3+NEQ fixture unexpectedly OPEN")
        if not verify_package(package):
            raise AssertionError("NAND3+NEQ package failed replay")

        case_merged = 0
        for depth in range(len(order) + 1):
            semantic_vectors = {
                continuation_vector(state, tuple(order), depth)
                for state in package.graph.layers[depth]
            }
            if len(semantic_vectors) != len(package.representatives[depth]):
                raise AssertionError("quotient differs from exhaustive semantics")
            case_merged += (
                len(package.graph.layers[depth])
                - len(package.representatives[depth])
            )

        if case_merged:
            strict_merge_cases += 1
        merged_states += case_merged
        total_explicit_states += package.graph.state_count
        total_quotient_nodes += package.quotient_nodes
        separator_records += len(package.separators)
        maximum_state_to_quotient_ratio = max(
            maximum_state_to_quotient_ratio,
            package.graph.state_count / package.quotient_nodes,
        )

    return {
        "seed": seed,
        "cases": cases,
        "explicit_states": total_explicit_states,
        "quotient_nodes": total_quotient_nodes,
        "merged_states": merged_states,
        "strict_merge_cases": strict_merge_cases,
        "separator_records_verified": separator_records,
        "maximum_state_to_quotient_ratio": maximum_state_to_quotient_ratio,
    }


def unsat_certificate_control():
    package = compile_quotient(
        ((1,), (-1,)),
        [1],
        state_budget=100,
        separator_budget=100,
    )
    if package.status != "EXACT" or package.sat is not False:
        raise AssertionError("UNSAT control was not decided exactly")
    if not verify_package(package):
        raise AssertionError("UNSAT quotient certificate failed replay")
    return {
        "sat": package.sat,
        "quotient_nodes": package.quotient_nodes,
        "verified": True,
    }


def corrupt_separator_control():
    package = compile_quotient(
        ((1, 2), (-1, -2)),
        [1, 2],
        state_budget=100,
        separator_budget=1_000,
    )
    if package.status != "EXACT" or not package.separators:
        raise AssertionError("separator corruption fixture is empty")

    corrupted = QuotientPackage(
        package.status,
        package.graph,
        package.class_of,
        package.representatives,
        list(package.separators),
        package.sat,
        package.witness,
        package.quotient_nodes,
        package.max_quotient_width,
        package.separator_volume,
        package.reason,
    )
    depth, class_a, class_b, suffix, label_a, label_b = corrupted.separators[0]
    corrupted.separators[0] = (
        depth,
        class_a,
        class_b,
        suffix,
        label_a,
        label_a,
    )
    if verify_package(corrupted):
        raise AssertionError("corrupt separator was accepted")
    return {"corrupt_separator_rejected": True}


def run():
    equality = equality_order_audit()
    horn = horn_undermerge_audit()
    pressure = nand3_neq_pressure()
    unsat = unsat_certificate_control()
    corrupt = corrupt_separator_control()

    result = {
        "artifact_id": "C037-JANUS-EXPLICIT-RESIDUAL-OBDD-ALIGNMENT",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "theorem": (
            "For a fixed variable order and an explicitly generated exact "
            "residual-state DAG, bottom-up partition refinement constructs the "
            "coarsest continuation quotient, replayable distinguishing suffixes, "
            "SAT witnesses, and a checkable UNSAT DAG certificate in polynomial "
            "time in the explicit graph and certificate volume."
        ),
        "alignment": (
            "The quotient is exactly the reduced OBDD / minimal ordered residual "
            "automaton for the selected variable order."
        ),
        "horn_undermerge": horn,
        "equality_order": equality,
        "nand3_neq_pressure": pressure,
        "unsat_certificate": unsat,
        "corrupt_separator_control": corrupt,
        "located_bottleneck": (
            "POLYNOMIAL_ORDER_DECOMPOSITION_AND_REACHABLE_QUOTIENT_CONSTRUCTION"
        ),
        "claim_boundary": (
            "C037 proves exact proof-carrying refinement once the reachable "
            "residual graph is explicitly available. It does not prove that a "
            "polynomial-size graph or a good order can be found for arbitrary "
            "CNF, and it does not resolve P versus NP."
        ),
    }
    payload = json.dumps(
        result,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    result["integrity_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()

    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))

    if arguments.self_test:
        assert result["status"] == "PASS"
        assert result["equality_order"]["rows"][-1]["blocked_max_width"] == 256
        assert result["equality_order"]["budget_control"]["status"] == "OPEN"
        assert result["corrupt_separator_control"]["corrupt_separator_rejected"]


if __name__ == "__main__":
    main()
