#!/usr/bin/env python3
"""
C021 JANUS Overlap / Interface / Feedback Barrier

Software-only exact experiment.

This cycle continues the JANUS Tear / Observer route after canonical C020.
It tests the next proposed mechanism:

    iNaiHR -> propose tractable proof languages
    AURA   -> label PAST / OBSTACLE / GUIDE / OUTCOME
    HRain  -> retain a content-addressed proof DAG
    JANUS  -> independently verify witnesses, Tears, and transformations

Questions:
1. Can Horn and dual-Horn modules be composed through a small interface?
2. Does clause-wise membership in tractable languages help on arbitrary 3-CNF?
3. Can cyclic definitions be solved when their SCC is affine?
4. Can nonlinear feedback definitions encode arbitrary 3-SAT?
5. Can symbolic substitution be kept polynomial by preserving a DAG?

No swarm, device, NAS runtime, Telegram backend, BCI, external LLM,
physical P-N junction, or quantum device is used.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]

CANONICAL_SEED = "44e21fdc9d37fda98e2e73b0c9eb268bd04cdca9d84d0519e4f1166be22b46fc"
DEFAULT_SEED = 9379992


def canonical_clause(clause: Iterable[int]) -> Clause:
    return tuple(sorted(set(clause), key=lambda x: (abs(x), x < 0)))


def canonical_cnf(formula: Iterable[Iterable[int]]) -> CNF:
    return tuple(sorted((canonical_clause(c) for c in formula)))


def variables(formula: CNF) -> list[int]:
    return sorted({abs(lit) for clause in formula for lit in clause})


def satisfies(formula: CNF, assignment: dict[int, bool]) -> bool:
    return all(
        any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause)
        for clause in formula
    )


def brute_force(formula: CNF) -> tuple[bool, dict[int, bool] | None, int]:
    vars_ = variables(formula)
    checks = 0
    for bits in itertools.product([False, True], repeat=len(vars_)):
        checks += 1
        assignment = dict(zip(vars_, bits))
        if satisfies(formula, assignment):
            return True, assignment, checks
    return False, None, checks


def simplify(formula: CNF, fixed: dict[int, bool]) -> CNF:
    out: list[Clause] = []
    for clause in formula:
        new_clause = []
        clause_sat = False
        for lit in clause:
            var = abs(lit)
            if var in fixed:
                if fixed[var] == (lit > 0):
                    clause_sat = True
                    break
            else:
                new_clause.append(lit)
        if not clause_sat:
            out.append(canonical_clause(new_clause))
    return canonical_cnf(out)


def is_horn(formula: CNF) -> bool:
    return all(sum(1 for lit in clause if lit > 0) <= 1 for clause in formula)


def is_dual_horn(formula: CNF) -> bool:
    return all(sum(1 for lit in clause if lit < 0) <= 1 for clause in formula)


@dataclass
class TractableResult:
    sat: bool
    assignment: dict[int, bool] | None
    certificate: dict[str, Any]


def solve_horn(formula: CNF, fixed: dict[int, bool] | None = None) -> TractableResult:
    fixed = dict(fixed or {})
    residual = simplify(formula, fixed)
    if not is_horn(residual):
        return TractableResult(False, None, {"kind": "NOT_HORN"})

    all_vars = set(variables(formula))
    rules: list[tuple[frozenset[int], int | None, int]] = []
    for idx, clause in enumerate(residual):
        positives = [lit for lit in clause if lit > 0]
        antecedent = frozenset(abs(lit) for lit in clause if lit < 0)
        consequent = positives[0] if positives else None
        rules.append((antecedent, consequent, idx))

    true_vars: set[int] = set()
    fired: list[int] = []
    changed = True
    while changed:
        changed = False
        for antecedent, consequent, idx in rules:
            if antecedent.issubset(true_vars):
                if consequent is None:
                    return TractableResult(
                        False,
                        None,
                        {
                            "kind": "HORN_FORWARD_CONTRADICTION",
                            "trigger_rule": idx,
                            "true_vars": sorted(true_vars),
                            "fixed": fixed,
                        },
                    )
                if consequent not in true_vars:
                    true_vars.add(consequent)
                    fired.append(idx)
                    changed = True

    assignment = {v: (v in true_vars) for v in all_vars if v not in fixed}
    assignment.update(fixed)
    if not satisfies(formula, assignment):
        raise AssertionError("Horn least-model construction failed verification")
    return TractableResult(
        True,
        assignment,
        {
            "kind": "HORN_LEAST_MODEL",
            "fired_rules": fired,
            "true_vars": sorted(true_vars),
            "fixed": fixed,
        },
    )


def solve_dual_horn(formula: CNF, fixed: dict[int, bool] | None = None) -> TractableResult:
    fixed = dict(fixed or {})
    transformed = canonical_cnf(tuple(tuple(-lit for lit in clause) for clause in formula))
    transformed_fixed = {v: (not value) for v, value in fixed.items()}
    result = solve_horn(transformed, transformed_fixed)
    if not result.sat:
        cert = dict(result.certificate)
        cert["kind"] = "DUAL_" + str(cert.get("kind", "HORN_CERTIFICATE"))
        return TractableResult(False, None, cert)

    assert result.assignment is not None
    assignment = {v: (not value) for v, value in result.assignment.items()}
    if not satisfies(formula, assignment):
        raise AssertionError("Dual-Horn construction failed verification")
    return TractableResult(
        True,
        assignment,
        {
            "kind": "DUAL_HORN_GREATEST_MODEL",
            "horn_certificate": result.certificate,
            "fixed": fixed,
        },
    )


def merge_assignments(*assignments: dict[int, bool]) -> dict[int, bool] | None:
    out: dict[int, bool] = {}
    for assignment in assignments:
        for var, value in assignment.items():
            if var in out and out[var] != value:
                return None
            out[var] = value
    return out


def interface_join(
    horn_formula: CNF,
    dual_formula: CNF,
) -> dict[str, Any]:
    shared = sorted(set(variables(horn_formula)) & set(variables(dual_formula)))
    states = 0
    state_hashes: list[str] = []

    for bits in itertools.product([False, True], repeat=len(shared)):
        states += 1
        fixed = dict(zip(shared, bits))
        state_hashes.append(
            hashlib.sha256(
                json.dumps(fixed, sort_keys=True).encode("utf-8")
            ).hexdigest()
        )
        h = solve_horn(horn_formula, fixed)
        if not h.sat:
            continue
        d = solve_dual_horn(dual_formula, fixed)
        if not d.sat:
            continue
        assert h.assignment is not None and d.assignment is not None
        merged = merge_assignments(h.assignment, d.assignment)
        if merged is None:
            continue
        combined = canonical_cnf(horn_formula + dual_formula)
        if satisfies(combined, merged):
            return {
                "sat": True,
                "assignment": merged,
                "interface": shared,
                "interface_width": len(shared),
                "states_examined": states,
                "theoretical_states": 1 << len(shared),
                "hrain_state_hashes": state_hashes,
                "horn_certificate": h.certificate,
                "dual_horn_certificate": d.certificate,
            }

    return {
        "sat": False,
        "assignment": None,
        "interface": shared,
        "interface_width": len(shared),
        "states_examined": states,
        "theoretical_states": 1 << len(shared),
        "hrain_state_hashes": state_hashes,
        "certificate": {
            "kind": "EXHAUSTIVE_INTERFACE_TEAR",
            "interface": shared,
            "states_checked": states,
        },
    }


def random_horn_clause(rng: random.Random, pool: list[int], width: int) -> Clause:
    chosen = rng.sample(pool, width)
    positive_count = rng.choice([0, 1])
    positives = set(rng.sample(chosen, positive_count))
    return canonical_clause(v if v in positives else -v for v in chosen)


def random_dual_clause(rng: random.Random, pool: list[int], width: int) -> Clause:
    chosen = rng.sample(pool, width)
    negative_count = rng.choice([0, 1])
    negatives = set(rng.sample(chosen, negative_count))
    return canonical_clause(-v if v in negatives else v for v in chosen)


def bounded_interface_fixture(
    rng: random.Random,
    k: int,
    horn_private: int,
    dual_private: int,
    clauses_each: int,
) -> tuple[CNF, CNF]:
    shared = list(range(1, k + 1))
    hp = list(range(k + 1, k + horn_private + 1))
    dp = list(range(k + horn_private + 1, k + horn_private + dual_private + 1))

    hpool = shared + hp
    dpool = shared + dp

    h: list[Clause] = []
    d: list[Clause] = []

    # Guarantee every interface variable occurs in both modules.
    for i, var in enumerate(shared):
        hpv = hp[i % len(hp)] if hp else var
        dpv = dp[i % len(dp)] if dp else var
        h.append(canonical_clause((-var, hpv)))
        d.append(canonical_clause((var, -dpv)))

    for _ in range(clauses_each):
        h.append(random_horn_clause(rng, hpool, rng.randint(1, min(3, len(hpool)))))
        d.append(random_dual_clause(rng, dpool, rng.randint(1, min(3, len(dpool)))))

    return canonical_cnf(h), canonical_cnf(d)


def random_3cnf(rng: random.Random, n_vars: int, n_clauses: int) -> CNF:
    out: list[Clause] = []
    for _ in range(n_clauses):
        chosen = rng.sample(range(1, n_vars + 1), 3)
        out.append(
            canonical_clause(v if rng.random() < 0.5 else -v for v in chosen)
        )
    return canonical_cnf(out)


def partition_horn_dual(formula: CNF) -> tuple[CNF, CNF]:
    horn: list[Clause] = []
    dual: list[Clause] = []
    for clause in formula:
        positives = sum(1 for lit in clause if lit > 0)
        negatives = len(clause) - positives
        if positives <= 1:
            horn.append(clause)
        elif negatives <= 1:
            dual.append(clause)
        else:
            raise AssertionError("A 3-clause escaped Horn union dual-Horn")
    return canonical_cnf(horn), canonical_cnf(dual)


def maximal_overlap_fixture(n: int) -> tuple[CNF, CNF]:
    h: list[Clause] = []
    d: list[Clause] = []
    for i in range(1, n + 1):
        a = i
        b = (i % n) + 1
        c = ((i + 1) % n) + 1
        h.append(canonical_clause((a, -b, -c)))
        d.append(canonical_clause((-a, b, c)))
    return canonical_cnf(h), canonical_cnf(d)


# ----------------------------- GF(2) cycles -----------------------------

@dataclass
class GF2Result:
    consistent: bool
    assignment: dict[int, bool] | None
    rank: int
    conflict_provenance: list[int] | None


def gf2_solve(equations: list[tuple[int, int]], n_vars: int) -> GF2Result:
    # Row format: [mask, rhs, provenance_mask]
    rows = [[mask, rhs & 1, 1 << i] for i, (mask, rhs) in enumerate(equations)]
    pivot_row = 0
    pivot_cols: list[int] = []

    for col in range(n_vars):
        pivot = next(
            (r for r in range(pivot_row, len(rows)) if (rows[r][0] >> col) & 1),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        for r in range(len(rows)):
            if r != pivot_row and ((rows[r][0] >> col) & 1):
                rows[r][0] ^= rows[pivot_row][0]
                rows[r][1] ^= rows[pivot_row][1]
                rows[r][2] ^= rows[pivot_row][2]
        pivot_cols.append(col)
        pivot_row += 1

    for mask, rhs, provenance in rows:
        if mask == 0 and rhs == 1:
            indices = [i for i in range(len(equations)) if (provenance >> i) & 1]
            return GF2Result(False, None, len(pivot_cols), indices)

    assignment_bits = [0] * n_vars
    for row_index, col in enumerate(pivot_cols):
        mask, rhs, _ = rows[row_index]
        value = rhs
        for j in range(col + 1, n_vars):
            if (mask >> j) & 1:
                value ^= assignment_bits[j]
        assignment_bits[col] = value

    assignment = {i + 1: bool(bit) for i, bit in enumerate(assignment_bits)}
    return GF2Result(True, assignment, len(pivot_cols), None)


def verify_gf2_witness(
    equations: list[tuple[int, int]],
    assignment: dict[int, bool],
) -> bool:
    for mask, rhs in equations:
        value = 0
        bit = 0
        temp = mask
        while temp:
            if temp & 1:
                value ^= int(assignment[bit + 1])
            temp >>= 1
            bit += 1
        if value != rhs:
            return False
    return True


def verify_gf2_conflict(
    equations: list[tuple[int, int]],
    indices: list[int],
) -> bool:
    mask = 0
    rhs = 0
    for index in indices:
        mask ^= equations[index][0]
        rhs ^= equations[index][1]
    return mask == 0 and rhs == 1


def affine_cycle(n: int, charges: list[int]) -> list[tuple[int, int]]:
    equations = []
    for i in range(n):
        j = (i + 1) % n
        equations.append(((1 << i) | (1 << j), charges[i] & 1))
    return equations


# ------------------------- circuit feedback reduction -------------------------

def or3_gate(out: int, a: int, b: int, c: int) -> list[Clause]:
    return [
        canonical_clause((-a, out)),
        canonical_clause((-b, out)),
        canonical_clause((-c, out)),
        canonical_clause((a, b, c, -out)),
    ]


def and2_gate(out: int, a: int, b: int) -> list[Clause]:
    return [
        canonical_clause((-out, a)),
        canonical_clause((-out, b)),
        canonical_clause((out, -a, -b)),
    ]


def equiv_gate(a: int, b: int) -> list[Clause]:
    return [
        canonical_clause((-a, b)),
        canonical_clause((a, -b)),
    ]


def encode_feedback_circuit(formula: CNF) -> tuple[CNF, dict[str, Any]]:
    n = max(variables(formula), default=0)
    next_var = n + 1
    clauses: list[Clause] = []
    gates: list[dict[str, Any]] = []
    clause_outputs: list[int] = []

    for clause in formula:
        if len(clause) != 3:
            raise ValueError("feedback reduction expects exact 3-CNF")
        out = next_var
        next_var += 1
        a, b, c = clause
        # Gate inputs may be signed literals. Introduce literal proxy values by
        # using signed literals directly in the exact OR encoding.
        block = [
            canonical_clause((-a, out)),
            canonical_clause((-b, out)),
            canonical_clause((-c, out)),
            canonical_clause((a, b, c, -out)),
        ]
        clauses.extend(block)
        gates.append({"kind": "OR3_LITERALS", "out": out, "inputs": [a, b, c]})
        clause_outputs.append(out)

    level = clause_outputs[:]
    while len(level) > 1:
        new_level = []
        for idx in range(0, len(level), 2):
            if idx + 1 == len(level):
                new_level.append(level[idx])
                continue
            out = next_var
            next_var += 1
            a, b = level[idx], level[idx + 1]
            clauses.extend(and2_gate(out, a, b))
            gates.append({"kind": "AND2", "out": out, "inputs": [a, b]})
            new_level.append(out)
        level = new_level

    output = level[0]
    p = next_var
    q = next_var + 1
    next_var += 2

    # Nonlinear feedback SCC:
    #   p <-> (output AND q)
    #   q <-> p
    #   p = 1
    clauses.extend(and2_gate(p, output, q))
    clauses.extend(equiv_gate(q, p))
    clauses.append((p,))

    metadata = {
        "original_variables": n,
        "gates": gates,
        "output": output,
        "feedback": {
            "p": p,
            "q": q,
            "equations": ["p <-> (output AND q)", "q <-> p", "p = 1"],
            "scc": [p, q],
        },
        "total_variables": next_var - 1,
    }
    return canonical_cnf(clauses), metadata


def eval_signed_literal(lit: int, assignment: dict[int, bool]) -> bool:
    return assignment[abs(lit)] == (lit > 0)


def extend_circuit_witness(
    formula: CNF,
    metadata: dict[str, Any],
    original_assignment: dict[int, bool],
) -> dict[int, bool] | None:
    assignment = dict(original_assignment)
    for gate in metadata["gates"]:
        kind = gate["kind"]
        out = gate["out"]
        inputs = gate["inputs"]
        if kind == "OR3_LITERALS":
            assignment[out] = any(eval_signed_literal(lit, assignment) for lit in inputs)
        elif kind == "AND2":
            assignment[out] = assignment[inputs[0]] and assignment[inputs[1]]
        else:
            raise AssertionError(kind)

    output = metadata["output"]
    if not assignment[output]:
        return None
    p = metadata["feedback"]["p"]
    q = metadata["feedback"]["q"]
    assignment[p] = True
    assignment[q] = True
    return assignment


def verify_feedback_reduction_structure(
    formula: CNF,
    circuit: CNF,
    metadata: dict[str, Any],
) -> bool:
    rebuilt, rebuilt_metadata = encode_feedback_circuit(formula)
    return circuit == rebuilt and metadata == rebuilt_metadata


# --------------------------- experiment runners ---------------------------

def run_bounded_interfaces(rng: random.Random, cases: int = 160) -> dict[str, Any]:
    mismatches = 0
    false_accepts = 0
    widths = []
    states = []
    dag_hashes: set[str] = set()

    for _ in range(cases):
        k = rng.randint(0, 6)
        h, d = bounded_interface_fixture(rng, k, 2, 2, rng.randint(2, 7))
        joined = interface_join(h, d)
        combined = canonical_cnf(h + d)
        truth, witness, _ = brute_force(combined)
        if joined["sat"] != truth:
            mismatches += 1
        if joined["sat"]:
            assignment = joined["assignment"]
            if assignment is None or not satisfies(combined, assignment):
                false_accepts += 1
        widths.append(joined["interface_width"])
        states.append(joined["states_examined"])
        dag_hashes.update(joined["hrain_state_hashes"])

    return {
        "cases": cases,
        "mismatches": mismatches,
        "false_accepts": false_accepts,
        "max_interface_width": max(widths),
        "max_states_examined": max(states),
        "unique_hrain_interface_nodes": len(dag_hashes),
        "parameterized_cost": "O(2^k poly(L))",
        "polynomial_when": "k = O(log L)",
    }


def run_generic_partition(rng: random.Random, cases: int = 100) -> dict[str, Any]:
    mismatches = 0
    unclassified = 0
    widths = []
    theoretical = []
    states_examined = []

    for _ in range(cases):
        n = rng.randint(8, 11)
        formula = random_3cnf(rng, n, rng.randint(3 * n, 5 * n))
        h, d = partition_horn_dual(formula)
        if len(h) + len(d) != len(formula):
            unclassified += 1
        joined = interface_join(h, d)
        truth, _, _ = brute_force(formula)
        if joined["sat"] != truth:
            mismatches += 1
        widths.append(joined["interface_width"])
        theoretical.append(joined["theoretical_states"])
        states_examined.append(joined["states_examined"])

    hmax, dmax = maximal_overlap_fixture(18)
    overlap = len(set(variables(hmax)) & set(variables(dmax)))

    return {
        "cases": cases,
        "unclassified_clauses": unclassified,
        "mismatches": mismatches,
        "min_interface_width": min(widths),
        "max_interface_width": max(widths),
        "average_interface_width": sum(widths) / len(widths),
        "max_theoretical_interface_states": max(theoretical),
        "max_actual_states_examined": max(states_examined),
        "maximal_overlap_fixture": {
            "variables": 18,
            "shared_interface": overlap,
            "theoretical_states": 1 << overlap,
            "horn_individually_tractable": is_horn(hmax),
            "dual_horn_individually_tractable": is_dual_horn(dmax),
        },
        "exact_observation": (
            "Every exact 3-clause is Horn or dual-Horn. Therefore clause-wise "
            "tractable-language coverage alone covers all 3-CNF and is not a SAT solution."
        ),
    }


def run_affine_cycles(rng: random.Random, cases: int = 240) -> dict[str, Any]:
    mismatches = 0
    witness_failures = 0
    conflict_failures = 0
    sat_count = 0
    unsat_count = 0

    for _ in range(cases):
        n = rng.randint(3, 14)
        charges = [rng.randrange(2) for _ in range(n)]
        equations = affine_cycle(n, charges)
        result = gf2_solve(equations, n)
        expected = (sum(charges) % 2) == 0
        if result.consistent != expected:
            mismatches += 1
        if result.consistent:
            sat_count += 1
            assert result.assignment is not None
            if not verify_gf2_witness(equations, result.assignment):
                witness_failures += 1
        else:
            unsat_count += 1
            if result.conflict_provenance is None or not verify_gf2_conflict(
                equations, result.conflict_provenance
            ):
                conflict_failures += 1

    return {
        "cases": cases,
        "sat": sat_count,
        "unsat": unsat_count,
        "mismatches": mismatches,
        "witness_failures": witness_failures,
        "conflict_certificate_failures": conflict_failures,
        "result": "Affine cyclic SCCs remain polynomially solvable by GF(2) elimination.",
    }


def run_feedback_reduction(rng: random.Random, cases: int = 140) -> dict[str, Any]:
    structural_failures = 0
    witness_failures = 0
    equivalence_failures = 0
    sat_count = 0
    unsat_count = 0

    for _ in range(cases):
        n = rng.randint(3, 7)
        formula = random_3cnf(rng, n, rng.randint(2, 9))
        truth, witness, _ = brute_force(formula)
        circuit, metadata = encode_feedback_circuit(formula)

        if not verify_feedback_reduction_structure(formula, circuit, metadata):
            structural_failures += 1

        if truth:
            sat_count += 1
            assert witness is not None
            extended = extend_circuit_witness(formula, metadata, witness)
            if extended is None or not satisfies(circuit, extended):
                witness_failures += 1
        else:
            unsat_count += 1

        # Exact assignment-level equivalence check:
        # every original assignment has a satisfying circuit extension iff it satisfies F.
        for bits in itertools.product([False, True], repeat=n):
            assignment = dict(zip(range(1, n + 1), bits))
            expected = satisfies(formula, assignment)
            extended = extend_circuit_witness(formula, metadata, assignment)
            obtained = extended is not None and satisfies(circuit, extended)
            if expected != obtained:
                equivalence_failures += 1
                break

    return {
        "cases": cases,
        "sat": sat_count,
        "unsat": unsat_count,
        "structural_failures": structural_failures,
        "witness_failures": witness_failures,
        "assignment_equivalence_failures": equivalence_failures,
        "reduction_size": "linear in the source 3-CNF",
        "feedback_scc": "p <-> (output AND q), q <-> p, with p=1",
        "consequence": (
            "A polynomial solver for general nonlinear constrained feedback definitions "
            "would solve arbitrary 3-SAT."
        ),
    }


def run_substitution_growth(max_depth: int = 32) -> dict[str, Any]:
    rows = []
    for depth in range(1, max_depth + 1):
        dag_nodes = depth + 1
        expanded_leaves = 1 << depth
        rows.append({
            "depth": depth,
            "dag_nodes": dag_nodes,
            "expanded_tree_leaves": expanded_leaves,
            "ratio": expanded_leaves / dag_nodes,
        })
    return {
        "max_depth": max_depth,
        "last": rows[-1],
        "rows": rows,
        "result": (
            "Textual substitution can expand exponentially even when the shared "
            "circuit DAG remains linear. HRain must preserve DAG sharing."
        ),
    }


def run_small_cycle_truth_tables() -> dict[str, Any]:
    # z1 <-> z2, z2 <-> z1
    equal_solutions = []
    # z1 <-> not z2, z2 <-> not z1
    anti_solutions = []
    # z <-> not z
    contradiction = []

    for z1, z2 in itertools.product([False, True], repeat=2):
        if (z1 == z2) and (z2 == z1):
            equal_solutions.append([z1, z2])
        if (z1 == (not z2)) and (z2 == (not z1)):
            anti_solutions.append([z1, z2])
    for z in [False, True]:
        if z == (not z):
            contradiction.append([z])

    return {
        "equality_cycle_solutions": equal_solutions,
        "negation_cycle_solutions": anti_solutions,
        "self_negation_solutions": contradiction,
        "interpretation": (
            "Cyclic equations may be underdetermined, multi-solution, or inconsistent. "
            "They are constraints, not automatically eliminable definitions."
        ),
    }


def run(seed: int = DEFAULT_SEED) -> dict[str, Any]:
    rng = random.Random(seed)

    bounded = run_bounded_interfaces(rng)
    generic = run_generic_partition(rng)
    affine = run_affine_cycles(rng)
    feedback = run_feedback_reduction(rng)
    substitution = run_substitution_growth()
    cycles = run_small_cycle_truth_tables()

    assertions = {
        "bounded_interface_exact": bounded["mismatches"] == 0,
        "bounded_interface_sound": bounded["false_accepts"] == 0,
        "all_3clauses_covered": generic["unclassified_clauses"] == 0,
        "generic_join_exact_on_test_range": generic["mismatches"] == 0,
        "maximal_overlap_is_linear": (
            generic["maximal_overlap_fixture"]["shared_interface"]
            == generic["maximal_overlap_fixture"]["variables"]
        ),
        "affine_cycles_exact": affine["mismatches"] == 0,
        "affine_witnesses_verified": affine["witness_failures"] == 0,
        "affine_conflicts_verified": affine["conflict_certificate_failures"] == 0,
        "feedback_reduction_structural": feedback["structural_failures"] == 0,
        "feedback_reduction_witnesses": feedback["witness_failures"] == 0,
        "feedback_assignment_equivalence": feedback["assignment_equivalence_failures"] == 0,
        "substitution_blowup_observed": (
            substitution["last"]["expanded_tree_leaves"] == 2 ** substitution["max_depth"]
        ),
        "cycles_not_unique_definitions": (
            len(cycles["equality_cycle_solutions"]) == 2
            and len(cycles["negation_cycle_solutions"]) == 2
            and len(cycles["self_negation_solutions"]) == 0
        ),
    }

    status = "PASS" if all(assertions.values()) else "FAIL"

    architecture = {
        "iNaiHR": {
            "role": "propose HORN / DUAL_HORN / AFFINE_SCC / FEEDBACK_CIRCUIT views",
            "boundary": "four proposals do not bound recursive total work",
        },
        "AURA": {
            "PAST": "canonical C020 Tear trilemma and prior local acyclic-unmasking tests",
            "OBSTACLE": "shared interface width and constrained feedback SCC",
            "GUIDE": "bounded-interface join plus typed SCC solvers",
            "OUTCOME": "verified witness, verified Tear, or OPEN",
        },
        "HRain": {
            "role": "content-addressed interface-state and proof DAG",
            "boundary": "memoization stores states but does not make 2^k states polynomial",
        },
        "JANUS_GATE": {
            "role": "verify Horn/dual-Horn witnesses, GF(2) witnesses/conflicts, and reduction maps",
        },
    }

    result = {
        "artifact_id": "C021-JANUS-OVERLAP-FEEDBACK-BARRIER",
        "status": status,
        "research_status": "EXPLORATORY_SOFTWARE_ONLY_NOT_CANONICAL",
        "seed": seed,
        "canonical_seed_sha256": CANONICAL_SEED,
        "software_only": True,
        "swarm_touched": False,
        "devices_touched": False,
        "nas_touched": False,
        "external_models_called": False,
        "telegram_backend_called": False,
        "architecture": architecture,
        "bounded_interface_composition": bounded,
        "horn_dual_horn_overlap": generic,
        "affine_cyclic_scc": affine,
        "nonlinear_feedback_reduction": feedback,
        "symbolic_substitution": substitution,
        "small_cycle_semantics": cycles,
        "assertions": assertions,
        "new_positive_result": (
            "Horn and dual-Horn modules can be composed exactly in O(2^k poly(L)) "
            "where k is their shared interface width; this is polynomial for k=O(log L). "
            "Affine cyclic SCCs are also polynomially decidable with proof-carrying GF(2) Tears."
        ),
        "new_obstruction": (
            "Every 3-clause is Horn or dual-Horn, so clause-wise language coverage already "
            "contains arbitrary 3-SAT. The missing resource is not language membership but "
            "a decomposition with a provably small semantic interface. In addition, a linear-size "
            "nonlinear feedback circuit with one constrained SCC is satisfiable exactly when "
            "an arbitrary source 3-CNF is satisfiable."
        ),
        "distance_to_p_equals_np": {
            "mathematical_status": "UNCHANGED_OPEN",
            "what_was_removed": [
                "The idea that tagging every clause with a tractable language is sufficient.",
                "The idea that all cyclic definitions are intrinsically hard.",
                "The idea that textual substitution is required; DAG sharing avoids that blowup.",
            ],
            "remaining_exact_target": (
                "Construct one deterministic polynomial-time selector that discovers a "
                "proof-carrying decomposition whose interface complexity is polynomially bounded, "
                "or handles large overlaps without enumerating 2^k states, for every CNF."
            ),
            "warning": (
                "A general solver for the nonlinear constrained-feedback class implemented here "
                "would already be a polynomial solver for 3-SAT."
            ),
        },
        "surviving_conjecture": {
            "name": "Polynomial Semantic Interface Selector Conjecture",
            "statement": (
                "For every CNF F of length L, one deterministic polynomial-time Observer "
                "constructs a proof-carrying network of tractable modules and cyclic SCC solvers "
                "whose total semantic interface state volume, proof volume, selection cost, "
                "and witness-recovery cost are poly(L)."
            ),
            "status": "OPEN",
        },
    }

    clean = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result["integrity"] = {"sha256": hashlib.sha256(clean.encode("utf-8")).hexdigest()}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    if args.output:
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.self_test and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
