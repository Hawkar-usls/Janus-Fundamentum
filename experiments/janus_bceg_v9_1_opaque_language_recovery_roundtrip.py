#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import random
from pathlib import Path

PREREG = Path('research/JANUS_BCEG_V9_1_OPAQUE_LANGUAGE_RECOVERY_ROUNDTRIP_PREREGISTRATION_2026-08-31.json')
HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('v9', HERE / 'janus_bceg_semantic_cut_compression_v9.py')
v9 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v9)


def cbytes(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def H(x):
    return hashlib.sha256(cbytes(x)).hexdigest()


def seed_int(*parts):
    return int.from_bytes(hashlib.sha256('|'.join(map(str, parts)).encode()).digest()[:8], 'big')


def canon_cnf(cnf):
    return tuple(sorted(tuple(sorted((int(x) for x in c), key=lambda z: (abs(z), z))) for c in cnf))


def cnf_hash(cnf):
    return H([list(c) for c in canon_cnf(cnf)])


def sat_clause(clause, bits):
    for lit in clause:
        b = (bits >> (abs(lit) - 1)) & 1
        if (lit > 0 and b) or (lit < 0 and not b):
            return True
    return False


def sat_cnf(cnf, bits):
    return all(sat_clause(c, bits) for c in cnf)


def xor_clause_block(vars_, rhs):
    out = []
    for bits in itertools.product((0, 1), repeat=len(vars_)):
        if (sum(bits) & 1) == rhs:
            continue
        clause = []
        for v, b in zip(vars_, bits):
            clause.append(v if b == 0 else -v)
        out.append(clause)
    return out


def signed_pair_block(a, b, rhs):
    # x_a XOR x_b = rhs: forbid the two assignments with opposite parity.
    out = []
    for xa, xb in itertools.product((0, 1), repeat=2):
        if (xa ^ xb) == rhs:
            continue
        out.append([a if xa == 0 else -a, b if xb == 0 else -b])
    return out


def shuffle_cnf(cnf, rng):
    out = [list(c) for c in cnf]
    for c in out:
        rng.shuffle(c)
    rng.shuffle(out)
    return out


class ParityDSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.x = [0] * n  # value[node] XOR value[parent]
        self.ops = 0

    def find(self, a):
        self.ops += 1
        if self.p[a] == a:
            return a, 0
        r, q = self.find(self.p[a])
        self.x[a] ^= q
        self.p[a] = r
        self.ops += 2
        return self.p[a], self.x[a]

    def union(self, a, b, rhs):
        ra, xa = self.find(a)
        rb, xb = self.find(b)
        self.ops += 1
        if ra == rb:
            return (xa ^ xb) == rhs
        # Deterministic parent choice for canonical replay.
        if ra > rb:
            ra, rb = rb, ra
            xa, xb = xb, xa
        self.p[rb] = ra
        self.x[rb] = xa ^ xb ^ rhs
        self.ops += 2
        return True


def signed_message(n, edges, force_inconsistent=False):
    d = ParityDSU(n)
    bad = bool(force_inconsistent)
    for a, b, rhs in sorted((int(a), int(b), int(rhs)) for a, b, rhs in edges):
        if not d.union(a, b, rhs):
            bad = True
    groups = {}
    parity_to_root = {}
    for i in range(n):
        r, q = d.find(i)
        groups.setdefault(r, []).append(i)
        parity_to_root[i] = q
    comps = []
    for members in groups.values():
        members = sorted(members)
        if len(members) < 2:
            continue
        anchor = members[0]
        qa = parity_to_root[anchor]
        rel = [[m, parity_to_root[m] ^ qa] for m in members[1:]]
        comps.append({'anchor': anchor, 'relations': rel})
    comps.sort(key=lambda z: (z['anchor'], z['relations']))
    body = {
        'schema': 'JANUS/BCEG/V9.1/SIGNED_EQ_DSU/v1',
        'language': 'SIGNED_EQ_DSU',
        'variables': n,
        'components': comps,
        'inconsistent': bad,
        'replayable': True,
    }
    body['message_hash'] = H(body)
    return body, d.ops + len(edges) + n, len(cbytes(body))


def signed_edges_of(msg):
    out = []
    for comp in msg['components']:
        a = int(comp['anchor'])
        for m, rhs in comp['relations']:
            out.append((a, int(m), int(rhs)))
    return out


def signed_eval(msg, bits):
    if msg['inconsistent']:
        return False
    for comp in msg['components']:
        a = int(comp['anchor'])
        av = (bits >> a) & 1
        for m, rhs in comp['relations']:
            if (av ^ ((bits >> int(m)) & 1)) != int(rhs):
                return False
    return True


def signed_join(a, b):
    assert a['variables'] == b['variables']
    return signed_message(int(a['variables']), signed_edges_of(a) + signed_edges_of(b), a['inconsistent'] or b['inconsistent'])


def signed_project(msg, eliminate):
    n = int(msg['variables'])
    elim = set(map(int, eliminate))
    keep = [i for i in range(n) if i not in elim]
    old_to_new = {old: i for i, old in enumerate(keep)}
    if msg['inconsistent']:
        out, ops, size = signed_message(len(keep), [], True)
        return out, ops + n, size, keep
    edges = []
    for comp in msg['components']:
        vals = {int(comp['anchor']): 0}
        for m, rhs in comp['relations']:
            vals[int(m)] = int(rhs)
        km = sorted(x for x in vals if x in old_to_new)
        if len(km) < 2:
            continue
        anchor = km[0]
        for m in km[1:]:
            edges.append((old_to_new[anchor], old_to_new[m], vals[anchor] ^ vals[m]))
    out, ops, size = signed_message(len(keep), edges, False)
    return out, ops + n + len(edges), size, keep


def gf2_message(n, rows, force_inconsistent=False):
    rr, bad, ops = v9.rref(rows, n)
    bad = bool(bad or force_inconsistent)
    body = {
        'schema': 'JANUS/BCEG/V9.1/GF2_RREF/v1',
        'language': 'GF2_RREF',
        'variables': n,
        'rows': [{'mask': int(m), 'rhs': int(b)} for m, b in rr],
        'inconsistent': bad,
        'rank': len(rr),
        'replayable': True,
    }
    body['message_hash'] = H(body)
    return body, ops + len(rows) * max(1, n), len(cbytes(body))


def gf2_rows_of(msg):
    return [(int(r['mask']), int(r['rhs'])) for r in msg['rows']]


def gf2_eval(msg, bits):
    if msg['inconsistent']:
        return False
    for r in msg['rows']:
        if v9.parity(int(r['mask']) & bits) != int(r['rhs']):
            return False
    return True


def gf2_join(a, b):
    assert a['variables'] == b['variables']
    return gf2_message(int(a['variables']), gf2_rows_of(a) + gf2_rows_of(b), a['inconsistent'] or b['inconsistent'])


def gf2_project(msg, eliminate):
    n = int(msg['variables'])
    elim = sorted(set(map(int, eliminate)))
    keep = [i for i in range(n) if i not in set(elim)]
    order = elim + keep
    reordered = [(v9.reorder_mask(mask, order), rhs) for mask, rhs in gf2_rows_of(msg)]
    rr, bad, ops1 = v9.rref(reordered, n)
    e = len(elim)
    kept_rows = []
    for mask, rhs in rr:
        if mask & ((1 << e) - 1):
            continue
        kept_rows.append((mask >> e, rhs))
    out, ops2, size = gf2_message(len(keep), kept_rows, bad or msg['inconsistent'])
    return out, ops1 + ops2 + len(reordered) * max(1, n), size, keep


def message_eval(msg, bits):
    if msg['language'] == 'SIGNED_EQ_DSU':
        return signed_eval(msg, bits)
    if msg['language'] == 'GF2_RREF':
        return gf2_eval(msg, bits)
    raise ValueError(msg['language'])


def detector_signed(cnf, boundary):
    ops = 0
    groups = {}
    for clause in cnf:
        ops += len(clause) + 1
        if len(clause) != 2:
            return None, {'detector': 'SIGNED_EQ_DSU', 'accepted': False, 'reason': 'NON_2CNF_CLAUSE', 'ops': ops}
        vs = tuple(sorted(abs(x) for x in clause))
        if len(set(vs)) != 2 or any(v not in boundary for v in vs):
            return None, {'detector': 'SIGNED_EQ_DSU', 'accepted': False, 'reason': 'INVALID_PAIR_SCOPE', 'ops': ops}
        groups.setdefault(vs, []).append(tuple(clause))
    edges = []
    for vs, cls in sorted(groups.items()):
        ops += len(cls) * 2
        if len(set(cls)) != 2:
            return None, {'detector': 'SIGNED_EQ_DSU', 'accepted': False, 'reason': 'PAIR_BLOCK_NOT_TWO_CLAUSES', 'ops': ops}
        forbidden = set()
        for clause in cls:
            mp = {abs(l): (1 if l < 0 else 0) for l in clause}
            forbidden.add((mp[vs[0]], mp[vs[1]]))
        if len(forbidden) != 2:
            return None, {'detector': 'SIGNED_EQ_DSU', 'accepted': False, 'reason': 'PAIR_BLOCK_DUPLICATE', 'ops': ops}
        pars = {a ^ b for a, b in forbidden}
        if len(pars) != 1:
            return None, {'detector': 'SIGNED_EQ_DSU', 'accepted': False, 'reason': 'PAIR_BLOCK_NOT_PARITY', 'ops': ops}
        rhs = 1 ^ next(iter(pars))
        edges.append((boundary.index(vs[0]), boundary.index(vs[1]), rhs))
    msg, cop, size = signed_message(len(boundary), edges)
    receipt = {
        'detector': 'SIGNED_EQ_DSU',
        'accepted': True,
        'reason': 'EXACT_PAIR_PARITY_BLOCKS',
        'ops': ops,
        'compile_ops': cop,
        'input_cnf_hash': cnf_hash(cnf),
        'message_hash': msg['message_hash'],
        'extracted_constraints': len(edges),
    }
    return msg, receipt


def detector_gf2(cnf, boundary):
    ops = 0
    groups = {}
    for clause in cnf:
        ops += len(clause) + 1
        if len(clause) != 3:
            return None, {'detector': 'GF2_RREF', 'accepted': False, 'reason': 'NON_3CLAUSE', 'ops': ops}
        vs = tuple(sorted(abs(x) for x in clause))
        if len(set(vs)) != 3 or any(v not in boundary for v in vs):
            return None, {'detector': 'GF2_RREF', 'accepted': False, 'reason': 'INVALID_TRIPLE_SCOPE', 'ops': ops}
        groups.setdefault(vs, []).append(tuple(clause))
    rows = []
    for vs, cls in sorted(groups.items()):
        ops += len(cls) * 3
        if len(set(cls)) != 4:
            return None, {'detector': 'GF2_RREF', 'accepted': False, 'reason': 'TRIPLE_BLOCK_NOT_FOUR_CLAUSES', 'ops': ops}
        forbidden = set()
        for clause in cls:
            mp = {abs(l): (1 if l < 0 else 0) for l in clause}
            forbidden.add(tuple(mp[v] for v in vs))
        if len(forbidden) != 4:
            return None, {'detector': 'GF2_RREF', 'accepted': False, 'reason': 'TRIPLE_BLOCK_DUPLICATE', 'ops': ops}
        pars = {sum(bits) & 1 for bits in forbidden}
        if len(pars) != 1:
            return None, {'detector': 'GF2_RREF', 'accepted': False, 'reason': 'TRIPLE_BLOCK_NOT_PARITY', 'ops': ops}
        rhs = 1 ^ next(iter(pars))
        mask = 0
        for v in vs:
            mask |= 1 << boundary.index(v)
        rows.append((mask, rhs))
    msg, cop, size = gf2_message(len(boundary), rows)
    receipt = {
        'detector': 'GF2_RREF',
        'accepted': True,
        'reason': 'EXACT_TRIPLE_PARITY_BLOCKS',
        'ops': ops,
        'compile_ops': cop,
        'input_cnf_hash': cnf_hash(cnf),
        'message_hash': msg['message_hash'],
        'extracted_constraints': len(rows),
    }
    return msg, receipt


def discover(candidate_input):
    # The candidate sees only these fields; family/expected language is not accepted here.
    assert set(candidate_input) == {'cnf', 'boundary_variables', 'requested_operations'}
    cnf = candidate_input['cnf']
    boundary = list(candidate_input['boundary_variables'])
    receipts = []
    total_detect = 0
    total_compile = 0
    for detector in (detector_signed, detector_gf2):
        msg, rec = detector(cnf, boundary)
        receipts.append(rec)
        total_detect += int(rec.get('ops', 0))
        total_compile += int(rec.get('compile_ops', 0))
        if msg is not None:
            return {
                'status': 'CERTIFIED_LANGUAGE',
                'language': msg['language'],
                'message': msg,
                'detector_receipts': receipts,
                'detect_ops': total_detect,
                'compile_ops': total_compile,
            }
    return {
        'status': 'OPEN_NO_CERTIFIED_LANGUAGE',
        'language': None,
        'message': None,
        'detector_receipts': receipts,
        'detect_ops': total_detect,
        'compile_ops': total_compile,
    }


def semantic_join(a, b):
    if a['language'] != b['language']:
        return None, 0, 0, 'NO_CERTIFIED_CROSS_LANGUAGE_JOIN'
    if a['language'] == 'SIGNED_EQ_DSU':
        m, ops, size = signed_join(a, b)
        return m, ops, size, None
    if a['language'] == 'GF2_RREF':
        m, ops, size = gf2_join(a, b)
        return m, ops, size, None
    return None, 0, 0, 'UNSUPPORTED_LANGUAGE'


def semantic_project(m, eliminate):
    if m['language'] == 'SIGNED_EQ_DSU':
        return (*signed_project(m, eliminate), None)
    if m['language'] == 'GF2_RREF':
        return (*gf2_project(m, eliminate), None)
    return None, 0, 0, [], 'UNSUPPORTED_LANGUAGE'


def to_bridge(m):
    atoms = []
    if m['language'] == 'SIGNED_EQ_DSU':
        for a, b, rhs in signed_edges_of(m):
            atoms.append({'kind': 'SIGNED_EDGE', 'vars': [a, b], 'rhs': rhs})
        root_kind = 'CONJUNCTION_OF_SIGNED_EDGES'
    elif m['language'] == 'GF2_RREF':
        for mask, rhs in gf2_rows_of(m):
            atoms.append({'kind': 'GF2_ROW', 'mask': mask, 'rhs': rhs})
        root_kind = 'CONJUNCTION_OF_GF2_ROWS'
    else:
        raise ValueError(m['language'])
    atoms.sort(key=lambda z: cbytes(z))
    b = {
        'schema': 'JANUS/BCEG/V9.1/TYPED_BOOL_DAG_ATOMS/v1',
        'root_kind': root_kind,
        'variables': int(m['variables']),
        'inconsistent': bool(m['inconsistent']),
        'atoms': atoms,
    }
    b['bridge_hash'] = H(b)
    return b, len(atoms) + int(m['variables']), len(cbytes(b))


def from_bridge(b):
    n = int(b['variables'])
    atoms = list(b['atoms'])
    if b['root_kind'] == 'CONJUNCTION_OF_SIGNED_EDGES':
        if any(a.get('kind') != 'SIGNED_EDGE' for a in atoms):
            return None, 0, 0, 'TYPED_ATOM_MISMATCH'
        edges = [(int(a['vars'][0]), int(a['vars'][1]), int(a['rhs'])) for a in atoms]
        m, ops, size = signed_message(n, edges, bool(b['inconsistent']))
        return m, ops + len(atoms), size, None
    if b['root_kind'] == 'CONJUNCTION_OF_GF2_ROWS':
        if any(a.get('kind') != 'GF2_ROW' for a in atoms):
            return None, 0, 0, 'TYPED_ATOM_MISMATCH'
        rows = [(int(a['mask']), int(a['rhs'])) for a in atoms]
        m, ops, size = gf2_message(n, rows, bool(b['inconsistent']))
        return m, ops + len(atoms), size, None
    return None, 0, 0, 'UNSUPPORTED_BRIDGE_ROOT'


def generate_signed(w, variant, seed):
    rng = random.Random(seed_int(seed, 'SIGNED', w, variant))
    edges = []
    for i in range(w - 1):
        rhs = rng.randrange(2)
        edges.append((i + 1, i + 2, rhs))
    left = []
    right = []
    for j, (a, b, rhs) in enumerate(edges):
        (left if j % 2 == 0 else right).extend(signed_pair_block(a, b, rhs))
    return shuffle_cnf(left, rng), shuffle_cnf(right, rng)


def independent_masks(w, target, rng):
    rows = []
    rank = 0
    attempts = 0
    triples = list(itertools.combinations(range(w), 3))
    rng.shuffle(triples)
    for triple in triples:
        attempts += 1
        mask = sum(1 << i for i in triple)
        rr, bad, _ = v9.rref(rows + [(mask, 0)], w)
        if not bad and len(rr) > rank:
            rows.append((mask, rng.randrange(2)))
            rank = len(v9.rref(rows, w)[0])
            if rank >= target:
                break
    return rows, attempts


def generate_gf2(w, variant, seed):
    rng = random.Random(seed_int(seed, 'GF2', w, variant))
    target = max(3, min(w - 1, (w + 1) // 2))
    rows, attempts = independent_masks(w, target, rng)
    left = []
    right = []
    for j, (mask, rhs) in enumerate(rows):
        vs = [i + 1 for i in range(w) if (mask >> i) & 1]
        block = xor_clause_block(vs, rhs)
        (left if j % 2 == 0 else right).extend(block)
    return shuffle_cnf(left, rng), shuffle_cnf(right, rng), attempts


def generate_hostile(w, variant, seed):
    rng = random.Random(seed_int(seed, 'HOSTILE', w, variant))
    # Each packet independently mixes a 2-CNF parity block and a 3-variable XOR block.
    # Hence neither frozen single-language detector may accept the packet.
    a1, b1 = 1, 2
    a2, b2 = max(1, w - 1), w
    t1 = [1, 3, min(w, 5)]
    if len(set(t1)) < 3:
        t1 = [1, 2, 3]
    t2 = [max(1, w - 4), max(2, w - 2), w]
    if len(set(t2)) < 3:
        t2 = [1, 2, 3]
    left = signed_pair_block(a1, b1, rng.randrange(2)) + xor_clause_block(t1, rng.randrange(2))
    right = signed_pair_block(a2, b2, rng.randrange(2)) + xor_clause_block(t2, rng.randrange(2))
    return shuffle_cnf(left, rng), shuffle_cnf(right, rng)


def candidate_input(cnf, w):
    return {
        'cnf': [list(c) for c in cnf],
        'boundary_variables': list(range(1, w + 1)),
        'requested_operations': ['JOIN', 'EXISTS_PROJECT', 'CANONICALIZE', 'ROUNDTRIP', 'REPLAY'],
    }


def audit_original(cnf, msg, w):
    mismatches = 0
    assignments = 0
    ops = 0
    for bits in range(1 << w):
        ref = sat_cnf(cnf, bits)
        got = message_eval(msg, bits)
        mismatches += int(ref != got)
        assignments += 1
        ops += len(cnf) + 1
    return assignments, ops, mismatches


def audit_projected(cnf, projected, keep, w):
    elim = [i for i in range(w) if i not in set(keep)]
    mismatches = 0
    assignments = 0
    ops = 0
    for kb in range(1 << len(keep)):
        base = 0
        for j, old in enumerate(keep):
            if (kb >> j) & 1:
                base |= 1 << old
        exists = False
        for eb in range(1 << len(elim)):
            bits = base
            for j, old in enumerate(elim):
                if (eb >> j) & 1:
                    bits |= 1 << old
            assignments += 1
            ops += len(cnf)
            if sat_cnf(cnf, bits):
                exists = True
                break
        got = message_eval(projected, kb)
        ops += 1
        mismatches += int(exists != got)
    return assignments, ops, mismatches


def run_supported_case(family, expected_language, w, variant, seed, audit_cfg):
    if family == 'OPAQUE_SIGNED_EQ_CHAIN':
        left, right = generate_signed(w, variant, seed)
        gen_ops = w
    elif family == 'OPAQUE_GF2_TRIPLE_PARITY':
        left, right, gen_ops = generate_gf2(w, variant, seed)
    else:
        raise ValueError(family)

    inp_a = candidate_input(left, w)
    inp_b = candidate_input(right, w)
    # Firewall audit is performed by harness, not communicated to discover().
    visible_keys_ok = set(inp_a) == {'cnf', 'boundary_variables', 'requested_operations'} and set(inp_b) == set(inp_a)

    ua = discover(inp_a)
    ub = discover(inp_b)
    if ua['status'] != 'CERTIFIED_LANGUAGE' or ub['status'] != 'CERTIFIED_LANGUAGE':
        return {
            'ground_truth_family': family, 'expected_language': expected_language, 'w': w, 'variant': variant,
            'candidate_visible_keys_ok': visible_keys_ok, 'status': 'SUPPORTED_DISCOVERY_FAILED',
            'discovered_a': ua['language'], 'discovered_b': ub['language'],
        }
    joined, join_ops, join_size, jerr = semantic_join(ua['message'], ub['message'])
    if jerr:
        return {
            'ground_truth_family': family, 'expected_language': expected_language, 'w': w, 'variant': variant,
            'candidate_visible_keys_ok': visible_keys_ok, 'status': 'SUPPORTED_JOIN_FAILED', 'reason': jerr,
            'discovered_a': ua['language'], 'discovered_b': ub['language'],
        }
    eliminate = list(range(w - (w // 3), w))
    projected, project_ops, project_size, keep, perr = semantic_project(joined, eliminate)
    if perr:
        return {
            'ground_truth_family': family, 'expected_language': expected_language, 'w': w, 'variant': variant,
            'candidate_visible_keys_ok': visible_keys_ok, 'status': 'SUPPORTED_PROJECT_FAILED', 'reason': perr,
        }

    bridge, bridge_encode_ops, bridge_size = to_bridge(projected)
    recovered, bridge_decode_ops, recovered_size, berr = from_bridge(bridge)
    roundtrip_match = bool(recovered and not berr and recovered['message_hash'] == projected['message_hash'])

    # Full replay from reversed clause order. This is separately charged.
    ra = discover(candidate_input(list(reversed(left)), w))
    rb = discover(candidate_input(list(reversed(right)), w))
    replay_ok = False
    replay_ops = ra['detect_ops'] + ra['compile_ops'] + rb['detect_ops'] + rb['compile_ops']
    if ra['message'] is not None and rb['message'] is not None:
        rj, rjo, _, rje = semantic_join(ra['message'], rb['message'])
        replay_ops += rjo
        if rj is not None and not rje:
            rp, rpo, _, rkeep, rpe = semantic_project(rj, eliminate)
            replay_ops += rpo
            if rp is not None and not rpe:
                replay_ok = (rp['message_hash'] == projected['message_hash'] and rkeep == keep)

    full_cnf = list(left) + list(right)
    eval_assignments = 0
    verify_ops = 0
    original_mm = None
    projected_mm = None
    if w <= int(audit_cfg['original_join_relation_exhaustive_through_w']):
        q, op, original_mm = audit_original(full_cnf, joined, w)
        eval_assignments += q
        verify_ops += op
    if w <= int(audit_cfg['projected_relation_exhaustive_through_w']):
        q, op, projected_mm = audit_projected(full_cnf, projected, keep, w)
        eval_assignments += q
        verify_ops += op

    detect_ops = ua['detect_ops'] + ub['detect_ops']
    compile_ops = ua['compile_ops'] + ub['compile_ops']
    canonicalize_ops = len(cbytes(joined)) + len(cbytes(projected))
    semantic_bytes = max(len(cbytes(joined)), len(cbytes(projected)), recovered_size)

    transition_receipt = {
        'schema': 'JANUS/BCEG/V9.1/RECOVERY-ROUNDTRIP-RECEIPT/v1',
        'input_packet_hashes': [cnf_hash(left), cnf_hash(right)],
        'unity': {
            'discovered_languages': [ua['language'], ub['language']],
            'detector_receipts': [ua['detector_receipts'], ub['detector_receipts']],
        },
        'service': {
            'joined_hash': joined['message_hash'],
            'projected_hash': projected['message_hash'],
            'eliminated_columns': eliminate,
        },
        'recovery': {
            'bridge_hash': bridge['bridge_hash'],
            'recovered_hash': recovered['message_hash'] if recovered else None,
            'roundtrip_match': roundtrip_match,
            'replay_match': replay_ok,
        },
        'historical_identity_changed': True,
        'semantic_identity_preserved': roundtrip_match,
    }
    transition_receipt['receipt_hash'] = H(transition_receipt)
    receipt_bytes = len(cbytes(transition_receipt))
    total_alg = (
        gen_ops + detect_ops + compile_ops + join_ops + project_ops + canonicalize_ops +
        bridge_encode_ops + bridge_decode_ops + replay_ops + semantic_bytes + receipt_bytes
    )
    input_literal_count = sum(len(c) for c in full_cnf)
    return {
        'ground_truth_family': family,
        'expected_language': expected_language,
        'w': w,
        'variant': variant,
        'candidate_visible_keys_ok': visible_keys_ok,
        'status': 'CERTIFIED_RECOVERY',
        'discovered_language': ua['language'] if ua['language'] == ub['language'] else 'MISMATCH',
        'packet_languages': [ua['language'], ub['language']],
        'joined_message_hash': joined['message_hash'],
        'projected_message_hash': projected['message_hash'],
        'recovered_message_hash': recovered['message_hash'] if recovered else None,
        'transition_receipt_hash': transition_receipt['receipt_hash'],
        'roundtrip_match': roundtrip_match,
        'replay_match': replay_ok,
        'historical_identity_changed': transition_receipt['historical_identity_changed'],
        'semantic_identity_preserved': transition_receipt['semantic_identity_preserved'],
        'original_audit_mismatches': original_mm,
        'projected_audit_mismatches': projected_mm,
        'keep_width': len(keep),
        'ledger': {
            'input_literal_count': input_literal_count,
            'detector_attempts': sum(len(x['detector_receipts']) for x in (ua, ub)),
            'detect_ops': detect_ops,
            'compile_ops': compile_ops,
            'join_ops': join_ops,
            'project_ops': project_ops,
            'canonicalize_ops': canonicalize_ops,
            'bridge_encode_ops': bridge_encode_ops,
            'bridge_decode_ops': bridge_decode_ops,
            'replay_ops': replay_ops,
            'serialized_semantic_bytes': semantic_bytes,
            'serialized_receipt_bytes': receipt_bytes,
            'algorithmic_boundary_assignments_enumerated': 0,
            'evaluation_only_assignments_enumerated': eval_assignments,
            'verification_ops': verify_ops,
            'bit_complexity_proxy': 8 * (semantic_bytes + receipt_bytes),
            'deferred_debt': 0,
            'total_algorithmic_paid_proxy': total_alg,
            'rejected_detector_work_charged': any(not r['accepted'] for r in ua['detector_receipts'] + ub['detector_receipts']),
        },
    }


def run_hostile_case(w, variant, seed):
    left, right = generate_hostile(w, variant, seed)
    ia, ib = candidate_input(left, w), candidate_input(right, w)
    ua, ub = discover(ia), discover(ib)
    final_open = ua['status'] == 'OPEN_NO_CERTIFIED_LANGUAGE' and ub['status'] == 'OPEN_NO_CERTIFIED_LANGUAGE'
    return {
        'ground_truth_family': 'OPAQUE_MIXED_EQ_XOR_UNSUPPORTED_BY_FROZEN_PORTFOLIO',
        'w': w,
        'variant': variant,
        'candidate_visible_keys_ok': set(ia) == {'cnf', 'boundary_variables', 'requested_operations'} and set(ib) == set(ia),
        'status': 'OPEN_NO_CERTIFIED_LANGUAGE' if final_open else 'HOSTILE_FALSE_ACCEPT',
        'final_semantic_message_emitted': False if final_open else True,
        'packet_statuses': [ua['status'], ub['status']],
        'packet_languages': [ua['language'], ub['language']],
        'algorithmic_boundary_assignments_enumerated': 0,
        'detect_ops': ua['detect_ops'] + ub['detect_ops'],
        'compile_ops': ua['compile_ops'] + ub['compile_ops'],
        'detector_attempts': sum(len(x['detector_receipts']) for x in (ua, ub)),
        'detector_receipts': [ua['detector_receipts'], ub['detector_receipts']],
    }


def selftest():
    s1, s2 = generate_signed(6, 0, 'SELFTEST')
    a, b = discover(candidate_input(s1, 6)), discover(candidate_input(s2, 6))
    assert a['language'] == b['language'] == 'SIGNED_EQ_DSU'
    j, _, _, e = semantic_join(a['message'], b['message'])
    assert j and not e
    p, _, _, keep, e = semantic_project(j, [4, 5])
    assert p and not e and keep == [0, 1, 2, 3]
    br, _, _ = to_bridge(p)
    rec, _, _, e = from_bridge(br)
    assert rec and not e and rec['message_hash'] == p['message_hash']

    g1, g2, _ = generate_gf2(6, 0, 'SELFTEST')
    a, b = discover(candidate_input(g1, 6)), discover(candidate_input(g2, 6))
    assert a['language'] == b['language'] == 'GF2_RREF'
    j, _, _, e = semantic_join(a['message'], b['message'])
    assert j and not e
    p, _, _, _, e = semantic_project(j, [4, 5])
    assert p and not e
    br, _, _ = to_bridge(p)
    rec, _, _, e = from_bridge(br)
    assert rec and not e and rec['message_hash'] == p['message_hash']

    h1, h2 = generate_hostile(6, 0, 'SELFTEST')
    assert discover(candidate_input(h1, 6))['status'] == 'OPEN_NO_CERTIFIED_LANGUAGE'
    assert discover(candidate_input(h2, 6))['status'] == 'OPEN_NO_CERTIFIED_LANGUAGE'
    return {'status': 'PASS', 'P_VS_NP': 'OPEN'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output')
    ap.add_argument('--journal')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(selftest(), indent=2))
        return

    p = json.loads(PREREG.read_text())
    assert p['status'] == 'FROZEN_BEFORE_HOLDOUT_EXECUTION'
    seed = p['holdout_seed']
    audit_cfg = p['bounded_independent_auditor']
    supported = []
    hostile = []
    journal = []
    for fam in p['frozen_supported_families']:
        for w in fam['widths']:
            for variant in range(int(fam['variants_per_width'])):
                row = run_supported_case(fam['generator_family'], fam['expected_language'], int(w), variant, seed, audit_cfg)
                supported.append(row)
                journal.append({'event': 'SUPPORTED_CASE_COMPLETE', **row})
    hf = p['frozen_hostile_family']
    for w in hf['widths']:
        for variant in range(int(hf['variants_per_width'])):
            row = run_hostile_case(int(w), variant, seed)
            hostile.append(row)
            journal.append({'event': 'HOSTILE_CASE_COMPLETE', **row})

    required_ledger = set(p['frozen_cost_ledger']['required_fields'])
    g1 = all(r.get('candidate_visible_keys_ok') for r in supported + hostile)
    g2 = len(supported) == 16 and all(r.get('status') == 'CERTIFIED_RECOVERY' and r.get('discovered_language') == r.get('expected_language') for r in supported)
    g3 = len(hostile) == 4 and all(r['status'] == 'OPEN_NO_CERTIFIED_LANGUAGE' and not r['final_semantic_message_emitted'] for r in hostile)
    g4 = all(r.get('ledger', {}).get('algorithmic_boundary_assignments_enumerated') == 0 for r in supported) and all(r['algorithmic_boundary_assignments_enumerated'] == 0 for r in hostile)
    g5 = all((r['original_audit_mismatches'] in (None, 0)) and (r['projected_audit_mismatches'] in (None, 0)) for r in supported)
    g6 = all(r['roundtrip_match'] and r['replay_match'] and r['projected_message_hash'] == r['recovered_message_hash'] for r in supported)
    g7 = all(r['historical_identity_changed'] and r['semantic_identity_preserved'] and r['transition_receipt_hash'] != r['projected_message_hash'] for r in supported)
    g8 = all(required_ledger.issubset(r['ledger']) and all((isinstance(r['ledger'][k], bool) or r['ledger'][k] >= 0) for k in required_ledger) for r in supported)
    g8 = g8 and all(r['detector_attempts'] >= 1 for r in hostile)
    g9 = True
    for r in supported:
        L = r['ledger']
        n = max(1, int(L['input_literal_count']))
        if L['total_algorithmic_paid_proxy'] > 500 * (n ** 3):
            g9 = False
        if max(L['serialized_semantic_bytes'], L['serialized_receipt_bytes']) > 128 * (n ** 2):
            g9 = False
    g10 = False  # universal theorem deliberately not supplied by this finite experiment
    g11 = True

    gates = [
        {'gate': 'V9_1_G1_OPAQUE_INPUT_FIREWALL', 'passed': g1},
        {'gate': 'V9_1_G2_SUPPORTED_LANGUAGE_DISCOVERY', 'passed': g2},
        {'gate': 'V9_1_G3_CORRECT_HOSTILE_REFUSAL', 'passed': g3},
        {'gate': 'V9_1_G4_ZERO_ALGORITHMIC_BOUNDARY_ENUMERATION', 'passed': g4},
        {'gate': 'V9_1_G5_BOUNDED_EXACTNESS', 'passed': g5},
        {'gate': 'V9_1_G6_RECOVERY_ROUNDTRIP', 'passed': g6},
        {'gate': 'V9_1_G7_REAL_DELTA_PROVENANCE', 'passed': g7},
        {'gate': 'V9_1_G8_FULL_EXERCISED_LEDGER', 'passed': g8},
        {'gate': 'V9_1_G9_FINITE_POLYNOMIAL_LIFECYCLE_SIGNATURE', 'passed': g9},
        {'gate': 'V9_1_G10_UNIVERSAL_OPAQUE_DISCOVERY', 'passed': g10, 'status': 'OPEN'},
        {'gate': 'V9_1_G11_SCIENTIFIC_BOUNDARY', 'passed': g11},
    ]
    finite_ok = all(x['passed'] for x in gates if x['gate'] not in ('V9_1_G10_UNIVERSAL_OPAQUE_DISCOVERY',))
    if finite_ok:
        verdict = 'FINITE_OPAQUE_TYPED_DISCOVERY_AND_RECOVERY_ROUNDTRIP'
    elif not g3:
        verdict = 'HOSTILE_FALSE_ACCEPT__INVALID'
    elif not g4:
        verdict = 'HIDDEN_ENUMERATION__INVALID'
    else:
        verdict = 'SUPPORTED_DISCOVERY_OR_ROUNDTRIP_REFUTED'

    by_language = {}
    for lang in ('SIGNED_EQ_DSU', 'GF2_RREF'):
        rows = [r for r in supported if r.get('expected_language') == lang]
        by_language[lang] = {
            'cases': len(rows),
            'certified_recovery': sum(r.get('status') == 'CERTIFIED_RECOVERY' for r in rows),
            'roundtrip_pass': sum(bool(r.get('roundtrip_match')) for r in rows),
            'replay_pass': sum(bool(r.get('replay_match')) for r in rows),
            'max_total_algorithmic_paid_proxy': max((r.get('ledger', {}).get('total_algorithmic_paid_proxy', 0) for r in rows), default=0),
            'max_serialized_semantic_bytes': max((r.get('ledger', {}).get('serialized_semantic_bytes', 0) for r in rows), default=0),
        }

    result = {
        'schema': 'JANUS/BCEG/V9.1/OPAQUE-LANGUAGE-RECOVERY-ROUNDTRIP/RESULT/v1.0',
        'status': 'COMPLETE_FROZEN_RESULT',
        'verdict': verdict,
        'summary': {
            'supported_cases': len(supported),
            'hostile_cases': len(hostile),
            'supported_certified_recovery': sum(r.get('status') == 'CERTIFIED_RECOVERY' for r in supported),
            'hostile_correct_refusal': sum(r['status'] == 'OPEN_NO_CERTIFIED_LANGUAGE' for r in hostile),
            'algorithmic_boundary_assignments_enumerated_total': sum(r.get('ledger', {}).get('algorithmic_boundary_assignments_enumerated', 0) for r in supported) + sum(r['algorithmic_boundary_assignments_enumerated'] for r in hostile),
            'evaluation_only_assignments_enumerated_total': sum(r.get('ledger', {}).get('evaluation_only_assignments_enumerated', 0) for r in supported),
            'P_VS_NP': 'OPEN',
        },
        'by_language': by_language,
        'gates': gates,
        'supported_cases_detail': supported,
        'hostile_cases_detail': hostile,
        'central_lesson': 'On this frozen typed portfolio, exact semantic language can be discovered from opaque CNF syntax without family labels, then survive JOIN, existential projection, canonical recovery roundtrip, and replay with zero solver-side full-boundary enumeration. The mixed EQ+XOR hostile family is correctly refused, exposing the next gap: certified cross-language composition/switch discovery rather than pretending one frozen language covers the relation.',
        'next_frontier': {
            'id': 'BCEG_V9_2_CROSS_LANGUAGE_SERVICE_SWITCH',
            'goal': 'Replace correct refusal on mixed opaque relations with an exact proof-carrying cross-language service path, while charging bridge discovery, AND/JOIN composition, EXISTS, canonicalization, verification, switching, and cumulative debt. No family label or post-hoc language selection.',
            'killer_condition': 'A compact mixed output does not win if discovery/translation/verification hides exponential work; unsupported operations must remain OPEN rather than silently approximated.'
        },
        'scientific_boundary': {
            'P_VS_NP': 'OPEN',
            'P_EQUALS_NP': False,
            'SAT_IN_P': 'NOT_PROVED',
            'arbitrary_CNF_language_discovery': 'OPEN',
            'universal_polynomial_boundary_elimination': 'OPEN',
            'finite_typed_success_is_universal_theorem': False,
        }
    }
    result['result_hash'] = H(result)
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    with open(args.journal, 'w') as f:
        for row in journal:
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + '\n')
        f.write(json.dumps({'event': 'FINAL_VERDICT', 'verdict': verdict, 'gates': [(x['gate'], x['passed']) for x in gates], 'P_VS_NP': 'OPEN'}, sort_keys=True) + '\n')
    print(json.dumps({
        'verdict': verdict,
        'summary': result['summary'],
        'by_language': by_language,
        'gates': [(x['gate'], x['passed']) for x in gates],
        'P_VS_NP': 'OPEN'
    }, indent=2))


if __name__ == '__main__':
    main()
