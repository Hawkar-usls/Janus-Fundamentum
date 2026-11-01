#!/usr/bin/env python3
"""UFR-001 opt-in experimental C023 interface: verified isomorphic cache edges.

Production C023 FCTracePolicy and its strict serialized verifier are untouched.
Boolean reuse requires a completed target, a total literal-preserving variable
bijection, and an independently replayed proof trace. No Feigenbaum claim.
"""
from __future__ import annotations

from copy import deepcopy
from time import perf_counter
from typing import Any

from janus_tear_policy0a_fc_trace import FCTracePolicy
from janus_tear_policy0a_masked_tseitin import (
    CNF, canonical_cnf, simplify_one, visible_affine_root_decision,
)
from janus_tear_policy0t_trace_certificate import (
    branch_variable, resolution_trace, unit_trace,
)
from janus_ufr_001 import canonicalize, find_verified_match, variables, verify_renaming


class UFRFCTracePolicy(FCTracePolicy):
    """Original search + optional proven equivalent residual reuse.

    The delegate performs identical C023 transitions when there is no match.
    No state is indexed until its delegated search call has completed.
    """

    def __init__(self, state_cap: int | None = None, *,
                 max_variables: int = 12, max_candidates: int = 720,
                 max_literals: int = 120) -> None:
        super().__init__(state_cap)
        self.max_variables = max_variables
        self.max_candidates = max_candidates
        self.max_literals = max_literals
        self.completed_iso: dict[CNF, list[tuple[CNF, int, bool]]] = {}
        self.iso_hits = 0
        self.iso_checks = 0
        self.iso_seconds = 0.0
        self.iso_fallbacks = 0

    def solve(self, cnf: CNF, variable_count: int):
        self.completed_iso = {}
        self.iso_hits = 0
        self.iso_checks = 0
        self.iso_seconds = 0.0
        self.iso_fallbacks = 0
        return super().solve(cnf, variable_count)

    def candidate(self, key: CNF):
        if len(variables(key)) > self.max_variables:
            return None
        if sum(len(row) for row in key) > self.max_literals:
            return None
        start = perf_counter()
        try:
            can = canonicalize(key, 'SAT',
                               max_variables=self.max_variables,
                               max_candidates=self.max_candidates)
            self.iso_checks += 1
            self.iso_fallbacks += int(not can.exhaustive)
            return can.key
        finally:
            self.iso_seconds += perf_counter() - start

    def search(self, cnf: CNF, depth: int, context: tuple[int, ...]):
        # Only evaluate a candidate if there exists a completed state.
        if self.completed_iso:
            propagated, contradiction, events = unit_trace(cnf)
            if not contradiction and propagated and propagated not in self.completed_memo:
                can_key = self.candidate(propagated)
                if can_key is not None:
                    for original, target_id, target_answer in self.completed_iso.get(can_key, []):
                        if propagated == original:
                            continue
                        started = perf_counter()
                        mapping = find_verified_match(
                            propagated, original, 'SAT',
                            max_variables=self.max_variables,
                            max_candidates=self.max_candidates,
                        )
                        self.iso_seconds += perf_counter() - started
                        if mapping is None:
                            continue
                        assert verify_renaming(propagated, original, mapping, 'SAT')
                        self.maximum_depth = max(self.maximum_depth, depth)
                        call_id = self.new_call({
                            'input': cnf, 'depth': depth, 'context': context,
                            'pre_units': events, 'pre_result': propagated,
                            'key': propagated,
                            'terminal': 'ISOMORPHIC_CACHE_HIT',
                            'cache_target': target_id,
                            'renaming': tuple(sorted(mapping.items())),
                            'result': target_answer,
                        })
                        self.iso_hits += 1
                        return target_answer, call_id

        answer, call_id = super().search(cnf, depth, context)
        call = self.calls[call_id]
        if call.get('terminal') == 'STATE':
            key = call['key']
            can_key = self.candidate(key)
            if can_key is not None:
                self.completed_iso.setdefault(can_key, []).append(
                    (key, int(call['state']), answer)
                )
        return answer, call_id


