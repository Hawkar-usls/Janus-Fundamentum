from __future__ import annotations

import json
from pathlib import Path

JOURNAL = Path('research/JANUS_TRUMP_R50G25_CHAIN_JOURNAL.json')
RECEIPTS = [
    Path('research/R50G25Z_CONTROLLED_GROWTH_DP_POLYNOMIAL_BUDGET_RESULT_RECEIPT.json'),
    Path('research/R50G25AA_RESOURCE_LIMIT_RECEIPT.json'),
    Path('research/R50G25AB_RESULT_RECEIPT.json'),
]


def main():
    journal = json.loads(JOURNAL.read_text())
    entries = list(journal.get('entries', []))
    by_gate = {str(e.get('gate')): e for e in entries}

    appended = []
    for path in RECEIPTS:
        receipt = json.loads(path.read_text())
        gate = str(receipt['gate'])
        if gate in by_gate:
            # Existing gate may only be accepted if the scientific identity agrees.
            old = by_gate[gate]
            for key in ('run_id', 'verdict', 'status'):
                if key in receipt and key in old and receipt[key] != old[key]:
                    raise AssertionError(('JOURNAL_GATE_DRIFT', gate, key, old[key], receipt[key]))
            continue
        entries.append(receipt)
        by_gate[gate] = receipt
        appended.append(gate)

    for gate in ('R50G25Z', 'R50G25AA', 'R50G25AB'):
        if gate not in by_gate:
            raise AssertionError(('MISSING_GATE_AFTER_SYNC', gate))

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
    }
    JOURNAL.write_text(json.dumps(journal, indent=2, sort_keys=False) + '\n')
    print(json.dumps({'version': journal['version'], 'appended': appended, 'entry_count': len(entries)}, sort_keys=True))


if __name__ == '__main__':
    main()
