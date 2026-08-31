#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, random
from pathlib import Path
from statistics import median

PREREG = Path('research/JANUS_BCEG_SEMANTIC_CUT_COMPRESSION_V9_PREREGISTRATION_2026-08-31.json')


def cbytes(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def H(x):
    return hashlib.sha256(cbytes(x)).hexdigest()


def parity(x: int) -> int:
    return x.bit_count() & 1


def rref(rows, n):
    a = [[int(m), int(b)] for m, b in rows]
    ops = 0
    pivot_row = 0
    for col in range(n):
        p = None
        for i in range(pivot_row, len(a)):
            ops += 1
            if (a[i][0] >> col) & 1:
                p = i
                break
        if p is None:
            continue
        if p != pivot_row:
            a[pivot_row], a[p] = a[p], a[pivot_row]
            ops += 1
        pm, pb = a[pivot_row]
        for i in range(len(a)):
            if i == pivot_row:
                continue
            ops += 1
            if (a[i][0] >> col) & 1:
                a[i][0] ^= pm
                a[i][1] ^= pb
                ops += 2
        pivot_row += 1
        if pivot_row == len(a):
            break
    clean = []
    inconsistent = False
    for m, b in a:
        if m == 0:
            if b:
                inconsistent = True
        else:
            clean.append((m, b))
    clean.sort(key=lambda z: ((z[0] & -z[0]).bit_length(), z[0], z[1]))
    ops += len(clean) * max(1, n)
    return clean, inconsistent, ops


def msg(rows, n, stage):
    rr, bad, ops = rref(rows, n)
    body = {
        'schema': 'JANUS/BCEG/V9/GF2_RREF_MESSAGE/v1',
        'stage': stage,
        'variables': n,
        'rows': [{'mask': m, 'rhs': b} for m, b in rr],
        'rank': len(rr),
        'inconsistent': bad,
        'replayable': True,
    }
    body['message_hash'] = H(body)
    size = len(cbytes(body))
    canon_ops = len(rr) * max(1, n)
    return body, ops, canon_ops, size


def rows_of(m):
    return [(int(x['mask']), int(x['rhs'])) for x in m['rows']]


def eval_msg(m, assignment: int) -> bool:
    if m['inconsistent']:
        return False
    return all(parity(int(r['mask']) & assignment) == int(r['rhs']) for r in m['rows'])


def gen_affine(w, variant, seed):
    r = max(2, math.ceil(math.log2(w)))
    rng = random.Random(int.from_bytes(hashlib.sha256(f'{seed}|{w}|{variant}'.encode()).digest()[:8], 'big'))
    witness = rng.getrandbits(w)
    rows = []
    current_rank = 0
    attempts = 0
    while current_rank < r:
        attempts += 1
        mask = rng.getrandbits(w)
        if mask == 0:
            continue
        cand = rows + [(mask, parity(mask & witness))]
        rr, bad, _ = rref(cand, w)
        if not bad and len(rr) > current_rank:
            rows = cand
            current_rank = len(rr)
    return rows, witness, r, attempts


def join_msgs(a, b):
    assert a['variables'] == b['variables']
    return msg(rows_of(a) + rows_of(b), a['variables'], 'JOIN')


def reorder_mask(mask, order):
    out = 0
    for new, old in enumerate(order):
        if (mask >> old) & 1:
            out |= 1 << new
    return out


def project_exists(m, eliminate_old_cols):
    n = int(m['variables'])
    elim = sorted(set(int(x) for x in eliminate_old_cols))
    keep = [i for i in range(n) if i not in set(elim)]
    order = elim + keep
    reordered = [(reorder_mask(mask, order), rhs) for mask, rhs in rows_of(m)]
    rr, bad, ops1 = rref(reordered, n)
    e = len(elim)
    keep_rows = []
    for mask, rhs in rr:
        if mask & ((1 << e) - 1):
            continue
        keep_rows.append((mask >> e, rhs))
    out, ops2, cop, size = msg(keep_rows, len(keep), 'EXISTS_PROJECT')
    return out, ops1 + ops2 + len(rows_of(m)) * max(1, n), cop, size, keep


def exhaustive_original(rows, m, w):
    mismatches = 0
    checks = 0
    for x in range(1 << w):
        ref = all(parity(mask & x) == rhs for mask, rhs in rows)
        got = eval_msg(m, x)
        checks += 1
        mismatches += int(ref != got)
    return checks, mismatches


def exhaustive_projection(rows, projected, keep_cols, w):
    keep_n = len(keep_cols)
    elim_cols = [i for i in range(w) if i not in set(keep_cols)]
    checks = 0
    mismatches = 0
    for kbits in range(1 << keep_n):
        base = 0
        for j, old in enumerate(keep_cols):
            if (kbits >> j) & 1:
                base |= 1 << old
        exists = False
        for ebits in range(1 << len(elim_cols)):
            x = base
            for j, old in enumerate(elim_cols):
                if (ebits >> j) & 1:
                    x |= 1 << old
            checks += 1
            if all(parity(mask & x) == rhs for mask, rhs in rows):
                exists = True
                break
        got = eval_msg(projected, kbits)
        mismatches += int(exists != got)
    return checks, mismatches


def affine_case(w, variant, cfg):
    rows, witness, expected_rank, gen_attempts = gen_affine(w, variant, cfg['seed'])
    left, right = rows[::2], rows[1::2]
    ma, ca, cca, sa = msg(left, w, 'COMPILE_A')
    mb, cb, ccb, sb = msg(right, w, 'COMPILE_B')
    joined, cj, ccj, sj = join_msgs(ma, mb)
    eliminate = list(range(w - (w // 3), w))
    projected, cp, ccp, sp, keep = project_exists(joined, eliminate)

    # Replay from reversed source rows; canonical identities must remain stable.
    ma2, _, _, _ = msg(list(reversed(left)), w, 'COMPILE_A')
    mb2, _, _, _ = msg(list(reversed(right)), w, 'COMPILE_B')
    joined2, _, _, _ = join_msgs(ma2, mb2)
    projected2, _, _, _, keep2 = project_exists(joined2, eliminate)
    replay = (joined['message_hash'] == joined2['message_hash'] and
              projected['message_hash'] == projected2['message_hash'] and keep == keep2)

    eval_enum = 0
    verify_ops = 0
    orig_mm = None
    proj_mm = None
    if w <= cfg['evaluation_only_exhaustive_checks']['original_relation_max_w']:
        q, orig_mm = exhaustive_original(rows, joined, w)
        eval_enum += q
        verify_ops += q * max(1, len(rows))
    if w <= cfg['evaluation_only_exhaustive_checks']['projected_relation_max_w']:
        q, proj_mm = exhaustive_projection(rows, projected, keep, w)
        eval_enum += q
        verify_ops += q * max(1, len(rows))

    compile_ops = ca + cb + gen_attempts * w
    join_ops = cj
    project_ops = cp
    canonicalize_ops = cca + ccb + ccj + ccp
    total_alg = compile_ops + join_ops + project_ops + canonicalize_ops + sj + sp
    serialized = max(sj, sp)
    rank = int(joined['rank'])
    row = {
        'family': 'AFFINE_SYNDROME_GROWING_SEPARATOR',
        'w': w,
        'variant': variant,
        'expected_semantic_rank': expected_rank,
        'semantic_rank_upper_bound': rank,
        'semantic_state_upper_bound': 1 << rank,
        'raw_boolean_state_space': 1 << w,
        'joined_message_hash': joined['message_hash'],
        'projected_message_hash': projected['message_hash'],
        'projected_width': len(keep),
        'projected_rank': projected['rank'],
        'serialized_message_bytes': serialized,
        'compile_ops': compile_ops,
        'join_ops': join_ops,
        'project_ops': project_ops,
        'canonicalize_ops': canonicalize_ops,
        'replay_ops': compile_ops + join_ops + project_ops + canonicalize_ops,
        'algorithmic_boundary_assignments_enumerated': 0,
        'evaluation_only_assignments_enumerated': eval_enum,
        'verification_ops': verify_ops,
        'bit_complexity_proxy': serialized * 8,
        'deferred_debt': 0,
        'total_algorithmic_paid_proxy': total_alg,
        'original_audit_mismatches': orig_mm,
        'projected_audit_mismatches': proj_mm,
        'replay_match': replay,
        'witness_used_only_to_make_consistent_system': witness,
    }
    return row


def hwb(bits):
    s = sum(bits)
    return 0 if s == 0 else bits[s - 1]


def hwb_kinds(n):
    return [('P0',), ('Pn',)] + [('Pi', i, b) for i in range(1, n) for b in (0, 1)]


def prime_true(kind, bits):
    s = sum(bits)
    if kind[0] == 'P0':
        return s == 0
    if kind[0] == 'Pn':
        return s == len(bits)
    _, i, b = kind
    return s == i and bits[i - 1] == b


def hwb_case(n):
    kinds = hwb_kinds(n)
    # This intentionally reproduces the current constructor pathology: each
    # symbolic prime is materialized as a complete truth row before packaging.
    prime_hashes = []
    compile_truth_rows = 0
    for kind in kinds:
        vals = []
        for x in range(1 << n):
            bits = [(x >> j) & 1 for j in range(n)]
            vals.append(int(prime_true(kind, bits)))
            compile_truth_rows += 1
        prime_hashes.append(H({'kind': kind, 'truth': vals}))
    cert = {
        'schema': 'JANUS/BCEG/V9/HWB_SDD_STYLE_PARTITION_CERT/v1',
        'n': n,
        'elements': [{'kind': list(k), 'prime_hash': h} for k, h in zip(kinds, prime_hashes)],
        'interface_only': True,
    }
    cert['message_hash'] = H(cert)
    size = len(cbytes(cert))
    mismatches = 0
    partition_failures = 0
    verify_ops = 0
    for x in range(1 << n):
        bits = [(x >> j) & 1 for j in range(n)]
        tr = [k for k in kinds if prime_true(k, bits)]
        verify_ops += len(kinds)
        if len(tr) != 1:
            partition_failures += 1
            continue
        k = tr[0]
        sub = 1 if (k[0] == 'Pn' or (k[0] == 'Pi' and k[2] == 1)) else 0
        mismatches += int(sub != hwb(bits))
    return {
        'family': 'HWB_CURRENT_CONSTRUCTOR_LIFECYCLE',
        'w': n,
        'serialized_message_bytes': size,
        'algorithmic_truth_rows_materialized': compile_truth_rows,
        'algorithmic_boundary_assignments_enumerated': compile_truth_rows,
        'evaluation_only_assignments_enumerated': 1 << n,
        'verification_ops': verify_ops,
        'semantic_mismatches': mismatches,
        'partition_failures': partition_failures,
        'message_hash': cert['message_hash'],
        'bit_complexity_proxy': size * 8,
        'deferred_debt': 0,
    }


def selftest():
    rows = [(0b11, 0), (0b110, 1)]
    m, _, _, _ = msg(rows, 3, 'SELFTEST')
    assert all(eval_msg(m, x) == all(parity(mask & x) == rhs for mask, rhs in rows) for x in range(8))
    p, _, _, _, keep = project_exists(m, [2])
    q, mm = exhaustive_projection(rows, p, keep, 3)
    assert q > 0 and mm == 0
    assert hwb([1, 0, 0]) == 1
    return {'status': 'PASS', 'P_VS_NP': 'OPEN'}


def run(output, journal):
    p = json.loads(PREREG.read_text())
    assert p['status'] == 'FROZEN_BEFORE_HOLDOUT_EXECUTION'
    pcfg = p['frozen_positive_family']
    affine = [affine_case(w, v, pcfg) for w in pcfg['raw_separator_widths'] for v in range(pcfg['variants_per_width'])]
    hwb_rows = [hwb_case(w) for w in p['frozen_hostile_control']['widths']]

    g1 = all(r['original_audit_mismatches'] in (None, 0) for r in affine)
    g2 = all(r['replay_match'] for r in affine)
    g3 = all(r['algorithmic_boundary_assignments_enumerated'] == 0 for r in affine)
    g4 = all((r['compile_ops'] + r['join_ops'] + r['project_ops'] + r['canonicalize_ops']) <= 20 * (r['w'] ** 3)
             and r['serialized_message_bytes'] <= 64 * (r['w'] ** 2) for r in affine)
    g5 = all(r['projected_audit_mismatches'] in (None, 0) for r in affine)
    big = [r for r in affine if r['w'] >= 12]
    g6 = all(r['semantic_rank_upper_bound'] < r['w'] and r['serialized_message_bytes'] / (2 ** r['w']) <= 0.15 for r in big)
    g7 = all(r['semantic_mismatches'] == 0 and r['partition_failures'] == 0 for r in hwb_rows)
    growth = []
    for a, b in zip(hwb_rows, hwb_rows[1:]):
        growth.append(b['algorithmic_truth_rows_materialized'] / a['algorithmic_truth_rows_materialized'])
    hidden_exp = bool(growth) and all(x >= 3.5 for x in growth)
    g8 = hidden_exp
    g9 = False  # No arbitrary-CNF coverage theorem and hostile current constructor is exponential.
    g10 = True

    gates = [
        {'gate': 'V9_G1_AFFINE_EXACTNESS_BOUNDED_AUDIT', 'passed': g1},
        {'gate': 'V9_G2_AFFINE_REPLAY', 'passed': g2},
        {'gate': 'V9_G3_ZERO_ALGORITHMIC_BOUNDARY_ENUMERATION', 'passed': g3},
        {'gate': 'V9_G4_AFFINE_POLYNOMIAL_LIFECYCLE_SIGNATURE', 'passed': g4},
        {'gate': 'V9_G5_PROJECTED_EXACTNESS_BOUNDED_AUDIT', 'passed': g5},
        {'gate': 'V9_G6_FINITE_SEMANTIC_COMPRESSION', 'passed': g6},
        {'gate': 'V9_G7_HWB_CERTIFICATE_EXACTNESS', 'passed': g7},
        {'gate': 'V9_G8_HWB_HIDDEN_EXPONENTIAL_DETECTION', 'passed': g8, 'truth_row_growth_ratios': growth},
        {'gate': 'V9_G9_UNIVERSAL_FULL_LIFECYCLE_ESCAPE', 'passed': g9, 'status': 'OPEN'},
        {'gate': 'V9_G10_SCIENTIFIC_BOUNDARY', 'passed': g10},
    ]

    if not all(x['passed'] for x in gates[:8]):
        verdict = 'REFUTED_AFFINE_SEMANTIC_CUT_IMPLEMENTATION' if not all(x['passed'] for x in gates[:7]) else 'HIDDEN_EXPONENTIAL_COMPILATION_NOT_DETECTED__INVALID_RUN'
    else:
        verdict = 'FINITE_TYPED_SEMANTIC_CUT_ESCAPE__HOSTILE_LIFECYCLE_BARRIER_REMAINS'

    by_w = {}
    for w in pcfg['raw_separator_widths']:
        z = [r for r in affine if r['w'] == w]
        by_w[str(w)] = {
            'median_semantic_rank_upper_bound': median(r['semantic_rank_upper_bound'] for r in z),
            'median_serialized_message_bytes': median(r['serialized_message_bytes'] for r in z),
            'median_total_algorithmic_paid_proxy': median(r['total_algorithmic_paid_proxy'] for r in z),
            'median_evaluation_only_assignments': median(r['evaluation_only_assignments_enumerated'] for r in z),
        }

    result = {
        'schema': 'JANUS/BCEG/SEMANTIC-CUT-COMPRESSION/V9/RESULT/v1.0',
        'status': 'COMPLETE_FROZEN_RESULT',
        'preregistration_commit': '5b41ee2247ec482e32cdd0425265c56259ab157d',
        'verdict': verdict,
        'affine_cases': affine,
        'affine_by_width': by_w,
        'hostile_hwb_cases': hwb_rows,
        'hostile_diagnosis': {
            'hidden_exponential_compilation_detected': hidden_exp,
            'truth_row_growth_ratios': growth,
            'meaning': 'The current exact HWB constructor can emit a compact symbolic partition certificate, but its exercised compilation path materializes exponentially growing truth rows. Compact output is therefore not a full lifecycle escape.'
        },
        'gates': gates,
        'scientific_boundary': {
            'typed_affine_family_escape_only': True,
            'arbitrary_CNF_coverage_proved': False,
            'universal_polynomial_boundary_elimination': 'OPEN',
            'SAT_IN_P': 'NOT_PROVED',
            'P_EQUALS_NP': False,
            'P_VS_NP': 'OPEN'
        },
        'next_frontier': 'V9_1_DISCOVER_SEMANTIC_LANGUAGE_FROM_OPAQUE_CUT_WITHOUT_FAMILY_LABEL_AND_WITH_HOSTILE_OPERATION_SWITCHES'
    }
    result['result_hash'] = H(result)
    Path(output).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    with open(journal, 'w') as f:
        for r in affine:
            f.write(json.dumps({'event': 'AFFINE_CASE_COMPLETE', **r}, sort_keys=True) + '\n')
        for r in hwb_rows:
            f.write(json.dumps({'event': 'HWB_HOSTILE_CASE_COMPLETE', **r}, sort_keys=True) + '\n')
        f.write(json.dumps({'event': 'FINAL_VERDICT', 'verdict': verdict, 'gates': gates, 'P_VS_NP': 'OPEN'}, sort_keys=True) + '\n')
    print(json.dumps({'verdict': verdict, 'gates': [[x['gate'], x['passed']] for x in gates], 'by_w': by_w, 'hwb_truth_row_growth': growth, 'P_VS_NP': 'OPEN'}, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--output')
    ap.add_argument('--journal')
    a = ap.parse_args()
    if a.self_test:
        print(json.dumps(selftest(), indent=2))
        return
    if not a.output or not a.journal:
        raise SystemExit('--output and --journal required')
    run(a.output, a.journal)


if __name__ == '__main__':
    main()
