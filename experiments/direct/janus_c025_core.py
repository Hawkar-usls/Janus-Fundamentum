"""C025 CNF primitives, certified normalization, and residual automaton."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]

DEFAULT_SEED = 250025
CANONICAL_SEED_SHA256 = "44e21fdc9d37fda98e2e73b0c9eb268bd04cdca9d84d0519e4f1166be22b46fc"
BASE_COMMIT = "994dd693604d1f557c367acc7b1b3ed6083ee4a8"


def canonical_clause(raw: Iterable[int]) -> Clause | None:
    literals = set(int(x) for x in raw)
    if any(-lit in literals for lit in literals):
        return None
    return tuple(sorted(literals, key=lambda lit: (abs(lit), lit < 0)))


def canonical_cnf(raw: Iterable[Iterable[int]]) -> CNF:
    clauses: set[Clause] = set()
    for clause in raw:
        canonical = canonical_clause(clause)
        if canonical is not None:
            clauses.add(canonical)
    return tuple(sorted(clauses, key=lambda clause: (len(clause), clause)))


def variables(formula: CNF) -> list[int]:
    return sorted({abs(lit) for clause in formula for lit in clause})


def satisfies(formula: CNF, assignment: dict[int, bool]) -> bool:
    return all(
        any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause)
        for clause in formula
    )


def cofactor(formula: CNF, variable: int, value: bool) -> CNF:
    true_literal = variable if value else -variable
    false_literal = -true_literal
    output = []
    for clause in formula:
        if true_literal in clause:
            continue
        if false_literal in clause:
            output.append(tuple(lit for lit in clause if lit != false_literal))
        else:
            output.append(clause)
    return canonical_cnf(output)


def restrict_formula(formula: CNF, fixed: dict[int, bool]) -> CNF:
    residual = formula
    for variable, value in sorted(fixed.items()):
        residual = cofactor(residual, variable, value)
    return residual


def brute_force(formula: CNF, universe: list[int]) -> tuple[bool, dict[int, bool] | None, int]:
    checks = 0
    for bits in itertools.product((False, True), repeat=len(universe)):
        checks += 1
        assignment = dict(zip(universe, bits))
        if satisfies(formula, assignment):
            return True, assignment, checks
    return False, None, checks


@dataclass(frozen=True)
class SubsumptionStep:
    removed: Clause
    subsumer: Clause


@dataclass(frozen=True)
class NormalizationCertificate:
    input_hash: str
    output_hash: str
    steps: tuple[SubsumptionStep, ...]


def cnf_hash(formula: CNF) -> str:
    return hashlib.sha256(json.dumps(formula, separators=(",", ":")).encode("utf-8")).hexdigest()


def normalize_subsumption(formula: CNF) -> tuple[CNF, NormalizationCertificate]:
    formula = canonical_cnf(formula)
    retained: list[Clause] = []
    steps: list[SubsumptionStep] = []
    for clause in sorted(formula, key=lambda c: (len(c), c)):
        subsumer = next((candidate for candidate in retained if set(candidate).issubset(clause)), None)
        if subsumer is not None:
            steps.append(SubsumptionStep(clause, subsumer))
        else:
            retained.append(clause)
    output = canonical_cnf(retained)
    certificate = NormalizationCertificate(cnf_hash(formula), cnf_hash(output), tuple(steps))
    if not verify_normalization(formula, output, certificate):
        raise AssertionError("generated subsumption certificate failed")
    return output, certificate


def verify_normalization(original: CNF, normalized: CNF, certificate: NormalizationCertificate) -> bool:
    original = canonical_cnf(original)
    normalized = canonical_cnf(normalized)
    if certificate.input_hash != cnf_hash(original) or certificate.output_hash != cnf_hash(normalized):
        return False
    removed = set()
    for step in certificate.steps:
        if step.removed not in original or step.subsumer not in original:
            return False
        if not set(step.subsumer).issubset(step.removed):
            return False
        removed.add(step.removed)
    return canonical_cnf(clause for clause in original if clause not in removed) == normalized


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True)
class BDDNode:
    variable: int
    low: int
    high: int


@dataclass
class AutomatonStats:
    status: str = "RUNNING"
    recursive_calls: int = 0
    memo_hits: int = 0
    residual_states: int = 0
    transition_checks: int = 0
    normalization_certificates: int = 0
    subsumption_steps: int = 0
    bdd_nodes: int = 0
    max_frontier_states: int = 0
    frontier_counts: dict[int, int] = field(default_factory=dict)
    error: str | None = None


@dataclass
class AutomatonResult:
    status: str
    sat: bool | None
    witness: dict[int, bool] | None
    root: int | None
    nodes: dict[int, BDDNode]
    stats: AutomatonStats


def compile_residual_automaton(formula: CNF, order: list[int], state_budget: int) -> AutomatonResult:
    formula, root_certificate = normalize_subsumption(formula)
    if len(order) != len(set(order)):
        raise ValueError("duplicate variable in order")
    if not set(variables(formula)).issubset(order):
        raise ValueError("order omits formula variables")
    stats = AutomatonStats(normalization_certificates=1, subsumption_steps=len(root_certificate.steps))
    memo: dict[tuple[int, CNF], int] = {}
    nodes: dict[int, BDDNode] = {}
    unique_nodes: dict[tuple[int, int, int], int] = {}
    next_node = 2
    depth_states: dict[int, set[CNF]] = {}

    def mk(variable: int, low: int, high: int) -> int:
        nonlocal next_node
        if low == high:
            return low
        key = (variable, low, high)
        if key in unique_nodes:
            return unique_nodes[key]
        node_id = next_node
        next_node += 1
        unique_nodes[key] = node_id
        nodes[node_id] = BDDNode(variable, low, high)
        return node_id

    def rec(depth: int, residual: CNF) -> int:
        stats.recursive_calls += 1
        key = (depth, residual)
        if key in memo:
            stats.memo_hits += 1
            return memo[key]
        if stats.residual_states >= state_budget:
            raise BudgetExceeded(f"residual state budget {state_budget} exceeded")
        stats.residual_states += 1
        depth_states.setdefault(depth, set()).add(residual)
        if not residual:
            memo[key] = 1
            return 1
        if () in residual:
            memo[key] = 0
            return 0
        if depth >= len(order):
            raise AssertionError("nonterminal residual after full order")
        variable = order[depth]
        low_raw = cofactor(residual, variable, False)
        low, low_certificate = normalize_subsumption(low_raw)
        high_raw = cofactor(residual, variable, True)
        high, high_certificate = normalize_subsumption(high_raw)
        for raw, normalized, certificate in ((low_raw, low, low_certificate), (high_raw, high, high_certificate)):
            stats.transition_checks += 1
            stats.normalization_certificates += 1
            stats.subsumption_steps += len(certificate.steps)
            if not verify_normalization(raw, normalized, certificate):
                raise AssertionError("transition normalization failed verification")
        low_id = rec(depth + 1, low)
        high_id = rec(depth + 1, high)
        node_id = mk(variable, low_id, high_id)
        memo[key] = node_id
        return node_id

    try:
        root = rec(0, formula)
    except BudgetExceeded as error:
        stats.status = "OPEN"
        stats.error = str(error)
        stats.bdd_nodes = len(nodes)
        stats.frontier_counts = {depth: len(states) for depth, states in sorted(depth_states.items())}
        stats.max_frontier_states = max(stats.frontier_counts.values(), default=0)
        return AutomatonResult("OPEN", None, None, None, nodes, stats)

    stats.status = "EXACT"
    stats.bdd_nodes = len(nodes)
    stats.frontier_counts = {depth: len(states) for depth, states in sorted(depth_states.items())}
    stats.max_frontier_states = max(stats.frontier_counts.values(), default=0)
    assignment = {variable: False for variable in order}
    node_id = root
    while node_id not in (0, 1):
        node = nodes[node_id]
        if node.low != 0:
            assignment[node.variable] = False
            node_id = node.low
        else:
            assignment[node.variable] = True
            node_id = node.high
    witness = assignment if node_id == 1 else None
    sat = root != 0
    if sat and (witness is None or not satisfies(formula, witness)):
        raise AssertionError("automaton witness failed formula")
    return AutomatonResult("EXACT", sat, witness, root, nodes, stats)


def truth_vector(formula: CNF, order: list[int]) -> tuple[int, ...]:
    return tuple(int(satisfies(formula, dict(zip(order, bits)))) for bits in itertools.product((False, True), repeat=len(order)))


def semantic_residual_profile(formula: CNF, order: list[int]) -> dict[int, int]:
    vector = truth_vector(formula, order)
    n = len(order)
    profile = {}
    for depth in range(n + 1):
        block_size = 1 << (n - depth)
        profile[depth] = len({vector[start:start + block_size] for start in range(0, len(vector), block_size)})
    return profile


def normalized_syntactic_profile(formula: CNF, order: list[int]) -> dict[int, int]:
    frontier = {canonical_cnf(formula)}
    profile = {0: 1}
    for depth, variable in enumerate(order, start=1):
        next_frontier = set()
        for residual in frontier:
            for value in (False, True):
                raw = cofactor(residual, variable, value)
                normalized, certificate = normalize_subsumption(raw)
                if not verify_normalization(raw, normalized, certificate):
                    raise AssertionError("profile normalization failed")
                next_frontier.add(normalized)
        frontier = next_frontier
        profile[depth] = len(frontier)
    return profile
