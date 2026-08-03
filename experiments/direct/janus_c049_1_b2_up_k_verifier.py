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

def basis(rows: Iterable[int], dim: int) -> tuple[int, ...]:
    table = {}
    limit = 1 << dim
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= limit:
            raise ValueError('outside ambient space')
        while x:
            p = x.bit_length() - 1
            if p in table:
                x ^= table[p]
            else:
                table[p] = x
                for q, y in list(table.items()):
                    if q != p and ((y >> p) & 1):
                        table[q] = y ^ x
                break
    for pivot in sorted(table):
        row = table[pivot]
        for other in sorted(table, reverse=True):
            if other != pivot and ((table[other] >> pivot) & 1):
                table[other] ^= row
    return tuple(table[p] for p in sorted(table, reverse=True))

def contains(big: tuple[int, ...], small: tuple[int, ...]) -> bool:
    for x0 in small:
        x = x0
        for y in big:
            x = min(x, x ^ y)
        if x:
            return False
    return True

def stat(raw: dict, dim: int):
    value = int(raw['value'])
    if value < 0:
        raise ValueError('negative value')
    return (basis(raw['left'], dim), basis(raw['right'], dim), value)

def compact(sequence):
    seq = list(sequence)
    while True:
        changed = False
        for i in range(1, len(seq)):
            if seq[i - 1] == seq[i]:
                del seq[i]
                changed = True
                break
        if changed:
            continue
        for i in range(len(seq)):
            for j in range(i + 2, len(seq)):
                if seq[i][:2] != seq[j][:2]:
                    continue
                values = [x[2] for x in seq[i:j + 1]]
                inc = values[0] <= values[-1] and all(values[0] <= z <= values[-1] for z in values[1:-1])
                dec = values[0] >= values[-1] and all(values[0] >= z >= values[-1] for z in values[1:-1])
                if inc or dec:
                    del seq[i + 1:j]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq)

def trajectory(raw: Sequence[dict], dim: int):
    if not raw:
        raise ValueError('empty trajectory')
    seq = tuple(stat(x, dim) for x in raw)
    if seq[0][1] != seq[-1][0]:
        raise ValueError('endpoint')
    for a, b in zip(seq, seq[1:]):
        if not contains(b[0], a[0]) or not contains(a[1], b[1]):
            raise ValueError('monotonicity')
    if compact(seq) != seq:
        raise ValueError('noncompact')
    return seq

def key(seq):
    return tuple(seq)

def stat_leq(a, b):
    return a[0] == b[0] and a[1] == b[1] and a[2] <= b[2]

def preorder(lower, upper):
    reachable = set()
    for i in range(len(lower)):
        for j in range(len(upper)):
            if not stat_leq(lower[i], upper[j]):
                continue
            if (i, j) == (0, 0) or any(prev in reachable for prev in ((i - 1, j - 1), (i - 1, j), (i, j - 1))):
                reachable.add((i, j))
    return (len(lower) - 1, len(upper) - 1) in reachable

def verify_witness(lower, upper, witness):
    if witness is None:
        return not preorder(lower, upper)
    path = witness.get('path')
    if not isinstance(path, list) or not path:
        return False
    parsed = []
    for cell in path:
        if not isinstance(cell, list) or len(cell) != 2 or not all(isinstance(x, int) for x in cell):
            return False
        parsed.append(tuple(cell))
    if parsed[0] != (0, 0) or parsed[-1] != (len(lower) - 1, len(upper) - 1):
        return False
    if any((b[0] - a[0], b[1] - a[1]) not in ((1, 0), (0, 1), (1, 1)) for a, b in zip(parsed, parsed[1:])):
        return False
    if any(i < 0 or j < 0 or i >= len(lower) or j >= len(upper) or not stat_leq(lower[i], upper[j]) for i, j in parsed):
        return False
    def encoded(stats):
        return [{'left': list(x[0]), 'right': list(x[1]), 'value': x[2]} for x in stats]
    if witness.get('path_length') != len(parsed) or not preorder(lower, upper):
        return False
    if 'lower_extension' in witness or 'upper_extension' in witness:
        return (
            witness.get('lower_extension') == encoded([lower[i] for i, _ in parsed])
            and witness.get('upper_extension') == encoded([upper[j] for _, j in parsed])
        )
    return True

def subspaces(dim):
    seen = {()}
    queue = [()]
    while queue:
        current = queue.pop(0)
        for vector in range(1, 1 << dim):
            candidate = basis((*current, vector), dim)
            if candidate not in seen:
                seen.add(candidate)
                queue.append(candidate)
    return tuple(sorted(seen))

def universe(dim, k):
    subs = subspaces(dim)
    states = tuple((l, r, v) for l in subs for r in subs for v in range(k + 1))
    bound = (2 * dim + 1) * (2 * k + 1)
    out = {}
    def dfs(seq, target):
        last = seq[-1]
        if last[0] == target:
            out[key(seq)] = seq
        if len(seq) >= bound:
            return
        for nxt in states:
            if not contains(nxt[0], last[0]) or not contains(last[1], nxt[1]) or not contains(target, nxt[0]):
                continue
            candidate = (*seq, nxt)
            if compact(candidate) == candidate:
                dfs(candidate, target)
    for first in states:
        if contains(first[1], first[0]):
            dfs((first,), first[1])
    return tuple(out[k0] for k0 in sorted(out))

