#!/usr/bin/env python3
from __future__ import annotations
import itertools, json, random
import janus_c037_certified_polynomial_ping_pong as c


def source_eval(clauses, assignment):
    return all(any(assignment[abs(lit)] == (lit > 0) for lit in clause) for clause in clauses)


def reduce_3cnf(clauses, n):
    # Variables 1..n are source bits; n+1..2n are complements.
    affine = tuple(((1 << (i - 1)) | (1 << (n + i - 1)), 1) for i in range(1, n + 1))
    horn = []
    for clause in clauses:
        falsity = []
        for lit in clause:
            v = abs(lit)
            falsity.append(n + v if lit > 0 else v)
        horn.append(tuple(-v for v in falsity))
    return c.norm(horn), affine


def reduced_sat(clauses, n):
    horn, affine = reduce_3cnf(clauses, n)
    for bits in itertools.product((False, True), repeat=2 * n):
        a = {i + 1: bits[i] for i in range(2 * n)}
        if c.eh(horn, a) and c.ea(affine, a):
            return True
    return False


def run():
    rng = random.Random(370370)

    # Deterministic 3-CNF / NAND3+NEQ images preserve satisfiability, while the
    # constants-only bridge remains OPEN when no unary facts are exposed.
    mapping_checks = 0
    open_images = 0
    for _ in range(40):
        n = 4
        clauses = []
        for _ in range(5):
            vs = rng.sample(range(1, n + 1), 3)
            clauses.append(tuple(v if rng.random() < .5 else -v for v in vs))
        source_sat = any(source_eval(clauses, {i + 1: b[i] for i in range(n)}) for b in itertools.product((False, True), repeat=n))
        assert source_sat == reduced_sat(clauses, n)
        h, a = reduce_3cnf(clauses, n)
        result = c.pingpong(h, a, 2 * n, range(1, 2 * n + 1), budget=500000)
        assert result['terminal']['status'] in ('OPEN_FIXPOINT', 'CONFLICT')
        if result['terminal']['status'] == 'OPEN_FIXPOINT':
            open_images += 1
        mapping_checks += 1

    # Equality syntax/order permutations do not authorize a false merge or a
    # compatibility claim. Equality versus NEQ remains a jointly UNSAT OPEN.
    equality_a = c.norm(((-1, 2), (1, -2)))
    equality_b = c.norm(((1, -2), (-1, 2), (-1, 2)))
    assert c.payloads(equality_a, ((3, 1),), 2)[0]['digest'] == c.payloads(equality_b, ((3, 1),), 2)[0]['digest']
    eq = c.pingpong(equality_b, ((3, 1),), 2, (2, 1), budget=100000)
    assert eq['terminal']['status'] == 'OPEN_FIXPOINT' and not c.models(equality_b, ((3, 1),), 2)

    # A beta-acyclic but non-Horn region is outside the admitted native language.
    beta_non_horn = ((1, 2), (-2, 3))
    assert c.pingpong(beta_non_horn, tuple(), 3, (1, 2, 3))['terminal']['status'] == 'OPEN_LANGUAGE'

    # Easy duplicate syntax is normalized before negotiation and cannot create
    # an exponential product trace.
    easy = tuple([(1,)] * 128)
    easy_result = c.pingpong(easy, ((1, 1),), 1, (1,), budget=100000)
    assert len(c.norm(easy)) == 1
    assert len(easy_result.get('events', [])) <= 1

    print(json.dumps({
        'status': 'PASS',
        'deterministic_3cnf_mapping_checks': mapping_checks,
        'nand3_neq_open_images': open_images,
        'order_sensitive_equality_control': 'CANONICAL_AND_OPEN_ON_NEQ',
        'beta_acyclic_cyclic_interface_control': 'OPEN_LANGUAGE',
        'easy_duplicate_syntax': 'NORMALIZED_TO_ONE_CLAUSE',
        'p_vs_np': 'OPEN'
    }, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    run()
