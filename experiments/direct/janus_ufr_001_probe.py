#!/usr/bin/env python3
"""Read-only structural opportunity probe over an existing C023 trace.

No C023 caches/certificates are altered; counts are potential reuse only.
"""
from __future__ import annotations

import argparse
import json

from janus_ufr_001 import canonicalize, find_verified_match


def inspect_completed_states(policy, *, max_variables=12, max_candidates=720):
    seen = {}
    inspected = 0
    candidates = 0
    verified = 0
    fallback = 0
    # State IDs are not necessarily completion order; proof-independent scan
    # measures opportunities, NOT claims hits in depth-first execution.
    for state in policy.states.values():
        key = state['key']
        can = canonicalize(key, max_variables=max_variables,
                           max_candidates=max_candidates)
        inspected += 1
        fallback += int(not can.exhaustive)
        if can.key in seen:
            candidates += 1
            prior = seen[can.key]
            if prior != key and find_verified_match(prior, key,
                    max_variables=max_variables, max_candidates=max_candidates) is not None:
                verified += 1
        else:
            seen[can.key] = key
    return {
        'status': 'DIAGNOSTIC_ONLY', 'states_inspected': inspected,
        'matching_keys': candidates,
        'verified_nonidentical_renamings': verified,
        'bounded_fallbacks': fallback,
        'claim_boundary': 'not executed cache hits, not speedup, no C023 verifier change',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture', choices=['diamond', 'maj3-k4', 'gt4'], default='diamond')
    parser.add_argument('--max-variables', type=int, default=12)
    args = parser.parse_args()
    from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
    if args.fixture == 'diamond':
        from janus_tear_policy0a_context_obstruction import cache_diamond_cnf
        cnf, count = cache_diamond_cnf(2)
    elif args.fixture == 'maj3-k4':
        from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
        from janus_tear_policy0a_masked_tseitin import K4_EDGES
        cnf, count = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    else:
        from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
        cnf, count = graph_tautology_cnf(4)
    policy = FCTracePolicy()
    result, root = policy.solve(cnf, count)
    assert result.answer is not None and root is not None
    assert verify_fc_trace(cnf, count, policy, root) == result.answer
    output = inspect_completed_states(policy, max_variables=args.max_variables)
    output.update(fixture=args.fixture, c023_answer=result.answer,
                  c023_calls=result.calls, c023_exact_cache_hits=result.cache_hits)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
