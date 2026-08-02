#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import random
from typing import Any

from c039_affine_core import Equation, VTree, digest, evaluate_equation
from c039_affine_compile import compile_affine
from c039_affine_verify import affine_separator, verify_compilation, verify_node_semantics_small


def blocked_eq_vtree(n: int) -> VTree:
    def balanced(vs: list[int]) -> VTree:
        if len(vs) == 1:
            return vs[0]
        split = len(vs) // 2
        return (balanced(vs[:split]), balanced(vs[split:]))
    return (balanced(list(range(1, n + 1))), balanced(list(range(n + 1, 2 * n + 1))))


def equality_system(n: int) -> tuple[Equation, ...]:
    return tuple(Equation((1 << (i - 1)) | (1 << (n + i - 1)), 0) for i in range(1, n + 1))


def random_affine(rng: random.Random, n: int, m: int) -> tuple[Equation, ...]:
    rows: list[Equation] = []
    for _ in range(m):
        mask = 0
        while mask == 0:
            for i in range(n):
                if rng.random() < 0.35:
                    mask |= 1 << i
        rows.append(Equation(mask, rng.randrange(2)))
    return tuple(rows)


def exhaustive_sat(equations: tuple[Equation, ...], n: int) -> bool:
    return any(
        all(evaluate_equation(eq, {i + 1: bits[i] for i in range(n)}) for eq in equations)
        for bits in itertools.product((False, True), repeat=n)
    )


def tseitin_cycle(n: int, unsat: bool) -> tuple[Equation, ...]:
    # Edge variables e_i on a cycle. Vertex i constrains e_{i-1} xor e_i.
    charges = [0] * n
    if unsat:
        charges[0] = 1
    rows = []
    for i in range(n):
        prev_edge = ((i - 1) % n) + 1
        next_edge = i + 1
        mask = (1 << (prev_edge - 1)) | (1 << (next_edge - 1))
        rows.append(Equation(mask, charges[i]))
    return tuple(rows)


