#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass, field
from typing import Any, Iterable


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=list)


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()


class OpenResult(RuntimeError):
    pass


@dataclass
class Meter:
    work_limit: int
    table_limit: int
    certificate_limit: int
    work: int = 0
    table_entries: int = 0
    native_calls: int = 0
    row_xors: int = 0
    horn_scans: int = 0

    def charge(self, amount: int = 1) -> None:
        self.work += amount
        if self.work > self.work_limit:
            raise OpenResult("OPEN_WORK_BUDGET")

    def table(self, amount: int = 1) -> None:
        self.table_entries += amount
        if self.table_entries > self.table_limit:
            raise OpenResult("OPEN_TABLE_BUDGET")
        self.charge(amount)

    def certificate(self, obj: Any) -> None:
        if len(canonical_json(obj).encode()) > self.certificate_limit:
            raise OpenResult("OPEN_CERTIFICATE_VOLUME")


@dataclass(frozen=True)
class AffineFactor:
    factor_id: int
    variables: tuple[int, ...]
    rhs: int

    @property
    def language(self) -> str:
        return "AFFINE_GF2"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.factor_id,
            "language": self.language,
            "variables": list(self.variables),
            "rhs": self.rhs,
        }


@dataclass(frozen=True)
class HornFactor:
    factor_id: int
    body: tuple[int, ...]
    head: int | None

    @property
    def language(self) -> str:
        return "SINGLE_HEAD_HORN"

    @property
    def variables(self) -> tuple[int, ...]:
        values = set(self.body)
        if self.head is not None:
            values.add(self.head)
        return tuple(sorted(values))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.factor_id,
            "language": self.language,
            "body": list(self.body),
            "head": self.head,
        }


Factor = AffineFactor | HornFactor


@dataclass
class Module:
    module_id: int
    language: str
    factor_ids: tuple[int, ...]
    variables: tuple[int, ...]
    boundary: tuple[int, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "language": self.language,
            "factor_ids": list(self.factor_ids),
            "variables": list(self.variables),
            "boundary": list(self.boundary),
        }


@dataclass
class DSU:
    parent: dict[int, int] = field(default_factory=dict)

    def add(self, item: int) -> None:
        self.parent.setdefault(item, item)

    def find(self, item: int) -> int:
        root = item
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[item] != item:
            nxt = self.parent[item]
            self.parent[item] = root
            item = nxt
        return root

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if ra > rb:
            ra, rb = rb, ra
        self.parent[rb] = ra
        return True


@dataclass
class GF2Row:
    mask: int
    rhs: int
    original_provenance: int
    fixed_provenance: int

    def xor_with(self, other: "GF2Row", meter: Meter) -> None:
        self.mask ^= other.mask
        self.rhs ^= other.rhs
        self.original_provenance ^= other.original_provenance
        self.fixed_provenance ^= other.fixed_provenance
        meter.row_xors += 1
        meter.charge()

    def clone(self) -> "GF2Row":
        return GF2Row(self.mask, self.rhs, self.original_provenance, self.fixed_provenance)


def parse_factors(raw: Iterable[dict[str, Any]]) -> tuple[Factor, ...]:
    factors: list[Factor] = []
    seen: set[int] = set()
    for item in raw:
        factor_id = int(item["id"])
        if factor_id in seen:
            raise ValueError("duplicate factor id")
        seen.add(factor_id)
        language = item["language"]
        if language == "AFFINE_GF2":
            variables = tuple(sorted(set(int(v) for v in item["variables"])))
            if not variables or int(item["rhs"]) not in (0, 1):
                raise ValueError("invalid affine factor")
            factors.append(AffineFactor(factor_id, variables, int(item["rhs"])))
        elif language == "SINGLE_HEAD_HORN":
            body = tuple(sorted(set(int(v) for v in item.get("body", []))))
            head = item.get("head")
            head = None if head is None else int(head)
            if head is not None and head in body:
                raise ValueError("tautological Horn rule is not normalized")
            factors.append(HornFactor(factor_id, body, head))
        else:
            raise OpenResult("OPEN_LANGUAGE")
    return tuple(sorted(factors, key=lambda f: f.factor_id))


def factor_variables(factor: Factor) -> tuple[int, ...]:
    return factor.variables


def input_size(factors: tuple[Factor, ...]) -> int:
    variables = {v for factor in factors for v in factor_variables(factor)}
    occurrences = sum(len(factor_variables(factor)) for factor in factors)
    return max(2, len(factors) + len(variables) + occurrences)


