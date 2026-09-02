#!/usr/bin/env python3
"""R43A exact width-3 XOR/Tseitin bundle recovery and certified GF(2) solve.

Authority is fail-closed: the whole CNF must partition into exact 4-clause
parity bundles on variable triples. Partial/malformed bundles return
NOT_RECOGNIZED and carry no SAT decision authority.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import defaultdict


def sha256_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def canonical_clause(clause):
    if len(clause) != 3 or len({abs(x) for x in clause}) != 3:
        return None
    if any(-x in clause for x in clause):
        return None
    return tuple(sorted(clause, key=lambda x: abs(x)))


def xor_bundle(variables, rhs):
    variables = tuple(sorted(variables))
    clauses = []
    for bits in itertools.product((0, 1), repeat=3):
        if sum(bits) % 2 == rhs:
            continue
        clauses.append([v if bit == 0 else -v for v, bit in zip(variables, bits)])
    return clauses


def graph_tseitin(vertices, edges, charges):
    edge_var = {tuple(sorted(edge)): i + 1 for i, edge in enumerate(edges)}
    incident = {v: [] for v in vertices}
    for (a, b), variable in edge_var.items():
        incident[a].append(variable)
        incident[b].append(variable)
    if not all(len(incident[v]) == 3 for v in vertices):
        raise AssertionError("GRAPH_NOT_3_REGULAR")
    clauses = []
    for v in vertices:
        clauses.extend(xor_bundle(sorted(incident[v]), int(charges.get(v, 0))))
    return clauses


def recover_exact_width3_xor(cnf):
    groups = defaultdict(list)
    visits = 0
    for clause in cnf:
        visits += 1
        canon = canonical_clause(clause)
        if canon is None:
            return None, {"recognized": False, "reason": "INVALID_OR_NON_WIDTH3_CLAUSE", "detector_clause_visits": visits}
        key = tuple(sorted(abs(x) for x in canon))
        groups[key].append(canon)

    equations = []
    for key in sorted(groups):
        bundle = groups[key]
        if len(bundle) != 4 or len(set(bundle)) != 4:
            return None, {
                "recognized": False,
                "reason": "BUNDLE_COUNT_OR_DUPLICATE_MISMATCH",
                "bundle_key": list(key),
                "count": len(bundle),
                "unique_count": len(set(bundle)),
                "detector_clause_visits": visits,
            }
        forbidden = set()
        parities = set()
        for clause in bundle:
            signs = {abs(lit): lit > 0 for lit in clause}
            bits = tuple(0 if signs[v] else 1 for v in key)
            forbidden.add(bits)
            parities.add(sum(bits) % 2)
        if len(parities) != 1:
            return None, {"recognized": False, "reason": "MIXED_FORBIDDEN_PARITY", "detector_clause_visits": visits}
        forbidden_parity = next(iter(parities))
        expected = {bits for bits in itertools.product((0, 1), repeat=3) if sum(bits) % 2 == forbidden_parity}
        if forbidden != expected:
            return None, {"recognized": False, "reason": "INCOMPLETE_PARITY_BUNDLE", "detector_clause_visits": visits}
        equations.append({"variables": list(key), "rhs": 1 ^ forbidden_parity})

    return equations, {"recognized": True, "bundle_count": len(equations), "detector_clause_visits": visits}


def gaussian_gf2(equations):
    variables = sorted({v for equation in equations for v in equation["variables"]})
    index = {v: i for i, v in enumerate(variables)}
    rows = []
    for eq_index, equation in enumerate(equations):
        mask = 0
        for v in equation["variables"]:
            mask ^= 1 << index[v]
        rows.append([mask, int(equation["rhs"]), 1 << eq_index])

    rank = 0
    row_xors = 0
    pivots = []
    for col in range(len(variables)):
        pivot = next((i for i in range(rank, len(rows)) if (rows[i][0] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for j in range(len(rows)):
            if j != rank and ((rows[j][0] >> col) & 1):
                rows[j][0] ^= rows[rank][0]
                rows[j][1] ^= rows[rank][1]
                rows[j][2] ^= rows[rank][2]
                row_xors += 1
        pivots.append((col, rank))
        rank += 1
        contradiction = next((row for row in rows if row[0] == 0 and row[1] == 1), None)
        if contradiction is not None:
            certificate = [i for i in range(len(equations)) if (contradiction[2] >> i) & 1]
            return {
                "decision": "UNSAT",
                "certificate_equation_indices": certificate,
                "gf2_row_xors": row_xors,
                "gf2_pivot_count": rank,
            }

    assignment = {v: 0 for v in variables}
    for col, row_index in pivots:
        assignment[variables[col]] = rows[row_index][1]
    return {
        "decision": "SAT",
        "assignment": assignment,
        "gf2_row_xors": row_xors,
        "gf2_pivot_count": rank,
    }


def verify_unsat_certificate(equations, indices):
    parity_variables = set()
    rhs = 0
    for i in indices:
        equation = equations[i]
        for v in equation["variables"]:
            if v in parity_variables:
                parity_variables.remove(v)
            else:
                parity_variables.add(v)
        rhs ^= int(equation["rhs"])
    return not parity_variables and rhs == 1


def clause_true(clause, assignment):
    return any((assignment[abs(lit)] == 1) if lit > 0 else (assignment[abs(lit)] == 0) for lit in clause)


def verify_sat_certificate(equations, cnf, assignment):
    equations_ok = all(sum(assignment[v] for v in eq["variables"]) % 2 == eq["rhs"] for eq in equations)
    cnf_ok = all(clause_true(clause, assignment) for clause in cnf)
    return equations_ok and cnf_ok


def solve_fail_closed(cnf):
    equations, detector = recover_exact_width3_xor(cnf)
    base = {
        "input_clause_count": len(cnf),
        "input_literal_count": sum(len(c) for c in cnf),
        "detector_clause_visits": detector["detector_clause_visits"],
    }
    if equations is None:
        return {
            "status": "NOT_RECOGNIZED",
            "decision_authority": False,
            "detector": detector,
            "resource_ledger": base,
        }

    solved = gaussian_gf2(equations)
    if solved["decision"] == "UNSAT":
        verified = verify_unsat_certificate(equations, solved["certificate_equation_indices"])
        verification_visits = len(solved["certificate_equation_indices"])
        certificate = {"type": "GF2_LINEAR_DEPENDENCY_0_EQ_1", "verified": verified, "equation_indices": solved["certificate_equation_indices"]}
    else:
        assignment = {int(k): int(v) for k, v in solved["assignment"].items()}
        verified = verify_sat_certificate(equations, cnf, assignment)
        verification_visits = len(equations) + len(cnf)
        certificate = {"type": "SAT_ASSIGNMENT", "verified": verified, "assignment_sha256": sha256_json(sorted(assignment.items()))}
    if not verified:
        raise AssertionError("CERTIFICATE_VERIFICATION_FAILED")

    return {
        "status": "RECOGNIZED_AND_CERTIFIED",
        "decision_authority": True,
        "decision": solved["decision"],
        "detector": detector,
        "certificate": certificate,
        "resource_ledger": {
            **base,
            "bundle_count": len(equations),
            "gf2_row_xors": solved["gf2_row_xors"],
            "gf2_pivot_count": solved["gf2_pivot_count"],
            "certificate_equation_count": len(solved.get("certificate_equation_indices", [])),
            "verification_clause_visits": verification_visits,
        },
    }


def frozen_suite():
    k4_v = list(range(4))
    k4_e = [(i, j) for i in k4_v for j in k4_v if i < j]
    prism_v = list(range(6))
    prism_e = [(0,1),(1,2),(2,0),(3,4),(4,5),(5,3),(0,3),(1,4),(2,5)]
    p_v = list(range(10))
    p_e = [(0,1),(1,2),(2,3),(3,4),(4,0),(5,7),(7,9),(9,6),(6,8),(8,5),(0,5),(1,6),(2,7),(3,8),(4,9)]

    k4_odd = graph_tseitin(k4_v, k4_e, {0: 1})
    prism_odd = graph_tseitin(prism_v, prism_e, {0: 1})
    p_odd = graph_tseitin(p_v, p_e, {0: 1})
    p_even = graph_tseitin(p_v, p_e, {})
    return [
        ("K4_ODD", k4_odd, "UNSAT"),
        ("PRISM6_ODD", prism_odd, "UNSAT"),
        ("PETERSEN10_ODD", p_odd, "UNSAT"),
        ("PETERSEN10_EVEN", p_even, "SAT"),
        ("MALFORMED_MISSING_CLAUSE", k4_odd[:-1], "NOT_RECOGNIZED"),
        ("MALFORMED_EXTRA_CLAUSE", k4_odd + [[100,101,102]], "NOT_RECOGNIZED"),
    ]


def main():
    tests = []
    for test_id, cnf, expected in frozen_suite():
        result = solve_fail_closed(cnf)
        actual = result.get("decision", result["status"])
        if actual != expected:
            raise AssertionError(f"FROZEN_EXPECTATION_MISMATCH:{test_id}:{actual}:{expected}")
        tests.append({"id": test_id, "expected": expected, "result": result})

    output = {
        "schema": "janus.trump.r43a.exact_cnf_to_gf2_tseitin.result.v1",
        "date": "2026-09-03",
        "route_id": "EXACT_WIDTH3_XOR_BUNDLE_TO_GF2_V1",
        "status": "ALL_FROZEN_TESTS_PASS",
        "tests": tests,
        "scientific_interpretation": {
            "exact_representation_switch_demonstrated": True,
            "resolution_hard_family_has_polynomial_specialized_representation": True,
            "general_3cnf_coverage_proved": False,
            "law": "SPECIAL_CLASS_REPRESENTATION_ESCAPE != UNIVERSAL_3SAT_RESOLVER",
        },
        "proof_authority_delta": 0,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
