#!/usr/bin/env python3
"""
C024 JANUS Fracture Channel Core

Exact software-only audit of the instance-specific polymorphism-fracture route.

For an arbitrary source 3-CNF F on variables x_1..x_n:

1. introduce c_i with NEQ(x_i,c_i);
2. encode every source clause as NAND3 over complements of its literals;
3. add semantically tautological NAND3 connectors so every NAND3 constraint
   belongs to one same-language region.

The resulting same-language region graph is a star:
- one central NAND3 region;
- n NEQ leaf regions;
- treewidth 1;
- cycle rank 0;
- minimum vertex cover 1.

Nevertheless, eliminating the NEQ leaves recovers the original 3-CNF exactly.
Thus low fracture-graph topology does not imply tractability.

The semantic payload lies in n independent complement channels.  Their GF(2)
rank is n, and the exact UNSAT 3-variable core becomes satisfiable if any one
NEQ channel is removed.

The experiment also attacks channel rank as a universal hardness measure:
large monotone positive 3-CNFs have the same rank-n star fracture but are
trivially satisfiable by the all-true assignment.

No general SAT oracle is used by the construction or normalization.  Brute
force appears only as an independent checker on small frozen fixtures.

No swarm, device, NAS runtime, Telegram backend, external LLM, BCI,
biological sample, physical P-N junction, miner, or quantum device is touched.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
NandScope = tuple[int, int, int]
NeqScope = tuple[int, int]

DEFAULT_SEED = 440223
CANONICAL_SEED_SHA256 = "44e21fdc9d37fda98e2e73b0c9eb268bd04cdca9d84d0519e4f1166be22b46fc"
BASE_COMMIT = "994dd693604d1f557c367acc7b1b3ed6083ee4a8"


def canonical_clause(raw: Iterable[int]) -> Clause | None:
    literals = set(int(x) for x in raw)
    if any(-lit in literals for lit in literals):
        return None
    return tuple(sorted(literals, key=lambda x: (abs(x), x < 0)))


def canonical_cnf(raw: Iterable[Iterable[int]]) -> CNF:
    clauses: set[Clause] = set()
    for clause in raw:
        canonical = canonical_clause(clause)
        if canonical is not None:
            clauses.add(canonical)
    return tuple(sorted(clauses))


def variables(formula: CNF) -> list[int]:
    return sorted({abs(lit) for clause in formula for lit in clause})


def satisfies_cnf(formula: CNF, assignment: dict[int, bool]) -> bool:
    return all(
        any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause)
        for clause in formula
    )


def brute_force_cnf(formula: CNF, n: int) -> tuple[bool, dict[int, bool] | None, int]:
    checks = 0
    for bits in itertools.product((False, True), repeat=n):
        checks += 1
        assignment = dict(zip(range(1, n + 1), bits))
        if satisfies_cnf(formula, assignment):
            return True, assignment, checks
    return False, None, checks


@dataclass(frozen=True)
class FractureInstance:
    source_n: int
    source_formula: CNF
    neq_constraints: tuple[NeqScope, ...]
    nand_constraints: tuple[NandScope, ...]
    source_nand_count: int
    connector_nand_count: int

    @property
    def total_variables(self) -> int:
        return 2 * self.source_n

    @property
    def total_constraints(self) -> int:
        return len(self.neq_constraints) + len(self.nand_constraints)


def complement_variable(n: int, variable: int) -> int:
    return n + variable


def literal_complement_node(n: int, literal: int) -> int:
    return complement_variable(n, literal) if literal > 0 else abs(literal)


def reduce_to_nand_neq(
    formula: CNF,
    n: int,
    connect_nand_region: bool = True,
) -> FractureInstance:
    formula = canonical_cnf(formula)
    if any(len(clause) != 3 for clause in formula):
        raise ValueError("C024 reduction requires exact 3-literal clauses")

    neq = tuple((i, complement_variable(n, i)) for i in range(1, n + 1))
    nand: list[NandScope] = []

    for clause in formula:
        nand.append(tuple(literal_complement_node(n, lit) for lit in clause))

    source_count = len(nand)
    connector_count = 0
    if connect_nand_region and n > 1:
        x1 = 1
        c1 = complement_variable(n, 1)
        for i in range(2, n + 1):
            nand.append((c1, x1, complement_variable(n, i)))
            nand.append((c1, x1, i))
            connector_count += 2

    return FractureInstance(
        source_n=n,
        source_formula=formula,
        neq_constraints=neq,
        nand_constraints=tuple(nand),
        source_nand_count=source_count,
        connector_nand_count=connector_count,
    )


def satisfies_fracture(
    instance: FractureInstance,
    assignment: dict[int, bool],
    dropped_neq_index: int | None = None,
) -> bool:
    for index, (x, c) in enumerate(instance.neq_constraints):
        if index == dropped_neq_index:
            continue
        if assignment[x] == assignment[c]:
            return False
    for a, b, c in instance.nand_constraints:
        if assignment[a] and assignment[b] and assignment[c]:
            return False
    return True


def brute_force_fracture(
    instance: FractureInstance,
    dropped_neq_index: int | None = None,
) -> tuple[bool, dict[int, bool] | None, int]:
    checks = 0
    universe = list(range(1, instance.total_variables + 1))
    for bits in itertools.product((False, True), repeat=len(universe)):
        checks += 1
        assignment = dict(zip(universe, bits))
        if satisfies_fracture(instance, assignment, dropped_neq_index):
            return True, assignment, checks
    return False, None, checks


def extend_source_witness(source_assignment: dict[int, bool], n: int) -> dict[int, bool]:
    extended = dict(source_assignment)
    for i in range(1, n + 1):
        extended[complement_variable(n, i)] = not source_assignment[i]
    return extended


def project_fracture_witness(assignment: dict[int, bool], n: int) -> dict[int, bool]:
    return {i: assignment[i] for i in range(1, n + 1)}


def nand_scope_to_source_clause(scope: NandScope, n: int) -> Clause | None:
    clause = []
    for node in scope:
        if 1 <= node <= n:
            clause.append(-node)
        elif n < node <= 2 * n:
            clause.append(node - n)
        else:
            raise ValueError("node outside reduction universe")
    return canonical_clause(clause)


def eliminate_neq_leaves(instance: FractureInstance) -> CNF:
    clauses = []
    for scope in instance.nand_constraints:
        clause = nand_scope_to_source_clause(scope, instance.source_n)
        if clause is not None:
            clauses.append(clause)
    return canonical_cnf(clauses)


class DSU:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


@dataclass
class FractureGraph:
    nand_regions: list[list[int]]
    neq_regions: list[list[int]]
    simple_edges: set[tuple[int, int]]
    attachment_multiplicity: dict[tuple[int, int], int]
    variable_attachments: dict[int, tuple[int, int]]

    @property
    def vertices(self) -> int:
        return len(self.nand_regions) + len(self.neq_regions)

    @property
    def edges(self) -> int:
        return len(self.simple_edges)

    @property
    def connected(self) -> bool:
        if self.vertices == 0:
            return True
        adjacency = {v: set() for v in range(self.vertices)}
        for a, b in self.simple_edges:
            adjacency[a].add(b)
            adjacency[b].add(a)
        seen = {0}
        stack = [0]
        while stack:
            v = stack.pop()
            for nxt in adjacency[v]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return len(seen) == self.vertices

    @property
    def cyclomatic_number(self) -> int:
        if self.vertices == 0:
            return 0
        components = 1 if self.connected else self._component_count()
        return self.edges - self.vertices + components

    def _component_count(self) -> int:
        adjacency = {v: set() for v in range(self.vertices)}
        for a, b in self.simple_edges:
            adjacency[a].add(b)
            adjacency[b].add(a)
        unseen = set(adjacency)
        count = 0
        while unseen:
            count += 1
            root = unseen.pop()
            stack = [root]
            while stack:
                v = stack.pop()
                for nxt in adjacency[v]:
                    if nxt in unseen:
                        unseen.remove(nxt)
                        stack.append(nxt)
        return count

    @property
    def is_tree(self) -> bool:
        return self.connected and self.edges == self.vertices - 1

    @property
    def exact_treewidth_for_star(self) -> int:
        if self.vertices <= 1:
            return 0
        if not self.is_tree:
            raise ValueError("exact_treewidth_for_star called on non-tree")
        return 1

    @property
    def minimum_vertex_cover_for_star(self) -> int:
        if self.vertices <= 1:
            return 0
        if len(self.nand_regions) == 1 and len(self.neq_regions) >= 1:
            return 1
        raise ValueError("not the certified star shape")


def build_fracture_graph(instance: FractureInstance) -> FractureGraph:
    nand_count = len(instance.nand_constraints)
    neq_count = len(instance.neq_constraints)
    nand_dsu = DSU(nand_count)
    neq_dsu = DSU(neq_count)
    by_variable_nand: dict[int, list[int]] = {}
    by_variable_neq: dict[int, list[int]] = {}

    for index, scope in enumerate(instance.nand_constraints):
        for variable in scope:
            by_variable_nand.setdefault(variable, []).append(index)
    for index, scope in enumerate(instance.neq_constraints):
        for variable in scope:
            by_variable_neq.setdefault(variable, []).append(index)

    for indices in by_variable_nand.values():
        for index in indices[1:]:
            nand_dsu.union(indices[0], index)
    for indices in by_variable_neq.values():
        for index in indices[1:]:
            neq_dsu.union(indices[0], index)

    nand_groups: dict[int, list[int]] = {}
    for index in range(nand_count):
        nand_groups.setdefault(nand_dsu.find(index), []).append(index)
    neq_groups: dict[int, list[int]] = {}
    for index in range(neq_count):
        neq_groups.setdefault(neq_dsu.find(index), []).append(index)

    nand_regions = list(nand_groups.values())
    neq_regions = list(neq_groups.values())
    nand_region_of_constraint = {
        constraint: region
        for region, constraints in enumerate(nand_regions)
        for constraint in constraints
    }
    neq_region_of_constraint = {
        constraint: region
        for region, constraints in enumerate(neq_regions)
        for constraint in constraints
    }

    edges: set[tuple[int, int]] = set()
    multiplicity: dict[tuple[int, int], int] = {}
    attachments: dict[int, tuple[int, int]] = {}
    offset = len(nand_regions)

    for variable in range(1, instance.total_variables + 1):
        nand_indices = by_variable_nand.get(variable, [])
        neq_indices = by_variable_neq.get(variable, [])
        if not nand_indices or not neq_indices:
            continue
        nand_region = nand_region_of_constraint[nand_indices[0]]
        neq_region = offset + neq_region_of_constraint[neq_indices[0]]
        edge = (nand_region, neq_region)
        edges.add(edge)
        multiplicity[edge] = multiplicity.get(edge, 0) + 1
        attachments[variable] = edge

    return FractureGraph(
        nand_regions=nand_regions,
        neq_regions=neq_regions,
        simple_edges=edges,
        attachment_multiplicity=multiplicity,
        variable_attachments=attachments,
    )


def gf2_rank(rows: list[int]) -> int:
    rows = [row for row in rows if row]
    rank = 0
    while rows:
        pivot = max(rows)
        rows.remove(pivot)
        if pivot == 0:
            continue
        bit = pivot.bit_length() - 1
        reduced = []
        for row in rows:
            if (row >> bit) & 1:
                row ^= pivot
            if row:
                reduced.append(row)
        rows = reduced
        rank += 1
    return rank


def neq_channel_rank(instance: FractureInstance) -> int:
    rows = []
    for x, c in instance.neq_constraints:
        rows.append((1 << (x - 1)) | (1 << (c - 1)))
    return gf2_rank(rows)


def planted_3cnf(rng: random.Random, n: int, m: int) -> tuple[CNF, dict[int, bool]]:
    planted = {v: bool(rng.getrandbits(1)) for v in range(1, n + 1)}
    clauses = []
    for _ in range(m):
        chosen = rng.sample(range(1, n + 1), 3)
        literals = [v if rng.random() < 0.5 else -v for v in chosen]
        if not any(planted[abs(lit)] == (lit > 0) for lit in literals):
            variable = chosen[0]
            literals[0] = variable if planted[variable] else -variable
        clause = canonical_clause(literals)
        assert clause is not None
        clauses.append(clause)
    formula = canonical_cnf(clauses)
    assert satisfies_cnf(formula, planted)
    return formula, planted


def complete_unsat_3core() -> CNF:
    clauses = []
    for bits in itertools.product((False, True), repeat=3):
        clause = canonical_clause(
            -index if bits[index - 1] else index
            for index in range(1, 4)
        )
        assert clause is not None
        clauses.append(clause)
    formula = canonical_cnf(clauses)
    truth, _, _ = brute_force_cnf(formula, 3)
    assert not truth
    return formula


def monotone_positive_3cnf(rng: random.Random, n: int, m: int) -> CNF:
    clauses = []
    for _ in range(m):
        chosen = rng.sample(range(1, n + 1), 3)
        clause = canonical_clause(chosen)
        assert clause is not None
        clauses.append(clause)
    formula = canonical_cnf(clauses)
    all_true = {v: True for v in range(1, n + 1)}
    assert satisfies_cnf(formula, all_true)
    return formula


def random_exact_3cnf(rng: random.Random, n: int, m: int) -> CNF:
    clauses = []
    for _ in range(m):
        chosen = rng.sample(range(1, n + 1), 3)
        clause = canonical_clause(v if rng.random() < 0.5 else -v for v in chosen)
        assert clause is not None
        clauses.append(clause)
    return canonical_cnf(clauses)


def audit_balanced_exact(rng: random.Random, cases: int = 160) -> dict[str, Any]:
    core = complete_unsat_3core()
    sat_count = unsat_count = 0
    reduction_mismatches = witness_failures = recovery_failures = 0
    topology_failures = rank_failures = 0
    total_source_checks = total_fracture_checks = 0

    for index in range(cases):
        n = rng.randint(3, 8)
        if index % 2 == 0:
            formula, _ = planted_3cnf(rng, n, rng.randint(n, 4 * n))
            expected = True
        else:
            noise, _ = planted_3cnf(rng, n, rng.randint(1, max(1, n)))
            formula = canonical_cnf(core + noise)
            expected = False

        source_truth, source_witness, source_checks = brute_force_cnf(formula, n)
        total_source_checks += source_checks
        if source_truth != expected:
            raise AssertionError("frozen balanced generator truth mismatch")

        instance = reduce_to_nand_neq(formula, n, True)
        fracture_truth, fracture_witness, fracture_checks = brute_force_fracture(instance)
        total_fracture_checks += fracture_checks
        if source_truth != fracture_truth:
            reduction_mismatches += 1
        if eliminate_neq_leaves(instance) != formula:
            recovery_failures += 1

        graph = build_fracture_graph(instance)
        if not (
            len(graph.nand_regions) == 1
            and len(graph.neq_regions) == n
            and graph.is_tree
            and graph.exact_treewidth_for_star == 1
            and graph.cyclomatic_number == 0
            and graph.minimum_vertex_cover_for_star == 1
        ):
            topology_failures += 1
        if neq_channel_rank(instance) != n:
            rank_failures += 1

        if source_truth:
            sat_count += 1
            assert source_witness is not None
            if not satisfies_fracture(instance, extend_source_witness(source_witness, n)):
                witness_failures += 1
            if fracture_witness is None or not satisfies_cnf(
                formula, project_fracture_witness(fracture_witness, n)
            ):
                witness_failures += 1
        else:
            unsat_count += 1

    return {
        "cases": cases,
        "sat": sat_count,
        "unsat": unsat_count,
        "reduction_mismatches": reduction_mismatches,
        "witness_failures": witness_failures,
        "exact_recovery_failures": recovery_failures,
        "topology_failures": topology_failures,
        "channel_rank_failures": rank_failures,
        "total_source_assignments_checked": total_source_checks,
        "total_fracture_assignments_checked": total_fracture_checks,
    }


def audit_linear_scaling(rng: random.Random) -> dict[str, Any]:
    rows = []
    for n in (8, 16, 32, 64, 128, 256):
        formula = random_exact_3cnf(rng, n, 4 * n)
        instance = reduce_to_nand_neq(formula, n, True)
        graph = build_fracture_graph(instance)
        recovered = eliminate_neq_leaves(instance)
        rows.append({
            "source_variables": n,
            "source_clauses": len(formula),
            "neq_constraints": len(instance.neq_constraints),
            "source_nand_constraints": instance.source_nand_count,
            "connector_nand_constraints": instance.connector_nand_count,
            "total_constraints": instance.total_constraints,
            "nand_regions": len(graph.nand_regions),
            "neq_regions": len(graph.neq_regions),
            "fracture_vertices": graph.vertices,
            "fracture_edges": graph.edges,
            "fracture_treewidth": graph.exact_treewidth_for_star,
            "fracture_cycle_rank": graph.cyclomatic_number,
            "fracture_vertex_cover": graph.minimum_vertex_cover_for_star,
            "channel_rank": neq_channel_rank(instance),
            "recovery_exact": recovered == formula,
            "maximum_attachment_multiplicity": max(graph.attachment_multiplicity.values()),
        })
    return {
        "rows": rows,
        "all_linear_shape": all(
            row["nand_regions"] == 1
            and row["neq_regions"] == row["source_variables"]
            and row["fracture_edges"] == row["source_variables"]
            and row["channel_rank"] == row["source_variables"]
            and row["recovery_exact"]
            for row in rows
        ),
    }


def audit_channel_essentiality() -> dict[str, Any]:
    formula = complete_unsat_3core()
    instance = reduce_to_nand_neq(formula, 3, True)
    base_truth, _, base_checks = brute_force_fracture(instance)
    dropped = []
    for index in range(3):
        truth, witness, checks = brute_force_fracture(instance, dropped_neq_index=index)
        dropped.append({
            "dropped_channel": index + 1,
            "becomes_sat": truth,
            "checks": checks,
            "spurious_witness": (
                {str(k): int(v) for k, v in sorted(witness.items())}
                if witness is not None else None
            ),
        })
    return {
        "source": "complete 3-variable UNSAT core",
        "base_unsat": not base_truth,
        "base_checks": base_checks,
        "channels": 3,
        "every_single_channel_is_essential": all(row["becomes_sat"] for row in dropped),
        "dropped_results": dropped,
    }


def audit_rank_not_hardness(rng: random.Random) -> dict[str, Any]:
    rows = []
    for n in (12, 24, 48, 96, 192):
        formula = monotone_positive_3cnf(rng, n, 4 * n)
        instance = reduce_to_nand_neq(formula, n, True)
        graph = build_fracture_graph(instance)
        all_true_source = {v: True for v in range(1, n + 1)}
        extended = extend_source_witness(all_true_source, n)
        rows.append({
            "source_variables": n,
            "channel_rank": neq_channel_rank(instance),
            "fracture_treewidth": graph.exact_treewidth_for_star,
            "fracture_cycle_rank": graph.cyclomatic_number,
            "all_true_source_witness": satisfies_cnf(formula, all_true_source),
            "extended_fracture_witness": satisfies_fracture(instance, extended),
        })
    return {
        "rows": rows,
        "all_high_rank_but_trivial": all(
            row["channel_rank"] == row["source_variables"]
            and row["all_true_source_witness"]
            and row["extended_fracture_witness"]
            for row in rows
        ),
        "verdict": "Linear semantic-channel rank is not by itself a hardness certificate.",
    }


def audit_normalization_idempotence(rng: random.Random, cases: int = 100) -> dict[str, Any]:
    failures = hash_mismatches = 0
    for _ in range(cases):
        n = rng.randint(3, 20)
        formula = random_exact_3cnf(rng, n, rng.randint(n, 5 * n))
        first = eliminate_neq_leaves(reduce_to_nand_neq(formula, n, True))
        second = eliminate_neq_leaves(reduce_to_nand_neq(first, n, True))
        if first != formula or second != first:
            failures += 1
        source_hash = hashlib.sha256(json.dumps(formula, separators=(",", ":")).encode()).hexdigest()
        recovered_hash = hashlib.sha256(json.dumps(first, separators=(",", ":")).encode()).hexdigest()
        if source_hash != recovered_hash:
            hash_mismatches += 1
    return {
        "cases": cases,
        "failures": failures,
        "hash_mismatches": hash_mismatches,
        "result": "NEQ-leaf elimination is exact and idempotent on the reduction image.",
    }


def run(seed: int = DEFAULT_SEED) -> dict[str, Any]:
    rng = random.Random(seed)
    balanced = audit_balanced_exact(rng)
    scaling = audit_linear_scaling(rng)
    essential = audit_channel_essentiality()
    easy_rank = audit_rank_not_hardness(rng)
    idempotence = audit_normalization_idempotence(rng)

    assertions = {
        "balanced_equivalence": balanced["reduction_mismatches"] == 0 and balanced["witness_failures"] == 0,
        "balanced_exact_recovery": balanced["exact_recovery_failures"] == 0,
        "balanced_star_topology": balanced["topology_failures"] == 0,
        "balanced_full_channel_rank": balanced["channel_rank_failures"] == 0,
        "linear_scaling_shape": scaling["all_linear_shape"],
        "every_channel_essential_on_unsat_core": essential["base_unsat"] and essential["every_single_channel_is_essential"],
        "rank_not_universal_hardness": easy_rank["all_high_rank_but_trivial"],
        "normalization_idempotent": idempotence["failures"] == 0 and idempotence["hash_mismatches"] == 0,
    }
    status = "PASS" if all(assertions.values()) else "FAIL"

    result = {
        "artifact_id": "C024-JANUS-FRACTURE-CHANNEL-CORE",
        "status": status,
        "research_status": "EXPLORATORY_SOFTWARE_ONLY_NOT_CANONICAL",
        "seed": seed,
        "holdout_seed": 440223,
        "canonical_seed_sha256": CANONICAL_SEED_SHA256,
        "base_repository_commit": BASE_COMMIT,
        "software_only": True,
        "swarm_touched": False,
        "devices_touched": False,
        "nas_touched": False,
        "external_models_called": False,
        "general_sat_oracle_called": False,
        "balanced_exact_audit": balanced,
        "linear_scaling_audit": scaling,
        "channel_essentiality": essential,
        "rank_not_hardness_control": easy_rank,
        "normalization_idempotence": idempotence,
        "assertions": assertions,
        "theorem_candidate": {
            "name": "Fracture-Star Normalization Lemma",
            "statement": "Every exact 3-CNF F with n variables and m clauses has a linear-size NAND3+NEQ encoding I(F) whose same-language region graph is a star of treewidth 1, cycle rank 0, and minimum vertex cover 1, while exact elimination of the NEQ leaves recovers F.",
            "status": "PROVED_WITHIN_EXPLICIT_ENCODING_DEFINITION",
        },
        "located_bottleneck": {
            "name": "NONLINEAR_QUOTIENT_CORE",
            "definition": "The residual relation after all certified bijective or Schaefer-preserving fracture leaves are eliminated.",
            "exact_result_here": "On the NAND3+NEQ reduction image, the nonlinear quotient core is exactly the original 3-CNF.",
        },
        "distance_to_p_equals_np": {
            "mathematical_status": "UNCHANGED_OPEN",
            "next_exact_target": "Find an instance-specific proof-carrying decomposition of the nonlinear quotient core, or a polynomial invariant stronger than topology or rank.",
        },
        "claim_boundary": "C024 does not prove P=NP, P!=NP, or an unrestricted lower bound.",
    }
    clean = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result["integrity"] = {"sha256": hashlib.sha256(clean.encode()).hexdigest()}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run(args.seed)
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.self_test and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
