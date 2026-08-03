from __future__ import annotations

import argparse
import copy
import hashlib
import json
from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable, Sequence

CLOSED = 'CLOSED_EXACT'
OPEN_WORK = 'OPEN_WORK_BUDGET'
OPEN_CERT = 'OPEN_CERTIFICATE_VOLUME'


@dataclass(frozen=True, order=True)
class S:
    l: tuple[int, ...]
    r: tuple[int, ...]
    v: int


def cj(x: Any, pretty: bool = False) -> bytes:
    if pretty:
        return (json.dumps(x, indent=2, sort_keys=True) + '\n').encode()
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def dg(x: Any) -> str:
    return hashlib.sha256(cj(x)).hexdigest()


def rref(rows: Iterable[int], d: int) -> tuple[int, ...]:
    limit = 1 << d
    piv: dict[int, int] = {}
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= limit:
            raise ValueError('outside')
        while x:
            p = x.bit_length() - 1
            if p in piv:
                x ^= piv[p]
            else:
                piv[p] = x
                for q in list(piv):
                    if q != p and ((piv[q] >> p) & 1):
                        piv[q] ^= x
                break
    for p in sorted(piv):
        row = piv[p]
        for q in sorted(piv, reverse=True):
            if q != p and ((piv[q] >> p) & 1):
                piv[q] ^= row
    return tuple(piv[p] for p in sorted(piv, reverse=True))


def vectors(b: Sequence[int]) -> tuple[int, ...]:
    vals = {0}
    for row in b:
        vals |= {x ^ row for x in tuple(vals)}
    return tuple(sorted(vals))


def has(big: Sequence[int], small: Sequence[int]) -> bool:
    return set(vectors(small)).issubset(set(vectors(big)))


def sm(a: Sequence[int], b: Sequence[int], d: int) -> tuple[int, ...]:
    return rref((*a, *b), d)


def inter(a: Sequence[int], b: Sequence[int], d: int) -> tuple[int, ...]:
    return rref(sorted(set(vectors(a)) & set(vectors(b))), d)


def enc(s: S) -> dict:
    return {'left': list(s.l), 'right': list(s.r), 'value': s.v}


def encg(g: Sequence[S]) -> list[dict]:
    return [enc(s) for s in g]


def compact_alt(g: Sequence[S]) -> tuple[S, ...]:
    seq = list(g)
    while True:
        changed = False
        for i in range(len(seq) - 1, 0, -1):
            if seq[i - 1] == seq[i]:
                del seq[i]
                changed = True
                break
        if changed:
            continue
        for j in range(len(seq) - 1, 1, -1):
            for i in range(j - 2, -1, -1):
                if (seq[i].l, seq[i].r) != (seq[j].l, seq[j].r):
                    continue
                vals = [x.v for x in seq[i:j + 1]]
                inc = vals[0] <= vals[-1] and all(vals[0] <= z <= vals[-1] for z in vals[1:-1])
                dec = vals[0] >= vals[-1] and all(vals[0] >= z >= vals[-1] for z in vals[1:-1])
                if inc or dec:
                    del seq[i + 1:j]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq)


def parse(raw: Sequence[dict], B: Sequence[int], d: int, compact: bool = True) -> tuple[S, ...]:
    if not raw:
        raise ValueError('empty')
    bb = rref(B, d)
    out = tuple(S(rref(x['left'], d), rref(x['right'], d), int(x['value'])) for x in raw)
    if any(x.v < 0 or not has(bb, x.l) or not has(bb, x.r) for x in out):
        raise ValueError('invalid stat')
    if out[0].r != out[-1].l:
        raise ValueError('endpoint')
    for a, b in zip(out, out[1:]):
        if not has(b.l, a.l) or not has(a.r, b.r):
            raise ValueError('monotonicity')
    if compact and compact_alt(out) != out:
        raise ValueError('noncompact')
    return out


def coord(v: int, basis: Sequence[int]) -> int:
    for mask in range(1 << len(basis)):
        x = 0
        for i, row in enumerate(basis):
            if (mask >> i) & 1:
                x ^= row
        if x == v:
            return mask
    raise ValueError('no coordinate')


def paths(m: int, n: int):
    out = []
    def rec(i, j, p):
        if (i, j) == (m - 1, n - 1):
            out.append(tuple(p)); return
        for di, dj in ((1, 1), (0, 1), (1, 0)):
            if i + di < m and j + dj < n:
                rec(i + di, j + dj, p + [(i + di, j + dj)])
    rec(0, 0, [(0, 0)])
    return tuple(sorted(out))