def discover_modules(
    factors: tuple[Factor, ...], meter: Meter
) -> tuple[list[Module], dict[tuple[int, int], tuple[int, ...]], list[int], tuple[Any, ...]]:
    by_language: dict[str, list[Factor]] = {"AFFINE_GF2": [], "SINGLE_HEAD_HORN": []}
    for factor in factors:
        by_language[factor.language].append(factor)
        meter.charge()

    components: list[tuple[str, tuple[int, ...]]] = []
    factor_by_id = {factor.factor_id: factor for factor in factors}
    for language in ("AFFINE_GF2", "SINGLE_HEAD_HORN"):
        language_factors = by_language[language]
        dsu = DSU()
        for factor in language_factors:
            dsu.add(factor.factor_id)
        by_variable: dict[int, list[int]] = {}
        for factor in language_factors:
            for variable in factor_variables(factor):
                by_variable.setdefault(variable, []).append(factor.factor_id)
                meter.charge()
        for ids in by_variable.values():
            for factor_id in ids[1:]:
                dsu.union(ids[0], factor_id)
                meter.charge()
        groups: dict[int, list[int]] = {}
        for factor in language_factors:
            groups.setdefault(dsu.find(factor.factor_id), []).append(factor.factor_id)
        for ids in groups.values():
            components.append((language, tuple(sorted(ids))))

    components.sort(key=lambda item: (min(item[1]), item[0]))
    modules: list[Module] = []
    head_conflicts: list[tuple[Any, ...]] = []
    for module_id, (language, factor_ids) in enumerate(components):
        variables = tuple(sorted({v for fid in factor_ids for v in factor_variables(factor_by_id[fid])}))
        if language == "SINGLE_HEAD_HORN":
            heads: dict[int, list[int]] = {}
            for factor_id in factor_ids:
                factor = factor_by_id[factor_id]
                assert isinstance(factor, HornFactor)
                if factor.head is not None:
                    heads.setdefault(factor.head, []).append(factor_id)
            for head, ids in sorted(heads.items()):
                if len(ids) > 1:
                    head_conflicts.append((head, tuple(ids), module_id))
        modules.append(Module(module_id, language, factor_ids, variables))
    if head_conflicts:
        return modules, {}, [], tuple(head_conflicts)

    variable_modules: dict[int, set[int]] = {}
    for module in modules:
        for variable in module.variables:
            variable_modules.setdefault(variable, set()).add(module.module_id)
            meter.charge()

    edge_variables: dict[tuple[int, int], set[int]] = {}
    for variable, mids in variable_modules.items():
        if len(mids) > 2:
            raise OpenResult("OPEN_INTERFACE_HYPEREDGE")
        if len(mids) == 2:
            a, b = sorted(mids)
            edge_variables.setdefault((a, b), set()).add(variable)
    edges = {edge: tuple(sorted(values)) for edge, values in sorted(edge_variables.items())}

    graph_dsu = DSU()
    for module in modules:
        graph_dsu.add(module.module_id)
    adjacency: dict[int, set[int]] = {module.module_id: set() for module in modules}
    for a, b in edges:
        if not graph_dsu.union(a, b):
            raise OpenResult("OPEN_MODULE_CYCLE")
        adjacency[a].add(b)
        adjacency[b].add(a)
        meter.charge()

    for module in modules:
        boundary = set()
        for neighbor in adjacency[module.module_id]:
            boundary.update(edges[tuple(sorted((module.module_id, neighbor)))])
        module.boundary = tuple(sorted(boundary))

    roots: list[int] = []
    visited: set[int] = set()
    for module in modules:
        if module.module_id in visited:
            continue
        root = module.module_id
        roots.append(root)
        stack = [root]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            stack.extend(sorted(adjacency[current] - visited, reverse=True))
    return modules, edges, roots, ()


def affine_mask(variables: Iterable[int]) -> int:
    mask = 0
    for variable in variables:
        mask ^= 1 << (variable - 1)
    return mask


