from __future__ import annotations
import argparse
import copy
import hashlib
import json
from typing import Any
from janus_c049_1_b2_up_k_core import (
    CapabilityExceeded,
    Ledger,
    OPEN_CERTIFICATE_VOLUME,
    OPEN_DISCOVERY_BUDGET,
    OPEN_WORK_BUDGET,
    decode_trajectory_charged,
    encode,
    extension_preorder_witness,
    minimize_generators,
    trajectory_key,
    up_k_closure,
    verify_extension_preorder_witness,
)

SOURCE = {
    'linear_layout_source': 'Jeong-Kim-Oum arXiv:1507.02184v4 Sections 3.1, 3.2, and 4.1',
    'grouped_framework_source': 'Jeong-Kim-Oum arXiv:1711.01381v3 Section 1',
    'relation_name': 'extension_preorder',
    'operational_alias': 'domination witness',
    'new_mathematical_object': False,
}

def canonical_json(value: Any, pretty: bool = False) -> bytes:
    if pretty:
        return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode('utf-8')
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')

def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()

def bind_integrity_and_volume(payload: dict, certificate_cap: int) -> dict:
    out = copy.deepcopy(payload)
    out.pop('integrity', None)
    out['certificate_bytes'] = 0
    while True:
        body = dict(out)
        body.pop('integrity', None)
        out['integrity'] = digest(body)
        measured = len(canonical_json(out, pretty=True))
        if measured == out['certificate_bytes']:
            break
        out['certificate_bytes'] = measured
    if out['certificate_bytes'] <= certificate_cap:
        return out
    refusal = {
        'case_id': payload.get('case_id'),
        'terminal': OPEN_CERTIFICATE_VOLUME,
        'phase': payload.get('phase', 'B2'),
        'capability': {'certificate_bytes': certificate_cap},
        'required_certificate_bytes': out['certificate_bytes'],
        'source': SOURCE,
        'p_vs_np': 'OPEN',
    }
    refusal['certificate_bytes'] = 0
    while True:
        body = dict(refusal)
        body.pop('integrity', None)
        refusal['integrity'] = digest(body)
        measured = len(canonical_json(refusal, pretty=True))
        if measured == refusal['certificate_bytes']:
            break
        refusal['certificate_bytes'] = measured
    return refusal

def capability(discovery: int = 1_000_000, work: int = 5_000_000, certificate: int = 1_000_000) -> dict:
    return {
        'discovery_work': discovery,
        'work': work,
        'certificate_bytes': certificate,
    }

def run_preorder_case(case_id: str, lower_raw: list[dict], upper_raw: list[dict], expected: bool, caps: dict) -> dict:
    ledger = Ledger(caps['discovery_work'], caps['work'])
    try:
        lower = decode_trajectory_charged(lower_raw, 1, ledger)
        upper = decode_trajectory_charged(upper_raw, 1, ledger)
        witness = extension_preorder_witness(lower, upper, ledger)
        accepted = witness is not None
        if accepted != expected:
            raise AssertionError('unexpected preorder result')
        if witness is not None and not verify_extension_preorder_witness(lower, upper, witness):
            raise AssertionError('producer witness failed local replay')
        payload = {
            'case_id': case_id,
            'phase': 'B2_EXTENSION_PREORDER',
            'terminal': 'CLOSED_EXACT',
            'ambient_dim': 1,
            'lower': encode(lower),
            'upper': encode(upper),
            'accepted': accepted,
            'witness': witness,
            'ledger': ledger.snapshot(),
            'capability': caps,
            'source': SOURCE,
            'p_vs_np': 'OPEN',
        }
    except CapabilityExceeded as exc:
        payload = {
            'case_id': case_id,
            'phase': 'B2_EXTENSION_PREORDER',
            'terminal': exc.terminal,
            'failed_counter': exc.counter,
            'attempted': exc.attempted,
            'cap': exc.cap,
            'ledger': ledger.snapshot(),
            'capability': caps,
            'source': SOURCE,
            'p_vs_np': 'OPEN',
        }
    return bind_integrity_and_volume(payload, caps['certificate_bytes'])

def run_closure_case(case_id: str, ambient_dim: int, k: int, generator_raw: list[list[dict]], caps: dict) -> dict:
    ledger = Ledger(caps['discovery_work'], caps['work'])
    try:
        generators = [decode_trajectory_charged(raw, ambient_dim, ledger) for raw in generator_raw]
        result = up_k_closure(generators, ambient_dim, k, ledger)
        payload = {
            'case_id': case_id,
            'phase': 'B2_UP_K_FULL_SET_CLOSURE',
            'terminal': 'CLOSED_EXACT',
            'capability': caps,
            'source': SOURCE,
            'closure': result,
            'grouped_leaf_policy': 'WHOLE_INPUT_SUBSPACES_ONLY',
            'supplied_layout_used_for_discovery': False,
            'sat_oracle_used': False,
            'p_vs_np': 'OPEN',
        }
    except CapabilityExceeded as exc:
        payload = {
            'case_id': case_id,
            'phase': 'B2_UP_K_FULL_SET_CLOSURE',
            'terminal': exc.terminal,
            'failed_counter': exc.counter,
            'attempted': exc.attempted,
            'cap': exc.cap,
            'ledger': ledger.snapshot(),
            'capability': caps,
            'source': SOURCE,
            'p_vs_np': 'OPEN',
        }
    return bind_integrity_and_volume(payload, caps['certificate_bytes'])