def join(g1: Sequence[S], g2: Sequence[S], p: Sequence[Sequence[int]], B: Sequence[int], d: int):
    pp = tuple((int(x[0]), int(x[1])) for x in p)
    if pp[0] != (0, 0) or pp[-1] != (len(g1) - 1, len(g2) - 1):
        raise ValueError('path endpoints')
    if len(set(pp)) != len(pp):
        raise ValueError('path repeats')
    if any((b[0] - a[0], b[1] - a[1]) not in ((1, 0), (0, 1), (1, 1)) for a, b in zip(pp, pp[1:])):
        raise ValueError('path step')
    init = inter(g1[0].r, g2[0].r, d)
    raw = []
    receipts = []
    for i, j in pp:
        a, b = g1[i], g2[j]
        cur = inter(sm(a.l, a.r, d), sm(b.l, b.r, d), d)
        correction = len(init) - len(cur)
        if correction < 0:
            raise ValueError('negative correction')
        z = S(sm(a.l, b.l, d), sm(a.r, b.r, d), a.v + b.v + correction)
        raw.append(z)
        receipts.append({
            'child_indices': [i, j],
            'child_left': enc(a),
            'child_right': enc(b),
            'initial_right_intersection_dim': len(init),
            'current_span_intersection_dim': len(cur),
            'lambda_correction': correction,
            'output': enc(z),
        })
    comp = compact_alt(raw)
    parse(encg(comp), B, d, True)
    return {
        'boundary': list(rref(B, d)),
        'path': [[i, j] for i, j in pp],
        'raw_join': encg(raw),
        'raw_length': len(raw),
        'raw_width': max(x.v for x in raw),
        'stat_receipts': receipts,
        'compactification_trace': None,
        'compact_join': encg(comp),
        'compact_length': len(comp),
        'compact_width': max(x.v for x in comp),
    }


def preorder(a: Sequence[S], b: Sequence[S]):
    parent = {}
    for i in range(len(a)):
        for j in range(len(b)):
            if not (a[i].l == b[j].l and a[i].r == b[j].r and a[i].v <= b[j].v):
                continue
            if (i, j) == (0, 0):
                parent[(i, j)] = None
            elif any(x in parent for x in ((i - 1, j - 1), (i - 1, j), (i, j - 1))):
                parent[(i, j)] = next(x for x in ((i - 1, j - 1), (i - 1, j), (i, j - 1)) if x in parent)
    end = (len(a) - 1, len(b) - 1)
    if end not in parent:
        return None
    path = []
    x = end
    while x is not None:
        path.append(x); x = parent[x]
    path.reverse()
    return {'path': [list(x) for x in path], 'path_length': len(path)}


def all_subspaces(B: Sequence[int], d: int):
    bb = rref(B, d)
    vs = vectors(bb)
    seen = {()}; queue = [()]
    while queue:
        q = queue.pop(0)
        for v in vs[1:]:
            x = rref((*q, v), d)
            if x not in seen:
                seen.add(x); queue.append(x)
    return tuple(sorted(seen))


def universe(B: Sequence[int], d: int, k: int):
    bb = rref(B, d); theta = len(bb)
    subs = all_subspaces(bb, d)
    states = tuple(S(l, r, v) for l in subs for r in subs for v in range(k + 1))
    bound = (2 * theta + 1) * (2 * k + 1)
    out = {}
    def key(g): return tuple((x.l, x.r, x.v) for x in g)
    def dfs(seq, target):
        last = seq[-1]
        if last.l == target: out[key(seq)] = seq
        if len(seq) >= bound: return
        for nxt in states:
            if has(nxt.l, last.l) and has(last.r, nxt.r) and has(target, nxt.l):
                cand = (*seq, nxt)
                if compact_alt(cand) == cand:
                    dfs(cand, target)
    for first in states:
        if has(first.r, first.l): dfs((first,), first.r)
    return tuple(out[x] for x in sorted(out))