def gaussian_solve(
    factors: list[AffineFactor], module_variables: tuple[int, ...], fixed: dict[int, bool], meter: Meter
) -> dict[str, Any]:
    meter.native_calls += 1
    rows: list[GF2Row] = []
    for index, factor in enumerate(factors):
        rows.append(GF2Row(affine_mask(factor.variables), factor.rhs, 1 << index, 0))
        meter.charge(len(factor.variables))
    fixed_items = sorted(fixed.items())
    for index, (variable, value) in enumerate(fixed_items):
        rows.append(GF2Row(1 << (variable - 1), int(value), 0, 1 << index))
        meter.charge()
    matrix = [row.clone() for row in rows]
    pivot_row = 0
    for variable in sorted(module_variables):
        bit = 1 << (variable - 1)
        candidate = next((i for i in range(pivot_row, len(matrix)) if matrix[i].mask & bit), None)
        meter.charge(max(1, len(matrix) - pivot_row))
        if candidate is None:
            continue
        matrix[pivot_row], matrix[candidate] = matrix[candidate], matrix[pivot_row]
        for i in range(len(matrix)):
            if i != pivot_row and matrix[i].mask & bit:
                matrix[i].xor_with(matrix[pivot_row], meter)
        pivot_row += 1
    for row in matrix:
        if row.mask == 0 and row.rhs:
            return {"status": "UNSAT", "proof": {
                "original_provenance": row.original_provenance,
                "fixed_provenance": row.fixed_provenance,
            }}
    matrix = [row for row in matrix if row.mask]
    matrix.sort(key=lambda row: (row.mask & -row.mask, row.mask))
    assignment = {variable: False for variable in module_variables}
    for row in reversed(matrix):
        pivot = row.mask & -row.mask
        variable = pivot.bit_length()
        value = row.rhs
        rest = row.mask ^ pivot
        while rest:
            bit = rest & -rest
            value ^= int(assignment[bit.bit_length()])
            rest ^= bit
        assignment[variable] = bool(value)
    if any(assignment[variable] != value for variable, value in fixed.items()):
        raise AssertionError("affine solver violated fixed assignment")
    return {"status": "SAT", "assignment": {str(v): int(assignment[v]) for v in sorted(assignment)}}


def horn_solve(
    factors: list[HornFactor], module_variables: tuple[int, ...], fixed: dict[int, bool], meter: Meter
) -> dict[str, Any]:
    meter.native_calls += 1
    true_variables = {variable for variable, value in fixed.items() if value}
    fixed_false = {variable for variable, value in fixed.items() if not value}
    derivations: list[dict[str, int]] = []
    changed = True
    while changed:
        changed = False
        for factor in factors:
            meter.horn_scans += 1
            meter.charge(max(1, len(factor.body)))
            if all(variable in true_variables for variable in factor.body):
                if factor.head is None:
                    return {"status": "UNSAT", "proof": {
                        "conflict_factor": factor.factor_id,
                        "derivations": derivations,
                    }}
                if factor.head in fixed_false:
                    return {"status": "UNSAT", "proof": {
                        "conflict_factor": factor.factor_id,
                        "fixed_false_head": factor.head,
                        "derivations": derivations,
                    }}
                if factor.head not in true_variables:
                    true_variables.add(factor.head)
                    derivations.append({"factor_id": factor.factor_id, "head": factor.head})
                    changed = True
    assignment = {variable: variable in true_variables for variable in module_variables}
    return {"status": "SAT", "assignment": {str(v): int(assignment[v]) for v in sorted(assignment)},
            "derivations": derivations}


def native_solve(module: Module, factor_by_id: dict[int, Factor], fixed: dict[int, bool], meter: Meter) -> dict[str, Any]:
    if module.language == "AFFINE_GF2":
        factors = [factor_by_id[fid] for fid in module.factor_ids]
        assert all(isinstance(factor, AffineFactor) for factor in factors)
        return gaussian_solve(factors, module.variables, fixed, meter)  # type: ignore[arg-type]
    factors = [factor_by_id[fid] for fid in module.factor_ids]
    assert all(isinstance(factor, HornFactor) for factor in factors)
    return horn_solve(factors, module.variables, fixed, meter)  # type: ignore[arg-type]


def bits_key(variables: tuple[int, ...], assignment: dict[int, bool]) -> str:
    return "".join("1" if assignment[variable] else "0" for variable in variables)


def key_assignment(variables: tuple[int, ...], key: str) -> dict[int, bool]:
    return {variable: bit == "1" for variable, bit in zip(variables, key)}


def all_keys(variables: tuple[int, ...]) -> Iterable[str]:
    for bits in itertools.product("01", repeat=len(variables)):
        yield "".join(bits)


def balanced_tree(items: list[Any]) -> Any:
    if not items:
        return None
    if len(items) == 1:
        return items[0]
    split = len(items) // 2
    return [balanced_tree(items[:split]), balanced_tree(items[split:])]


def derive_variable_vtree(modules: list[Module], edges: dict[tuple[int, int], tuple[int, ...]], roots: list[int]) -> Any:
    adjacency: dict[int, set[int]] = {module.module_id: set() for module in modules}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    variable_modules: dict[int, list[int]] = {}
    for module in modules:
        for variable in module.variables:
            variable_modules.setdefault(variable, []).append(module.module_id)
    owner = {variable: min(mids) for variable, mids in variable_modules.items()}
    owned: dict[int, list[int]] = {module.module_id: [] for module in modules}
    for variable, module_id in owner.items():
        owned[module_id].append(variable)

    def rec(node: int, parent: int | None) -> Any:
        parts: list[Any] = []
        own_tree = balanced_tree(sorted(owned[node]))
        if own_tree is not None:
            parts.append(own_tree)
        for child in sorted(adjacency[node]):
            if child != parent:
                parts.append(rec(child, node))
        return balanced_tree(parts)

    return balanced_tree([rec(root, None) for root in sorted(roots)])