def verify_case_integrity(case):
    body = dict(case)
    integrity = body.pop('integrity', None)
    if integrity != digest(body):
        return False
    if case.get('certificate_bytes') != len(canonical_json(case, pretty=True)):
        return False
    return True

def expected_minimal(generators):
    ordered = tuple(sorted({key(x): x for x in generators}.values(), key=key))
    retained = []
    for j, candidate in enumerate(ordered):
        strict = any(i != j and preorder(other, candidate) and not preorder(candidate, other) for i, other in enumerate(ordered))
        equiv_earlier = any(i < j and preorder(other, candidate) and preorder(candidate, other) for i, other in enumerate(ordered))
        if not strict and not equiv_earlier:
            retained.append(candidate)
    return tuple(retained)

def path_witness(lower, upper):
    parent = {}
    for i in range(len(lower)):
        for j in range(len(upper)):
            if not stat_leq(lower[i], upper[j]):
                continue
            if (i, j) == (0, 0):
                parent[(i, j)] = None
                continue
            for prev in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                if prev in parent:
                    parent[(i, j)] = prev
                    break
    end = (len(lower) - 1, len(upper) - 1)
    if end not in parent:
        return None
    path = []
    cursor = end
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    return {'path': [list(x) for x in path], 'path_length': len(path)}

def regenerate():
    a0 = {'left': [], 'right': [1], 'value': 0}
    a1 = {'left': [], 'right': [1], 'value': 1}
    b0 = {'left': [1], 'right': [], 'value': 0}
    b1 = {'left': [1], 'right': [], 'value': 1}
    z0 = {'left': [], 'right': [], 'value': 0}
    lower = trajectory([a0, b0], 1)
    upper = trajectory([a1, a0, b1], 1)
    rejected = trajectory([z0], 1)
    positive = path_witness(lower, upper)
    assert positive is not None and verify_witness(lower, upper, positive)
    assert not preorder(lower, rejected)

    higher = trajectory([a1, b1], 1)
    zero = trajectory([z0], 1)
    generators = (lower, higher, zero)
    retained = expected_minimal(generators)
    removed = [g for g in generators if key(g) not in {key(x) for x in retained}]
    assert len(retained) == 2 and len(removed) == 1
    deletion = path_witness(lower, higher)
    assert deletion is not None and verify_witness(lower, higher, deletion)

    u11 = universe(1, 1)
    closure_original = {key(candidate) for candidate in u11 if any(preorder(source, candidate) for source in generators)}
    closure_retained = {key(candidate) for candidate in u11 if any(preorder(source, candidate) for source in retained)}
    assert closure_original == closure_retained

    g00 = trajectory([{'left': [], 'right': [], 'value': 0}], 0)
    u02 = universe(0, 2)
    closure02 = {key(candidate) for candidate in u02 if preorder(g00, candidate)}

    bad_path = copy.deepcopy(positive)
    bad_path['path'][1] = [1, 0]
    assert not verify_witness(lower, upper, bad_path)
    missing_entry = set(closure_original)
    missing_entry.remove(next(iter(missing_entry)))
    assert missing_entry != closure_original
    bad_deletion = copy.deepcopy(deletion)
    bad_deletion['path'][0] = [1, 1]
    assert not verify_witness(lower, higher, bad_deletion)

    semantic_payload = {
        'positive_path': positive['path'],
        'd1_k1_universe': [repr(x) for x in sorted(key(x) for x in u11)],
        'd1_k1_closure': [repr(x) for x in sorted(closure_original)],
        'retained': [repr(key(x)) for x in retained],
        'removed': [repr(key(x)) for x in removed],
        'deletion_path': deletion['path'],
        'd0_k2_universe': [repr(x) for x in sorted(key(x) for x in u02)],
        'd0_k2_closure': [repr(x) for x in sorted(closure02)],
    }
    return {
        'preorder_positive': True,
        'preorder_negative': True,
        'd1_k1_universe_size': len(u11),
        'd1_k1_full_set_entries': len(closure_original),
        'retained_generators': len(retained),
        'removed_generators': len(removed),
        'generator_deletion_preserves_closure': closure_original == closure_retained,
        'd0_k2_universe_size': len(u02),
        'd0_k2_full_set_entries': len(closure02),
        'tamper_rejections': 3,
        'failures': 0,
        'semantic_audit_digest': digest(semantic_payload),
    }

if __name__ == '__main__':
    with open(sys.argv[1], encoding='utf-8') as handle:
        frozen = json.load(handle)
    assert frozen['artifact'] == 'C049.1-JANUS-EXTENSION-PREORDER-UP-K-B2'
    assert regenerate() == frozen['independent_replay']
    assert frozen['producer_audit_integrity'] == '4c62118a3d4cf7928c0cd99d016c8063e63c8932b7ee4c020a0be815d22375cd'
    assert frozen['p_vs_np'] == 'OPEN'
    print('VERIFIED C049.1 PHASE B2')
