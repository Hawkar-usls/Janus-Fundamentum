#!/usr/bin/env python3
"""Pre-registered adversarial comparison: original C023 vs opt-in UFR C023.

Independent 3-SAT and Exact-One fixtures are freshly generated from fixed seeds;
the Exact-One inputs are encoded exactly as at-least-one plus pairwise at-most-one
CNF. Only sound, independently replayed completed runs count as successes.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
import random
import time
import tracemalloc

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
from janus_tear_policy0a_masked_tseitin import (
    K4_EDGES, canonical_cnf, visible_tseitin_cnf,
)
from janus_ufr_001_certified_fc import (
    UFRFCTracePolicy, replay_ufr, serialize_ufr,
)


def random_sat(seed, n=10, clauses=42):
    rng = random.Random(seed)
    rows = []
    for _ in range(clauses):
        choices = rng.sample(range(1, n + 1), 3)
        rows.append(tuple(v if rng.randrange(2) else -v for v in choices))
    return canonical_cnf(rows), n


def random_exact_one_cnf(seed, n=8, constraints=12):
    rng = random.Random(seed)
    rows = []
    for _ in range(constraints):
        vs = rng.sample(range(1, n + 1), 3)
        lits = tuple(v if rng.randrange(2) else -v for v in vs)
        rows.append(lits)
        rows.extend((-a, -b) for a, b in combinations(lits, 2))
    return canonical_cnf(rows), n


def fixtures(extended=False):
    from janus_tear_policy0a_context_obstruction import complete_width_four_core
    def renamed_twin_unsat_cnf():
        shared = [(2, v) for v in (3, 4, 5, 6)]
        shared += [(-2, v) for v in (7, 8, 9, 10)]
        clauses = shared + [(1,) + row for row in complete_width_four_core(10)]
        clauses += [(-1,) + row for row in complete_width_four_core(14)]
        clauses.append((19, 20, 21))
        return canonical_cnf(clauses), 21
    # CI explicitly replays a nontrivial positive UFR cache-edge fixture.
    yield 'RENAMED_TWIN_POSITIVE_CONTROL', renamed_twin_unsat_cnf()
    yield 'GT4', graph_tautology_cnf(4)
    tseitin, count = visible_tseitin_cnf(4, K4_EDGES)
    yield 'TSEITIN_K4_NONAFFINE_WRAPPED', (canonical_cnf(list(tseitin) + [(count + 1, count + 2, count + 3)]), count + 3)
    for seed in (173, 191, 227):
        yield f'INDEPENDENT_3SAT_SEED_{seed}', random_sat(seed)
    for seed in (271, 307, 353):
        yield f'INDEPENDENT_EXACT_ONE_SEED_{seed}', random_exact_one_cnf(seed)
    if extended:
        yield 'GT5', graph_tautology_cnf(5)
        yield 'MAJ3_K4', maj3_lifted_tseitin_cnf(4, K4_EDGES)


def run_case(cnf, n, method, max_states):
    if method == 'EXACT_C023':
        policy = FCTracePolicy(state_cap=max_states)
    else:
        policy = UFRFCTracePolicy(
            state_cap=max_states, max_variables=24,
            max_candidates=120, max_literals=120,
        )
    tracemalloc.start()
    started = time.perf_counter()
    result, root_call = policy.solve(cnf, n)
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    verified = False
    if result.answer is not None:
        if root_call is not None:
            if method == 'EXACT_C023':
                verified = verify_fc_trace(cnf, n, policy, root_call) == result.answer
            else:
                verified = replay_ufr(cnf, n,
                                      serialize_ufr(policy, root_call)) == result.answer
        else:
            # Root affine dispatch is correct in baseline; record separately.
            verified = False
    return {
        'answer': result.answer,
        'status': ('PASS_REPLAY' if verified else
                   'AFFINE_ROOT_NOT_REPLAYED' if result.answer is not None and root_call is None else
                   'STATE_CAP_INCONCLUSIVE'),
        'calls': result.calls,
        'unique_states': result.unique_states,
        'exact_cache_hits': result.cache_hits,
        'isomorphic_cache_hits': getattr(policy, 'iso_hits', 0),
        'canonicalization_checks': getattr(policy, 'iso_checks', 0),
        'canonicalization_fallbacks': getattr(policy, 'iso_fallbacks', 0),
        'canonicalization_seconds': round(getattr(policy, 'iso_seconds', 0), 6),
        'wall_seconds': round(elapsed, 6),
        'peak_tracemalloc_bytes': peak,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--extended', action='store_true')
    parser.add_argument('--state-cap', type=int, default=3000)
    args = parser.parse_args()
    records = []
    for name, (cnf, n) in fixtures(args.extended):
        baseline = run_case(cnf, n, 'EXACT_C023', args.state_cap)
        ufr = run_case(cnf, n, 'CERTIFIED_UFR_C023', args.state_cap)
        if baseline['answer'] is not None and ufr['answer'] is not None:
            assert baseline['answer'] == ufr['answer'], (name, baseline, ufr)
        assert baseline['status'] == ufr['status'] or (
            baseline['status'] == 'STATE_CAP_INCONCLUSIVE' and
            ufr['status'] == 'PASS_REPLAY'
        ) or (
            baseline['status'] == 'PASS_REPLAY' and
            ufr['status'] == 'STATE_CAP_INCONCLUSIVE'
        ), (name, baseline, ufr)
        records.append({'fixture': name, 'variables': n, 'clauses': len(cnf),
                        'baseline': baseline, 'ufr': ufr})
    print(json.dumps({
        'experiment': 'JANUS-UFR-001-C023-ADVERSARIAL',
        'extended': args.extended,
        'state_cap': args.state_cap,
        'claim_boundary': 'finite optional research; no Feigenbaum scaling or general polynomial-time SAT algorithm',
        'cases': records,
    }, indent=2, sort_keys=True))
    assert all(row['baseline']['answer'] is None or
               row['baseline']['status'] in ('PASS_REPLAY', 'AFFINE_ROOT_NOT_REPLAYED')
               for row in records)
    assert all(row['ufr']['answer'] is None or
               row['ufr']['status'] in ('PASS_REPLAY', 'AFFINE_ROOT_NOT_REPLAYED')
               for row in records)


if __name__ == '__main__':
    main()