def vtree_leaves(tree: Any) -> list[int]:
    if tree is None:
        return []
    if isinstance(tree, int):
        return [tree]
    return vtree_leaves(tree[0]) + vtree_leaves(tree[1])


def evaluate_factor(factor: Factor, assignment: dict[int, bool]) -> bool:
    if isinstance(factor, AffineFactor):
        parity = 0
        for variable in factor.variables:
            parity ^= int(assignment[variable])
        return parity == factor.rhs
    if all(assignment[variable] for variable in factor.body):
        return factor.head is not None and assignment[factor.head]
    return True


def evaluate_all(factors: Iterable[Factor], assignment: dict[int, bool]) -> bool:
    return all(evaluate_factor(factor, assignment) for factor in factors)


def compile_portfolio(
    raw_factors: Iterable[dict[str, Any]], *, work_budget: int = 10_000_000,
    table_budget: int = 1_000_000, certificate_budget: int = 20_000_000,
    interface_limit: int | None = None,
) -> dict[str, Any]:
    meter = Meter(work_budget, table_budget, certificate_budget)
    try:
        factors = parse_factors(raw_factors)
        if not factors:
            return {"artifact_id": "C040-PORTFOLIO-GUIDED-MODULE-FOREST",
                    "schema": "janus.portfolio_module_forest.v1", "status": "SAT", "p_vs_np": "OPEN",
                    "factors": [], "modules": [], "edges": [], "roots": [], "variable_vtree": None,
                    "messages": [], "witness": {}, "cost": {"work_units": 0, "table_entries": 0,
                    "native_calls": 0}, "claim_boundary": "Empty admitted instance only."}
        size = input_size(factors)
        polynomial_limit = max(1, int(math.floor(math.log2(size))))
        if interface_limit is None:
            interface_limit = polynomial_limit
        if interface_limit > polynomial_limit:
            return {"artifact_id": "C040-PORTFOLIO-GUIDED-MODULE-FOREST", "status": "OPEN",
                    "reason": "OPEN_NONPOLYNOMIAL_INTERFACE_LIMIT", "requested_interface_limit": interface_limit,
                    "polynomial_interface_limit": polynomial_limit, "p_vs_np": "OPEN"}
        modules, edges, roots, head_conflicts = discover_modules(factors, meter)
        if head_conflicts:
            return {"artifact_id": "C040-PORTFOLIO-GUIDED-MODULE-FOREST", "status": "OPEN",
                    "reason": "OPEN_HEAD_CONFLICT",
                    "head_conflicts": [{"head": head, "factor_ids": list(ids), "module_id": module_id}
                                       for head, ids, module_id in head_conflicts],
                    "p_vs_np": "OPEN", "cost": {"work_units": meter.work}}
        for module in modules:
            if len(module.boundary) > interface_limit:
                return {"artifact_id": "C040-PORTFOLIO-GUIDED-MODULE-FOREST", "status": "OPEN",
                        "reason": "OPEN_INTERFACE_WIDTH", "module_id": module.module_id,
                        "boundary_size": len(module.boundary), "interface_limit": interface_limit,
                        "p_vs_np": "OPEN", "cost": {"work_units": meter.work}}

        factor_by_id = {factor.factor_id: factor for factor in factors}
        module_by_id = {module.module_id: module for module in modules}
        adjacency: dict[int, set[int]] = {module.module_id: set() for module in modules}
        for a, b in edges:
            adjacency[a].add(b)
            adjacency[b].add(a)
        records: dict[int, dict[str, Any]] = {}

        def compile_node(node_id: int, parent: int | None) -> None:
            module = module_by_id[node_id]
            children = [neighbor for neighbor in sorted(adjacency[node_id]) if neighbor != parent]
            for child in children:
                compile_node(child, node_id)
            parent_sep = () if parent is None else edges[tuple(sorted((node_id, parent)))]
            incident = module.boundary
            accepted_full: dict[str, dict[str, Any]] = {}
            blockers: dict[str, dict[str, Any]] = {}
            for full_key in all_keys(incident):
                meter.table()
                fixed = key_assignment(incident, full_key)
                native = native_solve(module, factor_by_id, fixed, meter)
                if native["status"] == "UNSAT":
                    blockers[full_key] = {"kind": "NATIVE_UNSAT", "certificate": native["proof"]}
                    continue
                child_keys: dict[str, str] = {}
                blocked = None
                for child in children:
                    separator = edges[tuple(sorted((node_id, child)))]
                    child_key = bits_key(separator, fixed)
                    child_keys[str(child)] = child_key
                    if not records[child]["table"][child_key]["value"]:
                        blocked = {"kind": "CHILD_FALSE", "child": child, "key": child_key}
                        break
                if blocked is not None:
                    blockers[full_key] = blocked
                    continue
                accepted_full[full_key] = {"native_assignment": native["assignment"], "child_keys": child_keys}

            table: dict[str, dict[str, Any]] = {}
            for parent_key in all_keys(parent_sep):
                candidates = [full_key for full_key in accepted_full
                              if bits_key(parent_sep, key_assignment(incident, full_key)) == parent_key]
                candidates.sort()
                if candidates:
                    table[parent_key] = {"value": True, "chosen_full_key": candidates[0]}
                else:
                    table[parent_key] = {"value": False, "blockers": {
                        full_key: blockers[full_key] for full_key in sorted(blockers)
                        if bits_key(parent_sep, key_assignment(incident, full_key)) == parent_key
                    }}
            record = {"module_id": node_id, "parent": parent, "children": children,
                      "parent_separator": list(parent_sep), "incident_boundary": list(incident),
                      "table": table, "accepted_full": accepted_full}
            record["digest"] = digest(record)
            meter.certificate(record)
            records[node_id] = record

        for root in roots:
            compile_node(root, None)
        unsat_root = next((root for root in roots if not records[root]["table"][""]["value"]), None)
        witness: dict[str, int] | None = None
        recovery: list[dict[str, Any]] = []
        if unsat_root is None:
            global_assignment: dict[int, bool] = {}

            def recover(node_id: int, parent_key: str) -> None:
                record = records[node_id]
                full_key = record["table"][parent_key]["chosen_full_key"]
                accepted = record["accepted_full"][full_key]
                native_assignment = {int(v): bool(value) for v, value in accepted["native_assignment"].items()}
                for variable, value in native_assignment.items():
                    if variable in global_assignment and global_assignment[variable] != value:
                        raise AssertionError("inconsistent recovered module assignments")
                    global_assignment[variable] = value
                recovery.append({"module_id": node_id, "parent_key": parent_key, "full_key": full_key,
                                 "native_assignment": accepted["native_assignment"]})
                for child_text, child_key in sorted(accepted["child_keys"].items(), key=lambda item: int(item[0])):
                    recover(int(child_text), child_key)

            for root in roots:
                recover(root, "")
            if not evaluate_all(factors, global_assignment):
                raise AssertionError("recovered witness does not satisfy input")
            witness = {str(v): int(global_assignment[v]) for v in sorted(global_assignment)}

        vtree = derive_variable_vtree(modules, edges, roots)
        expected_variables = sorted({v for factor in factors for v in factor_variables(factor)})
        leaves = vtree_leaves(vtree)
        if sorted(leaves) != expected_variables or len(leaves) != len(set(leaves)):
            raise AssertionError("derived variable vtree is invalid")
        output: dict[str, Any] = {
            "artifact_id": "C040-PORTFOLIO-GUIDED-MODULE-FOREST",
            "schema": "janus.portfolio_module_forest.v1", "status": "UNSAT" if unsat_root is not None else "SAT",
            "p_vs_np": "OPEN", "factors": [factor.to_dict() for factor in factors], "input_size": size,
            "polynomial_interface_limit": polynomial_limit, "interface_limit": interface_limit,
            "modules": [module.to_dict() for module in modules],
            "edges": [{"a": a, "b": b, "variables": list(values)} for (a, b), values in sorted(edges.items())],
            "roots": roots, "variable_vtree": vtree,
            "messages": [records[module_id] for module_id in sorted(records)], "witness": witness,
            "witness_recovery": recovery, "unsat_root": unsat_root,
            "cost": {"work_units": meter.work, "table_entries": meter.table_entries,
                     "native_calls": meter.native_calls, "row_xors": meter.row_xors,
                     "horn_scans": meter.horn_scans, "module_count": len(modules), "edge_count": len(edges),
                     "maximum_module_boundary": max((len(module.boundary) for module in modules), default=0)},
            "theorem": ("Raw tagged factors are partitioned deterministically into pure affine connected modules and "
                        "pure single-head Horn connected modules. If the discovered module interaction graph is a forest "
                        "and every module touches at most floor(log2 L) shared variables, exact bottom-up composition, "
                        "SAT recovery, UNSAT replay, discovery, and certificate volume are polynomial in input size L."),
            "claim_boundary": ("This is a discovered module-forest theorem, not a universal vtree theorem. Cyclic module "
                               "graphs, multi-producer Horn components, larger interfaces, unsupported languages, and "
                               "richer cross-language joins return OPEN. The derived variable vtree is a verified embedding "
                               "witness; the load-bearing algorithm is the certified module-forest dynamic program.")}
        output["cost"]["certificate_bytes"] = len(canonical_json(output).encode())
        output["integrity_sha256"] = digest({k: v for k, v in output.items() if k != "integrity_sha256"})
        meter.certificate(output)
        return output
    except OpenResult as exc:
        return {"artifact_id": "C040-PORTFOLIO-GUIDED-MODULE-FOREST", "status": "OPEN",
                "reason": str(exc), "p_vs_np": "OPEN",
                "cost": {"work_units": meter.work, "table_entries": meter.table_entries,
                         "native_calls": meter.native_calls, "row_xors": meter.row_xors,
                         "horn_scans": meter.horn_scans}}