def closure(gens: Sequence[Sequence[S]], B: Sequence[int], d: int, k: int):
    norm = []
    for g in gens:
        c = compact_alt(g)
        parse(encg(c), B, d, True)
        if max(x.v for x in c) <= k:
            norm.append(c)
    entries = []
    u = universe(B, d, k)
    for cand in u:
        for idx, src in enumerate(norm):
            w = preorder(src, cand)
            if w is not None:
                entries.append({'trajectory': encg(cand), 'source_index': idx, 'witness': w})
                break
    return {'boundary': list(rref(B, d)), 'k': k, 'generator_count': len(norm), 'universe_size': len(u), 'entry_count': len(entries), 'entries': entries}


def projected(g: Sequence[S], B0: Sequence[int], d: int):
    bb = rref(B0, d)
    pre = []
    receipts = []
    for x in g:
        l = inter(x.l, bb, d); r = inter(x.r, bb, d)
        lr = inter(x.l, x.r, d); lrb = inter(lr, bb, d)
        corr = len(lr) - len(lrb)
        y = S(l, r, x.v + corr)
        pre.append(y)
        receipts.append({'input': enc(x), 'output': enc(y), 'lambda_correction': corr, 'dim_left_intersection_right': len(lr), 'dim_triple_intersection': len(lrb)})
    c = compact_alt(pre)
    parse(encg(c), bb, d, True)
    return c, {'target_boundary': list(bb), 'projected_precompact': encg(pre), 'projection_receipts': receipts, 'output': encg(c)}


def verify_case_integrity(case: dict) -> bool:
    if case.get('certificate_bytes') != len(cj(case, pretty=True)):
        return False
    body = dict(case); got = body.pop('integrity', None)
    return got == dg(body)


def verify_artifact(artifact: dict) -> bool:
    try:
        if artifact.get('artifact_id') != 'C049.1-JANUS-PHASE-B3-PARTITION-AWARE-EXPAND-JOIN-SHRINK': return False
        body = dict(artifact); got = body.pop('integrity', None)
        if got != dg(body): return False
        cases = artifact['cases']
        if len(cases) != 8 or any(not verify_case_integrity(c) for c in cases): return False

        c = cases[0]; d = c['ambient_dim']
        child = rref(c['child_boundary_raw'], d); parent = rref(c['parent_boundary_raw'], d)
        if not has(parent, child): return False
        if c['input'] != c['output']: return False
        if c['transport']['child_boundary'] != list(child) or c['transport']['parent_boundary'] != list(parent): return False
        if c['transport']['child_basis_in_parent_coordinates'] != [coord(x, parent) for x in child]: return False
        arr = rref(c['arrangement_span'], d)
        if c['expand_condition_intersection'] != list(inter(arr, parent, d)): return False

        c = cases[1]; d = c['ambient_dim']; B = c['boundary']; g = parse(c['child_trajectory'], B, d, True)
        expected_paths = paths(len(g), len(g))
        seen_paths = tuple(sorted(tuple(tuple(x) for x in r['path']) for r in c['joins']))
        if seen_paths != expected_paths: return False
        for receipt in c['joins']:
            expected = join(g, g, receipt['path'], B, d)
            for key in ('boundary','path','raw_join','raw_length','raw_width','stat_receipts','compact_join','compact_length','compact_width'):
                if receipt[key] != expected[key]: return False
        if c['precompact_statistics_charged'] != sum(r['raw_length'] for r in c['joins']): return False
        blocks = tuple(rref(x, d) for x in c['grouped_factor_blocks'])
        if len(blocks) != 2: return False
        left_aug = sm(c['child_spans'][0], B, d); right_aug = sm(c['child_spans'][1], B, d)
        if c['join_precondition_intersection'] != list(inter(left_aug, right_aug, d)) or c['join_precondition_intersection'] != list(rref(B,d)): return False

        c = cases[2]; d = c['ambient_dim']; g = parse(c['input'], c['source_boundary'], d, True)
        comp, rec = projected(g, c['target_boundary'], d)
        if c['output'] != encg(comp): return False
        for key in ('target_boundary','projected_precompact','projection_receipts','output'):
            if c['projection'][key] != rec[key]: return False
        if c['source_width'] != max(x.v for x in g) or c['projected_width'] != max(x.v for x in comp): return False

        c = cases[3]; d = c['ambient_dim']; B = c['boundary']
        a = parse(c['left'], B, d, True); b = parse(c['right'], B, d, True)
        exp = join(a, b, c['join']['path'], B, d)
        for key in ('boundary','path','raw_join','raw_length','raw_width','stat_receipts','compact_join','compact_length','compact_width'):
            if c['join'][key] != exp[key]: return False
        if c['intermediate_excess'] != exp['raw_length'] - exp['compact_length'] or exp['raw_length'] != 11 or exp['compact_length'] != 5: return False

        c = cases[4]; d = c['ambient_dim']; B = c['common_boundary']; root = c['root_boundary']
        child = parse(c['child_trajectory'], B, d, True)
        joins = []
        for receipt in c['join_receipts']:
            exp = join(child, child, receipt['path'], B, d)
            for key in ('boundary','path','raw_join','raw_length','raw_width','stat_receipts','compact_join','compact_length','compact_width'):
                if receipt[key] != exp[key]: return False
            joins.append(parse(receipt['compact_join'], B, d, True))
        jc = closure(joins, B, d, c['k'])
        if c['joined_closure'] != jc: return False
        projected_gens = []
        if len(c['shrink_receipts']) != len(jc['entries']): return False
        for entry, receipt in zip(jc['entries'], c['shrink_receipts']):
            g = parse(entry['trajectory'], B, d, True)
            pg, rec = projected(g, root, d)
            for key in ('target_boundary','projected_precompact','projection_receipts','output'):
                if receipt[key] != rec[key]: return False
            projected_gens.append(pg)
        rc = closure(projected_gens, root, d, c['k'])
        if c['root_closure'] != rc or rc['entry_count'] != c['expected_root_entry_count'] != 1: return False

        c = cases[5]
        if not c['rejected'] or c['reason'] != 'grouped factor partition lost' or len(c['whole_blocks']) != 2 or len(c['split_blocks']) == 2: return False

        c = cases[6]
        if c['terminal'] != OPEN_WORK or c['attempted'] != 11 or c['attempted'] <= c['work_cap'] or c['work_counter'] != 'precompact_join_statistics': return False

        c = cases[7]
        if c['terminal'] != OPEN_CERT or c['required_certificate_bytes'] <= c['certificate_cap']: return False

        expected_summary = {
            'cases': 8,
            'closed_exact': 6,
            'open_work_budget': 1,
            'open_certificate_volume': 1,
            'lattice_paths_replayed': 6,
            'precompact_statistics_charged': 27,
            'full_pipeline_root_entries': 1,
            'partition_loss_rejected': True,
            'failures': 0,
        }
        if artifact['summary'] != expected_summary: return False
        if artifact['strict_boundary']['current_global_terminal'] != 'OPEN_TRAJECTORY_ENGINE_INCOMPLETE': return False
        if artifact['strict_boundary']['complete_no_layout_at_cap_enabled'] is not False: return False
        if artifact['strict_boundary']['p_vs_np'] != 'OPEN': return False
        return True
    except Exception:
        return False


