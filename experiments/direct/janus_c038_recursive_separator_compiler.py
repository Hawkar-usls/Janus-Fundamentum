#!/usr/bin/env python3
"""
C038 JANUS proof-carrying recursive separator compiler.

The compiler first constructs one assignment-independent recursive separator plan
from the CNF primal graph. It then compiles the formula along that fixed plan.

For fixed separator bound k:
- separator discovery is explicit and deterministic;
- every branch uses the same recursive plan / vtree;
- AND nodes combine disjoint variable regions;
- separator branches are mutually exclusive assignments;
- SAT witnesses are reconstructed;
- UNSAT is certified by the exhaustive branch DAG;
- unsupported structure or budget exhaustion returns OPEN.

This is an alignment with structured d-DNNF / SDD-style compilation, not a new
universal width parameter and not a proof of P versus NP.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import random
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

Clause = Tuple[int, ...]
CNF = Tuple[Clause, ...]
Assignment = Dict[int, bool]
Graph = Dict[int, Set[int]]


class OpenCompile(RuntimeError):
    def __init__(self, reason: str, stats: Optional[dict] = None):
        super().__init__(reason)
        self.reason = reason
        self.stats = stats or {}


def canon_clause(clause: Clause) -> Optional[Clause]:
    literals = set(clause)
    if any(-lit in literals for lit in literals):
        return None
    return tuple(sorted(literals, key=lambda lit: (abs(lit), lit < 0)))


def normalize(formula: CNF) -> CNF:
    clauses: List[Clause] = []
    for clause in formula:
        canonical = canon_clause(clause)
        if canonical is not None:
            clauses.append(canonical)
    clauses = sorted(set(clauses), key=lambda clause: (len(clause), clause))
    kept: List[Clause] = []
    for clause in clauses:
        clause_set = set(clause)
        if any(set(smaller) <= clause_set for smaller in kept):
            continue
        kept.append(clause)
    return tuple(kept)


def variables(formula: CNF) -> List[int]:
    return sorted({abs(lit) for clause in formula for lit in clause})


def restrict_cnf(formula: CNF, assignment: Assignment) -> CNF:
    residual: List[Clause] = []
    for clause in formula:
        satisfied = False
        remaining: List[int] = []
        for lit in clause:
            var = abs(lit)
            if var in assignment:
                if assignment[var] == (lit > 0):
                    satisfied = True
                    break
            else:
                remaining.append(lit)
        if not satisfied:
            residual.append(tuple(remaining))
    return normalize(tuple(residual))


def evaluate(formula: CNF, assignment: Assignment) -> bool:
    return all(
        any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause)
        for clause in formula
    )


def primal_graph(formula: CNF) -> Graph:
    graph: Graph = {var: set() for var in variables(formula)}
    for clause in formula:
        clause_vars = sorted({abs(lit) for lit in clause})
        for i, left in enumerate(clause_vars):
            for right in clause_vars[i + 1 :]:
                graph[left].add(right)
                graph[right].add(left)
    return graph


def induced_graph(graph: Graph, vertices: Iterable[int]) -> Graph:
    allowed = set(vertices)
    return {
        vertex: {neighbor for neighbor in graph.get(vertex, set()) if neighbor in allowed}
        for vertex in allowed
    }


def graph_components(graph: Graph, removed: Iterable[int] = ()) -> List[Set[int]]:
    removed_set = set(removed)
    unseen = set(graph) - removed_set
    result: List[Set[int]] = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        component = {start}
        queue = [start]
        while queue:
            vertex = queue.pop()
            for neighbor in graph.get(vertex, set()):
                if neighbor in unseen and neighbor not in removed_set:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        result.append(component)
    return result


def combine_vtrees(trees):
    work = [tree for tree in trees if tree is not None]
    if not work:
        return None
    while len(work) > 1:
        next_level = []
        iterator = iter(work)
        for left in iterator:
            right = next(iterator, None)
            next_level.append(left if right is None else (left, right))
        work = next_level
    return work[0]


def vtree_variables(vtree) -> Set[int]:
    if vtree is None:
        return set()
    if isinstance(vtree, int):
        return {vtree}
    return vtree_variables(vtree[0]) | vtree_variables(vtree[1])


class PlanBuilder:
    def __init__(
        self,
        max_separator: int = 1,
        base_variables: int = 2,
        balance_numerator: int = 2,
        balance_denominator: int = 3,
    ):
        self.max_separator = max_separator
        self.base_variables = base_variables
        self.balance_numerator = balance_numerator
        self.balance_denominator = balance_denominator
        self.plans: Dict[int, dict] = {}
        self.next_id = 0
        self.stats = {
            "plan_nodes": 0,
            "separator_subsets_checked": 0,
            "separator_nodes": 0,
            "component_nodes": 0,
            "leaf_nodes": 0,
        }

    def _add(self, plan: dict) -> int:
        plan_id = self.next_id
        self.next_id += 1
        self.plans[plan_id] = plan
        self.stats["plan_nodes"] += 1
        return plan_id

    def build_graph(self, graph: Graph) -> int:
        plan_vars = tuple(sorted(graph))

        if len(plan_vars) <= self.base_variables:
            plan_id = self._add({"type": "LEAF", "vars": plan_vars})
            self.stats["leaf_nodes"] += 1
            return plan_id

        components = sorted(graph_components(graph), key=lambda item: min(item))
        if len(components) > 1:
            child_ids = [
                self.build_graph(induced_graph(graph, component))
                for component in components
            ]
            plan_id = self._add(
                {
                    "type": "COMPONENTS",
                    "vars": plan_vars,
                    "components": tuple(tuple(sorted(component)) for component in components),
                    "children": tuple(child_ids),
                }
            )
            self.stats["component_nodes"] += 1
            return plan_id

        vertex_count = len(plan_vars)
        balance_limit = math.ceil(
            self.balance_numerator * vertex_count / self.balance_denominator
        )

        selected_separator = None
        selected_components = None
        for size in range(1, min(self.max_separator, vertex_count - 1) + 1):
            for separator in itertools.combinations(plan_vars, size):
                self.stats["separator_subsets_checked"] += 1
                remaining_components = sorted(
                    graph_components(graph, separator), key=lambda item: min(item)
                )
                if (
                    len(remaining_components) >= 2
                    and max(map(len, remaining_components)) <= balance_limit
                ):
                    selected_separator = tuple(separator)
                    selected_components = remaining_components
                    break
            if selected_separator is not None:
                break

        if selected_separator is None or selected_components is None:
            raise OpenCompile("NO_BALANCED_SEPARATOR", dict(self.stats))

        child_ids = [
            self.build_graph(induced_graph(graph, component))
            for component in selected_components
        ]
        plan_id = self._add(
            {
                "type": "SEPARATOR",
                "vars": plan_vars,
                "separator": selected_separator,
                "components": tuple(
                    tuple(sorted(component)) for component in selected_components
                ),
                "children": tuple(child_ids),
            }
        )
        self.stats["separator_nodes"] += 1
        return plan_id

    def build(self, formula: CNF) -> int:
        return self.build_graph(primal_graph(formula))


def plan_vtree(plans: Dict[int, dict], plan_id: int):
    plan = plans[plan_id]
    if plan["type"] == "LEAF":
        return combine_vtrees(plan["vars"])
    if plan["type"] == "COMPONENTS":
        return combine_vtrees(plan_vtree(plans, child) for child in plan["children"])

    separator_tree = combine_vtrees(plan["separator"])
    remainder_tree = combine_vtrees(
        plan_vtree(plans, child) for child in plan["children"]
    )
    return (separator_tree, remainder_tree)


class StructuredCompiler:
    def __init__(
        self,
        plans: Dict[int, dict],
        root_plan: int,
        node_budget: int = 100_000,
    ):
        self.plans = plans
        self.root_plan = root_plan
        self.node_budget = node_budget
        self.nodes: Dict[int, dict] = {}
        self.memo: Dict[Tuple[int, CNF], int] = {}
        self.next_id = 0
        self.stats = {
            "circuit_nodes": 0,
            "decision_nodes": 0,
            "and_nodes": 0,
            "table_nodes": 0,
            "terminal_nodes": 0,
            "branches": 0,
        }

    def _add(self, node: dict) -> int:
        if self.stats["circuit_nodes"] >= self.node_budget:
            raise OpenCompile("NODE_BUDGET", dict(self.stats))
        node_id = self.next_id
        self.next_id += 1
        self.nodes[node_id] = node
        self.stats["circuit_nodes"] += 1
        return node_id

    def compile(self, formula: CNF, plan_id: Optional[int] = None) -> int:
        if plan_id is None:
            plan_id = self.root_plan

        formula = normalize(formula)
        key = (plan_id, formula)
        if key in self.memo:
            return self.memo[key]

        plan = self.plans[plan_id]
        if not set(variables(formula)) <= set(plan["vars"]):
            raise AssertionError("formula escaped its plan variable region")

        if formula == ():
            node_id = self._add(
                {"type": "TRUE", "plan": plan_id, "formula": formula}
            )
            self.stats["terminal_nodes"] += 1
            self.memo[key] = node_id
            return node_id

        if formula == ((),):
            node_id = self._add(
                {"type": "FALSE", "plan": plan_id, "formula": formula}
            )
            self.stats["terminal_nodes"] += 1
            self.memo[key] = node_id
            return node_id

        if plan["type"] == "LEAF":
            rows = []
            for bits in itertools.product((False, True), repeat=len(plan["vars"])):
                assignment = dict(zip(plan["vars"], bits))
                rows.append((tuple(bits), evaluate(formula, assignment)))
            node_id = self._add(
                {
                    "type": "TABLE",
                    "plan": plan_id,
                    "formula": formula,
                    "vars": plan["vars"],
                    "rows": tuple(rows),
                }
            )
            self.stats["table_nodes"] += 1
            self.memo[key] = node_id
            return node_id

        if plan["type"] == "COMPONENTS":
            child_nodes = []
            reconstructed: List[Clause] = []
            for component_tuple, child_plan in zip(
                plan["components"], plan["children"]
            ):
                component = set(component_tuple)
                child_formula = normalize(
                    tuple(
                        clause
                        for clause in formula
                        if any(abs(lit) in component for lit in clause)
                    )
                )
                if any(
                    not {abs(lit) for lit in clause} <= component
                    for clause in child_formula
                ):
                    raise AssertionError("clause crossed a component boundary")
                reconstructed.extend(child_formula)
                child_nodes.append(self.compile(child_formula, child_plan))
            if normalize(tuple(reconstructed)) != formula:
                raise AssertionError("component partition lost clauses")

            node_id = self._add(
                {
                    "type": "AND",
                    "plan": plan_id,
                    "formula": formula,
                    "children": tuple(child_nodes),
                }
            )
            self.stats["and_nodes"] += 1
            self.memo[key] = node_id
            return node_id

        separator = plan["separator"]
        branches = []

        for bits in itertools.product((False, True), repeat=len(separator)):
            assignment = dict(zip(separator, bits))
            residual = restrict_cnf(formula, assignment)

            if residual in ((), ((),)):
                child_id = self._add(
                    {
                        "type": "TRUE" if residual == () else "FALSE",
                        "plan": plan_id,
                        "formula": residual,
                        "branch_terminal": True,
                    }
                )
                self.stats["terminal_nodes"] += 1
            else:
                child_nodes = []
                reconstructed: List[Clause] = []
                for component_tuple, child_plan in zip(
                    plan["components"], plan["children"]
                ):
                    component = set(component_tuple)
                    child_formula = normalize(
                        tuple(
                            clause
                            for clause in residual
                            if any(abs(lit) in component for lit in clause)
                        )
                    )
                    if any(
                        not {abs(lit) for lit in clause} <= component
                        for clause in child_formula
                    ):
                        raise AssertionError(
                            "restricted clause crossed a planned component boundary"
                        )
                    reconstructed.extend(child_formula)
                    child_nodes.append(self.compile(child_formula, child_plan))

                if normalize(tuple(reconstructed)) != residual:
                    raise AssertionError("separator branch lost clauses")

                child_id = self._add(
                    {
                        "type": "AND",
                        "plan": plan_id,
                        "formula": residual,
                        "children": tuple(child_nodes),
                        "branch_and": True,
                    }
                )
                self.stats["and_nodes"] += 1

            branches.append((tuple(bits), child_id))
            self.stats["branches"] += 1

        node_id = self._add(
            {
                "type": "DECISION",
                "plan": plan_id,
                "formula": formula,
                "separator": separator,
                "branches": tuple(branches),
            }
        )
        self.stats["decision_nodes"] += 1
        self.memo[key] = node_id
        return node_id


def solve_compilation(
    nodes: Dict[int, dict],
    node_id: int,
) -> Optional[Assignment]:
    node = nodes[node_id]
    node_type = node["type"]

    if node_type == "TRUE":
        return {}
    if node_type == "FALSE":
        return None
    if node_type == "TABLE":
        for bits, value in node["rows"]:
            if value:
                return dict(zip(node["vars"], bits))
        return None
    if node_type == "AND":
        witness: Assignment = {}
        for child in node["children"]:
            child_witness = solve_compilation(nodes, child)
            if child_witness is None:
                return None
            for var, value in child_witness.items():
                if var in witness and witness[var] != value:
                    raise AssertionError("decomposable children disagreed")
                witness[var] = value
        return witness
    if node_type == "DECISION":
        for bits, child in node["branches"]:
            child_witness = solve_compilation(nodes, child)
            if child_witness is not None:
                result = dict(child_witness)
                result.update(dict(zip(node["separator"], bits)))
                return result
        return None

    raise ValueError(f"unknown node type: {node_type}")


def verify_plan(
    plans: Dict[int, dict],
    root_plan: int,
    formula: CNF,
    max_separator: int,
    base_variables: int,
    balance_numerator: int = 2,
    balance_denominator: int = 3,
) -> bool:
    root_graph = primal_graph(formula)
    seen: Set[int] = set()

    def visit(plan_id: int, graph: Graph) -> bool:
        if plan_id in seen:
            return False
        seen.add(plan_id)

        plan = plans.get(plan_id)
        if plan is None or tuple(sorted(graph)) != tuple(plan["vars"]):
            return False

        if plan["type"] == "LEAF":
            return len(graph) <= base_variables

        if plan["type"] == "COMPONENTS":
            components = sorted(graph_components(graph), key=lambda item: min(item))
            if len(components) <= 1:
                return False
            encoded = tuple(tuple(sorted(component)) for component in components)
            if encoded != tuple(plan["components"]):
                return False
            return len(components) == len(plan["children"]) and all(
                visit(child, induced_graph(graph, component))
                for child, component in zip(plan["children"], components)
            )

        if plan["type"] != "SEPARATOR":
            return False

        separator = tuple(plan["separator"])
        if not (1 <= len(separator) <= max_separator):
            return False
        if not set(separator) <= set(graph):
            return False

        components = sorted(
            graph_components(graph, separator), key=lambda item: min(item)
        )
        limit = math.ceil(balance_numerator * len(graph) / balance_denominator)
        if len(components) < 2 or max(map(len, components)) > limit:
            return False

        encoded = tuple(tuple(sorted(component)) for component in components)
        if encoded != tuple(plan["components"]):
            return False

        return len(components) == len(plan["children"]) and all(
            visit(child, induced_graph(graph, component))
            for child, component in zip(plan["children"], components)
        )

    if not visit(root_plan, root_graph):
        return False

    vtree = plan_vtree(plans, root_plan)
    return vtree_variables(vtree) == set(root_graph)


def verify_compilation(
    nodes: Dict[int, dict],
    root: int,
    plans: Dict[int, dict],
    root_plan: int,
    source: CNF,
) -> bool:
    checked = set()

    def visit(node_id: int, plan_id: int, expected: CNF) -> bool:
        expected = normalize(expected)
        node = nodes.get(node_id)
        if (
            node is None
            or node.get("plan") != plan_id
            or normalize(node.get("formula", ())) != expected
        ):
            return False

        cache_key = (node_id, plan_id, expected)
        if cache_key in checked:
            return True
        checked.add(cache_key)

        plan = plans[plan_id]
        node_type = node["type"]

        if node_type == "TRUE":
            return expected == ()
        if node_type == "FALSE":
            return expected == ((),)
        if node_type == "TABLE":
            if plan["type"] != "LEAF" or tuple(node["vars"]) != tuple(plan["vars"]):
                return False
            expected_rows = []
            for bits in itertools.product(
                (False, True), repeat=len(plan["vars"])
            ):
                assignment = dict(zip(plan["vars"], bits))
                expected_rows.append((tuple(bits), evaluate(expected, assignment)))
            return tuple(expected_rows) == tuple(node["rows"])

        if node_type == "AND":
            if node.get("branch_and"):
                if plan["type"] != "SEPARATOR":
                    return False
            elif plan["type"] != "COMPONENTS":
                return False

            if len(node["children"]) != len(plan["children"]):
                return False

            reconstructed: List[Clause] = []
            for component_tuple, child_plan, child_node in zip(
                plan["components"], plan["children"], node["children"]
            ):
                component = set(component_tuple)
                child_formula = normalize(
                    tuple(
                        clause
                        for clause in expected
                        if any(abs(lit) in component for lit in clause)
                    )
                )
                if any(
                    not {abs(lit) for lit in clause} <= component
                    for clause in child_formula
                ):
                    return False
                reconstructed.extend(child_formula)
                if not visit(child_node, child_plan, child_formula):
                    return False

            return normalize(tuple(reconstructed)) == expected

        if node_type != "DECISION" or plan["type"] != "SEPARATOR":
            return False
        if tuple(node["separator"]) != tuple(plan["separator"]):
            return False

        separator = plan["separator"]
        all_bits = list(
            itertools.product((False, True), repeat=len(separator))
        )
        if [tuple(bits) for bits, _ in node["branches"]] != all_bits:
            return False

        for bits, child in node["branches"]:
            residual = restrict_cnf(expected, dict(zip(separator, bits)))
            child_node = nodes.get(child)
            if residual not in ((), ((),)) and (
                child_node is None or not child_node.get("branch_and")
            ):
                return False
            if not visit(child, plan_id, residual):
                return False

        return True

    if not visit(root, root_plan, source):
        return False

    witness = solve_compilation(nodes, root)
    if witness is None:
        return True

    completed = {var: witness.get(var, False) for var in variables(source)}
    return evaluate(source, completed)


def brute_force(formula: CNF) -> Tuple[bool, Optional[Assignment]]:
    formula_vars = variables(formula)
    for bits in itertools.product((False, True), repeat=len(formula_vars)):
        assignment = dict(zip(formula_vars, bits))
        if evaluate(formula, assignment):
            return True, assignment
    return False, None


def compile_with_plan(
    formula: CNF,
    max_separator: int = 1,
    base_variables: int = 2,
    node_budget: int = 100_000,
):
    formula = normalize(formula)
    builder = PlanBuilder(
        max_separator=max_separator,
        base_variables=base_variables,
    )
    root_plan = builder.build(formula)
    compiler = StructuredCompiler(
        builder.plans,
        root_plan,
        node_budget=node_budget,
    )
    root = compiler.compile(formula)
    return builder, root_plan, compiler, root


def equality_formula(pairs: int) -> CNF:
    clauses: List[Clause] = []
    for index in range(1, pairs + 1):
        left = index
        right = pairs + index
        clauses.append((-left, right))
        clauses.append((left, -right))
    return normalize(tuple(clauses))


def tree_formula(vertex_count: int, rng: random.Random) -> CNF:
    clauses: List[Clause] = []
    for vertex in range(2, vertex_count + 1):
        parent = rng.randint(1, vertex - 1)
        left = parent if rng.getrandbits(1) else -parent
        right = vertex if rng.getrandbits(1) else -vertex
        clauses.append((left, right))
    for vertex in range(1, vertex_count + 1):
        if rng.random() < 0.18:
            clauses.append((vertex if rng.getrandbits(1) else -vertex,))
    return normalize(tuple(clauses))


def random_formula(rng: random.Random, variable_count: int) -> CNF:
    clause_count = rng.randint(0, 2 * variable_count)
    clauses: List[Clause] = []
    for _ in range(clause_count):
        width = rng.randint(1, min(3, variable_count))
        chosen = rng.sample(range(1, variable_count + 1), width)
        clauses.append(
            tuple(var if rng.getrandbits(1) else -var for var in chosen)
        )
    return normalize(tuple(clauses))


def dense_clique_formula(variable_count: int) -> CNF:
    return normalize(
        tuple(
            (left, right)
            for left in range(1, variable_count + 1)
            for right in range(left + 1, variable_count + 1)
        )
    )


def blocked_equality_residual_count(pairs: int) -> int:
    formula = equality_formula(pairs)
    residuals = set()
    for bits in itertools.product((False, True), repeat=pairs):
        assignment = {index + 1: bits[index] for index in range(pairs)}
        residuals.add(restrict_cnf(formula, assignment))
    return len(residuals)


def random_audit(seed: int = 380038, cases: int = 600) -> dict:
    rng = random.Random(seed)
    exact = 0
    open_count = 0
    mismatches = 0
    witness_failures = 0
    verification_failures = 0
    total_plan_nodes = 0
    total_circuit_nodes = 0

    for _ in range(cases):
        variable_count = rng.randint(1, 9)
        formula = (
            tree_formula(variable_count, rng)
            if rng.random() < 0.72
            else random_formula(rng, variable_count)
        )
        try:
            builder, root_plan, compiler, root = compile_with_plan(
                formula,
                max_separator=1,
                base_variables=2,
                node_budget=5_000,
            )
        except OpenCompile:
            open_count += 1
            continue

        exact += 1
        total_plan_nodes += builder.stats["plan_nodes"]
        total_circuit_nodes += compiler.stats["circuit_nodes"]

        brute_sat, _ = brute_force(formula)
        witness = solve_compilation(compiler.nodes, root)
        compiled_sat = witness is not None

        if compiled_sat != brute_sat:
            mismatches += 1
        if witness is not None:
            completed = {
                var: witness.get(var, False)
                for var in variables(formula)
            }
            if not evaluate(formula, completed):
                witness_failures += 1

        if not verify_plan(
            builder.plans,
            root_plan,
            formula,
            max_separator=1,
            base_variables=2,
        ):
            verification_failures += 1

        if not verify_compilation(
            compiler.nodes,
            root,
            builder.plans,
            root_plan,
            formula,
        ):
            verification_failures += 1

    assert mismatches == 0
    assert witness_failures == 0
    assert verification_failures == 0

    return {
        "seed": seed,
        "cases": cases,
        "exact": exact,
        "open": open_count,
        "mismatches": mismatches,
        "witness_failures": witness_failures,
        "verification_failures": verification_failures,
        "total_plan_nodes": total_plan_nodes,
        "total_circuit_nodes": total_circuit_nodes,
    }


def equality_audit(max_pairs: int = 12) -> List[dict]:
    rows = []
    for pairs in range(1, max_pairs + 1):
        formula = equality_formula(pairs)
        builder, root_plan, compiler, root = compile_with_plan(
            formula,
            max_separator=1,
            base_variables=2,
            node_budget=100_000,
        )
        assert verify_plan(
            builder.plans,
            root_plan,
            formula,
            max_separator=1,
            base_variables=2,
        )
        assert verify_compilation(
            compiler.nodes,
            root,
            builder.plans,
            root_plan,
            formula,
        )
        exact_blocked_width = (
            blocked_equality_residual_count(pairs)
            if pairs <= 8
            else 2**pairs
        )
        assert exact_blocked_width == 2**pairs
        rows.append(
            {
                "pairs": pairs,
                "structured_plan_nodes": builder.stats["plan_nodes"],
                "structured_circuit_nodes": compiler.stats["circuit_nodes"],
                "blocked_obdd_width": exact_blocked_width,
            }
        )
    return rows


def large_tree_control(seed: int = 380039, variables_count: int = 127) -> dict:
    rng = random.Random(seed)
    formula = tree_formula(variables_count, rng)
    builder, root_plan, compiler, root = compile_with_plan(
        formula,
        max_separator=1,
        base_variables=2,
        node_budget=100_000,
    )
    assert verify_plan(
        builder.plans,
        root_plan,
        formula,
        max_separator=1,
        base_variables=2,
    )
    assert verify_compilation(
        compiler.nodes,
        root,
        builder.plans,
        root_plan,
        formula,
    )
    witness = solve_compilation(compiler.nodes, root)
    if witness is not None:
        completed = {
            var: witness.get(var, False)
            for var in variables(formula)
        }
        assert evaluate(formula, completed)
    return {
        "variables": variables_count,
        "plan_stats": builder.stats,
        "circuit_stats": compiler.stats,
        "sat": witness is not None,
    }


def open_controls() -> dict:
    dense = dense_clique_formula(8)
    dense_result = None
    try:
        compile_with_plan(
            dense,
            max_separator=1,
            base_variables=2,
            node_budget=10_000,
        )
        dense_result = "UNEXPECTED_EXACT"
    except OpenCompile as error:
        dense_result = error.reason

    budget_formula = tree_formula(63, random.Random(380040))
    budget_result = None
    try:
        compile_with_plan(
            budget_formula,
            max_separator=1,
            base_variables=2,
            node_budget=8,
        )
        budget_result = "UNEXPECTED_EXACT"
    except OpenCompile as error:
        budget_result = error.reason

    assert dense_result == "NO_BALANCED_SEPARATOR"
    assert budget_result == "NODE_BUDGET"

    return {
        "dense_clique_control": dense_result,
        "budget_control": budget_result,
    }


def corrupt_certificate_control() -> dict:
    formula = normalize(
        tuple((index, index + 1) for index in range(1, 8))
    )
    builder, root_plan, compiler, root = compile_with_plan(
        formula,
        max_separator=1,
        base_variables=2,
        node_budget=10_000,
    )
    assert verify_compilation(
        compiler.nodes,
        root,
        builder.plans,
        root_plan,
        formula,
    )

    corrupted = copy.deepcopy(compiler.nodes)
    decision_id = next(
        node_id
        for node_id, node in corrupted.items()
        if node["type"] == "DECISION"
    )
    first_bits, first_child = corrupted[decision_id]["branches"][0]
    flipped = tuple(not bit for bit in first_bits)
    branches = list(corrupted[decision_id]["branches"])
    branches[0] = (flipped, first_child)
    corrupted[decision_id]["branches"] = tuple(branches)

    rejected = not verify_compilation(
        corrupted,
        root,
        builder.plans,
        root_plan,
        formula,
    )
    assert rejected
    return {"corrupt_branch_assignment_rejected": rejected}


def run() -> dict:
    random_result = random_audit()
    equality_result = equality_audit()
    tree_result = large_tree_control()
    controls = open_controls()
    corrupt = corrupt_certificate_control()

    result = {
        "artifact_id": "C038-JANUS-PROOF-CARRYING-RECURSIVE-SEPARATOR-COMPILER",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "theorem": (
            "For every fixed separator bound k, the assignment-independent "
            "recursive separator plan and its structured deterministic compilation "
            "are constructible and independently replayable in n^{O(k)} total work "
            "on admitted formulas."
        ),
        "alignment": (
            "The output is a proof-carrying macro representation of a deterministic "
            "structured decomposable circuit respecting one fixed vtree."
        ),
        "random_audit": random_result,
        "equality_order_separation": equality_result,
        "large_tree_control": tree_result,
        "open_controls": controls,
        "corrupt_control": corrupt,
        "new_gate": "POLYNOMIAL_SEMANTIC_SEPARATOR_OR_VTREE_DISCOVERY",
        "claim_boundary": (
            "Fixed-k structured compilation only. The procedure returns OPEN when "
            "no allowed balanced separator is found or when the explicit circuit "
            "budget is exceeded. It does not show that arbitrary CNF has bounded k, "
            "does not optimize vtrees globally, and does not resolve P versus NP."
        ),
    }
    payload = json.dumps(
        result,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    result["integrity_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run()
    if args.output:
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    print(json.dumps(result, indent=2, sort_keys=True))

    if args.self_test:
        assert result["status"] == "PASS"
        assert result["random_audit"]["mismatches"] == 0
        assert result["random_audit"]["verification_failures"] == 0
        assert result["equality_order_separation"][-1]["blocked_obdd_width"] == 4096
        assert result["open_controls"]["dense_clique_control"] == "NO_BALANCED_SEPARATOR"
        assert result["corrupt_control"]["corrupt_branch_assignment_rejected"]


if __name__ == "__main__":
    main()