def exhaustive_sat(factors: tuple[Factor, ...]) -> tuple[bool, dict[int, bool] | None]:
    variables = sorted({v for factor in factors for v in factor_variables(factor)})
    for bits in itertools.product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        if evaluate_all(factors, assignment):
            return True, assignment
    return False, None


def verify_affine_unsat(factors: list[AffineFactor], fixed: dict[int, bool], proof: dict[str, int]) -> bool:
    mask = rhs = 0
    for index, factor in enumerate(factors):
        if proof["original_provenance"] >> index & 1:
            mask ^= affine_mask(factor.variables)
            rhs ^= factor.rhs
    for index, (variable, value) in enumerate(sorted(fixed.items())):
        if proof["fixed_provenance"] >> index & 1:
            mask ^= 1 << (variable - 1)
            rhs ^= int(value)
    return mask == 0 and rhs == 1


def verify_horn_unsat(factors: list[HornFactor], fixed: dict[int, bool], proof: dict[str, Any]) -> bool:
    by_id = {factor.factor_id: factor for factor in factors}
    true_variables = {variable for variable, value in fixed.items() if value}
    fixed_false = {variable for variable, value in fixed.items() if not value}
    for item in proof.get("derivations", []):
        factor = by_id.get(item["factor_id"])
        if factor is None or factor.head != item["head"] or not all(v in true_variables for v in factor.body):
            return False
        if factor.head in fixed_false:
            return False
        true_variables.add(factor.head)
    conflict = by_id.get(proof.get("conflict_factor"))
    if conflict is None or not all(v in true_variables for v in conflict.body):
        return False
    return conflict.head is None or conflict.head in fixed_false


