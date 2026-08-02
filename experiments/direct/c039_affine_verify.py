#!/usr/bin/env python3
from __future__ import annotations

import itertools
from typing import Any
from c039_affine_core import (
    Equation, Meter, Node, Row, VTree,
    assign_factors_and_boundaries, build_nodes, digest,
    evaluate_equation, join_rows, message_digest, project_rows,
    row_to_dict, solve_rows, validate_vtree, verify_row_provenance,
)


def _bits(mask: int):
    while mask:
        bit = mask & -mask
        yield bit
        mask ^= bit


def verify_compilation(certificate: dict[str, Any]) -> bool:
    if certificate.get('status') == 'OPEN':
        return certificate.get('p_vs_np') == 'OPEN'
    if certificate.get('schema') != 'janus.symbolic_affine_factor_compilation.v1':
        return False
    expected_integrity = digest({k: v for k, v in certificate.items() if k != 'integrity_sha256'})
    if certificate.get('integrity_sha256') != expected_integrity:
        return False
    equations = tuple(Equation(mask, rhs) for mask, rhs in certificate['equations'])
    variable_count = certificate['variable_count']
    variables = tuple(range(1, variable_count + 1))
    meter = Meter(10**9, 10**9, 10**9)
    tree = certificate['vtree']
    # JSON turns tuples into lists; restore recursively.
    def restore(t: Any) -> VTree:
        return int(t) if isinstance(t, int) else (restore(t[0]), restore(t[1]))
    tree = restore(tree)
    if not validate_vtree(tree, variables, meter):
        return False
    root, nodes = build_nodes(tree)
    assign_factors_and_boundaries(root, equations, meter)
    supplied = {record['node_id']: record for record in certificate['nodes']}
    rebuilt: dict[int, dict[str, Any]] = {}
    semantic_intern: dict[tuple[tuple[int, ...], str], int] = {}
    for node in nodes:
        if node.node_id not in supplied:
            return False
        rows, join_vars, sources = join_rows(node, rebuilt, equations)
        projected, contradiction = project_rows(rows, node.boundary, join_vars, meter)
        for row in projected:
            if not verify_row_provenance(row, equations):
                return False
        if contradiction is not None and not verify_row_provenance(contradiction, equations):
            return False
        expected_digest = message_digest(node.boundary, projected, contradiction)
        record = supplied[node.node_id]
        if tuple(record['boundary']) != node.boundary:
            return False
        if record['assigned_equations'] != sorted(node.assigned_equations):
            return False
        if record['join_vars'] != list(join_vars):
            return False
        if record['sources'] != sources:
            return False
        message = record['message']
        if message['digest'] != expected_digest:
            return False
        expected_status = 'FALSE' if contradiction is not None else 'AFFINE'
        if message['status'] != expected_status:
            return False
        if message['rows'] != [row_to_dict(row) for row in projected]:
            return False
        expected_contradiction = None if contradiction is None else row_to_dict(contradiction)
        if message['contradiction'] != expected_contradiction:
            return False
        key = (node.boundary, expected_digest)
        expected_merge = semantic_intern.get(key)
        if message.get('merge_with') != expected_merge:
            return False
        if expected_merge is None:
            semantic_intern[key] = node.node_id
        rebuilt[node.node_id] = record
    root_record = rebuilt[root.node_id]
    if root_record['message']['status'] == 'FALSE':
        proof = certificate.get('unsat_certificate')
        if proof is None:
            return False
        row = Row(**proof)
        if not (row.mask == 0 and row.rhs == 1 and verify_row_provenance(row, equations)):
            return False
        return certificate['status'] == 'UNSAT' and certificate.get('witness') is None
    witness_raw = certificate.get('witness')
    if witness_raw is None:
        return False
    witness = {int(v): bool(value) for v, value in witness_raw.items()}
    if set(witness) != set(variables):
        return False
    if not all(evaluate_equation(eq, witness) for eq in equations):
        return False
    trace_items = certificate.get('witness_recovery_trace', [])
    if len(trace_items) != len(nodes):
        return False
    trace = {item['node_id']: item for item in trace_items}
    if len(trace) != len(nodes):
        return False

    def check_recovery(node: Node, fixed: dict[int, bool]) -> bool:
        item = trace.get(node.node_id)
        if item is None:
            return False
        recorded_fixed = {int(v): bool(value) for v, value in item['boundary_assignment'].items()}
        if recorded_fixed != fixed:
            return False
        extension = {int(v): bool(value) for v, value in item['join_assignment'].items()}
        rows, join_vars, _ = join_rows(node, rebuilt, equations)
        if set(extension) != set(join_vars):
            return False
        if any(extension.get(v) != value for v, value in fixed.items()):
            return False
        if any(((sum(int(extension[bit.bit_length()]) for bit in _bits(row.mask)) & 1) != row.rhs) for row in rows):
            return False
        if node.left is None:
            var = node.leaves[0]
            recovered = extension.get(var, fixed.get(var, False))
            return witness[var] == recovered
        assert node.right is not None
        left_fixed = {v: extension[v] for v in node.left.boundary}
        right_fixed = {v: extension[v] for v in node.right.boundary}
        return check_recovery(node.left, left_fixed) and check_recovery(node.right, right_fixed)

    return certificate['status'] == 'SAT' and check_recovery(root, {})


