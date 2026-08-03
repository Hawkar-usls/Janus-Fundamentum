from __future__ import annotations

import copy
import hashlib
import json
import sys
from typing import Iterable, Sequence

CLOSED = 'CLOSED_EXACT'
OPEN_DISCOVERY = 'OPEN_DISCOVERY_BUDGET'
OPEN_WORK = 'OPEN_WORK_BUDGET'
OPEN_CERT = 'OPEN_CERTIFICATE_VOLUME'


def canonical_json(value, pretty=False):
    if pretty:
        return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()


def check_integrity(obj):
    body = dict(obj)
    claimed = body.pop('integrity', None)
    if claimed != digest(body):
        raise AssertionError('integrity mismatch')


def check_case_integrity(case):
    check_integrity(case)
    if case.get('certificate_bytes') != len(canonical_json(case, pretty=True)):
        raise AssertionError('certificate byte mismatch')


def rref(rows: Iterable[int], dim: int) -> tuple[int, ...]:
    limit = 1 << dim
    table = {}
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= limit:
            raise ValueError('vector outside ambient space')
        while x:
            pivot = x.bit_length() - 1
            if pivot in table:
                x ^= table[pivot]
            else:
                table[pivot] = x
                for other, row in list(table.items()):
                    if other != pivot and ((row >> pivot) & 1):
                        table[other] = row ^ x
                break
    for pivot in sorted(table):
        row = table[pivot]
        for other in sorted(table, reverse=True):
            if other != pivot and ((table[other] >> pivot) & 1):
                table[other] ^= row
    return tuple(table[pivot] for pivot in sorted(table, reverse=True))


def contains(big: tuple[int, ...], small: tuple[int, ...]) -> bool:
    for raw in small:
        x = raw
        for row in big:
            x = min(x, x ^ row)
        if x:
            return False
    return True


def parse_stat(raw: dict, dim: int):
    value = int(raw['value'])
    if value < 0:
        raise ValueError('negative value')
    return rref(raw['left'], dim), rref(raw['right'], dim), value


def compact(sequence):
    seq = list(sequence)
    while True:
        changed = False
        for index in range(1, len(seq)):
            if seq[index - 1] == seq[index]:
                del seq[index]
                changed = True
                break
        if changed:
            continue
        for start in range(len(seq)):
            for end in range(start + 2, len(seq)):
                if seq[start][:2] != seq[end][:2]:
                    continue
                values = [item[2] for item in seq[start:end + 1]]
                increasing = values[0] <= values[-1] and all(
                    values[0] <= value <= values[-1] for value in values[1:-1]
                )
                decreasing = values[0] >= values[-1] and all(
                    values[0] >= value >= values[-1] for value in values[1:-1]
                )
                if increasing or decreasing:
                    del seq[start + 1:end]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq)


def trajectory(raw: Sequence[dict], dim: int):
    if not raw:
        raise ValueError('empty trajectory')
    seq = tuple(parse_stat(item, dim) for item in raw)
    if seq[0][1] != seq[-1][0]:
        raise ValueError('endpoint mismatch')
    for left, right in zip(seq, seq[1:]):
        if not contains(right[0], left[0]) or not contains(left[1], right[1]):
            raise ValueError('monotonicity')
    if compact(seq) != seq:
        raise ValueError('noncompact trajectory')
    return seq


def encode(sequence):
    return [
        {'left': list(stat[0]), 'right': list(stat[1]), 'value': stat[2]}
        for stat in sequence
    ]


def stat_leq(lower, upper):
    return lower[0] == upper[0] and lower[1] == upper[1] and lower[2] <= upper[2]


def canonical_path(lower, upper):
    parent = {}
    for i in range(len(lower)):
        for j in range(len(upper)):
            if not stat_leq(lower[i], upper[j]):
                continue
            if (i, j) == (0, 0):
                parent[(i, j)] = None
                continue
            for previous in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                if previous in parent:
                    parent[(i, j)] = previous
                    break
    terminal = len(lower) - 1, len(upper) - 1
    if terminal not in parent:
        return None
    path = []
    cursor = terminal
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    return path