def verify_compilation(certificate: dict[str, Any]) -> bool:
    if certificate.get("p_vs_np") != "OPEN":
        return False
    if certificate.get("status") == "OPEN":
        return certificate.get("reason", "").startswith("OPEN_")
    if certificate.get("schema") != "janus.portfolio_module_forest.v1":
        return False
    expected_integrity = digest({k: v for k, v in certificate.items() if k != "integrity_sha256"})
    if expected_integrity != certificate.get("integrity_sha256"):
        return False
    try:
        factors = parse_factors(certificate["factors"])
    except (ValueError, OpenResult, KeyError, TypeError):
        return False
    replay = compile_portfolio(certificate["factors"], work_budget=100_000_000, table_budget=10_000_000,
                               certificate_budget=200_000_000, interface_limit=certificate["interface_limit"])
    if replay.get("status") != certificate.get("status"):
        return False
    for key in ("modules", "edges", "roots", "variable_vtree", "messages", "witness", "unsat_root"):
        if replay.get(key) != certificate.get(key):
            return False
    if certificate["status"] == "SAT":
        witness = {int(v): bool(value) for v, value in certificate["witness"].items()}
        return evaluate_all(factors, witness)
    factor_by_id = {factor.factor_id: factor for factor in factors}
    module_by_id = {module["module_id"]: module for module in certificate["modules"]}
    messages = {message["module_id"]: message for message in certificate["messages"]}
    for module_id, message in messages.items():
        module = module_by_id[module_id]
        incident = tuple(message["incident_boundary"])
        module_factors = [factor_by_id[fid] for fid in module["factor_ids"]]
        for entry in message["table"].values():
            if entry["value"]:
                continue
            for full_key, blocker in entry["blockers"].items():
                fixed = key_assignment(incident, full_key)
                if blocker["kind"] == "NATIVE_UNSAT":
                    if module["language"] == "AFFINE_GF2":
                        if not verify_affine_unsat(module_factors, fixed, blocker["certificate"]):  # type: ignore[arg-type]
                            return False
                    elif not verify_horn_unsat(module_factors, fixed, blocker["certificate"]):  # type: ignore[arg-type]
                        return False
                elif blocker["kind"] == "CHILD_FALSE":
                    child, key = blocker["child"], blocker["key"]
                    if child not in messages or messages[child]["table"][key]["value"]:
                        return False
                else:
                    return False
    return certificate.get("unsat_root") is not None