def verify_node_semantics_small(certificate: dict[str, Any]) -> bool:
    if certificate.get('status') not in ('SAT', 'UNSAT'):
        return False
    equations = tuple(Equation(mask, rhs) for mask, rhs in certificate['equations'])
    n = certificate['variable_count']
    if n > 10:
        raise ValueError('small-domain validator only')
    def restore(t: Any) -> VTree:
        return int(t) if isinstance(t, int) else (restore(t[0]), restore(t[1]))
    root, nodes = build_nodes(restore(certificate['vtree']))
    meter = Meter(10**9, 10**9, 10**9)
    assign_factors_and_boundaries(root, equations, meter)
    records = {record['node_id']: record for record in certificate['nodes']}

    def subtree_equations(node: Node) -> list[int]:
        out = list(node.assigned_equations)
        if node.left is not None:
            assert node.right is not None
            out.extend(subtree_equations(node.left))
            out.extend(subtree_equations(node.right))
        return out

    for node in nodes:
        record = records[node.node_id]
        message = record['message']
        boundary = node.boundary
        interior = tuple(v for v in node.leaves if v not in set(boundary))
        factor_ids = subtree_equations(node)
        for boundary_bits in itertools.product((False, True), repeat=len(boundary)):
            fixed = dict(zip(boundary, boundary_bits))
            expected = False
            for interior_bits in itertools.product((False, True), repeat=len(interior)):
                assignment = fixed | dict(zip(interior, interior_bits))
                if all(evaluate_equation(equations[idx], assignment) for idx in factor_ids):
                    expected = True
                    break
            if message['status'] == 'FALSE':
                actual = False
            else:
                actual = True
                for row_data in message['rows']:
                    row = Row(**row_data)
                    parity = 0
                    for bit in _bits(row.mask):
                        parity ^= int(fixed[bit.bit_length()])
                    if parity != row.rhs:
                        actual = False
                        break
            if actual != expected:
                return False
    return True


def affine_separator(a: tuple[Equation, ...], b: tuple[Equation, ...], n: int) -> dict[str, Any]:
    meter = Meter(10**7, 10**7, 10**7)

    def find(left: tuple[Equation, ...], right: tuple[Equation, ...], direction: str) -> dict[str, Any] | None:
        left_rows = [Row(eq.mask, eq.rhs, 1 << i) for i, eq in enumerate(left)]
        variables = tuple(range(1, n + 1))
        for idx, target in enumerate(right):
            # A relation entails target iff adding its affine negation is inconsistent.
            test = left_rows + [Row(target.mask, target.rhs ^ 1, 0)]
            assignment = solve_rows(test, variables, {}, meter)
            if assignment is not None:
                return {
                    'status': 'SEPARATOR',
                    'direction': direction,
                    'violated_row': idx,
                    'assignment': {str(v): int(assignment[v]) for v in variables},
                    'work_units': meter.work,
                }
        return None

    separator = find(a, b, 'A_NOT_B') or find(b, a, 'B_NOT_A')
    if separator is not None:
        return separator
    return {
        'status': 'MERGE',
        'reason': 'MUTUAL_AFFINE_ROW_ENTAILMENT',
        'work_units': meter.work,
    }
