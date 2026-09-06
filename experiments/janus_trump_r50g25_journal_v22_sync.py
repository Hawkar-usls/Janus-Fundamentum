from __future__ import annotations

import json
import re
from pathlib import Path

JOURNAL = Path('research/JANUS_TRUMP_R50G25_CHAIN_JOURNAL.json')
RECEIPTS = [
    Path('research/R50G25Z_CONTROLLED_GROWTH_DP_POLYNOMIAL_BUDGET_RESULT_RECEIPT.json'),
    Path('research/R50G25AA_RESOURCE_LIMIT_RECEIPT.json'),
    Path('research/R50G25AB_RESULT_RECEIPT.json'),
]


def canonical_gate(value):
    text = str(value)
    m = re.match(r'^(R50G25(?:AA|AB|Z))(?=$|_)', text)
    return m.group(1) if m else text


def main():
    journal = json.loads(JOURNAL.read_text())
    entries = list(journal.get('entries', []))
    by_gate = {canonical_gate(e.get('gate')): e for e in entries}

    appended = []
    for path in RECEIPTS:
        receipt = json.loads(path.read_text())
        raw_gate = str(receipt['gate'])
        gate = canonical_gate(raw_gate)
        if gate in by_gate:
            old = by_gate[gate]
            for key in ('run_id', 'verdict', 'status'):
                if key in receipt and key in old and receipt[key] != old[key]:
                    raise AssertionError(('JOURNAL_GATE_DRIFT', gate, key, old[key], receipt[key]))
            continue
        if raw_gate != gate:
            receipt = dict(receipt)
            receipt['gate_full'] = raw_gate
            receipt['gate'] = gate
        entries.append(receipt)
        by_gate[gate] = receipt
        appended.append(gate)

    for gate in ('R50G25Z', 'R50G25AA', 'R50G25AB'):
        if gate not in by_gate:
            raise AssertionError(('MISSING_GATE_AFTER_SYNC', gate, sorted(by_gate)))

    policy = journal.setdefault('policy', {})
    assert policy.get('P_VS_NP') == 'OPEN'
    assert policy.get('SAT_IN_P') == 'NOT_PROVED'
    assert policy.get('TRUMP_finished') is False
    policy['finite_success_is_not_universal_coverage'] = True

    journal['entries'] = entries
    journal['version'] = '2.2'
    journal['last_sync'] = {
        'gate_range': 'R50G25Z..R50G25AB',
        'appended_gates': appended,
        'source_receipts': [str(p) for p in RECEIPTS],
        'append_only_gate_identity_check': True,
        'canonical_gate_normalization': 'R50G25AA_* receipt names normalize to R50G25AA while preserving gate_full',
        'retrigger_marker': '2026-09-06T18:45Z',
    }
    JOURNAL.write_text(json.dumps(journal, indent=2, sort_keys=False) + '\n')
    print(json.dumps({'version': journal['version'], 'appended': appended, 'entry_count': len(entries)}, sort_keys=True))


if __name__ == '__main__':
    main()
