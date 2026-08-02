#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from dataclasses import dataclass, field
from typing import Any, Iterable

VTree = int | tuple['VTree', 'VTree']


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), default=list)


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()


class OpenBudget(RuntimeError):
    pass


@dataclass
class Meter:
    work_limit: int
    row_limit: int
    certificate_limit: int
    work: int = 0
    row_xors: int = 0
    pair_scores: int = 0
    projection_calls: int = 0
    solve_calls: int = 0
    emitted_rows: int = 0

    def charge(self, amount: int = 1) -> None:
        self.work += amount
        if self.work > self.work_limit:
            raise OpenBudget('WORK_BUDGET')

    def xor(self) -> None:
        self.row_xors += 1
        self.charge()

    def rows(self, count: int) -> None:
        self.emitted_rows += count
        if count > self.row_limit or self.emitted_rows > self.row_limit:
            raise OpenBudget('MESSAGE_ROW_BUDGET')

    def certificate(self, obj: Any) -> None:
        if len(canonical_json(obj).encode()) > self.certificate_limit:
            raise OpenBudget('CERTIFICATE_VOLUME_BUDGET')


@dataclass(frozen=True)
class Equation:
    mask: int
    rhs: int

    def support(self) -> tuple[int, ...]:
        return tuple(i + 1 for i in range(self.mask.bit_length()) if self.mask >> i & 1)


@dataclass
class Row:
    mask: int
    rhs: int
    provenance: int

    def xor_with(self, other: 'Row', meter: Meter | None = None) -> None:
        self.mask ^= other.mask
        self.rhs ^= other.rhs
        self.provenance ^= other.provenance
        if meter is not None:
            meter.xor()

    def clone(self) -> 'Row':
        return Row(self.mask, self.rhs, self.provenance)


@dataclass
class Node:
    node_id: int
    tree: VTree
    leaves: tuple[int, ...]
    left: 'Node | None' = None
    right: 'Node | None' = None
    parent: 'Node | None' = None
    assigned_equations: list[int] = field(default_factory=list)
    boundary: tuple[int, ...] = ()


def leaves(tree: VTree) -> tuple[int, ...]:
    return (tree,) if isinstance(tree, int) else leaves(tree[0]) + leaves(tree[1])


def build_nodes(tree: VTree) -> tuple[Node, list[Node]]:
    nodes: list[Node] = []

    def rec(t: VTree, parent: Node | None = None) -> Node:
        if isinstance(t, int):
            node = Node(len(nodes), t, (t,), parent=parent)
            nodes.append(node)
            return node
        placeholder = Node(-1, t, tuple(sorted(leaves(t))), parent=parent)
        left = rec(t[0], placeholder)
        right = rec(t[1], placeholder)
        placeholder.node_id = len(nodes)
        placeholder.left = left
        placeholder.right = right
        nodes.append(placeholder)
        return placeholder

    root = rec(tree)
    return root, nodes


def validate_vtree(tree: VTree, variables: tuple[int, ...], meter: Meter) -> bool:
    seen = leaves(tree)
    meter.charge(len(seen) + len(variables))
    return len(seen) == len(set(seen)) and tuple(sorted(seen)) == tuple(sorted(variables))


def greedy_vtree(equations: tuple[Equation, ...], variables: tuple[int, ...], meter: Meter) -> VTree:
    clusters: list[tuple[VTree, frozenset[int]]] = [(v, frozenset((v,))) for v in variables]
    supports = [frozenset(eq.support()) for eq in equations]
    if not clusters:
        raise ValueError('empty variable set')
    while len(clusters) > 1:
        best: tuple[Any, int, int] | None = None
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                a, b = clusters[i][1], clusters[j][1]
                score = 0
                for support in supports:
                    meter.pair_scores += 1
                    meter.charge()
                    if support & a and support & b:
                        score += 1
                union = a | b
                key = (-score, len(union), tuple(sorted(union)), i, j)
                if best is None or key < best[0]:
                    best = (key, i, j)
        assert best is not None
        _, i, j = best
        ta, a = clusters[i]
        tb, b = clusters[j]
        merged = ((ta, tb), a | b)
        clusters = [x for k, x in enumerate(clusters) if k not in (i, j)] + [merged]
    return clusters[0][0]


def node_for_scope(root: Node, scope: frozenset[int]) -> Node:
    if not scope:
        return root
    if root.left is None or root.right is None:
        return root
    left_set = frozenset(root.left.leaves)
    right_set = frozenset(root.right.leaves)
    if scope <= left_set:
        return node_for_scope(root.left, scope)
    if scope <= right_set:
        return node_for_scope(root.right, scope)
    return root


def assign_factors_and_boundaries(root: Node, equations: tuple[Equation, ...], meter: Meter) -> None:
    for idx, equation in enumerate(equations):
        scope = frozenset(equation.support())
        meter.charge(max(1, len(scope)))
        node_for_scope(root, scope).assigned_equations.append(idx)

    def top_down(node: Node, inherited: frozenset[int]) -> None:
        inside = frozenset(node.leaves)
        node.boundary = tuple(sorted(inside & inherited))
        local_scope: set[int] = set()
        for idx in node.assigned_equations:
            local_scope.update(equations[idx].support())
            meter.charge()
        carry = inherited | frozenset(local_scope)
        if node.left is not None:
            top_down(node.left, carry)
            assert node.right is not None
            top_down(node.right, carry)

    top_down(root, frozenset())