def fixtures() -> dict[str, Any]:
    a0 = {'left': [], 'right': [1], 'value': 0}
    a1 = {'left': [], 'right': [1], 'value': 1}
    b0 = {'left': [1], 'right': [], 'value': 0}
    b1 = {'left': [1], 'right': [], 'value': 1}
    z0 = {'left': [], 'right': [], 'value': 0}
    return {
        'lower': [a0, b0],
        'upper_extension': [a1, a0, b1],
        'upper_rejected': [z0],
        'higher_generator': [a1, b1],
        'zero_generator': [z0],
        'dimension_zero_generator': [{'left': [], 'right': [], 'value': 0}],
    }

def build() -> dict:
    f = fixtures()
    closed = capability()
    cases = [
        run_preorder_case('PREORDER_EXTENSION_REQUIRED', f['lower'], f['upper_extension'], True, closed),
        run_preorder_case('PREORDER_PAIR_MISMATCH_REJECTED', f['lower'], f['upper_rejected'], False, closed),
        run_closure_case(
            'UP_K_DOMINATED_GENERATOR_REMOVAL', 1, 1,
            [f['lower'], f['higher_generator'], f['zero_generator']], closed,
        ),
        run_closure_case(
            'UP_K_DIMENSION_ZERO_COMPLETE_UNIVERSE', 0, 2,
            [f['dimension_zero_generator']], closed,
        ),
        run_closure_case(
            'DISCOVERY_BUDGET_REFUSAL', 1, 1, [f['lower']],
            capability(discovery=100, work=5_000_000, certificate=1_000_000),
        ),
        run_closure_case(
            'WORK_BUDGET_REFUSAL', 1, 1, [f['lower']],
            capability(discovery=1_000_000, work=100, certificate=1_000_000),
        ),
        run_closure_case(
            'CERTIFICATE_VOLUME_REFUSAL', 1, 1, [f['lower']],
            capability(discovery=1_000_000, work=5_000_000, certificate=4_000),
        ),
    ]
    summary = {
        'cases': len(cases),
        'closed_exact': sum(case['terminal'] == 'CLOSED_EXACT' for case in cases),
        'open_discovery_budget': sum(case['terminal'] == OPEN_DISCOVERY_BUDGET for case in cases),
        'open_work_budget': sum(case['terminal'] == OPEN_WORK_BUDGET for case in cases),
        'open_certificate_volume': sum(case['terminal'] == OPEN_CERTIFICATE_VOLUME for case in cases),
        'preorder_positive': cases[0]['accepted'],
        'preorder_negative': not cases[1]['accepted'],
        'd1_k1_universe_size': cases[2]['closure']['universe_size'],
        'd1_k1_full_set_entries': cases[2]['closure']['entry_count'],
        'retained_generators': len(cases[2]['closure']['retained_generators']),
        'removed_generators': len(cases[2]['closure']['removals']),
        'd0_k2_universe_size': cases[3]['closure']['universe_size'],
        'd0_k2_full_set_entries': cases[3]['closure']['entry_count'],
        'failures': 0,
    }
    artifact = {
        'artifact_id': 'C049.1-JANUS-PHASE-B2-EXTENSION-PREORDER-UP-K',
        'cycle': 'C049.1',
        'phase': 'B2',
        'status': 'EXTENSION_PREORDER_DOMINANCE_MINIMIZATION_UP_K_IMPLEMENTED',
        'source': SOURCE,
        'cases': cases,
        'summary': summary,
        'strict_boundary': {
            'implemented': [
                'extension preorder lattice-path decision and witness',
                'deterministic generator minimization under the preorder',
                'direct deletion witness from retained generator to removed generator',
                'complete finite U_k(B) enumeration for admitted GF(2) boundary dimension and width cap',
                'exact up_k closure with one retained-source witness per entry',
                'three exact capability refusals',
            ],
            'pending': [
                'partition-aware expand', 'join', 'shrink', 'branch-decomposition dynamic program',
                'iterative compression', 'FOUND_LAYOUT reconstruction', 'complete NO_LAYOUT_AT_CAP replay',
                'C047 offset-aware affine-functional trellis composition from a discovered layout',
            ],
            'current_terminal_outside_b2_capability': 'OPEN_TRAJECTORY_ENGINE_INCOMPLETE',
            'no_layout_at_cap_enabled': False,
            'universal_polynomial_claim': False,
            'p_vs_np': 'OPEN',
        },
    }
    artifact['integrity'] = digest(artifact)
    return artifact

def self_test() -> None:
    artifact = build()
    assert artifact['summary']['failures'] == 0
    assert artifact['summary']['closed_exact'] == 4
    assert artifact['summary']['open_discovery_budget'] == 1
    assert artifact['summary']['open_work_budget'] == 1
    assert artifact['summary']['open_certificate_volume'] == 1
    assert artifact['summary']['removed_generators'] == 1
    assert artifact['summary']['retained_generators'] == 2
    assert artifact['summary']['d0_k2_universe_size'] == artifact['summary']['d0_k2_full_set_entries'] == 27

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    artifact = build()
    if args.output:
        with open(args.output, 'wb') as handle:
            handle.write(canonical_json(artifact, pretty=True))
    elif not args.self_test:
        print(canonical_json(artifact, pretty=True).decode(), end='')