def run_self_test(seed: int = 390039) -> dict[str, Any]:
    rng = random.Random(seed)
    random_cases = 0
    random_sat = 0
    random_unsat = 0
    max_rows = 0
    for _ in range(450):
        n = rng.randint(1, 8)
        equations = random_affine(rng, n, rng.randint(0, n + 5))
        certificate = compile_affine(equations, n, work_budget=2_000_000, row_budget=100_000, certificate_budget=4_000_000)
        assert certificate['status'] in ('SAT', 'UNSAT')
        assert verify_compilation(certificate)
        assert verify_node_semantics_small(certificate)
        expected = exhaustive_sat(equations, n)
        assert (certificate['status'] == 'SAT') == expected
        random_sat += int(expected)
        random_unsat += int(not expected)
        random_cases += 1
        max_rows = max(max_rows, max((len(node['message']['rows']) for node in certificate['nodes']), default=0))

    equality_controls = []
    for n in (4, 8, 16, 32, 64):
        equations = equality_system(n)
        certificate = compile_affine(
            equations,
            2 * n,
            supplied_vtree=blocked_eq_vtree(n),
            work_budget=12_000_000,
            row_budget=500_000,
            certificate_budget=30_000_000,
        )
        assert certificate['status'] == 'SAT' and verify_compilation(certificate)
        message_rows = max(len(node['message']['rows']) for node in certificate['nodes'])
        assert message_rows <= 2 * n
        equality_controls.append({
            'n': n,
            'explicit_c038_cut_classes': str(1 << n),
            'max_symbolic_message_rows': message_rows,
            'work_units': certificate['cost']['work_units'],
            'vtree_discovery': certificate['vtree_discovery'],
        })

    tseitin = []
    for n in (6, 10, 18, 30):
        for unsat in (False, True):
            certificate = compile_affine(tseitin_cycle(n, unsat), n, work_budget=5_000_000, certificate_budget=8_000_000)
            assert verify_compilation(certificate)
            assert (certificate['status'] == 'UNSAT') == unsat
            tseitin.append({'n': n, 'unsat': unsat, 'status': certificate['status'], 'work_units': certificate['cost']['work_units']})

    pair_checks = 0
    for _ in range(250):
        n = rng.randint(1, 7)
        a = random_affine(rng, n, rng.randint(0, n + 2))
        b = random_affine(rng, n, rng.randint(0, n + 2))
        result = affine_separator(a, b, n)
        if result['status'] == 'SEPARATOR':
            assignment = {int(v): bool(value) for v, value in result['assignment'].items()}
            sat_a = all(evaluate_equation(eq, assignment) for eq in a)
            sat_b = all(evaluate_equation(eq, assignment) for eq in b)
            assert sat_a != sat_b
        else:
            models_a = set()
            models_b = set()
            for bits in itertools.product((False, True), repeat=n):
                assignment = {i + 1: bits[i] for i in range(n)}
                if all(evaluate_equation(eq, assignment) for eq in a):
                    models_a.add(bits)
                if all(evaluate_equation(eq, assignment) for eq in b):
                    models_b.add(bits)
            assert models_a == models_b
        pair_checks += 1

    open_language = compile_affine(tuple(), 3, language='HORN_AFFINE_MIXED')
    assert open_language['status'] == 'OPEN' and open_language['reason'] == 'OPEN_LANGUAGE'
    nand3_neq = compile_affine(tuple(), 6, language='NAND3_NEQ_IMAGE')
    assert nand3_neq['status'] == 'OPEN' and nand3_neq['reason'] == 'OPEN_LANGUAGE'
    beta_non_affine = compile_affine(tuple(), 4, language='BETA_ACYCLIC_NON_AFFINE')
    assert beta_non_affine['status'] == 'OPEN' and beta_non_affine['reason'] == 'OPEN_LANGUAGE'
    budget_control = compile_affine(equality_system(20), 40, supplied_vtree=blocked_eq_vtree(20), work_budget=25)
    assert budget_control['status'] == 'OPEN'

    corrupt = compile_affine((Equation(1, 0), Equation(1, 1)), 1)
    assert corrupt['status'] == 'UNSAT' and verify_compilation(corrupt)
    corrupt['unsat_certificate']['provenance'] ^= 1
    corrupt['integrity_sha256'] = digest({k: v for k, v in corrupt.items() if k != 'integrity_sha256'})
    assert not verify_compilation(corrupt)

    result = {
        'artifact_id': 'C039-PROOF-CARRYING-SYMBOLIC-AFFINE-FACTORS',
        'status': 'PASS',
        'p_vs_np': 'OPEN',
        'seed': seed,
        'constructive_lemma': (
            'For affine GF(2) factors on any validated vtree, bottom-up conjoin/project/canonicalize '
            'produces exact canonical boundary relations with at most |B_u| rows per region. Discovery, '
            'join, projection, merge comparison, witness recovery, and UNSAT provenance are all charged '
            'and polynomial; no truth-table or SAT oracle is used.'
        ),
        'random_affine_cases': random_cases,
        'random_sat': random_sat,
        'random_unsat': random_unsat,
        'random_max_message_rows': max_rows,
        'equality_blocked_vtree_controls': equality_controls,
        'tseitin_cycle_controls': tseitin,
        'affine_merge_separator_checks': pair_checks,
        'open_language_controls': ['HORN_AFFINE_MIXED', 'NAND3_NEQ_IMAGE', 'BETA_ACYCLIC_NON_AFFINE'],
        'budget_control': budget_control['reason'],
        'corrupt_unsat_provenance': 'REJECTED',
        'new_gate': 'CROSS_LANGUAGE_SYMBOLIC_PROJECTION_CLOSED_UNDER_JOIN',
        'claim_boundary': (
            'The theorem closes symbolic factor construction for the affine portfolio branch, not for arbitrary CNF. '
            'Horn-affine and NAND3+NEQ mixtures return OPEN_LANGUAGE, and exponential lower bounds for explicit '
            'communication rows are not treated as general lower bounds.'
        ),
    }
    result['integrity_sha256'] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--seed', type=int, default=390039)
    args = parser.parse_args()
    result = run_self_test(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.self_test:
        assert result['status'] == 'PASS'


if __name__ == '__main__':
    main()