def row_to_dict(row: Row) -> dict[str, int]:
    return {'mask': row.mask, 'rhs': row.rhs, 'provenance': row.provenance}


def semantic_rows(rows: Iterable[Row]) -> list[list[int]]:
    return [[row.mask, row.rhs] for row in rows]


def gauss_jordan(rows: list[Row], pivot_vars: tuple[int, ...], meter: Meter) -> tuple[list[Row], Row | None]:
    matrix = [row.clone() for row in rows]
    pivot_row = 0
    for var in pivot_vars:
        bit = 1 << (var - 1)
        candidate = next((i for i in range(pivot_row, len(matrix)) if matrix[i].mask & bit), None)
        meter.charge(max(1, len(matrix) - pivot_row))
        if candidate is None:
            continue
        matrix[pivot_row], matrix[candidate] = matrix[candidate], matrix[pivot_row]
        for i in range(len(matrix)):
            if i != pivot_row and matrix[i].mask & bit:
                matrix[i].xor_with(matrix[pivot_row], meter)
        pivot_row += 1
    nonzero: list[Row] = []
    for row in matrix:
        meter.charge()
        if row.mask == 0:
            if row.rhs:
                return [], row
        else:
            nonzero.append(row)
    nonzero.sort(key=lambda row: (row.mask & -row.mask, row.mask, row.rhs))
    return nonzero, None


def project_rows(rows: list[Row], keep_vars: tuple[int, ...], all_join_vars: tuple[int, ...], meter: Meter) -> tuple[list[Row], Row | None]:
    meter.projection_calls += 1
    keep = frozenset(keep_vars)
    eliminate = tuple(v for v in sorted(all_join_vars) if v not in keep)
    reduced, contradiction = gauss_jordan(rows, eliminate, meter)
    if contradiction is not None:
        return [], contradiction
    eliminate_mask = sum(1 << (v - 1) for v in eliminate)
    residual = [row for row in reduced if row.mask & eliminate_mask == 0]
    canonical, contradiction = gauss_jordan(residual, tuple(sorted(keep_vars)), meter)
    if contradiction is not None:
        return [], contradiction
    meter.rows(len(canonical))
    return canonical, None


def evaluate_equation(equation: Equation, assignment: dict[int, bool]) -> bool:
    parity = 0
    mask = equation.mask
    while mask:
        bit = mask & -mask
        var = bit.bit_length()
        parity ^= int(assignment[var])
        mask ^= bit
    return parity == equation.rhs


def xor_original_equations(provenance: int, equations: tuple[Equation, ...]) -> tuple[int, int]:
    mask = rhs = 0
    for idx, equation in enumerate(equations):
        if provenance >> idx & 1:
            mask ^= equation.mask
            rhs ^= equation.rhs
    return mask, rhs


def verify_row_provenance(row: Row, equations: tuple[Equation, ...]) -> bool:
    return xor_original_equations(row.provenance, equations) == (row.mask, row.rhs)


def solve_rows(rows: list[Row], variables: tuple[int, ...], fixed: dict[int, bool], meter: Meter) -> dict[int, bool] | None:
    meter.solve_calls += 1
    units = [Row(1 << (v - 1), int(value), 0) for v, value in sorted(fixed.items())]
    reduced, contradiction = gauss_jordan(rows + units, tuple(sorted(variables)), meter)
    if contradiction is not None:
        return None
    assignment = {v: False for v in variables}
    for row in reversed(reduced):
        pivot_bit = row.mask & -row.mask
        pivot_var = pivot_bit.bit_length()
        value = row.rhs
        rest = row.mask ^ pivot_bit
        while rest:
            bit = rest & -rest
            value ^= int(assignment[bit.bit_length()])
            rest ^= bit
        assignment[pivot_var] = bool(value)
    if any(assignment.get(v) != bool(value) for v, value in fixed.items()):
        return None
    return assignment


def message_digest(boundary: tuple[int, ...], rows: list[Row], contradiction: Row | None) -> str:
    payload = {
        'boundary': list(boundary),
        'status': 'FALSE' if contradiction is not None else 'AFFINE',
        'rows': [] if contradiction is not None else semantic_rows(rows),
    }
    return digest(payload)


def join_rows(node: Node, records: dict[int, dict[str, Any]], equations: tuple[Equation, ...]) -> tuple[list[Row], tuple[int, ...], list[dict[str, Any]]]:
    rows: list[Row] = []
    sources: list[dict[str, Any]] = []
    join_vars: set[int] = set(node.boundary)
    if node.left is not None:
        assert node.right is not None
        for child in (node.left, node.right):
            child_record = records[child.node_id]
            join_vars.update(child.boundary)
            if child_record['message']['status'] == 'FALSE':
                contradiction = child_record['message']['contradiction']
                rows.append(Row(0, 1, contradiction['provenance']))
            else:
                for row_data in child_record['message']['rows']:
                    rows.append(Row(**row_data))
            sources.append({'kind': 'CHILD_MESSAGE', 'node_id': child.node_id, 'digest': child_record['message']['digest']})
    for idx in sorted(node.assigned_equations):
        equation = equations[idx]
        rows.append(Row(equation.mask, equation.rhs, 1 << idx))
        join_vars.update(equation.support())
        sources.append({'kind': 'LOCAL_EQUATION', 'equation_id': idx})
    return rows, tuple(sorted(join_vars)), sources

