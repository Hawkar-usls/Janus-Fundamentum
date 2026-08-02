#!/usr/bin/env python3
from __future__ import annotations

from typing import Any
from c039_affine_core import (
    Equation, Meter, Node, OpenBudget, Row, VTree,
    assign_factors_and_boundaries, build_nodes, canonical_json, digest,
    evaluate_equation, gauss_jordan, greedy_vtree, join_rows,
    message_digest, project_rows, row_to_dict, semantic_rows,
    solve_rows, validate_vtree, verify_row_provenance,
)


def compile_affine(
    equations: tuple[Equation, ...],
    variable_count: int,
    *,
    supplied_vtree: VTree | None = None,
    work_budget: int = 4_000_000,
    row_budget: int = 100_000,
    certificate_budget: int = 8_000_000,
    language: str = 'AFFINE_GF2',
) -> dict[str, Any]:
    if language != 'AFFINE_GF2':
        return {'status': 'OPEN', 'reason': 'OPEN_LANGUAGE', 'language': language, 'p_vs_np': 'OPEN'}
    variables = tuple(range(1, variable_count + 1))
    meter = Meter(work_budget, row_budget, certificate_budget)
    try:
        if supplied_vtree is None:
            tree = greedy_vtree(equations, variables, meter)
            discovery = 'DETERMINISTIC_EQUATION_COOCCURRENCE'
        else:
            tree = supplied_vtree
            discovery = 'SUPPLIED_BUT_VALIDATED_AND_CHARGED'
        if not validate_vtree(tree, variables, meter):
            return {'status': 'OPEN', 'reason': 'INVALID_VTREE', 'p_vs_np': 'OPEN'}
        root, nodes = build_nodes(tree)
        meter.charge(len(nodes))
        assign_factors_and_boundaries(root, equations, meter)
        records: dict[int, dict[str, Any]] = {}
        semantic_intern: dict[tuple[tuple[int, ...], str], int] = {}
        for node in nodes:
            before = meter.work
            rows, join_vars, sources = join_rows(node, records, equations)
            projected, contradiction = project_rows(rows, node.boundary, join_vars, meter)
            for row in projected:
                if not verify_row_provenance(row, equations):
                    raise AssertionError('bad provenance')
            if contradiction is not None and not verify_row_provenance(contradiction, equations):
                raise AssertionError('bad contradiction provenance')
            msg_digest = message_digest(node.boundary, projected, contradiction)
            key = (node.boundary, msg_digest)
            merge_with = semantic_intern.get(key)
            if merge_with is None:
                semantic_intern[key] = node.node_id
            message = {
                'status': 'FALSE' if contradiction is not None else 'AFFINE',
                'boundary': list(node.boundary),
                'rows': [row_to_dict(row) for row in projected],
                'contradiction': None if contradiction is None else row_to_dict(contradiction),
                'digest': msg_digest,
                'merge_with': merge_with,
            }
            record = {
                'node_id': node.node_id,
                'leaves': list(node.leaves),
                'boundary': list(node.boundary),
                'left': None if node.left is None else node.left.node_id,
                'right': None if node.right is None else node.right.node_id,
                'assigned_equations': list(sorted(node.assigned_equations)),
                'join_vars': list(join_vars),
                'eliminated_vars': [v for v in join_vars if v not in set(node.boundary)],
                'sources': sources,
                'message': message,
                'work_delta': meter.work - before,
            }
            records[node.node_id] = record
            meter.certificate(record)

        root_record = records[root.node_id]
        witness = None
        recovery_trace: list[dict[str, Any]] = []
        if root_record['message']['status'] != 'FALSE':
            final_assignment: dict[int, bool] = {}

            def recover(node: Node, boundary_assignment: dict[int, bool]) -> bool:
                rows, join_vars, _ = join_rows(node, records, equations)
                extension = solve_rows(rows, join_vars, boundary_assignment, meter)
                if extension is None:
                    return False
                recovery_trace.append({
                    'node_id': node.node_id,
                    'boundary_assignment': {str(v): int(boundary_assignment[v]) for v in sorted(boundary_assignment)},
                    'join_assignment': {str(v): int(extension[v]) for v in sorted(extension)},
                })
                if node.left is None:
                    var = node.leaves[0]
                    final_assignment[var] = extension.get(var, boundary_assignment.get(var, False))
                    return True
                assert node.right is not None
                left_boundary = {v: extension[v] for v in node.left.boundary}
                right_boundary = {v: extension[v] for v in node.right.boundary}
                return recover(node.left, left_boundary) and recover(node.right, right_boundary)

            if not recover(root, {}):
                raise AssertionError('witness recovery failed')
            for v in variables:
                final_assignment.setdefault(v, False)
            if not all(evaluate_equation(eq, final_assignment) for eq in equations):
                raise AssertionError('recovered witness invalid')
            witness = {str(v): int(final_assignment[v]) for v in variables}

        output: dict[str, Any] = {
            'artifact_id': 'C039-PROOF-CARRYING-SYMBOLIC-AFFINE-FACTORS',
            'schema': 'janus.symbolic_affine_factor_compilation.v1',
            'status': 'UNSAT' if root_record['message']['status'] == 'FALSE' else 'SAT',
            'p_vs_np': 'OPEN',
            'language': 'AFFINE_GF2',
            'variable_count': variable_count,
            'equations': [[eq.mask, eq.rhs] for eq in equations],
            'vtree': tree,
            'vtree_discovery': discovery,
            'root_node': root.node_id,
            'nodes': [records[i] for i in sorted(records)],
            'witness': witness,
            'witness_recovery_trace': recovery_trace,
            'unsat_certificate': root_record['message']['contradiction'],
            'cost': {
                'work_units': meter.work,
                'row_xors': meter.row_xors,
                'pair_scores': meter.pair_scores,
                'projection_calls': meter.projection_calls,
                'solve_calls': meter.solve_calls,
                'emitted_rows': meter.emitted_rows,
                'node_count': len(nodes),
            },
            'theorem': (
                'Affine GF(2) factors are closed under proof-carrying conjoin and existential projection. '
                'For every charged vtree, each region message is a canonical RREF relation with at most '
                'the boundary-variable count many rows; deterministic bottom-up compilation, SAT witness '
                'recovery, and XOR-provenance UNSAT certificates are polynomial in the input and certificate volume.'
            ),
            'claim_boundary': (
                'This is a complete symbolic factor compiler for affine systems only. General Horn-affine or '
                'NAND3+NEQ mixtures remain OPEN_LANGUAGE; no representation-specific compression is promoted '
                'to a universal SAT algorithm.'
            ),
        }
        output['cost']['certificate_bytes'] = len(canonical_json(output).encode())
        output['integrity_sha256'] = digest({k: v for k, v in output.items() if k != 'integrity_sha256'})
        meter.certificate(output)
        return output
    except OpenBudget as exc:
        return {
            'artifact_id': 'C039-PROOF-CARRYING-SYMBOLIC-AFFINE-FACTORS',
            'status': 'OPEN',
            'reason': str(exc),
            'p_vs_np': 'OPEN',
            'cost': {
                'work_units': meter.work,
                'row_xors': meter.row_xors,
                'pair_scores': meter.pair_scores,
                'projection_calls': meter.projection_calls,
                'solve_calls': meter.solve_calls,
                'emitted_rows': meter.emitted_rows,
            },
        }
