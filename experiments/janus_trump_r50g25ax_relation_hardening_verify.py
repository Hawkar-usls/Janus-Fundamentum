from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path


def lit_true(lit: int, assignment: dict[int, int]) -> bool:
    value = int(assignment[abs(int(lit))])
    return bool(value) if int(lit) > 0 else not bool(value)


def xor_convolve(a: int, b: int) -> int:
    out = 0
    for x in (0, 1):
        if a & (1 << x):
            for y in (0, 1):
                if b & (1 << y):
                    out |= 1 << (x ^ y)
    return out


def shift_mask(mask: int, bit: int) -> int:
    return int(mask) if int(bit) == 0 else ((int(mask) & 1) << 1) | ((int(mask) & 2) >> 1)


def independent_decision(payload):
    variables = tuple(map(int, payload['variables']))
    defects = [tuple(map(int, c)) for c in payload['defects']]
    equations = payload['equations']
    order = tuple(map(int, payload['order']))
    width = int(payload['induced_width'])
    assert len(equations) == 1
    eq = equations[0]
    eq_scope = set(map(int, eq['vars']))
    rhs = int(eq['rhs'])

    factors = []
    for clause in defects:
        scope = tuple(sorted({abs(l) for l in clause}))
        table = {}
        for bits in product((0, 1), repeat=len(scope)):
            a = {v: int(b) for v, b in zip(scope, bits)}
            if any(lit_true(l, a) for l in clause):
                table[bits] = 1
        factors.append((scope, table))

    total_rows = sum(len(t) for _, t in factors)
    max_scope = 0

    for v in order:
        gathered = [(s, t) for s, t in factors if v in s]
        factors = [(s, t) for s, t in factors if v not in s]
        if not gathered:
            gathered = [((v,), {(0,): 1, (1,): 1})]
            total_rows += 2
        union = sorted({u for s, _ in gathered for u in s})
        assert v in union
        new_scope = tuple(u for u in union if u != v)
        assert len(new_scope) <= width, (v, len(new_scope), width)
        max_scope = max(max_scope, len(new_scope))
        out = {}
        for boundary_bits in product((0, 1), repeat=len(new_scope)):
            a = {u: int(b) for u, b in zip(new_scope, boundary_bits)}
            mask_out = 0
            for value in (0, 1):
                a[v] = int(value)
                combined = 1
                viable = True
                for scope, table in gathered:
                    key = tuple(int(a[u]) for u in scope)
                    mask = int(table.get(key, 0))
                    if mask == 0:
                        viable = False
                        break
                    combined = xor_convolve(combined, mask)
                if viable:
                    mask_out |= shift_mask(combined, (1 if v in eq_scope else 0) * int(value))
            if mask_out:
                out[boundary_bits] = int(mask_out)
        total_rows += len(out)
        factors.append((new_scope, out))

    assert all(not s for s, _ in factors)
    root = 1
    for _, table in factors:
        root = xor_convolve(root, int(table.get((), 0)))
    return bool(root & (1 << rhs)), int(root), int(total_rows), int(max_scope)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--result', type=Path, required=True)
    args = ap.parse_args()
    raw = args.result.read_bytes()
    x = json.loads(raw)

    assert x['status'] == 'PASS', x
    assert x['relation_pass'] is True, x
    assert x['failures'] == [], x['failures']
    assert all(bool(v) for v in x['relation_contract'].values()), x['relation_contract']
    assert x['truth_oracle'] == {'generation':False,'selection':False,'verdict':False,'external_exact_sat_oracle':False}
    assert x['firewall'] == {'P_VS_NP':'OPEN','SAT_IN_P':'NOT_PROVED','TRUMP_finished':False}
    assert x['preregistration_commit'] == '7b9cef877200b2f056099309d672923df2178b9a'
    assert x['target_hash'] == 'cfbe4a9b4d4fbe5ec09ad3aa1c1ad8fe633e358b4d8744c92890133b6fa8056b'

    payload = x['source_relation_payload']
    payload_sha = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert payload_sha == x['source_relation_payload_sha256']
    assert len(payload['variables']) == 20
    assert len(payload['defects']) == 61
    assert len(payload['equations']) == 1
    assert payload['induced_width'] == 13

    sat, root_mask, independent_rows, max_scope = independent_decision(payload)
    dp = x['actual_relation_dp']
    assert ('SAT' if sat else 'UNSAT') == dp['decision']
    assert root_mask == dp['root_parity_mask']
    assert max_scope == dp['max_generated_scope']
    assert independent_rows == dp['total_materialized_rows']

    if sat:
        assert dp['reconstruction_pass'] is True
        assert dp['source_validation_pass'] is True
        assignment = {int(k): int(v) for k, v in dp['reconstructed_assignment'].items()}
        assert set(assignment) == set(map(int, payload['variables']))
        for clause in payload['defects']:
            assert any(lit_true(int(l), assignment) for l in clause)
        for eq in payload['equations']:
            lhs = 0
            for v in eq['vars']:
                lhs ^= assignment[int(v)]
            assert lhs == int(eq['rhs'])

    fs = x['frozen_separator']
    assert fs['induced_width'] == 13
    assert fs['frozen_state_bound_2_pow_w'] == 8192
    assert dp['certified_relation_rows_with_parity_charge'] <= fs['L4_budget']
    assert dp['max_generated_scope'] <= fs['induced_width']

    print('AX_RELATION_INDEPENDENT_VERIFY_SHA256=' + hashlib.sha256(raw).hexdigest())
    print(json.dumps({
        'status':'PASS',
        'decision':dp['decision'],
        'root_parity_mask':root_mask,
        'independent_materialized_rows':independent_rows,
        'max_generated_scope':max_scope,
        'reconstruction_pass':dp['reconstruction_pass'],
        'source_validation_pass':dp['source_validation_pass'],
    }, sort_keys=True))


if __name__ == '__main__':
    main()