def serialize_ufr(policy: UFRFCTracePolicy, root_call: int) -> dict[str, Any]:
    return {
        'schema': 'JANUS-UFR-FC-001',
        'root_call': root_call,
        'calls': deepcopy(policy.calls),
        'states': deepcopy(policy.states),
    }


def replay_ufr(root_cnf: CNF, variable_count: int, certificate: dict[str, Any]) -> bool:
    """Independent replay: never trust the producer's canonical keys or memo.

    Reconstruct unit propagation, local Resolution, branching and completed
    state order, including the exact bijection at every isomorphic cache hit.
    """
    assert certificate['schema'] == 'JANUS-UFR-FC-001'
    root = canonical_cnf(root_cnf)
    affine, _ = visible_affine_root_decision(root, variable_count)
    assert affine is None
    calls, states = certificate['calls'], certificate['states']
    assert isinstance(calls, dict) and isinstance(states, dict)
    visited_calls: set[int] = set()
    visited_states: set[int] = set()
    completed_exact: dict[CNF, tuple[bool, int]] = {}
    completed_id: dict[int, tuple[CNF, bool]] = {}

    def visit(call_id: int, input_cnf: CNF, depth: int,
              context: tuple[int, ...]) -> bool:
        assert type(call_id) is int and call_id in calls
        assert call_id not in visited_calls
        visited_calls.add(call_id)
        call = calls[call_id]
        assert call['input'] == input_cnf
        assert call['depth'] == depth and call['context'] == context
        after_unit, conflict, events = unit_trace(input_cnf)
        assert call['pre_units'] == events and call['pre_result'] == after_unit
        if conflict:
            assert call['terminal'] == 'PRE_UNIT_CONTRADICTION'
            assert call['result'] is False
            return False
        assert after_unit is not None
        if not after_unit:
            assert call['terminal'] == 'SAT_EMPTY' and call['result'] is True
            return True
        assert call['key'] == after_unit
        terminal = call['terminal']
        if terminal == 'CACHE_HIT':
            assert after_unit in completed_exact
            expected, target = completed_exact[after_unit]
            assert call['cache_target'] == target and call['result'] == expected
            return expected
        if terminal == 'ISOMORPHIC_CACHE_HIT':
            target_id = call['cache_target']
            assert type(target_id) is int and target_id in completed_id
            old_key, old_answer = completed_id[target_id]
            assert after_unit != old_key
            pairs = call['renaming']
            assert isinstance(pairs, (list, tuple))
            assert all(isinstance(p, (list, tuple)) and len(p) == 2
                       and all(type(x) is int for x in p) for p in pairs)
            assert tuple(tuple(p) for p in pairs) == tuple(sorted(tuple(p) for p in pairs))
            mapping = dict(pairs)
            assert len(mapping) == len(pairs)
            assert verify_renaming(after_unit, old_key, mapping, 'SAT')
            assert call['result'] is old_answer
            return old_answer

        assert terminal == 'STATE'
        state_id = call['state']
        assert type(state_id) is int and state_id in states
        assert state_id not in visited_states
        visited_states.add(state_id)
        state = states[state_id]
        assert state['id'] == state_id
        assert state['entry_call'] == call_id and state['key'] == after_unit
        assert state['depth'] == depth and state['context'] == context

        literal_count = sum(len(row) for row in after_unit)
        width = max(map(len, after_unit)) + 1
        attempts_budget = max(64, 4 * literal_count)
        additions_budget = max(8, len(after_unit) // 4)
        assert state['width_limit'] == width
        assert state['attempt_budget'] == attempts_budget
        assert state['addition_budget'] == additions_budget
        saturated, refuted, attempts, additions, resolution_events = resolution_trace(
            after_unit, width, attempts_budget, additions_budget
        )
        assert state['resolution_output'] == saturated
        assert state['resolution_refuted'] == refuted
        assert state['resolution_attempts'] == attempts
        assert state['resolution_additions'] == additions
        assert state['resolution_events'] == resolution_events
        if refuted:
            assert state['terminal'] == 'RESOLUTION_CONTRADICTION'
            result = False
        else:
            post, contradiction, post_events = unit_trace(saturated)
            assert state['post_units'] == post_events
            assert state['post_result'] == post
            if contradiction:
                assert state['terminal'] == 'POST_UNIT_CONTRADICTION'
                result = False
            elif not post:
                assert state['terminal'] == 'SAT_EMPTY'
                result = True
            else:
                assert post is not None
                pivot = branch_variable(post)
                assert state['branch_var'] == pivot
                children = state['children']
                assert isinstance(children, list)
                answers: list[bool] = []
                for child in children:
                    value = child['value']
                    assert type(value) is bool
                    literal = pivot if value else -pivot
                    assert child['literal'] == literal
                    child_input = simplify_one(post, pivot, value)
                    if child_input is None:
                        assert child['direct_conflict'] is True
                        assert child['call'] is None and child['result'] is False
                        answers.append(False)
                    else:
                        assert child['direct_conflict'] is False
                        child_answer = visit(child['call'], child_input,
                                             depth + 1, context + (literal,))
                        assert child['result'] is child_answer
                        answers.append(child_answer)
                    if answers[-1]:
                        break
                assert len(children) == len(answers)
                result = any(answers)
                assert state['terminal'] == ('BRANCH_SAT' if result else 'BRANCH_UNSAT')

        assert state['result'] is result and call['result'] is result
        assert after_unit not in completed_exact
        completed_exact[after_unit] = (result, state_id)
        completed_id[state_id] = (after_unit, result)
        return result

    answer = visit(certificate['root_call'], root, 0, ())
    assert visited_calls == set(calls)
    assert visited_states == set(states)
    return answer


def dump_ufr_json(policy: UFRFCTracePolicy, root_call: int) -> str:
    """Lossless JSON wire envelope: preserves tuple/list and integer dict keys."""
    import json

    def encode(obj):
        if isinstance(obj, tuple):
            return {'__ufr_tuple_v1__': [encode(x) for x in obj]}
        if isinstance(obj, list):
            return [encode(x) for x in obj]
        if isinstance(obj, dict):
            return {'__ufr_dict_v1__': [[encode(k), encode(v)]
                                        for k, v in obj.items()]}
        if obj is None or type(obj) in (int, bool, str, float):
            return obj
        raise TypeError(f'unsupported wire type: {type(obj).__name__}')

    return json.dumps(encode(serialize_ufr(policy, root_call)),
                      sort_keys=True, separators=(',', ':'))


def load_ufr_json(payload: str) -> dict[str, Any]:
    """Decode only the explicit tagged primitives, rejecting malformed envelopes."""
    import json

    if type(payload) is not str or len(payload) > 25_000_000:
        raise ValueError('invalid UFR certificate payload')
    wire = json.loads(payload)

    def decode(obj):
        if isinstance(obj, list):
            return [decode(x) for x in obj]
        if isinstance(obj, dict):
            if set(obj) == {'__ufr_tuple_v1__'}:
                assert isinstance(obj['__ufr_tuple_v1__'], list)
                return tuple(decode(x) for x in obj['__ufr_tuple_v1__'])
            if set(obj) == {'__ufr_dict_v1__'}:
                pairs = obj['__ufr_dict_v1__']
                assert isinstance(pairs, list)
                result = {}
                for pair in pairs:
                    assert isinstance(pair, list) and len(pair) == 2
                    key, value = decode(pair[0]), decode(pair[1])
                    assert key not in result
                    result[key] = value
                return result
            raise ValueError('non-canonical UFR wire tag')
        if obj is None or type(obj) in (int, bool, str, float):
            return obj
        raise ValueError('invalid UFR wire atom')

    certificate = decode(wire)
    assert isinstance(certificate, dict)
    return certificate


def replay_ufr_json(root_cnf: CNF, variable_count: int,
                    payload: str) -> bool:
    """Independently replay a round-tripped portable certificate."""
    return replay_ufr(root_cnf, variable_count, load_ufr_json(payload))