def make_affine(factor_id: int, variables: Iterable[int], rhs: int) -> dict[str, Any]:
    return {"id": factor_id, "language": "AFFINE_GF2", "variables": sorted(set(variables)), "rhs": rhs}


def make_horn(factor_id: int, body: Iterable[int], head: int | None) -> dict[str, Any]:
    return {"id": factor_id, "language": "SINGLE_HEAD_HORN", "body": sorted(set(body)), "head": head}


def random_forest_instance(rng: random.Random, max_variables: int = 9) -> list[dict[str, Any]]:
    module_count = rng.randint(1, 4)
    languages = ["AFFINE_GF2" if i % 2 == 0 else "SINGLE_HEAD_HORN" for i in range(module_count)]
    parents = [None] + [rng.randrange(i) for i in range(1, module_count)]
    next_variable = 1
    edge_var: dict[int, int] = {}
    for module_id in range(1, module_count):
        edge_var[module_id] = next_variable
        next_variable += 1
    private: dict[int, list[int]] = {}
    for module_id in range(module_count):
        count = rng.randint(1, 2)
        private[module_id] = list(range(next_variable, next_variable + count))
        next_variable += count
    if next_variable - 1 > max_variables:
        return random_forest_instance(rng, max_variables)
    incident: dict[int, list[int]] = {i: [] for i in range(module_count)}
    for child in range(1, module_count):
        parent = parents[child]
        assert parent is not None
        incident[child].append(edge_var[child])
        incident[parent].append(edge_var[child])
    factors: list[dict[str, Any]] = []
    factor_id = 0
    for module_id in range(module_count):
        variables = sorted(set(private[module_id] + incident[module_id]))
        if languages[module_id] == "AFFINE_GF2":
            factors.append(make_affine(factor_id, variables[:max(1, min(2, len(variables)))], rng.randrange(2)))
            factor_id += 1
            if rng.random() < 0.18:
                first = variables[0]
                factors.extend([make_affine(factor_id, [first], 0), make_affine(factor_id + 1, [first], 1)])
                factor_id += 2
        else:
            heads = list(private[module_id])
            rng.shuffle(heads)
            for head in heads:
                candidates = [v for v in variables if v != head]
                body = rng.sample(candidates, rng.randint(0, min(2, len(candidates))))
                factors.append(make_horn(factor_id, body, head))
                factor_id += 1
            if rng.random() < 0.18:
                body = rng.sample(variables, rng.randint(0, min(2, len(variables))))
                factors.append(make_horn(factor_id, body, None))
                factor_id += 1
    return factors


def head_conflict_family(n: int) -> list[dict[str, Any]]:
    factors: list[dict[str, Any]] = []
    factor_id = 0
    for i in range(n):
        a, b, q = 3 * i + 1, 3 * i + 2, 3 * i + 3
        factors.extend([make_horn(factor_id, [a], q), make_horn(factor_id + 1, [b], q)])
        factor_id += 2
    return factors


def interface_star(leaves: int) -> list[dict[str, Any]]:
    factors = [make_affine(0, list(range(1, leaves + 1)), 0)]
    for variable in range(1, leaves + 1):
        factors.append(make_horn(variable, [variable], leaves + variable))
    return factors


def alternating_cycle() -> list[dict[str, Any]]:
    return [make_affine(0, [1, 4], 0), make_horn(1, [1], 2),
            make_affine(2, [2, 3], 0), make_horn(3, [3], 4)]


def long_chain(modules: int) -> list[dict[str, Any]]:
    factors: list[dict[str, Any]] = []
    for module in range(modules):
        left = module if module > 0 else None
        right = module + 1 if module < modules - 1 else None
        private = modules + module + 1
        variables = [private] + ([left] if left else []) + ([right] if right else [])
        if module % 2 == 0:
            factors.append(make_affine(module, variables, 0))
        else:
            factors.append(make_horn(module, [v for v in variables if v != private], private))
    return factors