def witness_payload(path, lower=None, upper=None, full=False):
    result = {'path': [list(cell) for cell in path], 'path_length': len(path)}
    if full:
        result['lower_extension'] = encode([lower[i] for i, _ in path])
        result['upper_extension'] = encode([upper[j] for _, j in path])
    return result


def verify_witness(lower, upper, witness, require_full=False):
    path = canonical_path(lower, upper)
    if path is None:
        return witness is None
    if witness is None:
        return False
    return witness == witness_payload(path, lower, upper, require_full)


def subspaces(dim):
    seen = {()}
    queue = [()]
    while queue:
        current = queue.pop(0)
        for vector in range(1, 1 << dim):
            candidate = rref((*current, vector), dim)
            if candidate not in seen:
                seen.add(candidate)
                queue.append(candidate)
    return tuple(sorted(seen))


def universe(dim, k):
    spaces = subspaces(dim)
    states = tuple(
        (left, right, value)
        for left in spaces
        for right in spaces
        for value in range(k + 1)
    )
    bound = (2 * dim + 1) * (2 * k + 1)
    emitted = {}

    def dfs(seq, target):
        last = seq[-1]
        if last[0] == target:
            emitted[seq] = seq
        if len(seq) >= bound:
            return
        for next_stat in states:
            if not contains(next_stat[0], last[0]):
                continue
            if not contains(last[1], next_stat[1]):
                continue
            if not contains(target, next_stat[0]):
                continue
            candidate = (*seq, next_stat)
            if compact(candidate) == candidate:
                dfs(candidate, target)

    for first in states:
        if contains(first[1], first[0]):
            dfs((first,), first[1])
    return tuple(emitted[key] for key in sorted(emitted))


def expected_minimal(generators):
    ordered = tuple(sorted({generator: generator for generator in generators}.values()))
    relation = {
        (i, j): canonical_path(lower, upper)
        for i, lower in enumerate(ordered)
        for j, upper in enumerate(ordered)
    }
    relation = {pair: path for pair, path in relation.items() if path is not None}
    retained_indices = []
    for j in range(len(ordered)):
        strict = any(
            i != j and (i, j) in relation and (j, i) not in relation
            for i in range(len(ordered))
        )
        equivalent_earlier = any(
            i < j and (i, j) in relation and (j, i) in relation
            for i in range(len(ordered))
        )
        if not strict and not equivalent_earlier:
            retained_indices.append(j)
    retained = tuple(ordered[index] for index in retained_indices)
    removals = []
    for j, removed in enumerate(ordered):
        if j in retained_indices:
            continue
        candidates = [i for i in retained_indices if (i, j) in relation]
        if not candidates:
            raise AssertionError('removed generator has no retained predecessor')
        i = min(candidates, key=lambda index: ordered[index])
        removals.append({
            'removed': encode(removed),
            'retained': encode(ordered[i]),
            'witness': witness_payload(relation[(i, j)]),
            'reason': (
                'STRICTLY_COVERED'
                if (j, i) not in relation
                else 'EQUIVALENT_CANONICAL_REPRESENTATIVE'
            ),
        })
    return retained, removals


def expected_closure(raw_closure):
    dim = int(raw_closure['ambient_dim'])
    k = int(raw_closure['k'])
    generators = tuple(
        trajectory(raw, dim) for raw in raw_closure['input_generators']
    )
    retained, removals = expected_minimal(generators)
    complete_universe = universe(dim, k)
    entries = []
    for candidate in complete_universe:
        chosen = None
        for index, source in enumerate(retained):
            path = canonical_path(source, candidate)
            if path is not None:
                chosen = index, path
                break
        if chosen is not None:
            entries.append({
                'trajectory': encode(candidate),
                'source_generator_index': chosen[0],
                'witness': witness_payload(chosen[1]),
            })
    return {
        'retained_generators': [encode(item) for item in retained],
        'removals': removals,
        'universe_size': len(complete_universe),
        'entries': entries,
        'entry_count': len(entries),
    }