def rebind_case(case: dict) -> None:
    case.pop('integrity', None)
    case['certificate_bytes'] = 0
    while True:
        body = dict(case); body.pop('integrity', None)
        case['integrity'] = dg(body)
        n = len(cj(case, pretty=True))
        if n == case['certificate_bytes']: break
        case['certificate_bytes'] = n


def rebind_artifact(x: dict) -> None:
    x.pop('integrity', None)
    x['integrity'] = dg(x)


def tamper_self_test(artifact: dict) -> bool:
    variants = []
    a = copy.deepcopy(artifact)
    a['cases'][1]['joins'][0]['path'][1] = [1, 1]
    rebind_case(a['cases'][1]); rebind_artifact(a); variants.append(a)
    b = copy.deepcopy(artifact)
    b['cases'][3]['join']['raw_join'].pop()
    rebind_case(b['cases'][3]); rebind_artifact(b); variants.append(b)
    c = copy.deepcopy(artifact)
    c['cases'][2]['projection']['projection_receipts'][0]['lambda_correction'] += 1
    rebind_case(c['cases'][2]); rebind_artifact(c); variants.append(c)
    return all(not verify_artifact(x) for x in variants)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('artifact')
    p.add_argument('--tamper-self-test', action='store_true')
    args = p.parse_args()
    with open(args.artifact, encoding='utf-8') as h:
        artifact = json.load(h)
    if not verify_artifact(artifact):
        raise SystemExit('REJECTED')
    if args.tamper_self_test and not tamper_self_test(artifact):
        raise SystemExit('TAMPER TEST FAILED')
    print('VERIFIED C049.1 PHASE B3')
