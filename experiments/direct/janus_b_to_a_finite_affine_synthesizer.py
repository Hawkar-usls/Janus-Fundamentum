#!/usr/bin/env python3
"""JANUS reverse B->A finite-affine synthesizer.

The producer receives only RAW Boolean CNF.  It is not told a graph family,
constraint name, charge labels, block width, or a preferred modulus.

Deterministic discovery grammar:
  RAW CNF
    -> exact clause-scope relations
    -> bounded truth-table replay per discovered scope
    -> search small prime carriers for an exact affine representation
    -> choose the strictly smallest exact equation/carrier resource key
    -> assemble the recovered local equations globally
    -> exact finite-field consistency / contradiction certificate
    -> replay against the original CNF.

Local color/shape resemblance never admits a result.  Every local relation must
replay its source clauses exactly on the Boolean domain, and the final SAT/UNSAT
claim must carry an independently checkable witness/certificate.

Complexity firewall: local relation recovery enumerates 2^w Boolean tuples for
scope width w.  Therefore this implementation is polynomial only for bounded
scope width.  It is NOT an arbitrary-CNF polynomial SAT algorithm.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

PRIMES = (2, 3, 5, 7)
MAX_SCOPE_WIDTH = 8


def _dot(left, right, modulus: int) -> int:
    return sum(a * b for a, b in zip(left, right)) % modulus


def _rref(rows: list[list[int]], modulus: int, ncols: int):
    matrix = [[value % modulus for value in row[:ncols]] for row in rows]
    pivots: list[int] = []
    pivot_row = 0
    for col in range(ncols):
        hit = next((r for r in range(pivot_row, len(matrix)) if matrix[r][col] % modulus), None)
        if hit is None:
            continue
        matrix[pivot_row], matrix[hit] = matrix[hit], matrix[pivot_row]
        inverse = pow(matrix[pivot_row][col], -1, modulus)
        matrix[pivot_row] = [(value * inverse) % modulus for value in matrix[pivot_row]]
        for r in range(len(matrix)):
            if r == pivot_row:
                continue
            factor = matrix[r][col] % modulus
            if factor:
                matrix[r] = [
                    (value - factor * pivot_value) % modulus
                    for value, pivot_value in zip(matrix[r], matrix[pivot_row])
                ]
        pivots.append(col)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return matrix, pivots


def _nullspace(rows: list[list[int]], modulus: int, ncols: int) -> list[tuple[int, ...]]:
    rref, pivots = _rref(rows, modulus, ncols)
    pivot_set = set(pivots)
    free_columns = [col for col in range(ncols) if col not in pivot_set]
    basis_vectors = []
    for free in free_columns:
        vector = [0] * ncols
        vector[free] = 1
        for row_index in range(len(pivots) - 1, -1, -1):
            pivot = pivots[row_index]
            row = rref[row_index]
            total = sum(row[col] * vector[col] for col in range(pivot + 1, ncols)) % modulus
            vector[pivot] = (-total) % modulus
        basis_vectors.append(tuple(vector))
    return basis_vectors


def _normalize_equation(coefficients: tuple[int, ...], rhs: int, modulus: int):
    first = next((value % modulus for value in coefficients if value % modulus), None)
    if first is None:
        raise AssertionError("ZERO_AFFINE_EQUATION")
    scale = pow(first, -1, modulus)
    coeffs = tuple((value * scale) % modulus for value in coefficients)
    return coeffs, (rhs * scale) % modulus


def _scope_groups(raw_clauses):
    cnf = base.canon_cnf(raw_clauses)
    if not cnf:
        raise AssertionError("EMPTY_INPUT")
    groups: dict[tuple[int, ...], list[base.Clause]] = defaultdict(list)
    for clause in cnf:
        scope = tuple(sorted({abs(literal) for literal in clause}))
        if not scope:
            raise AssertionError("EMPTY_CLAUSE_NOT_IN_SCOPE_GRAMMAR")
        if len(scope) > MAX_SCOPE_WIDTH:
            raise AssertionError(f"SCOPE_WIDTH_EXCEEDS_BOUND:{len(scope)}")
        if len(scope) != len(clause):
            raise AssertionError("REPEATED_VARIABLE_LITERAL_NOT_IN_SCOPE_GRAMMAR")
        groups[scope].append(clause)
    return cnf, {scope: base.canon_cnf(clauses) for scope, clauses in groups.items()}


def _allowed_boolean_tuples(scope: tuple[int, ...], local_cnf: base.CNF):
    allowed = []
    for bits in product((0, 1), repeat=len(scope)):
        assignment = dict(zip(scope, bits))
        if all(
            any(bool(assignment[abs(literal)]) == (literal > 0) for literal in clause)
            for clause in local_cnf
        ):
            allowed.append(tuple(bits))
    return tuple(allowed)


def _truth_table_cnf(scope: tuple[int, ...], allowed: tuple[tuple[int, ...], ...]):
    allowed_set = set(allowed)
    clauses = []
    for bits in product((0, 1), repeat=len(scope)):
        if bits in allowed_set:
            continue
        # This clause is false on exactly the forbidden Boolean tuple.
        clause = tuple(variable if bit == 0 else -variable for variable, bit in zip(scope, bits))
        clauses.append(clause)
    return base.canon_cnf(clauses)


def _affine_candidates(scope: tuple[int, ...], local_cnf: base.CNF):
    allowed = _allowed_boolean_tuples(scope, local_cnf)
    if not allowed:
        return allowed, {}
    if _truth_table_cnf(scope, allowed) != local_cnf:
        raise AssertionError("LOCAL_TRUTH_TABLE_CLAUSE_REPLAY_FAILED")

    candidates = {}
    width = len(scope)
    for modulus in PRIMES:
        anchor = allowed[0]
        differences = [
            [((point[i] - anchor[i]) % modulus) for i in range(width)]
            for point in allowed[1:]
        ]
        coefficient_basis = _nullspace(differences, modulus, width)
        equations = set()
        for coefficients in coefficient_basis:
            if not any(value % modulus for value in coefficients):
                continue
            rhs = _dot(coefficients, anchor, modulus)
            equations.add(_normalize_equation(coefficients, rhs, modulus))
        if not equations:
            continue
        equations = tuple(sorted(equations))
        recovered = tuple(
            bits
            for bits in product((0, 1), repeat=width)
            if all(_dot(coeffs, bits, modulus) == rhs for coeffs, rhs in equations)
        )
        if recovered != allowed:
            continue
        candidates[modulus] = equations
    return allowed, candidates


def _incidence_summary(scopes: tuple[tuple[int, ...], ...]):
    variable_to_scopes: dict[int, list[int]] = defaultdict(list)
    for scope_index, scope in enumerate(scopes):
        for variable in scope:
            variable_to_scopes[variable].append(scope_index)

    adjacency = {index: set() for index in range(len(scopes))}
    for touched in variable_to_scopes.values():
        for left in touched:
            for right in touched:
                if left != right:
                    adjacency[left].add(right)

    components = []
    unseen = set(adjacency)
    while unseen:
        root = min(unseen)
        queue = deque([root])
        unseen.remove(root)
        component = []
        while queue:
            node = queue.popleft()
            component.append(node)
            for neighbor in sorted(adjacency[node]):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
        components.append(tuple(sorted(component)))

    degree_histogram = Counter(len(touched) for touched in variable_to_scopes.values())
    return {
        "variable_scope_degree_histogram": dict(sorted(degree_histogram.items())),
        "all_variables_touch_exactly_two_scopes": set(degree_histogram) == {2},
        "constraint_component_count": len(components),
        "constraint_components": [list(component) for component in components],
    }


def _mod2_global(rows, variable_order: tuple[int, ...]):
    index = {variable: position for position, variable in enumerate(variable_order)}
    n = len(variable_order)
    variable_mask = (1 << n) - 1
    basis: dict[int, tuple[int, int]] = {}

    for row_index, row in enumerate(rows):
        mask = 0
        for variable, coefficient in row["coefficients"].items():
            if coefficient % 2:
                mask ^= 1 << index[variable]
        augmented = mask | ((row["rhs"] % 2) << n)
        combination = 1 << row_index
        while True:
            variables = augmented & variable_mask
            if variables == 0:
                if (augmented >> n) & 1:
                    selected = [i for i in range(len(rows)) if (combination >> i) & 1]
                    return {
                        "decision": "UNSAT",
                        "contradiction_row_indices": selected,
                        "rank": len(basis),
                    }
                break
            pivot = variables.bit_length() - 1
            if pivot in basis:
                augmented ^= basis[pivot][0]
                combination ^= basis[pivot][1]
            else:
                basis[pivot] = (augmented, combination)
                break

    values = [0] * n
    for pivot in sorted(basis):
        augmented, _ = basis[pivot]
        rhs = (augmented >> n) & 1
        lower = augmented & ((1 << pivot) - 1)
        value = rhs
        while lower:
            bit = lower.bit_length() - 1
            value ^= values[bit]
            lower ^= 1 << bit
        values[pivot] = value
    return {
        "decision": "SAT",
        "rank": len(basis),
        "assignment": {variable_order[i]: values[i] for i in range(n)},
    }


def synthesize(raw_clauses) -> dict:
    cnf, groups = _scope_groups(raw_clauses)
    scopes = tuple(sorted(groups))
    local_records = []
    common_moduli = set(PRIMES)

    for scope in scopes:
        allowed, candidates = _affine_candidates(scope, groups[scope])
        common_moduli &= set(candidates)
        local_records.append({
            "scope": scope,
            "allowed": allowed,
            "candidates": candidates,
            "source_clause_count": len(groups[scope]),
        })

    if not common_moduli:
        raise AssertionError("NO_COMMON_EXACT_FINITE_AFFINE_CARRIER")

    resource_keys = []
    for modulus in sorted(common_moduli):
        equation_count = sum(len(record["candidates"][modulus]) for record in local_records)
        resource_keys.append(((equation_count, modulus), modulus))
    resource_keys.sort()
    chosen_key, modulus = resource_keys[0]

    equations = []
    scope_certificate = []
    for scope_index, record in enumerate(local_records):
        local_equations = record["candidates"][modulus]
        scope_certificate.append({
            "variables": list(record["scope"]),
            "allowed_boolean_tuple_count": len(record["allowed"]),
            "source_clause_count": record["source_clause_count"],
            "equations": [
                {"coefficients": list(coefficients), "rhs": rhs}
                for coefficients, rhs in local_equations
            ],
        })
        for equation_index, (coefficients, rhs) in enumerate(local_equations):
            equations.append({
                "scope_index": scope_index,
                "equation_index": equation_index,
                "coefficients": {
                    variable: coefficient
                    for variable, coefficient in zip(record["scope"], coefficients)
                    if coefficient % modulus
                },
                "rhs": rhs,
            })

    variable_order = tuple(sorted(base.vars_of(cnf)))
    incidence = _incidence_summary(scopes)
    if modulus != 2:
        return {
            "kind": "EXACT_FINITE_AFFINE_REPRESENTATION_CERTIFICATE",
            "source_fingerprint": base.fingerprint(cnf),
            "decision": "OPEN",
            "reason": "EXACT_CARRIER_DISCOVERED_BUT_GLOBAL_DECISION_IMPLEMENTED_ONLY_FOR_SMALLEST_BOOLEAN_FIELD",
            "modulus": modulus,
            "resource_key": list(chosen_key),
            "scopes": scope_certificate,
            "incidence": incidence,
            "exact_clause_replay": True,
            "P_VS_NP": "OPEN",
        }

    global_result = _mod2_global(equations, variable_order)
    decision = global_result["decision"]
    witness = None
    contradiction = None
    if decision == "SAT":
        witness = global_result["assignment"]
        if not base.verify_total_assignment(cnf, witness):
            raise AssertionError("RECOVERED_BOOLEAN_FIELD_WITNESS_FAILED_SOURCE_CNF")
    else:
        contradiction = {
            "row_indices": global_result["contradiction_row_indices"],
            "row_count": len(global_result["contradiction_row_indices"]),
        }

    local_truth_table_work = sum(1 << len(scope) for scope in scopes)
    certificate = {
        "kind": "EXACT_FINITE_AFFINE_CONSERVATION_CERTIFICATE",
        "source_fingerprint": base.fingerprint(cnf),
        "decision": decision,
        "modulus": modulus,
        "resource_key": list(chosen_key),
        "prime_carriers_scanned": list(PRIMES),
        "max_scope_width_bound": MAX_SCOPE_WIDTH,
        "scopes": scope_certificate,
        "global_equation_count": len(equations),
        "global_rank": global_result["rank"],
        "incidence": incidence,
        "witness": witness,
        "contradiction": contradiction,
        "exact_clause_replay": True,
        "resource_ledger": {
            "raw_variables": len(variable_order),
            "raw_clauses": len(cnf),
            "discovered_scopes": len(scopes),
            "max_observed_scope_width": max(len(scope) for scope in scopes),
            "local_truth_table_tuples_examined": local_truth_table_work,
            "global_elimination": "PYTHON_INTEGER_BITSET_EXACT_MOD_2",
            "complexity_boundary": "LOCAL_DISCOVERY_COST_CONTAINS_2^MAX_SCOPE_WIDTH",
        },
        "scientific_boundary": {
            "arbitrary_CNF_coverage": "OPEN",
            "unbounded_scope_polynomiality": "NOT_ESTABLISHED",
            "universal_polynomial_SAT_algorithm": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    return certificate


def verify_certificate(raw_clauses, certificate: dict) -> bool:
    """Independent verifier; never calls synthesize()."""
    try:
        cnf, groups = _scope_groups(raw_clauses)
        if certificate.get("kind") != "EXACT_FINITE_AFFINE_CONSERVATION_CERTIFICATE":
            return False
        if certificate.get("source_fingerprint") != base.fingerprint(cnf):
            return False
        modulus = int(certificate["modulus"])
        if modulus != 2:
            return False

        scope_rows = certificate["scopes"]
        scopes = tuple(sorted(groups))
        if len(scope_rows) != len(scopes):
            return False

        equations = []
        for scope_index, (scope, supplied) in enumerate(zip(scopes, scope_rows)):
            if tuple(int(v) for v in supplied["variables"]) != scope:
                return False
            allowed = _allowed_boolean_tuples(scope, groups[scope])
            supplied_equations = []
            for equation_index, equation in enumerate(supplied["equations"]):
                coefficients = tuple(int(value) % modulus for value in equation["coefficients"])
                rhs = int(equation["rhs"]) % modulus
                if len(coefficients) != len(scope) or not any(coefficients):
                    return False
                supplied_equations.append((coefficients, rhs))
                equations.append({
                    "scope_index": scope_index,
                    "equation_index": equation_index,
                    "coefficients": {
                        variable: coefficient
                        for variable, coefficient in zip(scope, coefficients)
                        if coefficient
                    },
                    "rhs": rhs,
                })
            recovered = tuple(
                bits
                for bits in product((0, 1), repeat=len(scope))
                if all(_dot(coefficients, bits, modulus) == rhs for coefficients, rhs in supplied_equations)
            )
            if recovered != allowed:
                return False
            if _truth_table_cnf(scope, recovered) != groups[scope]:
                return False

        if int(certificate["global_equation_count"]) != len(equations):
            return False
        variables = tuple(sorted(base.vars_of(cnf)))
        decision = certificate["decision"]
        if decision == "SAT":
            supplied_witness = certificate.get("witness")
            if supplied_witness is None:
                return False
            witness = {int(variable): int(value) for variable, value in supplied_witness.items()}
            return base.verify_total_assignment(cnf, witness)
        if decision != "UNSAT":
            return False

        contradiction = certificate.get("contradiction") or {}
        selected = [int(index) for index in contradiction.get("row_indices", [])]
        if not selected or any(index < 0 or index >= len(equations) for index in selected):
            return False
        coefficients = {variable: 0 for variable in variables}
        rhs = 0
        for index in selected:
            row = equations[index]
            rhs ^= row["rhs"] & 1
            for variable, coefficient in row["coefficients"].items():
                coefficients[variable] ^= coefficient & 1
        return rhs == 1 and not any(coefficients.values())
    except (AssertionError, KeyError, TypeError, ValueError):
        return False