def check_ledger(ledger, capability, terminal):
    if not isinstance(ledger, dict):
        raise AssertionError('bad ledger')
    if any(not isinstance(value, int) or value < 0 for value in ledger.values()):
        raise AssertionError('negative or noninteger ledger value')
    if terminal == CLOSED:
        if ledger.get('discovery_work', 0) > capability['discovery_work']:
            raise AssertionError('discovery cap exceeded')
        if ledger.get('work', 0) > capability['work']:
            raise AssertionError('work cap exceeded')


def verify_preorder_case(case):
    dim = case['ambient_dim']
    lower = trajectory(case['lower'], dim)
    upper = trajectory(case['upper'], dim)
    accepted = canonical_path(lower, upper) is not None
    if case['accepted'] != accepted:
        raise AssertionError('preorder answer mismatch')
    if accepted:
        if not verify_witness(lower, upper, case['witness'], require_full=True):
            raise AssertionError('preorder witness mismatch')
    elif case['witness'] is not None:
        raise AssertionError('negative preorder carries witness')
    check_ledger(case['ledger'], case['capability'], case['terminal'])


def verify_closure_case(case):
    closure = case['closure']
    expected = expected_closure(closure)
    for field in ('retained_generators', 'removals', 'universe_size', 'entries', 'entry_count'):
        if closure[field] != expected[field]:
            raise AssertionError(f'closure mismatch: {field}')
    if case.get('grouped_leaf_policy') != 'WHOLE_INPUT_SUBSPACES_ONLY':
        raise AssertionError('grouped leaf policy lost')
    if case.get('supplied_layout_used_for_discovery') is not False:
        raise AssertionError('supplied layout used')
    if case.get('sat_oracle_used') is not False:
        raise AssertionError('SAT oracle used')
    check_ledger(closure['ledger'], case['capability'], case['terminal'])


def verify_open_case(case):
    terminal = case['terminal']
    if terminal == OPEN_DISCOVERY:
        if case['cap'] != case['capability']['discovery_work']:
            raise AssertionError('discovery cap mismatch')
        if case['attempted'] != case['cap'] + 1:
            raise AssertionError('discovery attempted count mismatch')
        if case['ledger'].get('discovery_work') != case['cap']:
            raise AssertionError('discovery ledger mismatch')
    elif terminal == OPEN_WORK:
        if case['cap'] != case['capability']['work']:
            raise AssertionError('work cap mismatch')
        if case['attempted'] != case['cap'] + 1:
            raise AssertionError('work attempted count mismatch')
        if case['ledger'].get('work') != case['cap']:
            raise AssertionError('work ledger mismatch')
    elif terminal == OPEN_CERT:
        if case['required_certificate_bytes'] <= case['capability']['certificate_bytes']:
            raise AssertionError('certificate refusal not justified')
    else:
        raise AssertionError('unknown terminal')