def run_self_test(seed: int = 400040) -> dict[str, Any]:
    rng = random.Random(seed)
    random_cases = sat_cases = unsat_cases = max_modules = max_boundary = 0
    for _ in range(350):
        raw = random_forest_instance(rng)
        expected_sat, _ = exhaustive_sat(parse_factors(raw))
        certificate = compile_portfolio(raw, work_budget=5_000_000, table_budget=200_000,
                                        certificate_budget=8_000_000)
        assert certificate["status"] in ("SAT", "UNSAT")
        assert verify_compilation(certificate)
        assert (certificate["status"] == "SAT") == expected_sat
        random_cases += 1
        sat_cases += int(expected_sat)
        unsat_cases += int(not expected_sat)
        max_modules = max(max_modules, certificate["cost"]["module_count"])
        max_boundary = max(max_boundary, certificate["cost"]["maximum_module_boundary"])

    chain = compile_portfolio(long_chain(180), work_budget=20_000_000, table_budget=1_000_000,
                              certificate_budget=40_000_000)
    assert chain["status"] in ("SAT", "UNSAT") and verify_compilation(chain)
    affine64 = [make_affine(i, [i + 1, ((i + 1) % 64) + 1], 0) for i in range(64)]
    affine64_certificate = compile_portfolio(affine64, work_budget=20_000_000,
                                             certificate_budget=20_000_000)
    assert affine64_certificate["status"] == "SAT" and verify_compilation(affine64_certificate)
    horn64 = [make_horn(i, [i + 1], i + 2) for i in range(63)]
    horn64_certificate = compile_portfolio(horn64, work_budget=20_000_000,
                                           certificate_budget=20_000_000)
    assert horn64_certificate["status"] == "SAT" and verify_compilation(horn64_certificate)
    head_open = compile_portfolio(head_conflict_family(64))
    assert head_open["status"] == "OPEN" and head_open["reason"] == "OPEN_HEAD_CONFLICT"
    cycle_open = compile_portfolio(alternating_cycle())
    assert cycle_open["status"] == "OPEN" and cycle_open["reason"] == "OPEN_MODULE_CYCLE"
    star_open = compile_portfolio(interface_star(24))
    assert star_open["status"] == "OPEN" and star_open["reason"] == "OPEN_INTERFACE_WIDTH"
    budget_open = compile_portfolio(long_chain(30), work_budget=10)
    assert budget_open["status"] == "OPEN" and budget_open["reason"] == "OPEN_WORK_BUDGET"
    language_open = compile_portfolio([{"id": 0, "language": "BETA_ACYCLIC", "variables": [1]}])
    assert language_open["status"] == "OPEN" and language_open["reason"] == "OPEN_LANGUAGE"
    corrupt = compile_portfolio(random_forest_instance(random.Random(seed + 1)))
    assert corrupt["status"] in ("SAT", "UNSAT") and verify_compilation(corrupt)
    corrupt["messages"][0]["digest"] = "0" * 64
    corrupt["integrity_sha256"] = digest({k: v for k, v in corrupt.items() if k != "integrity_sha256"})
    assert not verify_compilation(corrupt)

    result = {"artifact_id": "C040-PORTFOLIO-GUIDED-MODULE-FOREST", "status": "PASS",
              "p_vs_np": "OPEN", "seed": seed,
              "constructive_theorem": ("Deterministic discovery and exact proof-carrying compilation are polynomial "
                                       "for raw factor sets whose maximal pure affine and pure single-head Horn modules "
                                       "form a forest and each module has at most floor(log2 L) shared variables."),
              "random_cases": random_cases, "random_sat": sat_cases, "random_unsat": unsat_cases,
              "random_max_modules": max_modules, "random_max_boundary": max_boundary,
              "accepted_chain_modules": 180, "accepted_affine_core_variables": 64,
              "accepted_single_head_horn_variables": 64, "head_conflict_family": "OPEN_HEAD_CONFLICT",
              "alternating_module_cycle": "OPEN_MODULE_CYCLE", "wide_interface_star": "OPEN_INTERFACE_WIDTH",
              "budget_control": "OPEN_WORK_BUDGET", "unsupported_language": "OPEN_LANGUAGE",
              "corrupt_certificate": "REJECTED",
              "new_gate": "RICHER_MESSAGES_OR_POLYNOMIAL_DISCOVERY_BEYOND_ACYCLIC_LOG_INTERFACES",
              "claim_boundary": ("The result discovers and compiles one restricted module-forest class. It does not "
                                 "prove that arbitrary CNF admits such a decomposition, that the derived vtree has "
                                 "polynomial standard factor width, or that multi-producer Horn and mixed cyclic "
                                 "interfaces can be solved by the current portfolio.")}
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--seed", type=int, default=400040)
    args = parser.parse_args()
    result = run_self_test(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.self_test:
        assert result["status"] == "PASS"


if __name__ == "__main__":
    main()