def verify_artifact(artifact):
    check_integrity(artifact)
    if artifact.get('artifact_id') != 'C049.1-JANUS-PHASE-B2-EXTENSION-PREORDER-UP-K':
        raise AssertionError('wrong artifact')
    if artifact.get('phase') != 'B2':
        raise AssertionError('wrong phase')
    if artifact.get('strict_boundary', {}).get('no_layout_at_cap_enabled') is not False:
        raise AssertionError('NO_LAYOUT boundary drift')
    cases = artifact.get('cases')
    if not isinstance(cases, list) or len(cases) != 7:
        raise AssertionError('case set mismatch')
    seen = set()
    for case in cases:
        check_case_integrity(case)
        case_id = case['case_id']
        if case_id in seen:
            raise AssertionError('duplicate case')
        seen.add(case_id)
        if case.get('p_vs_np') != 'OPEN':
            raise AssertionError('P/NP status drift')
        if case['terminal'] == CLOSED:
            if case['phase'] == 'B2_EXTENSION_PREORDER':
                verify_preorder_case(case)
            elif case['phase'] == 'B2_UP_K_FULL_SET_CLOSURE':
                verify_closure_case(case)
            else:
                raise AssertionError('unknown closed phase')
        else:
            verify_open_case(case)
    summary = artifact['summary']
    by_id = {case['case_id']: case for case in cases}
    expected_summary = {
        'cases': len(cases),
        'closed_exact': sum(case['terminal'] == CLOSED for case in cases),
        'open_discovery_budget': sum(case['terminal'] == OPEN_DISCOVERY for case in cases),
        'open_work_budget': sum(case['terminal'] == OPEN_WORK for case in cases),
        'open_certificate_volume': sum(case['terminal'] == OPEN_CERT for case in cases),
        'preorder_positive': by_id['PREORDER_EXTENSION_REQUIRED']['accepted'],
        'preorder_negative': not by_id['PREORDER_PAIR_MISMATCH_REJECTED']['accepted'],
        'd1_k1_universe_size': by_id['UP_K_DOMINATED_GENERATOR_REMOVAL']['closure']['universe_size'],
        'd1_k1_full_set_entries': by_id['UP_K_DOMINATED_GENERATOR_REMOVAL']['closure']['entry_count'],
        'retained_generators': len(by_id['UP_K_DOMINATED_GENERATOR_REMOVAL']['closure']['retained_generators']),
        'removed_generators': len(by_id['UP_K_DOMINATED_GENERATOR_REMOVAL']['closure']['removals']),
        'd0_k2_universe_size': by_id['UP_K_DIMENSION_ZERO_COMPLETE_UNIVERSE']['closure']['universe_size'],
        'd0_k2_full_set_entries': by_id['UP_K_DIMENSION_ZERO_COMPLETE_UNIVERSE']['closure']['entry_count'],
        'failures': 0,
    }
    if summary != expected_summary:
        raise AssertionError('summary mismatch')


def repair_digests(artifact):
    for case in artifact['cases']:
        case.pop('integrity', None)
        case['certificate_bytes'] = 0
        while True:
            case['integrity'] = digest({
                key: value for key, value in case.items() if key != 'integrity'
            })
            measured = len(canonical_json(case, pretty=True))
            if measured == case['certificate_bytes']:
                break
            case['certificate_bytes'] = measured
    artifact.pop('integrity', None)
    artifact['integrity'] = digest(artifact)


def self_tamper_controls(artifact):
    controls = []

    altered_path = copy.deepcopy(artifact)
    case = next(
        item for item in altered_path['cases']
        if item['case_id'] == 'UP_K_DOMINATED_GENERATOR_REMOVAL'
    )
    case['closure']['entries'][0]['witness']['path'][0] = [1, 1]
    controls.append(altered_path)

    missing_entry = copy.deepcopy(artifact)
    case = next(
        item for item in missing_entry['cases']
        if item['case_id'] == 'UP_K_DOMINATED_GENERATOR_REMOVAL'
    )
    case['closure']['entries'].pop()
    case['closure']['entry_count'] -= 1
    controls.append(missing_entry)

    altered_deletion = copy.deepcopy(artifact)
    case = next(
        item for item in altered_deletion['cases']
        if item['case_id'] == 'UP_K_DOMINATED_GENERATOR_REMOVAL'
    )
    case['closure']['removals'][0]['witness']['path'][0] = [1, 1]
    controls.append(altered_deletion)

    for control in controls:
        repair_digests(control)
        try:
            verify_artifact(control)
        except Exception:
            continue
        raise AssertionError('digest-repaired semantic tamper accepted')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: verifier FULL_ARTIFACT.json')
    with open(sys.argv[1], encoding='utf-8') as handle:
        artifact = json.load(handle)
    verify_artifact(artifact)
    self_tamper_controls(artifact)
    print('VERIFIED C049.1 PHASE B2 FULL TRANSCRIPTS')
